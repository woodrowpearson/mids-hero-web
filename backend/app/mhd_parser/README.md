# MHD Parser

Cross-platform Python parser for MHD (Mids Hero Designer) binary files used by City of Heroes.

## Overview

This parser can read the binary MHD files created by MidsReborn without requiring Windows or .NET dependencies. It's designed to be compatible with the MidsReborn file format while being fully cross-platform.

## Features

- Binary reader compatible with .NET BinaryReader format
- Support for 7-bit encoded integers used in .NET strings
- Data classes that mirror MidsReborn's structure
- File type detection based on headers
- Test-driven development with comprehensive test coverage

## Supported File Types

- `I12.mhd` - Main powers database (partial support)
- `EnhDB.mhd` - Enhancement database (planned)
- `Salvage.mhd` - Salvage database (planned)
- `Recipe.mhd` - Recipe database (planned)
- Additional file types planned

## Usage

```python
from app.mhd_parser import MHDParser

# Parse a file
parser = MHDParser()
result = parser.parse_file("path/to/I12.mhd")

if result:
    print(f"File type: {result['file_type']}")
    print(f"Version: {result['data']['version']}")
    
    # Access archetypes
    for archetype in result['data']['archetypes']:
        print(f"- {archetype.display_name} ({archetype.class_name})")
```

## Architecture

### Binary Reader

The `MHDBinaryReader` class provides methods to read .NET binary format:
- Strings with 7-bit encoded length prefixes
- Little-endian integers and floats
- Boolean values
- Arrays with count prefixes

### Data Classes

- `Archetype` - Character archetype data (Blaster, Tanker, etc.)
- Additional classes to be implemented:
  - `Power` - Individual power data
  - `Powerset` - Power set definitions
  - `Enhancement` - Enhancement items
  - `EnhancementSet` - Enhancement set bonuses
  - `Recipe` - Crafting recipes
  - `Salvage` - Salvage items

### Parser

The `MHDParser` class:
- Detects file type from header
- Routes to appropriate parsing method
- Returns structured data ready for database import

## Development

### Running Tests

```bash
# Run all MHD parser tests
uv run pytest tests/mhd_parser/ -v

# Run specific test file
uv run pytest tests/mhd_parser/test_parser.py -v
```

### Adding New Data Classes

1. Study the C# class in MidsReborn source
2. Create test first in `tests/mhd_parser/`
3. Implement Python equivalent in `data_classes.py`
4. Ensure binary compatibility with read/write methods

## Next Steps

1. Implement remaining data classes (Power, Powerset, Enhancement, etc.)
2. Complete parsing for all sections of main database
3. Add support for enhancement, salvage, and recipe databases
4. Create import scripts to load data into PostgreSQL
5. Test with actual MHD files from City of Heroes

## Technical Notes

### Binary Format

MHD files use .NET's BinaryWriter format:
- Strings: 7-bit encoded length prefix + UTF-8 bytes
- Numbers: Little-endian byte order
- Arrays: Count (as int32) followed by elements
- Booleans: Single byte (0 = false, non-zero = true)

### Compatibility

This parser aims for 100% compatibility with MidsReborn's file format. Any deviations should be considered bugs and reported.