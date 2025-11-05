# Filtered Data Migration Plan - Option B (Clean Break)

**Status**: Schema Design Complete
**Date**: 2025-11-04
**Decision**: Option B - Clean break from MHD data, rebuild schema for filtered_data

## Executive Summary

The filtered_data in `/filtered_data/` cannot be imported with the current database schema and import code. This plan implements Option B: a clean break that drops the old schema, creates a new one optimized for filtered_data, and builds new importers.

---

## Completed: Gap Analysis

### Data Structure Comparison

| Category | Files | Current Schema | New Schema Needed |
|----------|-------|----------------|-------------------|
| Archetypes | 21 | Basic fields only | +9 JSON/rich fields |
| Boost Sets | 228 | Basic set info | +5 JSON fields for bonuses |
| Enhancements | ~1,200+ | Basic bonuses | +15 fields for attuned/catalyst |
| Powers | 5,773 | Partial support | Complete JSON storage |
| Powersets | ~200+ | Missing | New table needed |
| Tables | 20 | None | New table needed |
| Tags | 300 | None | New table needed |
| Exclusion Groups | 16 | None | New table needed |
| Recharge Groups | 4 | None | New table needed |

### Key Findings

1. **Archetype Data**: filtered_data includes:
   - Complete `attrib_base` (100+ attributes per archetype)
   - `defiant_scale`, `class_requires`, `restrictions`
   - `primary_category`, `secondary_category` for powerset linking
   - Display help text and localization keys

2. **Enhancement Data**: filtered_data includes:
   - Complete boost set bonus structures
   - Attuned/catalyzation system
   - Unique groups and restrictions
   - Slot requirements (formulas)
   - Computed metadata for all variants

3. **Power Data**: filtered_data has EXTREMELY complex structure:
   - Nested effects with child_effects
   - Templates for each effect
   - PvP vs PvE variations
   - Complex expressions and formulas
   - FX data for visual effects
   - 600-900+ lines of JSON per power

4. **Supporting Data**:
   - **Tables**: Archetype-specific modifier tables (arrays of floats)
   - **Tags**: Power tagging system for interactions
   - **Exclusion Groups**: Mutually exclusive powers
   - **Recharge Groups**: Powers sharing recharge timers

---

## Completed: New Schema Design

Created `backend/app/models_new.py` with:

### New Models

1. **Archetype** (Extended)
   - Added: `attrib_base` (JSON), `defiant_scale`, `class_requires`, `restrictions`
   - Added: `primary_category`, `secondary_category`, `power_pool_category`, `epic_pool_category`
   - Added: `display_help`, `display_short_help`, `default_rank`, `is_villain`

2. **ArchetypeModifierTable** (NEW)
   - Links to archetype
   - Stores named modifier tables (e.g., "Melee_Damage")
   - Values stored as JSON array

3. **Powerset** (Extended)
   - Added: `display_fullname`, `display_help`, `display_short_help`
   - Added: `source_file`, `requires`
   - Added: `power_names`, `power_display_names`, `power_short_helps`, `available_level`

4. **Power** (Major Redesign)
   - Added: `full_name` (unique), `display_fullname`, `short_name`
   - Added: Many extracted fields for common queries
   - **Critical**: `power_data` JSON column stores complete power JSON
   - Added: `powerset_name` (denormalized), `archetypes`, `tags`
   - Added: `exclusion_groups`, `recharge_groups`

5. **EnhancementSet** (Extended)
   - Added: `group_name`, `conversion_groups`
   - Added: `boost_lists`, `bonuses`, `computed` (all JSON)

6. **Enhancement** (Major Redesign)
   - Added: `computed_name`, `boostset_name` (denormalized)
   - Added: `slot_requires`, `ignores_level_differences`, `bonuses_ignore_exemplar`
   - Added: `combinable`, `tradeable`, `account_bound`
   - Added: `boostable`, `attuned`, `catalyzes_to`, `superior_scales`
   - Added: `is_proc`, `is_unique`, `restricted_ats`, `unique_group`
   - Added: `aspects`, `global_bonuses`
   - Added: Level fields: `min_slot_level`, `min_bonus_level`, `only_at_50`

