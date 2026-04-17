#!/usr/bin/env python3
"""Run consolidated location audits and emit text + JSON reports."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import validate_locations
import verify_climate_provenance


@dataclass
class Issue:
    severity: str
    category: str
    destinationId: str
    file: str
    field: str
    issueCode: str
    message: str
    suggestedFix: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to repository root (defaults to parent of scripts directory).",
    )
    parser.add_argument(
        "--report-file",
        type=Path,
        default=None,
        help="Optional explicit JSON report output path.",
    )
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Exit non-zero when high-severity issues exist.",
    )
    parser.add_argument(
        "--fail-on-medium",
        action="store_true",
        help="Exit non-zero when medium-severity issues exist.",
    )
    return parser.parse_args()


def _to_repo_path(file_path: Path, repo_root: Path) -> str:
    try:
        return str(file_path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(file_path)


def _parse_validation_error(raw: str, repo_root: Path) -> tuple[Path, str]:
    file_part, _, message = raw.partition(": ")
    return Path(file_part), message if message else raw


def _suggestion_for_code(issue_code: str) -> str:
    suggestions = {
        "DIRECT_FLIGHT_CONTRADICTION": "Set destination-level direct flags to false or update prac.fltNote to match real routing.",
        "DIRECT_NO_AIRPORT_CONTRADICTION": "If destination has no airport/nonstop routing, set direct flags false and keep wording explicit.",
        "GENERIC_DESC": "Rewrite desc with destination-specific details (neighborhoods, logistics, seasonality).",
        "GENERIC_SWEET": "Rewrite sweet with destination-specific seasonality rather than template language.",
        "GENERIC_BESTFOR": "Replace bestFor tags with destination-specific traveler profiles.",
        "GENERIC_HIGHLIGHT": "Replace highlight with location-specific attraction or context.",
        "GENERIC_TODO_DESC": "Rewrite todo description with concrete destination details.",
        "GENERIC_ALERTS": "Replace placeholder alert block with destination-specific alerts.",
        "CLIMATE_VERIFIED_NO_URL": "Add source.climate[0].url for verified entries or mark climateVerified false with note.",
        "CLIMATE_SOURCE_MISSING": "Ensure linked CSV source URL exists with all 12 months for this destination.",
        "CLIMATE_MONTH_MISSING": "Ensure the source CSV has all 12 month rows and month labels match JSON abbreviations.",
        "CLIMATE_MISMATCH": "Update JSON month climate fields to match CSV source values, or correct the source link.",
        "SCHEMA_CONTRACT": "Fix location payload to satisfy required schema/data contract fields and types.",
    }
    return suggestions.get(issue_code, "Review and fix this field according to AGENTS.md data contract.")


def _classify_validation_issue(message: str) -> tuple[str, str, str, str]:
    lower = message.lower()

    if "direct lgw is true" in lower:
        return "high", "direct-flight", "prac.fltNote", "DIRECT_FLIGHT_CONTRADICTION"
    if "direct flags must be false when prac.fltnote says the destination has no airport" in lower:
        return "high", "direct-flight", "prac.directFrom", "DIRECT_NO_AIRPORT_CONTRADICTION"

    if "field 'desc' is generic" in lower:
        return "medium", "generic-content", "desc", "GENERIC_DESC"
    if "field 'sweet' is generic" in lower:
        return "medium", "generic-content", "sweet", "GENERIC_SWEET"
    if "prac.bestfor" in lower and "destination-specific" in lower:
        return "medium", "generic-content", "prac.bestFor", "GENERIC_BESTFOR"
    if "hls[" in lower and "template boilerplate" in lower:
        return "medium", "generic-content", "hls", "GENERIC_HIGHLIGHT"
    if "todo[" in lower and "template boilerplate" in lower:
        return "medium", "generic-content", "todo.desc", "GENERIC_TODO_DESC"
    if "prac.alerts matches a known placeholder block" in lower:
        return "medium", "generic-content", "prac.alerts", "GENERIC_ALERTS"

    return "high", "schema-data-contract", "", "SCHEMA_CONTRACT"


def _destination_id_for_file(file_path: Path) -> str:
    if file_path.name == "index.json":
        return "_manifest"
    return file_path.stem if file_path.suffix == ".json" else "_repo"


def gather_contract_issues(repo_root: Path) -> list[Issue]:
    locations_root = repo_root / "data" / "locations"
    index_path = locations_root / "index.json"
    errors: list[str] = []
    validate_locations.validate_index(index_path=index_path, locations_root=locations_root, errors=errors)

    for file_path in sorted(locations_root.glob("*.json")):
        if file_path.name == "index.json":
            continue
        validate_locations.validate_location(file_path=file_path, errors=errors)

    issues: list[Issue] = []
    for raw in errors:
        file_path, message = _parse_validation_error(raw=raw, repo_root=repo_root)
        severity, category, field, issue_code = _classify_validation_issue(message)
        issues.append(
            Issue(
                severity=severity,
                category=category,
                destinationId=_destination_id_for_file(file_path),
                file=_to_repo_path(file_path, repo_root),
                field=field,
                issueCode=issue_code,
                message=message,
                suggestedFix=_suggestion_for_code(issue_code),
            )
        )

    return issues


def _parse_climate_failure(failure: str) -> tuple[str, str, str, str]:
    parts = failure.split(":")
    filename = parts[0].strip()
    message = failure.strip()

    if "verified=true but source URL missing" in failure:
        return filename, "source.climate", "CLIMATE_VERIFIED_NO_URL", message
    if "verified=true but source URL not found with 12 CSV months" in failure:
        return filename, "source.climate", "CLIMATE_SOURCE_MISSING", message
    if "missing CSV month" in failure:
        return filename, "months", "CLIMATE_MONTH_MISSING", message
    if "CSV climate != JSON climate" in failure:
        return filename, "months", "CLIMATE_MISMATCH", message
    return filename, "source", "CLIMATE_PROVENANCE", message


def gather_climate_issues(repo_root: Path) -> list[Issue]:
    locations_dir = repo_root / "data" / "locations"
    csv_files = sorted((repo_root / "data" / "climate" / "uploads").glob("*.csv"))
    rows_by_url = verify_climate_provenance.load_rows_by_url(csv_files)

    issues: list[Issue] = []
    for file_path in sorted(locations_dir.glob("*.json")):
        if file_path.name == "index.json":
            continue

        data = json.loads(file_path.read_text(encoding="utf-8"))
        source = data.get("source") or {}
        climate_rows = source.get("climate") or []
        source_url = climate_rows[0].get("url", "").strip() if climate_rows else ""

        failures: list[str] = []
        if source.get("climateVerified"):
            if not source_url:
                failures.append(f"{file_path.name}: verified=true but source URL missing")
            else:
                by_month = rows_by_url.get(source_url)
                if not by_month or len(by_month) < 12:
                    failures.append(f"{file_path.name}: verified=true but source URL not found with 12 CSV months")
                else:
                    for month in data.get("months", []):
                        row = by_month.get(month.get("m"))
                        if row is None:
                            failures.append(f"{file_path.name}: missing CSV month '{month.get('m')}' for source URL")
                            continue
                        exp = verify_climate_provenance.expected_month(row)
                        got = {k: month.get(k) for k in verify_climate_provenance.CLIMATE_KEYS}
                        if exp != got:
                            failures.append(
                                f"{file_path.name}:{month.get('m')}: CSV climate != JSON climate (exp={exp}, got={got})"
                            )

        for failure in failures:
            filename, field, issue_code, message = _parse_climate_failure(failure)
            dest_id = Path(filename).stem
            issues.append(
                Issue(
                    severity="high",
                    category="climate-provenance",
                    destinationId=dest_id,
                    file=f"data/locations/{filename}",
                    field=field,
                    issueCode=issue_code,
                    message=message,
                    suggestedFix=_suggestion_for_code(issue_code),
                )
            )

    return issues


def build_report(issues: list[Issue]) -> dict[str, Any]:
    by_destination: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        by_destination[issue.destinationId].append(asdict(issue))

    affected_destinations = sorted(dest_id for dest_id in by_destination.keys() if not dest_id.startswith("_"))
    batches = [affected_destinations[idx : idx + 3] for idx in range(0, len(affected_destinations), 3)]

    severity_counts = Counter(issue.severity for issue in issues)
    category_counts = Counter(issue.category for issue in issues)

    return {
        "generatedOn": date.today().isoformat(),
        "summary": {
            "totalIssues": len(issues),
            "severityCounts": dict(severity_counts),
            "categoryCounts": dict(category_counts),
            "affectedDestinations": len(affected_destinations),
        },
        "batching": {
            "policy": "max 3 destinations per enrichment batch",
            "groups": batches,
        },
        "issuesByDestination": dict(sorted(by_destination.items())),
        "issues": [asdict(issue) for issue in issues],
    }


def print_human_summary(report: dict[str, Any], report_path: Path) -> None:
    summary = report["summary"]
    severity_counts = summary["severityCounts"]
    category_counts = summary["categoryCounts"]

    print("Location audit summary")
    print(f"- generatedOn: {report['generatedOn']}")
    print(f"- reportFile: {report_path}")
    print(f"- totalIssues: {summary['totalIssues']}")
    print(f"- severities: high={severity_counts.get('high', 0)} medium={severity_counts.get('medium', 0)}")
    print("- categories:")
    for category, count in sorted(category_counts.items()):
        print(f"  - {category}: {count}")

    if report["batching"]["groups"]:
        print("- destination batches (max 3):")
        for idx, group in enumerate(report["batching"]["groups"], start=1):
            print(f"  - batch {idx}: {', '.join(group)}")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = args.report_file or (reports_dir / f"location-audit-{date.today().isoformat()}.json")

    issues = gather_contract_issues(repo_root=repo_root)
    issues.extend(gather_climate_issues(repo_root=repo_root))

    report = build_report(issues=issues)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print_human_summary(report=report, report_path=report_path)

    high = report["summary"]["severityCounts"].get("high", 0)
    medium = report["summary"]["severityCounts"].get("medium", 0)
    if args.fail_on_high and high > 0:
        raise SystemExit(1)
    if args.fail_on_medium and medium > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
