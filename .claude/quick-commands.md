# Quick Commands Reference

Essential commands for Mids Hero Web development.

## Most Used Commands

```bash
just              # Show all commands
just dev          # Start everything
just test         # Run all tests
just quality      # Check code quality
just ucp "msg"    # Commit and push
```

## Development

```bash
just quickstart   # Initial setup
just health       # Environment check
just dev          # Start Docker services
just frontend-dev # Frontend only
just backend-dev  # Backend only
```

## Testing

```bash
just test         # All tests
just test-watch   # Watch mode
just lint         # Run linters
just lint-fix     # Auto-fix issues
just type-check   # Type checking
just format       # Format code
```

## Database

```bash
just db-migrate   # Run migrations
just db-migration-create "name"  # New migration
just db-reset     # Reset database
just db-seed      # Load sample data
```

## Docker

```bash
just docker-up    # Start containers
just docker-down  # Stop containers
just docker-logs  # View logs
just docker-clean # Clean everything
```

## Code Quality

```bash
just quality      # All checks
just lint         # Linting only
just lint-fix     # Fix issues
just type-check   # Type check
just format       # Format code
```

## Context Management

```bash
just token-usage      # Check tokens
just context-health   # Health check
just context-prune    # Clean context
just progress-update  # Update progress
```

## Utilities

```bash
just clean        # Clean artifacts
just build        # Production build
just api-docs     # Open API docs
just epic-status  # Show progress
```

## Git Shortcuts

```bash
just ucp "message"    # Add, commit, push
```

## Troubleshooting

```bash
just health       # Check environment
just install      # Reinstall deps
just clean        # Clean artifacts
just docker-clean # Reset Docker
```

## Environment Variables

Key variables in `.env`:
```bash
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
API_HOST=0.0.0.0
API_PORT=8000
```

## Port Reference

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## File Locations

- Backend code: `backend/app/`
- Frontend code: `frontend/src/`
- Database models: `backend/app/models.py`
- API routes: `backend/app/routers/`
- React components: `frontend/src/components/`
- Migrations: `backend/alembic/versions/`

## Common Workflows

### Add New API Endpoint
1. Create schema in `backend/app/schemas.py`
2. Add route in `backend/app/routers/`
3. Write tests in `backend/tests/`
4. Update API client in `frontend/src/services/`

### Add Frontend Feature
1. Create component in `frontend/src/components/`
2. Add to router if needed
3. Connect to API service
4. Write component tests
5. Update documentation

### Database Change
1. Modify `backend/app/models.py`
2. `just db-migration-create "description"`
3. Review migration file
4. `just db-migrate`
5. Update schemas and API