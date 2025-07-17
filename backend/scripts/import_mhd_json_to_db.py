#!/usr/bin/env python3
"""
Import MHD JSON data into PostgreSQL database.
This script loads the JSON files exported from MHD files into the database.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import (
    Archetype, Powerset, Power, PowerPrerequisite,
    EnhancementSet, Enhancement, SetBonus,
    ImportLog
)


class MHDDataImporter:
    """Import MHD data from JSON files into database."""
    
    def __init__(self, json_dir: str, db_url: str = None):
        self.json_dir = Path(json_dir)
        self.db_url = db_url or os.environ.get(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/mids_web'
        )
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.import_log = None
        self.stats = {
            'archetypes': 0,
            'powersets': 0,
            'powers': 0,
            'enhancements': 0,
            'enhancement_sets': 0,
            'errors': 0
        }
    
    def import_all(self):
        """Import all data in the correct order."""
        print(f"Starting import from {self.json_dir}")
        print(f"Database: {self.db_url}")
        
        # Test database connection
        if not self.test_connection():
            return False
        
        # Create import log
        session = self.Session()
        try:
            self.import_log = ImportLog(
                import_type='full',
                source_file=str(self.json_dir),
                game_version='Homecoming 2025.7.1111',
                started_at=datetime.utcnow()
            )
            session.add(self.import_log)
            session.commit()
            
            # Import in dependency order
            print("\n1. Importing Archetypes...")
            self.import_archetypes(session)
            
            print("\n2. Importing Powersets...")
            self.import_powersets(session)
            
            print("\n3. Importing Powers...")
            self.import_powers(session)
            
            print("\n4. Importing Enhancement Sets...")
            self.import_enhancement_sets(session)
            
            print("\n5. Importing Enhancements...")
            self.import_enhancements(session)
            
            # Update import log
            self.import_log.completed_at = datetime.utcnow()
            self.import_log.records_processed = sum(self.stats.values())
            self.import_log.records_imported = sum(
                v for k, v in self.stats.items() if k != 'errors'
            )
            self.import_log.errors = self.stats['errors']
            self.import_log.import_data = self.stats
            session.commit()
            
            print("\n" + "="*50)
            print("Import Summary:")
            print(f"  Archetypes: {self.stats['archetypes']}")
            print(f"  Powersets: {self.stats['powersets']}")
            print(f"  Powers: {self.stats['powers']}")
            print(f"  Enhancement Sets: {self.stats['enhancement_sets']}")
            print(f"  Enhancements: {self.stats['enhancements']}")
            print(f"  Errors: {self.stats['errors']}")
            print("="*50)
            
            return True
            
        except Exception as e:
            print(f"\nError during import: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
            return False
        finally:
            session.close()
    
    def test_connection(self):
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✓ Database connection successful")
                return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def import_archetypes(self, session):
        """Import archetypes from JSON."""
        file_path = self.json_dir / 'archetypes.json'
        if not file_path.exists():
            print(f"  File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing archetypes (optional - remove if appending)
        session.query(Archetype).delete()
        session.commit()  # Commit the delete before inserting
        
        for item in data:
            try:
                archetype = Archetype(
                    id=item['id'],
                    name=item['name'],
                    display_name=item['display_name'],
                    description=item['description'],
                    primary_group=item['primary_group'],
                    secondary_group=item['secondary_group'],
                    hit_points_base=item['hit_points_base'],
                    hit_points_max=item['hit_points_max']
                )
                session.add(archetype)
                self.stats['archetypes'] += 1
            except Exception as e:
                print(f"  Error importing archetype {item.get('name', 'unknown')}: {e}")
                self.stats['errors'] += 1
        
        session.commit()
        print(f"  Imported {self.stats['archetypes']} archetypes")
    
    def import_powersets(self, session):
        """Import powersets from JSON."""
        file_path = self.json_dir / 'powersets.json'
        if not file_path.exists():
            print(f"  File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing powersets
        session.query(Powerset).delete()
        session.commit()  # Commit the delete before inserting
        
        for item in data:
            try:
                powerset = Powerset(
                    id=item['id'],
                    name=item['name'],
                    display_name=item['display_name'],
                    description=item.get('description', ''),
                    archetype_id=item['archetype_id'],
                    powerset_type=item['powerset_type'],
                    icon_path=item.get('icon_path')
                )
                session.add(powerset)
                self.stats['powersets'] += 1
            except Exception as e:
                print(f"  Error importing powerset {item.get('name', 'unknown')}: {e}")
                self.stats['errors'] += 1
        
        session.commit()
        print(f"  Imported {self.stats['powersets']} powersets")
    
    def import_powers(self, session):
        """Import powers from JSON."""
        file_path = self.json_dir / 'powers.json'
        if not file_path.exists():
            print(f"  File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            print("  No powers to import (placeholder file)")
            return
        
        # Clear existing powers
        session.query(Power).delete()
        session.commit()  # Commit the delete before inserting
        
        for item in data:
            try:
                power = Power(
                    id=item['id'],
                    name=item['name'],
                    display_name=item['display_name'],
                    description=item.get('description', ''),
                    powerset_id=item['powerset_id'],
                    level_available=item.get('level_available', 1),
                    power_type=item.get('power_type'),
                    target_type=item.get('target_type'),
                    accuracy=item.get('accuracy', 1.0),
                    damage_scale=item.get('damage_scale'),
                    endurance_cost=item.get('endurance_cost'),
                    recharge_time=item.get('recharge_time'),
                    activation_time=item.get('activation_time'),
                    range_feet=item.get('range_feet'),
                    radius_feet=item.get('radius_feet'),
                    max_targets=item.get('max_targets'),
                    effects=item.get('effects'),
                    icon_path=item.get('icon_path'),
                    display_order=item.get('display_order')
                )
                session.add(power)
                self.stats['powers'] += 1
            except Exception as e:
                print(f"  Error importing power {item.get('name', 'unknown')}: {e}")
                self.stats['errors'] += 1
        
        session.commit()
        print(f"  Imported {self.stats['powers']} powers")
    
    def import_enhancement_sets(self, session):
        """Import enhancement sets from JSON."""
        file_path = self.json_dir / 'enhancement_sets.json'
        if not file_path.exists():
            print(f"  File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            print("  No enhancement sets to import")
            return
        
        # Clear existing enhancement sets
        session.query(EnhancementSet).delete()
        session.commit()  # Commit the delete before inserting
        
        for item in data:
            try:
                enh_set = EnhancementSet(
                    id=item['id'],
                    name=item['name'],
                    display_name=item['display_name'],
                    description=item.get('description', ''),
                    min_level=item.get('min_level', 10),
                    max_level=item.get('max_level', 50)
                )
                session.add(enh_set)
                self.stats['enhancement_sets'] += 1
            except Exception as e:
                print(f"  Error importing enhancement set {item.get('name', 'unknown')}: {e}")
                self.stats['errors'] += 1
        
        session.commit()
        print(f"  Imported {self.stats['enhancement_sets']} enhancement sets")
    
    def import_enhancements(self, session):
        """Import enhancements from JSON."""
        file_path = self.json_dir / 'enhancements.json'
        if not file_path.exists():
            print(f"  File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            print("  No enhancements to import")
            return
        
        # Clear existing enhancements
        session.query(Enhancement).delete()
        session.commit()  # Commit the delete before inserting
        
        for item in data:
            try:
                enhancement = Enhancement(
                    id=item['id'],
                    name=item['name'],
                    display_name=item['display_name'],
                    enhancement_type=item['enhancement_type'],
                    set_id=item.get('set_id'),
                    level_min=item.get('level_min', 1),
                    level_max=item.get('level_max', 50),
                    accuracy_bonus=item.get('accuracy_bonus'),
                    damage_bonus=item.get('damage_bonus'),
                    endurance_bonus=item.get('endurance_bonus'),
                    recharge_bonus=item.get('recharge_bonus'),
                    defense_bonus=item.get('defense_bonus'),
                    resistance_bonus=item.get('resistance_bonus'),
                    other_bonuses=item.get('other_bonuses'),
                    unique_enhancement=item.get('unique_enhancement', False),
                    icon_path=item.get('icon_path')
                )
                session.add(enhancement)
                self.stats['enhancements'] += 1
            except Exception as e:
                print(f"  Error importing enhancement {item.get('name', 'unknown')}: {e}")
                self.stats['errors'] += 1
        
        session.commit()
        print(f"  Imported {self.stats['enhancements']} enhancements")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python import_mhd_json_to_db.py <json_dir> [database_url]")
        print("Example: python import_mhd_json_to_db.py ../data/exported-json")
        sys.exit(1)
    
    json_dir = sys.argv[1]
    db_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    importer = MHDDataImporter(json_dir, db_url)
    success = importer.import_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()