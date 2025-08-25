"""Custom exceptions for JSON import module."""


class JsonImportError(Exception):
    """Base exception for JSON import errors."""

    pass


class ValidationError(JsonImportError):
    """Raised when JSON data fails validation."""

    def __init__(self, message: str, errors: list | None = None):
        super().__init__(message)
        self.errors = errors or []


class TransformationError(JsonImportError):
    """Raised when data transformation fails."""

    pass


class DatabaseError(JsonImportError):
    """Raised when database operations fail during import."""

    pass