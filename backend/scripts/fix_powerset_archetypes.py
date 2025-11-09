#!/usr/bin/env python3
"""Script to fix archetype_id for all 371 powersets based on display_fullname"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Archetype, Powerset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map category prefixes to archetypes
ARCHETYPE_CATEGORY_MAP = {
    "blaster": ["Blaster Ranged", "Blaster Support"],
    "brute": ["Brute Melee", "Brute Defense"],
    "controller": ["Controller Control", "Controller Buff"],
    "corruptor": ["Corruptor Ranged", "Corruptor Buff"],
    "defender": ["Defender Ranged", "Defender Buff"],
    "dominator": ["Dominator Control", "Dominator Assault"],
    "mastermind": ["Mastermind Buff", "Mastermind Summon"],
    "scrapper": ["Scrapper Melee", "Scrapper Defense"],
    "stalker": ["Stalker Melee", "Stalker Defense"],
    "tanker": ["Tanker Melee", "Tanker Defense"],
    "peacebringer": ["Peacebringer Defensive", "Peacebringer Offensive"],
    "warshade": ["Warshade Defensive", "Warshade Offensive"],
    "sentinel": ["Sentinel Ranged", "Sentinel Defense"],
    "arachnos_soldier": ["Arachnos Soldiers"],
    "arachnos_widow": ["Arachnos Widow"],
}


def extract_archetype_from_display_fullname(display_fullname: str) -> str | None:
    """Extract archetype name from display_fullname like 'Brute Defense.Invulnerability'"""
    if not display_fullname:
        return None

    # Split on first dot
    parts = display_fullname.split(".", 1)
    if len(parts) < 2:
        return None

    category_part = parts[0].strip()  # e.g., "Brute Defense"

    # Special handling for Arachnos archetypes
    if "training" in category_part.lower() or "teamwork" in category_part.lower():
        # Training Gadgets -> arachnos_soldier
        # Widow Training/Teamwork -> arachnos_widow
        # Also check the powerset name part for widow/fortunata
        powerset_name = parts[1].strip() if len(parts) > 1 else ""
        if (
            "widow" in category_part.lower()
            or "widow" in powerset_name.lower()
            or "fortunata" in powerset_name.lower()
        ):
            return "arachnos_widow"
        elif (
            "bane" in category_part.lower()
            or "crab" in category_part.lower()
            or "gadgets" in category_part.lower()
        ):
            return "arachnos_soldier"
        # Generic "Teamwork" defaults to arachnos_soldier
        elif "teamwork" in category_part.lower():
            return "arachnos_soldier"

    # Try to match against known category patterns
    for archetype, categories in ARCHETYPE_CATEGORY_MAP.items():
        for category in categories:
            if category.lower() == category_part.lower():
                return archetype

    # For special cases like "Pool", "Epic", "Incarnate", return None (not archetype-specific)
    special_categories = ["pool", "epic", "incarnate", "inherent", "temporary"]
    if any(cat in category_part.lower() for cat in special_categories):
        return None

    # Try to extract first word as archetype
    first_word = category_part.split()[0].lower()
    if first_word in ARCHETYPE_CATEGORY_MAP:
        return first_word

    logger.warning(f"Could not extract archetype from: {display_fullname}")
    return None


def fix_powerset_archetypes():
    """Update all powersets with correct archetype_id"""

    db = SessionLocal()

    try:
        # Load all archetypes into a map
        archetypes = db.query(Archetype).all()
        archetype_map = {at.name: at.id for at in archetypes}

        logger.info(f"Loaded {len(archetypes)} archetypes")

        # Get all powersets
        powersets = db.query(Powerset).all()
        logger.info(f"Processing {len(powersets)} powersets...")

        stats = {
            "updated": 0,
            "skipped": 0,
            "no_archetype": 0,
            "archetype_not_found": 0,
            "errors": [],
        }

        for ps in powersets:
            # Skip if already has archetype
            if ps.archetype_id is not None:
                stats["skipped"] += 1
                continue

            # Try to extract archetype from display_fullname
            archetype_name = None
            if ps.source_metadata and "display_fullname" in ps.source_metadata:
                display_fullname = ps.source_metadata["display_fullname"]
                archetype_name = extract_archetype_from_display_fullname(
                    display_fullname
                )

            if not archetype_name:
                logger.debug(f"Powerset {ps.name}: no archetype extracted")
                stats["no_archetype"] += 1
                continue

            # Look up archetype ID
            archetype_id = archetype_map.get(archetype_name)
            if not archetype_id:
                error_msg = f"Powerset {ps.name}: archetype '{archetype_name}' not found in database"
                logger.error(error_msg)
                stats["archetype_not_found"] += 1
                stats["errors"].append(error_msg)
                continue

            # Update powerset
            ps.archetype_id = archetype_id
            stats["updated"] += 1
            logger.info(
                f"Updated {ps.name}: archetype_id={archetype_id} ({archetype_name})"
            )

        # Commit all changes
        db.commit()

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("FIX ARCHETYPE SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total powersets: {len(powersets)}")
        logger.info(f"Updated: {stats['updated']}")
        logger.info(f"Already had archetype: {stats['skipped']}")
        logger.info(f"No archetype (special powersets): {stats['no_archetype']}")
        logger.info(f"Archetype not found: {stats['archetype_not_found']}")

        if stats["errors"]:
            logger.error(f"\nErrors: {len(stats['errors'])}")
            for error in stats["errors"][:10]:  # Show first 10
                logger.error(f"  - {error}")

        # Validate: check how many still have NULL archetype_id
        null_count = db.query(Powerset).filter(Powerset.archetype_id.is_(None)).count()
        logger.info(f"\nPowersets with NULL archetype_id after fix: {null_count}")

        return stats

    finally:
        db.close()


def main():
    """Main entry point"""
    logger.info("Fixing archetype_id for all powersets...")
    fix_powerset_archetypes()


if __name__ == "__main__":
    main()
