"""MHD Parser - Mids Hero Designer data file parser.

This package provides parsers for various MHD file formats used by
Mids Hero Designer for City of Heroes character building.
"""

from .enhancement_database_parser import EnhancementDatabase, parse_enhancement_database
from .errors import MhdDataError, MhdFormatError, MhdParseError, MhdVersionError
from .json_exporter import MhdJsonExporter
from .main_database_parser import MainDatabase, parse_main_database
from .recipe_parser import RecipeDatabase, parse_recipe_database
from .salvage_parser import SalvageDatabase, parse_salvage_database
from .text_mhd_parser import FileFormat, TextMhdFile, detect_file_format, parse_text_mhd

__version__ = "1.0.0"

__all__ = [
    # Main parsers
    "parse_main_database",
    "parse_enhancement_database",
    "parse_salvage_database",
    "parse_recipe_database",
    "parse_text_mhd",
    "detect_file_format",

    # Data classes
    "MainDatabase",
    "EnhancementDatabase",
    "SalvageDatabase",
    "RecipeDatabase",
    "TextMhdFile",
    "FileFormat",

    # Utilities
    "MhdJsonExporter",

    # Errors
    "MhdParseError",
    "MhdFormatError",
    "MhdVersionError",
    "MhdDataError",
]
