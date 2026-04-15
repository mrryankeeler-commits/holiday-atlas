#!/usr/bin/env python3
"""Validate Holiday Atlas location data contract."""

import argparse
import json
from pathlib import Path

REQ = {"m", "avg", "hi", "lo", "daylight", "cld", "rain", "busy", "ac", "fl"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to repository root (defaults to parent of scripts directory).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.repo_root / "data" / "locations"
    index = json.loads((root / "index.json").read_text(encoding="utf-8"))
    ids = [row["id"] for row in index]

    assert len(ids) == len(set(ids)), "Duplicate IDs in index.json"
    for loc_id in ids:
        file_path = root / f"{loc_id}.json"
        assert file_path.exists(), f"Missing location file: {file_path}"

    for file_path in root.glob("*.json"):
        if file_path.name == "index.json":
            continue
        data = json.loads(file_path.read_text(encoding="utf-8"))
        assert data["id"] == file_path.stem, f"ID mismatch in {file_path}"
        months = data["months"]
        assert len(months) == 12, f"Expected 12 months in {file_path}"
        for row in months:
            keys = set(row.keys())
            assert REQ.issubset(keys), f"Missing required month keys in {file_path}: {REQ - keys}"
            assert keys.issubset(REQ), f"Unexpected month keys in {file_path}: {keys - REQ}"

    print("validation OK")


if __name__ == "__main__":
    main()
