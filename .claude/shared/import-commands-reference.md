# Import Commands Reference

Comprehensive reference for all data import commands in Mids Hero Web.

## Command Categories

### Generic Import Commands (All Parsers)

| Command | Description | Example |
|---------|-------------|---------|
| `just import-all` | Import all data types from directory | `just import-all /data/exported-json-latest` |
| `just import-type` | Import specific data type | `just import-type powers data.json` |
| `just import-clear` | Clear existing data before import | `just import-clear powers data.json` |
| `just import-resume` | Resume import from specific record | `just import-resume powers data.json 1000` |

### Specific Data Type Shortcuts

| Command | Data Type | Example |
|---------|-----------|---------|
| `just import-archetypes` | Character archetypes | `just import-archetypes I9_structured.json` |
| `just import-powersets` | Powerset definitions | `just import-powersets I9_structured.json` |
| `just import-powers` | Power definitions | `just import-powers I9_structured.json` |
| `just import-enhancements` | Enhancement/IO sets | `just import-enhancements enhancements.json` |
| `just import-salvage` | Crafting salvage | `just import-salvage salvage.json` |
| `just import-recipes` | Enhancement recipes | `just import-recipes recipes.json` |

### I12 High-Performance Commands

| Command | Description | Parameters | Example |
|---------|-------------|------------|---------|
| `just i12-import` | Import I12 power data | file [batch_size] [chunk_size] [memory_limit] | `just i12-import data.json 1000 5000 1.0` |
| `just i12-import-resume` | Resume I12 import | file resume_from [batch_size] | `just i12-import-resume data.json 50000` |
| `just i12-validate` | Validate I12 data | file | `just i12-validate data.json` |

### System Status & Monitoring

| Command | Description | Output |
|---------|-------------|--------|
| `just import-health` | Full import system health check | System status, performance indicators |
| `just import-status` | Import system status | Database, cache, Redis status |
| `just import-stats` | Database record counts | Records per table |
| `just cache-stats` | Cache performance metrics | Hit rates, memory usage |

### Performance & Optimization

| Command | Description | Use Case |
|---------|-------------|----------|
| `just perf-bench` | I12 performance benchmarks | Test I12 import performance |
| `just perf-test-all` | All performance tests | Complete performance validation |
| `just db-optimize` | Database optimization | Refresh materialized views |
| `just db-vacuum` | Database maintenance | Optimize database performance |

### Cache Management

| Command | Description | Effect |
|---------|-------------|--------|
| `just cache-clear` | Clear power cache | Removes all cached data |
| `just cache-stats` | Cache performance statistics | Shows hit rates, sizes |

## Command Details

### Import All Data
```bash
# Import complete dataset from directory
just import-all /path/to/exported-json-latest

# With custom batch size
just import-all /path/to/data 2000
```

**Expected Files in Directory:**
- `I9_structured.json` (archetypes, powersets, powers)
- `enhancements.json`
- `salvage.json` 
- `recipes.json`
- `AttribMod.json`
- `TypeGrades.json`

### Import Specific Types
```bash
# Basic import
just import-type powers I9_structured.json

# With custom batch size
just import-type powers data.json 1500

# Clear existing data first
just import-clear powers data.json

# Resume from specific record
just import-resume powers data.json 5000
```

### I12 High-Performance Import
```bash
# Default settings (1000 batch, 5000 chunk, 1.0GB limit)
just i12-import I12_powers.json

# Custom settings
just i12-import data.json 500 2000 0.5

# Resume from record 150000
just i12-import-resume data.json 150000

# Validation only
just i12-validate data.json
```

### System Monitoring
```bash
# Complete health check
just import-health

# Quick status
just import-status

# Record counts
just import-stats

# Cache performance
just cache-stats
```

## Parameter Reference

