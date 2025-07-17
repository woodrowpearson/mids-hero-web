# MHD Data Import Status

## Overview

The MHD (Mids Hero Designer) data files have been located in `/data/Homecoming_2025-7-1111/`. These files contain the complete game database for City of Heroes/Homecoming.

## File Analysis

### Binary MHD Files
The following binary MHD files use a proprietary format:
- `I12.mhd` - Main database (3.3MB) containing archetypes, powersets, powers
- `EnhDB.mhd` - Enhancement database
- `SData.mhd` - Set data
- `Recipe.mhd` - Recipe data
- `Salvage.mhd` - Salvage data
- `Maths.mhd` - Mathematical formulas
- Others...

### Text MHD Files
Some files use a tab-delimited text format:
- `Origins.mhd` - Origin graphics mapping
- `bbcode.mhd` - BBCode templates

### JSON Files
- `AttribMod.json` - Attribute modifiers
- `TypeGrades.json` - Enhancement types and grades

## Current Status

1. **MHD Parser Implementation**: ✅ Complete
   - Created comprehensive parser structure with TDD
   - Supports both binary and text formats
   - Includes JSON export functionality

2. **Binary Format Challenge**: 
   - The Homecoming MHD files use a custom binary format that differs from standard .NET BinaryWriter
   - Initial attempts to parse reveal non-standard string encoding
   - Header: "Mids Reborn Powers Database" followed by version "2025.7.1111"

3. **Import Script**: ✅ Created
   - `scripts/import_mhd_data.py` ready to import parsed data
   - Handles dependency ordering and ID mapping
   - Supports dry-run mode for testing

## Next Steps

To complete the data import, we need one of the following:

### Option 1: Reverse Engineer Binary Format
- Analyze the binary structure of I12.mhd
- Update the parser to handle the custom encoding
- This is complex and time-consuming

### Option 2: Use Original C# Loader
- The original Mids Reborn application can read these files
- Create a C# console app using the original loader DLLs
- Export to JSON for Python import

### Option 3: Request JSON Export
- Contact the Homecoming/Mids Reborn team
- Request data in JSON or other standard format
- Most straightforward solution

## Recommendation

Given the project timeline and complexity, Option 2 or 3 would be most efficient. The infrastructure for importing data is ready - we just need the data in a parseable format.

## Files Ready for Import

Once we can parse the MHD files, the following will be imported:
- Archetypes (14 total including Blaster, Controller, etc.)
- Powersets (hundreds)
- Powers (thousands)
- Enhancements and Sets
- Recipes and Salvage

The database schema and import scripts are fully prepared to handle this data.