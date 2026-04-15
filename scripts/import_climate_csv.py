#!/usr/bin/env python3
"""Import per-location climate CSV files into `data/locations/<id>.json` months arrays.

This script is intentionally provider-agnostic and does not call external APIs.
It updates climate metrics (`avg`, `hi`, `lo`, `daylight`, `cld`, `rain`) and preserves
`busy`, `ac`, and `fl` from existing data unless score overrides are explicitly enabled.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_LOOKUP = {label.lower(): label for label in MONTH_LABELS}
MONTH_LOOKUP.update({str(i): MONTH_LABELS[i - 1] for i in range(1, 13)})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, help="Directory containing one CSV per location (for example: data/climate).")
    parser.add_argument("--input-file", type=Path, help="Single CSV file to import.")
    parser.add_argument("--id", dest="location_id", help="Location id to import. Required with --input-dir for single-location runs.")
    parser.add_argument(
        "--locations-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "locations",
        help="Directory containing location JSON files (default: data/locations).",
    )

    parser.add_argument("--month-col", default="month", help="CSV column for month number/name.")
    parser.add_argument("--avg-col", default="avg", help="CSV column for average temperature.")
    parser.add_argument("--hi-col", default="hi", help="CSV column for average high temperature.")
    parser.add_argument("--lo-col", default="lo", help="CSV column for average low temperature.")
    parser.add_argument("--daylight-col", default="daylight", help="CSV column for daylight hours.")
    parser.add_argument("--cloud-col", default="cld", help="CSV column for cloud cover percentage.")
    parser.add_argument("--rain-col", default="rain", help="CSV column for rainfall amount.")

    parser.add_argument("--busy-col", default="busy", help="CSV column for busy score when --allow-score-overrides is set.")
    parser.add_argument("--ac-col", default="ac", help="CSV column for accommodation score when --allow-score-overrides is set.")
    parser.add_argument("--fl-col", default="fl", help="CSV column for flight score when --allow-score-overrides is set.")
    parser.add_argument(
        "--allow-score-overrides",
        action="store_true",
        help="Allow CSV busy/ac/fl columns to override existing values.",
    )

    args = parser.parse_args()
    if bool(args.input_dir) == bool(args.input_file):
        parser.error("Provide exactly one of --input-dir or --input-file.")
    if args.input_dir and not args.input_dir.exists():
        parser.error(f"Input directory does not exist: {args.input_dir}")
    if args.input_file and not args.input_file.exists():
        parser.error(f"Input file does not exist: {args.input_file}")
    return args


def normalize_month(raw: str) -> str:
    value = str(raw).strip()
    if not value:
        raise ValueError("Month value cannot be empty")

    key = value.lower()
    if key in MONTH_LOOKUP:
        return MONTH_LOOKUP[key]

    if len(key) >= 3 and key[:3] in {m.lower() for m in MONTH_LABELS}:
        return MONTH_LOOKUP[key[:3]]

    raise ValueError(f"Unsupported month value: {raw!r}")


def _num(row: dict[str, str], col: str, cast: type[int] | type[float]) -> int | float:
    raw = row.get(col)
    if raw is None or str(raw).strip() == "":
        raise ValueError(f"Missing value in required column '{col}'")
    val = float(str(raw).strip())
    return int(round(val)) if cast is int else round(val, 1)


def _score_value(row: dict[str, str], col: str, fallback: int) -> int:
    raw = row.get(col)
    if raw is None or str(raw).strip() == "":
        return fallback
    return int(round(float(str(raw).strip())))


def import_csv_to_location(csv_path: Path, location_path: Path, args: argparse.Namespace) -> None:
    payload = json.loads(location_path.read_text(encoding="utf-8"))
    existing_by_month = {
        str(m.get("m")): m
        for m in payload.get("months", [])
        if isinstance(m, dict) and isinstance(m.get("m"), str)
    }

    rows = list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError(f"CSV is empty: {csv_path}")

    imported: dict[str, dict[str, Any]] = {}
    for row in rows:
        month = normalize_month(row.get(args.month_col, ""))
        base = existing_by_month.get(month, {})

        item = {
            "m": month,
            "avg": _num(row, args.avg_col, int),
            "hi": _num(row, args.hi_col, int),
            "lo": _num(row, args.lo_col, int),
            "daylight": _num(row, args.daylight_col, float),
            "cld": _num(row, args.cloud_col, int),
            "rain": _num(row, args.rain_col, int),
        }

        item["busy"] = _score_value(row, args.busy_col, int(base.get("busy", 3))) if args.allow_score_overrides else int(base.get("busy", 3))
        item["ac"] = _score_value(row, args.ac_col, int(base.get("ac", 3))) if args.allow_score_overrides else int(base.get("ac", 3))
        item["fl"] = _score_value(row, args.fl_col, int(base.get("fl", 3))) if args.allow_score_overrides else int(base.get("fl", 3))

        imported[month] = item

    missing = [m for m in MONTH_LABELS if m not in imported]
    if missing:
        raise ValueError(f"Missing months in {csv_path}: {missing}")

    payload["months"] = [imported[m] for m in MONTH_LABELS]
    location_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_targets(args: argparse.Namespace) -> list[tuple[str, Path]]:
    if args.input_file:
        loc_id = args.location_id or args.input_file.stem
        return [(loc_id, args.input_file)]

    if args.location_id:
        target = args.input_dir / f"{args.location_id}.csv"
        if not target.exists():
            raise FileNotFoundError(f"Missing CSV for id '{args.location_id}': {target}")
        return [(args.location_id, target)]

    return sorted((path.stem, path) for path in args.input_dir.glob("*.csv"))


def main() -> int:
    args = parse_args()
    targets = resolve_targets(args)
    if not targets:
        print("No CSV files found to import.", file=sys.stderr)
        return 1

    for loc_id, csv_path in targets:
        location_path = args.locations_dir / f"{loc_id}.json"
        if not location_path.exists():
            raise FileNotFoundError(f"Missing location JSON for id '{loc_id}': {location_path}")
        import_csv_to_location(csv_path=csv_path, location_path=location_path, args=args)
        print(f"updated {loc_id} from {csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
