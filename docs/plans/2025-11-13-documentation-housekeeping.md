# Implementation Plan: Project Documentation Housekeeping

**Created**: 2025-11-13
**Purpose**: Clean up documentation drift, update to reflect superpowers workflow, remove unused files
**Scope**: Documentation and project management files only (no code changes)

---

## Background & Context

The Mids Hero Web project has undergone significant workflow changes:

**Previous Workflow**:
- Manual development with direct Claude Code interaction
- Context managed via various .claude/ files
- Unclear documentation structure

**Current Workflow**:
- Superpowers plugin for planning (`/superpowers:write-plan`)
- Superpowers plugin for execution (`/superpowers:execute-plan`)
- Frontend development orchestrator (`.claude/skills/frontend-development`)
- Backend already complete (100% API coverage)

**Problem**: Documentation hasn't caught up with these changes, causing:
- Confusion about how to use the project
- Outdated instructions in CLAUDE.md
- Unused/stale files cluttering the repository
- Inconsistent project status tracking

---

## Objectives

1. **Audit all documentation** - Identify what's current, outdated, or unused
2. **Update CLAUDE.md** - Point to correct workflow (superpowers + frontend-development)
3. **Clean up .claude/ directory** - Remove unused context maps, outdated workflows
4. **Update README files** - Ensure all READMEs reflect current state
5. **Consolidate project status** - Single source of truth for progress
6. **Remove dead files** - Delete truly unused documentation
7. **Establish documentation standards** - Prevent future drift

---

## Verified Technical Constraints

**Repository Structure** (verified via exploration):
```
/Users/w/code/mids-hero-web/
├── CLAUDE.md                          # Main entry point (needs update)
├── README.md                          # Project README
├── .claude/
│   ├── skills/
│   │   ├── frontend-development/      # NEW: Recently created
│   │   └── verified-stage-development/ # Empty (needs cleanup?)
│   ├── docs/                          # Documentation
│   ├── workflows/                     # Workflows (may be outdated)
│   ├── modules/                       # Modules (may be outdated)
│   └── settings.json
├── docs/
│   ├── frontend/                      # NEW: Recently created
│   │   ├── architecture.md
│   │   ├── epic-breakdown.md
│   │   └── midsreborn-ui-analysis.md
│   ├── midsreborn/                    # MidsReborn specs
│   └── plans/                         # NEW: This plan lives here
├── backend/                           # Complete (no changes)
└── frontend/                          # Skeleton (to be built)
```

**Key Files Status**:
- ✅ Recent: `docs/frontend/*.md` (just created)
- ✅ Recent: `.claude/skills/frontend-development/` (just created)
- ❓ Status unknown: `.claude/workflows/`, `.claude/modules/`
- ❓ Status unknown: `.claude/docs/development-workflow.md`
- ❓ Status unknown: `.claude/state/progress.json`
- ⚠️ Needs update: `CLAUDE.md` (points to old workflow)

---

## Implementation Tasks

### Task 1: Audit Existing Documentation

**Objective**: Create comprehensive inventory of all documentation files

**Steps**:

1. List all documentation files:
   ```bash
   fd -e md . /Users/w/code/mids-hero-web
   fd -e json . /Users/w/code/mids-hero-web/.claude
   ```

2. Categorize each file:
   - **CURRENT**: Recently updated, reflects new workflow
   - **OUTDATED**: Contains old workflow references
   - **UNUSED**: No longer referenced or needed
   - **UNKNOWN**: Needs manual review

3. Create audit document: `docs/DOCUMENTATION-AUDIT-2025-11-13.md`

**Output**: Comprehensive list of all docs with status

**Acceptance Criteria**:
- All .md files cataloged
- All .json config files cataloged
- Each file tagged with status (CURRENT/OUTDATED/UNUSED/UNKNOWN)

---

### Task 2: Update CLAUDE.md (Main Entry Point)

**Objective**: Update CLAUDE.md to reflect superpowers workflow

**Current Issues**:
- Points to outdated context system
- Doesn't mention frontend-development skill
- Unclear about superpowers plugin usage

**Required Changes**:

1. **Update Quick Start section**:
   ```markdown
   ## 🎯 Quick Start for Development

   ### Backend (Complete - 100% API Coverage)
   Backend is complete with full test coverage. No changes needed.

   ### Frontend (In Development)
   Use the frontend-development skill to build React components:

   1. Run: Tell Claude "start epic 1.1" or similar frontend task
   2. Claude will invoke `.claude/skills/frontend-development`
   3. Workflow:
      - Analyzes MidsReborn UI
      - Invokes `/superpowers:write-plan` to create plan
      - Gets your approval
      - Invokes `/superpowers:execute-plan` to build components
      - Generates checkpoint for review

   See: `docs/frontend/epic-breakdown.md` for all epics
   ```

2. **Update Context System section**:
   ```markdown
   ## 📍 Development Workflow

   **Superpowers Plugin Workflow**:
   - `/superpowers:write-plan` - Create detailed implementation plans
   - `/superpowers:execute-plan` - Execute plans with quality gates
   - `.claude/skills/frontend-development` - Orchestrates frontend epics

   **Documentation**:
   - Backend: Complete (see backend/README.md)
   - Frontend: See `docs/frontend/` for architecture and epic breakdown
   - MidsReborn Specs: See `docs/midsreborn/` for reverse-engineering docs
   ```

3. **Remove outdated references**:
   - Remove references to `.claude/modules/` if unused
   - Remove references to `.claude/workflows/daily.md` if outdated
   - Remove context-map.json references if not used

**Output**: Updated CLAUDE.md

