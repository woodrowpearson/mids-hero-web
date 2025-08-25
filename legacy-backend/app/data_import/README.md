# Data Import Module

This module provides functionality to import City of Heroes game data from JSON files into the PostgreSQL database.

## Overview

The data import system is designed to handle large datasets efficiently using:
- Batch processing for performance
- Idempotent operations (safe to run multiple times)
- Progress tracking and logging
- Error handling with detailed reporting
- Resume capability for large imports

## Importers

### ArchetypeImporter
Imports character archetype data (Blaster, Controller, etc.)

### PowersetImporter & PowerImporter
Imports powerset and individual power data

### EnhancementImporter
Imports enhancement definitions including IO sets

### SalvageImporter
Imports crafting salvage items

### RecipeImporter
Imports enhancement recipes and their salvage requirements

### AttributeModifierImporter & TypeGradeImporter
Imports detailed attribute modifiers and archetype-specific grades

## Usage

### Command Line Interface

```bash
# Import all data files from a directory
python -m app.data_import.cli all /path/to/data/exported-json-latest

# Import specific data type
python -m app.data_import.cli archetypes /path/to/I9_structured.json

# Clear existing data before import
python -m app.data_import.cli --clear salvage /path/to/salvage.json

# Resume from specific record
python -m app.data_import.cli --resume-from 5000 powers /path/to/I12_structured.json

# Use custom batch size
python -m app.data_import.cli --batch-size 5000 recipes /path/to/recipes.json
```

### Programmatic Usage

```python
from app.data_import import ArchetypeImporter
from pathlib import Path

# Create importer
importer = ArchetypeImporter("postgresql://user:pass@localhost/db")

# Import data
result = importer.import_data(Path("data.json"))

print(f"Imported {result.records_imported} records")
print(f"Errors: {result.errors}")
```

## Import Order

Due to foreign key dependencies, data should be imported in this order:

1. Archetypes
2. Powersets
3. Powers
4. Salvage
5. Enhancements
6. Recipes
7. Attribute Modifiers
8. Type Grades

The `import all` command handles this automatically.

## Performance Considerations

- Default batch size is 1000 records
- Use larger batch sizes (5000-10000) for better performance on large datasets
- The I12 power data (360K+ entries) may take several minutes to import
- Consider using `--clear` flag for initial imports to avoid constraint violations

## Error Handling

- Errors are logged and stored in the ImportLog table
- Failed records are tracked individually
- Use `--continue-on-error` with `import all` to skip failed imports

## Database Requirements

- PostgreSQL 12+ with JSONB support
- Sufficient disk space for large datasets
- Proper indexes created via migrations