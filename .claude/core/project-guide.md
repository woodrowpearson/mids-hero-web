# Mids Hero Web - Core Project Guide

> **Purpose**: Modern web-based character build planner for City of Heroes, replacing legacy Windows Forms app.

## 🎯 Critical Rules

1. **ALWAYS use `just` commands** - Never run commands directly
2. **Run `just health` before starting** any work session
3. **Update progress**: `just update-progress` after completing tasks
4. **Token limits**: Stay under 90K, use `/clear` between tasks
5. **Follow `.claude/workflows/daily.md`** for standard procedures

## 🏗️ Tech Stack

- **Frontend**: React 19 + TypeScript
- **Backend**: FastAPI + Python 3.11, SQLAlchemy, PostgreSQL  
- **DevOps**: Docker, uv package manager, justfile commands

## 📍 Current Status

- **Epic 1**: ✅ Complete - Project setup, CI/CD, scaffolding
- **Epic 2**: 🚧 95% - Data import system (I12 parser done, MHD pending)
- **Epic 3-6**: 📋 Planned - API, Frontend, Deployment, Optimization

**Active Blockers**: MidsReborn MHD integration, production I12 data files

## 🚀 Quick Start

```bash
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"
just health          # Required health check
just dev            # Start all services
```

## 📁 Key Locations

- **Backend**: `/backend/app/` - FastAPI application
- **Frontend**: `/frontend/src/` - React application  
- **Database**: `/backend/alembic/` - Migrations
- **Import**: `/backend/app/data_import/` - Data parsers
- **Tests**: `/backend/tests/`, `/frontend/tests/`

## 🔧 Common Commands

```bash
# Development
just dev            # Start everything
just test          # Run tests
just lint-fix      # Fix code issues
just quality       # All quality checks

# Database  
just db-migrate    # Run migrations
just db-reset      # Reset database

# Import System
just import-health # Check import system
just i12-import    # Import power data
```

## 📚 Where to Find More

- **Database work**: Load `.claude/modules/database/`
- **Import work**: Load `.claude/modules/import/`
- **API work**: Load `.claude/modules/api/`
- **Frontend work**: Load `.claude/modules/frontend/`
- **Workflows**: See `.claude/workflows/`

## ⚠️ Important Gotchas

- Use `fd` not `find`, `trash` not `rm -rf`
- Check PR status before pushing
- Run quality checks before commits
- One issue per work session

---
*Keep this under 5K tokens. Load task-specific modules as needed.*