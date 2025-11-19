# Troubleshooting Guide
Last Updated: 2025-11-19 20:27:56 UTC

## 🚨 Quick Fixes

### Backend Won't Start
```bash
# Check PostgreSQL
docker-compose ps
docker-compose up -d db

# Verify .env
cat backend/.env

# Check port 8000
lsof -i :8000
```

### Database Issues
```bash
# Connection errors
just db-status          # Check migration status
just db-migrate        # Apply migrations
just db-reset          # Nuclear option

# Performance issues
just db-shell
VACUUM ANALYZE;        # Update statistics
```

### Import Failures
```bash
# Check health first
just import-health

# Common fixes
just import-clear powers data/imported/powers.json  # Clear bad data
just cache-stats                           # Check cache
python scripts/import_i12_data.py --clear-cache
```

### Frontend Build Errors
```bash
# Clean rebuild
trash frontend/node_modules
cd frontend && npm install
npm run build
```

### Python/uv Issues
```bash
# Update uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clear cache
uv cache clean

# Resync
cd backend && uv sync
```

## 🔍 Debugging Commands

### View Logs
```bash
just logs backend          # Backend logs
docker-compose logs -f     # All services
```

### Check Processes
```bash
docker-compose ps         # Container status
ps aux | grep python     # Python processes
ps aux | grep node       # Node processes
```

### Database Queries
```bash
just db-shell

-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '10 minutes';

-- Table sizes
SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Memory Issues
```bash
# Check Docker memory
docker stats

# Python memory usage
python -c "import psutil; print(f'{psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB')"
```

## 📊 Performance Diagnostics

### Slow Queries
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Explain query plan
EXPLAIN ANALYZE SELECT * FROM powers WHERE powerset_id = 1;
```

### Import Performance
```bash
# Test with smaller batch
python scripts/import_i12_data.py data.json \
    --batch-size 100 \
    --verbose

# Monitor progress
tail -f backend/i12_import.log
```

## 🛠️ Reset Procedures

### Full Database Reset
```bash
just db-reset
just db-migrate
just import-all data/exports/
```

### Cache Reset
```bash
# Redis cache
docker-compose restart redis

# Application cache
python scripts/import_i12_data.py --clear-cache
```

### Docker Reset
```bash
docker-compose down -v
docker-compose up -d
just health
```

## 🚑 Emergency Fixes

### Disk Space
```bash
# Check space
df -h

# Clean Docker
docker system prune -a

# Clean pip cache
uv cache clean
```

### Port Conflicts
```bash
# Find process on port
lsof -i :8000
kill -9 <PID>

# Change port in docker-compose.yml
```

### Corrupted Git
```bash
# Reset to clean state
git fetch origin
git reset --hard origin/main
```

---
*For specific error messages, search GitHub issues or ask in Discord*
