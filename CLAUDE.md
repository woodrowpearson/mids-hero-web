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

## 🚀 Claude Custom Commands

For efficiency, use pre-approved custom commands in `.claude/commands/`:

```bash
.claude/commands/update-progress.sh    # Full update, commit, push workflow
.claude/commands/ucp.sh "message"      # Quick commit and push  
.claude/commands/debug-session.sh      # Debug environment setup
```

### 📥 Data Import Commands

**Generic Import (All Parsers):**
```bash
just import-all data-dir               # Import all data types
just import-type powers file.json      # Import specific type  
just import-archetypes file.json       # Import archetypes
just import-powersets file.json        # Import powersets
just import-enhancements file.json     # Import enhancements
just import-clear type file.json       # Clear and import
```

**High-Performance I12 Import:**
```bash
just i12-import file.json              # Import 360K+ power records
just i12-import-resume file.json 50000 # Resume from record 50000
just i12-validate file.json            # Validate without importing

# Direct CLI usage (backend/scripts/import_i12_data.py)
python scripts/import_i12_data.py data.json --batch-size 1000 --memory-limit 1.0
python scripts/import_i12_data.py data.json --resume-from 50000 --clear-cache
```

**System Status & Performance:**
```bash
just import-health                     # Full system health check
just import-status                     # Import system status
just import-stats                      # Database record counts
just cache-stats                       # Cache performance
just perf-bench                        # I12 benchmarks
just perf-test-all                     # All performance tests
```

See `.claude/commands/README.md` for detailed usage.

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

**✅ Epic 1: Project Setup** - Complete (All 20 GitHub issues closed)

- Git repository and project structure established
- React 19 frontend scaffold with TypeScript
- FastAPI backend with proper Python structure  
- Docker environment configuration
- GitHub Actions CI/CD pipeline
- AI-powered workflows with @claude integration

**🚧 Epic 2: Data Import** - In Progress (90% Complete)

- ✅ Database schema design completed
- ✅ Comprehensive SQLAlchemy models implemented  
- ✅ Alembic migration framework set up
- ✅ Initial database migration created and applied
- ✅ Database schema deployment successful
- ✅ I12 streaming parser for 360K+ power data (#168)
- ✅ Multi-tier caching system (LRU + Redis)
- ✅ Database performance optimizations
- ✅ CLI import tool with resume capability
- 🚧 MidsReborn MHD integration (remaining work)
- 🚧 Full data pipeline completion

**📋 Epic 3-6**: Backend API, Frontend, Deployment, Optimization - Planned

## 🔧 Common Workflows

### Daily Development

```bash
just dev            # Start all services
just db-migrate     # Run pending migrations
just test-watch     # Run tests in watch mode
just lint-fix       # Auto-fix code issues
```

### Data Import Operations

```bash
just import-all data-dir                # Import all data types
just import-health                      # System health check
just import-stats                       # Database record counts
just i12-import data.json               # High-performance power data
just cache-stats                        # Check cache performance
just db-optimize                        # Database optimizations
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

1. **MidsReborn integration**: Epic 2 requires MidsReborn MHD parser completion  
2. **I12 data files**: Need actual I12 power data files for production import

### Recent Achievements

1. **I12 Streaming Parser**: Production-ready parser for 360K+ power records
   - `StreamingJsonReader`: Memory-efficient chunked JSON processing  
   - `PowerDataProcessor`: I12 format transformation with validation
   - `I12StreamingParser`: Main orchestrator with progress tracking
2. **Performance Optimization**: <100ms queries, <1GB memory usage, multi-tier caching
   - `PowerCacheService`: Multi-tier LRU + Redis caching for power queries
   - Database optimizations via migration `0236d1f741c9`
3. **Database Optimization**: Composite indexes, GIN indexes, materialized views
   - Import logs table for tracking large data imports
   - Power build summary materialized view for fast queries

## 🤖 AI Agent Guidelines

When creating specialized agents:

- **Database Agent**: Focus on migrations, models, import scripts
- **API Agent**: Handle endpoint creation, schemas, testing
- **Frontend Agent**: Component development, state management
- **DevOps Agent**: Docker, deployment, monitoring

Always reference `.claude/agents/` for agent-specific context.

## 📚 Documentation

- **Quick Commands**: `.claude/quick-commands.md` - Essential commands reference
- **Custom Commands**: `.claude/commands/` - Pre-approved automated workflows
- **Roadmap**: `.claude/epics/` - Detailed epic breakdowns  
- **Architecture**: `.claude/shared/architecture.md`
- **Database**: `.claude/shared/database-design.md`

## Important

- Use `fd` instead of `find` - NEVER use `find` command [[memory:905944]]
- Use `trash` instead of `rm -rf` - NEVER use `rm -rf` [[memory:648882]]

---

Remember: This is a community project recreating a beloved tool. Quality and accuracy are paramount - the City of Heroes community depends on precise build calculations.
