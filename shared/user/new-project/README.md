# Claude Code Project Template

This template provides an optimized structure for projects using Claude Code, focusing on context management and AI-assisted development workflows.

## Features

- **Optimized Context Management**: Keep Claude's context under 50k tokens
- **Token Monitoring**: Real-time tracking with alerts at 90k tokens
- **Modular Documentation**: Split large docs to prevent context overload
- **Agent Templates**: Specialized agents for different development tasks
- **Progress Tracking**: Multi-session coordination support
- **Just Integration**: Streamlined workflows with the `just` command runner

## Quick Start

1. **Clone this template**:
   ```bash
   cp -r claude-code-template my-project
   cd my-project
   ```

2. **Install required tools**:
   ```bash
   ./scripts/setup-commands.sh
   ```

3. **Setup environment**:
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

4. **Initialize project**:
   ```bash
   just quickstart
   ```

5. **Start development**:
   ```bash
   just dev
   ```

## Project Structure

```
.
├── CLAUDE.md              # Main context file (<5k tokens)
├── .claude/               # Modular Claude documentation
│   ├── CLAUDE.md         # Extended context
│   ├── templates/        # Agent templates
│   └── shared/           # Shared knowledge
├── scripts/              # Utility scripts
│   └── context/          # Context management tools
├── justfile              # Task automation
└── .env                  # Environment configuration
```

## Key Commands

### Context Management
- `just context-health` - Check context health
- `just context-analyze` - Analyze token usage
- `just optimize-context` - Full optimization

### Development
- `just dev` - Start development
- `just test` - Run tests
- `just quality` - Code quality checks

### Progress Tracking
- `just progress-update` - Update task progress
- `just context-resume` - Resume session

## Best Practices

1. **Keep CLAUDE.md under 5k tokens**
2. **Use modular docs in .claude/**
3. **Clear context between tasks with /clear**
4. **Monitor tokens with `just token-monitor`**
5. **Use "ultrathink" for complex problems**
6. **Start new conversations for unrelated tasks**
7. **NEVER use `find`, `rm -rf`, or `grep` commands**
8. **Always use `fd`, `trash`, and `rg` instead**

## Customization

1. Edit `CLAUDE.md` with project-specific instructions
2. Modify agent templates in `.claude/templates/`
3. Add custom just recipes for your workflow
4. Update `.env` with your configuration

## Token Management

Claude Code has a 200k token context window, but optimal performance is achieved by keeping active context under 50k tokens. This template includes tools to:

- Monitor token usage in real-time
- Alert when approaching limits
- Automatically prune oversized contexts
- Split large documents into modules

## Multi-Agent Coordination

For complex tasks that exceed context limits:

1. Use specialized agents from templates
2. Track progress across sessions
3. Share context through `.claude/shared/memory/`
4. Hand off tasks between agents cleanly

## Contributing

This template is designed to evolve with Claude Code best practices. Contributions and improvements are welcome!