#!/usr/bin/env python3
"""
Data Import Utility for Mids Hero Web
Imports JSON data exported from City of Heroes .mhd files into PostgreSQL database.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add backend app to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class DataImporter:
    def __init__(self, json_data_path: str):
        self.json_data_path = Path(json_data_path)
        self.db_url = "postgresql://postgres:postgres@localhost:5432/mids_web"
        
    def import_all_data(self):
        """Import all available JSON data into the database."""
        print(f"Starting data import from {self.json_data_path}")
        
        # Import AttribMod data
        self.import_attrib_mod_data()
        
        # Import TypeGrades data
        self.import_type_grades_data()
        
        print("Data import completed successfully!")
        
    def import_attrib_mod_data(self):
        """Import attribute modifier data."""
        attrib_mod_file = self.json_data_path / "AttribMod.json"
        if not attrib_mod_file.exists():
            print(f"Warning: {attrib_mod_file} not found, skipping...")
            return
            
        print(f"Importing attribute modifier data from {attrib_mod_file}")
        
        with open(attrib_mod_file, 'r') as f:
            attrib_data = json.load(f)
        
        # TODO: Process and import attrib mod data
        # This requires understanding the exact structure and mapping to database tables
        print(f"  Loaded {len(attrib_data.get('Modifier', []))} attribute modifiers")
        
    def import_type_grades_data(self):
        """Import enhancement type grades data."""
        type_grades_file = self.json_data_path / "TypeGrades.json"
        if not type_grades_file.exists():
            print(f"Warning: {type_grades_file} not found, skipping...")
            return
            
        print(f"Importing type grades data from {type_grades_file}")
        
        with open(type_grades_file, 'r') as f:
            type_grades_data = json.load(f)
        
        # Import SetTypes
        set_types = type_grades_data.get('SetTypes', [])
        print(f"  Found {len(set_types)} set types")
        
        # Import EnhancementGrades
        enhancement_grades = type_grades_data.get('EnhancementGrades', [])
        print(f"  Found {len(enhancement_grades)} enhancement grades")
        
        # Import SpecialEnhancementTypes
        special_types = type_grades_data.get('SpecialEnhancementTypes', [])
        print(f"  Found {len(special_types)} special enhancement types")
        
        # TODO: Implement actual database insertion
        # This requires proper mapping to the database schema
        
    def test_database_connection(self):
        """Test database connection."""
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("Database connection successful!")
                return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_json_data.py <json_data_path>")
        print("Example: python import_json_data.py ~/code/mids-hero-web/data/exported-json")
        sys.exit(1)
    
    json_data_path = sys.argv[1]
    
    # Expand tilde paths
    if json_data_path.startswith('~/'):
        json_data_path = os.path.expanduser(json_data_path)
    
    importer = DataImporter(json_data_path)
    
    # Test database connection first
    if not importer.test_database_connection():
        print("Please ensure database is running and accessible.")
        sys.exit(1)
    
    # Run import
    importer.import_all_data()

if __name__ == "__main__":
    main()