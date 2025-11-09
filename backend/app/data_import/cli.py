"""CLI interface for JSON data import"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.data_import.importers.archetype_importer import ArchetypeImporter
from app.data_import.importers.enhancement_importer import EnhancementImporter
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def import_archetypes(
    directory_path: str, db_session: Session = None
) -> dict[str, Any]:
    """Import all archetypes from directory

    Args:
        directory_path: Path to archetypes directory
        db_session: Optional database session (creates new if not provided)

    Returns:
        Import results dictionary
    """
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    try:
        directory = Path(directory_path)
        importer = ArchetypeImporter(db_session)

        logger.info(f"Importing archetypes from {directory}")
        result = await importer.import_from_directory(directory)

        logger.info(
            f"Archetype import complete: {result['imported']} imported, "
            f"{result['skipped']} skipped, {len(result['errors'])} errors"
        )

        return {
            "total_imported": result["imported"],
            "total_skipped": result["skipped"],
            "errors": result["errors"],
        }
    finally:
        if close_session:
            db_session.close()


async def import_enhancements(
    directory_path: str, db_session: Session = None
) -> dict[str, Any]:
    """Import all enhancement sets from directory"""
    close_session = False
    if db_session is None:
        db_session = SessionLocal()
        close_session = True

    try:
        directory = Path(directory_path)
        importer = EnhancementImporter(db_session)

        logger.info(f"Importing enhancement sets from {directory}")
        result = await importer.import_from_directory(directory)

        logger.info(
            f"Enhancement import complete: {result['sets_imported']} sets, "
            f"{result['enhancements_imported']} enhancements, "
            f"{result['skipped']} skipped"
        )

        return {
            "total_sets": result["sets_imported"],
            "total_enhancements": result["enhancements_imported"],
            "total_skipped": result["skipped"],
            "errors": result["errors"],
        }
    finally:
        if close_session:
            db_session.close()


def main():
    """Main CLI entry point"""
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m app.data_import.cli <command> <directory>")
        print("Commands: archetypes, enhancements, all")
        sys.exit(1)

    command = sys.argv[1]
    directory = sys.argv[2]

    if command == "archetypes":
        asyncio.run(import_archetypes(directory))
    elif command == "enhancements":
        asyncio.run(import_enhancements(directory))
    elif command == "all":
        asyncio.run(import_archetypes(f"{directory}/archetypes"))
        asyncio.run(import_enhancements(f"{directory}/boost_sets"))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
