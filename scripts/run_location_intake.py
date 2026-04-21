#!/usr/bin/env python3
"""Run the location intake workflow as a thin wrapper around existing scripts.

This wrapper intentionally reuses the current script entry points via subprocess
calls rather than importing or refactoring their core logic.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
REPORTS_DIR = REPO_ROOT / "reports" / "intake"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, help="Single CSV file to process.")
    parser.add_argument("--input-dir", type=Path, help="Directory of one-location CSV files to process.")
    parser.add_argument(
        "--mode",
        choices=("stage", "create"),
        default="stage",
        help="How unknown locations should be handled by the importer.",
    )
    parser.add_argument(
        "--unsafe",
        action="store_true",
        help="Disable safe-mode preflight failures on fuzzy matches, unknown/create targets, and invalid month coverage.",
    )
    parser.add_argument(
        "--write-reports",
        action="store_true",
        help="Write plan/audit/enrichment JSON reports to reports/intake/.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=REPORTS_DIR,
        help="Directory for optional wrapper-generated reports (default: reports/intake).",
    )
    parser.add_argument(
        "--locations-dir",
        type=Path,
        default=REPO_ROOT / "data" / "locations",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--pending-dir",
        type=Path,
        default=REPO_ROOT / "data" / "pending-locations",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--aliases-file",
        type=Path,
        default=REPO_ROOT / "data" / "climate" / "aliases.json",
        help="Optional alias map for misspellings/variants.",
    )
    parser.add_argument("--location-col", default="Location", help="Combined CSV location column name.")
    parser.add_argument("--id-col", default="id", help="Combined CSV id column name.")
    parser.add_argument("--city-col", default="city", help="CSV city column name.")
    parser.add_argument("--country-col", default="country", help="CSV country column name.")
    parser.add_argument("--region-col", default="region", help="CSV region column name.")
    parser.add_argument("--month-col", default="Month", help="CSV month column name.")
    parser.add_argument("--avg-col", default="Avg Temp (°C)", help="CSV average temperature column name.")
    parser.add_argument("--hi-col", default="Avg High (°C)", help="CSV average high temperature column name.")
    parser.add_argument("--lo-col", default="Avg Low (°C)", help="CSV average low temperature column name.")
    parser.add_argument("--daylight-col", default="Daylight (h/day)", help="CSV daylight column name.")
    parser.add_argument("--cloud-col", default="Cloud Cover (%)", help="CSV cloud cover column name.")
    parser.add_argument("--rain-col", default="Rainfall (mm)", help="CSV rainfall column name.")
    parser.add_argument("--busy-col", default="busy", help="CSV busy score column name.")
    parser.add_argument("--ac-col", default="ac", help="CSV accommodation score column name.")
    parser.add_argument("--fl-col", default="fl", help="CSV flight score column name.")
    parser.add_argument(
        "--allow-score-overrides",
        action="store_true",
        help="Allow CSV busy/ac/fl columns to override existing scores during import.",
    )
    parser.add_argument(
        "--disable-fuzzy-match",
        action="store_true",
        help="Disable fuzzy matching during planning and import.",
    )
    parser.add_argument(
        "--fuzzy-cutoff",
        type=float,
        default=0.84,
        help="Similarity threshold for fuzzy matching (0-1).",
    )
    parser.add_argument(
        "--default-region",
        default="Other",
        help="Fallback region when creating a new live scaffold in create mode.",
    )
    args = parser.parse_args()

    if bool(args.input_file) == bool(args.input_dir):
        parser.error("Provide exactly one of --input-file or --input-dir.")
    if args.input_file and not args.input_file.exists():
        parser.error(f"Input file does not exist: {args.input_file}")
    if args.input_dir and not args.input_dir.exists():
        parser.error(f"Input directory does not exist: {args.input_dir}")
    if args.aliases_file and not args.aliases_file.exists():
        args.aliases_file = None
    if args.fuzzy_cutoff < 0 or args.fuzzy_cutoff > 1:
        parser.error("--fuzzy-cutoff must be between 0 and 1")
    return args


def _run_command(
    command: list[str],
    *,
    capture_output: bool = False,
    label: str,
) -> subprocess.CompletedProcess[str]:
    print(f"\n==> {label}")
    print("$ " + " ".join(command))
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=capture_output,
        check=False,
    )


def _emit_streams(result: subprocess.CompletedProcess[str]) -> None:
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")


def _common_location_args(args: argparse.Namespace) -> list[str]:
    common = [
        "--locations-dir",
        str(args.locations_dir),
        "--month-col",
        args.month_col,
        "--id-col",
        args.id_col,
        "--city-col",
        args.city_col,
        "--country-col",
        args.country_col,
        "--region-col",
        args.region_col,
        "--location-col",
        args.location_col,
        "--fuzzy-cutoff",
        str(args.fuzzy_cutoff),
    ]
    if args.aliases_file:
        common.extend(["--aliases-file", str(args.aliases_file)])
    if args.disable_fuzzy_match:
        common.append("--disable-fuzzy-match")
    return common


def _common_import_metric_args(args: argparse.Namespace) -> list[str]:
    metric_args = [
        "--avg-col",
        args.avg_col,
        "--hi-col",
        args.hi_col,
        "--lo-col",
        args.lo_col,
        "--daylight-col",
        args.daylight_col,
        "--cloud-col",
        args.cloud_col,
        "--rain-col",
        args.rain_col,
        "--busy-col",
        args.busy_col,
        "--ac-col",
        args.ac_col,
        "--fl-col",
        args.fl_col,
    ]
    if args.allow_score_overrides:
        metric_args.append("--allow-score-overrides")
    return metric_args


def build_plan_command(args: argparse.Namespace, report_path: Path | None) -> list[str]:
    command = [sys.executable, str(SCRIPTS_DIR / "plan_climate_import.py"), "--format", "json", "--mode", args.mode]
    if args.input_file:
        command.extend(["--input-file", str(args.input_file)])
    else:
        command.extend(["--input-dir", str(args.input_dir)])
    command.extend(_common_location_args(args))
    command.extend(["--pending-dir", str(args.pending_dir)])
    if report_path:
        command.extend(["--report-file", str(report_path)])
    if not args.unsafe:
        command.extend(["--fail-on-unknown", "--fail-on-fuzzy", "--fail-on-invalid-months"])
    return command


def build_import_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(SCRIPTS_DIR / "import_climate_csv.py")]
    if args.input_file:
        command.extend(["--input-file", str(args.input_file)])
    else:
        command.extend(["--input-dir", str(args.input_dir)])
    command.extend(_common_location_args(args))
    command.extend(_common_import_metric_args(args))
    if args.mode == "create":
        command.extend(["--create-missing", "--default-region", args.default_region])
    else:
        command.extend(["--stage-unknown-dir", str(args.pending_dir)])
    return command


def build_simple_command(script_name: str, *, extra_args: list[str] | None = None) -> list[str]:
    command = [sys.executable, str(SCRIPTS_DIR / script_name)]
    if extra_args:
        command.extend(extra_args)
    return command


def ensure_reports_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_output(result: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    if result.returncode != 0:
        _emit_streams(result)
        raise SystemExit(result.returncode)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        _emit_streams(result)
        raise SystemExit(f"{label} did not return valid JSON: {exc}") from exc


def summarize_plan(plan_report: dict[str, Any]) -> dict[str, int]:
    return dict(plan_report.get("summary", {}).get("resolutionCounts", {}))


def summarize_enrichment(batch_report: dict[str, Any]) -> list[str]:
    next_batch = batch_report.get("nextBatch")
    if isinstance(next_batch, list):
        return [str(item) for item in next_batch]
    return []


def summarize_audit(audit_report: dict[str, Any]) -> dict[str, int]:
    summary = audit_report.get("summary", {})
    return {
        "totalIssues": int(summary.get("totalIssues", 0)),
        "high": int(summary.get("severityCounts", {}).get("high", 0)),
        "medium": int(summary.get("severityCounts", {}).get("medium", 0)),
    }


def main() -> int:
    args = parse_args()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    reports_dir = ensure_reports_dir(args.reports_dir) if args.write_reports else None
    plan_report_path = reports_dir / f"plan-{timestamp}.json" if reports_dir else None
    audit_report_path = reports_dir / f"audit-{timestamp}.json" if reports_dir else None
    enrichment_report_path = reports_dir / f"enrichment-{timestamp}.json" if reports_dir else None

    plan_result = _run_command(
        build_plan_command(args, plan_report_path),
        capture_output=True,
        label="Plan climate import",
    )
    plan_report = load_json_output(plan_result, "plan_climate_import.py")

    if plan_result.returncode != 0:
        # Kept for clarity even though load_json_output exits on non-zero.
        return plan_result.returncode

    resolution_counts = summarize_plan(plan_report)
    if not args.unsafe:
        print("Plan passed safe-mode checks.")
    else:
        print("Plan completed with safe-mode checks disabled.")
    print("Resolution counts: " + ", ".join(f"{key}={value}" for key, value in sorted(resolution_counts.items())))

    import_result = _run_command(
        build_import_command(args),
        capture_output=False,
        label="Import climate CSV",
    )
    if import_result.returncode != 0:
        raise SystemExit(import_result.returncode)

    validate_result = _run_command(
        build_simple_command("validate_locations.py"),
        capture_output=False,
        label="Validate locations",
    )
    if validate_result.returncode != 0:
        raise SystemExit(validate_result.returncode)

    provenance_result = _run_command(
        build_simple_command("verify_climate_provenance.py"),
        capture_output=False,
        label="Verify climate provenance",
    )
    if provenance_result.returncode != 0:
        raise SystemExit(provenance_result.returncode)

    audit_command = build_simple_command(
        "audit_locations.py",
        extra_args=["--fail-on-high"] + (["--report-file", str(audit_report_path)] if audit_report_path else []),
    )
    audit_result = _run_command(
        audit_command,
        capture_output=False,
        label="Audit locations",
    )
    if audit_result.returncode != 0:
        raise SystemExit(audit_result.returncode)

    if audit_report_path and audit_report_path.exists():
        audit_report = json.loads(audit_report_path.read_text(encoding="utf-8"))
    else:
        # Fallback path if reports were not requested.
        generated_report = REPO_ROOT / "reports" / f"location-audit-{datetime.now().date().isoformat()}.json"
        audit_report = json.loads(generated_report.read_text(encoding="utf-8"))

    enrichment_command = build_simple_command(
        "plan_enrichment_batch.py",
        extra_args=["--format", "json"] + (["--report-file", str(enrichment_report_path)] if enrichment_report_path else []),
    )
    enrichment_result = _run_command(
        enrichment_command,
        capture_output=True,
        label="Plan next enrichment batch",
    )
    batch_report = load_json_output(enrichment_result, "plan_enrichment_batch.py")

    audit_summary = summarize_audit(audit_report)
    next_batch = summarize_enrichment(batch_report)

    print("\nIntake summary")
    print(f"- input: {args.input_file if args.input_file else args.input_dir}")
    print(f"- mode: {args.mode}")
    print(f"- safeMode: {'off' if args.unsafe else 'on'}")
    print(f"- planResolutionCounts: {json.dumps(resolution_counts, ensure_ascii=False, sort_keys=True)}")
    print(
        "- audit: "
        f"totalIssues={audit_summary['totalIssues']} "
        f"high={audit_summary['high']} "
        f"medium={audit_summary['medium']}"
    )
    print(f"- nextEnrichmentBatch: {', '.join(next_batch) if next_batch else '-'}")
    if reports_dir:
        print(f"- reportsDir: {reports_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
