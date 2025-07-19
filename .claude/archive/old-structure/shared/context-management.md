# Context Management Guidelines

This document outlines strategies for managing AI context efficiently in the Mids Hero Web project.

## Context Optimization Strategy

### 1. Modular Documentation Structure

```
.claude/
├── CLAUDE.md              # Core 5k token summary
├── quick-commands.md      # Essential commands only
├── commands/              # Pre-approved workflows
├── agents/               # Specialized AI contexts
├── epics/                # Epic-specific details
└── shared/               # Architectural context
```

### 2. Token Management Rules

- **Core context**: Keep CLAUDE.md under 5k tokens
- **Working limit**: Stay under 50k tokens total
- **Warning threshold**: Alert at 40k tokens
- **Maximum limit**: 128k tokens hard limit

### 3. Context Reduction Strategies

#### For Development Tasks:
- Use `.claude/agents/database-agent.md` for database work
- Use `.claude/epics/epic-X.md` for specific epic context
- Reference `.claude/quick-commands.md` for command syntax

#### For Large Operations:
- Use custom commands: `.claude/commands/update-progress.sh`
- Clear context with `/clear` between unrelated tasks
- Use agent-specific contexts instead of full project context

### 4. File Organization Principles

1. **Single Responsibility**: Each file serves one purpose
2. **No Duplication**: Commands documented once in quick-commands.md
3. **Reference Pattern**: Link to detailed docs rather than duplicating
4. **Layered Detail**: Summary → Reference → Full detail

### 5. Context Health Monitoring

```bash
just token-usage          # Check current token count
just context-health       # Validate context structure
just context-prune        # Remove outdated context
```

### 6. Best Practices

#### When to Use Different Contexts:

**CLAUDE.md**: Always start here for project orientation
**quick-commands.md**: For command syntax lookup
**.claude/agents/**: For specialized work (database, API, frontend)
**.claude/epics/**: For epic-specific context and blockers
**.claude/shared/**: For architectural understanding

#### When to Clear Context:
- Switching between different epics
- After completing major milestones
- When approaching 40k token warning
- Between unrelated debugging sessions

#### Context Loading Strategy:
1. Start with CLAUDE.md (5k tokens)
2. Add relevant agent context (2-3k tokens)
3. Add specific epic context if needed (3-5k tokens)
4. Add shared architecture only if required (10k+ tokens)

### 7. Automated Context Management

The project includes automated tools:

- **Token monitoring**: Tracks and alerts on usage
- **Progress tracking**: Updates epic status automatically  
- **Context pruning**: Removes outdated temporary files
- **Health checks**: Validates context structure

### 8. Emergency Context Recovery

If context becomes too large:

1. Run `just context-prune` to clean up
2. Use `/clear` to reset Claude context
3. Load only essential files for current task
4. Use custom commands for complex operations

### 9. Documentation Maintenance

- Keep CLAUDE.md under 5k tokens always
- Update quick-commands.md when adding new just commands
- Archive completed epic contexts to reduce size
- Regular review and pruning of shared documentation

### 10. Team Collaboration

- Use consistent file references across team
- Document context patterns in this file
- Share context optimization strategies
- Regular context health reviews