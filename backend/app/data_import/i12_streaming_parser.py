"""Streaming JSON parser for I12 power data (360K+ entries)."""

import json
import logging
import time
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any

import psutil
from sqlalchemy.orm import Session

from app.models import Archetype, Power, Powerset

from .base_importer import BaseImporter

logger = logging.getLogger(__name__)


class StreamingJsonReader:
    """Streaming JSON reader for large files."""

    def __init__(self, chunk_size: int = 1000):
        """Initialize streaming reader.

        Args:
            chunk_size: Number of records to read per chunk
        """
        self.chunk_size = chunk_size

    def read_chunks(
        self,
        file_path: Path,
        progress_callback: Callable[[int, int, float], None] | None = None,
    ) -> Generator[list[dict[str, Any]], None, None]:
        """Read JSON file in chunks to control memory usage.

        Args:
            file_path: Path to JSON file
            progress_callback: Optional callback for progress updates

        Yields:
            Lists of records (chunks)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                # Load the entire JSON first to get total count
                # This is a trade-off for progress tracking
                data = json.load(f)

                if not isinstance(data, list):
                    raise ValueError("JSON file must contain an array of records")

                total_records = len(data)
                processed = 0

                # Process in chunks
                for i in range(0, total_records, self.chunk_size):
                    chunk = data[i : i + self.chunk_size]
                    processed += len(chunk)

                    # Call progress callback if provided
                    if progress_callback:
                        percentage = (processed / total_records) * 100
                        progress_callback(processed, total_records, percentage)

                    yield chunk

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise


class PowerDataProcessor:
    """Processor for transforming I12 power data."""

    def __init__(self):
        """Initialize the processor."""
        self._powerset_cache: dict[str, int] = {}
        self._archetype_cache: dict[str, int] = {}

    def load_caches(self, session: Session) -> None:
        """Load archetype and powerset caches."""
        # Load archetypes
        archetypes = session.query(Archetype.id, Archetype.name).all()
        self._archetype_cache = {arch.name: arch.id for arch in archetypes}
        logger.info(f"Loaded {len(self._archetype_cache)} archetypes into cache")

        # Load powersets
        powersets = session.query(Powerset.id, Powerset.name).all()
        self._powerset_cache = {ps.name: ps.id for ps in powersets}
        logger.info(f"Loaded {len(self._powerset_cache)} powersets into cache")

    def transform_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform I12 power data to model-compatible format.

        Args:
            raw_data: Raw I12 power data

        Returns:
            Dictionary ready for Power model creation
        """
        # Extract basic information
        name = raw_data.get("Name", "")
        internal_name = raw_data.get("InternalName", name)
        display_name = raw_data.get("DisplayName", name)
        description = raw_data.get("Description", f"{name} power")

        # Extract powerset information
        powerset_name = raw_data.get("PowersetName", "")
        powerset_id = self._powerset_cache.get(powerset_name)
        if not powerset_id:
            raise ValueError(f"Unknown powerset: {powerset_name}")

        # Extract level and type information
        level = raw_data.get("Level", 1)
        power_type = self._determine_power_type(raw_data)
        target_type = self._normalize_target_type(raw_data.get("TargetType", "Self"))

        # Extract numeric attributes with defaults
        accuracy = float(raw_data.get("Accuracy", 1.0))
        endurance_cost = float(raw_data.get("EnduranceCost", 0.0))
        recharge_time = float(raw_data.get("RechargeTime", 0.0))
        activation_time = float(raw_data.get("ActivationTime", 0.0))
        range_feet = raw_data.get("Range")
        radius_feet = raw_data.get("Radius")
        max_targets = raw_data.get("MaxTargets")

        # Extract complex data as JSON
        effects = raw_data.get("Effects", [])
        requirements = raw_data.get("Requirements", {})
        enhancement_types = raw_data.get("EnhancementTypes", [])

        # Build transformed data
        transformed = {
            "name": name,
            "internal_name": internal_name,
            "display_name": display_name,
            "description": description,
            "powerset_id": powerset_id,
            "level_available": int(level) if level else 1,
            "power_type": power_type,
            "target_type": target_type,
            "accuracy": accuracy,
            "endurance_cost": endurance_cost,
            "recharge_time": recharge_time,
            "activation_time": activation_time,
            "range_feet": int(range_feet) if range_feet else None,
            "radius_feet": int(radius_feet) if radius_feet else None,
            "max_targets": int(max_targets) if max_targets else None,
            "effects": effects,
            "effect_groups": self._extract_effect_groups(effects),
            "requires_line_of_sight": raw_data.get("RequiresLineOfSight", True),
            "modes_required": requirements.get("ModesRequired"),
            "modes_disallowed": requirements.get("ModesDisallowed"),
            "ai_report": raw_data.get("AIReport"),
            "display_info": {
                "enhancement_types": enhancement_types,
                "power_category": raw_data.get("PowerCategory"),
                "icon_name": raw_data.get("IconName"),
            },
            "icon_path": f"powers/{name.lower().replace(' ', '_')}.png",
            "display_order": raw_data.get("DisplayOrder", level),
        }

        return transformed

    def _determine_power_type(self, power_data: dict[str, Any]) -> str:
        """Determine power type from I12 data."""
        effects = power_data.get("Effects", [])
        target_type = power_data.get("TargetType", "").lower()
        power_type = power_data.get("PowerType", "").lower()

        # Analyze effects to determine type
        for effect in effects:
            effect_type = effect.get("EffectType", "").lower()

            if effect_type in ["damage", "damageovertime"]:
                return "attack"
            elif effect_type in ["defense", "resistance", "defenseovertime"]:
                return "defense"
            elif effect_type in [
                "hold",
                "immobilize",
                "stun",
                "sleep",
                "confuse",
                "fear",
            ]:
                return "control"
            elif effect_type in ["heal", "healovertime", "endurancerecovery"]:
                return "support"
            elif effect_type in ["fly", "superspeed", "superjump", "teleport"]:
                return "travel"

        # Fallback based on target type
        if target_type == "enemy":
            return "attack"
        elif target_type == "self" and power_type == "toggle":
            return "defense"

        return "support"  # Default

    def _normalize_target_type(self, target_type: str) -> str:
        """Normalize target type values."""
        target_type = target_type.lower()

        if target_type in ["enemy", "foe", "hostile"]:
            return "enemy"
        elif target_type in ["ally", "friend", "teammate"]:
            return "ally"
        elif target_type in ["self", "caster"]:
            return "self"
        elif target_type in ["location", "ground", "area"]:
            return "location"

        return "self"  # Default

    def _extract_effect_groups(
        self, effects: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Extract and organize effect groups from effects list."""
        groups = {}

        for effect in effects:
            effect_type = effect.get("EffectType", "Unknown")

            if effect_type not in groups:
                groups[effect_type] = {
                    "type": effect_type,
                    "effects": [],
                    "summary": {
                        "count": 0,
                        "avg_scale": 0.0,
                        "avg_duration": 0.0,
                        "avg_chance": 0.0,
                    },
                }

            groups[effect_type]["effects"].append(effect)

            # Update summary statistics
            summary = groups[effect_type]["summary"]
            summary["count"] += 1

            # Calculate running averages
            scale = effect.get("Scale", 0.0)
            duration = effect.get("Duration", 0.0)
            chance = effect.get("Chance", 1.0)

            count = summary["count"]
            summary["avg_scale"] = (
                (summary["avg_scale"] * (count - 1)) + scale
            ) / count
            summary["avg_duration"] = (
                (summary["avg_duration"] * (count - 1)) + duration
            ) / count
            summary["avg_chance"] = (
                (summary["avg_chance"] * (count - 1)) + chance
            ) / count

        return list(groups.values())

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Validate transformed power data."""
        # Check required fields
        required_fields = ["name", "powerset_id", "level_available"]
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Missing required field: {field}")
                return False

        # Validate numeric fields
        numeric_fields = [
            ("level_available", 1, 50),
            ("accuracy", 0.0, 10.0),
            ("endurance_cost", 0.0, 100.0),
            ("recharge_time", 0.0, 10000.0),
            ("activation_time", 0.0, 60.0),
        ]

        for field, min_val, max_val in numeric_fields:
            value = data.get(field)
            if value is not None:
                if not isinstance(value, int | float):
                    logger.error(f"Field {field} must be numeric, got {type(value)}")
                    return False
                if value < min_val or value > max_val:
                    logger.error(
                        f"Field {field} value {value} out of range [{min_val}, {max_val}]"
                    )
                    return False

        return True


class I12StreamingParser(BaseImporter):
    """Streaming parser for I12 power data with memory management."""

    def __init__(
        self,
        database_url: str,
        batch_size: int = 1000,
        chunk_size: int = 5000,
        memory_limit_gb: float = 1.0,
    ):
        """Initialize streaming parser.

        Args:
            database_url: Database connection URL
            batch_size: Number of records to process in database batches
            chunk_size: Number of records to read from file at once
            memory_limit_gb: Memory limit in GB before forcing garbage collection
        """
        super().__init__(database_url, batch_size)
        self.chunk_size = chunk_size
        self.memory_limit_bytes = memory_limit_gb * 1024 * 1024 * 1024

        self.reader = StreamingJsonReader(chunk_size)
        self.processor = PowerDataProcessor()

        # Statistics
        self.processed_count = 0
        self.imported_count = 0
        self.error_count = 0
        self.errors: list[dict[str, Any]] = []

    def get_import_type(self) -> str:
        """Get the type of import for logging."""
        return "i12_powers"

    def get_model_class(self) -> type[Power]:
        """Get the SQLAlchemy model class for this importer."""
        return Power

    def transform_data(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Transform using the processor."""
        return self.processor.transform_data(raw_data)

    def validate_data(self, data: dict[str, Any]) -> bool:
        """Validate using the processor."""
        return self.processor.validate_data(data)

    def import_data(
        self,
        file_path: Path,
        resume_from: int = 0,
        progress_callback: Callable[[int, int, float], None] | None = None,
    ) -> None:
        """Import I12 power data with streaming and progress tracking.

        Args:
            file_path: Path to I12 JSON file
            resume_from: Record number to resume from (for error recovery)
            progress_callback: Optional callback for progress updates
        """
        logger.info(f"Starting I12 power data import from {file_path}")
        start_time = time.time()

        # Load caches
        session = self.SessionLocal()
        try:
            self.processor.load_caches(session)
        finally:
            session.close()

        # Initialize progress tracking
        total_records = self._count_records(file_path)
        logger.info(f"Found {total_records} total records to process")

        # Skip to resume point if specified
        records_skipped = 0

        try:
            # Process file in chunks
            for chunk_idx, chunk in enumerate(self.reader.read_chunks(file_path)):
                # Skip chunks if resuming
                chunk_start = chunk_idx * self.chunk_size
                if chunk_start + len(chunk) <= resume_from:
                    records_skipped += len(chunk)
                    continue

                # Process records in chunk
                chunk_records = []
                for record_idx, raw_record in enumerate(chunk):
                    global_record_idx = chunk_start + record_idx

                    # Skip individual records if resuming
                    if global_record_idx < resume_from:
                        records_skipped += 1
                        continue

                    try:
                        # Transform and validate
                        transformed = self.transform_data(raw_record)
                        if self.validate_data(transformed):
                            chunk_records.append(transformed)
                        else:
                            self._record_error(
                                global_record_idx, "Validation failed", raw_record
                            )

                    except Exception as e:
                        self._record_error(global_record_idx, str(e), raw_record)

                    self.processed_count += 1

                # Batch insert chunk records
                if chunk_records:
                    try:
                        self._batch_insert(chunk_records)
                        self.imported_count += len(chunk_records)
                    except Exception as e:
                        logger.error(f"Batch insert failed for chunk {chunk_idx}: {e}")
                        self.error_count += len(chunk_records)

                # Update progress
                if progress_callback:
                    percentage = (self.processed_count / total_records) * 100
                    progress_callback(self.processed_count, total_records, percentage)

                # Memory management
                self._check_memory_usage()

                # Log progress
                if chunk_idx % 10 == 0:
                    logger.info(
                        f"Processed {self.processed_count}/{total_records} records "
                        f"({self.imported_count} imported, {self.error_count} errors)"
                    )

        except Exception as e:
            logger.error(f"Critical error during import: {e}")
            raise

        # Final statistics
        end_time = time.time()
        duration = end_time - start_time

        logger.info(
            f"I12 import completed in {duration:.2f} seconds. "
            f"Processed: {self.processed_count}, "
            f"Imported: {self.imported_count}, "
            f"Errors: {self.error_count}, "
            f"Skipped: {records_skipped}"
        )

        if self.errors:
            logger.warning(f"Import completed with {len(self.errors)} errors")

    def _count_records(self, file_path: Path) -> int:
        """Count total records in JSON file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                return len(data) if isinstance(data, list) else 0
        except Exception as e:
            logger.warning(f"Could not count records in {file_path}: {e}")
            return 0

    def _batch_insert(self, records: list[dict[str, Any]]) -> None:
        """Insert a batch of records into the database."""
        session = self.SessionLocal()
        try:
            power_objects = [Power(**record) for record in records]
            session.add_all(power_objects)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database batch insert failed: {e}")
            raise
        finally:
            session.close()

    def _record_error(
        self, record_idx: int, error_msg: str, raw_data: dict[str, Any]
    ) -> None:
        """Record an error for later analysis."""
        self.error_count += 1
        error_info = {
            "record_index": record_idx,
            "error": error_msg,
            "power_name": raw_data.get("Name", "Unknown"),
            "powerset_name": raw_data.get("PowersetName", "Unknown"),
            "timestamp": time.time(),
        }
        self.errors.append(error_info)

        # Log error details
        logger.error(
            f"Record {record_idx} error: {error_msg} "
            f"(Power: {error_info['power_name']}, "
            f"Powerset: {error_info['powerset_name']})"
        )

    def _check_memory_usage(self) -> None:
        """Check memory usage and force garbage collection if needed."""
        try:
            process = psutil.Process()
            memory_bytes = process.memory_info().rss

            if memory_bytes > self.memory_limit_bytes:
                logger.warning(
                    f"Memory usage {memory_bytes / (1024**3):.2f}GB exceeds limit "
                    f"{self.memory_limit_bytes / (1024**3):.2f}GB, forcing garbage collection"
                )
                import gc

                gc.collect()

                # Check memory again after GC
                memory_bytes_after = process.memory_info().rss
                logger.info(
                    f"Memory after GC: {memory_bytes_after / (1024**3):.2f}GB "
                    f"(freed {(memory_bytes - memory_bytes_after) / (1024**3):.2f}GB)"
                )

        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
