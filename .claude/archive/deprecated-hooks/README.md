# Deprecated Hooks (Archived 2025-11-13)
Last Updated: 2025-11-19 20:27:56 UTC

## Why Deprecated

These hooks were disabled during Claude infrastructure modernization because they:
- Depend on deprecated systems (context-map.json, custom modules)
- Duplicate native Claude Code features
- Conflict with official plugin functionality

## Hooks Archived

### context-validator.py
**Original Purpose**: Validate context structure and token usage based on context-map.json

**Why Deprecated**:
- Depends on context-map.json (now deprecated)
- Validates module files (custom modules system deprecated)
- Native Claude Code handles context validation automatically

**Replacement**: Native Claude Code context management

### token-limiter.py
**Original Purpose**: Enforce token limits on file edits

**Why Deprecated**:
- Depends on context-map.json for limits configuration
- Duplicates native Claude Code token management
- Native system has better understanding of full context
- May interfere with legitimate large file operations

**Replacement**: Native Claude Code token management

### subagent-state-tracker.py
**Original Purpose**: Track sub-agent work and state, save agent logs

**Why Deprecated**:
- Tracks deprecated "sub-agent" patterns
- Superpowers plugin has built-in agent tracking
- Potential conflicts with native Task tool behavior
- Adds overhead to every Task invocation

**Replacement**: Superpowers plugin native agent tracking

## Migration

No action needed - these hooks were already disabled in settings.json before archiving.

Native Claude Code features automatically provide:
- Context validation and management
- Token tracking and limits
- Agent state management (via superpowers)

## Historical Reference

Files preserved for reference only. Do not re-enable without:
1. Updating dependencies to remove context-map.json references
2. Verifying no conflicts with native features
3. Testing thoroughly in isolation

See `docs/research/hook-audit-results.md` for detailed audit analysis.
