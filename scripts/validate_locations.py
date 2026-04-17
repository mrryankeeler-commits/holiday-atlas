#!/usr/bin/env python3
"""Validate Holiday Atlas location data contract."""

import argparse
import json
import re
from pathlib import Path

REQ_MONTH_KEYS = {"m", "avg", "hi", "lo", "daylight", "cld", "rain", "busy", "ac", "fl"}
REQUIRED_TOP_LEVEL = {"id", "city", "country", "region", "desc", "hls", "todo", "prac", "sweet", "months"}
REQUIRED_PRAC_ARRAYS = {"alerts", "airports", "bestFor"}
OPTIONAL_PRAC_STRING_FIELDS = {"visa", "currency", "fltNote", "lang", "tz"}
INDEX_REQUIRED_FIELDS = {"id", "city", "country", "region", "lat", "lng"}
TODO_REQUIRED_FIELDS = {"name", "cat", "desc"}
PLACEHOLDER_ALERT_BLOCKS = {
    (
        "Weather variability can affect day plans; keep one flexible slot in your itinerary.",
        "Book high-demand attractions in advance during peak months.",
        "Use licensed transport options for late arrivals and airport transfers.",
    ),
    (
        "Reserve popular attractions early in peak months.",
        "Keep one flexible day for weather-dependent plans.",
    ),
}
GENERIC_PRAC_TEXT = {
    "",
    "-",
    "n/a",
    "na",
    "none",
    "unknown",
    "tbd",
    "to be confirmed",
    "coming soon",
    "not sure",
    "not provided",
}

# Known repeated boilerplate signatures that should be replaced with destination-specific copy.
GENERIC_CONTENT_PATTERNS = {
    "desc": (
        re.compile(r"\bperfect\s+for\s+a\s+city\s+break\b", flags=re.IGNORECASE),
        re.compile(r"\bgreat\s+mix\s+of\s+culture,\s*food,\s*and\s+nightlife\b", flags=re.IGNORECASE),
        re.compile(r"\boffers\s+something\s+for\s+every\s+traveller\b", flags=re.IGNORECASE),
    ),
    "sweet": (
        re.compile(r"\bbest\s+time\s+to\s+visit\s+is\s+spring\s+and\s+autumn\b", flags=re.IGNORECASE),
        re.compile(r"\bideal\s+for\s+year[- ]round\s+travel\b", flags=re.IGNORECASE),
        re.compile(r"\bshoulder\s+months\s+offer\s+the\s+best\s+balance\b", flags=re.IGNORECASE),
    ),
    "tag": (
        re.compile(r"^(couples|families|solo\s+travel(?:lers?)?|foodies?|history\s+lovers?)$", flags=re.IGNORECASE),
        re.compile(r"^(adventure|culture|beach|nature|city\s*break)$", flags=re.IGNORECASE),
    ),
    "hls": (
        re.compile(r"\bvisit\s+the\s+old\s+town\b", flags=re.IGNORECASE),
        re.compile(r"\bexplore\s+local\s+markets\s+and\s+cafes\b", flags=re.IGNORECASE),
    ),
    "todo_desc": (
        re.compile(r"\bdiscover\s+the\s+city'?s\s+top\s+landmarks\b", flags=re.IGNORECASE),
        re.compile(r"\benjoy\s+local\s+food\s+and\s+culture\b", flags=re.IGNORECASE),
    ),
}


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


def _is_generic_prac_text(value: str) -> bool:
    cleaned = " ".join(value.strip().split())
    if cleaned.lower() in GENERIC_PRAC_TEXT:
        return True
    return bool(re.fullmatch(r"(same as country|local time|varies|standard)", cleaned, flags=re.IGNORECASE))


def _normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def _first_pattern_match(value: str, patterns: tuple[re.Pattern[str], ...]) -> str | None:
    for pattern in patterns:
        if pattern.search(value):
            return pattern.pattern
    return None


def _looks_generic_desc(text: str, field: str) -> str | None:
    cleaned = _normalize_text(text)
    if not cleaned:
        return "empty"
    return _first_pattern_match(cleaned, GENERIC_CONTENT_PATTERNS[field])


