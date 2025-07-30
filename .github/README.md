# GitHub Configuration

This directory contains GitHub-specific configuration including workflows, issue templates, and project documentation.

## 📁 Directory Structure

```
.github/
├── workflows/          # GitHub Actions workflows
│   ├── ci.yml         # Continuous Integration
│   ├── claude-*.yml   # Claude Code integrations
│   ├── doc-*.yml      # Documentation automation
│   └── ...
├── ISSUE_TEMPLATE/    # Issue templates (if any)
├── PULL_REQUEST_TEMPLATE/ # PR templates (if any)
└── README.md          # This file
```

## 🤖 GitHub Actions Workflows

Our workflows provide automated CI/CD, AI-powered code review, and documentation synchronization. See [workflows/README.md](.github/workflows/README.md) for detailed information.

### Active Workflows

1. **ci.yml** - Main CI/CD pipeline with tests, linting, and security scanning
2. **claude-auto-review.yml** - Automatic PR review using Claude
3. **claude-code-integration.yml** - Interactive Claude assistant via @claude mentions
4. **context-health-check.yml** - Monitors Claude context system health
5. **doc-auto-sync.yml** - Automatically updates documentation when code changes
6. **doc-review.yml** - Reviews PRs for documentation impact
7. **update-claude-docs.yml** - Updates Claude-specific documentation
8. **dataexporter-tests.yml** - Tests for the DataExporter module

## 🔧 Claude Context System

The Claude context system is located at `.claude/` in the repository root (not in `.github/`). It contains:

- **Progressive context loading** based on declared tasks
- **Token management** with automatic warnings
- **Native sub-agents** for specialized development tasks
- **Activity tracking** and session management

See [/.claude/README.md](/.claude/README.md) for complete documentation about the context system.

## 🚀 Workflow Features

### Continuous Integration
- Automated testing for backend (Python/FastAPI) and frontend (React/TypeScript)
- Code quality checks with ruff, black, ESLint
- Security scanning with Trivy
- PostgreSQL integration testing

### AI-Powered Development
- **PR Reviews**: Claude automatically reviews code changes
- **Interactive Help**: Use @claude in PR/issue comments for assistance
- **Documentation Sync**: Automatic updates when code changes
- **Context Health**: Monitors token usage and file sizes

### Documentation Automation
- **Smart Detection**: Identifies which docs need updates based on code changes
- **Auto-sync**: Updates README files, API docs, and Claude context
- **Token Validation**: Ensures CLAUDE.md stays under 5K tokens
- **Weekly Sync**: Full documentation consistency check

## 📋 Setup Requirements

1. **Repository Secrets**:
   - `ANTHROPIC_API_KEY` - Required for Claude features
   - `CODECOV_TOKEN` - Optional for coverage reporting

2. **Branch Protection**:
   - Enable status checks for `ci` workflow
   - Require PR reviews before merging

3. **Permissions**:
   - Workflows need write access to PRs and issues
   - Claude actions need content read permissions

## 💡 Usage Examples

### Getting AI Code Review
Simply create a PR - Claude will automatically review it. For additional review:
```
@claude Can you review the error handling in this PR?
```

### Asking Claude Questions
In any PR or issue comment:
```
@claude How should I implement the power calculation system?
@claude What's the current status of Epic 2?
```

### Manual Documentation Sync
Trigger the doc-auto-sync workflow manually from the Actions tab with "Force full sync" option.

## 🛠️ Development Guidelines

When modifying workflows:

1. **Test in feature branches** before merging
2. **Update workflow documentation** in `.github/workflows/README.md`
3. **Maintain backward compatibility** with existing PRs
4. **Monitor token usage** to prevent context overflow
5. **Follow security best practices** for secrets and permissions

## 📊 Monitoring

- **Workflow Runs**: Check Actions tab for execution history
- **Context Health**: Review weekly health check reports
- **Token Usage**: Monitor CLAUDE.md size warnings
- **Documentation Drift**: Check doc-auto-sync summaries

## 🔗 Related Documentation

- [Workflows Documentation](.github/workflows/README.md) - Detailed workflow information
- [Claude Context System](/.claude/README.md) - AI assistant configuration
- [Project Overview](/CLAUDE.md) - Main project guide
- [Development Workflow](/.claude/docs/development-workflow.md) - Development best practices

## ⚠️ Important Notes

1. The `.claude/` directory is at the repository root, not inside `.github/`
2. All Claude-related configuration is in `.claude/settings.json`
3. Workflow modifications may affect PR checks - test carefully
4. Token limits are enforced to maintain Claude performance

---

*For workflow-specific documentation, see [.github/workflows/README.md](.github/workflows/README.md)*