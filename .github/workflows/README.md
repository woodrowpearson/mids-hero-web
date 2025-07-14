# GitHub Workflows for Mids Hero Web

This directory contains AI-powered workflows specifically designed for the Mids Hero Web project.

## Active Workflows

### 🔄 ci.yml
**Continuous Integration** - Full-stack testing and validation
- Backend: Python 3.11 + uv + PostgreSQL testing
- Frontend: React + TypeScript + Node.js testing
- Docker build validation
- Just command testing

### 🏥 context-health-check.yml
**Context Health Monitoring** - Ensures optimal Claude Code performance
- Monitors CLAUDE.md size (<5k tokens)
- Tracks total context usage (<50k tokens)
- Validates command compliance
- Runs every 6 hours + on PRs

### 🤖 ai-pr-review.yml
**AI Code Review** - Claude-powered PR analysis with CoH domain knowledge
- Code quality and architecture review
- City of Heroes mechanics validation
- Epic alignment checking
- Command compliance enforcement

### 💬 claude-code-integration.yml
**Claude Assistant** - Interactive help via @claude mentions
- Answers questions about codebase
- Provides City of Heroes mechanics guidance
- Suggests improvements and fixes
- Epic progress assistance

### 📚 doc-synthesis.yml
**Documentation Automation** - Keeps docs in sync with code
- Suggests README updates for API changes
- Updates CLAUDE.md for workflow changes
- Tracks epic progress documentation
- Maintains architecture docs

## Configuration

All workflows are configured via `.new-project/workflows/config.yaml`:

```yaml
# Example settings
context_management:
  max_file_tokens: 5000
  total_context_limit: 50000

mids_hero_web:
  current_epic: 2
  blocker_check: true
```

## Usage Examples

### Getting AI Code Review
Just create a PR - review happens automatically. For additional review:
```
Comment: /ai-review
```

### Asking Claude Questions
In any issue or PR:
```
@claude How should I structure the power calculation system?
@claude What's the status of Epic 2 data import?
@claude How do I add a new archetype to the database?
```

### Manual Documentation Update
```
Trigger the doc-synthesis workflow manually from Actions tab
```

## Setup Requirements

1. **GitHub Secret**: Add `ANTHROPIC_API_KEY` to repository secrets
2. **Branch Protection**: Enable for main branch (recommended)
3. **Permissions**: Workflows need read/write access to PRs and issues

## Mids Hero Web Specific Features

### Epic Tracking
- Monitors 6-epic roadmap progress
- Alerts on Epic 2 blocker status
- Updates progress automatically

### City of Heroes Domain
- Validates archetype definitions
- Checks power mechanics accuracy
- Ensures database model consistency

### Command Enforcement
- Requires `uv` instead of `pip`
- Enforces `fd` instead of `find`
- Mandates `trash` instead of `rm -rf`
- Prefers `just` commands

## Monitoring & Maintenance

### Weekly Tasks
- [ ] Check context health report
- [ ] Review AI suggestion accuracy
- [ ] Update epic progress if needed
- [ ] Monitor token usage trends

### Monthly Tasks
- [ ] Review workflow configuration
- [ ] Update token limits if needed
- [ ] Check AI model performance
- [ ] Update City of Heroes validation rules

## Troubleshooting

### Common Issues

**Workflow not triggering:**
- Check ANTHROPIC_API_KEY is set
- Verify branch protection settings
- Ensure workflow permissions are correct

**AI responses not appearing:**
- Check API key validity and credits
- Verify rate limits aren't exceeded
- Check workflow logs for errors

**Context warnings:**
- Run `just context-prune`
- Split large documentation files
- Update .claudeignore if needed

**Epic tracking issues:**
- Verify .claude/epics/ files exist
- Check file format consistency
- Run `just progress-update` manually

### Getting Help

1. Check workflow logs in Actions tab
2. Review `.new-project/workflows/implementation-guide.md`
3. Run `just health` for local diagnostics
4. Ask @claude in an issue for specific help

## Development

When modifying workflows:

1. **Test in feature branch first**
2. **Keep City of Heroes context** - AI needs domain knowledge
3. **Maintain token efficiency** - Don't inflate context
4. **Update configuration docs** when changing settings
5. **Test with real PRs** before merging

## Community

These workflows are designed for the City of Heroes community:
- **Accuracy**: Validates game mechanics against known standards
- **Legacy**: Maintains compatibility with Mids Reborn expectations  
- **Servers**: Supports both Homecoming and Rebirth variations
- **Community input**: Encourages feedback on mechanics changes