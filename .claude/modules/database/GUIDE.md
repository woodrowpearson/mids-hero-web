# Database Module Guide

## Quick Reference

**Connection**: `postgresql://postgres:postgres@localhost:5432/mids_web`

**Key Commands**:
```bash
just db-migrate                    # Apply migrations
just db-migration-create "desc"    # Create migration
just db-shell                     # PostgreSQL shell
just db-reset                     # Reset database
```

## Core Tables & Models

### Main Entities
```
archetypes (5 records)          → backend/app/models/archetype.py
├── powersets (106 records)     → backend/app/models/powerset.py
│   └── powers (2,000+ records) → backend/app/models/power.py
└── enhancements (1,900+)       → backend/app/models/enhancement.py
    └── enhancement_sets (300+) → backend/app/models/enhancement_set.py
```

### Key Models

**Power** (`backend/app/models/power.py`):
```python
class Power(Base):
    __tablename__ = "powers"
    
    # Identity
    id: int (PK)
    name: str
    internal_name: str (unique)
    
    # Relationships
    powerset_id: int (FK)
    
    # Stats
    level_available: int
    accuracy: Decimal
    damage_scale: Decimal
    endurance_cost: Decimal
    recharge_time: Decimal
    
    # Complex data
    effects: JSON
    effect_groups: JSON
```

**Indexes**: 
- Composite: `(powerset_id, level_available)`
- GIN: `effects`, `effect_groups` (PostgreSQL)
- Covering: Build queries optimization

## Common Database Operations

### High-Performance Import
```python
# Use I12StreamingParser for 360K+ records
from app.data_import import I12StreamingParser

parser = I12StreamingParser(
    database_url=DATABASE_URL,
    batch_size=1000,      # Records per transaction
    chunk_size=5000,      # File reading chunk
    memory_limit_gb=1.0   # Auto garbage collection
)
parser.import_data(file_path)
```

### Efficient Queries
```python
# Use PowerCacheService for cached queries
from app.services.power_cache import get_power_cache

cache = get_power_cache()
power = cache.get_power_by_id(session, power_id)  # Multi-tier cache
powers = cache.get_powers_by_powerset(session, powerset_id, level_filter=20)
```

### Direct Session Usage
```python
from app.database import get_db

# Context manager
with get_db() as db:
    powers = db.query(Power).filter(
        Power.powerset_id == 1,
        Power.level_available <= 20
    ).all()

# Dependency injection (FastAPI)
@app.get("/powers")
def get_powers(db: Session = Depends(get_db)):
    return db.query(Power).all()
```

## Migration Best Practices

### Create Migration
```bash
# Auto-generate from model changes
just db-migration-create "add power prerequisites"

# Review generated file
cat backend/alembic/versions/*_add_power_prerequisites.py

# Apply migration
just db-migrate
```

### Migration Template
```python
def upgrade() -> None:
    # Add index for performance
    op.create_index(
        'idx_power_name_search',
        'powers',
        ['name'],
        postgresql_using='gin',
        postgresql_ops={'name': 'gin_trgm_ops'}
    )
    
    # Add column with default
    op.add_column('powers',
        sa.Column('is_epic', sa.Boolean(), 
                  server_default='false', nullable=False)
    )

def downgrade() -> None:
    op.drop_index('idx_power_name_search')
    op.drop_column('powers', 'is_epic')
```

## Performance Optimization

### Query Optimization
```python
# ❌ N+1 Query Problem
for powerset in db.query(Powerset).all():
    powers = db.query(Power).filter_by(powerset_id=powerset.id).all()

# ✅ Eager Loading
powersets = db.query(Powerset)\
    .options(selectinload(Powerset.powers))\
    .all()

# ✅ Join Query
results = db.query(Powerset, func.count(Power.id))\
    .join(Power)\
    .group_by(Powerset.id)\
    .all()
```

### Materialized Views
```sql
-- Power build summary for fast queries
CREATE MATERIALIZED VIEW power_build_summary AS
SELECT p.*, ps.name as powerset_name, a.name as archetype_name
FROM powers p
JOIN powersets ps ON p.powerset_id = ps.id
JOIN archetypes a ON ps.archetype_id = a.id;

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY power_build_summary;
```

### Connection Pooling
```python
# backend/app/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Persistent connections
    max_overflow=40,       # Maximum overflow
    pool_pre_ping=True,    # Verify connections
    pool_recycle=3600      # Recycle after 1 hour
)
```

## Import System Details

### Batch Processing Pattern
```python
def batch_insert(records: List[Dict], batch_size: int = 1000):
    session = SessionLocal()
    try:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            session.bulk_insert_mappings(Power, batch)
            session.commit()
            
            # Memory management
            if i % 10000 == 0:
                session.close()
                session = SessionLocal()
                gc.collect()
    finally:
        session.close()
```

### Import Progress Tracking
```sql
-- import_logs table
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    import_type VARCHAR(50),
    source_file VARCHAR(255),
    records_processed INTEGER,
    records_imported INTEGER,
    errors INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## Troubleshooting

### Common Issues

**"relation does not exist"**:
```bash
just db-migrate  # Run migrations
```

**Performance degradation**:
```bash
just db-shell
ANALYZE;  -- Update statistics
VACUUM;   -- Clean up dead rows
```

**Connection pool exhausted**:
```python
# Check active connections
SELECT count(*) FROM pg_stat_activity 
WHERE datname = 'mids_web';

# Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'mids_web' 
AND state = 'idle' 
AND state_change < NOW() - INTERVAL '10 minutes';
```

### Debug Commands
```bash
# Check current schema version
just db-status

# View table structure
just db-shell
\d powers
\di *idx*  -- List all indexes

# Query performance
EXPLAIN ANALYZE SELECT * FROM powers WHERE powerset_id = 1;
```

---
*For schema details, see `.claude/modules/database/schema-reference.md`*