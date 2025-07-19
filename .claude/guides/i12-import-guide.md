# I12 Power Data Import Guide

Complete guide for importing I12 power data (360K+ records) using the high-performance streaming parser.

## Quick Start

```bash
# Basic import
just i12-import /path/to/I12_powers.json

# Check system health
just import-health

# Monitor progress
just import-stats
```

## Prerequisites

### System Requirements
- **Memory**: 2GB+ available (parser uses <1GB)
- **Disk Space**: 5GB+ for database storage
- **Redis**: Required for optimal caching performance
- **PostgreSQL**: 12+ with JSONB support

### Setup Verification
```bash
# Check all systems
just import-health

# Verify database status
just db-status

# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

## Data Preparation

### I12 File Format
The I12 streaming parser expects JSON files in this format:
```json
[
  {
    "Name": "Fire Blast",
    "InternalName": "Blaster_Ranged.Fire_Blast.Blast",
    "DisplayName": "Fire Blast", 
    "Description": "You can hurl a blast of fire...",
    "PowersetFullName": "Blaster.Fire_Blast",
    "PowersetName": "Fire Blast",
    "ArchetypeName": "Blaster",
    "Level": 1,
    "PowerType": "Click",
    "TargetType": "Enemy",
    "Range": 80.0,
    "Accuracy": 1.0,
    "EnduranceCost": 5.2,
    "RechargeTime": 4.0,
    "ActivationTime": 1.67,
    "MaxTargets": 1,
    "Effects": [...],
    "Requirements": {...},
    "EnhancementTypes": [...]
  }
]
```

### File Validation
```bash
# Validate file before import
just i12-validate /path/to/data.json

# Check file size and record count
ls -lh /path/to/data.json
jq '. | length' /path/to/data.json
```

## Import Operations

### Basic Import
```bash
# Standard import with default settings
just i12-import /path/to/I12_powers.json

# Custom batch and chunk sizes for performance tuning
just i12-import data.json 500 2000 0.5
#                         │   │    └─ Memory limit (GB)
#                         │   └────── Chunk size (records per read)
#                         └─────────── Batch size (records per DB transaction)
```

### Resume Capability
```bash
# Resume from specific record (useful for large imports)
just i12-import-resume /path/to/data.json 150000

# Resume with custom batch size
just i12-import-resume data.json 50000 2000
```

### Validation Only
```bash
# Test data without importing (dry run)
just i12-validate /path/to/data.json
```

## Performance Tuning

### Configuration Parameters

| Parameter | Default | Description | Tuning Guidelines |
|-----------|---------|-------------|-------------------|
| `batch_size` | 1000 | Records per DB transaction | Lower for memory, higher for speed |
| `chunk_size` | 5000 | Records read at once | Balance memory vs I/O |
| `memory_limit` | 1.0 GB | Memory limit before GC | Set based on available RAM |

### Performance Scenarios

**Large Memory Available (8GB+)**:
```bash
just i12-import data.json 2000 10000 2.0
```

**Limited Memory (4GB)**:
```bash
just i12-import data.json 500 2000 0.5
```

**SSD Storage (Fast I/O)**:
```bash
just i12-import data.json 1500 8000 1.5
```

**Network Storage (Slow I/O)**:
```bash
just i12-import data.json 1000 3000 1.0
```

## Monitoring & Diagnostics

### Real-Time Monitoring
```bash
# Full system health check
just import-health

# Database record counts
just import-stats

# Cache performance metrics
just cache-stats

# Memory and performance
just perf-bench
```

### Log Analysis
```bash
# View import logs (during import)
tail -f backend/i12_import.log

# Docker logs
docker-compose logs backend

# Database connections
just db-connect
\d+ powers
SELECT COUNT(*) FROM powers;
```

## Error Recovery

### Common Issues

**Memory Errors**:
```bash
# Reduce memory usage
just i12-import data.json 500 1000 0.5

# Clear cache before import
just cache-clear
```

**Database Errors**:
```bash
# Check constraints and foreign keys
just db-status

# Ensure prerequisites exist
just import-stats  # Check archetypes/powersets
```

**Import Interruption**:
```bash
# Check last successful record
just import-stats

