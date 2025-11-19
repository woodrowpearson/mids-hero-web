# .claude/ Directory
Last Updated: 2025-11-19 20:27:56 UTC

**Purpose**: Claude Code configuration and project-specific customization

**Last Updated**: 2025-11-13

## Structure

```
.claude/
├── skills/                    # Project-specific skills
│   └── frontend-development/  # Frontend orchestration skill
├── commands/                  # Slash commands
│   ├── code-review.md        # PR review automation
│   └── update-changelog.md   # Changelog management
├── hooks/                     # Event hooks
│   ├── bash_command_validator.py  # Command standards enforcement
│   ├── git-commit-hook.sh         # Git safety checks
│   └── activity-logger.py         # Development activity logging
├── workflows/                 # Workflow documentation
│   ├── claude/               # Claude-specific workflows
│   └── github/               # GitHub Actions docs
├── archive/                   # Deprecated/archived files
│   ├── deprecated-modules/   # Old custom context system
│   ├── deprecated-context-map.json  # Old context config
│   └── old-state/            # Historical state files
├── settings.json             # Claude Code configuration
├── settings-backup-2025-11-13.json  # Pre-modernization backup
└── README.md                 # This file
```

## Official Plugins

This project uses official Anthropic plugins:

- **superpowers** - Planning and execution workflow
- **frontend-design** - Distinctive UI generation (via superpowers)
- **code-review** - Automated PR review (via superpowers)

Access via global plugin cache, not project-local.

## Custom Configuration

### Skills
- `skills/frontend-development/` - Orchestrates frontend epic development

### Commands
- `/code-review` - Multi-agent PR review with confidence scoring
- `/update-changelog` - Manage CHANGELOG.md entries

### Hooks
- **Bash command validator** - Enforces `fd`, `rg`, `trash`, `uv` usage
- **Git commit hook** - Prevents direct commits to `main`
- **Activity logger** - Tracks development activity for session insights

## Removed/Deprecated

**As of 2025-11-13**:
- ❌ Custom modules system → Native context loading
- ❌ context-map.json → Native automatic context
- ❌ Custom token management → Native management
- ❌ Manual context triggers → Claude decides context
- ❌ context-validator.py → Native validation
- ❌ token-limiter.py → Native token management
- ❌ subagent-state-tracker.py → Superpowers native tracking

See `archive/deprecated-modules/README.md` for migration details.

## Development Workflow

**Frontend Development**:
1. Tell Claude: "start epic 1.1" or describe frontend task
2. Claude invokes `skills/frontend-development/`
3. Workflow: Plan → Approve → Execute → Review

**Code Review**:
1. Create PR
2. Tell Claude: `/code-review`
3. Multi-agent review with confidence-scored feedback

**Changelog**:
1. Tell Claude: "update changelog for version X.Y.Z"
2. Follows Keep a Changelog format

## Best Practices

- ✅ Rely on native Claude Code features for context
- ✅ Use official plugins when available
- ✅ Keep configuration simple
- ✅ Document custom hooks/commands
- ❌ Don't create custom context-loading systems
- ❌ Don't manually manage tokens/context

## Resources

- [Claude Code Documentation](https://code.claude.com/docs/)
- [Superpowers Plugin](https://github.com/chadmcrowell/superpowers)
- [Research: Best Practices](../docs/research/claude-code-best-practices.md)
- [Research: Hook Audit](../docs/research/hook-audit-results.md)
