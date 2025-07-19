"""CLI interface for data import operations."""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .archetype_importer import ArchetypeImporter
from .attribute_importer import AttributeModifierImporter, TypeGradeImporter
from .enhancement_importer import EnhancementImporter
from .power_importer import PowerImporter, PowersetImporter
from .recipe_importer import RecipeImporter
from .salvage_importer import SalvageImporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    load_dotenv()
    return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/mids_web")


def import_archetypes(args: argparse.Namespace) -> None:
    """Import archetype data."""
    logger.info("Starting archetype import...")
    importer = ArchetypeImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing archetype data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_powersets(args: argparse.Namespace) -> None:
    """Import powerset data."""
    logger.info("Starting powerset import...")
    importer = PowersetImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing powerset data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_powers(args: argparse.Namespace) -> None:
    """Import power data."""
    logger.info("Starting power import...")
    importer = PowerImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing power data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_enhancements(args: argparse.Namespace) -> None:
    """Import enhancement data."""
    logger.info("Starting enhancement import...")
    importer = EnhancementImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing enhancement data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_salvage(args: argparse.Namespace) -> None:
    """Import salvage data."""
    logger.info("Starting salvage import...")
    importer = SalvageImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing salvage data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_recipes(args: argparse.Namespace) -> None:
    """Import recipe data."""
    logger.info("Starting recipe import...")
    importer = RecipeImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing recipe data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_attribute_modifiers(args: argparse.Namespace) -> None:
    """Import attribute modifier data."""
    logger.info("Starting attribute modifier import...")
    importer = AttributeModifierImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing attribute modifier data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_type_grades(args: argparse.Namespace) -> None:
    """Import type grade data."""
    logger.info("Starting type grade import...")
    importer = TypeGradeImporter(args.database_url, args.batch_size)

    if args.clear:
        logger.warning("Clearing existing type grade data...")
        importer.clear_existing_data()

    result = importer.import_data(Path(args.file), args.resume_from)
    logger.info(f"Import completed: {result.records_imported} records imported")


def import_all(args: argparse.Namespace) -> None:
    """Import all data in the correct order."""
    logger.info("Starting full data import...")

    # Set default paths if not provided
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    # Import in dependency order
    steps = [
        ("archetypes", "I9_structured.json", import_archetypes),
        ("powersets", "I9_structured.json", import_powersets),
        ("powers", "I9_structured.json", import_powers),
        ("salvage", "salvage.json", import_salvage),
        ("enhancements", "enhancements.json", import_enhancements),
        ("recipes", "recipes.json", import_recipes),
        ("attribute_modifiers", "AttribMod.json", import_attribute_modifiers),
        ("type_grades", "TypeGrades.json", import_type_grades),
    ]

    for name, filename, import_func in steps:
        file_path = data_dir / filename
        if not file_path.exists():
            logger.warning(f"Skipping {name}: file not found ({file_path})")
            continue

        # Create args for the specific import
        import_args = argparse.Namespace(
            file=str(file_path),
            database_url=args.database_url,
            batch_size=args.batch_size,
            clear=args.clear,
            resume_from=0,
        )

        try:
            import_func(import_args)
        except Exception as e:
            logger.error(f"Failed to import {name}: {e}")
            if not args.continue_on_error:
                raise

    logger.info("Full import completed!")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Import City of Heroes game data into PostgreSQL database"
    )

    # Common arguments
    parser.add_argument(
        "--database-url",
        type=str,
        default=get_database_url(),
        help="Database connection URL",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of records to process in each batch",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before import",
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Resume from specific record index",
    )

    # Subcommands for different import types
    subparsers = parser.add_subparsers(dest="command", help="Import command")

    # Individual import commands
    for cmd, help_text in [
        ("archetypes", "Import archetype data"),
        ("powersets", "Import powerset data"),
        ("powers", "Import power data"),
        ("enhancements", "Import enhancement data"),
        ("salvage", "Import salvage data"),
        ("recipes", "Import recipe data"),
        ("attribute-modifiers", "Import attribute modifier data"),
        ("type-grades", "Import type grade data"),
    ]:
        sub = subparsers.add_parser(cmd, help=help_text)
        sub.add_argument("file", help="Path to JSON file to import")

    # Import all command
    all_parser = subparsers.add_parser("all", help="Import all data files")
    all_parser.add_argument(
        "data_dir",
        help="Directory containing all JSON data files",
    )
    all_parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue importing even if one file fails",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Map commands to functions
    command_map = {
        "archetypes": import_archetypes,
        "powersets": import_powersets,
        "powers": import_powers,
        "enhancements": import_enhancements,
        "salvage": import_salvage,
        "recipes": import_recipes,
        "attribute-modifiers": import_attribute_modifiers,
        "type-grades": import_type_grades,
        "all": import_all,
    }

    try:
        command_func = command_map[args.command]
        command_func(args)
    except KeyboardInterrupt:
        logger.info("Import interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
