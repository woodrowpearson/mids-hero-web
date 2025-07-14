# Development Workflow

This document outlines the standard development workflow for the Mids Hero Web project.

## Daily Development Flow

### 1. Start Your Day
```bash
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"
just health          # Verify environment
just dev             # Start all services
```

### 2. Before Starting Work
- Check current epic status: `just epic-status`
- Review blockers in CLAUDE.md
- Update local branches: `git pull origin main`

### 3. Development Cycle
```bash
# Create feature branch
git checkout -b feature/epic-2-data-import

# Make changes
just test-watch      # Run tests while coding
just lint-fix        # Fix issues as you go

# Commit frequently
just ucp "feat: add data import parser"
```

### 4. Code Quality Gates
Before pushing:
```bash
just quality         # Run all checks
just test           # Ensure tests pass
just build          # Verify build works
```

## Epic-Specific Workflows

### Epic 2: Data Import (Current)
1. Obtain .mhd files from Homecoming
2. Create parser in `backend/app/data_import/`
3. Write import scripts
4. Validate imported data
5. Document the process

### Epic 3: Backend API
1. Define Pydantic schemas
2. Implement CRUD operations
3. Add API endpoints
4. Write comprehensive tests
5. Update API documentation

### Epic 4: Frontend
1. Create component structure
2. Implement state management
3. Connect to backend API
4. Add responsive design
5. Test user workflows

## Testing Strategy

### Backend Testing
```bash
cd backend
uv run pytest tests/unit/          # Unit tests
uv run pytest tests/integration/    # Integration tests
uv run pytest tests/e2e/           # End-to-end tests
```

### Frontend Testing
```bash
cd frontend
npm test                           # Unit tests
npm run test:integration           # Integration tests
npm run test:e2e                  # E2E with Cypress
```

## Database Workflows

### Schema Changes
1. Modify models in `backend/app/models.py`
2. Create migration: `just db-migration-create "add power prerequisites"`
3. Review migration file
4. Apply: `just db-migrate`
5. Test rollback: `just db-reset`

### Data Import
1. Place .mhd files in `data/raw/`
2. Run parser: `python -m app.data_import.parser`
3. Validate: `python -m app.data_import.validator`
4. Load: `just db-seed`

## Debugging

### Backend Debugging
- Check logs: `docker-compose logs -f backend`
- Interactive shell: `docker-compose exec backend python`
- Database queries: `docker-compose exec db psql -U midsuser midsdb`

### Frontend Debugging
- Browser DevTools for React
- Redux DevTools for state
- Network tab for API calls

## Performance Monitoring

### Backend Performance
- FastAPI automatic metrics at `/metrics`
- Database query profiling enabled in dev
- Async operation monitoring

### Frontend Performance
- React DevTools Profiler
- Lighthouse audits
- Bundle size analysis

## Deployment Checklist

Before deploying:
1. [ ] All tests passing
2. [ ] No linting errors
3. [ ] Database migrations tested
4. [ ] API documentation updated
5. [ ] Frontend build optimized
6. [ ] Environment variables configured
7. [ ] Docker images built and tagged
8. [ ] Health checks verified

## Troubleshooting

### Common Issues

**Backend won't start**
- Check PostgreSQL is running
- Verify .env configuration
- Check port 8000 availability

**Frontend compilation errors**
- Clear node_modules: `trash frontend/node_modules`
- Reinstall: `cd frontend && npm install`

**Database connection issues**
- Verify PostgreSQL container: `docker-compose ps`
- Check credentials in .env
- Ensure migrations are applied

**Import errors with uv**
- Update uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Clear cache: `uv cache clean`
- Resync: `cd backend && uv sync`

## Best Practices

1. **Commit Messages**: Use conventional commits
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation
   - `test:` Test additions
   - `refactor:` Code refactoring

2. **Branch Naming**: `type/epic-number-description`
   - `feature/epic-2-import-parser`
   - `fix/epic-3-api-validation`
   - `docs/epic-1-setup-guide`

3. **Code Reviews**: Required for all PRs
   - Run `just quality` before requesting
   - Include tests for new features
   - Update documentation

4. **Token Management**: 
   - Run `just token-usage` regularly
   - Keep contexts focused
   - Use /clear between tasks