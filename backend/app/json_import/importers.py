"""JSON import functions for City of Heroes data."""

import logging
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from .exceptions import DatabaseError, JsonImportError
from .transformers import JsonDataTransformer
from .validators import JsonSchemaValidator

logger = logging.getLogger(__name__)


async def import_archetypes(
    session: AsyncSession, data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Import archetype data from JSON.

    Args:
        session: Database session
        data: List of archetype records

    Returns:
        Import statistics

    Raises:
        JsonImportError: If import fails
    """
    validator = JsonSchemaValidator()
    transformer = JsonDataTransformer(session)

    stats = {"total": len(data), "imported": 0, "failed": 0, "errors": []}

    try:
        # Validate all records first
        validated_records = validator.validate_bulk(data, "archetype")

        # Transform and import each record
        for idx, record in enumerate(validated_records):
            try:
                archetype = await transformer.transform_archetype(record.dict())
                session.add(archetype)
                await session.flush()

                # Store mapping for reference resolution
                transformer.archetype_map[record.id] = archetype.id
                stats["imported"] += 1

            except Exception as e:
                logger.error(f"Failed to import archetype {idx}: {e}")
                stats["failed"] += 1
                stats["errors"].append({"index": idx, "error": str(e)})

        await session.commit()
        logger.info(
            f"Imported {stats['imported']}/{stats['total']} archetypes "
            f"({stats['failed']} failed)"
        )

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Archetype import failed: {e}")

    return stats


async def import_powersets(
    session: AsyncSession, data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Import powerset data from JSON.

    Args:
        session: Database session
        data: List of powerset records

    Returns:
        Import statistics

    Raises:
        JsonImportError: If import fails
    """
    validator = JsonSchemaValidator()
    transformer = JsonDataTransformer(session)

    stats = {"total": len(data), "imported": 0, "failed": 0, "errors": []}

    try:
        # Validate all records first
        validated_records = validator.validate_bulk(data, "powerset")

        # Transform and import each record
        for idx, record in enumerate(validated_records):
            try:
                powerset = await transformer.transform_powerset(record.dict())
                session.add(powerset)
                await session.flush()

                # Store mapping for reference resolution
                transformer.powerset_map[record.id] = powerset.id
                stats["imported"] += 1

            except Exception as e:
                logger.error(f"Failed to import powerset {idx}: {e}")
                stats["failed"] += 1
                stats["errors"].append({"index": idx, "error": str(e)})

        await session.commit()
        logger.info(
            f"Imported {stats['imported']}/{stats['total']} powersets "
            f"({stats['failed']} failed)"
        )

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Powerset import failed: {e}")

    return stats


async def import_powers(
    session: AsyncSession, data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Import power data from JSON.

    Args:
        session: Database session
        data: List of power records

    Returns:
        Import statistics

    Raises:
        JsonImportError: If import fails
    """
    validator = JsonSchemaValidator()
    transformer = JsonDataTransformer(session)

    stats = {"total": len(data), "imported": 0, "failed": 0, "errors": []}

    # For large datasets, process in batches
    batch_size = 1000

    try:
        for batch_start in range(0, len(data), batch_size):
            batch_end = min(batch_start + batch_size, len(data))
            batch_data = data[batch_start:batch_end]

            # Validate batch
            validated_records = validator.validate_bulk(batch_data, "power")

            # Transform and import each record in batch
            for idx, record in enumerate(validated_records):
                actual_idx = batch_start + idx
                try:
                    power = await transformer.transform_power(record.dict())
                    session.add(power)
                    stats["imported"] += 1

                    # Flush periodically to avoid memory issues
                    if stats["imported"] % 100 == 0:
                        await session.flush()

                except Exception as e:
                    logger.error(f"Failed to import power {actual_idx}: {e}")
                    stats["failed"] += 1
                    stats["errors"].append({"index": actual_idx, "error": str(e)})

            # Commit after each batch
            await session.commit()
            logger.info(
                f"Processed batch {batch_start}-{batch_end}: "
                f"{stats['imported']} imported, {stats['failed']} failed"
            )

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Power import failed: {e}")

    logger.info(
        f"Total: Imported {stats['imported']}/{stats['total']} powers "
        f"({stats['failed']} failed)"
    )
    return stats


async def import_enhancements(
    session: AsyncSession, data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Import enhancement data from JSON.

    Args:
        session: Database session
        data: List of enhancement records

    Returns:
        Import statistics

    Raises:
        JsonImportError: If import fails
    """
    validator = JsonSchemaValidator()
    transformer = JsonDataTransformer(session)

    stats = {"total": len(data), "imported": 0, "failed": 0, "errors": []}

    try:
        # Validate all records first
        validated_records = validator.validate_bulk(data, "enhancement")

        # Transform and import each record
        for idx, record in enumerate(validated_records):
            try:
                enhancement = await transformer.transform_enhancement(record.dict())
                session.add(enhancement)
                await session.flush()

                # Store mapping for reference resolution
                transformer.enhancement_map[record.id] = enhancement.id
                stats["imported"] += 1

            except Exception as e:
                logger.error(f"Failed to import enhancement {idx}: {e}")
                stats["failed"] += 1
                stats["errors"].append({"index": idx, "error": str(e)})

        await session.commit()
        logger.info(
            f"Imported {stats['imported']}/{stats['total']} enhancements "
            f"({stats['failed']} failed)"
        )

    except Exception as e:
        await session.rollback()
        raise DatabaseError(f"Enhancement import failed: {e}")

    return stats


async def import_from_directory(directory: Path) -> Dict[str, Any]:
    """Import all JSON data files from a directory.

    Expected directory structure:
    - archetypes.json or archetypes/
    - powersets.json or powersets/
    - powers.json or powers/
    - enhancements.json or enhancements/

    Args:
        directory: Path to the directory containing JSON files

    Returns:
        Import statistics for all data types

    Raises:
        JsonImportError: If import fails
    """
    if not directory.exists():
        raise JsonImportError(f"Directory not found: {directory}")

    stats = {}

    async for session in get_async_session():
        try:
            # Import in dependency order
            # 1. Archetypes (no dependencies)
            archetype_file = directory / "archetypes.json"
            if archetype_file.exists():
                import json

                with open(archetype_file, "r", encoding="utf-8") as f:
                    archetype_data = json.load(f)
                stats["archetypes"] = await import_archetypes(session, archetype_data)

            # 2. Powersets (depends on archetypes)
            powerset_file = directory / "powersets.json"
            if powerset_file.exists():
                import json

                with open(powerset_file, "r", encoding="utf-8") as f:
                    powerset_data = json.load(f)
                stats["powersets"] = await import_powersets(session, powerset_data)

            # 3. Powers (depends on powersets)
            power_file = directory / "powers.json"
            if power_file.exists():
                import json

                with open(power_file, "r", encoding="utf-8") as f:
                    power_data = json.load(f)
                stats["powers"] = await import_powers(session, power_data)

            # 4. Enhancements (independent)
            enhancement_file = directory / "enhancements.json"
            if enhancement_file.exists():
                import json

                with open(enhancement_file, "r", encoding="utf-8") as f:
                    enhancement_data = json.load(f)
                stats["enhancements"] = await import_enhancements(
                    session, enhancement_data
                )

        finally:
            await session.close()

    return stats