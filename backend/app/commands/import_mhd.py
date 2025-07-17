"""FastAPI management command for importing MHD files."""

import asyncio
import logging
from pathlib import Path

import click
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.mhd_parser.cli import MhdParserCLI
from app.mhd_parser.main_database_parser import parse_main_database
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
        """Import main database file."""
        logger.info(f"Importing main database from {file_path}")

        with open(file_path, 'rb') as f:
            db = parse_main_database(f)

        # Import in dependency order
        await self._import_archetypes(db.archetypes)
        await self._import_powersets(db.powersets)
        await self._import_powers(db.powers)
        await self._import_summons(db.summons)

        await self.session.commit()
        logger.info("Main database import complete")

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
                playable=arch.playable
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
@click.argument('path', type=click.Path(exists=True))
@click.option('--type', 'file_type',
              type=click.Choice(['main', 'enhancement', 'salvage', 'recipe', 'auto']),
              default='auto', help='Type of MHD file')
@click.option('--dry-run', is_flag=True, help='Parse without importing')
@click.option('--export-json', is_flag=True, help='Export to JSON')
@click.option('--output', type=click.Path(), help='Output directory for JSON')
@click.option('--log-level', default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']))
def import_mhd(path: str, file_type: str, dry_run: bool,
               export_json: bool, output: str | None, log_level: str):
    """Import MHD files into the database.

    Examples:
        python -m app.commands.import_mhd data/I12.mhd
        python -m app.commands.import_mhd data/ --export-json --output json/
    """
    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    path_obj = Path(path)

    if dry_run or export_json:
        # Use CLI for dry-run and JSON export
        cli = MhdParserCLI()

        if path_obj.is_file():
            cli.parse_file(path_obj, Path(output) if output else None,
                          dry_run, export_json)
        else:
            cli.parse_directory(path_obj, "*.mhd",
                              Path(output) if output else None,
                              dry_run, export_json)
    else:
        # Real database import
        asyncio.run(_import_to_database(path_obj, file_type))


async def _import_to_database(path: Path, file_type: str):
    """Import MHD data to database."""
    async for session in get_async_session():
        importer = DatabaseImporter(session)

        try:
            if path.is_file():
                if file_type == 'main' or (file_type == 'auto' and 'i12' in path.name.lower()):
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
