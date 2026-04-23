#!/usr/bin/env python3
"""Verify climate provenance and CSV-to-JSON consistency for live locations."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CLIMATE_KEYS = ("avg", "hi", "lo", "daylight", "cld", "rain")
MONTH_LABELS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH_LOOKUP = {label.lower(): label for label in MONTH_LABELS}
MONTH_LOOKUP.update({str(i): MONTH_LABELS[i - 1] for i in range(1, 13)})


def _normalized_col_key(value: str) -> str:
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _row_get(row: dict[str, str], col: str, aliases: tuple[str, ...] = ()) -> str:
    candidates = (col, *aliases)
    for candidate in candidates:
        if candidate in row:
            return str(row.get(candidate, ""))

    normalized_map = {_normalized_col_key(key): key for key in row.keys()}
    for candidate in candidates:
        mapped = normalized_map.get(_normalized_col_key(candidate))
        if mapped is not None:
            return str(row.get(mapped, ""))
    return ""


def normalize_month(raw: str) -> str:
    value = str(raw).strip()
    key = value.lower()
    if key in MONTH_LOOKUP:
        return MONTH_LOOKUP[key]
    if len(key) >= 3 and key[:3] in MONTH_LOOKUP:
        return MONTH_LOOKUP[key[:3]]
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to repository root (defaults to parent of scripts directory).",
    )
    parser.add_argument(
        "--fail-on-unverified",
        action="store_true",
        help="Fail if any location is marked unverified.",
    )
    return parser.parse_args()


def load_rows_by_url(csv_files: list[Path]) -> dict[str, dict[str, dict[str, str]]]:
    rows_by_url: dict[str, dict[str, dict[str, str]]] = {}
    for csv_file in csv_files:
        with csv_file.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                url = _row_get(row, "Source URL", ("Source",)).strip()
                if not url:
                    continue
                month = normalize_month(_row_get(row, "Month"))
                if month:
                    rows_by_url.setdefault(url, {})[month] = row
    return rows_by_url


def expected_month(row: dict[str, str]) -> dict[str, int | float]:
    return {
        "avg": round(float(_row_get(row, "Avg Temp (°C)", ("Avg temp (°C)",)))),
        "hi": round(float(_row_get(row, "Avg High (°C)", ("Avg high (°C)",)))),
        "lo": round(float(_row_get(row, "Avg Low (°C)", ("Avg low (°C)",)))),
        "daylight": round(float(_row_get(row, "Daylight (h/day)")), 1),
        "cld": round(float(_row_get(row, "Cloud Cover (%)", ("Cloud cover (%)",)))),
        "rain": round(float(_row_get(row, "Rainfall (mm)"))),
    }


def main() -> None:
    args = parse_args()
    locations_dir = args.repo_root / "data" / "locations"
    csv_files = sorted((args.repo_root / "data" / "climate" / "uploads").glob("*.csv"))

    rows_by_url = load_rows_by_url(csv_files)
    verified = 0
    unverified = 0
    failures: list[str] = []

    for file_path in sorted(locations_dir.glob("*.json")):
        if file_path.name == "index.json":
            continue
        data = json.loads(file_path.read_text(encoding="utf-8"))
        source = data.get("source") or {}
        climate_rows = source.get("climate") or []
        source_url = climate_rows[0].get("url", "").strip() if climate_rows else ""

        if source.get("climateVerified"):
            verified += 1
            if not source_url:
                failures.append(f"{file_path.name}: verified=true but source URL missing")
                continue

            by_month = rows_by_url.get(source_url)
            if not by_month or len(by_month) < 12:
                failures.append(f"{file_path.name}: verified=true but source URL not found with 12 CSV months")
                continue

            for month in data["months"]:
                row = by_month.get(month["m"])
                if row is None:
                    failures.append(f"{file_path.name}: missing CSV month '{month['m']}' for source URL")
                    continue
                exp = expected_month(row)
                got = {k: month[k] for k in CLIMATE_KEYS}
                if exp != got:
                    failures.append(
                        f"{file_path.name}:{month['m']}: CSV climate != JSON climate (exp={exp}, got={got})"
                    )
        else:
            unverified += 1

    if args.fail_on_unverified and unverified > 0:
        failures.append(f"{unverified} locations are unverified")

    print(f"verified={verified} unverified={unverified} failures={len(failures)}")
    for failure in failures:
        print(f"FAIL: {failure}")

    if failures:
        raise SystemExit(1)

    print("provenance verification OK")


if __name__ == "__main__":
    main()
