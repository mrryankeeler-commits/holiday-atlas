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
import math
import statistics
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "locations" / "index.json"
LOCATIONS_DIR = ROOT / "data" / "locations"
FAILURES_LOG_PATH = ROOT / "scripts" / "output" / "enrichment_failures.jsonl"

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
WIND_KMH_TO_MPH = 0.621371

# Monthly serialization contract (per month label key)
# - avg_temp_c
# - avg_high_c
# - avg_low_c
# - apparent_temp_c
# - relative_humidity_pct
# - dew_point_c
# - rainfall_mm
# - rain_mm
# - snowfall_cm
# - precipitation_hours
# - cloud_cover_pct
# - sunshine_hours
# - sunrise
# - sunset
# - daylight_hours
# - mean_wind_speed_mph
# - max_wind_speed_mph
# - max_gusts_mph
# - dominant_wind_direction_deg
# - shortwave_radiation_sum
# - comfort_labels.feels_like_label
# - comfort_labels.humidity_label
# - comfort_labels.mugginess_label
# - comfort_labels.cloudiness_label
# - comfort_labels.wind_label

DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_mean",
    "relative_humidity_2m_mean",
    "dew_point_2m_mean",
    "precipitation_sum",
    "snowfall_sum",
    "precipitation_hours",
    "rain_sum",
    "cloud_cover_mean",
    "sunshine_duration",
    "daylight_duration",
    "wind_speed_10m_mean",
    "wind_speed_10m_max",
    "wind_gusts_10m_max",
    "wind_direction_10m_dominant",
    "shortwave_radiation_sum",
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


def _kmh_to_mph(value_kmh: float | int | None) -> float | None:
    if value_kmh is None:
        return None
    return round(float(value_kmh) * WIND_KMH_TO_MPH, 2)


