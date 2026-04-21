#!/usr/bin/env python3
"""Plan the next enrichment batch for live locations without modifying repo data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import audit_locations


REASON_GENERIC_CONTENT = "GENERIC_CONTENT"
REASON_DRAFT_SCAFFOLD = "DRAFT_SCAFFOLD"
REASON_MISSING_PRACTICAL_DEPTH = "MISSING_PRACTICAL_DEPTH"
REASON_QUEUE_PENDING = "QUEUE_PENDING"
REASON_HIGH_SEVERITY_BLOCKER = "HIGH_SEVERITY_BLOCKER"


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    parser.add_argument("--report-file", type=Path, help="Optional path to write the report.")
    parser.add_argument("--max-batch-size", type=int, default=3, help="Maximum number of locations in nextBatch.")
    parser.add_argument(
        "--include-blocked",
        action="store_true",
        help="Include blocked location details in text output. JSON always includes them.",
    )
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Exit non-zero if any location from the active queue/import set has high-severity blockers.",
    )
    parser.add_argument("--queue-file", type=Path, help="Optional markdown queue file to anchor batch ordering.")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root,
        help="Repository root (defaults to parent of scripts directory).",
    )
    args = parser.parse_args()
    if args.max_batch_size < 1:
        parser.error("--max-batch-size must be at least 1")
    if args.queue_file and not args.queue_file.exists():
        parser.error(f"Queue file does not exist: {args.queue_file}")
    return args


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def _find_default_queue_file(repo_root: Path) -> Path | None:
    pending_matches = sorted((repo_root / "data" / "pending-locations").glob("enrichment-queue-*.md"))
    if pending_matches:
        return pending_matches[-1]

    import_matches = sorted((repo_root / "docs").glob("import-batch-*.md"))
    if import_matches:
        return import_matches[-1]

    return None


def _parse_queue_ids(queue_path: Path) -> list[str]:
    text = queue_path.read_text(encoding="utf-8")
    ids: list[str] = []
    seen: set[str] = set()

    patterns = (
        re.compile(r"^\|\s*\[\s*\]\s*\|\s*\d+\s*\|\s*([a-z0-9-]+)\s*\|", flags=re.MULTILINE),
        re.compile(r"^- \[\s*\]\s*`([a-z0-9-]+)`", flags=re.MULTILINE),
    )
    for pattern in patterns:
        for match in pattern.finditer(text):
            loc_id = match.group(1).strip()
            if loc_id and loc_id not in seen:
                ids.append(loc_id)
                seen.add(loc_id)
    return ids


def _load_live_locations(repo_root: Path) -> dict[str, dict[str, Any]]:
    locations_dir = repo_root / "data" / "locations"
    payloads: dict[str, dict[str, Any]] = {}
    for file_path in sorted(locations_dir.glob("*.json")):
        if file_path.name == "index.json":
            continue
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        payloads[file_path.stem] = payload
    return payloads


def _classify_issue_reason(issue: audit_locations.Issue) -> str | None:
    if issue.severity == "high":
        return REASON_HIGH_SEVERITY_BLOCKER
    if issue.category == "generic-content":
        return REASON_GENERIC_CONTENT
    return None


def _has_skeletal_practicals(payload: dict[str, Any]) -> bool:
    source = payload.get("source") or {}
    if isinstance(source, dict) and source.get("draftOnly") is True:
        return False

    prac = payload.get("prac") or {}
    if not isinstance(prac, dict):
        return True

    alerts = prac.get("alerts")
    airports = prac.get("airports")
    best_for = prac.get("bestFor")
    flt_note = str(prac.get("fltNote", "")).strip()
    lang = str(prac.get("lang", "")).strip()
    tz = str(prac.get("tz", "")).strip()
    visa = str(prac.get("visa", "")).strip()
    currency = str(prac.get("currency", "")).strip()

    if not alerts or not airports or not best_for:
        return True
    if not flt_note or not lang or not tz or not visa or not currency:
        return True

    scoring = source.get("scoring") if isinstance(source, dict) else None
    if not isinstance(scoring, dict):
        return True
    if not str(scoring.get("reviewedOn", "")).strip() or not str(scoring.get("profile", "")).strip():
        return True

    return False


def _collect_state(
    repo_root: Path, queue_ids: list[str], queue_path: Path | None
) -> tuple[dict[str, Any], list[str]]:
    live_payloads = _load_live_locations(repo_root)
    issues = audit_locations.gather_contract_issues(repo_root=repo_root)
    issues.extend(audit_locations.gather_climate_issues(repo_root=repo_root))

    issues_by_destination: dict[str, list[audit_locations.Issue]] = defaultdict(list)
    for issue in issues:
        if issue.destinationId.startswith("_"):
            continue
        issues_by_destination[issue.destinationId].append(issue)

    blocked: list[dict[str, Any]] = []
    needs_enrichment: list[dict[str, Any]] = []
    ready_ids: list[str] = []
    blocked_ids: set[str] = set()

    for loc_id, payload in sorted(live_payloads.items()):
        destination_issues = issues_by_destination.get(loc_id, [])
        reason_codes: set[str] = set()
        blockers: list[dict[str, str]] = []

        for issue in destination_issues:
            reason = _classify_issue_reason(issue)
            if reason == REASON_HIGH_SEVERITY_BLOCKER:
                blocked_ids.add(loc_id)
                blockers.append(
                    {
                        "issueCode": issue.issueCode,
                        "category": issue.category,
                        "message": issue.message,
                    }
                )
            elif reason:
                reason_codes.add(reason)

        source = payload.get("source") or {}
        if isinstance(source, dict) and source.get("draftOnly") is True:
            reason_codes.add(REASON_DRAFT_SCAFFOLD)

        if _has_skeletal_practicals(payload):
            reason_codes.add(REASON_MISSING_PRACTICAL_DEPTH)

        if loc_id in queue_ids:
            reason_codes.add(REASON_QUEUE_PENDING)

        if loc_id in blocked_ids:
            blocked.append(
                {
                    "id": loc_id,
                    "reasons": [REASON_HIGH_SEVERITY_BLOCKER],
                    "blockingIssues": blockers,
                    "inQueue": loc_id in queue_ids,
                }
            )
            continue

        if reason_codes:
            needs_enrichment.append(
                {
                    "id": loc_id,
                    "reasons": sorted(reason_codes),
                    "inQueue": loc_id in queue_ids,
                }
            )
            ready_ids.append(loc_id)

    queue_rank = {loc_id: idx for idx, loc_id in enumerate(queue_ids)}
    ready_ids = sorted(
        ready_ids,
        key=lambda loc_id: (0, queue_rank[loc_id]) if loc_id in queue_rank else (1, loc_id),
    )

    report = {
        "summary": {
            "totalLiveLocations": len(live_payloads),
            "totalBlocked": len(blocked),
            "totalNeedingEnrichment": len(needs_enrichment),
            "totalReadyForBatching": len(ready_ids),
        },
        "queue": {
            "file": _repo_rel(queue_path, repo_root) if queue_path else None,
            "ids": queue_ids,
        },
        "blocked": sorted(blocked, key=lambda item: item["id"]),
        "needsEnrichment": sorted(needs_enrichment, key=lambda item: item["id"]),
    }
    return report, ready_ids


def _print_text(report: dict[str, Any], next_batch: list[str], remaining_queue: list[str], include_blocked: bool) -> None:
    summary = report["summary"]
    print("Enrichment batch plan")
    print(f"- totalLiveLocations: {summary['totalLiveLocations']}")
    print(f"- totalBlocked: {summary['totalBlocked']}")
    print(f"- totalNeedingEnrichment: {summary['totalNeedingEnrichment']}")
    print(f"- totalReadyForBatching: {summary['totalReadyForBatching']}")
    print(f"- queueFile: {report['queue']['file'] or '-'}")
    print(f"- nextBatch: {', '.join(next_batch) if next_batch else '-'}")
    print(f"- remainingQueue: {', '.join(remaining_queue) if remaining_queue else '-'}")

    if include_blocked and report["blocked"]:
        print("\nBlocked")
        for item in report["blocked"]:
            issue_codes = ", ".join(issue["issueCode"] for issue in item["blockingIssues"])
            print(f"- {item['id']}: {issue_codes or REASON_HIGH_SEVERITY_BLOCKER}")

    if report["needsEnrichment"]:
        print("\nNeeds Enrichment")
        for item in report["needsEnrichment"]:
            print(f"- {item['id']}: {', '.join(item['reasons'])}")


def _write_report(report: dict[str, Any], report_file: Path) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    queue_path = args.queue_file.resolve() if args.queue_file else _find_default_queue_file(repo_root)
    queue_ids = _parse_queue_ids(queue_path) if queue_path else []

    report, ready_ids = _collect_state(repo_root=repo_root, queue_ids=queue_ids, queue_path=queue_path)
    next_batch = ready_ids[: args.max_batch_size]
    remaining_queue = ready_ids[args.max_batch_size :]
    report["nextBatch"] = next_batch
    report["remainingQueue"] = remaining_queue

    if args.report_file:
        _write_report(report, args.report_file)

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        _print_text(report, next_batch, remaining_queue, args.include_blocked)

    if args.fail_on_blocked and queue_ids:
        blocked_queue_ids = {item["id"] for item in report["blocked"] if item["id"] in set(queue_ids)}
        if blocked_queue_ids:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
