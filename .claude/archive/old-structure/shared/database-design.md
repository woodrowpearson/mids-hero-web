# Database Design

## Overview

The Mids Hero Web database is designed to store all City of Heroes game data and character builds with optimal performance and data integrity.

## Entity Relationship Diagram

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Archetype  │1────*│   Powerset   │1────*│    Power    │
└─────────────┘      └──────────────┘      └─────────────┘
                            │                      │
                            │                      │ can slot
                            │                      ▼
                            │              ┌─────────────┐
                            └─────────────▶│ Enhancement │
                                          └─────────────┘
                                                  │
                                                  │ part of
                                                  ▼
                                          ┌─────────────┐
                                          │  Set Bonus  │
                                          └─────────────┘
```

## Core Tables

### archetypes
Primary table for character classes (e.g., Blaster, Controller, Tanker)

```sql
CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    display_name VARCHAR(100),
    primary_group VARCHAR(50),    -- damage, control, defense, support
    secondary_group VARCHAR(50),  -- damage, control, defense, support
    hit_points_base INTEGER,
    hit_points_max INTEGER,
    inherent_power_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_archetype_name ON archetypes(name);
CREATE INDEX idx_archetype_groups ON archetypes(primary_group, secondary_group);
```

### powersets
Groupings of powers available to archetypes

```sql
CREATE TABLE powersets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    archetype_id INTEGER REFERENCES archetypes(id),
    powerset_type VARCHAR(20) NOT NULL, -- primary, secondary, pool, epic, incarnate
    icon_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, archetype_id, powerset_type)
);

