#!/usr/bin/env python3
"""Import climate CSV files into `data/locations/<id>.json` month arrays.

This script is intentionally provider-agnostic and does not call external APIs.
It updates climate metrics (`avg`, `hi`, `lo`, `daylight`, `cld`, `rain`) and preserves
`busy`, `ac`, and `fl` from existing data unless score overrides are explicitly enabled.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
import unicodedata
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
        "--location-col",
        default="location",
        help="CSV column that identifies location in a combined multi-location CSV.",
    )
    parser.add_argument("--city-col", default="city", help="CSV city column for creating missing location files.")
    parser.add_argument("--country-col", default="country", help="CSV country column for creating missing location files.")
    parser.add_argument("--region-col", default="region", help="CSV region column for creating missing location files.")
    parser.add_argument("--id-col", default="id", help="CSV id column for combined CSV mode.")
    parser.add_argument(
        "--aliases-file",
        type=Path,
        help="Optional JSON file mapping misspellings/aliases to canonical location ids.",
    )
    parser.add_argument(
        "--disable-fuzzy-match",
        action="store_true",
        help="Disable fuzzy matching of misspelled location names to existing ids.",
    )
    parser.add_argument(
        "--fuzzy-cutoff",
        type=float,
        default=0.9,
        help="Similarity threshold for fuzzy matching (0-1, default 0.9).",
    )
    parser.add_argument(
        "--create-missing",
        action="store_true",
        help="Create a new location file when one does not exist yet.",
    )
    parser.add_argument(
        "--stage-unknown-dir",
        type=Path,
        help="If provided, unknown locations are written here as pending JSON and skipped from active locations.",
    )
    parser.add_argument(
        "--default-region",
        default="Other",
        help="Fallback region value when creating a new location file and no region column is available.",
    )
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
    if args.fuzzy_cutoff < 0 or args.fuzzy_cutoff > 1:
        parser.error("--fuzzy-cutoff must be between 0 and 1")
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


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return value.strip("-")


def _token_key(value: str) -> str:
    parts = [p for p in _slugify(value).split("-") if p]
    return "-".join(sorted(parts))


def _similarity(a: str, b: str) -> float:
    direct = difflib.SequenceMatcher(None, a, b).ratio()
    tokenized = difflib.SequenceMatcher(None, _token_key(a), _token_key(b)).ratio()
    return max(direct, tokenized)


def _load_aliases(args: argparse.Namespace) -> dict[str, str]:
    if not args.aliases_file:
        return {}
    payload = json.loads(args.aliases_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Alias file must be an object map: {args.aliases_file}")
    return {_slugify(str(k)): str(v).strip() for k, v in payload.items() if str(v).strip()}


def _build_known_location_index(locations_dir: Path) -> dict[str, str]:
    index: dict[str, str] = {}
    for file_path in locations_dir.glob("*.json"):
        if file_path.name == "index.json":
            continue
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        loc_id = str(payload.get("id") or file_path.stem).strip()
        city = str(payload.get("city", "")).strip()
        country = str(payload.get("country", "")).strip()
        keys = {loc_id, file_path.stem}
        if city:
            keys.add(_slugify(city))
        if city and country:
            keys.add(_slugify(f"{city}-{country}"))
            keys.add(_slugify(f"{city}, {country}"))
        for key in keys:
            s = _slugify(key)
            if s:
                index[s] = loc_id
    return index


def _parse_location_fields(row: dict[str, str], args: argparse.Namespace) -> tuple[str, str]:
    city = str(row.get(args.city_col, "")).strip()
    country = str(row.get(args.country_col, "")).strip()
    if city and country:
        return city, country

    raw = str(row.get(args.location_col, "")).strip()
    if not raw:
        return city, country
    parts = [part.strip() for part in raw.split(",")]
    if not city:
        city = parts[0]
    if not country and len(parts) > 1:
        country = ", ".join(parts[1:]).strip()
    return city, country


def _infer_scores(month_item: dict[str, Any]) -> tuple[int, int, int]:
    avg = float(month_item["avg"])
    hi = float(month_item["hi"])
    lo = float(month_item["lo"])
    daylight = float(month_item["daylight"])
    cld = float(month_item["cld"])
    rain = float(month_item["rain"])

    seasonality = max(0.0, hi - lo)
    comfort = max(0.0, 10.0 - abs(avg - 22.0) / 2.0)
    weather_penalty = (rain / 35.0) + (cld / 30.0)
    daylight_bonus = max(0.0, (daylight - 10.0) / 1.8)

    busy = round(max(1.0, min(5.0, 1.7 + comfort * 0.23 + daylight_bonus * 0.28 - weather_penalty * 0.35 + seasonality * 0.06)))
    ac = round(max(1.0, min(5.0, 2.4 + comfort * 0.18 + (5.0 - weather_penalty) * 0.18 + seasonality * 0.08)))
    fl = round(max(1.0, min(5.0, 2.7 + comfort * 0.12 + seasonality * 0.04 - (busy - 3.0) * 0.10)))
    return int(busy), int(ac), int(fl)


def _build_new_location_payload(
    location_id: str,
    rows: list[dict[str, str]],
    imported_by_month: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    first = rows[0] if rows else {}
    city, country = _parse_location_fields(first, args)
    if not city:
        city = location_id.replace("-", " ").title()
    if not country:
        country = "Unknown"
    region = str(first.get(args.region_col, "")).strip() or args.default_region

    months: list[dict[str, Any]] = []
    for m in MONTH_LABELS:
        base = dict(imported_by_month[m])
        busy, ac, fl = _infer_scores(base)
        base.update({"busy": busy, "ac": ac, "fl": fl})
        months.append(base)

    return {
        "id": location_id,
        "city": city,
        "country": country,
        "region": region,
        "desc": f"{city} travel guide.",
        "hls": [],
        "todo": [],
        "prac": {
            "directGW": "",
            "visa": "",
            "currency": "",
            "alerts": [],
            "wifi": {"r": "", "notes": ""},
            "sim": "",
            "safety": "",
            "lang": "",
            "power": "",
        },
        "sweet": "Apr-Jun,Sep-Oct",
        "months": months,
    }


def _upsert_index_entry(location_path: Path, args: argparse.Namespace) -> None:
    payload = json.loads(location_path.read_text(encoding="utf-8"))
    index_path = args.locations_dir / "index.json"
    if not index_path.exists():
        return

    index = json.loads(index_path.read_text(encoding="utf-8"))
    entry = {k: payload[k] for k in ("id", "city", "country", "region")}
    existing_idx = next((i for i, row in enumerate(index) if row.get("id") == payload["id"]), None)
    if existing_idx is None:
        index.append(entry)
    else:
        index[existing_idx].update(entry)
    index.sort(key=lambda row: str(row.get("id", "")))
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_csv_to_location(csv_path: Path, location_path: Path, args: argparse.Namespace) -> None:
    rows = list(csv.DictReader(csv_path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError(f"CSV is empty: {csv_path}")

    payload: dict[str, Any] = {}
    existing_by_month: dict[str, dict[str, Any]] = {}
    if location_path.exists():
        payload = json.loads(location_path.read_text(encoding="utf-8"))
        existing_by_month = {
            str(m.get("m")): m
            for m in payload.get("months", [])
            if isinstance(m, dict) and isinstance(m.get("m"), str)
        }
    elif not args.create_missing:
        raise FileNotFoundError(f"Missing location JSON for id '{location_path.stem}': {location_path}")

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

    if not payload:
        payload = _build_new_location_payload(location_path.stem, rows, imported, args)
    else:
        payload["months"] = [imported[m] for m in MONTH_LABELS]
    location_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _upsert_index_entry(location_path, args)


def _location_id_from_row(row: dict[str, str], args: argparse.Namespace) -> str:
    explicit = str(row.get(args.id_col, "")).strip()
    if explicit:
        return explicit
    city, country = _parse_location_fields(row, args)
    if city and country:
        return _slugify(f"{city}-{country}")
    if city:
        return _slugify(city)
    raw = str(row.get(args.location_col, "")).strip()
    if raw:
        return _slugify(raw)
    raise ValueError("Could not infer location id; provide id column or location/city values.")


def _resolve_location_id(
    raw_id: str,
    known_index: dict[str, str],
    alias_map: dict[str, str],
    args: argparse.Namespace,
) -> tuple[str | None, str]:
    key = _slugify(raw_id)
    if key in known_index:
        return known_index[key], "exact"
    if key in alias_map:
        mapped = alias_map[key]
        return mapped, "alias"
    if args.disable_fuzzy_match or not known_index:
        return None, "unknown"

    best_key = ""
    best_score = -1.0
    for candidate in known_index.keys():
        score = _similarity(key, candidate)
        if score > best_score:
            best_key = candidate
            best_score = score
    if best_score < args.fuzzy_cutoff or not best_key:
        return None, "unknown"
    return known_index[best_key], "fuzzy"


def _stage_unknown_location(
    unresolved_id: str,
    rows: list[dict[str, str]],
    source_file: Path,
    args: argparse.Namespace,
) -> Path:
    if not args.stage_unknown_dir:
        raise FileNotFoundError(
            f"Unknown location '{unresolved_id}'. Provide alias/id, enable --create-missing, or set --stage-unknown-dir."
        )
    args.stage_unknown_dir.mkdir(parents=True, exist_ok=True)
    first = rows[0] if rows else {}
    city, country = _parse_location_fields(first, args)
    payload = {
        "id": _slugify(unresolved_id),
        "source": str(source_file),
        "city": city,
        "country": country,
        "region": str(first.get(args.region_col, "")).strip() or "",
        "rows": rows,
    }
    out_path = args.stage_unknown_dir / f"{payload['id']}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def import_combined_csv(input_file: Path, args: argparse.Namespace) -> list[str]:
    rows = list(csv.DictReader(input_file.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError(f"CSV is empty: {input_file}")

    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        loc_id = _location_id_from_row(row, args)
        grouped.setdefault(loc_id, []).append(row)

    alias_map = _load_aliases(args)
    known_index = _build_known_location_index(args.locations_dir)
    updated: list[str] = []
    staged: list[Path] = []
    grouped_resolved: dict[str, list[dict[str, str]]] = {}
    for loc_id, loc_rows in sorted(grouped.items()):
        resolved_id, resolution = _resolve_location_id(loc_id, known_index, alias_map, args)
        if resolved_id:
            grouped_resolved.setdefault(resolved_id, []).extend(loc_rows)
            if resolution != "exact":
                print(f"resolved '{loc_id}' -> '{resolved_id}' via {resolution}", file=sys.stderr)
            continue

        if args.create_missing:
            grouped_resolved.setdefault(_slugify(loc_id), []).extend(loc_rows)
            continue

        staged_path = _stage_unknown_location(loc_id, loc_rows, input_file, args)
        staged.append(staged_path)
        print(f"staged unknown location '{loc_id}' to {staged_path}", file=sys.stderr)

    for loc_id, loc_rows in sorted(grouped_resolved.items()):
        tmp_csv = input_file.with_name(f".{input_file.stem}.{loc_id}.tmp.csv")
        try:
            with tmp_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(loc_rows[0].keys()))
                writer.writeheader()
                writer.writerows(loc_rows)
            location_path = args.locations_dir / f"{loc_id}.json"
            import_csv_to_location(csv_path=tmp_csv, location_path=location_path, args=args)
            updated.append(loc_id)
        finally:
            tmp_csv.unlink(missing_ok=True)
    if staged:
        print(f"staged {len(staged)} unknown location(s)", file=sys.stderr)
    return updated


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
    if args.input_file and not args.location_id:
        updated = import_combined_csv(args.input_file, args)
        for loc_id in updated:
            print(f"updated {loc_id} from {args.input_file}")
        return 0

    targets = resolve_targets(args)
    if not targets:
        print("No CSV files found to import.", file=sys.stderr)
        return 1

    for loc_id, csv_path in targets:
        location_path = args.locations_dir / f"{loc_id}.json"
        import_csv_to_location(csv_path=csv_path, location_path=location_path, args=args)
        print(f"updated {loc_id} from {csv_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
