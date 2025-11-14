# Hook Audit Results

**Date**: 2025-11-13
**Against**: Official Anthropic Claude Code best practices

## Executive Summary

**KEEP**: 1 hook (git-commit-hook.sh)
**MODIFY**: 1 hook (activity-logger.py - remove context-map dependency)
**REMOVE**: 3 hooks (context-validator.py, token-limiter.py, subagent-state-tracker.py)

---

## Hooks Reviewed

### activity-logger.py

**Purpose**: Logs tool usage and development activity for session tracking

**Current Implementation**:
- Tracks Bash commands, file edits, reads
- Writes to `.claude/state/logs/activity.jsonl`
- Updates session stats

**Compliance**: ⚠️ **MODIFY**

**Reasoning**:
- ✅ Legitimate logging use case
- ✅ Runs in background (doesn't block)
- ✅ Proper JSON I/O handling
- ❌ May reference context-map.json for stats (needs verification)
- ✅ Useful for debugging and session analysis

**Recommendation**: Keep but verify no dependencies on deprecated context-map.json

---

### context-validator.py

**Purpose**: Validates context structure and token usage based on context-map.json rules

**Current Implementation**:
- Loads `.claude/context-map.json` for configuration
- Checks CLAUDE.md token count against limits
- Validates module files against token limits
- Uses tiktoken for token counting

**Compliance**: ❌ **REMOVE**

**Reasoning**:
- ❌ Depends on context-map.json (being deprecated)
- ❌ Validates modules system (being deprecated)
- ❌ Duplicates native Claude Code context management
- ❌ Token validation should be native, not custom
- ❌ References `.claude/modules/` which we're archiving

**Migration Path**: Remove entirely. Native Claude Code handles context validation.

---

### git-commit-hook.sh

**Purpose**: Prevents direct commits to main branch, enforces branch naming conventions

**Current Implementation**:
- Checks current branch
- Blocks commits to main with exit 1
- Warns about branch naming conventions
- Provides helpful error messages

**Compliance**: ✅ **KEEP**

**Reasoning**:
- ✅ Safety feature (prevents accidental main commits)
- ✅ Proper exit codes (1 for blocking)
- ✅ Clear error messages with guidance
- ✅ Doesn't interfere with native features
- ✅ Aligns with project workflow (CLAUDE.md requires feature branches)
- ✅ Simple bash script, no complex dependencies

**Recommendation**: Keep as-is. This is a valuable safety hook.

---

### subagent-state-tracker.py

**Purpose**: Tracks sub-agent work and state, saves agent logs and summaries

**Current Implementation**:
- Extracts agent type from Task tool
- Saves state to `.claude/state/agents/`
- Creates task IDs and tracks history
- Logs agent-specific state files

**Compliance**: ❌ **REMOVE**

**Reasoning**:
- ❌ Tracks "sub-agents" concept which may be outdated
- ❌ Modern superpowers plugin has built-in agent tracking
- ❌ Creates complex state management outside native system
- ❌ Potential conflicts with native Task tool behavior
- ❌ Adds overhead to every Task invocation
- ⚠️ May be tracking deprecated agent patterns

**Migration Path**: Remove. Superpowers plugin handles agent state natively.

---

### token-limiter.py

**Purpose**: Enforces token limits on file edits

**Current Implementation**:
- Checks file content token count before writes
- Loads limits from context-map.json
- Uses tiktoken for counting
- Blocks edits exceeding limits

**Compliance**: ❌ **REMOVE**

**Reasoning**:
- ❌ Depends on context-map.json (being deprecated)
- ❌ Duplicates native Claude Code token management
- ❌ Native system better understands token context
- ❌ May interfere with legitimate large file operations
- ❌ False sense of control (doesn't account for full context)

**Migration Path**: Remove. Native Claude Code manages tokens automatically.

---

## Recommendations

### KEEP

**git-commit-hook.sh**:
- Essential safety feature
- No conflicts with native features
- Aligns with project workflow
- Already properly configured in settings.json

### MODIFY

**activity-logger.py**:
- Useful for debugging and analysis
- Verify no context-map.json dependencies
- If clean, keep as logging tool
- If dependencies exist, remove references to deprecated systems

### REMOVE

**context-validator.py**:
- Reason: Depends on deprecated context-map.json and modules
- Action: Disable in settings.json, move to archive
- Migration: Native context validation

**token-limiter.py**:
- Reason: Depends on deprecated context-map.json, duplicates native features
- Action: Disable in settings.json, move to archive
- Migration: Native token management

**subagent-state-tracker.py**:
- Reason: Tracks deprecated patterns, conflicts with superpowers
- Action: Disable in settings.json, move to archive
- Migration: Superpowers native agent tracking

---

## Implementation Plan

### Step 1: Verify activity-logger.py

Check if it references context-map.json:
```bash
rg 'context-map|context_map' .claude/hooks/activity-logger.py
```

If clean, keep. If dependencies exist, remove them or disable hook.

### Step 2: Disable hooks in settings.json

Remove or comment out:
- context-validator.py (UserPromptSubmit)
- token-limiter.py (PreToolUse Edit|MultiEdit|Write)
- subagent-state-tracker.py (PreToolUse Task)

Keep only:
- bash_command_validator.py (PreToolUse Bash) - NEW
- git-commit-hook.sh (PreToolUse Bash(git commit:*)) - EXISTING
- activity-logger.py (various) - IF CLEAN

### Step 3: Archive deprecated hooks

```bash
mkdir -p .claude/archive/deprecated-hooks
mv .claude/hooks/context-validator.py .claude/archive/deprecated-hooks/
mv .claude/hooks/token-limiter.py .claude/archive/deprecated-hooks/
mv .claude/hooks/subagent-state-tracker.py .claude/archive/deprecated-hooks/
```

### Step 4: Create archive README

Document why hooks were deprecated and migration path.

---

## Benefits of Cleanup

**Reduced Complexity**:
- 3 fewer hooks to maintain
- No dependencies on deprecated systems
- Clearer what's custom vs native

**Better Performance**:
- Fewer hooks = faster tool execution
- No redundant validation
- Native features are optimized

**Alignment with Best Practices**:
- Rely on native context/token management
- Use official plugin systems for agents
- Keep only project-specific safety features

**Maintainability**:
- Less custom code to update
- Native features updated by Anthropic
- Clear separation of concerns

---

## Testing After Cleanup

1. **Verify git safety still works**: Try committing to main (should block)
2. **Verify bash validator works**: Try using grep (should block)
3. **Verify activity logging works** (if kept): Check `.claude/state/logs/`
4. **Verify no errors**: Start new session, no hook errors
5. **Verify performance**: Tool execution feels responsive

---

## Conclusion

Of 5 existing hooks:
- **1 KEEP**: git-commit-hook.sh (safety feature)
- **1 VERIFY**: activity-logger.py (useful if clean)
- **3 REMOVE**: context-validator, token-limiter, subagent-state-tracker (depend on deprecated systems)

This cleanup aligns with official Anthropic practices: rely on native features, keep only project-specific customizations.
