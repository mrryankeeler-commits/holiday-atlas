#!/usr/bin/env python3
"""Scan location JSON files for leftover generic travel-copy signatures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SIGNATURES = {
    "generic_desc": {
        "needles": ["rewards timing around the local weather curve"],
        "label": "Generic description",
    },
    "generic_wifi_note": {
        "needles": ["Typical visitor connectivity in"],
        "label": "Generic wifi note",
    },
    "generic_visa_note": {
        "needles": ["UK/Irish passport holders should verify"],
        "label": "Generic visa note",
    },
    "flight_note_review": {
        "needles": [
            "has no airport;",
            "uses one main airport",
            "has two major airports",
        ],
        "label": "Flight note review candidate",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--locations-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "locations",
        help="Directory containing live location JSON files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    locations = sorted(path for path in args.locations_dir.glob("*.json") if path.name != "index.json")

    findings: dict[str, list[str]] = {key: [] for key in SIGNATURES}

    for path in locations:
        text = path.read_text(encoding="utf-8")
        for key, config in SIGNATURES.items():
            if any(needle in text for needle in config["needles"]):
                findings[key].append(path.stem)

    summary = {
        key: {
            "label": config["label"],
            "count": len(findings[key]),
            "destinations": findings[key],
        }
        for key, config in SIGNATURES.items()
    }

    print("Travel copy audit")
    for key, info in summary.items():
        print(f"- {info['label']}: {info['count']}")
        if info["destinations"]:
            print(f"  {', '.join(info['destinations'])}")

    print("\nJSON summary")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