**Acceptance Criteria**:
- CLAUDE.md reflects superpowers workflow
- Links point to current documents
- No references to unused/outdated files

---

### Task 3: Clean Up .claude/ Directory

**Objective**: Remove unused files, update structure

**Files to Review**:

1. **`.claude/skills/verified-stage-development/`**:
   - Currently empty directory
   - Action: Delete if truly empty and unused

2. **`.claude/workflows/`**:
   - Check if workflows are current
   - Action: Update or remove outdated workflows

3. **`.claude/modules/`**:
   - Check if modules are used
   - Action: Remove if superseded by superpowers plugin

4. **`.claude/docs/`**:
   - Review all documentation
   - Action: Consolidate into main `docs/` or update

5. **`.claude/state/progress.json`**:
   - Check if still used for tracking
   - Action: Update or deprecate in favor of new system

**Output**: Clean .claude/ directory structure

**Acceptance Criteria**:
- No empty directories
- No outdated workflow files
- Clear structure that matches current development approach

---

### Task 4: Update All README Files

**Objective**: Ensure all READMEs are current and helpful

**Files to Update**:

1. **Root `/README.md`**:
   - Update project status (Backend: Complete, Frontend: In Development)
   - Link to `docs/frontend/epic-breakdown.md` for frontend roadmap
   - Update tech stack section (mention Next.js, shadcn/ui, etc.)
   - Update getting started (point to superpowers workflow)

2. **`backend/README.md`** (if exists):
   - Mark as COMPLETE
   - Document 100% API coverage
   - Link to API documentation

3. **`frontend/README.md`** (create if needed):
   - Document Next.js setup (when Epic 1.1 completes)
   - Link to `docs/frontend/architecture.md`
   - Explain development workflow (frontend-development skill)

4. **`docs/frontend/README.md`** (create):
   - Overview of frontend documentation
   - Link to architecture, epic-breakdown, midsreborn-ui-analysis

5. **`shared/user/midsreborn-screenshots/README.md`**:
   - Already created and current (no changes needed)

**Output**: All READMEs updated

**Acceptance Criteria**:
- Each directory with significant content has a README
- READMEs accurately describe current state
- READMEs link to relevant detailed documentation

---

### Task 5: Consolidate Project Status Tracking

**Objective**: Single source of truth for project progress

**Create**: `docs/PROJECT-STATUS.md`

**Content**:

```markdown
# Mids Hero Web - Project Status

**Last Updated**: 2025-11-13

## Overall Progress

- ✅ **Backend**: 100% Complete (Epics 1-3)
- 🚧 **Frontend**: 0% Complete (Epic 1.1 ready to start)
- 📋 **Infrastructure**: Not Started (Deferred to post-frontend)

## Backend Status (COMPLETE)

### Epic 1: Setup & CI/CD ✅
- Database migrations
- GitHub Actions optimized
- Development environment

### Epic 2: I12 Parser & Database ✅
- Power data import
- Database integration
- Validation

### Epic 3: Calculation APIs ✅
- Power calculations
- Enhancement slotting
- Set bonuses
- Build totals
- 100% test coverage

## Frontend Status (IN DEVELOPMENT)

### Epic 1: Foundation & Setup 🚧
- [ ] Epic 1.1: Next.js + Design System (READY TO START)
- [ ] Epic 1.2: State Management
- [ ] Epic 1.3: Layout Shell
- [ ] Epic 1.4: API Client

### Epic 2-7: See `docs/frontend/epic-breakdown.md`

## Development Workflow

**Current Approach**: Superpowers Plugin + Frontend Development Skill

1. Tell Claude: "start epic 1.1" or describe frontend task
2. Claude invokes `.claude/skills/frontend-development`
3. Workflow:
   - Analyzes MidsReborn UI
   - Creates plan via `/superpowers:write-plan`
   - Gets approval
   - Executes via `/superpowers:execute-plan`
   - Generates checkpoint

**Documentation**:
- Frontend Architecture: `docs/frontend/architecture.md`
- Epic Breakdown: `docs/frontend/epic-breakdown.md`
- MidsReborn Analysis: `docs/frontend/midsreborn-ui-analysis.md`
```

**Output**: docs/PROJECT-STATUS.md

**Acceptance Criteria**:
- Clear progress tracking
- Links to detailed docs
- Updated workflow instructions

---

### Task 6: Remove Dead/Unused Files

**Objective**: Delete truly unused documentation

**Process**:

1. Based on audit from Task 1, identify UNUSED files
2. Verify no references (grep for filename)
3. Move to `.deprecated/` folder first (safety)
4. After confirmation, delete

**Candidate Files** (TBD after audit):
- Empty skill directories
- Superseded workflow docs
- Old context maps
- Duplicate documentation

**Output**: Clean repository

**Acceptance Criteria**:
- No unused files in main tree
- Clear justification for deletions

---

### Task 7: Create Documentation Standards

**Objective**: Prevent future drift

**Create**: `docs/DOCUMENTATION-STANDARDS.md`

**Content**: Standards for document headers, organization, maintenance, deprecation

**Output**: Documentation standards guide

---

## Acceptance Criteria

- [ ] All documentation current and accurate
- [ ] CLAUDE.md reflects superpowers workflow
- [ ] Clear PROJECT-STATUS.md
- [ ] No unused files in main tree
- [ ] All READMEs updated
- [ ] Documentation standards established

---

## Execution Notes

**Execute with**: `/superpowers:execute-plan` in new session

**Estimated Time**: 2-3 hours

**Can Be Done In Batches**: Yes (task by task)

---

**Plan Status**: Ready for Execution
**Created By**: superpowers:write-plan
**Date**: 2025-11-13
