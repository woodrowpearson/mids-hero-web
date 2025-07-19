#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["sqlalchemy", "psycopg2-binary"]
# ///
"""Database optimization script for import operations."""

import os
from sqlalchemy import create_engine, text

def main():
    """Optimize database for import operations."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/mids_web')
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        try:
            conn.execute(text('REFRESH MATERIALIZED VIEW power_build_summary'))
            print('✅ Power build summary materialized view refreshed')
        except Exception as e:
            print(f'⚠️ Materialized view refresh failed: {e}')
        
        try:
            conn.execute(text('ANALYZE'))
            print('✅ Database statistics updated')
        except Exception as e:
            print(f'⚠️ Database analyze failed: {e}')

if __name__ == '__main__':
    main()