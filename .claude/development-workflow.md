}# Development Workflow

This document outlines the standard development workflow for the Mids Hero Web project, integrating `just` commands and Claude custom commands.

## 🎯 Starting a New Work Session

### 1. Environment Setup & Health Check (REQUIRED)

```bash
# Set project root and navigate
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"

# REQUIRED: Run health check before any work
just health          # Verify environment
just dev             # Start all services
```

### 2. Session Management (RECOMMENDED)

Use Claude session commands to track your work:

```bash
# Start a new development session
/project:session-start issue-123-feature-name

# Or use the debug session script
.claude/commands/debug-session.sh
```

### 3. Before Starting Work

- Check current epic status: `just epic-status`
- Review blockers in CLAUDE.md
- Update local branches: `git pull origin main`
- Review import system status: `just import-status`

## 📝 Development Cycle

### Creating Feature Branch

```bash
# Create feature branch following naming convention
git checkout -b feature/issue-123-description
# Or for epic work
git checkout -b feature/epic-2-component-name
```

### Active Development

```bash
# Run tests while coding
just test-watch

# Fix linting issues as you go
just lint-fix

# Check code quality frequently
just quality

# Update session progress
/project:session-update "Implemented authentication logic"
```

### Committing Changes

#### Option 1: Quick Commit & Push

```bash
# Using just command (recommended)
just ucp "feat: add authentication middleware"

# Or using Claude custom command
.claude/commands/ucp.sh "feat: add authentication middleware"
```

#### Option 2: Full Progress Update & Push

```bash
# Complete workflow: update progress, commit, push (RECOMMENDED)
just update-progress

# Or use the script directly
.claude/commands/update-progress.sh
```

### Code Quality Gates

Before pushing or creating PR:

```bash
just quality         # Run all checks
just test           # Ensure tests pass
just build          # Verify build works
just type-check     # TypeScript/Python type checking
```

## 🔧 Data Import Workflows (Epic 2)

### I12 Power Data Import

```bash
# Full import with monitoring
just i12-import data/i12_powers.json

# Resume from failure
just i12-import-resume data/i12_powers.json 50000

# Validate before import
just i12-validate data/i12_powers.json

# Check import health
just import-health
```

### Generic Data Import

```bash
# Import all data types from directory
just import-all data/exports/

# Import specific types
just import-archetypes data/archetypes.json
just import-powersets data/powersets.json
just import-enhancements data/enhancements.json

# Clear and reimport
just import-clear powers data/powers.json
```

### Import System Monitoring

```bash
# Check system status
just import-status      # Overall status
just import-stats       # Database record counts
just cache-stats        # Cache performance
just perf-bench         # Run benchmarks
```

## 📋 Epic-Specific Workflows

### Epic 2: Data Import (Current - 95% Complete)

1. Run import health check: `just import-health`
2. Import I12 data: `just i12-import file.json`
3. Monitor progress and handle errors
4. Verify with: `just import-stats`
5. Document in session: `/project:session-update`

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

## 🐛 Debugging

### Quick Debug Session

```bash
# Start comprehensive debug session
.claude/commands/debug-session.sh
```

### Backend Debugging

```bash
# View logs
just logs backend       # Or: docker-compose logs -f backend

# Interactive Python shell
just backend-shell      # Or: docker-compose exec backend python

# Database queries
just db-shell          # Or: docker-compose exec db psql -U postgres mids_web

# Check import errors
just import-health
```

### Frontend Debugging

- Browser DevTools for React
- React Developer Tools extension
- Network tab for API calls
- Console for runtime errors

## Performance Monitoring

### Backend Performance

- FastAPI automatic metrics at `/metrics`
- Database query profiling enabled in dev
- Async operation monitoring

### Frontend Performance

- React DevTools Profiler
- Lighthouse audits
- Bundle size analysis

## 🚀 Pre-Deployment Workflow

### Final Checks

```bash
# Run comprehensive quality checks
just quality
just test
just build

# Update progress and documentation
.claude/commands/update-progress.sh

# End development session
/project:session-end
```

### Deployment Checklist

Before deploying:

1. [ ] All tests passing: `just test`
2. [ ] No linting errors: `just lint`
3. [ ] Type checking passes: `just type-check`
4. [ ] Database migrations tested: `just db-migrate`
5. [ ] API documentation updated
6. [ ] Frontend build optimized: `just build`
7. [ ] Import system healthy: `just import-health`
8. [ ] Environment variables configured
9. [ ] Docker images built and tagged
10. [ ] Health checks verified: `just health`

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

## 💡 Best Practices

### Session Management

1. **Always start work sessions**: Use `/project:session-start` or `just health`
2. **Update progress regularly**: Use `/project:session-update` during work
3. **End sessions properly**: Use `/project:session-end` when done

### Commit Workflow

1. **Quick commits**: `just ucp "message"` or `.claude/commands/ucp.sh`
2. **Full updates**: `.claude/commands/update-progress.sh`
3. **Conventional commits**:
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation
   - `test:` Test additions
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks
   - `perf:` Performance improvements

### Branch Management

1. **Naming convention**: `type/issue-number-description`
   - `feature/issue-168-i12-handler`
   - `fix/issue-203-auth-bug`
   - `docs/epic-2-import-guide`

### Code Quality

1. **Pre-push checklist**:

   ```bash
   just quality        # All checks
   just test          # Test suite
   just lint-fix      # Auto-fix issues
   ```

2. **Import system checks** (when working on data):
   ```bash
   just import-health  # System health
   just import-stats   # Verify counts
   just cache-stats    # Performance
   ```

### Token Management

1. **Monitor usage**: Check context size regularly
2. **Use /clear**: Between unrelated tasks
3. **Keep focused**: One issue per session

## 🔄 Workflow Integration with CLAUDE.md

This workflow is designed to work with CLAUDE.md requirements:

- Always run `just health` at session start
- Use pre-approved commands in `.claude/commands/`
- Update progress after completing tasks
- Follow the just command patterns
- Reference documentation in `.claude/` directory
