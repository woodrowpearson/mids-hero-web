# Daily Development Workflow

## 🌅 Session Start (Required)

```bash
# 1. Set environment
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"

# 2. Health check (MANDATORY)
just health

# 3. Context validation (AUTOMATIC)
just context-check  # Or happens automatically via hooks

# 4. Start services
just dev

# 5. Declare your task to Claude
# Example: "I need to work on database migrations"
# This loads appropriate context modules automatically
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
# Note: Activity is automatically logged via hooks
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

# 2. Create PR if needed
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
*Full workflow: `.claude/docs/development-workflow.md`*