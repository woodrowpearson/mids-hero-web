# Claude Custom Commands

This directory contains custom commands for Claude to automate common workflows.

## Available Commands

### 1. `update-progress.sh` - Full Update, Commit, and Push
Comprehensive command that updates refactor progress, commits all changes, and pushes to remote.

**Usage:**
```bash
# Claude can run this with:
.claude/commands/update-progress.sh
```

**Features:**
- Checks you're on a feature branch (not main/develop)
- Stages all changes
- Updates refactor progress for new/modified files
- Auto-generates meaningful commit messages
- Pushes to remote (sets upstream if needed)
- Shows PR information if available

### 2. `ucp.sh` - Quick Update-Commit-Push
Shortened version for quick updates.

**Usage:**
```bash
# With custom commit message
.claude/commands/ucp.sh "feat: Add new feature"

# With auto-generated message
.claude/commands/ucp.sh
```

**Features:**
- Ultra-fast execution
- Optional commit message
- Auto-updates refactor progress
- Minimal output

## Claude Integration

These commands are pre-approved in `.claude/settings.local.json`, so Claude can run them without asking for permission each time.

## Examples

### When Claude should use `update-progress.sh`:
- After completing a major task
- When you specifically ask to "update refactor progress and commit changes and push"
- Before switching to a new task
- When detailed feedback is wanted

### When Claude should use `ucp.sh`:
- Quick saves during work
- Minor updates
- When you say "quick commit and push"
- Frequent checkpoint commits

## Adding New Commands

1. Create script in this directory
2. Make it executable: `chmod +x command-name.sh`
3. Add to `.claude/settings.local.json`:
   ```json
   "Bash(.claude/commands/command-name.sh:*)"
   ```

## Best Practices

- Always use `set -euo pipefail` for safety
- Add colors for better visibility
- Handle edge cases gracefully
- Provide clear feedback
- Keep commands focused on single purpose