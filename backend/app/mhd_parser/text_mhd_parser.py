"""Parser for text-based MHD files (Origins.mhd, NLevels.mhd, etc.)."""

from dataclasses import dataclass
from enum import Enum
from typing import BinaryIO


class FileFormat(Enum):
    """File format enumeration."""
    BINARY = "binary"
    TEXT_WITH_VERSION = "text_with_version"
    TEXT_TSV = "text_tsv"


@dataclass
class TextMhdFile:
    """Represents a parsed text-based MHD file."""

    version: str | None  # Version if present (e.g., "Version 1.5.0")
    headers: list[str]  # Column headers if tab-delimited
    data: list[list[str]]  # Data rows (each row is a list of values)


def detect_file_format(stream: BinaryIO) -> FileFormat:
    """Detect whether a file is binary or text format.

    Args:
        stream: Binary stream to analyze

    Returns:
        FileFormat enum indicating the detected format

    Raises:
        EOFError: If stream is empty
    """
    # Save current position
    pos = stream.tell()

    try:
        # Read first few bytes
        header = stream.read(20)
        if not header:
            raise EOFError("Empty file")

        # Check for binary format (7-bit encoded string)
        # Binary files typically start with a small byte (string length)
        # followed by readable text
        if header[0] < 0x20 and header[0] > 0:
            # Likely a string length byte
            if all(0x20 <= b <= 0x7E or b in (0x09, 0x0A, 0x0D) for b in header[1:]):
                return FileFormat.BINARY

        # Check for text format
        try:
            text = header.decode('utf-8', errors='strict')

            # Check for version header
            if text.startswith("Version"):
                return FileFormat.TEXT_WITH_VERSION

            # Check for tab delimiter (TSV format)
            if '\t' in text:
                return FileFormat.TEXT_TSV

            # Default to version format for plain text
            return FileFormat.TEXT_WITH_VERSION

        except UnicodeDecodeError:
            # Not valid UTF-8, assume binary
            return FileFormat.BINARY

    finally:
        # Restore position
        stream.seek(pos)


def parse_text_mhd(stream: BinaryIO) -> TextMhdFile:
    """Parse a text-based MHD file.

    Args:
        stream: Binary stream containing text data

    Returns:
        Parsed TextMhdFile object

    Raises:
        ValueError: If file format cannot be determined
    """
    # Read entire file as text
    content = stream.read().decode('utf-8', errors='replace')
    lines = content.strip().split('\n')

    if not lines:
        return TextMhdFile(version=None, headers=[], data=[])

    version = None
    headers = []
    data = []
    start_index = 0

    # Check for version header
    if lines[0].startswith("Version"):
        version = lines[0].replace("Version", "").strip()
        start_index = 1

    # Process remaining lines
    for i, line in enumerate(lines[start_index:], start_index):
        # Skip empty lines
        if not line.strip():
            continue

        # Check if this is a tab-delimited file
        if '\t' in line:
            # First line with tabs becomes headers
            if not headers and i == start_index:
                headers = line.split('\t')
            else:
                data.append(line.split('\t'))
        else:
            # Single column data
            data.append([line])

    return TextMhdFile(
        version=version,
        headers=headers,
        data=data
    )
