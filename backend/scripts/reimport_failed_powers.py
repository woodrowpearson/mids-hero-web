#!/usr/bin/env python3
"""Script to re-import the 12 powers that failed due to range overflow"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Power, Powerset
from app.data_import.importers.power_importer import PowerImporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of 12 failed power files that have range=10000.0
FAILED_POWER_FILES = [
    "filtered_data/powers/inherent/inherent/shadow_recall.json",
    "filtered_data/powers/warshade_defensive/umbral_aura/shadow_recall.json",
    "filtered_data/powers/incarnate/destiny/incandescence_core_epiphany.json",
    "filtered_data/powers/incarnate/destiny/incandescence_core_invocation.json",
    "filtered_data/powers/incarnate/destiny/incandescence_invocation.json",
    "filtered_data/powers/incarnate/destiny/incandescence_partial_core_invocation.json",
    "filtered_data/powers/incarnate/destiny/incandescence_partial_radial_invocation.json",
    "filtered_data/powers/incarnate/destiny/incandescence_radial_epiphany.json",
    "filtered_data/powers/incarnate/destiny/incandescence_radial_invocation.json",
    "filtered_data/powers/incarnate/destiny/incandescence_total_core_invocation.json",
    "filtered_data/powers/incarnate/destiny/incandescence_total_radial_invocation.json",
    "filtered_data/powers/incarnate/destiny_silent/incandescence.json",
]


async def reimport_failed_powers(project_root: Path):
    """Re-import the 12 powers that failed with range overflow"""

    db = SessionLocal()
    importer = PowerImporter(db)

    try:
        results = {
            "imported": 0,
            "skipped": 0,
            "errors": [],
        }

        for power_file_rel in FAILED_POWER_FILES:
            power_file = project_root / power_file_rel

            if not power_file.exists():
                error_msg = f"Power file not found: {power_file}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                continue

            # Determine powerset from directory structure
            # Path format: filtered_data/powers/{category}/{powerset}/power.json
            parts = power_file.parts
            category = parts[-3]  # e.g., "inherent", "incarnate"
            powerset_dirname = parts[-2]  # e.g., "inherent", "destiny"

            # Normalize powerset name (capitalize first letter, replace _ with space)
            # Map directory names to actual powerset names in database
            powerset_map = {
                "inherent": "Inherent",
                "umbral_aura": "Umbral_Aura",
                "destiny": "Destiny",
                "destiny_silent": "Destiny_Silent",
            }

            powerset_name = powerset_map.get(powerset_dirname.lower())
            if not powerset_name:
                # Try capitalizing first letter
                powerset_name = powerset_dirname.replace("_", " ").title().replace(" ", "_")

            # Query powerset by name
            powerset = db.query(Powerset).filter_by(name=powerset_name).first()

            if not powerset:
                error_msg = f"Powerset '{powerset_name}' not found for power {power_file.name}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                continue

            logger.info(f"Importing {power_file.name} into powerset '{powerset_name}'...")

            # Use the importer to import the power
            result = await importer.import_power(power_file, powerset.id)

            if result["success"]:
                results["imported"] += result["imported"]
                results["skipped"] += result["skipped"]
                logger.info(f"  ✓ Success: {power_file.name}")
            else:
                results["errors"].extend(result["errors"])
                logger.error(f"  ✗ Failed: {power_file.name}")

        # Print summary
        logger.info("\n" + "="*60)
        logger.info("REIMPORT SUMMARY")
        logger.info("="*60)
        logger.info(f"Total attempted: {len(FAILED_POWER_FILES)}")
        logger.info(f"Successfully imported: {results['imported']}")
        logger.info(f"Skipped (already exist): {results['skipped']}")
        logger.info(f"Errors: {len(results['errors'])}")

        if results["errors"]:
            logger.error("\nErrors encountered:")
            for error in results["errors"]:
                logger.error(f"  - {error}")

        return results

    finally:
        db.close()


def main():
    """Main entry point"""
    # Get project root (backend/scripts -> backend -> project_root)
    project_root = Path(__file__).parent.parent.parent

    logger.info(f"Project root: {project_root}")
    logger.info(f"Re-importing {len(FAILED_POWER_FILES)} powers that failed with range overflow...")

    asyncio.run(reimport_failed_powers(project_root))


if __name__ == "__main__":
    main()
