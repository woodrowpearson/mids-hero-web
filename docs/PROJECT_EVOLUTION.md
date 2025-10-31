# Mids Hero Web - Project Evolution
Last Updated: 2025-10-30

## Timeline Overview

This document traces the evolution of Mids Hero Web from initial concept to current state, with emphasis on key architectural pivots.

---

## Phase 1: Project Setup (June-July 2025)

### Epic 1: Foundation
**Status**: ✅ Complete
**Duration**: ~3 weeks

**Key Milestones**:
- Initial repository creation
- React 19 + TypeScript frontend scaffold
- FastAPI backend with SQLAlchemy ORM
- PostgreSQL database with Docker
- GitHub Actions CI/CD pipeline
- Project structure and naming conventions established

**Commits**:
- Initial Git repository
- Bootstrap React app with TypeScript
- FastAPI backend scaffold
- Docker environment configuration
- CI pipeline setup

**Deliverables**:
- Working local development environment
- Automated testing pipeline
- Database migration framework (Alembic)
- Basic health check endpoints

---

## Phase 2: The MHD Parser Era (July-August 2025)

### Initial Approach: Binary MHD Parsing
**Status**: ❌ Abandoned
**Duration**: ~4 weeks

**The Problem**:
Mids Reborn stores character build data in binary `.mhd` files using .NET serialization. The initial plan was to:
1. Parse these binary files directly
2. Extract game data (powers, enhancements, archetypes)
3. Populate PostgreSQL database
4. Provide web-based build editing

**Implementation Attempts**:

#### Attempt 1: Python Binary Reader
**Commits**:
- `45535da` - Complete Subtask 2.5.6: Parse complete I12.mhd file (TDD)
- `3362b30` - Complete Subtask 2.5.7: Parse Enhancement database (TDD)
- `5496af8` - Complete Subtask 2.5.8: Parse Salvage and Recipe databases (TDD)

**Files Created**:
- `backend/archive/mhd_parser/binary_reader.py`
- `backend/archive/mhd_parser/power_parser.py`
- `backend/archive/mhd_parser/enhancement_database_parser.py`
- `backend/archive/mhd_parser/text_mhd_parser.py`

**Challenges**:
- .NET binary serialization complexity
- Endianness issues
- Variable-length encoding
- Undocumented data structures
- Character encoding problems (UTF-16 vs ASCII)

#### Attempt 2: MidsReborn Integration
**Commits**:
- `7cc32f1` - Add DataExporter with MidsReborn integration
- `1e8b994` - Implement MidsReborn integration for DataExporter
- `34701d6` - Add Mac MidsReborn MHD parser for data extraction
- `6f952a0` - Implement MidsReborn Context initialization

**Approach**:
- Clone MidsReborn C# codebase
- Create DataExporter console app
- Load MidsReborn's DatabaseAPI
- Export to JSON using existing serializers

