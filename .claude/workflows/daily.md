# Daily Development Workflow

## 🌅 Session Start (Required)

```bash
# 1. Set environment
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"

# 2. Health check (MANDATORY)
just health

# 3. Start services
just dev

# 4. Begin session tracking
/project:session-start issue-123-description
```

## 🔄 Development Cycle

### Before Coding
```bash
git pull origin main            # Get latest
just import-status             # Check data system
git checkout -b feature/issue-123-component
```

### During Development
```bash
just test-watch                # Run tests continuously
just lint-fix                  # Fix issues as you go
/project:session-update "Implemented X feature"
```

### Committing Work
```bash
# Quick commit
just ucp "feat: add user authentication"

# Full update (includes progress.json)
just update-progress
```

## ✅ Pre-Push Checklist

```bash
just quality      # All code checks
just test        # Test suite passes
just build       # Build succeeds
```

## 🏁 Session End

```bash
# 1. Final update
just update-progress

# 2. End session
/project:session-end

# 3. Create PR if needed
gh pr create --title "feat: Add X" --body "..."
```

## 🚀 Quick Commands

| Task | Command |
|------|---------|
| View logs | `just logs backend` |
| Database shell | `just db-shell` |
| Python REPL | `just backend-shell` |
| Reset database | `just db-reset` |
| Import health | `just import-health` |

## ⚡ Hotkeys

- **Quality check**: `just quality`
- **Quick save**: `just ucp "message"`  
- **Token check**: Monitor at 90K warning
- **Context clear**: `/clear` between tasks

---
*Full workflow: `.claude/development-workflow.md`*