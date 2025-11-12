# Mids Hero Web - Implementation Plans

**Created**: 2025-11-06
**Using**: writing-plans skill (superpowers)

This directory contains comprehensive, bite-sized implementation plans for all remaining Mids Hero Web development work.

---

## 📋 Plan Files

### Phase 1: Critical Cleanup (8 days)
**File**: `2025-11-06-epic-2.5.5-cleanup.md` (31 KB)
- Resolve duplicate directories (backend/backend/app/core)
- Remove all MHD/I12 legacy code
- Update database models for JSON
- Retrain Claude AI agents
- Migrate Justfile commands
- **Blocks**: Epic 2.6, 2.7, full Epic 3

### Phase 2: JSON Data Migration (8 days)
**File**: `2025-11-06-epic-2.6-json-migration.md` (55 KB)
- Implement archetype importer
- Implement enhancement set importer
- Implement power importer (5,775 powers)
- Progress tracking and validation
- Full integration testing
- **Depends on**: Epic 2.5.5

### Phase 3: Backend API - Calculations (4 days)
**File**: `2025-11-06-epic-3.2-calculation-endpoints.md` (23 KB)
- Enhancement Diversification (ED) calculator
- Damage calculator with enhancements
- Defense/resistance calculator
- Build calculation API endpoint
- Power analysis (DPS/DPA/DPE)
- **Depends on**: Epic 2.6

### Phase 4: Backend API - Write Operations (2 days)
**File**: `2025-11-06-epic-3.3-write-operations.md` (11 KB)
- POST /api/builds (create)
- PUT /api/builds/{id} (update)
- DELETE /api/builds/{id} (delete)
- Power slot operations (add/remove powers)
- Enhancement slotting
- Validation rules

### Phase 5: Testing, Frontend, Deployment, Optimization
**File**: `2025-11-06-epic-3.4-4.x-5-6.md` (18 KB)
- **Epic 3.4**: API testing & OpenAPI docs (2 days)
- **Epic 4.1-4.3**: React frontend (20 days)
  - Core UI components
  - Build editor with real-time calculations
  - Data browser pages
- **Epic 5**: Production deployment (8 days)
  - Docker production setup
  - CI/CD pipeline
  - Monitoring (Prometheus/Grafana)
- **Epic 6**: Optimization (8 days)
  - Redis caching
  - Database indexes
  - Frontend performance

---

## 🎯 Plan Methodology

All plans follow the **writing-plans skill** format:

### TDD Workflow
Every task follows Test-Driven Development:
1. **Step 1**: Write the failing test
2. **Step 2**: Run test to verify it fails
3. **Step 3**: Write minimal implementation
4. **Step 4**: Run test to verify it passes
5. **Step 5**: Commit changes

### Bite-Sized Tasks
Each step is 2-5 minutes of work:
- One specific action per step
- Clear expected outcomes
- Immediate verification
- Frequent commits

### Complete Code Examples
Plans include:
- ✅ Exact file paths
- ✅ Complete code (not pseudocode)
- ✅ Full test implementations
- ✅ Exact bash commands
- ✅ Expected outputs

---

## 🚀 How to Use These Plans

### Option 1: Execute with superpowers:executing-plans
Open a new Claude session and use the executing-plans skill:

```bash
# In Claude Code:
/superpowers:execute-plan docs/plans/2025-11-06-epic-2.5.5-cleanup.md
```

The plan will be executed task-by-task with review checkpoints between batches.

### Option 2: Execute with superpowers:subagent-driven-development
Stay in current session and dispatch subagents per task:

```bash
# In Claude Code:
Use the subagent-driven-development skill with the plan
```

Fresh subagent handles each task + code review between tasks.

### Option 3: Manual Execution
Follow the plan manually, executing each step sequentially:

1. Read the task section
2. Execute Step 1 (write test)
3. Execute Step 2 (verify fails)
4. Execute Step 3 (implement)
5. Execute Step 4 (verify passes)
6. Execute Step 5 (commit)
7. Move to next task

---

## 📊 Timeline Summary

| Phase | Epic | Duration | Start | End |
|-------|------|----------|-------|-----|
| 1 | Epic 2.5.5 Cleanup | 8 days | Day 1 | Day 8 |
| 2 | Epic 2.6 JSON Migration | 8 days | Day 9 | Day 16 |
| 3a | Epic 3.2 Calculations | 4 days | Day 17 | Day 20 |
| 3b | Epic 3.3 Write Ops | 2 days | Day 21 | Day 22 |
| 3c | Epic 3.4 Testing | 2 days | Day 23 | Day 24 |
| 4 | Epic 4 Frontend | 20 days | Day 25 | Day 44 |
| 5 | Epic 5 Deployment | 8 days | Day 45 | Day 52 |
| 6 | Epic 6 Optimization | 8 days | Day 53 | Day 60 |
| **Total** | | **60 days** | | **~3 months** |

---

## ⚠️ Critical Dependencies

```
Epic 2.5.5 (Cleanup)
    ↓
Epic 2.6 (JSON Migration)
    ↓
Epic 3.2 (Calculations) → Epic 3.3 (Write Ops) → Epic 3.4 (Testing)
    ↓
Epic 4 (Frontend)
    ↓
Epic 5 (Deployment)
    ↓
Epic 6 (Optimization)
```

**IMPORTANT**: Epic 2.5.5 must be completed before any other work can proceed. It resolves critical architectural conflicts that block all other epics.

---

## 📈 Progress Tracking

After completing each epic:

1. Update `.claude/state/progress.json`
2. Update `CLAUDE.md` status section
3. Create PR with comprehensive description
4. Close associated GitHub issues
5. Start next epic

---

## 🛠️ Tech Stack by Phase

### Backend (Epics 2-3)
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- pytest
- Alembic (migrations)

### Frontend (Epic 4)
- React 18
- TypeScript
- TailwindCSS
- shadcn/ui
- TanStack Query
- Vite

### DevOps (Epic 5)
- Docker & Docker Compose
- GitHub Actions
- Nginx
- PostgreSQL 15
- Redis 7

### Monitoring (Epic 5-6)
- Prometheus
- Grafana
- Sentry (error tracking)
- Loki (logs)

---

## 📝 Plan Quality Metrics

Each plan includes:
- ✅ **100% test coverage** requirements
- ✅ **Exact file paths** (no ambiguity)
- ✅ **Complete code examples** (no TODOs)
- ✅ **Clear success criteria** (verifiable)
- ✅ **Rollback strategies** (safety)
- ✅ **Performance targets** (<100ms API, <2s frontend load)

---

## 🎓 Skills Referenced

These plans were created using:
- `superpowers:writing-plans` - Implementation plan creation
- `superpowers:executing-plans` - Batch execution with checkpoints
- `superpowers:subagent-driven-development` - Task-by-task with review
- `superpowers:test-driven-development` - TDD methodology
- `superpowers:verification-before-completion` - Validation requirements

---

## 💡 Next Steps

1. **Review plans** - Ensure alignment with project goals
2. **Choose execution method** - executing-plans vs subagent-driven
3. **Start Epic 2.5.5** - Critical cleanup must be done first
4. **Track progress** - Update status after each task
5. **Iterate** - Plans may need adjustment during implementation

---

## 📞 Support

If plans need adjustment or clarification:
- Open GitHub issue referencing plan file and section
- Update plan file with learnings
- Commit changes to plan for future reference

---

**Created with**: Claude Code + superpowers:writing-plans skill
**Total Plan Size**: 188 KB across 6 files
**Estimated Completion**: ~60 days (3 months) of focused development
