# Deprecated Modules (Archived 2025-11-13)
Last Updated: 2025-11-19 20:27:56 UTC

## Why Deprecated

These modules were part of a custom context-loading system built before:
- Anthropic native context loading
- Official Claude Code plugin system
- Superpowers plugin workflow

## Superseded By

- **Modules** → Native Claude Code context loading + official plugins
- **Context-map.json** → Native automatic context management
- **Custom triggers** → Claude decides what context to load

## Historical Value

These modules contain useful reference information that has been:
- Extracted to `docs/` where still relevant
- Superseded by newer documentation
- Preserved here for historical reference

## Migration

**Database Module**:
- Schema reference → `backend/app/models.py` (authoritative source)
- See also: Alembic migrations in `backend/alembic/versions/`

**API Module**:
- Specification → OpenAPI/Swagger docs (auto-generated at http://localhost:8000/docs)
- Guide → `backend/README.md` and `backend/api/README.md`

**Frontend Module**:
- Architecture → `docs/frontend/architecture.md`
- Epic breakdown → `docs/frontend/epic-breakdown.md`
- Guide → `frontend/README.md`

**Import Module**:
- Commands → `backend/app/data_import/README.md`
- Usage → `CLAUDE.md` import commands section

**Testing Module**:
- Guide → Covered in test files and `backend/README.md`
- Test structure → `backend/tests/` and `frontend/src/__tests__/`

## Do Not Use

These files should not be loaded or referenced in current development.
Use the locations listed in Migration section instead.

## Contents

All original module files preserved as-is for historical reference:
- `api/` - API documentation and guides
- `database/` - Database schema and migration guides
- `frontend/` - Frontend architecture and patterns
- `import/` - Data import procedures
- `testing/` - Testing strategies and guides
