#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pathlib"]
# ///

"""
Validate filtered City of Data and create comprehensive manifest.

Usage: uv run scripts/validate_filtered_data.py
"""

import json
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

FILTERED_DIR = Path("/Users/w/code/mids-hero-web/filtered_data")
SOURCE_DIR = Path("/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916")
OUTPUT_MANIFEST = FILTERED_DIR / "manifest.json"

def load_manifest_fragments() -> Dict:
    """Load all manifest fragments from filtering agents."""
    fragments = {}

    for fragment_file in FILTERED_DIR.glob("*_manifest.json"):
        with open(fragment_file) as f:
            data = json.load(f)
        fragments[data["directory"]] = data

    return fragments

def count_files_by_directory() -> Dict[str, int]:
    """Count files in each filtered directory."""
    counts = {}

    for directory in FILTERED_DIR.iterdir():
        if directory.is_dir() and not directory.name.startswith("."):
            file_count = len([f for f in directory.rglob("*") if f.is_file()])
            counts[directory.name] = file_count

    return counts

def validate_archetypes() -> Dict:
    """Validate archetype completeness."""
    archetypes_dir = FILTERED_DIR / "archetypes"

    # Known player archetypes (City of Heroes) - normalized to lowercase for comparison
    expected_archetypes = {
        "blaster", "controller", "defender", "scrapper", "tanker",
        "brute", "stalker", "mastermind", "dominator", "corruptor",
        "peacebringer", "warshade", "arachnos_soldier", "arachnos_widow",
        "sentinel"
    }

    # Get archetype files (they are .json files, not directories)
    found_files = {f.stem.lower() for f in archetypes_dir.iterdir() if f.is_file() and f.suffix == ".json" and f.name != "index.json"}

    return {
        "expected": sorted(list(expected_archetypes)),
        "found": sorted(list(found_files)),
        "all_present": expected_archetypes.issubset(found_files),
        "extra": sorted(list(found_files - expected_archetypes))
    }

def validate_power_categories() -> Dict:
    """Validate power category completeness."""
    powers_dir = FILTERED_DIR / "powers"

    if not powers_dir.exists():
        return {"error": "powers directory not found"}

    categories = [d.name for d in powers_dir.iterdir() if d.is_dir()]

    # Check for required patterns (case-insensitive)
    has_pool = any("pool" in cat.lower() for cat in categories)
    has_epic = any("epic" in cat.lower() for cat in categories)
    has_inherent = any("inherent" in cat.lower() for cat in categories)
    has_incarnate = any("incarnate" in cat.lower() for cat in categories)

    return {
        "total_categories": len(categories),
        "has_pool": has_pool,
        "has_epic": has_epic,
        "has_inherent": has_inherent,
        "has_incarnate": has_incarnate,
        "all_required_present": all([has_pool, has_epic, has_inherent, has_incarnate]),
        "sample_categories": categories[:10]
    }

def validate_boost_sets() -> Dict:
    """Validate boost sets completeness."""
    boost_dir = FILTERED_DIR / "boost_sets"

    if not boost_dir.exists():
        return {"error": "boost_sets directory not found"}

    file_count = len([f for f in boost_dir.rglob("*") if f.is_file()])

    return {
        "present": True,
        "total_files": file_count
    }

def validate_schema_integrity() -> Dict:
    """Validate that index.json files are valid JSON."""
    errors = []
    checked = 0

    for index_file in FILTERED_DIR.rglob("index.json"):
        checked += 1
        try:
            with open(index_file) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            errors.append({
                "file": str(index_file.relative_to(FILTERED_DIR)),
                "error": str(e)
            })

    return {
        "files_checked": checked,
        "errors": errors,
        "valid": len(errors) == 0
    }