# Resume from checkpoint
just i12-import-resume data.json LAST_RECORD_NUMBER
```

### Troubleshooting Steps

1. **Check System Health**:
   ```bash
   just import-health
   ```

2. **Validate Data**:
   ```bash
   just i12-validate data.json
   ```

3. **Check Prerequisites**:
   ```bash
   just import-stats  # Ensure archetypes/powersets exist
   ```

4. **Clear Cache**:
   ```bash
   just cache-clear
   ```

5. **Reset if Needed**:
   ```bash
   just db-reset
   just db-migrate
   ```

## Performance Optimization

### Database Optimization
```bash
# Refresh materialized views
just db-optimize

# Database maintenance
just db-vacuum

# Check query performance
just perf-bench
```

### Cache Optimization
```bash
# View cache statistics
just cache-stats

# Clear and rebuild cache
just cache-clear
# Import will rebuild cache automatically
```

## Production Import Workflow

### Pre-Import Checklist
- [ ] System resources available (memory, disk)
- [ ] Redis running and accessible
- [ ] Database migrations up to date
- [ ] Backup created (if updating existing data)
- [ ] File validated with `just i12-validate`

### Import Process
```bash
# 1. System health check
just import-health

# 2. Clear cache for clean state
just cache-clear

# 3. Validate data file
just i12-validate /path/to/I12_data.json

# 4. Run import with monitoring
just i12-import /path/to/I12_data.json

# 5. Verify results
just import-stats
just cache-stats
```

### Post-Import Verification
```bash
# Check record counts
just import-stats

# Verify data integrity
just db-connect
SELECT COUNT(*) FROM powers;
SELECT archetype_name, COUNT(*) FROM power_build_summary GROUP BY archetype_name;

# Test cache performance
just cache-stats

# Run performance benchmarks
just perf-bench
```

## Advanced Usage

### Custom Import Scripts
For specialized imports, use the Python CLI directly:
```bash
cd backend
uv run python scripts/import_i12_data.py \
  /path/to/data.json \
  --batch-size 1500 \
  --chunk-size 8000 \
  --memory-limit 2.0 \
  --resume-from 0 \
  --verbose
```

### Integration with Other Importers
```bash
# Import prerequisites first
just import-archetypes /path/to/I9_structured.json
just import-powersets /path/to/I9_structured.json

# Then import I12 power data
just i12-import /path/to/I12_powers.json

# Import remaining data
just import-enhancements /path/to/enhancements.json
```

### Automated Workflows
```bash
# Complete data import workflow
just import-all /path/to/exported-json-latest

# Or selective import with I12 optimization
just import-archetypes /path/to/I9_structured.json
just import-powersets /path/to/I9_structured.json  
just i12-import /path/to/I12_powers.json
just import-enhancements /path/to/enhancements.json
```

## Performance Benchmarks

### Expected Performance
- **Import Rate**: 1,000-5,000 records/second
- **Memory Usage**: <1GB peak
- **Import Time**: 2-5 minutes for 360K records
- **Query Performance**: <100ms average

### Benchmark Commands
```bash
# Run I12 performance benchmark
just perf-bench

# Full performance test suite
just perf-test-all

# Custom benchmark
cd backend
uv run pytest tests/test_i12_streaming_parser.py::TestI12StreamingParser::test_performance_benchmark -v
```

## Support & Resources

### Documentation
- **Implementation Details**: `backend/app/data_import/i12_streaming_parser.py`
- **Test Examples**: `backend/tests/test_i12_streaming_parser.py`
- **Memory Tracking**: `.claude/memory/issue-168-i12-power-data-handler.md`

### Community
- **GitHub Issues**: Report problems with I12 import
- **Performance Discussions**: Share tuning results
- **Feature Requests**: Suggest improvements

### Emergency Contacts
- **Database Issues**: Use database agent (`.claude/agents/database-agent.md`)
- **Performance Problems**: Check I12 agent context (`.claude/agents/i12-import-agent.md`)
- **System Failures**: Run `just import-health` for diagnostics