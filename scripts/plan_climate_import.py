#!/usr/bin/env python3
"""Preview climate CSV import actions without modifying repository data."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import import_climate_csv


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-file", type=Path, help="Mixed multi-location CSV file to preview.")
    parser.add_argument("--input-dir", type=Path, help="Directory of one-location CSV files to preview.")
    parser.add_argument(
        "--mode",
        choices=("stage", "create"),
        default="stage",
        help="How unknown locations would be handled by the real importer.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument("--report-file", type=Path, help="Optional path to also write the JSON report.")
    parser.add_argument(
        "--fail-on-unknown",
        action="store_true",
        help="Exit non-zero if any location is unresolved and would be staged/created as unknown.",
    )
    parser.add_argument(
        "--fail-on-fuzzy",
        action="store_true",
        help="Exit non-zero if any location uses fuzzy matching.",
    )
    parser.add_argument(
        "--fail-on-invalid-months",
        action="store_true",
        help="Exit non-zero if any planned entry has invalid or incomplete month coverage.",
    )
    parser.add_argument(
        "--locations-dir",
        type=Path,
        default=repo_root / "data" / "locations",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--pending-dir",
        type=Path,
        default=repo_root / "data" / "pending-locations",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--aliases-file",
        type=Path,
        default=repo_root / "data" / "climate" / "aliases.json",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--location-col",
        default="Location",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--id-col",
        default="id",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--city-col",
        default="city",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--country-col",
        default="country",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--region-col",
        default="region",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--month-col",
        default="Month",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--fuzzy-cutoff",
        type=float,
        default=0.84,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--disable-fuzzy-match",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    if bool(args.input_file) == bool(args.input_dir):
        parser.error("Provide exactly one of --input-file or --input-dir.")
    if args.input_file and not args.input_file.exists():
        parser.error(f"Input file does not exist: {args.input_file}")
    if args.input_dir and not args.input_dir.exists():
        parser.error(f"Input directory does not exist: {args.input_dir}")
    if args.fuzzy_cutoff < 0 or args.fuzzy_cutoff > 1:
        parser.error("--fuzzy-cutoff must be between 0 and 1")
    if args.aliases_file and not args.aliases_file.exists():
        args.aliases_file = None
    return args


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def _load_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _analyze_months(rows: list[dict[str, str]], month_col: str) -> tuple[list[str], list[str], list[str]]:
    seen: list[str] = []
    counts: Counter[str] = Counter()
    warnings: list[str] = []

    for idx, row in enumerate(rows, start=1):
        raw_month = import_climate_csv._row_get(row, month_col, ("Month",))
        try:
            month = import_climate_csv.normalize_month(raw_month)
        except ValueError as exc:
            warnings.append(f"row {idx}: {exc}")
            continue
        seen.append(month)
        counts[month] += 1

    months_present = [month for month in import_climate_csv.MONTH_LABELS if counts[month] > 0]
    missing_months = [month for month in import_climate_csv.MONTH_LABELS if counts[month] == 0]
    duplicate_months = [month for month in import_climate_csv.MONTH_LABELS if counts[month] > 1]
    if duplicate_months:
        warnings.append(f"duplicate month rows: {', '.join(duplicate_months)}")
    return months_present, missing_months, warnings


def _finalize_entry(
    *,
    requested_id: str,
    resolved_id: str,
    resolution: str,
    row_count: int,
    months_present: list[str],
    missing_months: list[str],
    target_path: str,
    manifest_action: str,
    live_file_exists: bool,
    would_write: bool,
    warnings: list[str],
) -> dict[str, Any]:
    return {
        "requestedId": requested_id,
        "resolvedId": resolved_id,
        "resolution": resolution,
        "rowCount": row_count,
        "monthsPresent": months_present,
        "missingMonths": missing_months,
        "targetPath": target_path,
        "manifestAction": manifest_action,
        "liveFileExists": live_file_exists,
        "wouldWrite": would_write,
        "warnings": warnings,
    }


def _plan_combined_file(args: argparse.Namespace, repo_root: Path) -> list[dict[str, Any]]:
    rows = _load_csv_rows(args.input_file)
    if not rows:
        return [
            _finalize_entry(
                requested_id="",
                resolved_id="",
                resolution="error",
                row_count=0,
                months_present=[],
                missing_months=import_climate_csv.MONTH_LABELS.copy(),
                target_path="",
                manifest_action="none",
                live_file_exists=False,
                would_write=False,
                warnings=[f"CSV is empty: {args.input_file}"],
            )
        ]

    alias_map = import_climate_csv._load_aliases(args)
    known_index = import_climate_csv._build_known_location_index(args.locations_dir)
    grouped: dict[str, list[dict[str, str]]] = {}
    errors: list[dict[str, Any]] = []

    for idx, row in enumerate(rows, start=1):
        try:
            loc_id = import_climate_csv._location_id_from_row(row, args)
        except ValueError as exc:
            errors.append(
                _finalize_entry(
                    requested_id=f"row-{idx}",
                    resolved_id="",
                    resolution="error",
                    row_count=1,
                    months_present=[],
                    missing_months=import_climate_csv.MONTH_LABELS.copy(),
                    target_path="",
                    manifest_action="none",
                    live_file_exists=False,
                    would_write=False,
                    warnings=[str(exc)],
                )
            )
            continue
        grouped.setdefault(loc_id, []).append(row)

    entries: list[dict[str, Any]] = errors
    for requested_id, group_rows in sorted(grouped.items()):
        months_present, missing_months, month_warnings = _analyze_months(group_rows, args.month_col)
        invalid_months = bool(missing_months) or any(warning.startswith("row ") for warning in month_warnings)
        resolved_id, resolved_via = import_climate_csv._resolve_location_id(requested_id, known_index, alias_map, args)
        warnings = list(month_warnings)

        if resolved_id:
            resolution = resolved_via
            if resolved_via == "fuzzy":
                warnings.append("resolved via fuzzy match")
            target_path = _repo_rel(args.locations_dir / f"{resolved_id}.json", repo_root)
            live_file_exists = (args.locations_dir / f"{resolved_id}.json").exists()
            entries.append(
                _finalize_entry(
                    requested_id=requested_id,
                    resolved_id=resolved_id,
                    resolution=resolution,
                    row_count=len(group_rows),
                    months_present=months_present,
                    missing_months=missing_months,
                    target_path=target_path,
                    manifest_action="none",
                    live_file_exists=live_file_exists,
                    would_write=not invalid_months,
                    warnings=warnings,
                )
            )
            continue

        safe_id = import_climate_csv._sanitize_location_id(requested_id)
        if args.mode == "create":
            warnings.append("create mode would generate a draft scaffold for a new live location")
            entries.append(
                _finalize_entry(
                    requested_id=requested_id,
                    resolved_id=safe_id,
                    resolution="new-create",
                    row_count=len(group_rows),
                    months_present=months_present,
                    missing_months=missing_months,
                    target_path=_repo_rel(args.locations_dir / f"{safe_id}.json", repo_root),
                    manifest_action="add",
                    live_file_exists=False,
                    would_write=not invalid_months,
                    warnings=warnings,
                )
            )
        else:
            warnings.append("unknown location would be staged to pending")
            entries.append(
                _finalize_entry(
                    requested_id=requested_id,
                    resolved_id=safe_id,
                    resolution="unknown-stage",
                    row_count=len(group_rows),
                    months_present=months_present,
                    missing_months=missing_months,
                    target_path=_repo_rel(args.pending_dir / f"{safe_id}.json", repo_root),
                    manifest_action="none",
                    live_file_exists=False,
                    would_write=not invalid_months,
                    warnings=warnings,
                )
            )

    return entries


def _plan_input_dir(args: argparse.Namespace, repo_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    csv_paths = sorted(args.input_dir.glob("*.csv"))
    if not csv_paths:
        return [
            _finalize_entry(
                requested_id="",
                resolved_id="",
                resolution="error",
                row_count=0,
                months_present=[],
                missing_months=import_climate_csv.MONTH_LABELS.copy(),
                target_path="",
                manifest_action="none",
                live_file_exists=False,
                would_write=False,
                warnings=[f"No CSV files found in {args.input_dir}"],
            )
        ]

    for csv_path in csv_paths:
        try:
            requested_id = import_climate_csv._sanitize_location_id(csv_path.stem)
        except ValueError as exc:
            entries.append(
                _finalize_entry(
                    requested_id=csv_path.stem,
                    resolved_id="",
                    resolution="error",
                    row_count=0,
                    months_present=[],
                    missing_months=import_climate_csv.MONTH_LABELS.copy(),
                    target_path="",
                    manifest_action="none",
                    live_file_exists=False,
                    would_write=False,
                    warnings=[str(exc)],
                )
            )
            continue

        rows = _load_csv_rows(csv_path)
        months_present, missing_months, warnings = _analyze_months(rows, args.month_col)
        invalid_months = bool(missing_months) or any(warning.startswith("row ") for warning in warnings)
        target_live = args.locations_dir / f"{requested_id}.json"
        live_file_exists = target_live.exists()

        if live_file_exists:
            resolution = "exact"
            target_path = _repo_rel(target_live, repo_root)
            manifest_action = "none"
        elif args.mode == "create":
            resolution = "new-create"
            target_path = _repo_rel(target_live, repo_root)
            manifest_action = "add"
            warnings.append("create mode would generate a draft scaffold for a new live location")
        else:
            resolution = "unknown-stage"
            target_path = _repo_rel(args.pending_dir / f"{requested_id}.json", repo_root)
            manifest_action = "none"
            warnings.append("unknown location would be staged to pending")

        entries.append(
            _finalize_entry(
                requested_id=requested_id,
                resolved_id=requested_id,
                resolution=resolution,
                row_count=len(rows),
                months_present=months_present,
                missing_months=missing_months,
                target_path=target_path,
                manifest_action=manifest_action,
                live_file_exists=live_file_exists,
                would_write=not invalid_months,
                warnings=warnings,
            )
        )

    return entries


def _build_report(args: argparse.Namespace, entries: list[dict[str, Any]]) -> dict[str, Any]:
    resolution_counts = Counter(entry["resolution"] for entry in entries)
    input_meta: dict[str, Any]
    if args.input_file:
        input_meta = {"inputFile": str(args.input_file)}
    else:
        input_meta = {"inputDir": str(args.input_dir)}

    return {
        "mode": args.mode,
        "input": input_meta,
        "summary": {
            "totalEntries": len(entries),
            "resolutionCounts": dict(sorted(resolution_counts.items())),
        },
        "entries": entries,
    }


def _print_text(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Climate import plan")
    print(f"- mode: {report['mode']}")
    for key, value in report["input"].items():
        print(f"- {key}: {value}")
    print(f"- totalEntries: {summary['totalEntries']}")
    print("- resolutionCounts:")
    for resolution, count in summary["resolutionCounts"].items():
        print(f"  - {resolution}: {count}")

    for entry in report["entries"]:
        print("")
        print(f"{entry['requestedId'] or '(unresolved)'}")
        print(f"  requestedId: {entry['requestedId']}")
        print(f"  resolvedId: {entry['resolvedId']}")
        print(f"  resolution: {entry['resolution']}")
        print(f"  rowCount: {entry['rowCount']}")
        print(f"  monthsPresent: {', '.join(entry['monthsPresent']) if entry['monthsPresent'] else '-'}")
        print(f"  missingMonths: {', '.join(entry['missingMonths']) if entry['missingMonths'] else '-'}")
        print(f"  targetPath: {entry['targetPath'] or '-'}")
        print(f"  manifestAction: {entry['manifestAction']}")
        print(f"  liveFileExists: {str(entry['liveFileExists']).lower()}")
        print(f"  wouldWrite: {str(entry['wouldWrite']).lower()}")
        print(f"  warnings: {', '.join(entry['warnings']) if entry['warnings'] else '-'}")


def _write_report(report: dict[str, Any], report_file: Path) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _should_fail(args: argparse.Namespace, entries: list[dict[str, Any]]) -> bool:
    for entry in entries:
        if args.fail_on_unknown and entry["resolution"] in {"unknown-stage", "new-create", "error"}:
            return True
        if args.fail_on_fuzzy and entry["resolution"] == "fuzzy":
            return True
        if args.fail_on_invalid_months and (entry["missingMonths"] or entry["wouldWrite"] is False):
            return True
    return False


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    if args.input_file:
        entries = _plan_combined_file(args, repo_root)
    else:
        entries = _plan_input_dir(args, repo_root)

    report = _build_report(args, entries)

    if args.report_file:
        _write_report(report, args.report_file)

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        _print_text(report)

    return 1 if _should_fail(args, entries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
