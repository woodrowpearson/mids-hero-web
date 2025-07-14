#!/usr/bin/env python3
"""Manual database migration script to apply schema directly."""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.database import Base
from app.models import *  # Import all models

def main():
    """Apply the database schema manually."""
    # Database URL for the Docker container
    database_url = "postgresql://postgres:postgres@localhost:5432/mids_web"
    
    print(f"🔗 Connecting to database: {database_url}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")
        
        # Create all tables
        print("🏗️  Creating database tables...")
        Base.metadata.create_all(engine)
        
        print("✅ Database schema applied successfully!")
        
        # Verify tables were created
        print("🔍 Verifying tables...")
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            print(f"📊 Created {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()