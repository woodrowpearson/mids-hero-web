"""Power and Powerset JSON importer"""
import json
import logging
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Powerset, Power

logger = logging.getLogger(__name__)


class PowerImporter:
    """Import powers and powersets from City of Data JSON files"""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def import_powerset(self, powerset_dir: Path, archetype_id: int) -> Dict[str, Any]:
        """Import a powerset from its directory

        Args:
            powerset_dir: Directory containing powerset index.json
            archetype_id: ID of the archetype this powerset belongs to

        Returns:
            Import results
        """
        result = {
            'success': False,
            'powersets_imported': 0,
            'powers_imported': 0,
            'skipped': 0,
            'errors': []
        }

        try:
            index_file = powerset_dir / "index.json"
            if not index_file.exists():
                result['errors'].append(f"No index.json in {powerset_dir}")
                return result

            with open(index_file) as f:
                data = json.load(f)

            # Check if powerset already exists
            existing = self.db.query(Powerset).filter_by(
                name=data['name']
            ).first()

            if existing:
                logger.info(f"Powerset {data['name']} already exists")
                result['skipped'] = 1
                result['success'] = True
                return result

            # Create powerset
            powerset = Powerset(
                name=data['name'],
                display_name=data.get('display_name', data['name']),
                display_fullname=data.get('display_fullname', ''),
                display_help=data.get('display_help', ''),
                display_short_help=data.get('display_short_help', ''),
                archetype_id=archetype_id,
                powerset_type='primary',  # Will need to determine this properly
                icon=data.get('icon', ''),
                requires=data.get('requires', ''),
                power_names=data.get('power_names', []),
                power_display_names=data.get('power_display_names', []),
                power_short_helps=data.get('power_short_helps', []),
                available_level=data.get('available_level', []),
                source_metadata=data
            )

            self.db.add(powerset)
            self.db.commit()

            result['powersets_imported'] = 1
            result['success'] = True
            logger.info(f"Imported powerset: {data['name']}")

        except Exception as e:
            self.db.rollback()
            error_msg = f"Error importing powerset {powerset_dir}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    async def import_all_powersets(self, powers_root: Path) -> Dict[str, Any]:
        """Import all powersets from root powers directory

        Args:
            powers_root: Root directory containing power category folders

        Returns:
            Aggregate import results
        """
        result = {
            'success': True,
            'powersets_imported': 0,
            'powers_imported': 0,
            'skipped': 0,
            'errors': []
        }

        # Find all powerset directories (they contain index.json)
        powerset_dirs = []
        for category_dir in powers_root.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                for powerset_dir in category_dir.iterdir():
                    if powerset_dir.is_dir() and (powerset_dir / "index.json").exists():
                        powerset_dirs.append(powerset_dir)

        logger.info(f"Found {len(powerset_dirs)} powersets")

        # For now, import without archetype association (will fix later)
        for powerset_dir in powerset_dirs:
            ps_result = await self.import_powerset(powerset_dir, None)
            result['powersets_imported'] += ps_result['powersets_imported']
            result['powers_imported'] += ps_result['powers_imported']
            result['skipped'] += ps_result['skipped']
            result['errors'].extend(ps_result['errors'])

            if not ps_result['success']:
                result['success'] = False

        return result
