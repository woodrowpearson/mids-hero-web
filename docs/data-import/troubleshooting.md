# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the Mids Hero Web data import system.

## Table of Contents
- [Common Issues](#common-issues)
- [Import Errors](#import-errors)
- [Performance Problems](#performance-problems)
- [Database Issues](#database-issues)
- [Memory Issues](#memory-issues)
- [Data Validation Errors](#data-validation-errors)
- [Diagnostic Tools](#diagnostic-tools)
- [Emergency Procedures](#emergency-procedures)

## Common Issues

### Quick Diagnosis Flowchart

```mermaid
flowchart TD
    Start([Import Problem])
    Type{What type<br/>of error?}
    
    Import[Import fails<br/>to start]
    Slow[Import running<br/>slowly]
    Error[Import shows<br/>errors]
    Memory[Out of<br/>memory]
    Data[Invalid data<br/>errors]
    
    Start --> Type
    Type --> Import
    Type --> Slow
    Type --> Error
    Type --> Memory
    Type --> Data
    
    Import --> CheckDB[Check database<br/>connection]
    Import --> CheckFiles[Check file<br/>paths]
    
    Slow --> CheckPerf[Run performance<br/>diagnostics]
    Slow --> CheckIndex[Check database<br/>indexes]
    
    Error --> CheckLogs[Review error<br/>logs]
    Error --> ValidateJSON[Validate JSON<br/>files]
    
    Memory --> ReduceBatch[Reduce batch<br/>size]
    Memory --> CheckRAM[Check system<br/>memory]
    
    Data --> CheckSchema[Verify data<br/>schema]
    Data --> CheckRefs[Check foreign<br/>key refs]
    
    style Start fill:#f44336
    style Type fill:#ff9800
    style CheckDB,CheckFiles,CheckPerf,CheckIndex,CheckLogs,ValidateJSON,ReduceBatch,CheckRAM,CheckSchema,CheckRefs fill:#4caf50
```

## Import Errors

### Error: "Database connection failed"

**Symptoms:**
```
ERROR: Database connection failed
psycopg2.OperationalError: could not connect to server
```

**Diagnosis:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
just db-check

# Check connection string
echo $DATABASE_URL
```

**Solutions:**
1. **Start PostgreSQL:**
   ```bash
   sudo systemctl start postgresql
   ```

2. **Fix connection string:**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost:5432/midshero"
   ```

3. **Check firewall:**
   ```bash
   sudo ufw allow 5432/tcp
   ```

### Error: "File not found"

**Symptoms:**
```
ERROR: File not found: data/json/powers.json
FileNotFoundError: [Errno 2] No such file or directory
```

**Diagnosis:**
```bash
# Check file exists
ls -la data/json/

# Check current directory
pwd

# Find JSON files
find . -name "*.json" -type f
```

**Solutions:**
1. **Use absolute paths:**
   ```bash
   just import-powers /absolute/path/to/powers.json
   ```

2. **Check file permissions:**
   ```bash
   chmod 644 data/json/*.json
   ```

### Error: "Invalid JSON format"

**Symptoms:**
```
ERROR: Invalid JSON in file
json.decoder.JSONDecodeError: Expecting value: line 1 column 1
```

**Diagnosis:**
```bash
# Validate JSON syntax
just validate-json data/powers.json

# Check file encoding
file -i data/powers.json

# Preview file content
head -n 20 data/powers.json
```

**Solutions:**
1. **Fix JSON syntax:**
   ```bash
   # Use jq to format and validate
   jq . data/powers.json > data/powers_fixed.json
   ```

2. **Convert encoding:**
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 data/powers.json > data/powers_utf8.json
   ```

## Performance Problems

### Slow Import Performance

**Symptoms:**
- Import takes hours instead of minutes
- Progress bar moves very slowly
- Database CPU usage is high

**Performance Diagnostics:**

```mermaid
graph LR
    subgraph "Performance Bottlenecks"
        IO[Disk I/O<br/>Check: iostat]
        CPU[CPU Usage<br/>Check: top]
        RAM[Memory<br/>Check: free -h]
        DB[Database<br/>Check: pg_stat]
        Net[Network<br/>Check: netstat]
    end
    
    style IO fill:#f44336
    style CPU fill:#ff9800
    style RAM fill:#ffeb3b
    style DB fill:#4caf50
    style Net fill:#2196f3
```

**Diagnosis Commands:**
```bash
# Overall system performance
just perf-diagnose

# Database performance
just db-slow-queries
just db-table-stats

# Import-specific metrics
just import-perf --verbose

# I/O statistics
iostat -x 1 10

# Database connections
just db-connections
```

**Solutions:**

1. **Optimize batch size:**
   ```bash
   # Increase for better performance (if memory allows)
   just import-powers data.json --batch-size 5000
   
   # Decrease for memory constraints
   just import-powers data.json --batch-size 500
   ```

2. **Database optimization:**
   ```bash
   # Run maintenance
   just db-optimize
   
   # Update statistics
   just db-analyze
   
   # Rebuild indexes
   just db-reindex
   ```

3. **Disable constraints temporarily:**
   ```bash
   # For massive imports only!
   just db-constraints-disable
   just import-all data/
   just db-constraints-enable
   ```

## Database Issues

### Foreign Key Constraint Violations

**Symptoms:**
```
ERROR: Foreign key constraint violation
psycopg2.errors.ForeignKeyViolation: insert or update on table "powers" 
violates foreign key constraint "powers_powerset_id_fkey"
```

**Diagnosis:**
```sql
-- Check missing references
SELECT DISTINCT p.powerset_id 
FROM staging_powers p
LEFT JOIN powersets ps ON p.powerset_id = ps.id
WHERE ps.id IS NULL;

-- Check import order
SELECT table_name, count(*) 
FROM information_schema.tables 
WHERE table_schema = 'public'
GROUP BY table_name;
```

**Solutions:**

1. **Import in correct order:**
   ```bash
   # Always follow dependency order
   just import-archetypes data/archetypes.json
   just import-powersets data/powersets.json
   just import-powers data/powers.json  # Depends on powersets
   ```

2. **Fix missing references:**
   ```python
   # Add to importer to skip invalid references
   def validate_references(self, data):
       if data.get('powerset_id'):
           exists = self.db.query(Powerset).filter_by(
               id=data['powerset_id']
           ).count() > 0
           if not exists:
               self.logger.warning(f"Skipping: powerset {data['powerset_id']} not found")
               return False
       return True
   ```

### Duplicate Key Errors

**Symptoms:**
```
ERROR: Duplicate key value violates unique constraint
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "powers_pkey"
```

**Solutions:**

1. **Use upsert logic:**
   ```bash
   # Clear before import
   just import-clear powers data/powers.json
   ```

2. **Check for duplicates in source:**
   ```bash
   # Find duplicates in JSON
   jq '[.[] | .id] | group_by(.) | map(select(length > 1))' data/powers.json
   ```

## Memory Issues

### Out of Memory Errors

**Symptoms:**
```
ERROR: Out of memory
MemoryError: Unable to allocate array
Process killed by OOM killer
```

**Memory Monitoring:**

```mermaid
graph TD
    subgraph "Memory Usage Breakdown"
        Total[Total RAM<br/>16 GB]
        System[System<br/>2 GB]
        Import[Import Process<br/>8 GB]
        Cache[Cache<br/>4 GB]
        Free[Free<br/>2 GB]
    end
    
    Total --> System
    Total --> Import
    Total --> Cache
    Total --> Free
    
    style Total fill:#2196f3
    style Import fill:#f44336
    style Cache fill:#ff9800
    style Free fill:#4caf50
```

**Diagnosis:**
```bash
# Monitor memory usage
watch -n 1 'free -h'

# Check import process memory
ps aux | grep import

# System memory info
just system-memory

# Check swap usage
swapon -s
```

**Solutions:**

1. **Reduce memory usage:**
   ```bash
   # Smaller batch size
   just i12-import data.json --batch-size 1000 --memory-limit 2.0
   
   # Enable streaming mode
   just i12-import data.json --streaming
   ```

2. **Increase system memory:**
   ```bash
   # Add swap space (temporary fix)
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Clear caches:**
   ```bash
   # Clear application cache
   just cache-clear
   
   # Clear system cache (Linux)
   sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
   ```

## Data Validation Errors

### Schema Validation Failures

**Symptoms:**
```
ERROR: Schema validation failed
Required field 'name' missing
Invalid type for field 'level': expected int, got string
```

**Validation Tools:**

```python
# validate_schema.py
import json
import jsonschema

def validate_power_schema(data):
    schema = {
        "type": "object",
        "required": ["id", "name", "powerset_id"],
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "name": {"type": "string", "minLength": 1},
            "powerset_id": {"type": "integer", "minimum": 1},
            "level_available": {"type": "integer", "minimum": 1, "maximum": 50}
        }
    }
    
    try:
        jsonschema.validate(data, schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, str(e)
```

**Solutions:**

1. **Fix data types:**
   ```python
   # Data cleaning script
   def clean_power_data(power):
       # Convert string numbers to integers
       if isinstance(power.get('level_available'), str):
           power['level_available'] = int(power['level_available'])
       
       # Set defaults for missing optional fields
       power.setdefault('description', '')
       power.setdefault('icon', None)
       
       return power
   ```

2. **Validate before import:**
   ```bash
   # Run validation only
   just import-validate data/powers.json
   
   # Generate validation report
   just validate-report data/ > validation_report.txt
   ```

## Diagnostic Tools

### Built-in Diagnostics

```bash
# Comprehensive system check
just diagnose-all

# Import-specific diagnostics
just import-diagnose

# Database diagnostics
just db-diagnose

# Performance diagnostics
just perf-diagnose
```

### Custom Diagnostic Script

```python
#!/usr/bin/env python
"""
Comprehensive import diagnostics script
"""
import sys
import json
import psutil
import psycopg2
from pathlib import Path

def check_system():
    """Check system resources."""
    print("=== System Check ===")
    
    # Memory
    mem = psutil.virtual_memory()
    print(f"Memory: {mem.percent}% used ({mem.used / 1024**3:.1f} GB / {mem.total / 1024**3:.1f} GB)")
    
    # CPU
    cpu = psutil.cpu_percent(interval=1)
    print(f"CPU: {cpu}% used")
    
    # Disk
    disk = psutil.disk_usage('/')
    print(f"Disk: {disk.percent}% used ({disk.used / 1024**3:.1f} GB / {disk.total / 1024**3:.1f} GB)")
    
    return mem.available > 1024**3  # At least 1GB free

def check_database():
    """Check database connection and status."""
    print("\n=== Database Check ===")
    
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cur = conn.cursor()
        
        # Check version
        cur.execute("SELECT version();")
        print(f"PostgreSQL: {cur.fetchone()[0].split(',')[0]}")
        
        # Check table counts
        cur.execute("""
            SELECT schemaname, tablename, n_live_tup 
            FROM pg_stat_user_tables 
            ORDER BY n_live_tup DESC 
            LIMIT 10;
        """)
        
        print("\nTop tables by row count:")
        for row in cur.fetchall():
            print(f"  {row[1]}: {row[2]:,} rows")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        return False

def check_import_files(path):
    """Check import files."""
    print(f"\n=== Import Files Check ===")
    print(f"Path: {path}")
    
    required_files = [
        'archetypes.json',
        'powersets.json', 
        'powers.json',
        'enhancements.json',
        'recipes.json',
        'salvage.json'
    ]
    
    missing = []
    for file in required_files:
        file_path = Path(path) / file
        if file_path.exists():
            size = file_path.stat().st_size / 1024**2  # MB
            print(f"  ✓ {file}: {size:.1f} MB")
        else:
            print(f"  ✗ {file}: MISSING")
            missing.append(file)
    
    return len(missing) == 0

def main():
    """Run all diagnostics."""
    print("Mids Hero Web Import Diagnostics")
    print("=" * 40)
    
    results = {
        'system': check_system(),
        'database': check_database(),
        'files': check_import_files(sys.argv[1] if len(sys.argv) > 1 else 'data/json')
    }
    
    print("\n=== Summary ===")
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{check}: {status}")
    
    if all(results.values()):
        print("\nAll checks passed! System ready for import.")
        return 0
    else:
        print("\nSome checks failed. Please resolve issues before importing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Emergency Procedures

### Import Process Hung

**Symptoms:**
- Import progress stuck at same percentage
- No CPU/disk activity
- Process appears frozen

**Recovery Steps:**

```mermaid
flowchart TD
    Hung[Import Hung]
    Check[Check Process<br/>Status]
    Active{Still<br/>Active?}
    
    Kill[Kill Process]
    Recover[Check Recovery<br/>Point]
    Resume[Resume from<br/>Last Position]
    Restart[Restart from<br/>Beginning]
    
    Hung --> Check
    Check --> Active
    Active -->|Yes| Kill
    Active -->|No| Recover
    Kill --> Recover
    Recover --> Resume
    Recover --> Restart
    
    style Hung fill:#f44336
    style Kill fill:#ff5252
    style Resume fill:#4caf50
    style Restart fill:#ff9800
```

**Commands:**
```bash
# 1. Check if process is actually hung
just import-status --detailed

# 2. If truly hung, kill the process
pkill -f "import"

# 3. Check last successful position
just import-recovery-info

# 4. Resume from last position
just i12-import-resume data.json 150000

# 5. Or restart with smaller batch
just i12-import data.json --batch-size 100
```

### Database Corruption

**Symptoms:**
- Inconsistent query results
- Unexpected errors during normal operations
- Data integrity check failures

**Recovery:**
```bash
# 1. Stop all import processes
just import-stop-all

# 2. Run integrity check
just db-integrity-check

# 3. If corruption detected, restore from backup
just db-restore-latest

# 4. Verify restoration
just validate-all-data

# 5. Resume normal operations
just import-health
```

### Complete System Recovery

**When all else fails:**

```bash
#!/bin/bash
# Full system recovery script

echo "Starting complete system recovery..."

# 1. Stop all services
systemctl stop midshero-api
systemctl stop postgresql

# 2. Backup current state (just in case)
tar -czf emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/lib/postgresql/

# 3. Reset database
sudo -u postgres dropdb midshero
sudo -u postgres createdb midshero

# 4. Restore from known good backup
just db-restore /backups/midshero_last_known_good.sql

# 5. Clear all caches
redis-cli FLUSHALL

# 6. Restart services
systemctl start postgresql
systemctl start midshero-api

# 7. Verify system health
just health-check-all

echo "Recovery complete. Please verify system functionality."
```

## Getting Help

If you cannot resolve an issue using this guide:

1. **Check logs:**
   ```bash
   tail -f logs/import_$(date +%Y%m%d).log
   journalctl -u midshero-import -f
   ```

2. **Generate diagnostic report:**
   ```bash
   just generate-diagnostic-report > diag_$(date +%Y%m%d_%H%M%S).txt
   ```

3. **Contact support** with:
   - Diagnostic report
   - Error messages
   - Steps to reproduce
   - System specifications

4. **Community resources:**
   - GitHub Issues: https://github.com/woodrowpearson/mids-hero-web/issues
   - Discord: #mids-hero-support
   - Wiki: https://wiki.midshero.com/troubleshooting