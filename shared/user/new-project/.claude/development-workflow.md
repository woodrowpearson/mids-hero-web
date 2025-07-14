# Development Workflow

## Standard Development Process

```bash
# 1. Start your day
just sync              # Sync with upstream
just context-resume    # Check context management status
just dev              # Start dev server

# 2. Create feature branch
just feature issue-123-description

# 3. Development cycle (TDD)
# Write tests first
just test-match test_new_feature

# Implement feature
# ... code changes ...

# Run quality checks
just quality          # format + lint + typecheck

# 4. Test thoroughly
just test             # Run all tests
just test-cov         # Check coverage

# 5. Commit and push
just ucp "feat: add new feature"

# 6. Before PR
just validate         # Run all validation
just ci-local        # Run CI checks locally
```

## Context Management During Development

### Monitor Token Usage
```bash
just token-monitor    # Real-time monitoring
just context-health   # Health check
```

### When Context Gets Large
```bash
just context-analyze  # See what's taking space
just context-prune    # Remove unnecessary context
just optimize-context # Full optimization
```

### Multi-Session Work
```bash
# Save progress before ending session
just progress-update --task "current-task"

# Resume in new session
just context-resume
```

## Best Practices

1. **Frequent Commits**: Commit small, logical changes
2. **Clear Messages**: Use conventional commits (feat:, fix:, docs:, etc.)
3. **Test First**: Write tests before implementation
4. **Monitor Context**: Keep under 50k tokens
5. **Use Scratch**: Experiment in `.agent-scratch/`

## Debugging

```bash
just logs 100 error   # Check error logs
just dev-debug        # Start with debugger
just env-info        # Check environment
```

## Code Style

- Follow existing patterns in the codebase
- Use type hints for Python
- Keep functions focused and small
- Document complex logic
- No comments unless specifically requested