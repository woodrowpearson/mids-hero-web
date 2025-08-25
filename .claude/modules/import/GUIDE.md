# Import Module Guide

## Quick Start

```bash
# Check system health first
just import-health

# Import everything from a directory
just import-all data/exports/

# Import specific data type  
just i12-import data/imported/I12_powers.json
```

## Import System Architecture

### High-Performance I12 Parser
- **Capacity**: 360K+ power records
- **Memory**: < 1GB with streaming
- **Speed**: ~1000 records/second
- **Features**: Resume on failure, progress tracking, validation

### Components
```
backend/app/data_import/
├── i12_streaming_parser.py   # Main I12 parser
├── base_importer.py         # Base class for all importers
├── cli.py                   # Command-line interface
└── validators/              # Data validation
```

## I12 Power Data Import

### Basic Import
```bash
# Import with default settings
just i12-import data/imported/I12_powers.json

# With custom batch size and memory limit
cd backend
python scripts/import_i12_data.py data/imported/I12_powers.json \
    --batch-size 500 \
    --memory-limit 0.5
```

### Resume Failed Import
```bash
# Resume from specific record
just i12-import-resume data/i12_powers.json 50000

# Or directly
python scripts/import_i12_data.py data/imported/I12_powers.json \
    --resume-from 50000
```

### Validate Without Importing
```bash
just i12-validate data/i12_powers.json
```

## Generic Data Import

### Import All Types
```bash
# Import archetypes, powersets, powers, enhancements
just import-all data/exports/

# With custom batch size
just import-all data/exports/ 500
```

### Import Specific Types
```bash
just import-archetypes data/imported/archetypes.json
just import-powersets data/imported/powersets.json  
just import-powers data/imported/powers.json
just import-enhancements data/imported/enhancements.json
```

### Clear and Reimport
```bash
# Clear existing data and import fresh
just import-clear powers data/imported/powers.json
```

## Monitoring & Health

### System Status
```bash
# Overall health check
just import-health

# Detailed status
just import-status

# Database record counts
just import-stats

# Cache performance
just cache-stats
```

### Performance Testing
```bash
# Run I12 benchmarks
just perf-bench

# Full performance test suite
just perf-test-all
```

## Implementation Details

### I12 Parser Architecture
```python
# Three-layer streaming design
StreamingJsonReader  # Chunked file reading
    ↓
PowerDataProcessor  # Format transformation  
    ↓
I12StreamingParser  # Database operations
```

### Memory Management
```python
# Automatic garbage collection
parser = I12StreamingParser(
    memory_limit_gb=1.0  # Triggers GC when exceeded
)

# Manual memory monitoring
import psutil
process = psutil.Process()
memory_mb = process.memory_info().rss / 1024 / 1024
```

### Error Handling
```python
# Parser tracks all errors
parser.import_data(file_path)
print(f"Imported: {parser.imported_count}")
print(f"Errors: {parser.error_count}")

# Error details available
for error in parser.errors[:10]:
    print(f"Record {error['record_index']}: {error['error']}")
```

## Data Formats

### I12 Power Format
```json
{
  "Name": "Fire Blast",
  "InternalName": "Blaster_Ranged.Fire_Blast.Blast",  
  "PowersetName": "Fire Blast",
  "ArchetypeName": "Blaster",
  "Level": 1,
  "Accuracy": 1.0,
  "EnduranceCost": 5.2,
  "RechargeTime": 4.0,
  "Effects": [
    {
      "EffectType": "Damage",
      "DamageType": "Fire",
      "Scale": 1.0
    }
  ]
}
```

### Database Transform
```python
# I12 format → Database model
{
    "name": "Fire Blast",
    "internal_name": "Blaster_Ranged.Fire_Blast.Blast",
    "powerset_id": 1,  # Resolved from cache
    "level_available": 1,
    "accuracy": 1.0,
    "endurance_cost": 5.2,
    "recharge_time": 4.0,
    "effects": [...]  # Preserved as JSON
}
```

## Troubleshooting

### Common Issues

**"Unknown powerset" errors**:
```bash
# Ensure powersets imported first
just import-powersets data/powersets.json
just import-powers data/powers.json  # Then powers
```

**Memory errors**:
```bash
# Reduce batch/chunk sizes
python scripts/import_i12_data.py data/imported/I12_powers.json \
    --batch-size 100 \
    --chunk-size 1000 \
    --memory-limit 0.5
```

**Resume not working**:
```bash
# Check import logs
just db-shell
SELECT * FROM import_logs ORDER BY created_at DESC LIMIT 5;
```

### Debug Mode
```bash
# Verbose logging
cd backend
export LOG_LEVEL=DEBUG
python scripts/import_i12_data.py data/imported/I12_powers.json --verbose
```

### Clear Cache
```bash
# If cache corrupted
python scripts/import_i12_data.py data/imported/I12_powers.json --clear-cache
```

## Best Practices

1. **Order Matters**: Import archetypes → powersets → powers
2. **Validate First**: Use validate mode before large imports
3. **Monitor Progress**: Watch logs for error patterns
4. **Batch Sizing**: Start with defaults, adjust if needed
5. **Cache Warm-up**: Import frequently-used data first

---
*For command details, see `.claude/modules/import/commands-reference.md`*