-- Indexes
CREATE INDEX idx_powerset_archetype ON powersets(archetype_id);
CREATE INDEX idx_powerset_type ON powersets(powerset_type);
CREATE INDEX idx_powerset_name ON powersets(name);
```

### powers
Individual abilities within powersets

```sql
CREATE TABLE powers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    powerset_id INTEGER REFERENCES powersets(id),
    level_available INTEGER DEFAULT 1,
    power_type VARCHAR(50), -- attack, defense, control, support, travel
    target_type VARCHAR(50), -- self, ally, enemy, location
    -- Base stats
    accuracy DECIMAL(5,2) DEFAULT 1.0,
    damage_scale DECIMAL(5,2),
    endurance_cost DECIMAL(5,2),
    recharge_time DECIMAL(6,2),
    activation_time DECIMAL(4,2),
    range_feet INTEGER,
    radius_feet INTEGER,
    max_targets INTEGER,
    -- Effects stored as JSONB for flexibility
    effects JSONB,
    -- UI information
    icon_path VARCHAR(255),
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_power_powerset ON powers(powerset_id);
CREATE INDEX idx_power_level ON powers(level_available);
CREATE INDEX idx_power_type ON powers(power_type);
CREATE INDEX idx_power_name ON powers(name);
```

### power_prerequisites
Requirements for taking certain powers

```sql
CREATE TABLE power_prerequisites (
    id SERIAL PRIMARY KEY,
    power_id INTEGER REFERENCES powers(id),
    required_power_id INTEGER REFERENCES powers(id),
    required_level INTEGER,
    prerequisite_type VARCHAR(20), -- one_of, all_of
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_prereq_power ON power_prerequisites(power_id);
CREATE INDEX idx_prereq_required ON power_prerequisites(required_power_id);
```

### enhancements
Items that can be slotted into powers to improve them

```sql
CREATE TABLE enhancements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    enhancement_type VARCHAR(50), -- IO, SO, DO, TO, HamiO, set_piece
    set_id INTEGER, -- References enhancement_sets if part of a set
    level_min INTEGER DEFAULT 1,
    level_max INTEGER DEFAULT 50,
    -- Enhancement values as percentages
    accuracy_bonus DECIMAL(5,2),
    damage_bonus DECIMAL(5,2),
    endurance_bonus DECIMAL(5,2),
    recharge_bonus DECIMAL(5,2),
    defense_bonus DECIMAL(5,2),
    resistance_bonus DECIMAL(5,2),
    -- Additional bonuses as JSONB
    other_bonuses JSONB,
    unique_enhancement BOOLEAN DEFAULT FALSE,
    icon_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_enhancement_type ON enhancements(enhancement_type);
CREATE INDEX idx_enhancement_set ON enhancements(set_id);
CREATE INDEX idx_enhancement_level ON enhancements(level_min, level_max);
```

### enhancement_sets
Named sets that provide bonuses when multiple pieces are slotted

```sql
CREATE TABLE enhancement_sets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    description TEXT,
    min_level INTEGER DEFAULT 10,
    max_level INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### set_bonuses
Bonuses granted by slotting multiple enhancements from the same set

```sql
CREATE TABLE set_bonuses (
    id SERIAL PRIMARY KEY,
    set_id INTEGER REFERENCES enhancement_sets(id),
    pieces_required INTEGER NOT NULL, -- 2, 3, 4, 5, 6
    bonus_description TEXT,
    -- Bonus values
    bonus_type VARCHAR(50), -- defense, resistance, recharge, etc.
    bonus_amount DECIMAL(5,2),
    bonus_details JSONB, -- For complex bonuses
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_set_bonus_set ON set_bonuses(set_id);
CREATE INDEX idx_set_bonus_pieces ON set_bonuses(pieces_required);
```

### power_enhancement_compatibility
Which enhancements can be slotted in which powers

```sql
CREATE TABLE power_enhancement_compatibility (
    id SERIAL PRIMARY KEY,
    power_id INTEGER REFERENCES powers(id),
    enhancement_type VARCHAR(50), -- accuracy, damage, endurance, etc.
    allowed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(power_id, enhancement_type)
);

-- Indexes
CREATE INDEX idx_compat_power ON power_enhancement_compatibility(power_id);
CREATE INDEX idx_compat_type ON power_enhancement_compatibility(enhancement_type);
```

## Character Build Tables

### builds
Stored character builds

```sql
CREATE TABLE builds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    archetype_id INTEGER REFERENCES archetypes(id),
    primary_powerset_id INTEGER REFERENCES powersets(id),
    secondary_powerset_id INTEGER REFERENCES powersets(id),
    user_id INTEGER, -- Future user system
    level INTEGER DEFAULT 1,
    build_data JSONB, -- Complete build data
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_build_user ON builds(user_id);
CREATE INDEX idx_build_archetype ON builds(archetype_id);
CREATE INDEX idx_build_public ON builds(is_public);
```

### build_powers
Powers selected in a build

```sql
CREATE TABLE build_powers (
    id SERIAL PRIMARY KEY,
    build_id INTEGER REFERENCES builds(id) ON DELETE CASCADE,
    power_id INTEGER REFERENCES powers(id),
    level_taken INTEGER NOT NULL,
    slot_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_build_power_build ON build_powers(build_id);
CREATE INDEX idx_build_power_power ON build_powers(power_id);
```

### build_enhancements
Enhancements slotted in build powers

```sql
CREATE TABLE build_enhancements (
    id SERIAL PRIMARY KEY,
    build_power_id INTEGER REFERENCES build_powers(id) ON DELETE CASCADE,
    enhancement_id INTEGER REFERENCES enhancements(id),
    slot_number INTEGER NOT NULL,
    enhancement_level INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_build_enh_power ON build_enhancements(build_power_id);
CREATE INDEX idx_build_enh_enhancement ON build_enhancements(enhancement_id);
```

## Data Import Tables

### import_logs
Track data imports from game files

```sql
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    import_type VARCHAR(50), -- full, incremental, patch
    source_file VARCHAR(255),
    game_version VARCHAR(50),
    records_processed INTEGER,
    records_imported INTEGER,
    errors INTEGER,
    import_data JSONB, -- Detailed import statistics
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Optimization

### Materialized Views

```sql
-- Powerset with power count
CREATE MATERIALIZED VIEW mv_powerset_summary AS
SELECT 
    ps.id,
    ps.name,
    ps.archetype_id,
    ps.powerset_type,
    COUNT(p.id) as power_count,
    MIN(p.level_available) as min_level,
    MAX(p.level_available) as max_level
FROM powersets ps
LEFT JOIN powers p ON ps.id = p.powerset_id
GROUP BY ps.id;

-- Enhancement set completion bonuses
CREATE MATERIALIZED VIEW mv_set_bonus_summary AS
SELECT 
    es.id as set_id,
    es.name as set_name,
    COUNT(DISTINCT e.id) as total_pieces,
    json_agg(
        json_build_object(
            'pieces', sb.pieces_required,
            'bonus', sb.bonus_description,
            'type', sb.bonus_type,
            'amount', sb.bonus_amount
        ) ORDER BY sb.pieces_required
    ) as bonuses
FROM enhancement_sets es
JOIN enhancements e ON es.id = e.set_id
JOIN set_bonuses sb ON es.id = sb.set_id
GROUP BY es.id, es.name;
```

### Indexing Strategy

1. **Primary Keys**: All tables have auto-incrementing primary keys
2. **Foreign Keys**: Indexed for join performance
3. **Search Fields**: Name fields indexed for quick lookups
4. **Composite Indexes**: For common query patterns
5. **Partial Indexes**: For filtered queries

### Query Optimization Tips

1. Use prepared statements to avoid SQL injection
2. Batch inserts for data import operations
3. Use EXPLAIN ANALYZE for query optimization
4. Consider partitioning for large tables (future)
5. Regular VACUUM and ANALYZE operations

## Migration Strategy

1. All schema changes through Alembic migrations
2. Never modify production schema directly
3. Test migrations on development first
4. Include rollback procedures
5. Document breaking changes

## Backup and Recovery

1. Daily automated backups
2. Point-in-time recovery capability
3. Test restore procedures monthly
4. Keep backups for 30 days minimum
5. Separate backup for each game version