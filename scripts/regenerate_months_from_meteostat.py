#!/usr/bin/env python3
"""One-time Meteostat-backed monthly climate regeneration for Holiday Atlas."""

from __future__ import annotations

import argparse
import calendar
import json
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import meteostat as ms
from astral import LocationInfo
from astral.sun import sun
from zoneinfo import ZoneInfo

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# 45 destinations added in commit f26c6bf
TARGET_IDS = [
    "andorra-la-vella", "arugam-bay", "astana", "athens", "bergen", "bled", "braga", "bratislava", "budapest",
    "cairo", "catania", "colombo", "copenhagen", "darjeeling", "faro", "florence", "gdansk", "goa", "granada",
    "guilin", "ha-giang", "hurghada", "jambiani", "kandy", "katowice", "krakow", "marrakech", "meteora", "munnar",
    "osaka", "palermo", "paphos", "prague", "riga", "rome", "samarkand", "sanya", "seville", "tallinn", "toledo",
    "trieste", "turin", "valletta", "vienna", "zakopane",
]

# Fixed coordinates/timezones avoid geocoding dependency/rate limits in CI
CITY_META: Dict[str, Tuple[float, float, str]] = {
    "andorra-la-vella": (42.5078, 1.5211, "Europe/Andorra"),
    "arugam-bay": (6.8404, 81.8306, "Asia/Colombo"),
    "astana": (51.1694, 71.4491, "Asia/Almaty"),
    "athens": (37.9838, 23.7275, "Europe/Athens"),
    "bergen": (60.3913, 5.3221, "Europe/Oslo"),
    "bled": (46.3692, 14.1136, "Europe/Ljubljana"),
    "braga": (41.5454, -8.4265, "Europe/Lisbon"),
    "bratislava": (48.1486, 17.1077, "Europe/Bratislava"),
    "budapest": (47.4979, 19.0402, "Europe/Budapest"),
    "cairo": (30.0444, 31.2357, "Africa/Cairo"),
    "catania": (37.5079, 15.0830, "Europe/Rome"),
    "colombo": (6.9271, 79.8612, "Asia/Colombo"),
    "copenhagen": (55.6761, 12.5683, "Europe/Copenhagen"),
    "darjeeling": (27.0410, 88.2663, "Asia/Kolkata"),
    "faro": (37.0194, -7.9304, "Europe/Lisbon"),
    "florence": (43.7696, 11.2558, "Europe/Rome"),
    "gdansk": (54.3520, 18.6466, "Europe/Warsaw"),
    "goa": (15.2993, 74.1240, "Asia/Kolkata"),
    "granada": (37.1773, -3.5986, "Europe/Madrid"),
    "guilin": (25.2742, 110.2902, "Asia/Shanghai"),
    "ha-giang": (22.8233, 104.9836, "Asia/Ho_Chi_Minh"),
    "hurghada": (27.2579, 33.8116, "Africa/Cairo"),
    "jambiani": (-6.3122, 39.5340, "Africa/Dar_es_Salaam"),
    "kandy": (7.2906, 80.6337, "Asia/Colombo"),
    "katowice": (50.2649, 19.0238, "Europe/Warsaw"),
    "krakow": (50.0647, 19.9450, "Europe/Warsaw"),
    "marrakech": (31.6295, -7.9811, "Africa/Casablanca"),
    "meteora": (39.7217, 21.6300, "Europe/Athens"),
    "munnar": (10.0889, 77.0595, "Asia/Kolkata"),
    "osaka": (34.6937, 135.5023, "Asia/Tokyo"),
    "palermo": (38.1157, 13.3615, "Europe/Rome"),
    "paphos": (34.7720, 32.4297, "Asia/Nicosia"),
    "prague": (50.0755, 14.4378, "Europe/Prague"),
    "riga": (56.9496, 24.1052, "Europe/Riga"),
    "rome": (41.9028, 12.4964, "Europe/Rome"),
    "samarkand": (39.6542, 66.9597, "Asia/Samarkand"),
    "sanya": (18.2528, 109.5119, "Asia/Shanghai"),
    "seville": (37.3891, -5.9845, "Europe/Madrid"),
    "tallinn": (59.4370, 24.7536, "Europe/Tallinn"),
    "toledo": (39.8628, -4.0273, "Europe/Madrid"),
    "trieste": (45.6495, 13.7768, "Europe/Rome"),
    "turin": (45.0703, 7.6869, "Europe/Rome"),
    "valletta": (35.8989, 14.5146, "Europe/Malta"),
    "vienna": (48.2082, 16.3738, "Europe/Vienna"),
    "zakopane": (49.2992, 19.9496, "Europe/Warsaw"),
}


def _to_int(value: float, fallback: int) -> int:
    if pd.isna(value):
        return fallback
    return int(round(float(value)))


def _to_float(value: float, fallback: float, ndigits: int = 1) -> float:
    if pd.isna(value):
        return round(fallback, ndigits)
    return round(float(value), ndigits)


def daylight_hours(lat: float, lon: float, tz: str, month: int) -> Tuple[str, str, float]:
    loc = LocationInfo(latitude=lat, longitude=lon, timezone=tz)
    dt = date(2024, month, 15)
    event = sun(loc.observer, date=dt, tzinfo=ZoneInfo(tz))
    rise = event["sunrise"].strftime("%H:%M")
    set_ = event["sunset"].strftime("%H:%M")
    hours = (event["sunset"] - event["sunrise"]).total_seconds() / 3600
    return rise, set_, hours


