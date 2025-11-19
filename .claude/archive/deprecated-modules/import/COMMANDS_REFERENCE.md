# Import Commands Reference
Last Updated: 2025-11-19 20:27:56 UTC

## Just Commands

### Basic Import Commands
```bash
# Import all data types from directory
just import-all <data_dir> [batch_size]
# Example: just import-all data/exports/ 1000

# Import specific type
just import-type <type> <file> [batch_size]
# Example: just import-type powers data/imported/powers.json 500

# Clear and import (removes existing data)
just import-clear <type> <file> [batch_size]
# Example: just import-clear enhancements data/imported/enhancements.json
```

### Type-Specific Commands
```bash
just import-archetypes <file>     # Import archetype data
just import-powersets <file>      # Import powerset data
just import-powers <file>         # Import power data
just import-enhancements <file>   # Import enhancement data
just import-recipes <file>        # Import recipe data
just import-salvage <file>        # Import salvage data
```

### I12 Power Import
```bash
# Standard import
just i12-import <file>
# Example: just i12-import data/imported/I12_powers.json

# Resume from failure
just i12-import-resume <file> <record_number>
# Example: just i12-import-resume data/imported/I12_powers.json 50000

# Validate only (no import)
just i12-validate <file>
# Example: just i12-validate data/imported/I12_powers.json
```

### Health & Monitoring
```bash
just import-health      # Full system health check
just import-status      # Current import system status
just import-stats       # Database record counts
just cache-stats        # Cache performance metrics
just perf-bench         # Run performance benchmarks
just perf-test-all      # Complete performance test suite
```

## Python CLI Direct Usage

### Import Script Options
```bash
cd backend
python scripts/import_i12_data.py --help

Options:
  json_file                    Path to I12 JSON data file
  --database-url URL          Database connection URL
  --batch-size N              Records per database transaction (default: 1000)
  --chunk-size N              Records to read at once (default: 5000)
  --memory-limit GB           Memory limit before GC (default: 1.0)
  --resume-from N             Resume from record number
  --validate-only             Validate without importing
  --clear-cache               Clear power cache before import
  --verbose, -v               Enable verbose logging
```

### Examples
```bash
# Basic import
python scripts/import_i12_data.py data/imported/I12_powers.json

# Performance tuning
python scripts/import_i12_data.py data/imported/I12_powers.json \
    --batch-size 2000 \
    --chunk-size 10000 \
    --memory-limit 2.0

# Debug mode
python scripts/import_i12_data.py data/imported/I12_powers.json \
    --verbose \
    --batch-size 100

# Resume with cache clear
python scripts/import_i12_data.py data/imported/I12_powers.json \
    --resume-from 150000 \
    --clear-cache
```

### Generic Import CLI
```bash
cd backend
python -m app.data_import.cli --help

Commands:
  all <directory>              Import all data types
  archetypes <file>           Import archetypes
  powersets <file>            Import powersets
  powers <file>               Import powers
  enhancements <file>         Import enhancements
  clear-and-import <type> <file>  Clear existing and import

Options:
  --batch-size N              Batch size for imports
  --dry-run                   Validate without importing
```

## Environment Variables

```bash
# Database connection
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# Logging
export LOG_LEVEL="DEBUG"  # DEBUG, INFO, WARNING, ERROR

# Performance
export IMPORT_BATCH_SIZE="1000"
export IMPORT_MEMORY_LIMIT="1.0"
```

## Output Examples

### Successful Import
```
🚀 Starting I12 power data import from data/imported/I12_powers.json
📊 Found 360,847 total records to process
⏳ Processing... 50,000/360,847 (13.8%)
⏳ Processing... 100,000/360,847 (27.7%)
...
✅ Import completed in 342.5 seconds
📈 Processed: 360,847, Imported: 360,523, Errors: 324
```

### Health Check Output
```
🏥 Import System Health Check
============================
Database status:
✅ Connected to PostgreSQL
✅ All migrations applied

Table record counts:
📊 Archetypes: 5
📊 Powersets: 106
📊 Powers: 2,147
📊 Enhancements: 1,934

Cache status:
✅ Memory cache: 847/1000 (84.7%)
✅ Redis: Connected
✅ Hit rate: 92.3%

Performance indicators:
✅ I12 parser: Ready for 360K+ records
✅ Memory limit: 1GB
✅ Target query time: <100ms
```

### Error Handling
```
❌ Import failed with 1,245 errors
First 10 errors:
  1. Record 10234: Unknown powerset 'Gadgetry'
  2. Record 10235: Invalid level value: -1
  ...

💡 Tip: Run with --verbose for detailed error logs
```

## Quick Troubleshooting

| Issue | Command |
|-------|---------|
| Check what's imported | `just import-stats` |
| Verify system health | `just import-health` |
| View recent imports | `just db-shell` → `SELECT * FROM import_logs ORDER BY created_at DESC;` |
| Clear bad data | `just import-clear <type> <file>` |
| Reset everything | `just db-reset` → `just import-all data/` |

---
*For implementation details, see `.claude/modules/import/guide.md`*
