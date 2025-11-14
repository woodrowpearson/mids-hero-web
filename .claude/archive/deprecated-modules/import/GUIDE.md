# Import Module Guide

## Overview
The import system processes JSON game data from the filtered City of Data source located at `filtered_data/`.

## Architecture
- **JSON manifest-driven**: All imports reference `filtered_data/manifest.json`
- **Batch processing**: Imports process data in configurable batch sizes
- **Progress tracking**: Real-time progress with resume capability
- **Validation**: Comprehensive schema validation before database insert

## Key Components

### JSONDataImporter
Primary class for importing JSON data.

Location: `backend/app/data_import/json_importer.py`

Methods:
- `import_archetypes(manifest_path)`: Import character archetypes
- `import_powersets(manifest_path)`: Import power sets
- `import_powers(manifest_path)`: Import individual powers
- `import_enhancements(manifest_path)`: Import enhancement sets

### Data Sources

Filtered data location: `filtered_data/`

Structure:
```
filtered_data/
├── manifest.json              # Master manifest
├── archetypes/               # 15 player archetypes
├── powersets/                # Power set definitions
├── powers/                   # 5,775 individual powers
└── boost_sets/               # 228 enhancement sets
```

## Usage

### Import All Data
```bash
just json-import-all
```

### Import Specific Category
```bash
just json-import-archetypes
just json-import-powersets
just json-import-powers
just json-import-enhancements
```

### Health Check
```bash
just json-import-health
```

## Implementation Details

### Manifest Structure
```json
{
  "version": "2025.06.17",
  "source": "city_of_data_homecoming",
  "categories": {
    "archetypes": {
      "count": 15,
      "path": "archetypes/"
    },
    "powers": {
      "count": 5775,
      "path": "powers/"
    }
  }
}
```

### Import Flow
1. Read manifest.json
2. Validate manifest schema
3. Process each category sequentially
4. Batch database inserts (100 records/batch)
5. Track progress in import_progress table
6. Handle errors with rollback capability

### Error Handling
- Invalid JSON: Skip file, log error, continue
- Schema mismatch: Log validation errors, skip record
- Database errors: Rollback batch, log error, retry
- Missing files: Log warning, continue with available data

## Testing

Run import tests:
```bash
pytest tests/backend/data_import/ -v
```

Test coverage requirement: >85%

## Related Skills
- @database-specialist: For schema questions
- @backend-specialist: For API integration
