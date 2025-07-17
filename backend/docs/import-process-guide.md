# MHD Data Import Process Guide

## Overview

This guide documents the process for importing City of Heroes game data from MHD (Mids Hero Designer) files into the Mids Hero Web database.

## Prerequisites

- PostgreSQL database running
- Python environment with dependencies installed
- MHD data files (located in `/data/Homecoming_2025-7-1111/`)
- Converted JSON files (see conversion process below)

## Current Status

### ✅ Completed
1. **Database Schema**: All tables and relationships defined
2. **Import Scripts**: Python scripts ready for data import
3. **Parser Framework**: MHD parser implementation with tests
4. **Automation Script**: `update_game_data.py` for future updates

### 🚧 Blocked
- **Binary Format**: Homecoming MHD files use a custom binary format
- **Data Conversion**: Need to convert MHD to JSON/SQL format

## Import Process

### Step 1: Convert MHD to JSON

#### Option A: Use DataExporter (Partial)
```bash
cd DataExporter
dotnet run /path/to/mhd/files /path/to/output
```

This will:
- Copy existing JSON files (AttribMod.json, TypeGrades.json)
- Create partial parse of I12.mhd
- Generate hex dump for analysis

#### Option B: Use Mids Reborn (Recommended)
1. Build Mids Reborn from source
2. Add JSON export functionality
3. Load MHD files and export to JSON

#### Option C: Request from Community
Contact Mids Reborn team for data in standard format

### Step 2: Import JSON to Database

Once you have JSON files:

```bash
cd backend

# Dry run first
uv run python scripts/import_mhd_data.py --dry-run

# Actual import
uv run python scripts/import_mhd_data.py --clean

# Import specific JSON files
uv run python scripts/import_json_data.py archetypes.json
```

### Step 3: Validate Import

```bash
# Check counts
uv run python scripts/validate_import.py

# Run tests
uv run pytest tests/test_import_validation.py
```

## Automated Updates

For future game updates:

```bash
# Automated update with backup
uv run python scripts/update_game_data.py \
  --data-dir /path/to/new/data \
  --backup-dir ./backups

# Force update without version check
uv run python scripts/update_game_data.py \
  --data-dir /path/to/new/data \
  --force
```

## File Formats

### MHD Binary Format (Homecoming)
- Custom binary format, not standard .NET serialization
- Starts with length-prefixed strings
- Contains: Archetypes, Powersets, Powers, Enhancements

### Expected JSON Structure
```json
{
  "archetypes": [{
    "name": "Class_Blaster",
    "displayName": "Blaster",
    "description": "...",
    "hitPointsBase": 1000,
    "hitPointsMax": 1606,
    "primaryGroup": "Ranged_Damage",
    "secondaryGroup": "Ranged_Support"
  }],
  "powersets": [{
    "name": "Fire_Blast",
    "displayName": "Fire Blast",
    "archetypeId": 1,
    "setType": "primary"
  }],
  "powers": [{
    "name": "Flares",
    "displayName": "Flares",
    "powersetId": 1,
    "levelAvailable": 1
  }]
}
```

## Database Schema

Key tables:
- `archetypes` - Character classes
- `powersets` - Power collections
- `powers` - Individual powers
- `enhancements` - Power enhancements
- `enhancement_sets` - Enhancement collections
- `set_bonuses` - Bonuses from sets

## Troubleshooting

### Binary Format Issues
If MHD parsing fails:
1. Check file headers match expected format
2. Verify file isn't corrupted
3. Try different parser options

### Import Failures
1. Check database connectivity
2. Verify schema migrations are applied
3. Check for duplicate data
4. Review import logs

### Data Validation
1. Compare counts with known values
2. Test sample builds
3. Verify relationships intact

## Next Steps

1. **Immediate**: Get MHD data in parseable format
2. **Short-term**: Complete data import
3. **Long-term**: Automate updates from game patches

## Resources

- [Mids Reborn GitHub](https://github.com/LoadedCamel/MidsReborn)
- [City of Heroes Forums](https://forums.homecomingservers.com/)
- [Database Schema Docs](./database-schema.md)
- [API Documentation](./api-docs.md)