# Quick Command Reference

## 🚦 Session Start
```bash
just health                        # REQUIRED before work
just dev                          # Start all services
/project:session-start issue-123  # Track work session
```

## 💻 Development
```bash
just test                # Run all tests
just test-watch         # Watch mode
just lint-fix          # Auto-fix issues  
just quality           # All checks
just build             # Build project
```

## 📦 Git Workflow
```bash
just git-validate          # Check workflow status
just git-feature NAME      # Create feature branch
just git-fix NAME          # Create fix branch
just ucp "feat: message"   # Quick commit & push
just update-progress       # Full update workflow
just git-pr                # Create pull request
```

## 🗄️ Database
```bash
just db-migrate                      # Apply migrations
just db-migration-create "name"      # New migration
just db-reset                       # Reset database
just db-shell                       # PostgreSQL shell
```

## 📥 Import System
```bash
just import-health              # System health check
just import-stats              # Record counts
just i12-import file.json      # Import powers
just import-all dir/           # Import everything
```

## 🐛 Debugging
```bash
just logs backend          # View logs
just backend-shell        # Python REPL
docker-compose ps         # Check services
```

## 🧹 Maintenance
```bash
/clear                    # Clear context
just token-usage         # Check tokens
just cache-stats         # Cache performance
```

## 📝 Session Management
```bash
/project:session-update "progress note"  # Update session
/project:session-current                # Current status
/project:session-end                    # End session
```

---
*See `.claude/workflows/` for detailed procedures*