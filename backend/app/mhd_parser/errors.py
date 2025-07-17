"""Enhanced error handling for MHD parser with context tracking."""



class MhdParseError(Exception):
    """Base exception for MHD parsing errors."""

    def __init__(self, message: str, position: int | None = None,
                 context: list[str] | None = None):
        """Initialize parse error with context.

        Args:
            message: Error description
            position: Byte position in file where error occurred
            context: Stack of what was being parsed
        """
        self.position = position
        self.context = context or []

        # Build detailed error message
        error_parts = []

        if position is not None:
            error_parts.append(f"Error at position {position}")

        if context:
            error_parts.append(f"While parsing: {' > '.join(context)}")

        error_parts.append(message)

        super().__init__(' | '.join(error_parts))


class MhdFormatError(MhdParseError):
    """Raised when file format is invalid or unexpected."""
    pass


class MhdVersionError(MhdParseError):
    """Raised when file version is unsupported."""
    pass


class MhdDataError(MhdParseError):
    """Raised when data values are invalid."""
    pass


def format_parse_context(entity_type: str, entity_name: str | None = None,
                        field: str | None = None) -> str:
    """Format a parsing context string.

    Args:
        entity_type: Type of entity being parsed (e.g., "Archetype")
        entity_name: Name of the entity if known
        field: Current field being parsed

    Returns:
        Formatted context string
    """
    parts = [entity_type]

    if entity_name:
        parts.append(f"[{entity_name}]")

    if field:
        parts.append(f".{field}")

    return ''.join(parts)
