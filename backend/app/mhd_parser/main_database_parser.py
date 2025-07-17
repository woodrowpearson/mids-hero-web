"""Parser for complete MHD database files."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import BinaryIO

from .archetype_parser import Archetype, parse_archetype
from .binary_reader import BinaryReader
from .power_parser import Power, parse_power
from .powerset_parser import Powerset, parse_powerset


class DatabaseSection(Enum):
    """Database section markers."""
    ARCHETYPES = "BEGIN:ARCHETYPES"
    POWERSETS = "BEGIN:POWERSETS"
    POWERS = "BEGIN:POWERS"
    SUMMONS = "BEGIN:SUMMONS"


@dataclass
class SummonedEntity:
    """Represents a summoned entity (pet/pseudo-pet) from MHD data."""

    uid: str
    display_name: str
    entity_type: int
    class_name: str
    powerset_full_names: list[str]
    upgrade_power_full_names: list[str]


@dataclass
class MainDatabase:
    """Represents a complete MHD database file."""

    # Header info
    header: str
    version: str
    date: int | datetime
    issue: int
    page_vol: int
    page_vol_text: str

    # Entity collections
    archetypes: list[Archetype]
    powersets: list[Powerset]
    powers: list[Power]
    summons: list[SummonedEntity]


def parse_summoned_entity(stream: BinaryIO) -> SummonedEntity:
    """Parse a SummonedEntity record from a binary stream.
    
    Args:
        stream: Binary stream positioned at the start of a SummonedEntity
        
    Returns:
        Parsed SummonedEntity object
        
    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # Basic fields
        uid = reader.read_string()
        display_name = reader.read_string()
        entity_type = reader.read_int32()
        class_name = reader.read_string()

        # PowersetFullName array
        powerset_count = reader.read_int32()
        powerset_full_names = []
        for _ in range(powerset_count):
            powerset_full_names.append(reader.read_string())

        # UpgradePowerFullName array
        upgrade_count = reader.read_int32()
        upgrade_power_full_names = []
        for _ in range(upgrade_count):
            upgrade_power_full_names.append(reader.read_string())

        return SummonedEntity(
            uid=uid,
            display_name=display_name,
            entity_type=entity_type,
            class_name=class_name,
            powerset_full_names=powerset_full_names,
            upgrade_power_full_names=upgrade_power_full_names
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing SummonedEntity: {str(e)}")


def _parse_version(version_str: str) -> tuple:
    """Parse version string into components.
    
    Args:
        version_str: Version string like "3.0.7.21"
        
    Returns:
        Tuple of (major, minor, patch, build)
    """
    parts = version_str.split('.')
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


def parse_main_database(stream: BinaryIO) -> MainDatabase:
    """Parse a complete MHD database file.
    
    Args:
        stream: Binary stream positioned at the start of the database
        
    Returns:
        Parsed MainDatabase object with all entities
        
    Raises:
        EOFError: If stream ends unexpectedly
        ValueError: If file format is invalid
    """
    reader = BinaryReader(stream)

    try:
        # Parse header
        header = reader.read_string()
        if not header.startswith("Mids"):
            raise ValueError(f"Invalid database header: {header}")

        # Version info
        version = reader.read_string()
        date = _parse_date(reader, version)

        # Issue info
        issue = reader.read_int32()
        page_vol = reader.read_int32()
        page_vol_text = reader.read_string()

        # Initialize collections
        archetypes = []
        powersets = []
        powers = []
        summons = []

        # Parse sections in order
        expected_sections = [
            DatabaseSection.ARCHETYPES,
            DatabaseSection.POWERSETS,
            DatabaseSection.POWERS,
            DatabaseSection.SUMMONS
        ]

        for expected_section in expected_sections:
            # Read section marker
            marker = reader.read_string()
            if marker != expected_section.value:
                raise ValueError(f"Invalid section marker: expected {expected_section.value}, got {marker}")

            # Read count
            count = reader.read_int32()

            # Parse entities based on section
            if expected_section == DatabaseSection.ARCHETYPES:
                for _ in range(count):
                    archetypes.append(parse_archetype(stream))
            elif expected_section == DatabaseSection.POWERSETS:
                for _ in range(count):
                    powersets.append(parse_powerset(stream))
            elif expected_section == DatabaseSection.POWERS:
                for _ in range(count):
                    powers.append(parse_power(stream))
            elif expected_section == DatabaseSection.SUMMONS:
                for _ in range(count):
                    summons.append(parse_summoned_entity(stream))

        return MainDatabase(
            header=header,
            version=version,
            date=date,
            issue=issue,
            page_vol=page_vol,
            page_vol_text=page_vol_text,
            archetypes=archetypes,
            powersets=powersets,
            powers=powers,
            summons=summons
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing database: {str(e)}")
