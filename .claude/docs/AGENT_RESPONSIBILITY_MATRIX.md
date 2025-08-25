# Claude Code Sub-Agent Responsibility Matrix
Last Updated: 2025-08-25 00:00:00 UTC

## Overview

This document clarifies the responsibilities and boundaries between Claude Code's native sub-agents to prevent overlap and ensure efficient task routing.

## Agent Responsibilities

### 🔧 backend-specialist
**Primary Focus**: FastAPI backend services and REST API implementation

**Responsibilities**:
- REST API endpoint design and implementation
- Pydantic model creation for request/response validation
- Authentication and authorization systems
- Database query optimization (working with database-specialist)
- API performance optimization and caching
- OpenAPI/Swagger documentation
- API testing with pytest

**NOT Responsible For**:
- Database schema design (→ database-specialist)
- Complex game calculations (→ calculation-specialist)
- Frontend API integration (→ frontend-specialist)
- Deployment configuration (→ devops-specialist)

### 🗄️ database-specialist
**Primary Focus**: Database schema, migrations, and data integrity

**Responsibilities**:
- Alembic migration creation and management
- PostgreSQL schema design and optimization
- Index creation and query optimization
- Database seeding and fixtures
- Data integrity constraints
- Legacy data migration (MHD → PostgreSQL)

**NOT Responsible For**:
- API endpoint creation (→ backend-specialist)
- Business logic implementation (→ backend-specialist)
- Import file parsing (→ import-specialist)

### 🧮 calculation-specialist
**Primary Focus**: City of Heroes game mechanics and formulas

**Responsibilities**:
- Damage calculation formulas
- Enhancement bonus calculations
- Set bonus aggregation
- Exemplar scaling logic
- Proc rate calculations
- Combat mechanics implementation

**NOT Responsible For**:
- API endpoint exposure (→ backend-specialist)
- Database storage (→ database-specialist)
- UI calculation display (→ frontend-specialist)

### 🎨 frontend-specialist
**Primary Focus**: React components and user interface

**Responsibilities**:
- React component development
- TypeScript interfaces and types
- State management (Redux/Context)
- UI/UX implementation
- Frontend testing with Vitest
- API integration on frontend

**NOT Responsible For**:
- API endpoint creation (→ backend-specialist)
- Game calculations (→ calculation-specialist)
- Backend business logic (→ backend-specialist)

### 📥 import-specialist
**Primary Focus**: Game data file parsing and import

**Responsibilities**:
- I12 power data parsing
- MHD file format parsing
- Binary data extraction
- Import pipeline optimization
- Data validation and integrity
- Bulk import operations

**NOT Responsible For**:
- Database schema (→ database-specialist)
- API endpoints for imports (→ backend-specialist)
- Import UI (→ frontend-specialist)

### 🧪 testing-specialist
**Primary Focus**: Test creation and quality assurance

**Responsibilities**:
- Unit test creation (pytest/Vitest)
- Integration test design
- E2E test implementation (Playwright)
- Test fixture creation
- Test coverage improvement
- Performance testing

**Works With All Agents**: Creates tests for their implementations

### 📚 documentation-specialist
**Primary Focus**: Documentation and Claude context management

**Responsibilities**:
- CLAUDE.md maintenance (<5K tokens)
- Module documentation updates
- API documentation
- Epic progress tracking
- README synchronization
- Development workflow docs

**Works With All Agents**: Documents their work

### 🚀 devops-specialist
**Primary Focus**: Deployment and infrastructure

**Responsibilities**:
- CI/CD pipeline configuration
- Docker optimization
- GitHub Actions workflows
- Environment configuration
- Monitoring and logging setup
- Production deployment

**NOT Responsible For**:
- Application code (→ other specialists)
- Database migrations (→ database-specialist)

## Coordination Guidelines

### When Multiple Agents Are Needed

1. **API with Complex Calculations**:
   - Lead: backend-specialist (API structure)
   - Support: calculation-specialist (game formulas)
   - Order: calculation-specialist → backend-specialist

2. **Database-Backed API**:
   - Lead: backend-specialist (API design)
   - Support: database-specialist (schema/queries)
   - Order: database-specialist → backend-specialist

3. **Full Feature Implementation**:
   - Order: database → calculation → backend → frontend → testing

4. **Import Pipeline**:
   - Lead: import-specialist (parsing)
   - Support: database-specialist (storage)
   - Order: import-specialist → database-specialist

### Hand-off Protocol

When an agent completes work that another agent needs:

1. Agent saves state via subagent-state-tracker hook
2. Provides clear summary of completed work
3. Identifies next agent needed
4. Lists any blockers or dependencies

### Example Task Routing

**Task**: "Create an API endpoint for character power calculations"

1. **calculation-specialist**: Implement power calculation logic
2. **backend-specialist**: Create API endpoint using calculation logic
3. **testing-specialist**: Write tests for both calculation and API
4. **documentation-specialist**: Update API docs

## State Management

The `subagent-state-tracker.py` hook automatically:
- Saves agent work to `.claude/state/agents/`
- Logs activities to `.claude/state/logs/`
- Creates daily summaries in `.claude/state/summaries/`

This ensures continuity between agent hand-offs and provides audit trails.

## Conflict Resolution

If unclear which agent to use:
1. Consider the primary output needed
2. Use the agent closest to that domain
3. Let that agent coordinate with others as needed

Remember: Agents can identify when they need support from other specialists and should explicitly state this in their responses.