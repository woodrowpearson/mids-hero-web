# AI Workflows Implementation Guide

This guide explains how to set up and customize the AI-powered workflows for your project.

## Overview

The workflows provide:

- Automated PR reviews with Claude
- Documentation synthesis
- Context health monitoring
- Command usage enforcement
- Token usage tracking

## Setup

### 1. GitHub Secrets

Add these secrets to your repository:

```
ANTHROPIC_API_KEY - Your Anthropic API key for Claude
```

### 2. Enable Workflows

Workflows are stored in `.github/workflows/`. To enable:

1. Copy workflows to your repository
2. Customize as needed
3. Commit and push

### 3. Configuration

Edit `.new-project/workflows/config.yaml` to customize:

- Review criteria
- Documentation targets
- Token limits
- Command enforcement rules

## Workflow Descriptions

### claude-code-integration.yml

- Responds to `@claude` mentions in issues/PRs
- Provides code suggestions and answers questions
- Integrates with Claude Code patterns

### context-health-check.yml

- Monitors token usage across files
- Alerts when approaching limits
- Suggests optimizations
- Runs on schedule and PRs

### doc-synthesis.yml

- Auto-generates documentation for changes
- Updates README, API docs, etc.
- Commits changes back to PR

### ai-pr-review.yml

- Reviews code changes
- Checks for forbidden commands
- Validates context limits
- Posts detailed feedback

### ci.yml

- Standard CI checks (lint, test, build)
- Type checking
- Security scanning
- Coverage reporting

## Command Enforcement

The workflows enforce these commands:

- Use `fd` instead of `find`
- Use `trash` instead of `rm -rf`
- Use `rg` instead of `grep`

## Token Management

Context limits enforced:

- Individual files: 5,000 tokens
- Total context: 50,000 tokens
- Warning at 90% usage
- Critical at 95% usage

## Customization

### Adding New Checks

1. Edit the workflow YAML files
2. Add check logic in the appropriate job
3. Update config.yaml if needed

### Changing Token Limits

Edit `.new-project/workflows/config.yaml`:

```yaml
context_management:
  max_file_tokens: 5000
  total_context_limit: 50000
```

### Custom Review Prompts

Modify the review prompt in `ai-pr-review.yml` to focus on your project's specific needs.

## Troubleshooting

### Workflow Not Triggering

- Check workflow permissions
- Verify branch protection rules
- Ensure secrets are set

### Token Limit Exceeded

- Run `just context-prune`
- Split large files
- Use `.claudeignore`

### Review Not Posting

- Check API key is valid
- Verify PR permissions
- Check workflow logs

## Best Practices

1. **Regular Monitoring**: Check context health weekly
2. **Incremental Updates**: Keep changes focused
3. **Clear Documentation**: Update docs with code
4. **Token Awareness**: Monitor usage trends
5. **Command Compliance**: Always use safe commands

## Integration with Claude Code

These workflows are designed to work seamlessly with Claude Code:

1. Context stays within optimal limits
2. Commands match Claude Code requirements
3. Documentation follows Claude patterns
4. Memory persists across sessions

## Support

For issues or questions:

1. Check workflow logs in Actions tab
2. Review this guide
3. Check `.new-project/workflows/config.yaml`
4. Create an issue with details