7. **Tag** (NEW)
   - Stores tag name
   - `bears`: Powers that have this tag
   - `affects`: Powers affected by this tag

8. **ExclusionGroup** (NEW)
   - Group name
   - Array of mutually exclusive powers

9. **RechargeGroup** (NEW)
   - Group name
   - Array of powers sharing recharge timer

### Design Decisions

1. **JSON Storage Strategy**:
   - Simple lookups: Extract to columns (e.g., `accuracy`, `recharge_time`)
   - Complex nested data: Store as JSON (e.g., `power_data`, `attrib_base`)
   - Balance between query performance and schema simplicity

2. **Denormalization**:
   - `Enhancement.boostset_name` - Avoid joins for common queries
   - `Power.powerset_name` - Same reason
   - Trade-off: Slight data duplication for major query speed improvement

3. **Complete Data Preservation**:
   - Power's `power_data` JSON stores EVERYTHING from filtered_data
   - No data loss during import
   - Can always extract new fields later if needed

---

## Migration Steps

### Step 1: Database Backup and Drop (Manual)

```bash
# Backup existing database (if needed)
pg_dump mids_web > backup_before_migration.sql

# Drop and recreate database
dropdb mids_web
createdb mids_web
```

### Step 2: Replace Models

```bash
# Backup old models
mv backend/app/models.py backend/app/models_old.py

# Use new models
mv backend/app/models_new.py backend/app/models.py
```

### Step 3: Create Initial Migration

```bash
# Generate Alembic migration from models
cd backend
alembic revision --autogenerate -m "Clean break: New schema for filtered_data"

# Review the generated migration
# Apply migration
alembic upgrade head
```

### Step 4: Build New Importers

Create in `backend/app/data_import_filtered/`:

1. **`base_filtered_importer.py`**
   - Base class similar to existing BaseImporter
   - But optimized for filtered_data JSON structure

2. **`archetype_importer.py`**
   - Direct JSON mapping from filtered_data
   - Compute hit_points from attrib_base if needed
   - Import archetype modifier tables

3. **`powerset_importer.py`** (NEW)
   - Import index.json files from power directories
   - Link to archetypes via categories

