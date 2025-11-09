"""Enhancement set JSON importer"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import EnhancementSet, Enhancement

logger = logging.getLogger(__name__)


class EnhancementImporter:
    """Import enhancement sets from City of Data JSON files"""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def import_from_file(self, json_path: Path) -> Dict[str, Any]:
        """Import enhancement set from a single JSON file

        Args:
            json_path: Path to boost set JSON file

        Returns:
            Dict with import results
        """
        result = {
            'success': False,
            'sets_imported': 0,
            'enhancements_imported': 0,
            'skipped': 0,
            'errors': []
        }

        try:
            with open(json_path) as f:
                data = json.load(f)

            # Check if set already exists
            existing = self.db.query(EnhancementSet).filter_by(
                name=data['name']
            ).first()

            if existing:
                logger.info(f"Enhancement set {data['name']} already exists")
                result['skipped'] = 1
                result['success'] = True
                return result

            # Create enhancement set
            boost_set = EnhancementSet(
                name=data['name'],
                display_name=data.get('display_name', data['name']),
                group_name=data.get('group_name', ''),
                min_level=data.get('min_level', 10),
                max_level=data.get('max_level', 50),
                conversion_groups=data.get('conversion_groups', []),
                boost_lists=data.get('boost_lists', []),
                bonuses=data.get('bonuses', []),
                computed=data.get('computed', {}),
                source_metadata=data
            )

            self.db.add(boost_set)
            self.db.commit()

            result['sets_imported'] = 1
            result['success'] = True
            logger.info(f"Imported set: {data['name']}")

        except Exception as e:
            self.db.rollback()
            error_msg = f"Error importing {json_path}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    async def import_from_directory(self, directory: Path) -> Dict[str, Any]:
        """Import all enhancement sets from directory"""
        result = {
            'success': True,
            'sets_imported': 0,
            'enhancements_imported': 0,
            'skipped': 0,
            'errors': []
        }

        json_files = list(directory.glob("*.json"))
        logger.info(f"Found {len(json_files)} enhancement set files")

        for json_file in json_files:
            file_result = await self.import_from_file(json_file)
            result['sets_imported'] += file_result['sets_imported']
            result['enhancements_imported'] += file_result['enhancements_imported']
            result['skipped'] += file_result['skipped']
            result['errors'].extend(file_result['errors'])

            if not file_result['success']:
                result['success'] = False

        return result
