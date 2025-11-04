#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Filter boost_sets directory (copy all - all enhancements player-relevant).

Usage: uv run scripts/filter_boost_sets.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916/boost_sets")
OUTPUT_DIR = Path("/Users/w/code/mids-hero-web/filtered_data/boost_sets")
MANIFEST_ENTRIES: List[Dict] = []

def copy_boost_sets_directory():
    """Copy entire boost_sets directory."""
    print(f"Copying boost_sets from {SOURCE_DIR} to {OUTPUT_DIR}...")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    shutil.copytree(SOURCE_DIR, OUTPUT_DIR)

    # Count files
    total_files = len(list(OUTPUT_DIR.rglob("*")))
    print(f"✓ Copied {total_files} boost set files")

    # Generate manifest entries
    for file_path in OUTPUT_DIR.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(Path("/Users/w/code/mids-hero-web/filtered_data"))
            MANIFEST_ENTRIES.append({
                "source": f"boost_sets/{file_path.relative_to(OUTPUT_DIR)}",
                "reason": "layer_3_special_directory:boost_sets",
                "layer": 3,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

    return total_files

def save_manifest_fragment():
    """Save manifest entries for synthesis agent."""
    manifest_file = Path("/Users/w/code/mids-hero-web/filtered_data/boost_sets_manifest.json")

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "boost_sets",
            "total_files": len(MANIFEST_ENTRIES),
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Boost Sets Processor ===\n")

    total = copy_boost_sets_directory()
    save_manifest_fragment()

    print(f"\n✅ Boost sets processing complete")
    print(f"Total files: {total}")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
