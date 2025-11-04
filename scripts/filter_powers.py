#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Filter powers directory using Layer 1 + Layer 2 rules.

Usage: uv run scripts/filter_powers.py
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Set

SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916/powers")
OUTPUT_DIR = Path("/Users/w/code/mids-hero-web/filtered_data/powers")
MAPPING_FILE = Path("/Users/w/code/mids-hero-web/.claude/docs/archetype-category-mapping.json")
MANIFEST_ENTRIES: List[Dict] = []
EXCLUDED_ENTRIES: List[Dict] = []

# Layer 1 patterns
LAYER_1_PATTERNS = ["Pool", "Epic", "Inherent", "Incarnate"]

# Exclusion patterns
EXCLUSION_PATTERNS = ["Villain_", "NPC_", "Critter_", "Enemy_"]

def load_archetype_categories() -> Set[str]:
    """Load Layer 2 archetype-linked categories."""
    with open(MAPPING_FILE) as f:
        data = json.load(f)
    # Normalize to lowercase for case-insensitive matching
    return set(cat.lower() for cat in data["all_categories"])

def matches_layer_1(category_name: str) -> bool:
    """Check if category matches Layer 1 explicit patterns."""
    category_lower = category_name.lower()
    return any(pattern.lower() in category_lower for pattern in LAYER_1_PATTERNS)

def matches_exclusion(category_name: str) -> bool:
    """Check if category matches exclusion patterns."""
    category_lower = category_name.lower()
    return any(pattern.lower() in category_lower for pattern in EXCLUSION_PATTERNS)

def filter_powers(archetype_categories: Set[str]):
    """Filter power categories using 3-layer rules."""

    # Read powers index
    with open(SOURCE_DIR / "index.json") as f:
        powers_index = json.load(f)

    kept_categories = []
    excluded_categories = []

    # Get all category directories
    for category_dir in SOURCE_DIR.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        category_name = category_dir.name

        # Check exclusion first
        if matches_exclusion(category_name):
            excluded_categories.append({
                "category": category_name,
                "reason": "exclusion_pattern"
            })
            print(f"✗ EXCLUDE: {category_name} (exclusion pattern)")
            continue

        # Check Layer 1
        if matches_layer_1(category_name):
            kept_categories.append({
                "category": category_name,
                "reason": "layer_1_explicit",
                "layer": 1
            })
            print(f"✓ KEEP: {category_name} (Layer 1 - explicit)")
            copy_category(category_dir, category_name, "layer_1_explicit", 1)
            continue

        # Check Layer 2 (case-insensitive)
        if category_name.lower() in archetype_categories:
            kept_categories.append({
                "category": category_name,
                "reason": "layer_2_archetype_linked",
                "layer": 2
            })
            print(f"✓ KEEP: {category_name} (Layer 2 - archetype-linked)")
            copy_category(category_dir, category_name, "layer_2_archetype_linked", 2)
            continue

        # Flag for review
        excluded_categories.append({
            "category": category_name,
            "reason": "no_match_review_needed"
        })
        print(f"? REVIEW: {category_name} (no matching rule)")

    print(f"\n✅ Filtering complete")
    print(f"Kept: {len(kept_categories)} categories")
    print(f"Excluded: {len(excluded_categories)} categories")

    return kept_categories, excluded_categories

def copy_category(category_dir: Path, category_name: str, reason: str, layer: int):
    """Copy a power category directory."""
    dest_dir = OUTPUT_DIR / category_name

    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    shutil.copytree(category_dir, dest_dir)

    # Track files
    for file_path in dest_dir.rglob("*"):
        if file_path.is_file():
            relative_source = file_path.relative_to(Path("/Users/w/code/mids-hero-web/filtered_data"))
            MANIFEST_ENTRIES.append({
                "source": f"powers/{category_name}/{file_path.relative_to(dest_dir)}",
                "reason": reason,
                "layer": layer,
                "copied_to": str(relative_source),
                "size_bytes": file_path.stat().st_size
            })

def save_manifest_fragment(kept_categories, excluded_categories):
    """Save manifest entries for synthesis agent."""
    manifest_file = Path("/Users/w/code/mids-hero-web/filtered_data/powers_manifest.json")

    with open(manifest_file, "w") as f:
        json.dump({
            "directory": "powers",
            "total_files": len(MANIFEST_ENTRIES),
            "kept_categories": kept_categories,
            "excluded_categories": excluded_categories,
            "entries": MANIFEST_ENTRIES
        }, f, indent=2)

    print(f"✓ Saved manifest fragment to {manifest_file}")

def main():
    print("=== Powers Processor ===\n")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load archetype categories
    print("Loading archetype-category mapping...")
    archetype_categories = load_archetype_categories()
    print(f"✓ Loaded {len(archetype_categories)} archetype-linked categories\n")

    # Filter powers
    kept, excluded = filter_powers(archetype_categories)

    # Save manifest
    save_manifest_fragment(kept, excluded)

    print(f"\n✅ Powers processing complete")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
