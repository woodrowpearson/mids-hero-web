# Development Workflow

This document outlines the modern development workflow for the Mids Hero Web project using Claude Code with progressive context loading and automated workflow management.

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

### 2. Context Loading & Task Declaration

**Tell Claude what you're working on** to load the right context:

```bash
# For Epic 2 completion (loads import + database modules)
"I need to complete Epic 2 data import tasks"

# For Epic 3 API work (loads api + database modules)  
"I need to work on Epic 3 API development"

# For database work (loads database module)
"I need to work on database migrations"

# For frontend work (loads frontend module)
"I need to build React components"
```

### 3. Branch Creation & Issue Selection

```bash
# Create feature branch for specific issue
git checkout -b feature/issue-153-data-import

# Pull latest changes
git pull origin main

# Check project status
just health
```

## 📝 Development Cycle

### Active Development

```bash
# Run tests while coding (if available)
just test-watch

# Fix linting issues as you go
just lint-fix

# Check code quality frequently
just quality
```

### Working with Claude Code

**Tell Claude your specific task:**
```bash
# Be specific about what you want to implement
"I want to implement GitHub issue #153 - Execute data import and populate database"

"I want to create the authentication API endpoints for Epic 3"

"I want to fix the database migration issue in issue #xyz"
```

**Claude will automatically:**
- Load relevant context (database, import, api, frontend modules)
- Apply appropriate tool restrictions based on task type
- Monitor token usage and suggest context optimization
- Log all activities for session tracking

### Committing Changes

**Quick Commit & Push:**
```bash
# Using just command (recommended)
just ucp "feat: add authentication middleware"
```

**Full Progress Update & Push:**
```bash
# Complete workflow: update progress, commit, push
just update-progress
```

### Code Quality Gates

Before pushing or creating PR:

```bash
just quality         # Run all checks
just test           # Ensure tests pass
just build          # Verify build works
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

### Epic 2: Data Import Completion (95% Complete - 5% Remaining)

**Remaining Tasks:**
- Issue #153: Execute data import and populate database
- Issue #170: Document data import process

**Workflow:**
```bash
# 1. Declare Epic 2 work to Claude
"I need to complete Epic 2 data import tasks"

# 2. Check system status
just import-health

# 3. Execute data import (main remaining task)
just i12-import file.json

# 4. Verify completion
just import-stats

# 5. Document and close issues
```

### Epic 3: Backend API Development (Ready to Start)

**Phase 1 (Can start immediately):**
```bash
# 1. Declare Epic 3 work to Claude  
"I need to work on Epic 3 API development"

# 2. Implement authentication system
# 3. Create Pydantic schemas
# 4. Build basic CRUD endpoints
# 5. Set up testing framework
```

**Phase 2 (After Epic 2 completion):**
- Build calculation engine
- Advanced search and filtering
- Import/Export integration
- Performance optimization

### Epic 2.5: Context Management (Optional Infrastructure)

**Claude Code workflow improvements - not required for Epic 3:**
- Session summarization
- Agent-based context quarantine  
- RAG documentation indexing

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

### Backend Debugging

```bash
# View logs
just logs backend

# Interactive Python shell
just backend-shell

# Database queries
just db-shell

# Check import errors
just import-health
```

### Frontend Debugging

- Browser DevTools for React
- React Developer Tools extension
- Network tab for API calls
- Console for runtime errors

### Claude Code Debugging

```bash
# Check context health
# (Context validation happens automatically via hooks)

# Monitor token usage
# (Automatic warnings at 90K tokens)

# Use /clear between unrelated tasks to prevent context pollution
```

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
just update-progress
```

### Deployment Checklist

Before deploying:

1. [ ] All tests passing: `just test`
2. [ ] No linting errors: `just lint`
3. [ ] Database migrations tested: `just db-migrate`
4. [ ] API documentation updated
5. [ ] Frontend build optimized: `just build`
6. [ ] Import system healthy: `just import-health`
7. [ ] Environment variables configured
8. [ ] Docker images built and tagged
9. [ ] Health checks verified: `just health`

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

### Working with Claude Code

1. **Declare your task clearly**: 
   ```bash
   "I need to work on Epic 2 data import completion"
   "I want to implement GitHub issue #153"
   "I need to create authentication API endpoints"
   ```

2. **Let Claude load appropriate context**:
   - Epic 2 work → Loads import + database modules
   - Epic 3 work → Loads api + database modules
   - Database work → Loads database module only
   - Frontend work → Loads frontend module only

3. **Use /clear between unrelated tasks** to prevent context pollution

### Commit Workflow

1. **Quick commits**: `just ucp "message"`
2. **Full updates**: `just update-progress`
3. **Conventional commits**:
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation
   - `test:` Test additions
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks
   - `perf:` Performance improvements

### Branch Management

**Naming convention**: `feature/issue-number-description`
- `feature/issue-153-data-import`
- `feature/epic-3-authentication`
- `fix/issue-203-auth-bug`

### Code Quality

**Pre-push checklist**:
```bash
just quality        # All checks
just test          # Test suite
just lint-fix      # Auto-fix issues
```

**Data import checks** (Epic 2 work):
```bash
just import-health  # System health
just import-stats   # Verify counts
```

### Context Management

1. **Progressive loading**: Claude automatically loads only relevant modules
2. **Token monitoring**: Automatic warnings at 90K tokens
3. **Activity logging**: All tool usage automatically tracked
4. **One task per session**: Maintains focus and context clarity

## 🔄 Modern Claude Code Integration

This workflow leverages Claude Code's advanced features:

- **Progressive context loading** based on task declaration
- **Automated hook system** for validation and logging
- **Tool loadouts** that restrict tools based on task type
- **Token management** with automatic warnings and optimization
- **Activity tracking** for session continuity

### Key Changes from Legacy Workflow

❌ **Removed obsolete features**:
- `/project:session-start` commands (not needed)
- `.claude/commands/debug-session.sh` (deprecated)
- Manual context management
- Complex session tracking scripts

✅ **New modern approach**:
- Task declaration for automatic context loading
- Automatic hook-based activity logging
- Progressive module loading system
- Simplified just-based commands
