#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Extract archetype → power category mappings from City of Data.

Usage: uv run scripts/map_archetype_categories.py
Output: .claude/docs/archetype-category-mapping.json
"""

import json
from pathlib import Path
from typing import Dict, List, Set

def extract_archetype_categories(archetypes_dir: Path) -> Dict[str, Dict[str, str]]:
    """Extract primary/secondary categories for each archetype."""
    mapping = {}

    # List of player archetypes (not NPC archetypes like boss_*, minion_*, etc.)
    player_archetypes = [
        "blaster", "controller", "defender", "scrapper", "tanker",
        "brute", "stalker", "mastermind", "dominator", "corruptor",
        "peacebringer", "warshade", "arachnos_soldier", "arachnos_widow",
        "sentinel"
    ]

    for archetype_name in player_archetypes:
        archetype_file = archetypes_dir / f"{archetype_name}.json"

        if not archetype_file.exists():
            print(f"Warning: No file for {archetype_name}")
            continue

        with open(archetype_file) as f:
            data = json.load(f)

        primary = data.get("primary_category")
        secondary = data.get("secondary_category")
        epic_pool = data.get("epic_pool_category")
        power_pool = data.get("power_pool_category")

        mapping[archetype_name] = {
            "primary": primary,
            "secondary": secondary,
            "epic_pool": epic_pool,
            "power_pool": power_pool,
            "display_name": data.get("display_name", archetype_name)
        }

        print(f"✓ {archetype_name}: primary={primary}, secondary={secondary}")

    return mapping

def get_all_archetype_categories(mapping: Dict) -> Set[str]:
    """Get unique set of all categories referenced by archetypes."""
    categories = set()
    for archetype, data in mapping.items():
        if data["primary"]:
            categories.add(data["primary"])
        if data["secondary"]:
            categories.add(data["secondary"])
        # Note: epic_pool and power_pool are typically null or reference "epic"/"pool"
        # which we handle separately in Layer 1
    return categories

def main():
    base_dir = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916")
    archetypes_dir = base_dir / "archetypes"
    output_file = Path("/Users/w/code/mids-hero-web/.claude/docs/archetype-category-mapping.json")

    print("Extracting archetype→category mappings...")
    mapping = extract_archetype_categories(archetypes_dir)

    print("\nAll archetype-linked categories:")
    all_categories = get_all_archetype_categories(mapping)
    for cat in sorted(all_categories):
        print(f"  - {cat}")

    # Save mapping
    output_data = {
        "archetypes": mapping,
        "all_categories": sorted(list(all_categories)),
        "total_archetypes": len(mapping),
        "total_categories": len(all_categories),
        "generated_date": "2025-11-01"
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Mapping saved to {output_file}")
    print(f"Total archetypes: {len(mapping)}")
    print(f"Total unique categories: {len(all_categories)}")

if __name__ == "__main__":
    main()
