"""JSON Import Module for City of Heroes Data.

This module replaces the deprecated MHD binary parser with JSON-based import.
It provides validation, transformation, and import capabilities for game data.

Epic 2.5.5: Created as part of MHD Dependencies Refactoring
"""

from .exceptions import JsonImportError, ValidationError
from .importers import (
    import_archetypes,
    import_enhancements,
    import_powers,
    import_powersets,
)
from .transformers import JsonDataTransformer
from .validators import JsonSchemaValidator

__all__ = [
    # Main import functions
    "import_archetypes",
    "import_powers",
    "import_powersets",
    "import_enhancements",
    # Utility classes
    "JsonSchemaValidator",
    "JsonDataTransformer",
    # Exceptions
    "JsonImportError",
    "ValidationError",
]