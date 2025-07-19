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

Claude uses **progressive context loading** based on your task:

```
Always Loaded:
├── CLAUDE.md (this file)        # ~2K tokens
├── .claude/settings.json        # Configuration
└── .claude/context-map.json     # Loading rules

Task-Based Loading:
├── Database → .claude/modules/database/
├── Import   → .claude/modules/import/
├── API      → .claude/modules/api/
├── Frontend → .claude/modules/frontend/
└── Testing  → .claude/modules/testing/
```

**Tell Claude your task** to load the right context:
- "I need to work on database migrations" 
- "Help me import I12 power data"
- "Let's build an API endpoint"

## 🚀 Essential Commands

```bash
# Development
just test          # Run tests
just lint-fix      # Fix issues
just quality       # All checks

# Git workflow  
just ucp "message"      # Quick commit
just update-progress    # Full update

# Database
just db-migrate         # Run migrations
just db-shell          # PostgreSQL

# Import
just import-health     # Check system
just i12-import file   # Import powers
```

## 📊 Current Status

- **Epic 1**: ✅ Complete (Setup, CI/CD)
- **Epic 2**: 🚧 95% (I12 parser done, MHD pending)
- **Epic 3-6**: 📋 Planned (API, Frontend, Deploy)

## 🛠️ Critical Rules

1. **ALWAYS use `just`** - Never run commands directly
2. **Run `just health`** before starting work
3. **One task per session** - Use `/clear` between
4. **Update progress** - `just update-progress`
5. **Check tokens** - Warning at 90K

## 📁 Key Locations

- **Core Guide**: `.claude/core/project-guide.md`
- **Quick Ref**: `.claude/core/quick-reference.md`
- **Workflows**: `.claude/workflows/daily.md`
- **Modules**: `.claude/modules/{task}/guide.md`

## 🔧 For Specific Work

| Task | Say This | Loads |
|------|----------|-------|
| Database | "work on database" | `.claude/modules/database/` |
| Import | "import data" | `.claude/modules/import/` |
| API | "build API" | `.claude/modules/api/` |
| Frontend | "React component" | `.claude/modules/frontend/` |
| Debug | "fix error" | `.claude/workflows/troubleshooting.md` |

## ⚠️ Remember

- Use `fd` not `find`
- Use `trash` not `rm -rf`  
- Keep sessions focused
- Load only what you need

---

*Claude's context system explained: `.claude/README.md`*  
*Full documentation: `.claude/docs/`*