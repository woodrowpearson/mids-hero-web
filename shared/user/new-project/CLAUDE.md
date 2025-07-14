# CLAUDE.md - Core Instructions

This file provides essential guidance to Claude when working with this repository.

## Quick Start

```bash
# Always use just for operations
export PROJECT_ROOT_DIR=$(git rev-parse --show-toplevel)
cd "$PROJECT_ROOT_DIR"
just quickstart         # Setup environment
just dev               # Start development
just health            # Run health checks
```

## Context Management

- **Core docs**: `.claude/` - Modular documentation
- **Shared context**: `.claude/shared/` - Shared knowledge
- **Agent templates**: `.claude/templates/` - Specialized agents

## Critical Rules

1. **Always use just** for all operations
2. **Keep contexts under 50k tokens** to prevent distraction
3. **Run `just health` before any work
4. **Update progress**: `just progress-update`
5. **Monitor token usage**: Alert at 90k/128k
6. **Use /clear frequently** between unrelated tasks

## Development Workflow

See `.claude/development-workflow.md` for detailed workflow.

## Quick Commands

```bash
just           # Show all available commands
just dev       # Start development server
just test      # Run tests
just quality   # Run code quality checks
just ucp "msg" # Commit and push
```

## Documentation

- **Development**: `.claude/development-workflow.md`
- **Commands**: `.claude/quick-commands.md`
- **Architecture**: `.claude/shared/architecture.md`
- **Standards**: `.claude/shared/standards.md`

## Important

- Use `fd` instead of `find` - NEVER use `find` command
- Use `trash` instead of `rm -rf` - NEVER use `rm -rf`
- Start new conversations for separate tasks
- Use "ultrathink" for complex problems requiring deep analysis