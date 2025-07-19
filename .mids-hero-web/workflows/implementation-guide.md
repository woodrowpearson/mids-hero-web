# AI Workflows Implementation Guide - Mids Hero Web

This guide explains how to set up and customize the AI-powered workflows for the Mids Hero Web project.

## Overview

The workflows provide City of Heroes-aware automation:

- Automated PR reviews with Claude (understands CoH mechanics)
- Documentation synthesis for epic progress
- Context health monitoring (50k token limits)
- Command usage enforcement (uv, fd, trash, just)
- Epic 2 blocker tracking

## Setup

### 1. GitHub Secrets

Add this secret to your repository (Settings → Secrets and variables → Actions):

```
ANTHROPIC_API_KEY - Your Anthropic API key for Claude
```

### 2. Enable Workflows

The workflows are now in `.github/workflows/`. They will activate automatically on:
- Pull requests
- Issue comments mentioning @claude
- Scheduled context health checks

### 3. Configuration

Edit `.new-project/workflows/config.yaml` to customize for your needs:

- Epic tracking settings
- Code review criteria  
- Token limits
- City of Heroes domain validation

## Workflow Descriptions

### ci.yml
- **Purpose**: Continuous integration for full-stack project
- **Features**: 
  - Backend: uv-based Python testing with PostgreSQL
  - Frontend: Node.js testing and linting
  - Docker build validation
  - Just command testing
- **City of Heroes specific**: Database integration tests

### context-health-check.yml
- **Purpose**: Monitors Claude Code context health
- **Features**:
  - CLAUDE.md size validation (<5k tokens)
  - Total context monitoring (<50k tokens)
  - Command compliance checking
  - Epic progress validation
- **Schedule**: Every 6 hours + on PRs

### ai-pr-review.yml
- **Purpose**: AI-powered code review with CoH domain knowledge
- **Features**:
  - Code quality analysis
  - Epic alignment checking
  - City of Heroes mechanics validation
  - Command compliance enforcement
  - Architecture pattern validation
- **Trigger**: PRs and `/ai-review` comments

### claude-code-integration.yml
- **Purpose**: @claude mentions in issues/PRs
- **Features**:
  - Question answering about the codebase
  - City of Heroes mechanics help
  - Epic progress guidance
  - Command suggestions
- **Trigger**: Comments containing `@claude`

### doc-synthesis.yml
- **Purpose**: Automated documentation updates
- **Features**:
  - Detects when docs need updating
  - Suggests README/CLAUDE.md changes
  - Epic progress documentation
  - API documentation updates
- **Trigger**: Code changes in PRs

## Mids Hero Web Specific Features

### Epic Tracking
- Monitors progress through the 6-epic roadmap
- Epic 2 (data import) now 90% complete with I12 parser
- Tracks I12 streaming parser performance metrics
- Updates epic status files automatically
- Prepares for Epic 3 (Backend API) transition

### City of Heroes Domain Validation
- Validates archetype definitions
- Checks power mechanics accuracy
- Ensures enhancement calculations are correct
- Verifies database model consistency
- Validates I12 power data import accuracy
- Checks streaming parser performance targets
- Ensures cache optimization for 360K+ power records

### Tech Stack Enforcement
- **Backend**: Enforces uv over pip usage
- **Frontend**: Validates React/TypeScript patterns
- **Database**: Ensures PostgreSQL best practices
- **Import System**: Validates I12 streaming parser performance
- **Caching**: Checks Redis integration and multi-tier caching
- **Commands**: Requires just, fd, trash usage

## Command Enforcement

The workflows enforce these Mids Hero Web standards:

✅ **Required Commands**:
- `uv` for Python package management
- `fd` for file searching  
- `trash` for safe file deletion
- `just` for development workflows
- `just import-*` for data import operations
- `just i12-*` for high-performance power data import
- `just cache-*` for cache management
- `just perf-*` for performance testing

