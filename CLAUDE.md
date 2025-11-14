# CLAUDE.md - Mids Hero Web AI Assistant Guide

> **This is your entry point**. Claude loads this file automatically. Keep it under 5K tokens.

## 🎯 Project: Modern City of Heroes Build Planner

Replacing legacy Windows Forms app with React/FastAPI web application.

## ⚡ Quick Start

```bash
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"
just health    # REQUIRED before any work
just dev       # Start services
```

## 📍 Development Workflow

**Superpowers Plugin Workflow**:
- `/superpowers:write-plan` - Create detailed implementation plans
- `/superpowers:execute-plan` - Execute plans with quality gates
- `.claude/skills/frontend-development` - Orchestrates frontend epics

**Code Review**:
Use `/code-review` command to automatically review PRs:
- CLAUDE.md compliance checking
- Bug detection
- Historical context analysis
- Confidence-scored feedback (threshold: 80)

**Current Focus**: Frontend development using superpowers workflow

**How to Use**:
1. Tell Claude: "start epic 1.1" or describe frontend task
2. Claude invokes `.claude/skills/frontend-development`
3. Workflow:
   - Analyzes MidsReborn UI
   - Creates plan via `/superpowers:write-plan`
   - Gets your approval
   - Executes via `/superpowers:execute-plan`
   - Generates checkpoint for review

**Documentation**:
- Frontend: `docs/frontend/` (architecture, epic breakdown, UI analysis)
- Backend: Complete (see `backend/README.md`, `api/README.md`)
- MidsReborn Specs: `docs/midsreborn/` (reverse-engineering reference)

## 🚀 Essential Commands

```bash
# Development
just test          # Run tests
just lint-fix      # Fix issues
just quality       # All checks

# Git workflow (ALWAYS use feature branches!)
git checkout -b feature/issue-XXX  # Create branch FIRST
just ucp "message"                 # Quick commit
just update-progress               # Full update
git push -u origin feature/...     # Push branch
gh pr create                       # Create PR

# Database
just db-migrate         # Run migrations
just db-shell          # PostgreSQL

# Import
just import-health     # Check system
just i12-import file   # Import powers
```

## 📊 Current Status

**Backend**: ✅ **100% Complete**
- Epic 1: Setup & CI/CD ✅
- Epic 2: I12 Parser & Database ✅
- Epic 3: Calculation APIs ✅ (100% test coverage)

**Frontend**: 🚧 **In Development**
- Epic 1.1: Next.js + Design System (READY TO START)
- Epic 1.2-1.4: State Management, Layout, API Client (Planned)
- Epic 2-7: See `docs/frontend/epic-breakdown.md`

**See**: `docs/PROJECT_STATUS.md` for detailed progress

## 🛠️ Critical Rules

1. **ALWAYS use `just`** - Never run commands directly
2. **Run `just health`** before starting work
3. **NEVER commit to main** - Always create feature branch first
4. **One task per session** - Use `/clear` between
5. **Update progress** - `just update-progress`
6. **Check tokens** - Warning at 90K
7. **Create PR for changes** - Use `gh pr create` after pushing

## 📁 Key Locations

- **Project Status**: `docs/PROJECT_STATUS.md`
- **Frontend Docs**: `docs/frontend/` (architecture, epics, UI analysis)
- **Frontend Skill**: `.claude/skills/frontend-development/`
- **MidsReborn Specs**: `docs/midsreborn/` (calculation reference)
- **Implementation Plans**: `docs/plans/`
- **GitHub Workflows**: `.claude/workflows/github/`

## ⚠️ Command Standards

Command standards are automatically enforced via hooks:

- ✅ `fd` - NOT `find`
- ✅ `rg` - NOT `grep`
- ✅ `trash` - NOT `rm -rf`
- ✅ `uv` - NOT `pip`

Violations will be blocked automatically.

## ⚠️ Remember

- Keep sessions focused
- Load only what you need

---

_Full documentation: `docs/` and `.claude/`_
_Development workflow: Use superpowers plugin for planning and execution_
