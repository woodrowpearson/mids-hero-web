# Phase 2 Migration Instructions

## Status
✅ **Completed**: Schema replacement (models.py)
⏸️ **Pending**: Migration generation and application (requires database)

## What Was Done

1. **Backed up old models**: `backend/app/models_old.py`
2. **Activated new schema**: Replaced `models.py` with new filtered_data schema
3. **New models include**:
   - Extended: `Archetype`, `Powerset`, `Power`, `EnhancementSet`, `Enhancement`
   - New: `ArchetypeModifierTable`, `Tag`, `ExclusionGroup`, `RechargeGroup`

## Next Steps (Requires Database Environment)

### Prerequisites
- PostgreSQL database running on `localhost:5432`
- Database `mids_web` created
- Python environment with `uv` and dependencies installed

### Commands to Run

```bash
# Step 1: Ensure database is running
docker compose up -d db
# OR
pg_ctl -D /path/to/data start

# Step 2: Create/reset database (OPTIONAL - for clean start)
# WARNING: This drops all existing data!
dropdb mids_web 2>/dev/null || true
createdb mids_web

# Step 3: Generate Alembic migration
cd backend
uv run alembic revision --autogenerate -m "Clean break: New schema for filtered_data"

# Step 4: Review the generated migration
# Check: backend/alembic/versions/<hash>_clean_break_new_schema_for_filtered_data.py
# Verify all tables are included:
# - archetypes (extended)
# - archetype_modifier_tables (NEW)
# - powersets (extended)
# - powers (major redesign)
# - enhancement_sets (extended)
# - enhancements (major redesign)
# - tags (NEW)
# - exclusion_groups (NEW)
# - recharge_groups (NEW)
# - builds (unchanged)
# - build_powers (unchanged)
# - build_enhancements (unchanged)
# - import_logs (unchanged)

# Step 5: Apply migration
uv run alembic upgrade head

# Step 6: Verify schema
psql mids_web -c "\d archetypes"
psql mids_web -c "\d archetype_modifier_tables"
psql mids_web -c "\d tags"
psql mids_web -c "\d exclusion_groups"
psql mids_web -c "\d recharge_groups"
psql mids_web -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
# Should show 13 tables total

# Step 7: Proceed to Phase 3
# See: .claude/docs/filtered-data-import-progress.md
```

## Important Notes

1. **Breaking Change**: This is a clean break from the old schema
2. **Old importers will break**: They use the old model structure
3. **API endpoints may break**: They reference old model fields
4. **Expected behavior**: This is intentional - we're rebuilding for filtered_data

## Rollback (If Needed)

```bash
# Restore old models
cp backend/app/models_old.py backend/app/models.py

# Revert migration (if applied)
cd backend
uv run alembic downgrade -1
```

## File Changes Summary

- ✅ `backend/app/models.py` - Now contains new schema (600+ lines)
- ✅ `backend/app/models_old.py` - Backup of old schema
- 📋 Migration file - To be generated in environment with database

---

**Phase 2 Progress**: 50% complete (schema ready, migration pending)
**Next Action**: Run migration generation in database environment
**Updated**: 2025-11-05