4. **`enhancement_set_importer.py`**
   - Import boost_sets/*.json
   - Handle bonuses, boost_lists, computed data

5. **`enhancement_importer.py`**
   - Iterate through each boost_set's computed.boost_infos
   - Create Enhancement record per variant
   - Handle catalyzation relationships

6. **`power_importer.py`**
   - Import individual power JSON files
   - Store complete JSON in power_data column
   - Extract commonly-queried fields to columns
   - Link to powersets, archetypes

7. **`tag_importer.py`** (NEW)
   - Import tags/*.json files
   - Simple structure: tag name + bears/affects arrays

8. **`exclusion_group_importer.py`** (NEW)
   - Import exclusion_groups/*.json files

9. **`recharge_group_importer.py`** (NEW)
   - Import recharge_groups/*.json files

10. **`table_importer.py`** (NEW)
    - Import tables/*.json files
    - Create ArchetypeModifierTable records
    - Link named tables to archetypes

### Step 5: CLI Integration

Update `justfile` with new commands:

```makefile
# Import all filtered data
import-filtered-all:
    python -m backend.scripts.import_filtered_data --all

# Import by category
import-filtered-archetypes:
    python -m backend.scripts.import_filtered_data --archetypes

import-filtered-powersets:
    python -m backend.scripts.import_filtered_data --powersets

import-filtered-powers:
    python -m backend.scripts.import_filtered_data --powers

import-filtered-enhancements:
    python -m backend.scripts.import_filtered_data --enhancements

import-filtered-supporting:
    python -m backend.scripts.import_filtered_data --tags --exclusion-groups --recharge-groups --tables
```

### Step 6: Testing

Create test suite:

```bash
# Run import
just import-filtered-all

# Validate counts
psql mids_web -c "SELECT COUNT(*) FROM archetypes;"  # Expect: 15 player ATs
psql mids_web -c "SELECT COUNT(*) FROM enhancement_sets;"  # Expect: 228
psql mids_web -c "SELECT COUNT(*) FROM enhancements;"  # Expect: ~1,200+
psql mids_web -c "SELECT COUNT(*) FROM powers;"  # Expect: 5,773
psql mids_web -c "SELECT COUNT(*) FROM powersets;"  # Expect: ~200+
psql mids_web -c "SELECT COUNT(*) FROM tags;"  # Expect: 300
psql mids_web -c "SELECT COUNT(*) FROM exclusion_groups;"  # Expect: 16
psql mids_web -c "SELECT COUNT(*) FROM recharge_groups;"  # Expect: 4

# Validate data integrity
psql mids_web -c "SELECT name, display_name FROM archetypes LIMIT 5;"
psql mids_web -c "SELECT full_name, display_name, recharge_time FROM powers LIMIT 10;"
```

### Step 7: Update API Endpoints

Update existing API endpoints to use new schema:

- `GET /api/archetypes` - Use new fields
- `GET /api/archetypes/{id}` - Include attrib_base
- `GET /api/powersets` - New endpoint structure
- `GET /api/powers` - Use new fields + power_data
- `GET /api/enhancement-sets` - Include bonuses
- `GET /api/enhancements` - New filtering by attuned/catalyst

### Step 8: Remove Old Code

Delete old MHD-related code:

```bash
# Old parsers
rm -rf backend/app/parsers/mhd_parser.py

# Old import commands
rm -rf backend/app/commands/import_mhd.py
rm -rf backend/scripts/import_i12_data.py

# Legacy data structures
rm -rf scripts/import_json_data.py  # Only handles AttribMod/TypeGrades
```

---

## Implementation Order

### Phase 1: Foundation (Current Session)
- ✅ Complete gap analysis
- ✅ Design new schema
- ✅ Create models_new.py
- 🔄 Create migration plan document (this file)

### Phase 2: Database Setup
- Replace models.py with new version
- Generate and apply Alembic migration
- Verify empty schema created successfully

### Phase 3: Core Importers
- Build base filtered importer
- Build archetype importer + table importer
- Build enhancement set/enhancement importers
- Test core data import

### Phase 4: Power System
- Build powerset importer
- Build power importer
- Test power import (most complex)

### Phase 5: Supporting Data
- Build tag/exclusion/recharge importers
- Complete import pipeline
- Full validation tests

### Phase 6: API Updates
- Update existing endpoints
- Add new endpoints for new data
- Integration testing

### Phase 7: Cleanup
- Remove old code
- Update documentation
- Close Epic 2.5/2.6 issues

---

## Estimated Effort

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| Phase 1 | Foundation | ✅ 4 hours (Complete) |
| Phase 2 | Database Setup | 1 hour |
| Phase 3 | Core Importers | 6-8 hours |
| Phase 4 | Power System | 8-10 hours |
| Phase 5 | Supporting Data | 3-4 hours |
| Phase 6 | API Updates | 4-6 hours |
| Phase 7 | Cleanup | 2-3 hours |
| **Total** | | **28-36 hours** |

---

## Next Steps

**Immediate**:
1. Review this migration plan
2. Decide: Proceed with Phase 2, or adjust approach?
3. If proceeding: Replace models.py and generate migration

**Questions for User**:
- Should we proceed immediately with Phase 2?
- Any concerns about the schema design?
- Want to start with a specific importer as proof of concept?

---

## Success Criteria

- [ ] All 6,363 filtered_data files successfully imported
- [ ] Zero data loss (all JSON structures preserved)
- [ ] Import completes in < 5 minutes
- [ ] Query performance acceptable (<100ms for common queries)
- [ ] All API endpoints working with new schema
- [ ] Old MHD code completely removed
- [ ] Tests passing

---

## Rollback Plan

If migration fails:

```bash
# Restore old database
psql -U postgres -d mids_web < backup_before_migration.sql

# Restore old models
mv backend/app/models_old.py backend/app/models.py
mv backend/app/models.py backend/app/models_new.py

# Rollback migration
alembic downgrade -1
```

---

**Document Status**: ✅ Complete
**Next Action**: Await user approval to proceed with Phase 2
