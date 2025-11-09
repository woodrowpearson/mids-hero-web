"""Archetype JSON importer"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Archetype

logger = logging.getLogger(__name__)


class ArchetypeImporter:
    """Import archetypes from City of Data JSON files"""

    def __init__(self, db_session: Session):
        """Initialize with database session

        Args:
            db_session: SQLAlchemy session for database operations
        """
        self.db = db_session

    async def import_from_file(self, json_path: Path) -> Dict[str, Any]:
        """Import archetype from a single JSON file

        Args:
            json_path: Path to archetype JSON file

        Returns:
            Dict with import results: {success, imported, skipped, errors}
        """
        result = {
            'success': False,
            'imported': 0,
            'skipped': 0,
            'errors': []
        }

        try:
            # Read JSON file
            with open(json_path) as f:
                data = json.load(f)

            # Check if already exists (using name as unique identifier)
            existing = self.db.query(Archetype).filter_by(
                name=data['name']
            ).first()

            if existing:
                logger.info(f"Archetype {data['name']} already exists, skipping")
                result['skipped'] = 1
                result['success'] = True
                return result

            # Create archetype record
            archetype = Archetype(
                name=data['name'],
                display_name=data.get('display_name', data['name']),
                display_help=data.get('display_help', ''),
                display_short_help=data.get('display_short_help', ''),
                icon=data.get('icon', ''),
                primary_category=data.get('primary_category', ''),
                secondary_category=data.get('secondary_category', ''),
                class_key=data.get('class_key', ''),
                default_rank=data.get('default_rank', ''),
                is_villain=data.get('is_villain', False),
                attrib_base=data.get('attrib_base', {}),
                source_metadata=data  # Store full JSON
            )

            self.db.add(archetype)
            self.db.commit()

            result['imported'] = 1
            result['success'] = True
            logger.info(f"Imported archetype: {data['name']}")

        except Exception as e:
            self.db.rollback()
            error_msg = f"Error importing {json_path}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    async def import_from_directory(self, directory: Path) -> Dict[str, Any]:
        """Import all archetypes from a directory

        Args:
            directory: Path to directory containing archetype JSON files

        Returns:
            Dict with import results
        """
        result = {
            'success': True,
            'imported': 0,
            'skipped': 0,
            'errors': []
        }

        json_files = list(directory.glob("*.json"))
        logger.info(f"Found {len(json_files)} archetype files")

        for json_file in json_files:
            file_result = await self.import_from_file(json_file)
            result['imported'] += file_result['imported']
            result['skipped'] += file_result['skipped']
            result['errors'].extend(file_result['errors'])

            if not file_result['success']:
                result['success'] = False

        return result