def _looks_generic_tag(text: str) -> str | None:
    cleaned = _normalize_text(text)
    if not cleaned:
        return "empty"
    return _first_pattern_match(cleaned, GENERIC_CONTENT_PATTERNS["tag"])


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

    for field in ("desc", "sweet"):
        value = data.get(field)
        if isinstance(value, str) and not value.strip():
            add_error(errors, file_path, f"field '{field}' must be a non-empty string")
        elif isinstance(value, str):
            generic_reason = _looks_generic_desc(value, field)
            if generic_reason:
                add_error(
                    errors,
                    file_path,
                    f"{field} appears generic (match={generic_reason!r}, text={value!r}); use destination-specific copy",
                )

    country = str(data.get("country", "")).strip()
    region = str(data.get("region", "")).strip()
    if country and region and re.fullmatch(rf"{re.escape(country)}\s+region", region, flags=re.IGNORECASE):
        add_error(errors, file_path, "region must be specific; avoid generic '<country> region' patterns")

    source = data.get("source")
    if isinstance(source, dict) and source.get("draftOnly") is True:
        add_error(errors, file_path, "draft-only skeleton detected (source.draftOnly=true); enrich and remove draft flag")

    hls = data.get("hls")
    if isinstance(hls, list):
        if not hls:
            add_error(errors, file_path, "hls must include at least one highlight")
        for idx, item in enumerate(hls):
            if not isinstance(item, str) or not item.strip():
                add_error(errors, file_path, f"hls[{idx}] must be a non-empty string")
                continue
            generic_reason = _first_pattern_match(_normalize_text(item), GENERIC_CONTENT_PATTERNS["hls"])
            if generic_reason:
                add_error(
                    errors,
                    file_path,
                    f"hls[{idx}] appears generic (match={generic_reason!r}, text={item!r})",
                )

    todo = data.get("todo")
    if isinstance(todo, list):
        if not todo:
            add_error(errors, file_path, "todo must include at least one activity")
        for idx, item in enumerate(todo):
            if not isinstance(item, dict):
                add_error(errors, file_path, f"todo[{idx}] expected object, got {type(item).__name__}")
                continue
            missing_todo = sorted(TODO_REQUIRED_FIELDS - set(item.keys()))
            if missing_todo:
                add_error(errors, file_path, f"todo[{idx}] missing required fields: {', '.join(missing_todo)}")
            for key in sorted(TODO_REQUIRED_FIELDS):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    add_error(errors, file_path, f"todo[{idx}].{key} must be a non-empty string")
            todo_desc = item.get("desc")
            if isinstance(todo_desc, str) and todo_desc.strip():
                generic_reason = _first_pattern_match(_normalize_text(todo_desc), GENERIC_CONTENT_PATTERNS["todo_desc"])
                if generic_reason:
                    add_error(
                        errors,
                        file_path,
                        f"todo[{idx}].desc appears generic (match={generic_reason!r}, text={todo_desc!r})",
                    )

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
            elif field in prac and field != "airports":
                for idx, item in enumerate(prac[field]):
                    if not isinstance(item, str) or not item.strip():
                        add_error(errors, file_path, f"prac.{field}[{idx}] must be a non-empty string")
                    elif field == "bestFor":
                        generic_reason = _looks_generic_tag(item)
                        if generic_reason:
                            add_error(
                                errors,
                                file_path,
                                f"prac.bestFor[{idx}] appears generic (match={generic_reason!r}, text={item!r}); be destination-specific",
                            )

        alerts = prac.get("alerts")
        if isinstance(alerts, list) and tuple(alerts) in PLACEHOLDER_ALERT_BLOCKS:
            add_error(
                errors,
                file_path,
                "prac.alerts matches a known placeholder block; replace with destination-specific alerts",
            )

        airports = prac.get("airports")
        if isinstance(airports, list):
            if not airports:
                note = prac.get("airportsExceptionNote")
                if not isinstance(note, str) or not note.strip():
                    add_error(
                        errors,
                        file_path,
                        "prac.airports cannot be empty unless prac.airportsExceptionNote explains the exception",
                    )
            for idx, item in enumerate(airports):
                if not isinstance(item, dict):
                    add_error(errors, file_path, f"prac.airports[{idx}] expected object, got {type(item).__name__}")
                    continue
                for key in ("name", "code"):
                    value = item.get(key)
                    if not isinstance(value, str) or not value.strip():
                        add_error(errors, file_path, f"prac.airports[{idx}].{key} must be a non-empty string")
                if "km" in item and (
                    isinstance(item["km"], bool) or not isinstance(item["km"], (int, float)) or item["km"] < 0
                ):
                    add_error(errors, file_path, f"prac.airports[{idx}].km must be a non-negative number")
                if "dgw" in item and not isinstance(item["dgw"], bool):
                    add_error(errors, file_path, f"prac.airports[{idx}].dgw must be a boolean")

        if "directGW" in prac and not isinstance(prac["directGW"], bool):
            add_error(errors, file_path, "invalid prac.directGW (expected boolean)")

        for field in sorted(OPTIONAL_PRAC_STRING_FIELDS):
            if field in prac and not isinstance(prac[field], str):
                add_error(errors, file_path, f"invalid prac.{field} (expected string)")
            elif field in {"visa", "currency", "lang", "tz"} and isinstance(prac.get(field), str):
                value = prac[field].strip()
                if not value or _is_generic_prac_text(value):
                    add_error(errors, file_path, f"prac.{field} must be destination-specific (not empty/generic)")

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