def _circular_mean_deg(values: list[float | int | None]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    if not clean:
        return None
    radians = [math.radians(v) for v in clean]
    sin_mean = statistics.mean(math.sin(r) for r in radians)
    cos_mean = statistics.mean(math.cos(r) for r in radians)
    if sin_mean == 0 and cos_mean == 0:
        return None
    return round((math.degrees(math.atan2(sin_mean, cos_mean)) + 360.0) % 360.0, 2)


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


def _humidity_label(relative_humidity_pct: float | None) -> str | None:
    if relative_humidity_pct is None:
        return None
    if relative_humidity_pct < 35:
        return "dry"
    if relative_humidity_pct < 60:
        return "comfortable"
    if relative_humidity_pct < 75:
        return "humid"
    return "very humid"


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


def _wind_label(wind_mph: float | None) -> str | None:
    if wind_mph is None:
        return None
    if wind_mph < 6:
        return "light"
    if wind_mph < 12:
        return "breezy"
    if wind_mph < 22:
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


def _is_monthly_dataset_null_only(monthly: dict[str, dict[str, Any]]) -> bool:
    for month_values in monthly.values():
        for value in month_values.values():
            if value is not None:
                return False
    return True


def _append_failure_log(*, location_id: str, endpoint: str, error_message: str) -> None:
    FAILURES_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": location_id,
        "endpoint": endpoint,
        "error_message": error_message,
        "logged_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }
    with FAILURES_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _fetch_with_state(
    *, location_id: str, endpoint: str, fn: Any, default: Any = None, **kwargs: Any
) -> tuple[bool, Any, str | None]:
    try:
        return True, fn(**kwargs), None
    except (HTTPError, URLError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
        message = f"{type(exc).__name__}: {exc}"
        _append_failure_log(location_id=location_id, endpoint=endpoint, error_message=message)
        return False, default, message


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
        humidity_mean = _safe_mean(month_vals("relative_humidity_2m_mean", month_num))
        dew_mean = _safe_mean(month_vals("dew_point_2m_mean", month_num))
        cloud_mean = _safe_mean(month_vals("cloud_cover_mean", month_num))
        wind_speed_mean = _safe_mean(month_vals("wind_speed_10m_mean", month_num))
        wind_speed_max_mean = _safe_mean(month_vals("wind_speed_10m_max", month_num))

        rain_entries = [
            (years_by_index[i], (daily.get("rain_sum") or [None])[i] if i < len(daily.get("rain_sum") or []) else None)
            for i in month_idxs
        ]
        precip_entries = [
            (years_by_index[i], (daily.get("precipitation_sum") or [None])[i] if i < len(daily.get("precipitation_sum") or []) else None)
            for i in month_idxs
        ]
        snowfall_entries = [
            (years_by_index[i], (daily.get("snowfall_sum") or [None])[i] if i < len(daily.get("snowfall_sum") or []) else None)
            for i in month_idxs
        ]
        precipitation_hours_entries = [
            (
                years_by_index[i],
                (daily.get("precipitation_hours") or [None])[i]
                if i < len(daily.get("precipitation_hours") or [])
                else None,
            )
            for i in month_idxs
        ]
        shortwave_radiation_entries = [
            (
                years_by_index[i],
                (daily.get("shortwave_radiation_sum") or [None])[i]
                if i < len(daily.get("shortwave_radiation_sum") or [])
                else None,
            )
            for i in month_idxs
        ]

        sunrise_vals = month_vals("sunrise", month_num)
        sunset_vals = month_vals("sunset", month_num)

        monthly[label] = {
            "avg_temp_c": temp_mean,
            "avg_high_c": _safe_mean(month_vals("temperature_2m_max", month_num)),
            "avg_low_c": _safe_mean(month_vals("temperature_2m_min", month_num)),
            "apparent_temp_c": apparent_mean,
            "relative_humidity_pct": humidity_mean,
            "dew_point_c": dew_mean,
            "rainfall_mm": _safe_yearly_month_total_average(precip_entries),
            "rain_mm": _safe_yearly_month_total_average(rain_entries),
            "snowfall_cm": _safe_yearly_month_total_average(snowfall_entries),
            "precipitation_hours": _safe_yearly_month_total_average(precipitation_hours_entries),
            "cloud_cover_pct": cloud_mean,
            "sunshine_hours": _seconds_to_hours(_safe_mean(month_vals("sunshine_duration", month_num))),
            "sunrise": _safe_median_time_iso(sunrise_vals),
            "sunset": _safe_median_time_iso(sunset_vals),
            "daylight_hours": _seconds_to_hours(_safe_mean(month_vals("daylight_duration", month_num))),
            "mean_wind_speed_mph": _kmh_to_mph(wind_speed_mean),
            "max_wind_speed_mph": _kmh_to_mph(wind_speed_max_mean),
            "max_gusts_mph": _kmh_to_mph(_safe_mean(month_vals("wind_gusts_10m_max", month_num))),
            "dominant_wind_direction_deg": _circular_mean_deg(month_vals("wind_direction_10m_dominant", month_num)),
            "shortwave_radiation_sum": _safe_yearly_month_total_average(shortwave_radiation_entries),
            "comfort_labels": {
                "feels_like_label": _feels_like_label(apparent_mean),
                "humidity_label": _humidity_label(humidity_mean),
                "mugginess_label": _mugginess_label(dew_mean),
                "cloudiness_label": _cloudiness_label(cloud_mean),
                "wind_label": _wind_label(_kmh_to_mph(wind_speed_mean)),
            },
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

    fetch_state: dict[str, dict[str, Any]] = {
        "geocoding": {"fetch_ok": False, "error_message": None},
        "archive": {"fetch_ok": False, "error_message": None},
        "elevation": {"fetch_ok": False, "error_message": None},
    }

    geo_ok, geo, geo_err = _fetch_with_state(
        location_id=location_id,
        endpoint="geocoding",
        fn=_fetch_geocoding,
        default={},
        city=city,
        country=country,
    )
    fetch_state["geocoding"] = {"fetch_ok": geo_ok, "error_message": geo_err}

    lat = geo.get("latitude", location_index_entry.get("lat"))
    lng = geo.get("longitude", location_index_entry.get("lng"))
    if lat is None or lng is None:
        raise ValueError("Missing coordinates from geocoding/index")
    lat = float(lat)
    lng = float(lng)

    elevation_m = geo.get("elevation")
    if elevation_m is not None:
        fetch_state["elevation"] = {"fetch_ok": True, "error_message": None}
    else:
        elev_ok, elevation_m, elev_err = _fetch_with_state(
            location_id=location_id,
            endpoint="elevation",
            fn=_fetch_elevation,
            default=None,
            lat=lat,
            lng=lng,
        )
        fetch_state["elevation"] = {"fetch_ok": elev_ok, "error_message": elev_err}

    archive_ok, archive, archive_err = _fetch_with_state(
        location_id=location_id,
        endpoint="archive",
        fn=_fetch_archive,
        default={},
        lat=lat,
        lng=lng,
    )
    fetch_state["archive"] = {"fetch_ok": archive_ok, "error_message": archive_err}

    monthly: dict[str, dict[str, Any]] | None = None
    if archive_ok:
        daily = archive.get("daily")
        if isinstance(daily, dict):
            monthly = _build_monthly_from_daily(daily)
            if _is_monthly_dataset_null_only(monthly):
                monthly = None
                fetch_state["archive"] = {
                    "fetch_ok": False,
                    "error_message": "Archive payload produced null-only monthly climate dataset",
                }
                _append_failure_log(
                    location_id=location_id,
                    endpoint="archive",
                    error_message="Archive payload produced null-only monthly climate dataset",
                )
        else:
            fetch_state["archive"] = {"fetch_ok": False, "error_message": "Archive payload missing daily object"}
            _append_failure_log(
                location_id=location_id,
                endpoint="archive",
                error_message="Archive payload missing daily object",
            )

    source_obj = {
        "provider": "open-meteo",
        "geocoding_endpoint": GEOCODING_ENDPOINT,
        "elevation_endpoint": ELEVATION_ENDPOINT,
        "archive_endpoint": ARCHIVE_ENDPOINT,
        "start_date": HISTORICAL_START,
        "end_date": HISTORICAL_END,
        "timezone": TIMEZONE,
        "daily_variables": DAILY_VARIABLES,
        "status": fetch_state,
    }

    has_any_upstream = bool(geo_ok or archive_ok or fetch_state["elevation"]["fetch_ok"])
    if has_any_upstream:
        payload["meta"] = {
            "elevation_m": round(float(elevation_m), 1) if elevation_m is not None else None,
            "population": geo.get("population"),
            "timezone": (archive.get("timezone") if isinstance(archive, dict) else None) or geo.get("timezone"),
            "admin1": geo.get("admin1"),
            "admin2": geo.get("admin2"),
            "climate_koppen": geo.get("climate_koppen") or geo.get("climate") or None,
            "climate_summary": geo.get("climate_summary") or None,
        }

    if monthly is not None:
        payload["climate"] = {
            "source": source_obj,
            "monthly": monthly,
        }

        payload["humidity"] = {
            "monthly_relative_humidity_2m_mean": {
                month: monthly[month]["relative_humidity_pct"] for month in MONTH_ORDER
            },
            "source": source_obj,
        }
    elif has_any_upstream and "climate" in payload and isinstance(payload["climate"], dict):
        existing_source = payload["climate"].get("source")
        if isinstance(existing_source, dict):
            existing_source["status"] = fetch_state

    return payload, {"id": location_id, "path": str(location_path), "fetch_state": fetch_state}


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
