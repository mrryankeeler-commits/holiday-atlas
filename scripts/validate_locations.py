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
GENERIC_CONTENT_PATTERNS = {
    "desc": (
        re.compile(r"^a great destination for travelers seeking .*", flags=re.IGNORECASE),
        re.compile(r"^this destination offers a mix of culture, food, and scenery\.?$", flags=re.IGNORECASE),
        re.compile(r"^perfect for a short break or longer stay\.?$", flags=re.IGNORECASE),
    ),
    "sweet": (
        re.compile(r"^best (time|months) to visit: .*", flags=re.IGNORECASE),
        re.compile(r"^visit in (spring|summer|autumn|fall|winter) for the best weather\.?$", flags=re.IGNORECASE),
        re.compile(r"^ideal year-round depending on your preferences\.?$", flags=re.IGNORECASE),
    ),
    "tag": (
        re.compile(r"^couples$", flags=re.IGNORECASE),
        re.compile(r"^friends$", flags=re.IGNORECASE),
        re.compile(r"^solo$", flags=re.IGNORECASE),
        re.compile(r"^everyone$", flags=re.IGNORECASE),
        re.compile(r"^all travelers$", flags=re.IGNORECASE),
    ),
    "hls": (
        re.compile(r"^historic old town$", flags=re.IGNORECASE),
        re.compile(r"^local food scene$", flags=re.IGNORECASE),
        re.compile(r"^beautiful views$", flags=re.IGNORECASE),
        re.compile(r"^friendly locals$", flags=re.IGNORECASE),
    ),
    "todo_desc": (
        re.compile(r"^a great way to experience local culture\.?$", flags=re.IGNORECASE),
        re.compile(r"^perfect for photos and sightseeing\.?$", flags=re.IGNORECASE),
        re.compile(r"^ideal for travelers of all ages\.?$", flags=re.IGNORECASE),
    ),
}
DEPARTURE_AIRPORT_CODES = ("LGW", "LCY")
NO_DIRECT_ROUTE_PATTERNS = (
    re.compile(r"\bno\s+(?:practical\s+|routine\s+|regular\s+)?(?:direct|non[-\s]?stop)\b", flags=re.IGNORECASE),
    re.compile(r"\bwithout\s+(?:practical\s+)?(?:direct|non[-\s]?stop)\b", flags=re.IGNORECASE),
)
NO_AIRPORT_PROSE_PATTERNS = (
    re.compile(r"\bhas no (?:major\s+)?(?:commercial\s+)?airport\b", flags=re.IGNORECASE),
    re.compile(r"\bno (?:major\s+)?commercial airport\b", flags=re.IGNORECASE),
    re.compile(r"\bno airport of (?:its|their) own\b", flags=re.IGNORECASE),
    re.compile(r"\bno airport\b", flags=re.IGNORECASE),
)


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
    return bool(
        re.fullmatch(
            r"(same as country|local time|varies|standard|see destination local timezone)",
            cleaned,
            flags=re.IGNORECASE,
        )
    )


def _looks_like_timezone(value: str) -> bool:
    cleaned = " ".join(value.strip().split())
    timezone_id = re.search(r"\b[A-Za-z_]+/[A-Za-z_]+(?:/[A-Za-z_]+)?\b", cleaned)
    utc_offset = re.search(r"\b(?:UTC|GMT)\s*[+\-−]\s*\d{1,2}(?::\d{2})?\b", cleaned, flags=re.IGNORECASE)
    return bool(timezone_id or utc_offset)


def _looks_like_language_detail(value: str) -> bool:
    cleaned = " ".join(value.strip().split())
    if re.search(r"\blocal language\b", cleaned, flags=re.IGNORECASE):
        return False

    # Require at least one alphabetic token that isn't generic filler.
    tokens = re.findall(r"[A-Za-z][A-Za-z'\-]+", cleaned)
    generic_tokens = {
        "and",
        "or",
        "plus",
        "local",
        "language",
        "languages",
        "english",
        "widely",
        "spoken",
        "some",
        "basic",
        "varies",
        "variable",
        "availability",
    }
    specific_tokens = [tok for tok in tokens if tok.lower() not in generic_tokens]
    return bool(specific_tokens)


def _looks_like_country_specific_visa_detail(value: str) -> bool:
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return False

    # Accept if concrete country/policy clues appear.
    concrete_policy_patterns = (
        r"\b(UK|U\.K\.|Irish|Ireland|US|U\.S\.|USA|EU|EEA|Schengen)\b",
        r"\b(visa[-\s]?free|e-?visa|visa on arrival|transit visa|residence permit)\b",
        r"\b\d+\s*(day|days|month|months)\b",
    )
    if any(re.search(pattern, cleaned, flags=re.IGNORECASE) for pattern in concrete_policy_patterns):
        return True

    # Reject pure generic warnings without policy context.
    pure_warning = re.fullmatch(
        r"(?:always\s+)?verify\s+(?:entry|visa|immigration)\s+(?:rules|requirements)(?:\s+before\s+(?:travel|booking|departure))?\.?",
        cleaned,
        flags=re.IGNORECASE,
    )
    return not bool(pure_warning)