### Generic Import Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | - | Data type: archetypes, powersets, powers, enhancements, salvage, recipes, attribute-modifiers, type-grades |
| `file` | path | - | Path to JSON data file |
| `batch_size` | integer | 1000 | Records processed per database transaction |
| `resume_from` | integer | 0 | Record index to resume from |

### I12 Import Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `file` | path | - | - | Path to I12 JSON file |
| `batch_size` | integer | 1000 | 100-5000 | Database transaction size |
| `chunk_size` | integer | 5000 | 1000-10000 | File reading chunk size |
| `memory_limit` | float | 1.0 | 0.5-4.0 | Memory limit in GB |
| `resume_from` | integer | 0 | 0-∞ | Starting record index |

## Performance Tuning

### Memory-Constrained Systems
```bash
# Small batch and chunk sizes
just i12-import data.json 500 1000 0.5

# Generic imports with small batches
just import-type powers data.json 500
```

### High-Performance Systems
```bash
# Large batch and chunk sizes
just i12-import data.json 2000 10000 2.0

# Generic imports with large batches
just import-type powers data.json 3000
```

### Network Storage
```bash
# Moderate settings for network I/O
just i12-import data.json 1000 3000 1.0
```

## Error Codes & Recovery

### Common Exit Codes
- `0` - Success
- `1` - File not found or invalid
- `2` - Database connection error
- `3` - Validation errors
- `4` - Memory limit exceeded
- `5` - Foreign key constraint violations

### Recovery Commands
```bash
# After file errors
just i12-validate data.json

# After database errors
just db-status
just db-migrate

# After memory errors
just cache-clear
just i12-import data.json 500 1000 0.5

# After constraint errors
just import-stats  # Check prerequisites
```

## Integration Patterns

### Full Data Import Workflow
```bash
# 1. Prerequisites
just import-archetypes I9_structured.json
just import-powersets I9_structured.json

# 2. High-performance power import
just i12-import I12_powers.json

# 3. Additional data
just import-enhancements enhancements.json
just import-salvage salvage.json
just import-recipes recipes.json

# 4. System optimization
just db-optimize
just cache-stats
```

### Development Workflow
```bash
# Quick setup for testing
just import-clear archetypes I9_structured.json
just import-clear powersets I9_structured.json
just i12-validate test_data.json
just i12-import test_data.json 100 500 0.2
```

### Production Deployment
```bash
# Health check
just import-health

# Full import with monitoring
just import-all /data/production-export

# Optimization
just db-optimize
just db-vacuum

# Verification
just import-stats
just perf-bench
```

## Environment Variables

### Database Configuration
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mids_web
```

### I12 Import Configuration
```bash
I12_MEMORY_LIMIT_GB=1.0
I12_BATCH_SIZE=1000
I12_CHUNK_SIZE=5000
```

### Cache Configuration
```bash
REDIS_URL=redis://redis:6379/0
```

## CLI Direct Usage

For advanced usage, call the import modules directly:

### Generic Imports
```bash
cd backend
uv run python -m app.data_import.cli --help
uv run python -m app.data_import.cli --batch-size 1500 powers data.json
```

### I12 Import
```bash
cd backend
uv run python scripts/import_i12_data.py --help
uv run python scripts/import_i12_data.py data.json --verbose --resume-from 10000
```

## Best Practices

### Data Preparation
- Validate files before import: `just i12-validate`
- Check file sizes and record counts
- Ensure prerequisite data exists (archetypes, powersets)

### Import Order
1. Archetypes (required for powersets)
2. Powersets (required for powers) 
3. Powers (I12 or generic)
4. Enhancements, Salvage, Recipes (any order)
5. Attribute modifiers, Type grades (any order)

### Performance
- Start with defaults, tune based on results
- Monitor with `just import-health` during imports
- Use `just cache-stats` to verify caching effectiveness
- Run `just perf-bench` to validate performance

### Error Prevention
- Always run `just import-health` before large imports
- Use `just i12-validate` for I12 data
- Keep Redis running for optimal performance
- Monitor memory usage during imports