# CLAUDE.md - Mids Hero Web Development Guide

This file provides essential guidance for AI-assisted development of the Mids Hero Web project.

## 🚀 Quick Start

```bash
# Set project root and navigate
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"

# Development workflow
just quickstart     # Initial setup
just dev           # Start all services
just health        # Run health checks
just test          # Run all tests
```

## 📋 Project Overview

Mids Hero Web is a modern web-based character build planner for City of Heroes, replacing the legacy Windows Forms application with a React/FastAPI stack.

### Core Functionality
- Character archetype and powerset selection
- Power selection with level/prerequisite validation  
- Enhancement slotting with set bonus calculations
- Build statistics computation and validation
- Import/export of character builds
- Real-time updates from game servers

### Tech Stack
- **Frontend**: React 19 + TypeScript, Material-UI (planned)
- **Backend**: FastAPI + Python 3.11, SQLAlchemy, PostgreSQL
- **DevOps**: Docker, uv package manager, GCP (planned)

## 🛠️ Development Standards

### Critical Rules
1. **Always use just** for all operations - NEVER run commands directly
2. **Token limits**: Keep contexts under 50k tokens, alert at 90k/128k
3. **Run `just health`** before starting any work session
4. **Update progress** after completing tasks: `just progress-update`
5. **Use /clear** between unrelated tasks to prevent context pollution

### Code Standards
- **Python**: Follow PEP 8, use type hints, async/await patterns
- **TypeScript**: Strict mode enabled, proper interface definitions
- **Database**: Always use migrations, never modify schema directly
- **API**: RESTful conventions, Pydantic schemas for validation
- **Testing**: TDD approach, maintain >80% coverage

## 📊 Current Development State

Following the 6-epic roadmap (see `.claude/epics/` for details):

**✅ Epic 1: Project Setup** - Complete
- Git repository initialized
- Docker environment configured
- Backend/frontend scaffolds created
- Database models defined

**🚧 Epic 2: Data Import** - In Progress (CRITICAL BLOCKER)
- Need City of Heroes game data files
- Database migrations pending
- Import scripts to be created

**📋 Epic 3-6**: Backend API, Frontend, Deployment, Optimization - Planned

## 🔧 Common Workflows

### Daily Development
```bash
just dev            # Start all services
just db-migrate     # Run pending migrations
just test-watch     # Run tests in watch mode
just lint-fix       # Auto-fix code issues
```

### Database Operations
```bash
just db-migration-create "description"  # Create new migration
just db-reset                          # Reset database
just db-seed                           # Load sample data
```

### Code Quality
```bash
just quality        # Run all checks
just format         # Format code
just type-check     # Type checking
```

## 📁 Project Structure

```
mids-hero-web/
├── .claude/              # AI development context
│   ├── agents/          # Specialized AI agents
│   ├── epics/           # Roadmap epic details
│   └── shared/          # Shared context
├── backend/             # FastAPI application
│   ├── app/            # Application code
│   └── pyproject.toml  # Dependencies
├── frontend/            # React application  
├── scripts/            # Helper scripts
├── docker-compose.yml  # Local development
└── justfile           # Development commands
```

## ⚠️ Important Notes

### Current Blockers
1. **No game data**: Epic 2 requires City of Heroes .mhd files
2. **No migrations**: Database schema exists but not migrated
3. **Mock data only**: API returns placeholders

### Development Priorities
1. Obtain game data files (contact Homecoming team)
2. Create and run database migrations
3. Implement data import pipeline
4. Replace mock API responses with real data

## 🤖 AI Agent Guidelines

When creating specialized agents:
- **Database Agent**: Focus on migrations, models, import scripts
- **API Agent**: Handle endpoint creation, schemas, testing
- **Frontend Agent**: Component development, state management
- **DevOps Agent**: Docker, deployment, monitoring

Always reference `.claude/agents/` for agent-specific context.

## 📚 Documentation

- **Roadmap**: `.claude/epics/` - Detailed epic breakdowns
- **Architecture**: `.claude/shared/architecture.md`
- **API Design**: `.claude/shared/api-standards.md`
- **Database**: `.claude/shared/database-design.md`

---

Remember: This is a community project recreating a beloved tool. Quality and accuracy are paramount - the City of Heroes community depends on precise build calculations.