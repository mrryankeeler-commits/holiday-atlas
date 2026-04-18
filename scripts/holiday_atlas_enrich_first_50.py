#!/usr/bin/env python3
"""Enrich Holiday Atlas location files using Open-Meteo APIs.

Scope for this PoC run:
- Reads only the first 50 entries from data/locations/index.json.
- Writes file updates only for:
  * andorra-la-vella
  * accra-ghana
  * beppu-japan

For each processed destination:
- Preserves existing top-level fields.
- Leaves existing `months` array unchanged.
- Adds/updates `meta`, `climate`, and `humidity` blocks.
"""

from __future__ import annotations

import json
import statistics
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "locations" / "index.json"
LOCATIONS_DIR = ROOT / "data" / "locations"

FIRST_N = 50
POC_WRITE_IDS = {"andorra-la-vella", "accra-ghana", "beppu-japan"}

GEOCODING_ENDPOINT = "https://geocoding-api.open-meteo.com/v1/search"
ELEVATION_ENDPOINT = "https://api.open-meteo.com/v1/elevation"
ARCHIVE_ENDPOINT = "https://archive-api.open-meteo.com/v1/archive"

HISTORICAL_START = "1991-01-01"
HISTORICAL_END = "2020-12-31"
TIMEZONE = "auto"

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NUM_TO_LABEL = {i + 1: label for i, label in enumerate(MONTH_ORDER)}

DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "relative_humidity_2m_mean",
    "dew_point_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "cloud_cover_mean",
    "sunshine_duration",
    "daylight_duration",
    "wind_speed_10m_mean",
    "wind_gusts_10m_max",
    "sunrise",
    "sunset",
]


