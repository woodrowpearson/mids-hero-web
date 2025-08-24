"""DEPRECATED: MHD binary import is no longer supported.

This command has been deprecated as part of Epic 2.5.5 cleanup.
Please use the JSON import functionality instead:
  - Use DataExporter C# project to convert MHD to JSON
  - Use scripts/import_i12_data.py to import JSON data
"""

import asyncio
import logging
from pathlib import Path

import click
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
# DEPRECATED: MHD parser has been archived
# from app.mhd_parser.cli import MhdParserCLI
# from app.mhd_parser.main_database_parser import parse_main_database
from app.models import Archetype as ArchetypeModel

logger = logging.getLogger(__name__)


class DatabaseImporter:
    """Import parsed MHD data into the database."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.archetype_map = {}  # Index -> DB ID mapping
        self.powerset_map = {}
        self.power_map = {}

    async def import_main_database(self, file_path: Path) -> None:
        """DEPRECATED: Use JSON import instead."""
        raise NotImplementedError(
            "MHD binary import is no longer supported. "
            "Please use DataExporter to convert MHD to JSON, "
            "then use scripts/import_i12_data.py for import."
        )

    async def _import_archetypes(self, archetypes):
        """Import archetypes and build index mapping."""
        for idx, arch in enumerate(archetypes):
            model = ArchetypeModel(
                name=arch.class_name,
                display_name=arch.display_name,
                description=arch.desc_long,
                hit_points=arch.hitpoints,
                max_hp=arch.hp_cap,
                primary_category=arch.primary_group,
                secondary_category=arch.secondary_group,
                playable=arch.playable,
            )
            self.session.add(model)
            await self.session.flush()  # Get the ID
            self.archetype_map[idx] = model.id

        logger.info(f"Imported {len(archetypes)} archetypes")

    async def _import_powersets(self, powersets):
        """Import powersets with archetype references."""
        # TODO: Implement when Powerset model exists
        logger.info(f"Would import {len(powersets)} powersets")

    async def _import_powers(self, powers):
        """Import powers with powerset references."""
        # TODO: Implement when Power model exists
        logger.info(f"Would import {len(powers)} powers")

    async def _import_summons(self, summons):
        """Import summon entities."""
        # TODO: Implement when Summon model exists
        logger.info(f"Would import {len(summons)} summons")


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--type",
    "file_type",
    type=click.Choice(["main", "enhancement", "salvage", "recipe", "auto"]),
    default="auto",
    help="Type of MHD file",
)
@click.option("--dry-run", is_flag=True, help="Parse without importing")
@click.option("--export-json", is_flag=True, help="Export to JSON")
@click.option("--output", type=click.Path(), help="Output directory for JSON")
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
def import_mhd(
    path: str,
    file_type: str,
    dry_run: bool,
    export_json: bool,
    output: str | None,
    log_level: str,
):
    """DEPRECATED: MHD binary import is no longer supported.

    This command has been deprecated as part of Epic 2.5.5 cleanup.
    
    Please use the JSON import workflow instead:
    1. Use DataExporter C# project to convert MHD to JSON:
       cd DataExporter && dotnet run -- /path/to/mhd/file.mhd
    
    2. Import JSON data using:
       python backend/scripts/import_i12_data.py /path/to/json/file.json
    
    Or use the justfile commands:
       just i12-import /path/to/json/file.json
    """
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    path_obj = Path(path)

    logger.error("MHD binary import is deprecated!")
    logger.error("Please use the JSON import workflow:")
    logger.error("1. Convert MHD to JSON: cd DataExporter && dotnet run -- %s", path)
    logger.error("2. Import JSON: python backend/scripts/import_i12_data.py <json_file>")
    logger.error("Or use: just i12-import <json_file>")
    
    click.echo("\n" + "="*60)
    click.echo("ERROR: MHD binary import is no longer supported!")
    click.echo("="*60)
    click.echo("\nThis command was deprecated as part of Epic 2.5.5 cleanup.")
    click.echo("\nPlease use the JSON import workflow instead:")
    click.echo("\n1. Convert MHD to JSON using DataExporter:")
    click.echo(f"   cd DataExporter && dotnet run -- {path}")
    click.echo("\n2. Import the JSON data:")
    click.echo("   python backend/scripts/import_i12_data.py <json_file>")
    click.echo("\nOr use the justfile command:")
    click.echo("   just i12-import <json_file>")
    click.echo("="*60)
    
    raise SystemExit(1)


async def _import_to_database(path: Path, file_type: str):
    """Import MHD data to database."""
    async for session in get_async_session():
        importer = DatabaseImporter(session)

        try:
            if path.is_file():
                if file_type == "main" or (
                    file_type == "auto" and "i12" in path.name.lower()
                ):
                    await importer.import_main_database(path)
                else:
                    logger.warning(f"Database import not implemented for {file_type}")
            else:
                # Import all main database files
                for file_path in path.glob("*i12*.mhd"):
                    await importer.import_main_database(file_path)

        except Exception as e:
            logger.error(f"Import failed: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


if __name__ == "__main__":
    import_mhd()
