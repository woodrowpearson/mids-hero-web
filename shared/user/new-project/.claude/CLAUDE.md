# CLAUDE.md - Modular Core Instructions

This modular CLAUDE.md provides guidance to Claude agents working with this repository.

## Quick Start

```bash
# Initialize environment
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"

# Run health checks
just health
```

## Critical Rules

1. **Always use PROJECT_ROOT_DIR** for paths
2. **Run health checks before any work**
3. **Create feature branches from main/develop**
4. **Monitor token usage (alert at 90k/128k)**
5. **Use /clear command frequently**

## Development Workflow

```bash
# 1. Create feature branch
just feature my-feature

# 2. Make changes (TDD approach)
just test-match test_new_feature  # Write test first
# Implement feature
just quality                      # Runs format, lint, and typecheck

# 3. Commit and push
just ucp "feat: implement feature"
```

## Multi-Agent Coordination

For complex tasks exceeding context limits:

1. Check `./shared/memory/` for persistent context
2. Use `.agent-scratch/` for experiments and temporary work
3. Spawn specialized agents from `./templates/` when needed
4. Update progress: `just progress-update --task "id" --status "completed"`

```bash
# Quick scratch workspace
just scratch experiment-name
```

## Token Management

- Context window: 200,000 tokens
- Keep active context under 50,000 tokens
- Use `just context-health` to monitor
- Run `just context-prune` when approaching limits

## Important Reminders

- Use `fd` instead of `find` - NEVER use `find` command
- Use `trash` instead of `rm -rf` - NEVER use `rm -rf`
- Commit frequently with clear messages
- Update task progress immediately after completion