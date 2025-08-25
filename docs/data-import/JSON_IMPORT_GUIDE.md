# JSON Data Import Guide

## Overview

As part of Epic 2.5.5 cleanup, the project has transitioned from MHD binary parsing to JSON-based data import. This guide covers the new JSON import workflow.

## Migration Status

- ✅ **MHD Parser**: Archived to `/backend/archive/mhd_parser/`
- ✅ **JSON Import Module**: Created at `/backend/app/json_import/`
- ✅ **Existing I12 Parser**: Retained at `/backend/app/data_import/`
- ✅ **C# DataExporter**: Kept for MHD→JSON conversion

## JSON Data Sources

The project uses JSON data from two primary sources:

1. **City of Data**: `/external/city_of_data/raw_data_homecoming-20250617_6916/`
   - Pre-exported JSON from Homecoming server
   - Contains archetypes, powers, enhancements, etc.

2. **DataExporter Output**: For converting MHD files
   - Use C# DataExporter to convert MHD to JSON
   - Located at `/DataExporter/`

## Import Workflow

### Method 1: Import from City of Data (Recommended)

```bash
# Import all JSON data
python backend/scripts/import_i12_data.py external/city_of_data/raw_data_homecoming-20250617_6916/powers.json

# Or use justfile command
just i12-import external/city_of_data/raw_data_homecoming-20250617_6916/powers.json
```

### Method 2: Using New JSON Import Module

```bash
# Import all data from directory
python -m app.json_import.cli import-all external/city_of_data/raw_data_homecoming-20250617_6916/

# Import specific file
python -m app.json_import.cli import-file --type archetype archetypes.json

# Validate JSON before import
python -m app.json_import.cli validate --schema power powers.json
```

### Method 3: Convert MHD to JSON (Legacy Support)

If you have MHD files that need conversion:

```bash
# 1. Convert using C# DataExporter
cd DataExporter
dotnet run -- ~/path/to/mhd/data ~/output/json/directory

# 2. Import the converted JSON
python backend/scripts/import_i12_data.py ~/output/json/directory/powers.json
```

## JSON Schema Validation

The new JSON import module includes schema validation for all data types:

### Power Schema
```json
{
  "id": 1,
  "name": "fire_blast",
  "display_name": "Fire Blast",
  "description": "Launches a blast of fire",
  "powerset_id": 10,
  "power_type": "Ranged",
  "accuracy": 1.0,
  "damage": 62.56,
  "endurance_cost": 5.2,
  "recharge_time": 4.0,
  "activation_time": 1.67,
  "range": 80,
  "max_targets": 1
}
```

### Archetype Schema
```json
{
  "id": 1,
  "name": "blaster",
  "display_name": "Blaster",
  "description": "Ranged damage dealer",
  "hit_points": 1204.8,
  "max_hit_points": 1606.4,
  "primary_powersets": [1, 2, 3],
  "secondary_powersets": [4, 5, 6]
}
```

## API Endpoints

The API endpoints remain unchanged and work with the imported JSON data:

- `GET /api/archetypes` - List all archetypes
- `GET /api/powers/{id}` - Get specific power
- `GET /api/powersets/{id}` - Get powerset details
- `GET /api/enhancements` - List enhancements

## Deprecated Commands

The following commands are no longer functional:

- ❌ `python -m app.commands.import_mhd` - Returns deprecation notice
- ❌ Any direct MHD binary parsing operations

## Troubleshooting

### Import Failures

If import fails, check:
1. JSON file validity: `python -m json.tool yourfile.json`
2. Schema compliance: Use the validate command
3. Database connectivity: Ensure PostgreSQL is running
4. Memory for large files: Use batch processing

### Performance Tips

For large datasets (360K+ powers):
- Use the I12StreamingParser for memory efficiency
- Process in batches of 1000 records
- Enable Redis caching if available
- Use database indexes for foreign keys

## Development

### Adding New Data Types

1. Create schema in `validators.py`:
```python
class NewTypeSchema(BaseModel):
    id: int
    name: str
    # Add fields
```

2. Create transformer in `transformers.py`:
```python
async def transform_new_type(self, data: Dict[str, Any]) -> NewType:
    # Transform logic
```

3. Create importer in `importers.py`:
```python
async def import_new_types(session: AsyncSession, data: List[Dict[str, Any]]):
    # Import logic
```

## Related Documentation

- [I12 Streaming Parser](./i12_streaming_parser.md) - For large dataset imports
- [Database Schema](../database/schema.md) - Database structure
- [API Documentation](../api/README.md) - API endpoints

## Support

For issues or questions:
- Check Epic 2.5.5 issues (#256-#272)
- Review `/archive/mhd-legacy/README.md` for legacy information
- Contact the development team

---

*Last Updated: 2025-08-24 - Epic 2.5.5 Task 2.5.5.2 Completion*