def _fetch_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    query = urllib.parse.urlencode(params, doseq=True)
    full_url = f"{url}?{query}"
    with urllib.request.urlopen(full_url, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _safe_mean(values: list[float | int | None]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return None
    return round(sum(clean) / len(clean), 2)


def _safe_yearly_month_total_average(entries: list[tuple[int, float | int | None]]) -> float | None:
    yearly_totals: dict[int, float] = defaultdict(float)
    yearly_has_data: dict[int, bool] = defaultdict(bool)
    for year, val in entries:
        if val is None:
            continue
        yearly_totals[year] += float(val)
        yearly_has_data[year] = True

    totals = [total for year, total in yearly_totals.items() if yearly_has_data.get(year)]
    if not totals:
        return None
    return round(sum(totals) / len(totals), 2)


def _safe_median_time_iso(times: list[str | None]) -> str | None:
    seconds: list[int] = []
    for raw in times:
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(str(raw))
        except ValueError:
            continue
        seconds.append(dt.hour * 3600 + dt.minute * 60 + dt.second)

    if not seconds:
        return None

    median_seconds = int(statistics.median(seconds))
    hours = (median_seconds // 3600) % 24
    minutes = (median_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def _seconds_to_hours(value: float | int | None) -> float | None:
    if value is None:
        return None
    return round(float(value) / 3600.0, 2)


def _mugginess_label(dew_point_c: float | None) -> str | None:
    if dew_point_c is None:
        return None
    if dew_point_c < 10:
        return "dry"
    if dew_point_c < 16:
        return "comfortable"
    if dew_point_c < 20:
        return "muggy"
    return "very muggy"


def _cloudiness_label(cloud_pct: float | None) -> str | None:
    if cloud_pct is None:
        return None
    if cloud_pct < 25:
        return "mostly clear"
    if cloud_pct < 50:
        return "partly cloudy"
    if cloud_pct < 75:
        return "mostly cloudy"
    return "overcast"


def _wind_label(wind_kph: float | None) -> str | None:
    if wind_kph is None:
        return None
    if wind_kph < 10:
        return "light"
    if wind_kph < 20:
        return "breezy"
    if wind_kph < 35:
        return "windy"
    return "very windy"


def _feels_like_label(apparent_c: float | None) -> str | None:
    if apparent_c is None:
        return None
    if apparent_c < 5:
        return "cold"
    if apparent_c < 15:
        return "cool"
    if apparent_c < 25:
        return "comfortable"
    if apparent_c < 32:
        return "warm"
    return "hot"


def _pick_best_geocoding_result(results: list[dict[str, Any]], city: str, country: str) -> dict[str, Any] | None:
    if not results:
        return None

    city_l = city.lower().strip()
    country_l = country.lower().strip()

    exact = [
        r
        for r in results
        if str(r.get("name", "")).lower().strip() == city_l
        and str(r.get("country", "")).lower().strip() == country_l
    ]
    if exact:
        return exact[0]

    by_country = [r for r in results if str(r.get("country", "")).lower().strip() == country_l]
    if by_country:
        return by_country[0]

    return results[0]


def _fetch_geocoding(city: str, country: str) -> dict[str, Any]:
    payload = _fetch_json(
        GEOCODING_ENDPOINT,
        {
            "name": city,
            "country": country,
            "count": 10,
            "language": "en",
            "format": "json",
        },
    )
    results = payload.get("results") or []
    if not isinstance(results, list):
        raise ValueError("Geocoding payload missing results list")

    pick = _pick_best_geocoding_result(results, city=city, country=country)
    if not pick:
        raise ValueError(f"No geocoding result for {city}, {country}")
    return pick


def _fetch_elevation(lat: float, lng: float) -> float | None:
    payload = _fetch_json(ELEVATION_ENDPOINT, {"latitude": lat, "longitude": lng})
    elevations = payload.get("elevation")
    if isinstance(elevations, list) and elevations:
        val = elevations[0]
        return float(val) if val is not None else None
    if isinstance(elevations, (int, float)):
        return float(elevations)
    return None


def _fetch_archive(lat: float, lng: float) -> dict[str, Any]:
    return _fetch_json(
        ARCHIVE_ENDPOINT,
        {
            "latitude": lat,
            "longitude": lng,
            "start_date": HISTORICAL_START,
            "end_date": HISTORICAL_END,
            "timezone": TIMEZONE,
            "daily": DAILY_VARIABLES,
        },
    )


def _build_monthly_from_daily(daily: dict[str, list[Any]]) -> dict[str, dict[str, Any]]:
    dates = daily.get("time") or []
    if not isinstance(dates, list) or not dates:
        raise ValueError("Archive payload missing daily.time")

    indexes_by_month: dict[int, list[int]] = defaultdict(list)
    years_by_index: dict[int, int] = {}
    for idx, date_str in enumerate(dates):
        dt = datetime.strptime(str(date_str), "%Y-%m-%d")
        indexes_by_month[dt.month].append(idx)
        years_by_index[idx] = dt.year

    def month_vals(metric: str, month_num: int) -> list[Any]:
        series = daily.get(metric) or []
        if not isinstance(series, list):
            return []
        return [series[i] if i < len(series) else None for i in indexes_by_month.get(month_num, [])]

    monthly: dict[str, dict[str, Any]] = {}
    for month_num in range(1, 13):
        label = MONTH_NUM_TO_LABEL[month_num]
        month_idxs = indexes_by_month.get(month_num, [])

        temp_mean = _safe_mean(month_vals("temperature_2m_mean", month_num))
        apparent_mean = _safe_mean(month_vals("apparent_temperature_mean", month_num))
        dew_mean = _safe_mean(month_vals("dew_point_2m_mean", month_num))
        cloud_mean = _safe_mean(month_vals("cloud_cover_mean", month_num))
        wind_mean = _safe_mean(month_vals("wind_speed_10m_mean", month_num))

        rain_entries = [
            (years_by_index[i], (daily.get("rain_sum") or [None])[i] if i < len(daily.get("rain_sum") or []) else None)
            for i in month_idxs
        ]
        precip_entries = [
            (years_by_index[i], (daily.get("precipitation_sum") or [None])[i] if i < len(daily.get("precipitation_sum") or []) else None)
            for i in month_idxs
        ]

        sunrise_vals = month_vals("sunrise", month_num)
        sunset_vals = month_vals("sunset", month_num)

        monthly[label] = {
            "temperature_c_mean": temp_mean,
            "temperature_c_max_mean": _safe_mean(month_vals("temperature_2m_max", month_num)),
            "temperature_c_min_mean": _safe_mean(month_vals("temperature_2m_min", month_num)),
            "apparent_temperature_c_mean": apparent_mean,
            "apparent_temperature_c_max_mean": _safe_mean(month_vals("apparent_temperature_max", month_num)),
            "apparent_temperature_c_min_mean": _safe_mean(month_vals("apparent_temperature_min", month_num)),
            "relative_humidity_pct_mean": _safe_mean(month_vals("relative_humidity_2m_mean", month_num)),
            "dew_point_c_mean": dew_mean,
            "cloud_cover_pct_mean": cloud_mean,
            "daylight_hours_mean": _seconds_to_hours(_safe_mean(month_vals("daylight_duration", month_num))),
            "sunshine_hours_mean": _seconds_to_hours(_safe_mean(month_vals("sunshine_duration", month_num))),
            "rainfall_mm": _safe_yearly_month_total_average(precip_entries),
            "rain_mm": _safe_yearly_month_total_average(rain_entries),
            "wind_kph_mean": wind_mean,
            "wind_gust_kph_mean": _safe_mean(month_vals("wind_gusts_10m_max", month_num)),
            "sunrise_local_median": _safe_median_time_iso(sunrise_vals),
            "sunset_local_median": _safe_median_time_iso(sunset_vals),
            "mugginess_label": _mugginess_label(dew_mean),
            "cloudiness_label": _cloudiness_label(cloud_mean),
            "wind_label": _wind_label(wind_mean),
            "feels_like_label": _feels_like_label(apparent_mean),
        }

    return monthly


def _enrich_location(location_index_entry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    location_id = str(location_index_entry["id"])
    location_path = LOCATIONS_DIR / f"{location_id}.json"
    if not location_path.exists():
        raise FileNotFoundError(f"Location file not found: {location_path}")

    payload = json.loads(location_path.read_text(encoding="utf-8"))

    city = str(location_index_entry.get("city") or payload.get("city") or "").strip()
    country = str(location_index_entry.get("country") or payload.get("country") or "").strip()
    if not city or not country:
        raise ValueError("Missing city/country for geocoding")

    geo = _fetch_geocoding(city=city, country=country)

    lat = float(geo.get("latitude", location_index_entry.get("lat")))
    lng = float(geo.get("longitude", location_index_entry.get("lng")))
    elevation_m = geo.get("elevation")
    if elevation_m is None:
        elevation_m = _fetch_elevation(lat=lat, lng=lng)

    archive = _fetch_archive(lat=lat, lng=lng)
    daily = archive.get("daily")
    if not isinstance(daily, dict):
        raise ValueError("Archive payload missing daily object")

    monthly = _build_monthly_from_daily(daily)

    source_obj = {
        "provider": "open-meteo",
        "geocoding_endpoint": GEOCODING_ENDPOINT,
        "elevation_endpoint": ELEVATION_ENDPOINT,
        "archive_endpoint": ARCHIVE_ENDPOINT,
        "start_date": HISTORICAL_START,
        "end_date": HISTORICAL_END,
        "timezone": TIMEZONE,
        "daily_variables": DAILY_VARIABLES,
    }

    payload["meta"] = {
        "elevation_m": round(float(elevation_m), 1) if elevation_m is not None else None,
        "population": geo.get("population"),
        "timezone": archive.get("timezone") or geo.get("timezone"),
        "admin1": geo.get("admin1"),
        "admin2": geo.get("admin2"),
        "climate_koppen": geo.get("climate_koppen") or geo.get("climate") or None,
        "climate_summary": geo.get("climate_summary") or None,
    }

    payload["climate"] = {
        "source": source_obj,
        "monthly": monthly,
    }

    payload["humidity"] = {
        "monthly_relative_humidity_2m_mean": {
            month: monthly[month]["relative_humidity_pct_mean"] for month in MONTH_ORDER
        },
        "source": source_obj,
    }

    return payload, {"id": location_id, "path": str(location_path)}


def main() -> int:
    index_payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    if not isinstance(index_payload, list):
        raise ValueError("data/locations/index.json must be an array")

    targets = index_payload[:FIRST_N]
    print(f"Loaded {len(index_payload)} index entries; processing first {len(targets)}.")
    print(f"PoC write is restricted to: {', '.join(sorted(POC_WRITE_IDS))}")

    success = 0
    failures = 0

    for entry in targets:
        location_id = str(entry.get("id", "")).strip()
        if not location_id:
            failures += 1
            print("[FAIL] missing id in index entry")
            continue

        try:
            enriched_payload, info = _enrich_location(entry)
            if location_id in POC_WRITE_IDS:
                out_path = Path(info["path"])
                out_path.write_text(json.dumps(enriched_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"[OK] {location_id}: enriched + wrote {out_path}")
            else:
                print(f"[OK] {location_id}: enriched (no write; PoC write restriction)")
            success += 1
        except Exception as exc:  # per-destination guardrail for batch continuity
            failures += 1
            print(f"[FAIL] {location_id}: {exc}")

    print(f"Done. success={success} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
