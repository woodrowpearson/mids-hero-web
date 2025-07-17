# DataExporter - MidsReborn MHD to JSON Converter

This tool uses the MidsReborn parser to export City of Heroes MHD data files to JSON format for import into the Mids Hero Web database.

## Overview

The DataExporter leverages the proven MidsReborn C# parser to read binary MHD files and export them as JSON. This approach was chosen over implementing a custom parser due to:

1. **Reliability**: MidsReborn's parser is battle-tested and handles all edge cases
2. **Completeness**: Supports all data types (powers, enhancements, recipes, salvage)
3. **Maintainability**: Updates to MHD format only require updating MidsReborn reference

## Prerequisites

- .NET 8.0 SDK
- MHD data files from City of Heroes (Homecoming)
- Access to MidsReborn source code (included in external/)

## Building

```bash
cd DataExporter
dotnet build
```

## Usage

```bash
dotnet run -- <mhd-data-folder> <output-folder>

# Example:
dotnet run -- ~/code/mids-hero-web/data/Homecoming_2025-7-1111 ~/code/mids-hero-web/data/exported-json
```

## Required MHD Files

The data folder should contain:
- `I12.mhd` - Main database (archetypes, powersets, powers)
- `EnhDB.mhd` - Enhancement database
- `Recipe.mhd` - Crafting recipes
- `Salvage.mhd` - Salvage items

## Output Files

The exporter creates the following JSON files:
- `archetypes.json` - Character classes
- `powersets.json` - Power sets for each archetype
- `powers.json` - Individual powers
- `enhancements.json` - Enhancement items
- `enhancement_sets.json` - Named enhancement sets
- `set_bonuses.json` - Set bonus effects
- `recipes.json` - Crafting recipes
- `salvage.json` - Salvage items
- `export_report.json` - Export statistics and metadata

## JSON Schema

### Archetypes
```json
{
  "id": 1,
  "name": "Class_Blaster",
  "display_name": "Blaster",
  "description": "The Blaster is an offensive juggernaut...",
  "primary_group": "Blaster_Ranged",
  "secondary_group": "Blaster_Support",
  "hit_points_base": 1205,
  "hit_points_max": 2409
}
```

### Powers
```json
{
  "id": 1,
  "name": "Fire_Blast",
  "display_name": "Fire Blast",
  "description": "Hurls a blast of fire...",
  "powerset_id": 1,
  "level_available": 1,
  "power_type": "click",
  "target_type": "enemy",
  "accuracy": 1.0,
  "damage_scale": 1.0,
  "endurance_cost": 5.2,
  "recharge_time": 4.0,
  "activation_time": 1.67,
  "range_feet": 80,
  "max_targets": 1
}
```

## Technical Details

The DataExporter:
1. References MidsReborn.csproj to access parsing logic
2. Uses `DatabaseAPI.LoadMainDatabase()` and related methods
3. Maps MidsReborn's data structures to our database schema
4. Handles null values and invalid references gracefully
5. Creates detailed export reports

## Troubleshooting

### "MidsReborn.csproj not found"
Ensure you have the MidsReborn source in `external/MidsReborn/`

### "Failed to load main database"
Check that I12.mhd exists and is a valid MidsReborn database file

### Windows/Linux compatibility
MidsReborn targets Windows, but the core parsing logic should work cross-platform

## Next Steps

After exporting to JSON:
1. Run the Python import script to load data into PostgreSQL
2. Verify data integrity with test queries
3. Start the API server to access the data

See `/backend/scripts/import_mhd_json_to_db.py` for the import process.