# Quick Commands Reference

## Essential Commands

```bash
just              # Show all available commands
just quickstart   # Complete setup for new developers
just dev          # Start development server
just test         # Run tests
just quality      # Run code quality checks
just ucp "msg"    # Commit and push
```

## Context Management

```bash
just context-health      # Check context health
just context-analyze     # Analyze token usage
just context-prune       # Remove oversized contexts
just context-resume      # Resume session with status
just optimize-context    # Full optimization workflow
just token-monitor       # Real-time token monitoring
```

## Development

```bash
just dev-port 3000      # Start on custom port
just dev-debug          # Start with debugger
just logs 50 backend    # View logs
just shell              # Python REPL
just docs               # Build/serve documentation
```

## Testing

```bash
just test               # Run all tests
just test-match auth    # Run tests matching pattern
just test-cov           # Run with coverage
just test-fast          # Run fast tests only
just test-watch         # Watch mode
```

## Code Quality

```bash
just lint               # Run linting with fixes
just format             # Format code
just typecheck          # Type checking
just validate           # All validation checks
just security           # Security scan
just complexity         # Analyze complexity
```

## Git Workflows

```bash
just feature my-feature    # Create feature branch
just sync                  # Sync with upstream
just release 1.0.0        # Create release
just pre-commit           # Run pre-commit hooks
```

## Agent Development

```bash
just init-agent assistant  # Create new agent
just run-agent assistant "task description"
just monitor              # Launch monitoring dashboard
just cost-analysis 7d     # Analyze AI costs
```

## Maintenance

```bash
just clean              # Remove generated files
just reset              # Reset environment
just backup             # Create backup
just deps-check         # Check outdated deps
just deps-update        # Update dependencies
```

## CI/CD

```bash
just ci                 # Run CI pipeline
just ci-local          # Local CI checks
just build             # Build for production
just package           # Build package
```