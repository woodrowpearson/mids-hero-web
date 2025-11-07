# GitHub Configuration

This directory contains GitHub-specific configuration including workflows, actions, and automation.

## 📁 Directory Structure

```
.github/
├── workflows/          # GitHub Actions workflows
│   ├── ci.yml          # Main CI/CD pipeline
│   ├── claude-unified.yml    # Claude AI code review
│   ├── doc-management.yml    # Documentation automation
│   ├── context-health-check.yml  # Context monitoring
│   ├── update-claude-docs.yml    # Doc updates
│   ├── reusable-*.yml        # Reusable workflow components
│   └── reusable-components-demo.yml  # Demo of reusable components
├── actions/            # Composite actions
│   ├── setup-project/  # Project environment setup
│   └── post-comment/   # PR/issue commenting
└── README.md           # This file
```

## 🤖 Active Workflows

See [workflows/README.md](workflows/README.md) for detailed workflow documentation.

### Main Workflows

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| **ci.yml** | CI/CD pipeline | Push, PR |
| **claude-unified.yml** | AI code review | PR, @claude mentions |
| **doc-management.yml** | Documentation sync | Code changes, schedule |
| **context-health-check.yml** | Monitor context health | Schedule, push |
| **update-claude-docs.yml** | Update Claude docs | Doc changes |

### Reusable Components

| Component | Purpose | Used By |
|-----------|---------|---------|
| **reusable-change-detection.yml** | Analyze file changes | Multiple workflows |
| **reusable-claude-setup.yml** | Claude AI integration | claude-unified, doc-management |
| **reusable-pr-context.yml** | Extract PR metadata | Multiple workflows |
| **reusable-token-validation.yml** | Validate token counts | doc-management |

See [Reusable Components Guide](../.claude/workflows/github/REUSABLE_COMPONENTS.md) for usage examples.

## 🚀 Quick Start

### For Developers

1. **Create PR** → Automatic CI + Claude review
2. **Ask Questions** → Comment `@claude [question]` on PR/issue
3. **Documentation** → Auto-updated when code changes

### For Maintainers

1. **Monitor Actions** → Check Actions tab
2. **Review Health** → Weekly context health reports
3. **Manual Sync** → Trigger doc-management workflow

## 📋 Setup Requirements

### Repository Secrets
- `ANTHROPIC_API_KEY` - Required for Claude features
- `CODECOV_TOKEN` - Optional for coverage reporting

### Branch Protection
- Enable required status checks
- Require PR reviews before merging

## 🔗 Related Documentation

- **[Workflows Documentation](workflows/README.md)** - Detailed workflow info
- **[Claude Context System](../.claude/README.md)** - AI configuration
- **[Project Guide](../CLAUDE.md)** - Main project documentation
- **[Reusable Components](../.claude/workflows/github/REUSABLE_COMPONENTS.md)** - Component usage guide

## ⚠️ Important Notes

1. Claude context system is at `.claude/` (repository root)
2. Configuration: `.claude/settings.json`
3. Token limits enforced for performance
4. All workflows use reusable components where possible

---

*For detailed workflow documentation, see [workflows/README.md](workflows/README.md)*
