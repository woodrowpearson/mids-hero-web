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

## 📍 Context System

Claude uses **native sub-agents** with automatic delegation based on your task:

```
Always Loaded:
├── CLAUDE.md (this file)        # ~2K tokens
├── .claude/settings.json        # Configuration
└── .claude/context-map.json     # Loading rules

Native Sub-Agents:
├── Database → database-specialist
├── Import   → import-specialist  
├── API      → backend-specialist
├── Frontend → frontend-specialist
├── Testing  → testing-specialist
├── DevOps   → devops-specialist
├── Calculations → calculation-specialist
└── Documentation → documentation-specialist
```

**Tell Claude your task** to automatically delegate to the right specialist:
- "I need to work on database migrations"
- "Help me import I12 power data"
- "Let's build an API endpoint"

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

- **Epic 1**: ✅ Complete (Setup, CI/CD, GitHub Actions optimized)
- **Epic 2**: ✅ Complete (I12 parser, database integration)
- **Epic 2.5.2**: ✅ Complete (Native sub-agents, workflows optimized)
- **Epic 2.5.3**: ✅ Complete (RAG with ChromaDB + Gemini)
- **Epic 2.5.4**: ✅ Complete (RAG implementation with testing)
- **Epic 2.5.5**: ✅ Complete (Project cleanup and state management)
- **Epic 2.6**: 🚧 IN PROGRESS (JSON Data Migration)
- **Epic 2.7**: 📋 PLANNED (RAG Enhancement & Documentation Indexing)
- **Epic 3**: 🚧 25% (Core API endpoints done)
- **Epic 4-6**: 📋 Planned (Frontend, Deploy, Optimize)

## 🛠️ Critical Rules

1. **ALWAYS use `just`** - Never run commands directly
2. **Run `just health`** before starting work
3. **NEVER commit to main** - Always create feature branch first
4. **One task per session** - Use `/clear` between
5. **Update progress** - `just update-progress`
6. **Check tokens** - Warning at 90K
7. **Create PR for changes** - Use `gh pr create` after pushing

## 📁 Key Locations

- **Workflows**: `.claude/workflows/daily.md`
- **Modules**: `.claude/modules/{task}/guide.md`
- **Dev Guide**: `.claude/docs/development-workflow.md`
- **Progress**: `.claude/state/progress.json`

## 🔧 For Specific Work

| Task | Say This | Auto-Delegates To |
|------|----------|-------------------|
| Database | "work on database" | `database-specialist` |
| Import | "import data" | `import-specialist` |
| API | "build API" | `backend-specialist` |
| Frontend | "React component" | `frontend-specialist` |
| Testing | "write tests" | `testing-specialist` |
| Calculations | "implement formulas" | `calculation-specialist` |
| DevOps | "deploy changes" | `devops-specialist` |
| Documentation | "update docs" | `documentation-specialist` |

## ⚠️ CRITICAL Command Compliance

**ALWAYS use these commands:**
- ✅ `fd` - NEVER use `find`
- ✅ `rg` (ripgrep) - NEVER use `grep`  
- ✅ `trash` - NEVER use `rm -rf`
- ✅ `uv` - NEVER use `pip`

**GitHub Actions will FAIL if you use forbidden commands!**

## ⚠️ Remember

- Keep sessions focused
- Load only what you need

---

*Claude's context system explained: `.claude/README.md`*
*Full documentation: `.claude/docs/`*
