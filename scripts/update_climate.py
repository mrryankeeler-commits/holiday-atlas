#!/usr/bin/env python3
"""Update monthly climate fields for all locations using Open-Meteo APIs.

This script reads `data/locations/index.json`, resolves coordinates via Open-Meteo
geocoding, fetches historical daily weather, and rewrites each
`data/locations/<id>.json` `months` block with climatological monthly values.

Fields updated per month: avg, hi, lo, sun, cld, rain, rise, set.
Fields preserved per month (if present): busy, ac, fl.
"""

from __future__ import annotations

import json
import argparse
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "locations" / "index.json"
LOCATIONS_DIR = ROOT / "data" / "locations"

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

START_DATE = "2016-01-01"
END_DATE = "2025-12-31"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fetch_json(url: str, retries: int = 3, backoff_seconds: float = 1.5) -> Dict[str, Any]:
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < retries:
                time.sleep(backoff_seconds * attempt)
    raise RuntimeError(f"Request failed after {retries} attempts: {url}\n{last_exc}")


def geocode_city(city: str, country: str) -> Dict[str, Any]:
    params = urllib.parse.urlencode({"name": city, "count": 10, "language": "en", "format": "json"})
    payload = fetch_json(f"{GEOCODE_URL}?{params}")
    results = payload.get("results") or []
    if not results:
        raise RuntimeError(f"No geocoding results for {city}, {country}")

    country_l = country.lower()

    # Prefer exact country match first.
    for result in results:
        if str(result.get("country", "")).lower() == country_l:
            return result

    # Then relaxed contains matching for special names.
    for result in results:
        result_country = str(result.get("country", "")).lower()
        if country_l in result_country or result_country in country_l:
            return result

    return results[0]


def hhmm_to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def minutes_to_hhmm(total_minutes: float) -> str:
    rounded = int(round(total_minutes)) % (24 * 60)
    return f"{rounded // 60:02d}:{rounded % 60:02d}"


def compute_monthly_climate(daily: Dict[str, List[Any]], existing_months: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_month: Dict[int, Dict[str, List[float]]] = {
        i: {
            "avg": [],
            "hi": [],
            "lo": [],
            "sun_hours": [],
            "cloud": [],
            "sunrise_min": [],
            "sunset_min": [],
        }
        for i in range(1, 13)
    }
    rain_by_month_year: Dict[tuple[int, int], float] = defaultdict(float)

    dates = daily["time"]
    t_mean = daily["temperature_2m_mean"]
    t_max = daily["temperature_2m_max"]
    t_min = daily["temperature_2m_min"]
    sunshine = daily["sunshine_duration"]
    cloud = daily["cloud_cover_mean"]
    precip = daily["precipitation_sum"]
    sunrise = daily["sunrise"]
    sunset = daily["sunset"]

    for i, iso_date in enumerate(dates):
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        month = dt.month
        year = dt.year

        def add_if_number(bucket: str, value: Any) -> None:
            if value is None:
                return
            by_month[month][bucket].append(float(value))

        add_if_number("avg", t_mean[i])
        add_if_number("hi", t_max[i])
        add_if_number("lo", t_min[i])
        if sunshine[i] is not None:
            by_month[month]["sun_hours"].append(float(sunshine[i]) / 3600.0)
        add_if_number("cloud", cloud[i])

        if precip[i] is not None:
            rain_by_month_year[(month, year)] += float(precip[i])

        if sunrise[i]:
            by_month[month]["sunrise_min"].append(float(hhmm_to_minutes(str(sunrise[i]).split("T", 1)[1][:5])))
        if sunset[i]:
            by_month[month]["sunset_min"].append(float(hhmm_to_minutes(str(sunset[i]).split("T", 1)[1][:5])))

    existing_by_month = {m.get("m"): m for m in existing_months if isinstance(m, dict)}

    out: List[Dict[str, Any]] = []
    for idx, short in enumerate(MONTHS, start=1):
        rain_totals = [v for (m, _y), v in rain_by_month_year.items() if m == idx]
        row = {
            "m": short,
            "avg": int(round(statistics.mean(by_month[idx]["avg"]))) if by_month[idx]["avg"] else None,
            "hi": int(round(statistics.mean(by_month[idx]["hi"]))) if by_month[idx]["hi"] else None,
            "lo": int(round(statistics.mean(by_month[idx]["lo"]))) if by_month[idx]["lo"] else None,
            "sun": int(round(statistics.mean(by_month[idx]["sun_hours"]))) if by_month[idx]["sun_hours"] else None,
            "cld": int(round(statistics.mean(by_month[idx]["cloud"]))) if by_month[idx]["cloud"] else None,
            "rain": int(round(statistics.mean(rain_totals))) if rain_totals else None,
            "rise": minutes_to_hhmm(statistics.mean(by_month[idx]["sunrise_min"])) if by_month[idx]["sunrise_min"] else None,
            "set": minutes_to_hhmm(statistics.mean(by_month[idx]["sunset_min"])) if by_month[idx]["sunset_min"] else None,
        }

        prev = existing_by_month.get(short, {})
        row["busy"] = prev.get("busy", 3)
        row["ac"] = prev.get("ac", 3)
        row["fl"] = prev.get("fl", 3)
        out.append(row)

    return out


def update_location(location_entry: Dict[str, Any]) -> None:
    loc_id = location_entry["id"]
    city = location_entry["city"]
    country = location_entry["country"]

    path = LOCATIONS_DIR / f"{loc_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing file for id={loc_id}: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    geo = geocode_city(city=city, country=country)
    lat = geo["latitude"]
    lon = geo["longitude"]

    params = urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "timezone": "auto",
            "daily": ",".join(
                [
                    "temperature_2m_mean",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "sunshine_duration",
                    "cloud_cover_mean",
                    "precipitation_sum",
                    "sunrise",
                    "sunset",
                ]
            ),
        }
    )

    payload = fetch_json(f"{ARCHIVE_URL}?{params}")
    daily = payload.get("daily")
    if not daily:
        raise RuntimeError(f"Archive API missing daily payload for {loc_id}")

    data["months"] = compute_monthly_climate(daily=daily, existing_months=data.get("months", []))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {loc_id} ({city}, {country})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh monthly climate blocks from Open-Meteo.")
    parser.add_argument("--id", dest="location_id", help="Optional single location id to update.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if args.location_id:
        index = [loc for loc in index if loc.get("id") == args.location_id]
        if not index:
            print(f"No location found in index for id={args.location_id}", file=sys.stderr)
            return 2
    failures: List[str] = []

    for loc in index:
        try:
            update_location(loc)
        except Exception as exc:  # noqa: BLE001
            msg = f"{loc.get('id')}: {exc}"
            failures.append(msg)
            print(f"ERROR {msg}", file=sys.stderr)

    if failures:
        print("\nCompleted with failures:", file=sys.stderr)
        for f in failures:
            print(f" - {f}", file=sys.stderr)
        return 1

    print("\nAll location climate blocks updated successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
