"""MHD Parser - Mids Hero Designer data file parser.

This package provides parsers for various MHD file formats used by
Mids Hero Designer for City of Heroes character building.
"""

from .main_database_parser import parse_main_database, MainDatabase
from .enhancement_database_parser import parse_enhancement_database, EnhancementDatabase
from .salvage_parser import parse_salvage_database, SalvageDatabase
from .recipe_parser import parse_recipe_database, RecipeDatabase
from .text_mhd_parser import parse_text_mhd, detect_file_format, FileFormat, TextMhdFile
from .json_exporter import MhdJsonExporter
from .errors import MhdParseError, MhdFormatError, MhdVersionError, MhdDataError

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