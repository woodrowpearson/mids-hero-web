# Context Management Workflow Integration
Last Updated: 2025-08-25 00:00:00 UTC

## Current Integration Status

### ✅ What's Integrated

1. **Manual Commands Available**
   ```bash
   just context-check      # Full context validation
   just context-validate   # Validate structure and limits
   just token-analyze      # Analyze token usage
   ```

2. **Automation Hooks Defined**
   - Session start hook: `.claude/automation/hooks/session-start-hook.sh`
   - Context monitor hook: `.claude/automation/hooks/context-monitor-hook.sh`
   - Session end hook: `.claude/automation/hooks/session-end-hook.sh`

3. **Configuration Ready**
   - Settings.json includes automation_hooks section
   - Context-map.json defines all rules and limits

### ✅ What's NOW Integrated

**Claude Code DOES have hooks support** as of 2025! Our implementation includes:
- **UserPromptSubmit**: Validates context on each user input
- **PreToolUse**: Enforces token limits and logs activity
- **PostToolUse**: Tracks file modifications
- **Stop**: Generates session summaries

### 📋 Current Workflow

#### Automated Integration (ACTIVE NOW) ✨
1. **On user prompt** → Runs context validation automatically
2. **Before file edits** → Checks token limits and blocks if exceeded
3. **During work** → Logs all tool usage automatically
4. **After file changes** → Records modifications
5. **At session end** → Generates activity summary

#### Manual Commands (Still Available)
```bash
# Manual health checks (optional)
just context-check       # Full validation and analysis
just context-validate    # Structure validation
just token-analyze       # Token usage analysis

# View logs
cat .claude/state/logs/activity.jsonl      # Tool usage
cat .claude/state/logs/file-changes.log    # File modifications
cat .claude/state/session-stats.json       # Session statistics
```

## How to Use Context Management Today

### 1. **Beginning a Session**
```bash
# Traditional start
just health

# With context validation
just context-check
```

### 2. **During Development**
```bash
# Check if approaching limits
just token-analyze .claude/

# Validate after adding files
just context-validate
```

### 3. **Using the Scratchpad**
```bash
# Edit scratchpad for notes
edit .claude/state/scratchpad.md

# It's automatically cleared on session start (if hooks run)
```

### 4. **Monitoring Context Health**
```bash
# Quick check
just context-check

# Detailed analysis
python scripts/context/validate_context.py
```

## Integration Points

### 1. **GitHub Actions** (Recommended)
```yaml
# .github/workflows/context-check.yml
name: Context Health Check
on:
  push:
    paths:
      - '.claude/**'
      - 'CLAUDE.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install tiktoken
      - run: just context-validate
```

### 2. **Pre-commit Hook**
```bash
# .git/hooks/pre-commit
#!/bin/bash
just context-validate || {
    echo "Context validation failed!"
    exit 1
}
```

### 3. **VS Code Task**
```json
// .vscode/tasks.json
{
  "label": "Claude Context Check",
  "type": "shell",
  "command": "just context-check",
  "problemMatcher": []
}
```

## Future Enhancements

### When Claude Code Adds Hook Support
1. Hooks will run automatically
2. Real-time token monitoring
3. Automatic summarization at 50K tokens
4. Context quarantine for different tasks

### What Would Change
- No manual commands needed
- Automatic validation on start
- Real-time warnings
- Session summaries generated

## Best Practices Now

1. **Run `just context-check` periodically**
   - Especially after adding new documentation
   - Before major context reorganization

2. **Monitor token usage**
   - Run `just token-analyze` when context feels heavy
   - Use `/clear` proactively

3. **Use the scratchpad**
   - Edit `.claude/state/scratchpad.md` for temporary notes
   - Move important info to proper docs

4. **Check validation before commits**
   - Ensure no files exceed limits
   - Verify required files exist

## Summary

The context management system is **built and ready** but requires **manual execution** until Claude Code adds native hook support. The scripts work today - they're just not automatically triggered by Claude Code sessions.

Use the `just` commands to maintain healthy context!