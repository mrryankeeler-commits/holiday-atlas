#!/usr/bin/env python3
"""Report queue-only enrichment entries that are safe cleanup candidates."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


QUEUE_PATTERNS = (
    re.compile(r"^\|\s*\[\s*\]\s*\|\s*\d+\s*\|\s*([a-z0-9-]+)\s*\|", flags=re.MULTILINE),
    re.compile(r"^- \[\s*\]\s*`([a-z0-9-]+)`", flags=re.MULTILINE),
)


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root,
        help="Repository root (defaults to parent of scripts directory).",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Reserved for a future explicit apply mode. Currently reports only.",
    )
    return parser.parse_args()


def _run_plan_enrichment_batch(repo_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(repo_root / "scripts" / "plan_enrichment_batch.py"),
        "--format",
        "json",
        "--repo-root",
        str(repo_root),
    ]
    result = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
        raise SystemExit(result.returncode)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"plan_enrichment_batch.py did not return valid JSON: {exc}") from exc


def _repo_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def _parse_unchecked_ids(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    ids: list[str] = []
    seen: set[str] = set()
    for pattern in QUEUE_PATTERNS:
        for match in pattern.finditer(text):
            loc_id = match.group(1).strip()
            if loc_id and loc_id not in seen:
                ids.append(loc_id)
                seen.add(loc_id)
    return ids


def _find_checklist_sources(repo_root: Path, planner_queue_file: str | None) -> list[Path]:
    sources: list[Path] = []

    if planner_queue_file:
        queue_path = repo_root / planner_queue_file
        if queue_path.exists():
            sources.append(queue_path)

    import_batch_matches = sorted((repo_root / "docs").glob("import-batch-*.md"))
    if import_batch_matches:
        latest_import_batch = import_batch_matches[-1]
        if latest_import_batch not in sources:
            sources.append(latest_import_batch)

    return sources


def _build_report(repo_root: Path, plan_report: dict[str, Any]) -> dict[str, Any]:
    queue_only_entries = plan_report.get("queueOnlyPending") or []
    queue_only_ids = [str(entry.get("id")) for entry in queue_only_entries if str(entry.get("id", "")).strip()]
    planner_queue_file = plan_report.get("queue", {}).get("file")
    source_paths = _find_checklist_sources(repo_root, planner_queue_file)

    source_details: list[dict[str, Any]] = []
    occurrences: dict[str, list[str]] = {loc_id: [] for loc_id in queue_only_ids}
    for source_path in source_paths:
        unchecked_ids = _parse_unchecked_ids(source_path)
        source_rel = _repo_rel(source_path, repo_root)
        source_details.append(
            {
                "file": source_rel,
                "uncheckedIds": unchecked_ids,
            }
        )
        unchecked_set = set(unchecked_ids)
        for loc_id in queue_only_ids:
            if loc_id in unchecked_set:
                occurrences[loc_id].append(source_rel)

    candidates: list[dict[str, Any]] = []
    for loc_id in queue_only_ids:
        candidates.append(
            {
                "id": loc_id,
                "sources": occurrences.get(loc_id, []),
                "missingFromSources": not bool(occurrences.get(loc_id)),
            }
        )

    return {
        "summary": {
            "queueOnlyPending": len(queue_only_ids),
            "sourceFilesScanned": len(source_details),
            "safeCleanupCandidates": len(candidates),
            "applySupported": False,
        },
        "planner": {
            "queueFile": planner_queue_file,
        },
        "sources": source_details,
        "safeCleanupCandidates": candidates,
        "applyNote": (
            "Dry-run only. Automatic queue cleanup is disabled because queue state is duplicated across "
            "multiple markdown tracking files with different semantics, so auto-editing them would be ambiguous."
        ),
    }


def _print_text(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print("Queue reconcile report")
    print(f"- plannerQueueFile: {report['planner']['queueFile'] or '-'}")
    print(f"- queueOnlyPending: {summary['queueOnlyPending']}")
    print(f"- sourceFilesScanned: {summary['sourceFilesScanned']}")
    print(f"- safeCleanupCandidates: {summary['safeCleanupCandidates']}")
    print(f"- applySupported: {'yes' if summary['applySupported'] else 'no'}")

    if report["sources"]:
        print("\nSources")
        for source in report["sources"]:
            ids = ", ".join(source["uncheckedIds"]) if source["uncheckedIds"] else "-"
            print(f"- {source['file']}: {ids}")

    if report["safeCleanupCandidates"]:
        print("\nSafe queue cleanup candidates")
        for candidate in report["safeCleanupCandidates"]:
            if candidate["sources"]:
                print(f"- {candidate['id']}: present in {', '.join(candidate['sources'])}")
            else:
                print(f"- {candidate['id']}: not found in scanned sources")
    else:
        print("\nSafe queue cleanup candidates")
        print("- none")

    print("\nApply mode")
    print(f"- {report['applyNote']}")


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()

    plan_report = _run_plan_enrichment_batch(repo_root)
    report = _build_report(repo_root, plan_report)

    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        _print_text(report)

    if args.apply:
        print("\nNo files were changed.", file=sys.stderr)
        print(report["applyNote"], file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