def calc_sun_hrs_day(tsun: float, month: int) -> float | None:
    if pd.isna(tsun):
        return None
    tsun_f = float(tsun)
    # Meteostat tsun can appear as monthly total minutes. If already small, treat as daily hours.
    if tsun_f <= 24:
        return tsun_f
    days = calendar.monthrange(2024, month)[1]
    return tsun_f / 60.0 / days


def build_months(df: pd.DataFrame, existing_months: List[dict], lat: float, lon: float, tz: str, preserve_indices: bool) -> List[dict]:
    by_month = df.groupby(df.index.month).mean(numeric_only=True)
    if len(by_month.index) < 12:
        missing = [m for m in range(1, 13) if m not in by_month.index]
        raise RuntimeError(f"Missing monthly climate rows: {missing}")

    out: List[dict] = []
    for month in range(1, 13):
        row = by_month.loc[month]
        base = existing_months[month - 1] if existing_months and len(existing_months) == 12 else {}

        avg = _to_int(row.get("tavg"), int(base.get("avg", 18)))
        hi = _to_int(row.get("tmax"), int(base.get("hi", avg + 4)))
        lo = _to_int(row.get("tmin"), int(base.get("lo", avg - 4)))
        rain = max(0, _to_int(row.get("prcp"), int(base.get("rain", 0))))

        rise, set_, daylen = daylight_hours(lat, lon, tz, month)

        sun_hrs = calc_sun_hrs_day(row.get("tsun"), month)
        if sun_hrs is None:
            # Fallback proxy if station lacks sunshine observations
            wet_penalty = min(5.0, rain / 70.0)
            sun_hrs = max(1.0, min(daylen - 0.5, daylen * 0.62 - wet_penalty))
        sun_hrs = round(max(0.5, min(daylen, sun_hrs)), 1)

        cld = int(round(max(8, min(92, (1 - (sun_hrs / max(daylen, 1))) * 100))))

        if preserve_indices:
            busy = int(base.get("busy", 3))
            ac = int(base.get("ac", 3))
            fl = int(base.get("fl", 3))
        else:
            # Simple seasonality heuristic from weather quality + precipitation
            score = (avg / 6.0) + (sun_hrs / 2.0) - (rain / 60.0)
            if score >= 5.5:
                busy = 5
            elif score >= 4.5:
                busy = 4
            elif score >= 3.3:
                busy = 3
            else:
                busy = 2
            ac = min(5, max(1, busy + (1 if busy >= 4 else 0)))
            fl = min(5, max(1, busy + (1 if month in (7, 8, 12) else 0)))

        out.append({
            "m": MONTH_LABELS[month - 1],
            "avg": avg,
            "hi": hi,
            "lo": lo,
            "sun": sun_hrs,
            "cld": cld,
            "rain": rain,
            "rise": rise,
            "set": set_,
            "busy": busy,
            "ac": ac,
            "fl": fl,
        })

    return out


def regenerate(repo_root: Path, start_year: int, end_year: int, ids: Iterable[str], preserve_indices: bool) -> None:
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)

    for loc_id in ids:
        if loc_id not in CITY_META:
            raise KeyError(f"Missing CITY_META coordinates for '{loc_id}'")

        lat, lon, tz = CITY_META[loc_id]
        path = repo_root / "data" / "locations" / f"{loc_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))

        point = ms.Point(lat, lon)
        ts = ms.monthly(point, start, end)
        if ts is None:
            df = None
        elif hasattr(ts, "fetch"):
            df = ts.fetch()
        else:
            df = ts

        if df is None or df.empty:
            stations_api = ms.Stations() if hasattr(ms, "Stations") else ms.stations()
            stations = stations_api.nearby(lat, lon).fetch(5)
            for station_id in stations.index.tolist():
                station_ts = ms.monthly(station_id, start, end)
                if station_ts is None:
                    continue
                station_df = station_ts.fetch() if hasattr(station_ts, "fetch") else station_ts
                if station_df is not None and not station_df.empty:
                    df = station_df
                    print(f"fallback station used for {loc_id}: {station_id}")
                    break

        if df is None or df.empty:
            print(f"warning: no Meteostat data returned for {loc_id}; keeping existing months")
            continue

        payload["months"] = build_months(df, payload.get("months", []), lat, lon, tz, preserve_indices)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"updated {loc_id}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to repository root (defaults to parent of scripts directory)",
    )
    p.add_argument("--start-year", type=int, default=2014)
    p.add_argument("--end-year", type=int, default=2024)
    p.add_argument("--all-locations", action="store_true", help="Process all TARGET_IDS")
    p.add_argument("--ids", nargs="*", default=[], help="Specific location IDs to process")
    p.add_argument("--recompute-seasonality", action="store_true", help="Recompute busy/ac/fl instead of preserving")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ids = TARGET_IDS if args.all_locations or not args.ids else args.ids
    regenerate(
        repo_root=args.repo_root,
        start_year=args.start_year,
        end_year=args.end_year,
        ids=ids,
        preserve_indices=not args.recompute_seasonality,
    )


if __name__ == "__main__":
    main()
