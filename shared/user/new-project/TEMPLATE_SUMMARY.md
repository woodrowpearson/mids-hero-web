# Claude Code Project Template Summary

This template provides a complete setup for projects using Claude Code with optimized context management and development workflows.

## What's Included

### 1. Context Management System

- **CLAUDE.md** - Main context file (kept under 5k tokens)
- **.claude/** - Modular documentation directory
- **Token monitoring** - Real-time usage tracking
- **Context pruning** - Automatic optimization
- **Progress tracking** - Multi-session coordination

### 2. Command Enforcement

- **NEVER use `find`** - Always use `fd`
- **NEVER use `rm -rf`** - Always use `trash`
- **NEVER use `grep`** - Always use `rg` (ripgrep)
- Setup script installs required tools automatically

### 3. Development Automation

- **justfile** - Task runner with Claude-optimized recipes
- Context health monitoring
- Token usage analysis
- Agent templates for specialized tasks
- Git workflow helpers

### 4. File Structure

```
project-root/
├── CLAUDE.md                    # Main context (<5k tokens)
├── .claude/                     # Modular documentation
│   ├── CLAUDE.md               # Extended context
│   ├── development-workflow.md  # Dev process
│   ├── quick-commands.md       # Command reference
│   ├── templates/              # Agent templates
│   │   ├── backend-agent.md
│   │   ├── frontend-agent.md
│   │   └── specialized-agent.md
│   └── shared/                 # Shared knowledge
│       ├── architecture.md
│       ├── standards.md
│       ├── critical-rules.md   # Command usage rules
│       └── memory/             # Session persistence
├── .github/                    # GitHub configuration
│   └── workflows/              # CI/CD and AI workflows
│       ├── claude-code-integration.yml
│       ├── context-health-check.yml
│       ├── doc-synthesis.yml
│       ├── ai-pr-review.yml
│       └── ci.yml
├── .new-project/              # AI workflow configuration
│   └── workflows/
│       ├── config.yaml         # Workflow settings
│       └── implementation-guide.md
├── scripts/
│   ├── setup-commands.sh       # Install fd, trash, rg
│   ├── doc_synthesis.py        # Documentation generator
│   └── context/                # Context management
│       ├── context_health_monitor.py
│       ├── measure_context_complexity.py
│       ├── context_pruning.py
│       ├── analyze_token_usage.py
│       └── update_progress.py
├── justfile                    # Task automation
├── .env.template              # Environment template
├── .gitignore                 # Git exclusions
├── .claudeignore              # Claude exclusions
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── SETUP_PROMPT.md           # Setup instructions
└── TEMPLATE_SUMMARY.md       # This file
```

### 5. Key Features

#### Token Management

- Automatic token counting with tiktoken
- Alerts at 90k tokens (context window: 200k)
- Recommended limit: 50k tokens for optimal performance
- Context pruning for oversized files

#### Multi-Agent Support

- Specialized agent templates
- Progress tracking across sessions
- Shared memory for coordination
- Clear handoff procedures

#### Development Workflow

- TDD approach with test-first development
- Automated quality checks (format, lint, typecheck)
- Git workflow integration
- CI/CD ready

### 6. Quick Start Commands

```bash
# Setup
just quickstart          # Complete setup
just install-tools       # Install fd, trash, rg

# Development
just dev                 # Start development
just test               # Run tests
just quality            # Code quality checks

# Context Management
just context-health      # Check health
just context-analyze     # Analyze usage
just context-prune       # Optimize context
just token-monitor       # Live monitoring

# Progress Tracking
just progress-update     # Update task status
just context-resume      # Resume session

# Git Workflow
just feature my-feature  # Create branch
just ucp "message"       # Commit & push
```

### 7. Best Practices Enforced

1. **Context under 50k tokens** - Prevents performance degradation
2. **Modular documentation** - Split large files automatically
3. **No forbidden commands** - fd/trash/rg only
4. **Frequent /clear** - Between unrelated tasks
5. **Session management** - Track progress across sessions
6. **"ultrathink" usage** - For complex problems

### 8. Customization Points

- Edit CLAUDE.md for project-specific instructions
- Add custom agent templates
- Extend justfile with project recipes
- Configure .env with your settings
- Add project-specific Python dependencies

### 9. Why This Template?

- **Optimized for Claude Code** - Follows all best practices
- **Token efficient** - Prevents context overload
- **Developer friendly** - Automated workflows
- **Safety first** - No destructive commands
- **Extensible** - Easy to customize

### 10. AI-Powered GitHub Workflows

The template includes sophisticated GitHub workflows:

#### Included Workflows

1. **claude-code-integration.yml** - Respond to @claude mentions
2. **context-health-check.yml** - Monitor token usage and context health
3. **doc-synthesis.yml** - Auto-generate documentation from changes
4. **ai-pr-review.yml** - AI-powered code review with Claude
5. **ci.yml** - Standard CI/CD pipeline

#### Key Features

- Automated PR reviews checking for forbidden commands
- Context size monitoring and alerts
- Documentation auto-generation
- Token usage tracking
- Command enforcement (fd/trash/rg)

#### Configuration

- `.new-project/workflows/config.yaml` - Centralized workflow config
- Customizable review criteria
- Token limit enforcement
- Security scanning

### 11. Getting Help

- Use SETUP_PROMPT.md for Claude to help setup
- Check .claude/shared/critical-rules.md for command usage
- Run `just` to see all available commands
- Monitor with `just context-health` regularly
- Review workflow logs in GitHub Actions

This template represents the distilled best practices from the abundance-mvp project, optimized specifically for Claude Code development workflows with integrated AI assistance.
