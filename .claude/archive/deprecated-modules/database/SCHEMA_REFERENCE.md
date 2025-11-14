# Database Schema Reference
Last Updated: 2025-08-25 00:00:00 UTC

## Entity Relationship Diagram

```
┌─────────────┐
│ archetypes  │
│ (5 records) │
└──────┬──────┘
       │ 1:N
┌──────▼──────────┐         ┌──────────────────┐
│   powersets     │         │ enhancement_sets │
│ (106 records)   │         │  (300+ records)  │
└──────┬──────────┘         └────────┬─────────┘
       │ 1:N                         │ 1:N
┌──────▼──────────┐         ┌────────▼─────────┐
│    powers       │         │  enhancements    │
│ (2000+ records) │         │ (1900+ records)  │
└─────────────────┘         └──────────────────┘
```

## Complete Table Schemas

### archetypes
```sql
CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,      -- "Blaster", "Controller"
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    primary_category VARCHAR(50),           -- "hero", "villain"  
    secondary_category VARCHAR(50),
    hit_points_base INTEGER,
    inherent_powers JSON,                   -- ["Rest", "Sprint"]
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### powersets
```sql
CREATE TABLE powersets (
    id SERIAL PRIMARY KEY,
    archetype_id INTEGER REFERENCES archetypes(id),
    name VARCHAR(50) NOT NULL,              -- "Fire_Blast"
    display_name VARCHAR(100) NOT NULL,     -- "Fire Blast"
    description TEXT,
    powerset_type VARCHAR(20),              -- "primary", "secondary", "pool", "epic"
    power_order JSON,                       -- [1, 1, 2, 6, 8, 12, 18, 26, 32]
    icon_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(archetype_id, name, powerset_type)
);
```

### powers
```sql
CREATE TABLE powers (
    id SERIAL PRIMARY KEY,
    powerset_id INTEGER REFERENCES powersets(id),
    name VARCHAR(100) NOT NULL,
    internal_name VARCHAR(255) UNIQUE,      -- "Blaster_Ranged.Fire_Blast.Flares"
    display_name VARCHAR(100),
    description TEXT,
    level_available INTEGER NOT NULL,
    power_type VARCHAR(50),                 -- "attack", "defense", "support"
    target_type VARCHAR(50),                -- "self", "enemy", "ally", "location"
    
    -- Numeric stats (DECIMAL for precision)
    accuracy DECIMAL(5,2) DEFAULT 1.0,
    damage_scale DECIMAL(8,3),
    endurance_cost DECIMAL(6,2),
    recharge_time DECIMAL(8,2),
    activation_time DECIMAL(5,2),
    interrupt_time DECIMAL(5,2),
    range_feet INTEGER,
    radius_feet INTEGER,
    arc_degrees INTEGER,
    max_targets INTEGER,
    
    -- Complex JSON data
    effects JSON,                           -- [{"type": "damage", "scale": 1.0, ...}]
    effect_groups JSON,                     -- Grouped/summarized effects
    enhancements_allowed JSON,              -- ["accuracy", "damage", "recharge"]
    
    -- Requirements and restrictions
    requires_line_of_sight BOOLEAN DEFAULT true,
    modes_required JSON,                    -- ["flying", "hovering"]
    modes_disallowed JSON,                  -- ["phased"]
    ai_report TEXT,
    
    -- Display
    icon_path VARCHAR(255),
    display_order INTEGER,
    display_info JSON,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_power_powerset_level ON powers(powerset_id, level_available);
CREATE INDEX idx_power_type_level ON powers(power_type, level_available);
CREATE INDEX idx_power_internal_name ON powers(internal_name);
CREATE INDEX idx_power_effects ON powers USING GIN (effects);
CREATE INDEX idx_power_effect_groups ON powers USING GIN (effect_groups);
```

### enhancement_sets
```sql
CREATE TABLE enhancement_sets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    min_level INTEGER DEFAULT 1,
    max_level INTEGER DEFAULT 50,
    allowed_origins JSON,                   -- ["magic", "technology", "mutation"]
    set_type VARCHAR(50),                   -- "invention", "archetype", "special"
    
    -- Set bonuses at different piece counts
    bonuses JSON,                           -- {"2": [...], "3": [...], "6": [...]}
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### enhancements
```sql
CREATE TABLE enhancements (
    id SERIAL PRIMARY KEY,
    set_id INTEGER REFERENCES enhancement_sets(id),
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    slot_type VARCHAR(50),                  -- "accuracy", "damage", "defense_buff"
    
    -- Enhancement values
    schedule VARCHAR(20),                   -- "A", "B", "C", "D"
    modifier_values JSON,                   -- {"accuracy": 0.265, "endurance": 0.265}
    
    -- Requirements
    min_level INTEGER DEFAULT 1,
    max_level INTEGER DEFAULT 50,
    unique_per_build BOOLEAN DEFAULT false,
    
    -- Crafting (for IOs)
    recipe_id INTEGER,
    salvage_required JSON,
    influence_cost INTEGER,
    
    icon_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### import_logs
```sql
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    import_type VARCHAR(50),                -- "i12_powers", "mhd_build"
    source_file VARCHAR(255),
    game_version VARCHAR(50),
    records_processed INTEGER,
    records_imported INTEGER,
    errors INTEGER,
    import_data JSON,                       -- Additional metadata
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_import_logs_type ON import_logs(import_type);
CREATE INDEX idx_import_logs_date ON import_logs(started_at);
```

## JSON Field Structures

### Power Effects
```json
{
  "effects": [
    {
      "type": "Damage",
      "damage_type": "Fire",
      "scale": 1.32,
      "target": "Enemy",
      "chance": 1.0,
      "duration": 0,
      "stacking": "replace",
      "flags": ["unresistable", "critical"]
    }
  ]
}
```

### Enhancement Set Bonuses
```json
{
  "bonuses": {
    "2": [
      {"type": "Defense", "attribute": "AoE", "value": 0.025}
    ],
    "3": [
      {"type": "Endurance", "value": 0.03}
    ],
    "6": [
      {"type": "Recharge", "value": 0.10}
    ]
  }
}
```

## Materialized Views

### power_build_summary
```sql
CREATE MATERIALIZED VIEW power_build_summary AS
SELECT 
    p.id,
    p.name,
    p.internal_name,
    p.display_name,
    p.powerset_id,
    ps.name as powerset_name,
    ps.archetype_id,
    a.name as archetype_name,
    p.level_available,
    p.power_type,
    p.accuracy,
    p.damage_scale,
    p.endurance_cost,
    p.recharge_time
FROM powers p
JOIN powersets ps ON p.powerset_id = ps.id
JOIN archetypes a ON ps.archetype_id = a.id;

CREATE INDEX idx_pbs_archetype ON power_build_summary(archetype_id, level_available);
CREATE INDEX idx_pbs_powerset ON power_build_summary(powerset_id, level_available);
```

---
*Model files located in `backend/app/models/`*