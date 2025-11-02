#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Review and selectively copy metadata directories.

Usage: uv run scripts/filter_metadata.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict

SOURCE_BASE = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916")
OUTPUT_BASE = Path("/Users/w/code/mids-hero-web/filtered_data")
MANIFEST_ENTRIES: List[Dict] = []

# Directories to review
METADATA_DIRS = [
    "tables",
    "tags",
    "entity_tags",
    "exclusion_groups",
    "recharge_groups"
]

def analyze_directory(dir_name: str):
    """Analyze metadata directory to determine relevance."""
    source_dir = SOURCE_BASE / dir_name

    if not source_dir.exists():
        print(f"⚠️  {dir_name} not found, skipping")
        return None

    file_count = len(list(source_dir.rglob("*")))
    print(f"\n📂 {dir_name}/")
    print(f"   Files: {file_count}")

    # Check for index.json
    index_file = source_dir / "index.json"
    if index_file.exists():
        with open(index_file) as f:
            data = json.load(f)
        print(f"   Index keys: {list(data.keys())}")

    # For now, include tables (likely needed for lookups)
    # Skip entity_tags (NPC-related)
    # Include exclusion_groups, recharge_groups (power mechanics)
    # Include tags (may be referenced)

    if dir_name in ["tables", "exclusion_groups", "recharge_groups", "tags"]:
        return True  # Keep
    else:
        return False  # Exclude

def copy_metadata_directory(dir_name: str):
    """Copy metadata directory to filtered_data."""
    source_dir = SOURCE_BASE / dir_name
    dest_dir = OUTPUT_BASE / dir_name

    print(f"✓ Copying {dir_name}...")

    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    shutil.copytree(source_dir, dest_dir)

    # Track files
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(OUTPUT_BASE)
            MANIFEST_ENTRIES.append({
                "source": f"{dir_name}/{file_path.relative_to(dest_dir)}",
                "reason": f"metadata:{dir_name}",
                "layer": 3,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

def save_manifest_fragment():
    """Save manifest entries for synthesis agent."""
    manifest_file = OUTPUT_BASE / "metadata_manifest.json"

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "metadata",
            "total_files": len(MANIFEST_ENTRIES),
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"\n✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Metadata Processor ===\n")

    kept_dirs = []
    excluded_dirs = []

    for dir_name in METADATA_DIRS:
        should_keep = analyze_directory(dir_name)

        if should_keep is None:
            continue
        elif should_keep:
            copy_metadata_directory(dir_name)
            kept_dirs.append(dir_name)
        else:
            excluded_dirs.append(dir_name)
            print(f"✗ Excluding {dir_name}")

    save_manifest_fragment()

    print(f"\n✅ Metadata processing complete")
    print(f"Kept: {kept_dirs}")
    print(f"Excluded: {excluded_dirs}")

if __name__ == "__main__":
    main()
