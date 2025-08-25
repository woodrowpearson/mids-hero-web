"""Parser for complete Enhancement database files (EnhDB.mhd)."""

from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO

from .binary_reader import BinaryReader
from .enhancement_parser import (
    Enhancement,
    EnhancementSet,
    parse_enhancement,
    parse_enhancement_set,
)


@dataclass
class EnhancementDatabase:
    """Represents a complete Enhancement database file."""

    # Header info
    header: str
    version: str
    date: int | datetime

    # Entity collections
    enhancements: list[Enhancement]
    enhancement_sets: list[EnhancementSet]


def _parse_version(version_str: str) -> tuple:
    """Parse version string into components.

    Args:
        version_str: Version string like "3.0.7.21"

    Returns:
        Tuple of (major, minor, patch, build)
    """
    parts = version_str.split(".")
    if len(parts) != 4:
        return (0, 0, 0, 0)

    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return (0, 0, 0, 0)


def _parse_date(reader: BinaryReader, version_str: str) -> int | datetime:
    """Parse date based on version.

    For versions >= 3.0, date is stored as Int64 (.NET ticks).
    For older versions, date is stored as Int32 (YYYYMMDD).

    Args:
        reader: Binary reader
        version_str: Version string to determine format

    Returns:
        Either int (YYYYMMDD) or datetime object
    """
    major, minor, _, _ = _parse_version(version_str)

    if major >= 3:
        # Read as Int64 (.NET ticks)
        ticks = reader.read_int64()
        # Convert .NET ticks to datetime
        # .NET epoch is January 1, 0001
        # Python datetime epoch is January 1, 1970
        # .NET ticks are 100-nanosecond intervals
        try:
            # Calculate seconds since Unix epoch
            dot_net_epoch_offset = 621355968000000000  # Ticks between 0001 and 1970
            unix_ticks = ticks - dot_net_epoch_offset
            unix_seconds = unix_ticks / 10000000  # Convert to seconds
            return datetime.fromtimestamp(unix_seconds)
        except (ValueError, OverflowError):
            # If conversion fails, return raw ticks
            return ticks
    else:
        # Read as Int32 (YYYYMMDD format)
        return reader.read_int32()


def parse_enhancement_database(stream: BinaryIO) -> EnhancementDatabase:
    """Parse a complete Enhancement database file.

    Args:
        stream: Binary stream positioned at the start of the database

    Returns:
        Parsed EnhancementDatabase object with all entities

    Raises:
        EOFError: If stream ends unexpectedly
        ValueError: If file format is invalid
    """
    reader = BinaryReader(stream)

    try:
        # Parse header
        header = reader.read_string()
        if "Enhancement" not in header:
            raise ValueError(f"Invalid enhancement database header: {header}")

        # Version info
        version = reader.read_string()
        date = _parse_date(reader, version)

        # Read enhancement count
        enhancement_count = reader.read_int32()
        enhancements = []
        for _ in range(enhancement_count):
            enhancements.append(parse_enhancement(stream))

        # Read enhancement set count
        set_count = reader.read_int32()
        enhancement_sets = []
        for _ in range(set_count):
            enhancement_sets.append(parse_enhancement_set(stream))

        return EnhancementDatabase(
            header=header,
            version=version,
            date=date,
            enhancements=enhancements,
            enhancement_sets=enhancement_sets,
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing enhancement database: {str(e)}")
