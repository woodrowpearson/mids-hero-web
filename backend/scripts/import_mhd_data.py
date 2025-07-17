#!/usr/bin/env python3
"""Import MHD data files into the database.

This script reads the Homecoming MHD data files and imports them into the PostgreSQL database.
It handles the dependency order and mapping between file indices and database IDs.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, DATABASE_URL
from app.mhd_parser.cli import MhdParserCLI
from app.mhd_parser.main_database_parser import MainDatabase, parse_main_database
from app.models import (
    Archetype,
    Powerset,
    Power,
    Enhancement,
    EnhancementSet,
    SetBonus,
    PowerEnhancementCompatibility,
    ImportLog,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MhdDataImporter:
    """Handles importing MHD data into the database."""
    
    def __init__(self, session: Session):
        self.session = session
        self.archetype_map: Dict[int, int] = {}  # index -> db_id
        self.powerset_map: Dict[int, int] = {}   # index -> db_id
        self.power_map: Dict[int, int] = {}      # index -> db_id
        self.enhancement_map: Dict[int, int] = {} # index -> db_id
        
    def import_origins(self, origins_file: Path) -> None:
        """Import origin data from Origins.mhd."""
        logger.info(f"Skipping origins import - Origin model not defined")
    
    def import_archetypes(self, db: MainDatabase) -> None:
        """Import archetype data."""
        logger.info(f"Importing {len(db.archetypes)} archetypes")
        
        for idx, arch in enumerate(db.archetypes):
            # Check if archetype already exists
            existing = self.session.query(Archetype).filter_by(name=arch.class_name).first()
            if existing:
                self.archetype_map[idx] = existing.id
                logger.debug(f"Archetype {arch.display_name} already exists")
                continue
                
            archetype = Archetype(
                name=arch.class_name,
                display_name=arch.display_name,
                description=arch.desc_long,
                hit_points_base=arch.hitpoints,
                hit_points_max=int(arch.hp_cap),
                primary_group=arch.primary_group,
                secondary_group=arch.secondary_group,
                # Additional attributes can be stored in JSON
                attributes={
                    "playable": arch.playable,
                    "class_type": arch.class_type,
                    "origins": arch.origins,
                    "recharge_cap": arch.recharge_cap,
                    "damage_cap": arch.damage_cap,
                    "recovery_cap": arch.recovery_cap,
                    "regen_cap": arch.regen_cap,
                    "resist_cap": arch.resist_cap,
                    "damage_resist_cap": arch.damage_resist_cap,
                    "perception_cap": arch.perception_cap,
                    "base_recovery": arch.base_recovery,
                    "base_regen": arch.base_regen,
                    "base_threat": arch.base_threat,
                }
            )
            self.session.add(archetype)
            self.session.flush()  # Get the ID
            
            self.archetype_map[idx] = archetype.id
            logger.debug(f"Created archetype: {arch.display_name}")
        
        self.session.commit()
        logger.info(f"Created {len(self.archetype_map)} archetypes")
    
    def import_powersets(self, db: MainDatabase) -> None:
        """Import powerset data."""
        logger.info(f"Importing {len(db.powersets)} powersets")
        
        for idx, ps in enumerate(db.powersets):
            # Map archetype index to database ID
            archetype_id = None
            if ps.archetype_index >= 0:
                archetype_id = self.archetype_map.get(ps.archetype_index)
                if not archetype_id:
                    logger.warning(f"Powerset {ps.display_name} references unknown archetype index {ps.archetype_index}")
            
            # Check if powerset already exists
            existing = self.session.query(Powerset).filter_by(full_name=ps.full_name).first()
            if existing:
                self.powerset_map[idx] = existing.id
                logger.debug(f"Powerset {ps.display_name} already exists")
                continue
            
            powerset = Powerset(
                archetype_id=archetype_id,
                name=ps.set_name,
                full_name=ps.full_name,
                display_name=ps.display_name,
                description=ps.description,
                set_type=ps.set_type.value,  # Convert enum to string
                group_name=ps.uid_trunk_set,
                # Store additional data in attributes
                attributes={
                    "image_name": ps.image_name,
                    "sub_name": ps.sub_name,
                    "at_class": ps.at_class,
                    "uid_link_secondary": ps.uid_link_secondary,
                    "mutex_list": ps.mutex_list,
                }
            )
            self.session.add(powerset)
            self.session.flush()
            
            self.powerset_map[idx] = powerset.id
            logger.debug(f"Created powerset: {ps.display_name}")
        
        self.session.commit()
        logger.info(f"Created {len(self.powerset_map)} powersets")
    
    def import_powers(self, db: MainDatabase) -> None:
        """Import power data."""
        logger.info(f"Importing {len(db.powers)} powers")
        
        powers_created = 0
        for idx, pwr in enumerate(db.powers):
            # Map powerset index to database ID
            powerset_id = None
            if hasattr(pwr, 'powerset_index') and pwr.powerset_index >= 0:
                powerset_id = self.powerset_map.get(pwr.powerset_index)
            
            # Check if power already exists
            existing = self.session.query(Power).filter_by(full_name=pwr.full_name).first()
            if existing:
                self.power_map[idx] = existing.id
                logger.debug(f"Power {pwr.display_name} already exists")
                continue
            
            power = Power(
                powerset_id=powerset_id,
                name=pwr.power_name,
                full_name=pwr.full_name,
                display_name=pwr.display_name,
                description=pwr.desc_long,
                short_description=pwr.desc_short,
                level_available=pwr.level,
                # Store additional attributes
                attributes={
                    "power_index": pwr.power_index,
                    "effect_area": pwr.effect_area.value if hasattr(pwr.effect_area, 'value') else pwr.effect_area,
                    "requires": getattr(pwr, 'requires', []),
                    "modes_disallowed": pwr.modes_disallowed,
                    "modes_required": pwr.modes_required,
                    "cast_time": pwr.cast_time,
                    "recharge_time": pwr.recharge_time,
                    "endurance_cost": pwr.endurance_cost,
                    "range": pwr.range,
                    "radius": pwr.radius,
                    "arc": pwr.arc,
                    "max_targets": pwr.max_targets,
                    "vector": pwr.vector.value if hasattr(pwr.vector, 'value') else pwr.vector,
                    "target": pwr.target.value if hasattr(pwr.target, 'value') else pwr.target,
                    "available": pwr.available.value if hasattr(pwr.available, 'value') else pwr.available,
                    "ai_groups": pwr.ai_groups,
                    "ignore_strength": pwr.ignore_strength,
                    "boosts_allowed": pwr.boosts_allowed,
                    "boost_sets_allowed": pwr.boost_sets_allowed,
                }
            )
            self.session.add(power)
            self.session.flush()
            
            self.power_map[idx] = power.id
            powers_created += 1
            
            if powers_created % 100 == 0:
                logger.info(f"Created {powers_created} powers...")
        
        self.session.commit()
        logger.info(f"Created {powers_created} powers total")
    
    def cleanup_database(self) -> None:
        """Remove any existing data before import."""
        logger.info("Cleaning up existing data...")
        
        # Delete in reverse dependency order
        self.session.query(SetBonus).delete()
        self.session.query(Enhancement).delete()
        self.session.query(EnhancementSet).delete()
        self.session.query(Power).delete()
        self.session.query(Powerset).delete()
        self.session.query(Archetype).delete()
        
        self.session.commit()
        logger.info("Database cleaned")


@click.command()
@click.option('--data-dir', '-d', type=Path, 
              default='/Users/w/code/mids-hero-web/data/Homecoming_2025-7-1111',
              help='Directory containing MHD files')
@click.option('--clean', is_flag=True, help='Clean database before import')
@click.option('--dry-run', is_flag=True, help='Perform a dry run without database changes')
def main(data_dir: Path, clean: bool, dry_run: bool):
    """Import MHD data files into the database."""
    if not data_dir.exists():
        logger.error(f"Data directory {data_dir} does not exist")
        sys.exit(1)
    
    # Create database session
    database_url = DATABASE_URL
    if dry_run:
        logger.info("DRY RUN - No database changes will be made")
        database_url = "sqlite:///:memory:"
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        importer = MhdDataImporter(session)
        
        if clean and not dry_run:
            importer.cleanup_database()
        
        # Import origins first (no dependencies)
        origins_file = data_dir / "Origins.mhd"
        if origins_file.exists():
            importer.import_origins(origins_file)
        
        # Parse the main database
        main_db_file = data_dir / "I12.mhd"
        if not main_db_file.exists():
            logger.error(f"Main database file {main_db_file} not found")
            sys.exit(1)
        
        logger.info(f"Parsing main database from {main_db_file}")
        with open(main_db_file, 'rb') as f:
            db = parse_main_database(f)
        
        logger.info(f"Parsed database with:")
        logger.info(f"  - {len(db.archetypes)} archetypes")
        logger.info(f"  - {len(db.powersets)} powersets")
        logger.info(f"  - {len(db.powers)} powers")
        logger.info(f"  - {len(db.summons)} summons")
        
        # Import in dependency order
        importer.import_archetypes(db)
        importer.import_powersets(db)
        importer.import_powers(db)
        
        if not dry_run:
            logger.info("Import completed successfully!")
        else:
            logger.info("Dry run completed - no data was saved")
            
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()