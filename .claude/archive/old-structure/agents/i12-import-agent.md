# I12 Import Agent

Specialized agent for I12 power data import operations in the Mids Hero Web project.

## Core Responsibilities

- I12 streaming parser operations for 360K+ power records
- Multi-tier caching system management (LRU + Redis)
- Database optimization for high-performance queries
- Memory management and performance monitoring
- Import error recovery and resume functionality

## Context Files

When working on I12 import tasks, include:

- `.claude/memory/issue-168-i12-power-data-handler.md`
- `backend/app/data_import/i12_streaming_parser.py`
- `backend/app/services/power_cache.py`
- `backend/scripts/import_i12_data.py`
- `backend/tests/test_i12_streaming_parser.py`
- `backend/alembic/versions/0236d1f741c9_add_i12_power_data_optimizations.py`

## Key Commands

```bash
# I12 High-Performance Import
just i12-import data.json                    # Import 360K+ power records
just i12-import-resume data.json 50000       # Resume from record 50000
just i12-validate data.json                  # Validate without importing

# System Monitoring
just import-health                           # Full system health check
just import-stats                            # Database record counts
just cache-stats                             # Cache performance metrics
just perf-bench                              # I12 performance benchmarks

# Cache Management
just cache-clear                             # Clear power cache
just db-optimize                             # Refresh materialized views

# Performance Testing
just perf-test-all                           # All performance tests
```

## Technical Specifications

### Performance Targets
- **Memory Usage**: < 1GB during import
- **Import Time**: < 5 minutes for 360K records  
- **Query Performance**: < 100ms average
- **Concurrent Access**: Supported via Redis caching

### Architecture Components

1. **StreamingJsonReader**: Chunked file processing
2. **PowerDataProcessor**: I12 format transformation  
3. **I12StreamingParser**: Main orchestrator with memory management
4. **PowerCacheService**: Multi-tier caching (LRU + Redis)
5. **Database Optimizations**: Indexes, materialized views

## Import Process

```python
# Standard I12 import workflow
parser = I12StreamingParser(
    database_url="postgresql://...",
    batch_size=1000,
    chunk_size=5000, 
    memory_limit_gb=1.0
)

parser.import_data(
    file_path=Path("I12_data.json"),
    resume_from=0,
    progress_callback=progress_handler
)
```

## Memory Management

- **Streaming Processing**: Never load entire file into memory
- **Chunked Reading**: Configurable chunk sizes (default: 5000)
- **Batch Inserts**: Database batches (default: 1000)
- **Garbage Collection**: Automatic when memory limit reached
- **Progress Tracking**: Real-time memory monitoring

## Database Optimizations

### Indexes Created
- `idx_power_powerset_level` - Composite index for common queries
- `idx_power_type_level` - Power type filtering  
- `idx_power_name_powerset` - Name-based lookups
- `idx_power_internal_name` - Internal name searches
- `idx_power_effects` - GIN index for JSON effects
- `idx_power_effect_groups` - GIN index for effect groups

### Materialized View
- `power_build_summary` - Pre-computed power data for builds
- Includes joins with archetypes and powersets
- Refreshed via `just db-optimize`

## Caching Strategy

### Two-Tier Architecture
1. **Memory Cache (LRU)**: Fast access for frequently used data
2. **Redis Cache**: Distributed caching for concurrent access

### Cache Types
- `get_power_by_id()` - Individual power details
- `get_powers_by_powerset()` - Powerset power lists  
- `get_build_summary_data()` - Build planning data

### Cache Management
```bash
just cache-stats    # View performance metrics
just cache-clear    # Clear all cache layers
```

## Error Handling

### Recovery Features
- **Resume Capability**: Restart from any record number
- **Error Logging**: Detailed error tracking with context
- **Validation**: Pre-import data validation
- **Rollback**: Transaction safety for failed batches

### Common Issues
1. **Memory Exceeded**: Reduce chunk_size or batch_size
2. **Validation Errors**: Check required fields and data types
3. **Foreign Key Violations**: Ensure archetypes/powersets exist
4. **Performance Issues**: Check cache configuration

## Performance Monitoring

### Key Metrics
- **Import Rate**: Records per second
- **Memory Usage**: Current and peak memory
- **Cache Hit Rate**: Memory and Redis performance
- **Query Performance**: Average response times

### Benchmarking
```bash
just perf-bench        # Run I12 performance benchmark
just perf-test-all     # Full performance test suite
```

## CLI Usage Examples

```bash
# Basic import
just i12-import /path/to/I12_powers.json

# Custom configuration
just i12-import data.json 500 2500 0.5  # batch_size chunk_size memory_limit

# Resume failed import
just i12-import-resume data.json 150000

# Validation only
just i12-validate data.json

# System health check
just import-health
```

## Troubleshooting

### Memory Issues
```bash
# Check current memory usage
just import-stats

# Reduce memory footprint
just i12-import data.json 500 1000 0.5
```

### Performance Issues  
```bash
# Check cache performance
just cache-stats

# Optimize database
just db-optimize

# Run benchmarks
just perf-bench
```

### Import Failures
```bash
# Check system health
just import-health

# Validate data first
just i12-validate data.json

# Resume from last known good record
just i12-import-resume data.json RECORD_NUMBER
```

## Integration Notes

- **Compatible with existing importers**: Works alongside other data import tools
- **Redis dependency**: Requires Redis for optimal performance
- **Database migration**: Requires migration 0236d1f741c9 or later
- **Testing**: Comprehensive test suite in `test_i12_streaming_parser.py`

## Future Enhancements

- [ ] Parallel import processing
- [ ] Real-time import monitoring dashboard
- [ ] Incremental update support
- [ ] Data compression for cache efficiency
- [ ] Import scheduling and automation