def compile_manifest(fragments: Dict, validation: Dict) -> Dict:
    """Compile comprehensive manifest from all data."""

    # Collect all entries
    all_kept = []
    all_excluded = []

    for directory, fragment in fragments.items():
        all_kept.extend(fragment.get("entries", []))

        # Powers has excluded entries
        if "excluded_categories" in fragment:
            for exc in fragment["excluded_categories"]:
                all_excluded.append({
                    "source": f"powers/{exc['category']}/",
                    "reason": exc["reason"]
                })

    # Count by layer
    layer_counts = {1: 0, 2: 0, 3: 0}
    for entry in all_kept:
        layer = entry.get("layer", 3)
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    # Count by directory
    dir_counts = {}
    for entry in all_kept:
        dir_name = entry["copied_to"].split("/")[0]
        dir_counts[dir_name] = dir_counts.get(dir_name, 0) + 1

    # Load filter rules
    with open(Path("/Users/w/code/mids-hero-web/.claude/docs/archetype-category-mapping.json")) as f:
        mapping = json.load(f)

    manifest = {
        "metadata": {
            "source_dir": "raw_data_homecoming-20250617_6916",
            "filtered_date": datetime.now().isoformat(),
            "total_source_files": len([f for f in SOURCE_DIR.rglob("*") if f.is_file()]),
            "kept_files": len(all_kept),
            "excluded_files": len(all_excluded),
            "strategy_version": "v1.0",
            "epic": "2.5",
            "github_issue": "#300"
        },
        "filter_rules": {
            "explicit_categories": ["Pool", "Epic", "Inherent", "Incarnate"],
            "archetype_linked": mapping["all_categories"],
            "special_directories": ["boost_sets", "archetypes"],
            "exclusion_patterns": ["Villain_*", "NPC_*", "Critter_*", "Enemy_*"]
        },
        "kept_files": all_kept,
        "excluded_files": all_excluded,
        "statistics": {
            "by_layer": layer_counts,
            "by_directory": dir_counts
        },
        "validation": validation
    }

    return manifest

def main():
    print("=== Validation & Manifest Creation ===\n")

    # Load fragments
    print("Loading manifest fragments...")
    fragments = load_manifest_fragments()
    print(f"✓ Loaded {len(fragments)} fragments\n")

    # Validate
    print("Validating filtered data...\n")

    validation = {}

    print("1. Checking archetypes...")
    validation["archetypes"] = validate_archetypes()
    print(f"   ✓ Found {len(validation['archetypes']['found'])} archetypes")

    print("2. Checking power categories...")
    validation["power_categories"] = validate_power_categories()
    print(f"   ✓ Found {validation['power_categories']['total_categories']} categories")

    print("3. Checking boost sets...")
    validation["boost_sets"] = validate_boost_sets()
    print(f"   ✓ Boost sets present: {validation['boost_sets']['total_files']} files")

    print("4. Checking schema integrity...")
    validation["schema"] = validate_schema_integrity()
    print(f"   ✓ Checked {validation['schema']['files_checked']} index files")

    # Compile manifest
    print("\nCompiling manifest...")
    manifest = compile_manifest(fragments, validation)

    # Save manifest
    with open(OUTPUT_MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"✓ Saved manifest to {OUTPUT_MANIFEST}")

    # Summary
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    print(f"Total source files: {manifest['metadata']['total_source_files']:,}")
    print(f"Kept files: {manifest['metadata']['kept_files']:,}")
    print(f"Excluded files: {manifest['metadata']['excluded_files']:,}")
    print(f"\nBy Layer:")
    print(f"  Layer 1 (Explicit): {manifest['statistics']['by_layer'][1]:,}")
    print(f"  Layer 2 (Archetype-linked): {manifest['statistics']['by_layer'][2]:,}")
    print(f"  Layer 3 (Special dirs): {manifest['statistics']['by_layer'][3]:,}")
    print(f"\nValidation:")
    print(f"  Archetypes: {'✅ PASS' if validation['archetypes']['all_present'] else '⚠️  REVIEW'}")
    print(f"  Power categories: {'✅ PASS' if validation['power_categories']['all_required_present'] else '⚠️  REVIEW'}")
    print(f"  Boost sets: {'✅ PASS' if validation['boost_sets']['present'] else '❌ FAIL'}")
    print(f"  Schema integrity: {'✅ PASS' if validation['schema']['valid'] else '❌ FAIL'}")

    if validation['schema']['errors']:
        print(f"\n⚠️  Schema errors found:")
        for err in validation['schema']['errors']:
            print(f"    - {err['file']}: {err['error']}")

    print("\n✅ Validation complete")
    print(f"Manifest saved to: {OUTPUT_MANIFEST}")

if __name__ == "__main__":
    main()
