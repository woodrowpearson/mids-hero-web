"""Base importer class for data import operations."""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import ImportLog

logger = logging.getLogger(__name__)


class BaseImporter(ABC):
    """Base class for all data importers."""

    def __init__(self, database_url: str, batch_size: int = 1000):
        """Initialize the importer.

        Args:
            database_url: Database connection string
            batch_size: Number of records to process in each batch
        """
        self.database_url = database_url
        self.batch_size = batch_size
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.errors: list[dict[str, Any]] = []
        self.processed_count = 0
        self.imported_count = 0

    @abstractmethod
    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        pass

    @abstractmethod
    def get_model_class(self) -> type[Base]:
        """Get the SQLAlchemy model class for this importer."""
        pass

    @abstractmethod
    def transform_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform raw JSON data to model-compatible format.

        Args:
            raw_data: Raw data from JSON file

        Returns:
            Dictionary ready for model creation
        """
        pass

    def load_json_file(self, file_path: Path) -> dict[str, Any]:
        """Load data from JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            Parsed JSON data
        """
        logger.info(f"Loading JSON file: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        logger.info(
            f"Loaded {len(data) if isinstance(data, list) else 'object'} from {file_path}"
        )
        return data

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Validate transformed data before import.

        Args:
            data: Transformed data dictionary

        Returns:
            True if valid, False otherwise
        """
        # Basic validation - can be overridden by subclasses
        return bool(data)

    def import_batch(self, session: Session, batch: list[dict[str, Any]]) -> int:
        """Import a batch of records.

        Args:
            session: Database session
            batch: List of records to import

        Returns:
            Number of successfully imported records
        """
        model_class = self.get_model_class()
        imported = 0

        try:
            # Use bulk_insert_mappings for better performance
            session.bulk_insert_mappings(model_class, batch)
            session.commit()
            imported = len(batch)
            logger.info(f"Imported batch of {imported} records")
        except IntegrityError as e:
            # Try individual inserts on integrity error
            session.rollback()
            logger.warning(f"Batch insert failed, trying individual inserts: {e}")

            for record in batch:
                try:
                    obj = model_class(**record)
                    session.add(obj)
                    session.commit()
                    imported += 1
                except Exception as record_error:
                    session.rollback()
                    self.errors.append({"record": record, "error": str(record_error)})
                    logger.error(f"Failed to import record: {record_error}")

        return imported

    def import_data(self, file_path: Path, resume_from: int = 0) -> ImportLog:
        """Import data from JSON file.

        Args:
            file_path: Path to JSON file
            resume_from: Index to resume from (for large datasets)

        Returns:
            ImportLog record
        """
        session = self.SessionLocal()
        import_log = ImportLog(
            import_type=self.get_import_type(),
            source_file=str(file_path),
            records_processed=0,
            records_imported=0,
            errors=0,
            started_at=datetime.utcnow(),
        )

        # Add import_log to session immediately to prevent detached instance errors
        session.add(import_log)
        session.commit()
        import_log_id = import_log.id

        try:
            # Load and prepare data
            raw_data = self.load_json_file(file_path)

            # Handle different JSON structures
            if isinstance(raw_data, dict):
                # Look for a key that contains the list of items
                items = None
                for key in raw_data:
                    if isinstance(raw_data[key], list):
                        items = raw_data[key]
                        break

                if items is None:
                    # Single item
                    items = [raw_data]
            else:
                items = raw_data

            total_items = len(items)
            logger.info(f"Processing {total_items} items (resuming from {resume_from})")

            # Process in batches
            batch = []
            for i in range(resume_from, total_items):
                item = items[i]
                self.processed_count += 1

                # Log progress every 10%
                if self.processed_count % max(1, total_items // 10) == 0:
                    progress = (self.processed_count / total_items) * 100
                    logger.info(
                        f"Progress: {progress:.1f}% ({self.processed_count}/{total_items})"
                    )

                # Transform and validate
                try:
                    transformed = self.transform_data(item)
                    if self.validate_data(transformed):
                        batch.append(transformed)
                    else:
                        self.errors.append(
                            {"record": item, "error": "Validation failed"}
                        )
                except Exception as e:
                    self.errors.append({"record": item, "error": str(e)})
                    logger.error(f"Failed to transform record: {e}")
                    continue

                # Import batch when full
                if len(batch) >= self.batch_size:
                    self.imported_count += self.import_batch(session, batch)
                    batch = []

            # Import remaining records
            if batch:
                self.imported_count += self.import_batch(session, batch)

            # Update import log - refresh from DB to avoid detached instance issues
            import_log = session.query(ImportLog).filter_by(id=import_log_id).first()
            import_log.records_processed = self.processed_count
            import_log.records_imported = self.imported_count
            import_log.errors = len(self.errors)
            import_log.import_data = {
                "errors": self.errors[:100]  # Store first 100 errors
            }
            import_log.completed_at = datetime.utcnow()

            session.commit()

            logger.info(
                f"Import completed: {self.imported_count}/{self.processed_count} imported, "
                f"{len(self.errors)} errors"
            )

        except Exception as e:
            logger.error(f"Import failed: {e}")
            # Refresh import_log from DB to avoid detached instance issues
            try:
                import_log = session.query(ImportLog).filter_by(id=import_log_id).first()
                if import_log:
                    import_log.errors = -1  # Indicate fatal error
                    import_log.import_data = {"fatal_error": str(e)}
                    import_log.completed_at = datetime.utcnow()
                    session.commit()
            except Exception as log_error:
                logger.error(f"Failed to update import log: {log_error}")
            raise
        finally:
            session.close()

        # Return a simple dict instead of the SQLAlchemy object to avoid detached instance issues
        return type('ImportLogResult', (), {
            'records_imported': self.imported_count,
            'records_processed': self.processed_count,
            'errors': len(self.errors)
        })()

    def clear_existing_data(self) -> None:
        """Clear existing data for this model type.

        WARNING: This will delete all existing records!
        """
        session = self.SessionLocal()
        try:
            model_class = self.get_model_class()
            count = session.query(model_class).count()

            if count > 0:
                logger.warning(
                    f"Deleting {count} existing {model_class.__name__} records"
                )
                session.query(model_class).delete()
                session.commit()
                logger.info(f"Deleted {count} records")
        finally:
            session.close()
