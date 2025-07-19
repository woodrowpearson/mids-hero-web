# Database Agent

Specialized agent for database-related tasks in the Mids Hero Web project.

## Core Responsibilities

- Database schema design and modifications
- Migration creation and management
- Data import pipeline development
- Query optimization
- Data validation

## Context Files

When working on database tasks, include:

- `.claude/shared/database-design.md`
- `.claude/epics/epic-2-data-import.md`
- `backend/app/models.py`
- `backend/alembic/`

## Key Commands

```bash
# Migration operations
just db-migrate                          # Run migrations
just db-migration-create "description"   # Create migration
just db-reset                           # Reset database

# Database access
docker-compose exec db psql -U midsuser midsdb

# Run Python with database context
cd backend && uv run python
>>> from app.database import SessionLocal
>>> from app.models import *
>>> db = SessionLocal()
```

## Current Tasks

1. **Create initial migrations** from existing models
2. **Design import schema** for .mhd files
3. **Implement data validation** framework
4. **Optimize query performance** with indexes

## Data Import Focus

The critical blocker is obtaining game data files. While waiting:

1. Set up import framework structure
2. Create validation test suite
3. Design incremental update system
4. Prepare performance benchmarks

## Schema Best Practices

1. **Normalization**: Maintain 3NF for data integrity
2. **Indexing**: Index foreign keys and search fields
3. **JSONB Usage**: Use for flexible/varied data only
4. **Constraints**: Enforce at database level
5. **Naming**: Use snake_case consistently

## Migration Guidelines

1. Always review auto-generated migrations
2. Include both upgrade and downgrade
3. Test on development first
4. Never modify migrations after deployment
5. Document breaking changes

## Performance Considerations

- Use EXPLAIN ANALYZE for slow queries
- Batch operations for imports
- Consider materialized views for calculations
- Monitor connection pool usage
- Profile with realistic data volumes

## Import Pipeline Architecture

```python
class ImportPipeline:
    """Data import workflow"""

    phases = [
        "parse",      # Extract from .mhd
        "transform",  # Convert to models
        "validate",   # Check integrity
        "load",       # Insert to database
        "verify"      # Post-import checks
    ]
```

## Validation Checklist

After any data operation:

- [ ] Foreign key constraints satisfied
- [ ] Required fields populated
- [ ] Unique constraints maintained
- [ ] Data ranges reasonable
- [ ] Relationships intact

## Common Issues

1. **Migration conflicts**: Rebase and regenerate
2. **Import failures**: Check constraints and types
3. **Performance**: Analyze query plans
4. **Deadlocks**: Review transaction scope

## Resources

- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/)
- [PostgreSQL Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)continue
