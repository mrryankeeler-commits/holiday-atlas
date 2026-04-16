#!/usr/bin/env python3
"""Validate Holiday Atlas location data contract."""

import argparse
import json
from pathlib import Path

REQ_MONTH_KEYS = {"m", "avg", "hi", "lo", "daylight", "cld", "rain", "busy", "ac", "fl"}
REQUIRED_TOP_LEVEL = {"id", "city", "country", "region", "desc", "hls", "todo", "prac", "sweet", "months"}
REQUIRED_PRAC_ARRAYS = {"alerts", "airports", "bestFor"}
OPTIONAL_PRAC_STRING_FIELDS = {"visa", "currency", "fltNote", "lang", "tz"}
INDEX_REQUIRED_FIELDS = {"id", "city", "country", "region", "lat", "lng"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to repository root (defaults to parent of scripts directory).",
    )
    return parser.parse_args()


def add_error(errors: list[str], file_path: Path, message: str) -> None:
    errors.append(f"{file_path}: {message}")


def validate_index(index_path: Path, locations_root: Path, errors: list[str]) -> list[str]:
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_error(errors, index_path, f"invalid JSON ({exc})")
        return []

    if not isinstance(index, list):
        add_error(errors, index_path, f"expected top-level array, got {type(index).__name__}")
        return []

    ids: list[str] = []
    for pos, row in enumerate(index):
        entry_label = f"entry[{pos}]"
        if not isinstance(row, dict):
            add_error(errors, index_path, f"{entry_label} expected object, got {type(row).__name__}")
            continue

        missing = sorted(INDEX_REQUIRED_FIELDS - set(row.keys()))
        if missing:
            add_error(errors, index_path, f"{entry_label} missing required fields: {', '.join(missing)}")
            continue

        loc_id = row["id"]
        if not isinstance(loc_id, str) or not loc_id:
            add_error(errors, index_path, f"{entry_label} has invalid id (expected non-empty string)")
            continue

        for coord_key, min_value, max_value in (("lat", -90, 90), ("lng", -180, 180)):
            coord_value = row.get(coord_key)
            if isinstance(coord_value, bool) or not isinstance(coord_value, (int, float)):
                add_error(errors, index_path, f"{entry_label} has invalid {coord_key} (expected number)")
                continue
            if not (min_value <= coord_value <= max_value):
                add_error(
                    errors,
                    index_path,
                    f"{entry_label} has out-of-range {coord_key} ({coord_value}; expected {min_value}..{max_value})",
                )

        ids.append(loc_id)

    duplicates = sorted({loc_id for loc_id in ids if ids.count(loc_id) > 1})
    if duplicates:
        add_error(errors, index_path, f"duplicate ids: {', '.join(duplicates)}")

    for loc_id in ids:
        file_path = locations_root / f"{loc_id}.json"
        if not file_path.exists():
            add_error(errors, file_path, "missing file referenced by data/locations/index.json")

    return ids


def validate_location(file_path: Path, errors: list[str]) -> None:
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        add_error(errors, file_path, f"invalid JSON ({exc})")
        return

    if not isinstance(data, dict):
        add_error(errors, file_path, f"expected top-level object, got {type(data).__name__}")
        return

    keys = set(data.keys())
    missing_top = sorted(REQUIRED_TOP_LEVEL - keys)
    if missing_top:
        add_error(errors, file_path, f"missing required top-level fields: {', '.join(missing_top)}")

    loc_id = data.get("id")
    if loc_id != file_path.stem:
        add_error(
            errors,
            file_path,
            f"id mismatch (json id={loc_id!r}, filename stem={file_path.stem!r})",
        )

    for field in ("hls", "todo", "months"):
        if field in data and not isinstance(data[field], list):
            add_error(errors, file_path, f"invalid field type for '{field}' (expected array)")

    prac = data.get("prac")
    if "prac" in data and not isinstance(prac, dict):
        add_error(errors, file_path, "invalid field type for 'prac' (expected object)")
    elif isinstance(prac, dict):
        missing_prac_arrays = sorted(REQUIRED_PRAC_ARRAYS - set(prac.keys()))
        if missing_prac_arrays:
            add_error(errors, file_path, f"prac missing required fields: {', '.join(missing_prac_arrays)}")

        for field in REQUIRED_PRAC_ARRAYS:
            if field in prac and not isinstance(prac[field], list):
                add_error(errors, file_path, f"invalid prac.{field} (expected array)")

        if "directGW" in prac and not isinstance(prac["directGW"], bool):
            add_error(errors, file_path, "invalid prac.directGW (expected boolean)")

        for field in sorted(OPTIONAL_PRAC_STRING_FIELDS):
            if field in prac and not isinstance(prac[field], str):
                add_error(errors, file_path, f"invalid prac.{field} (expected string)")

    months = data.get("months")
    if isinstance(months, list):
        if len(months) != 12:
            add_error(errors, file_path, f"expected 12 months, got {len(months)}")

        for idx, row in enumerate(months):
            if not isinstance(row, dict):
                add_error(errors, file_path, f"months[{idx}] expected object, got {type(row).__name__}")
                continue

            month_keys = set(row.keys())
            missing = sorted(REQ_MONTH_KEYS - month_keys)
            extra = sorted(month_keys - REQ_MONTH_KEYS)
            if missing:
                add_error(errors, file_path, f"months[{idx}] missing required keys: {', '.join(missing)}")
            if extra:
                add_error(errors, file_path, f"months[{idx}] has unexpected keys: {', '.join(extra)}")


def main() -> None:
    args = parse_args()
    locations_root = args.repo_root / "data" / "locations"
    index_path = locations_root / "index.json"

    errors: list[str] = []
    ids = validate_index(index_path=index_path, locations_root=locations_root, errors=errors)

    for file_path in sorted(locations_root.glob("*.json")):
        if file_path.name == "index.json":
            continue
        validate_location(file_path=file_path, errors=errors)

    if errors:
        print("validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    if not ids:
        print("validation OK (no indexed locations found)")
        return

    print(f"validation OK ({len(ids)} indexed locations)")


if __name__ == "__main__":
    main()
