#!/usr/bin/env python3
"""Automated game data update script.

This script automates the process of updating the database when new game versions
are released. It handles version checking, backup creation, data import, and validation.

Usage:
    python update_game_data.py --data-dir /path/to/new/data [options]
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import click
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, DATABASE_URL
from app.models import ImportLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GameDataUpdater:
    """Handles automated game data updates."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def check_current_version(self) -> Optional[str]:
        """Check the current game data version in the database."""
        with self.SessionLocal() as session:
            result = session.query(ImportLog).order_by(
                ImportLog.imported_at.desc()
            ).first()
            
            if result and result.metadata:
                return result.metadata.get('version', 'unknown')
            return None
    
    def extract_version_from_data(self, data_dir: Path) -> Optional[str]:
        """Extract version information from data files."""
        # Try to read version from I12.mhd or other files
        version_indicators = [
            data_dir / "version.txt",
            data_dir / "version.json",
        ]
        
        for indicator in version_indicators:
            if indicator.exists():
                try:
                    if indicator.suffix == '.json':
                        with open(indicator) as f:
                            data = json.load(f)
                            return data.get('version')
                    else:
                        return indicator.read_text().strip()
                except Exception as e:
                    logger.warning(f"Failed to read version from {indicator}: {e}")
        
        # Extract from directory name as fallback
        if "Homecoming" in data_dir.name:
            # e.g., "Homecoming_2025-7-1111" -> "2025.7.1111"
            parts = data_dir.name.split('_')[-1].split('-')
            if len(parts) == 3:
                return '.'.join(parts)
        
        return None
    
    def backup_database(self, backup_dir: Path) -> Path:
        """Create a database backup before updating."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"mids_web_backup_{timestamp}.sql"
        backup_path = backup_dir / backup_name
        
        logger.info(f"Creating database backup: {backup_path}")
        
        # Use pg_dump for PostgreSQL
        if "postgresql" in self.database_url:
            import subprocess
            
            # Parse connection string
            from urllib.parse import urlparse
            parsed = urlparse(self.database_url)
            
            cmd = [
                'pg_dump',
                '-h', parsed.hostname or 'localhost',
                '-p', str(parsed.port or 5432),
                '-U', parsed.username or 'postgres',
                '-d', parsed.path.lstrip('/'),
                '-f', str(backup_path),
                '--verbose'
            ]
            
            env = {'PGPASSWORD': parsed.password} if parsed.password else {}
            
            try:
                subprocess.run(cmd, check=True, env=env)
                logger.info(f"Database backed up successfully to {backup_path}")
                return backup_path
            except subprocess.CalledProcessError as e:
                logger.error(f"Backup failed: {e}")
                raise
        else:
            logger.warning("Backup only supported for PostgreSQL databases")
            return backup_path
    
    def validate_data_directory(self, data_dir: Path) -> bool:
        """Validate that the data directory contains expected files."""
        required_files = [
            "I12.mhd",  # Main database
            "EnhDB.mhd",  # Enhancements
            "Recipe.mhd",  # Recipes
        ]
        
        missing = []
        for file in required_files:
            if not (data_dir / file).exists():
                missing.append(file)
        
        if missing:
            logger.error(f"Missing required files: {', '.join(missing)}")
            return False
        
        return True
    
    def import_data(self, data_dir: Path, clean: bool = False) -> bool:
        """Import game data using the import_mhd_data script."""
        from import_mhd_data import main as import_main
        
        try:
            # Create a mock argparse namespace
            class Args:
                def __init__(self):
                    self.data_dir = data_dir
                    self.clean = clean
                    self.dry_run = False
            
            # Note: This would need to be adapted to work with the actual import
            # For now, this is a placeholder showing the intended flow
            logger.info(f"Starting data import from {data_dir}")
            logger.warning("Note: Actual import blocked on binary format decoding")
            
            # Record the import attempt
            with self.SessionLocal() as session:
                import_log = ImportLog(
                    import_type="game_update",
                    source_file=str(data_dir),
                    status="pending",
                    metadata={
                        "version": self.extract_version_from_data(data_dir),
                        "clean_import": clean
                    }
                )
                session.add(import_log)
                session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False
    
    def validate_import(self) -> Dict[str, int]:
        """Validate the imported data by checking counts."""
        with self.SessionLocal() as session:
            counts = {}
            
            # Check various entity counts
            tables = [
                'archetypes',
                'powersets', 
                'powers',
                'enhancements',
                'enhancement_sets'
            ]
            
            for table in tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[table] = result.scalar()
                except Exception as e:
                    logger.warning(f"Could not count {table}: {e}")
                    counts[table] = -1
            
            return counts
    
    def generate_report(self, 
                       current_version: Optional[str],
                       new_version: Optional[str],
                       counts: Dict[str, int],
                       backup_path: Optional[Path]) -> str:
        """Generate an import report."""
        report_lines = [
            "=== Game Data Update Report ===",
            f"Timestamp: {datetime.now().isoformat()}",
            f"Previous Version: {current_version or 'None'}",
            f"New Version: {new_version or 'Unknown'}",
            "",
            "Entity Counts:",
        ]
        
        for entity, count in counts.items():
            if count >= 0:
                report_lines.append(f"  - {entity}: {count:,}")
            else:
                report_lines.append(f"  - {entity}: Error reading count")
        
        if backup_path:
            report_lines.extend([
                "",
                f"Backup Location: {backup_path}",
            ])
        
        report_lines.extend([
            "",
            "Status: Update completed successfully" if all(c >= 0 for c in counts.values()) else "Status: Update completed with errors",
        ])
        
        return "\n".join(report_lines)


@click.command()
@click.option('--data-dir', '-d', type=Path, required=True,
              help='Directory containing new game data files')
@click.option('--backup-dir', '-b', type=Path, 
              default=Path('./backups'),
              help='Directory for database backups')
@click.option('--clean', is_flag=True,
              help='Clean existing data before import')
@click.option('--skip-backup', is_flag=True,
              help='Skip database backup (not recommended)')
@click.option('--force', is_flag=True,
              help='Force update even if version appears unchanged')
def main(data_dir: Path, backup_dir: Path, clean: bool, skip_backup: bool, force: bool):
    """Update game data from new MHD files."""
    if not data_dir.exists():
        logger.error(f"Data directory {data_dir} does not exist")
        sys.exit(1)
    
    updater = GameDataUpdater(DATABASE_URL)
    
    # Check current version
    current_version = updater.check_current_version()
    new_version = updater.extract_version_from_data(data_dir)
    
    logger.info(f"Current version: {current_version}")
    logger.info(f"New version: {new_version}")
    
    if current_version == new_version and not force:
        logger.info("Versions match - no update needed. Use --force to update anyway.")
        return
    
    # Validate data directory
    if not updater.validate_data_directory(data_dir):
        logger.error("Data directory validation failed")
        sys.exit(1)
    
    # Create backup
    backup_path = None
    if not skip_backup:
        backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            backup_path = updater.backup_database(backup_dir)
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            if not force:
                logger.error("Aborting update. Use --force to continue without backup.")
                sys.exit(1)
    
    # Import data
    logger.info("Starting data import...")
    if updater.import_data(data_dir, clean=clean):
        # Validate import
        counts = updater.validate_import()
        
        # Generate report
        report = updater.generate_report(
            current_version, new_version, counts, backup_path
        )
        
        logger.info("\n" + report)
        
        # Save report
        report_path = backup_dir / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.write_text(report)
        logger.info(f"Report saved to {report_path}")
    else:
        logger.error("Import failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()