❌ **Forbidden Commands**:
- `pip install` (use `uv add`)
- `find` (use `fd`)
- `rm -rf` (use `trash`)
- Direct script execution (use `just`)

## Token Management

Context limits enforced for optimal Claude Code usage:

- **CLAUDE.md**: 5,000 tokens maximum
- **Total project context**: 50,000 tokens recommended
- **Warning threshold**: 45,000 tokens (90%)
- **Critical threshold**: 47,500 tokens (95%)

## Customization for Your Workflow

### Adding Epic-Specific Checks

To add validation for specific epics:

```yaml
# In .new-project/workflows/config.yaml
mids_hero_web:
  epic_tracking:
    custom_checks:
      epic_3:
        - "Check API endpoint consistency"
        - "Validate Pydantic schemas"
      epic_4:
        - "Check React component patterns"
        - "Validate TypeScript interfaces"
```

### Modifying Review Criteria

Customize the AI review focus in `config.yaml`:

```yaml
review_focus:
  - "Your specific requirement 1"
  - "Your specific requirement 2"
  - "Database model accuracy for City of Heroes data"  # Keep this
```

### Changing Token Limits

Adjust context management in `config.yaml`:

```yaml
context_management:
  max_file_tokens: 5000      # Individual file limit
  total_context_limit: 50000  # Total project limit
  claude_md_limit: 5000      # CLAUDE.md specific limit
```

## Troubleshooting

### Workflow Not Triggering

1. **Check permissions**: Ensure `ANTHROPIC_API_KEY` is set
2. **Verify branch protection**: Make sure workflows can run on your branches
3. **Check syntax**: Validate YAML syntax in workflow files

### AI Review Not Working

1. **API Key**: Verify your Anthropic API key is valid and has credits
2. **Rate limits**: Check if you're hitting API rate limits
3. **File size**: Large diffs may be truncated automatically

### Token Limit Warnings

1. **Run pruning**: `just context-prune` to clean up
2. **Split files**: Break large documentation into smaller files
3. **Use .claudeignore**: Exclude large files from context

### Epic Progress Not Updating

1. **Check file paths**: Ensure `.claude/epics/` files exist
2. **Validate format**: Epic files should follow the established format
3. **Manual update**: Use `just progress-update` to sync manually

## Integration with Development Workflow

These workflows integrate seamlessly with daily development:

1. **Create PR** → CI runs, context checked, AI review posted
2. **Ask questions** → Mention @claude for instant help
3. **Update code** → Documentation suggestions automatically generated
4. **Epic progress** → Tracked and reported in PR comments

## Best Practices

### For Developers
1. **Keep CLAUDE.md under 5k tokens** - Critical for performance
2. **Use just commands** - Ensures consistency across team
3. **Update epic progress** - Use `just progress-update` regularly
4. **Ask Claude questions** - Use @claude mentions liberally

### For Maintainers
1. **Monitor context health** - Check weekly reports
2. **Review AI suggestions** - Don't auto-merge, always review
3. **Update configuration** - Adjust thresholds as project grows
4. **Epic milestone tracking** - Keep roadmap updated

## Support

For issues with the AI workflows:

1. **Check workflow logs** in GitHub Actions tab
2. **Review configuration** in `.new-project/workflows/config.yaml`
3. **Run diagnostics**: `just context-health`
4. **Check epic status**: `just epic-status`

## City of Heroes Community Notes

These workflows are designed specifically for the Mids Hero Web project:

- **Accuracy first**: AI validates game mechanics against known standards
- **Community feedback**: Workflows suggest getting community input on mechanics changes
- **Legacy compatibility**: Ensures compatibility with original Mids Reborn expectations
- **Server variations**: Prepared for Homecoming/Rebirth server differences

The AI assistant understands City of Heroes terminology and can help with:
- Archetype and powerset relationships
- Enhancement set bonus calculations  
- Build validation rules
- Game data import formats
- Community standards and expectations