#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["sqlalchemy", "psycopg2-binary"]
# ///
"""Database statistics script for import monitoring."""

import os
from sqlalchemy import create_engine, text

def main():
    """Print database record counts for all import tables."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mids_web')
    engine = create_engine(database_url)
    
    tables = [
        'archetypes', 'powersets', 'powers', 'enhancements', 
        'salvage', 'recipes', 'attribute_modifiers', 'type_grades'
    ]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                print(f'{table:20}: {count:>8,} records')
            except Exception:
                print(f'{table:20}: Table not found')

if __name__ == '__main__':
    main()