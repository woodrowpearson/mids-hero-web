# Database Module Guide (Condensed)

## Quick Reference

### Connection
```bash
# Database URL format
postgresql://postgres:devpassword@localhost:5432/mids_hero

# Access via just commands
just db-shell      # psql access
just db-migrate    # Run migrations
just db-reset      # Full reset
```

### Core Tables & Models

#### 1. **archetypes** - Character classes
```python
# SQLAlchemy model: backend/app/models/archetype.py
id, name (unique), display_name, description
primary_group, secondary_group  # damage/control/defense/support
hit_points_base, hit_points_max
```

#### 2. **powersets** - Power groupings
```python
# SQLAlchemy model: backend/app/models/powerset.py
id, name, display_name, description
archetype_id (FK), powerset_type  # primary/secondary/pool/epic
UNIQUE(name, archetype_id, powerset_type)
```

#### 3. **powers** - Individual abilities
```python
# SQLAlchemy model: backend/app/models/power.py
id, name, display_name, description, powerset_id (FK)
level_available, power_type, target_type
# Stats: accuracy, damage_scale, endurance_cost, recharge_time
effects (JSONB)  # Flexible effect storage
```

#### 4. **enhancements** - Power improvements
```python
# SQLAlchemy model: backend/app/models/enhancement.py
id, name, enhancement_type  # IO/SO/DO/TO/HamiO/set_piece
set_id (FK optional), level_min/max
# Bonuses: accuracy, damage, endurance, recharge, defense, resistance
other_bonuses (JSONB)
```

#### 5. **enhancement_sets** & **set_bonuses**
```python
# Sets provide bonuses when multiple pieces slotted
enhancement_sets: id, name (unique), min/max_level
set_bonuses: set_id (FK), pieces_required (2-6), bonus_type, bonus_amount
```

### Key Relationships
```
Archetype -> Powerset -> Power -> Enhancement
                            └─> Power Prerequisites
Enhancement -> Enhancement Set -> Set Bonuses
```

## Common Operations

### 1. Import Data
```python
# Use bulk operations for performance
from sqlalchemy import insert

# Batch insert with conflict handling
stmt = insert(Power).values(power_data)
stmt = stmt.on_conflict_do_update(
    index_elements=['name', 'powerset_id'],
    set_=dict(updated_at=func.now())
)
db.execute(stmt)
```

### 2. Query Patterns
```python
# Get archetype with powersets
archetype = db.query(Archetype)\
    .options(joinedload(Archetype.powersets))\
    .filter_by(name="Blaster")\
    .first()

# Find powers by level
powers = db.query(Power)\
    .filter(Power.level_available <= 10)\
    .order_by(Power.level_available)\
    .all()

# Enhancement compatibility check
compat = db.query(PowerEnhancementCompatibility)\
    .filter_by(power_id=power_id, enhancement_type="damage")\
    .first()
```

### 3. Performance Tips
```python
# Use indexes effectively
from sqlalchemy import Index

# Composite index for common queries
Index('idx_power_search', Power.powerset_id, Power.level_available)

# JSONB queries
db.query(Power).filter(
    Power.effects['damage_type'].astext == 'fire'
)

# Bulk operations
db.bulk_insert_mappings(Power, power_list)
db.bulk_update_mappings(Enhancement, update_list)
```

## Migration Best Practices

### Creating Migrations
```bash
# Always use descriptive names
just db-migration-create "add_power_effects_jsonb"

# In migration file:
def upgrade():
    op.add_column('powers', 
        sa.Column('effects', sa.JSON(), nullable=True))
    op.create_index('idx_power_effects', 'powers', 
        [sa.text("(effects->>'damage_type')")])

def downgrade():
    op.drop_index('idx_power_effects')
    op.drop_column('powers', 'effects')
```

### Data Migrations
```python
# Use bulk_insert for data migrations
from alembic import op
from sqlalchemy import table, column

def upgrade():
    # Create temp table reference
    power_table = table('powers',
        column('id'), column('effects'))
    
    # Update in batches
    conn = op.get_bind()
    for batch in get_batches(conn, 1000):
        op.bulk_update(power_table, batch)
```

## Performance Optimization

### 1. Indexes (Already in schema)
- Primary keys: Auto-indexed
- Foreign keys: All indexed
- Search fields: name columns indexed
- Composite: (archetype_id, powerset_type)

### 2. Query Optimization
```sql
-- Use EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM powers WHERE powerset_id = 1;

-- Materialized views for complex queries
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_powerset_summary;
```

### 3. Connection Pooling
```python
# In backend/app/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Import System

### High-Performance I12 Import
```python
# StreamingJsonReader for large files
from backend.app.data_import.parsers.i12 import I12StreamingParser

parser = I12StreamingParser(
    db_session=db,
    batch_size=1000,
    memory_limit_gb=1.0
)
parser.parse_file("powers.json", resume_from=50000)
```

### Import Tracking
```sql
-- Check import status
SELECT import_type, source_file, records_processed, 
       completed_at - started_at as duration
FROM import_logs 
ORDER BY created_at DESC;
```

## Troubleshooting

### Common Issues
1. **Constraint violations**: Check UNIQUE constraints
2. **FK errors**: Ensure parent records exist
3. **JSONB queries slow**: Add GIN index
4. **Migration fails**: Check for data dependencies

### Debug Commands
```bash
just db-shell                    # Direct psql access
just import-health              # System health check
just cache-stats               # Cache performance
just db-table-counts           # Quick record counts
```

## Key Files
- Models: `backend/app/models/*.py`
- Migrations: `backend/alembic/versions/`
- Import: `backend/app/data_import/`
- Database config: `backend/app/database.py`