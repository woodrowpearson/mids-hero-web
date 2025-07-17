"""Parser for Salvage records and database from MHD files."""

from dataclasses import dataclass
from enum import IntEnum
from typing import BinaryIO

from .binary_reader import BinaryReader


class SalvageRarity(IntEnum):
    """Salvage rarity enumeration."""

    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    VERY_RARE = 3


class SalvageType(IntEnum):
    """Salvage type enumeration."""

    COMPONENT = 0
    CATALYST = 1
    SPECIAL = 2


@dataclass
class Salvage:
    """Represents a Salvage record from MHD data."""

    internal_name: str
    display_name: str
    rarity: SalvageRarity
    salvage_type: SalvageType
    description: str


@dataclass
class SalvageDatabase:
    """Represents a complete Salvage database file."""

    header: str
    version: str
    salvage_items: list[Salvage]


def parse_salvage(stream: BinaryIO) -> Salvage:
    """Parse a Salvage record from a binary stream.

    Args:
        stream: Binary stream positioned at the start of a Salvage record

    Returns:
        Parsed Salvage object

    Raises:
        EOFError: If stream ends while reading
    """
    reader = BinaryReader(stream)

    try:
        # Read fields in order
        internal_name = reader.read_string()
        display_name = reader.read_string()
        rarity = SalvageRarity(reader.read_int32())
        salvage_type = SalvageType(reader.read_int32())
        description = reader.read_string()

        return Salvage(
            internal_name=internal_name,
            display_name=display_name,
            rarity=rarity,
            salvage_type=salvage_type,
            description=description,
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing Salvage: {str(e)}")


def parse_salvage_database(stream: BinaryIO) -> SalvageDatabase:
    """Parse a complete Salvage database file.

    Args:
        stream: Binary stream positioned at the start of the database

    Returns:
        Parsed SalvageDatabase object with all items

    Raises:
        EOFError: If stream ends unexpectedly
        ValueError: If file format is invalid
    """
    reader = BinaryReader(stream)

    try:
        # Parse header
        header = reader.read_string()
        if "Salvage" not in header:
            raise ValueError(f"Invalid salvage database header: {header}")

        # Version
        version = reader.read_string()

        # Read salvage count
        salvage_count = reader.read_int32()
        salvage_items = []

        for _ in range(salvage_count):
            salvage_items.append(parse_salvage(stream))

        return SalvageDatabase(
            header=header, version=version, salvage_items=salvage_items
        )

    except EOFError as e:
        raise EOFError(f"Unexpected EOF while parsing salvage database: {str(e)}")