**Files Created**:
- `external/DataExporter/` (C# project)
- Windows VM setup documentation
- Integration test suites

**Challenges**:
- Windows Forms dependencies
- Complex initialization sequence
- Mac development environment issues
- Fragile cross-platform builds

**Decision Point**: After 4 weeks of effort, the team realized:
- Binary parsing was overly complex
- Maintenance burden would be high
- Data structure was undocumented and changed frequently
- A better solution existed: direct server data

---

## Phase 3: The JSON-Native Pivot (August 2025)

### Epic 2.5.5: Legacy Elimination
**Status**: ✅ Complete
**Duration**: ~2 weeks

**The Breakthrough**:
Discovered the `city_of_data` GitLab repository containing JSON exports of game server data:
- Direct from City of Heroes Homecoming server
- Already in JSON format
- Includes all powers, enhancements, archetypes
- Updated regularly by server maintainers
- No binary parsing needed!

**Key Commits**:
- `1da08c2` - chore: remove legacy MHD parser references
- `a611e17` - feat: Refactor MHD dependencies for JSON import (Epic 2.5.5 Task 2.5.5.2)
- `156e574` - feat: Implement JSON Data Import System (Epic 2.6)
- `bc128e8` - feat: Epic 2.5.5 - Legacy Elimination & JSON-Native Foundation

**Architecture Change**:
```
OLD APPROACH:
MidsReborn .mhd files → Binary Parser → Python Objects → Database

NEW APPROACH:
city_of_data JSON → Direct Import → Database
```

**Benefits**:
- 90% reduction in parser complexity
- Direct data source from game servers
- Automatic updates when servers update
- No Windows dependencies
- Maintainable by team without C# knowledge

**Files Moved to Archive**:
- `backend/archive/mhd_parser/` (entire directory)
- `external/DataExporter/` (entire C# project)
- Related test files

**New Implementation**:
- `scripts/import_json_data.py` - Generic JSON importer
- `backend/app/commands/import_mhd.py` - Updated to use JSON
- Database models updated for JSON schema

---

## Phase 4: Data Import Optimization (August 2025)

### Epic 2.6: JSON Data Import System
**Status**: ✅ Complete
**Duration**: ~2 weeks

**Challenge**: The `city_of_data` repository contains **360,000+ power records** in a single JSON file.

**Solution**: High-performance streaming importer with:
- Streaming JSON parser (ijson library)
- Multi-tier caching (LRU + Redis)
- Batch database inserts
- Progress tracking and resume capability
- Composite and GIN database indexes

**Performance Metrics**:
- Import speed: ~1,500 records/second
- Memory usage: <1GB for 360K records
- Query performance: <100ms average
- Cache hit rate: >90%

**Key Files**:
- `scripts/import_json_data.py` - Main import script
- `backend/app/models.py` - Optimized SQLAlchemy models
- `alembic/versions/*` - Database optimization migrations

**Justfile Commands**:
```bash
just import-all data-directory         # Import all data types
just i12-import data.json              # High-performance I12 import
just import-health                     # System health check
just cache-stats                       # Cache performance
```

---

## Phase 5: Agentic Development Workflow (August-October 2025)

### Epic 2.5.2: Native Sub-Agents Implementation
**Status**: ✅ Complete
**Duration**: ~3 weeks

**The Experiment**:
Could AI agents assist development at scale?

**Initial Approach**: Custom MCP Agents
- Attempted to build custom Model Context Protocol agents
- Complex architecture
- Difficult to maintain
- Token management challenges

**Pivot**: Anthropic Native Sub-Agents
**Commit**: `b8314d1` - feat: add Claude Code native sub-agents for specialized development tasks

**Created 8 Specialized Agents**:
1. **Database Specialist** - Schema design, migrations, query optimization
2. **Backend Specialist** - FastAPI endpoints, Pydantic schemas
3. **Frontend Specialist** - React components, TypeScript, UI/UX
4. **Import Specialist** - Data import, city_of_data integration
5. **Testing Specialist** - pytest, Vitest, E2E tests
6. **DevOps Specialist** - Docker, CI/CD, deployment
7. **Calculation Specialist** - Game mechanics, damage calculations
8. **Documentation Specialist** - Maintaining docs, CLAUDE.md

**Agent Files**:
```
.claude/agents/
├── DATABASE_SPECIALIST.md
├── BACKEND_SPECIALIST.md
├── FRONTEND_SPECIALIST.md
├── IMPORT_SPECIALIST.md
├── TESTING_SPECIALIST.md
├── DEVOPS_SPECIALIST.md
├── CALCULATION_SPECIALIST.md
└── DOCUMENTATION_SPECIALIST.md
```

**Integration Pattern**:
- Engineers declare their task: "I need to work on database migrations"
- Claude automatically loads `DATABASE_SPECIALIST.md`
- Context-specific documentation loaded from `.claude/modules/database/`
- Agent provides specialized guidance

**GitHub Workflows Created**:
- `claude-auto-review.yml` - Automatic PR review
- `claude-code-integration.yml` - @claude mentions in PRs
- `doc-auto-sync.yml` - Documentation sync
- `context-health-check.yml` - Context validation

**Benefits Observed**:
- 40% reduction in CI/CD runtime
- Faster PR review cycles
- Consistent documentation updates
- Reduced context switching for developers

---

### Epic 2.5.3: RAG Implementation
**Status**: ✅ Complete (later removed)
**Duration**: ~2 weeks

**Experiment**: Retrieval-Augmented Generation for codebase search

**Implementation**:
- Gemini embeddings with offline fallback
- ChromaDB vector database
- Multi-format document processing
- Batch processing with cost optimization

**Outcome**:
- Successfully implemented and tested (100/102 tests passing)
- Later archived as project pivoted to simpler documentation approach
- Files moved to `backend/rag/` (excluded from git)

---

## Phase 6: GitHub Actions Optimization (August-September 2025)

### Workflow Consolidation
**Status**: ✅ Complete

**Problem**:
- 15+ separate GitHub Actions workflows
- Redundant YAML
- Long CI/CD execution times
- Duplicate Claude context loading

**Solution - Three Phases**:

#### Phase 1: Basic Optimizations
**Commit**: `1148558` - feat: implement Phase 1 GitHub Actions optimizations

Changes:
- Dynamic timeouts based on PR size
- Concurrency controls to prevent duplicate runs
- Skip-doc-review label support
- Max turns limits for AI responses

#### Phase 2: Workflow Consolidation
**Commit**: `1e3a6f0` - feat: consolidate GitHub workflows (Phase 2 optimization)

Changes:
- Consolidated claude-code-integration from 3 jobs to 1 matrix job
- 60% less YAML duplication
- Unified error handling
- Consistent timeout strategies

#### Phase 3: Reusable Components
**Commit**: `f8d6060` - feat: implement Phase 3 reusable workflow components

Changes:
- Created reusable workflow components
- Shared composite actions
- Centralized configuration
- Documented in `.claude/workflows/github/REUSABLE_COMPONENTS.md`

**Results**:
- 40% performance improvement
- 100% GitHub Actions success rate (15/15 passing)
- Reduced maintenance burden

---

## Current State: Epic 3 - Backend API (October 2025)

### Status: 🚧 25% Complete

**Completed**:
- ✅ Core data endpoints (GET /api/archetypes, powers, etc.)
- ✅ Database optimization for read operations
- ✅ Pydantic schemas for validation

**In Progress**:
- 🚧 Build simulation endpoints
- 🚧 Calculation logic (damage, resistance, etc.)

**Planned**:
- 📋 Write/modify operations (POST, PUT, DELETE)
- 📋 User authentication
- 📋 Build saving/sharing

---

## Key Architectural Decisions

### ✅ Decision 1: Abandon MHD Binary Parsing
**When**: August 2025
**Why**: Complexity, maintenance burden, better alternative existed
**Impact**: 4 weeks of work abandoned, but unlocked faster path forward

### ✅ Decision 2: Adopt city_of_data JSON Source
**When**: August 2025
**Why**: Direct server data, JSON format, community-maintained
**Impact**: 90% reduction in parser complexity, maintainable long-term

### ✅ Decision 3: Native Claude Sub-Agents
**When**: August 2025
**Why**: Simpler than custom MCP agents, better Anthropic support
**Impact**: Successful agentic development workflow

### ✅ Decision 4: uv Over pip
**When**: July 2025
**Why**: 10x faster dependency resolution, better lockfiles
**Impact**: Faster CI/CD, reproducible builds

### ✅ Decision 5: GitHub Actions Automation
**When**: August-September 2025
**Why**: Reduce manual work, enforce standards, AI-assisted PR review
**Impact**: 40% faster CI/CD, consistent documentation

---

## Lessons Learned

### 1. Validate Assumptions Early
The MHD parser consumed 4 weeks before discovering a better path. Earlier research into `city_of_data` would have saved time.

### 2. Embrace Pivots
Willingness to abandon the MHD parser (despite sunk cost) led to a better architecture.

### 3. AI Agents Require Structure
Random AI assistance didn't scale. Specialized sub-agents with clear domains proved effective.

### 4. Automate Ruthlessly
GitHub Actions automation reduced toil and enforced quality standards.

### 5. Documentation as Code
Keeping `.claude/` docs in git with automated sync ensured they stayed current.

---

## Future Roadmap

### Epic 4: Frontend Development (Q4 2025)
- React build planner UI
- Power selection interface
- Enhancement slotting
- Build statistics display

### Epic 5: Deployment (Q1 2026)
- Google Cloud Platform deployment
- Docker registry
- Production database
- CDN for frontend assets

### Epic 6: Optimization (Q2 2026)
- Performance tuning
- Caching strategies
- Mobile responsiveness
- Advanced build validation

---

*This evolution reflects the messy reality of software development: experiments, pivots, and continuous learning.*