def _matches_any_pattern(value: str, pattern_key: str) -> bool:
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return True
    return any(pattern.search(cleaned) for pattern in GENERIC_CONTENT_PATTERNS[pattern_key])


def _looks_generic_desc(text: str) -> bool:
    return _matches_any_pattern(text, "desc")


def _looks_generic_tag(text: str) -> bool:
    return _matches_any_pattern(text, "tag")


def _looks_generic_sweet(text: str) -> bool:
    return _matches_any_pattern(text, "sweet")


def _looks_generic_hls(text: str) -> bool:
    return _matches_any_pattern(text, "hls")


def _looks_generic_todo_desc(text: str) -> bool:
    return _matches_any_pattern(text, "todo_desc")


def _matches_any_regex(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    cleaned = " ".join(str(text).strip().split())
    return any(pattern.search(cleaned) for pattern in patterns)


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
    desc = data.get("desc")
    if isinstance(desc, str) and _looks_generic_desc(desc):
        add_error(errors, file_path, f"field 'desc' is generic boilerplate: {desc!r}")
    sweet = data.get("sweet")
    if isinstance(sweet, str) and _looks_generic_sweet(sweet):
        add_error(errors, file_path, f"field 'sweet' is generic boilerplate: {sweet!r}")

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
            elif _looks_generic_hls(item):
                add_error(errors, file_path, f"hls[{idx}] matches known template boilerplate: {item!r}")

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
            desc_value = item.get("desc")
            if isinstance(desc_value, str) and _looks_generic_todo_desc(desc_value):
                add_error(errors, file_path, f"todo[{idx}].desc matches known template boilerplate: {desc_value!r}")

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
                    elif field == "bestFor" and _looks_generic_tag(item):
                        add_error(errors, file_path, f"prac.bestFor[{idx}] must be destination-specific: {item!r}")

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
        if "directFrom" in prac:
            direct_from = prac["directFrom"]
            if not isinstance(direct_from, dict):
                add_error(errors, file_path, "invalid prac.directFrom (expected object)")
            else:
                for code in DEPARTURE_AIRPORT_CODES:
                    if code in direct_from and not isinstance(direct_from[code], bool):
                        add_error(errors, file_path, f"invalid prac.directFrom.{code} (expected boolean)")
        else:
            direct_from = {}

        flt_note = prac.get("fltNote", "")
        has_no_direct_phrase = isinstance(flt_note, str) and _matches_any_regex(flt_note, NO_DIRECT_ROUTE_PATTERNS)
        has_no_airport_phrase = isinstance(flt_note, str) and _matches_any_regex(flt_note, NO_AIRPORT_PROSE_PATTERNS)
        dest_direct_lgw = bool(prac.get("directGW")) or bool(direct_from.get("LGW"))
        dest_direct_any = any(bool(direct_from.get(code)) for code in DEPARTURE_AIRPORT_CODES) or bool(prac.get("directGW"))

        if dest_direct_lgw and (has_no_direct_phrase or has_no_airport_phrase):
            add_error(
                errors,
                file_path,
                "destination direct LGW is true but prac.fltNote states no direct/no-airport routing for the destination",
            )
        if dest_direct_any and has_no_airport_phrase:
            add_error(
                errors,
                file_path,
                "destination direct flags must be false when prac.fltNote says the destination has no airport",
            )

        for field in sorted(OPTIONAL_PRAC_STRING_FIELDS):
            if field in prac and not isinstance(prac[field], str):
                add_error(errors, file_path, f"invalid prac.{field} (expected string)")
            elif field in {"visa", "currency", "lang", "tz"} and isinstance(prac.get(field), str):
                value = prac[field].strip()
                if not value or _is_generic_prac_text(value):
                    if field == "tz":
                        add_error(errors, file_path, "prac.tz must include concrete timezone, not placeholder")
                    elif field == "lang":
                        add_error(errors, file_path, "prac.lang must include concrete language names, not placeholders")
                    elif field == "visa":
                        add_error(errors, file_path, "prac.visa must include country-specific policy context, not generic warning")
                    else:
                        add_error(errors, file_path, "prac.currency must include concrete local currency detail")
                    continue

                if field == "tz" and not _looks_like_timezone(value):
                    add_error(errors, file_path, "prac.tz must include concrete timezone, not placeholder")
                elif field == "lang" and not _looks_like_language_detail(value):
                    add_error(errors, file_path, "prac.lang must include concrete language names, not placeholders")
                elif field == "visa" and not _looks_like_country_specific_visa_detail(value):
                    add_error(errors, file_path, "prac.visa must include country-specific policy context, not generic warning")

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
