# Claude Infrastructure Modernization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Modernize `.claude/` infrastructure to align with Anthropic best practices, adopt official plugins, and eliminate custom context-loading systems.

**Architecture:** Replace custom modules/context-map system with official Anthropic plugins (frontend-design, code-review), implement proper bash command validation hooks, add CHANGELOG.md automation, and deprecate incompatible infrastructure.

**Tech Stack:**
- Anthropic Claude Code plugins (frontend-design, code-review)
- Python hooks (bash validator)
- Claude Code settings.json (official schema)
- Superpowers plugin (already integrated)

---

## Background

**Current State (from CLAUDE-INFRASTRUCTURE-REVIEW.md)**:
- Custom modules system (`.claude/modules/`) - pre-superpowers era
- Custom context-map.json with manual triggers
- 5 hooks of unknown compliance status
- Outdated content referencing deprecated workflows

**Target State**:
- Official Anthropic plugins where applicable
- Clean hooks following official examples
- No custom context loading (rely on Claude Code native)
- Documentation aligned with current workflow

---

## Task 1: Research Anthropic Documentation

**Objective**: Verify assumptions against official Claude Code documentation

**Files**:
- Create: `docs/research/claude-code-best-practices.md`

### Step 1: Research official hook documentation

**Action**: Use WebFetch or WebSearch to find Claude Code hooks documentation

**Search Query**: "Anthropic Claude Code hooks documentation official"

**Expected URLs**:
- https://docs.anthropic.com/en/docs/claude-code/hooks
- https://github.com/anthropics/claude-code/tree/main/examples/hooks

**Document Findings**:
```markdown
# Claude Code Best Practices Research

## Hooks

**Official Hook Types**:
- [List discovered hook types]

**Recommended Hooks**:
- [List recommended hooks from docs]

**Deprecated Patterns**:
- [List patterns to avoid]
```

### Step 2: Research plugin system

**Search Query**: "Anthropic Claude Code plugins official documentation"

**Expected Info**:
- How plugins are structured
- Official plugin locations
- How to install/configure plugins

### Step 3: Research context loading

**Search Query**: "Claude Code context loading automatic"

**Key Questions**:
- Does Claude Code natively handle context loading?
- Should we use context-map.json?
- Are custom modules recommended?

### Step 4: Document findings

Save all research to `docs/research/claude-code-best-practices.md` with sections:
- Hooks (official types, recommendations)
- Plugins (structure, installation)
- Context Loading (native behavior, recommendations)
- Settings.json (official schema fields)

### Step 5: Commit research

```bash
git add docs/research/claude-code-best-practices.md
git commit -m "docs: research Claude Code best practices"
```

---

## Task 2: Install Official Plugins

**Objective**: Install frontend-design and code-review plugins following official structure

**Files**:
- Create: `.claude/plugins/` directory structure
- Create: `.claude/plugins/frontend-design/` (if needed)
- Create: `.claude/plugins/code-review/` (if needed)

### Step 1: Verify plugin installation location

**Check Current State**:
```bash
ls -la .claude/plugins/ 2>/dev/null || echo "plugins directory doesn't exist"
```

**Expected**: May not exist, or may have existing plugins

### Step 2: Check if plugins already installed via superpowers

**Action**: Check if superpowers already includes these plugins

```bash
fd -t d 'frontend-design|code-review' ~/.claude/plugins/cache/
```

**Note**: Superpowers installs to global cache, not project-local

### Step 3: Create commands directory

```bash
mkdir -p .claude/commands
```

### Step 4: Create code-review command

**File**: `.claude/commands/code-review.md`

```markdown
# Code Review Command

Automatically review pull requests using multiple specialized agents.

## Usage

Run: `/code-review` in any PR context

## Configuration

**Confidence Threshold**: 80 (issues below this score are filtered)

**Agent Types**:
- CLAUDE.md compliance auditors (2x for redundancy)
- Bug detection agent (focuses on changes only)
- Historical context analyzer (uses git blame)

## Behavior

**Skips**:
- Closed or draft PRs
- Trivial/automated changes
- Previously reviewed PRs

**Output**: Review comments with CLAUDE.md references and GitHub blob links
```

### Step 5: Update CLAUDE.md to mention code review

**File**: `CLAUDE.md`

**Add Section After "Development Workflow"**:
```markdown
## Code Review

Use `/code-review` command to automatically review PRs:
- CLAUDE.md compliance checking
- Bug detection
- Historical context analysis
- Confidence-scored feedback (threshold: 80)
```

### Step 6: Commit plugin setup

```bash
git add .claude/commands/code-review.md CLAUDE.md
git commit -m "feat: add code-review plugin command"
```

---

## Task 3: Implement Bash Command Validator Hook

**Objective**: Replace CLAUDE.md command guidelines with enforced hook

**Files**:
- Create: `.claude/hooks/bash_command_validator.py`
- Modify: `.claude/settings.json`
- Modify: `CLAUDE.md` (remove command enforcement section)

### Step 1: Create bash validator hook

**File**: `.claude/hooks/bash_command_validator.py`

```python
#!/usr/bin/env python3
"""
Bash Command Validator Hook
Enforces project command standards
"""

import json
import re
import sys

# Validation rules: (pattern, suggestion)
_VALIDATION_RULES = [
    (r'\bgrep\b', "Use 'rg' (ripgrep) instead of 'grep'"),
    (r'\bfind\b', "Use 'fd' instead of 'find'"),
    (r'\brm\s+-rf\b', "Use 'trash' instead of 'rm -rf'"),
    (r'\bpip\b', "Use 'uv' instead of 'pip'"),
]


def _validate_command(command: str) -> list[str]:
    """Check command against validation rules."""
    issues = []
    for pattern, message in _VALIDATION_RULES:
        if re.search(pattern, command):
            issues.append(message)
    return issues


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    issues = _validate_command(command)
    if issues:
        print("Command validation failed:", file=sys.stderr)
        for message in issues:
            print(f"  • {message}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
```

### Step 2: Make hook executable

```bash
chmod +x .claude/hooks/bash_command_validator.py
```

### Step 3: Test hook locally

```bash
echo '{"tool_name": "Bash", "tool_input": {"command": "grep foo bar"}}' | python3 .claude/hooks/bash_command_validator.py
```

**Expected**: Exit code 2 with error message about using `rg`

### Step 4: Add hook to settings.json

**File**: `.claude/settings.json`

**Find PreToolUse hooks section**, add bash validator:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/bash_command_validator.py",
            "continue_on_error": false,
            "description": "Validate bash commands against project standards"
          }
        ]
      }
    ]
  }
}
```

**Important**: Place BEFORE existing Bash hooks in PreToolUse array

### Step 5: Update CLAUDE.md

**File**: `CLAUDE.md`

**Remove** the "CRITICAL Command Compliance" section (lines 97-106)

**Replace with**:
```markdown
## ⚠️ Command Standards

Command standards are automatically enforced via hooks:
- ✅ `fd` - NOT `find`
- ✅ `rg` - NOT `grep`
- ✅ `trash` - NOT `rm -rf`
- ✅ `uv` - NOT `pip`

Violations will be blocked automatically.
```

### Step 6: Commit bash validator

```bash
git add .claude/hooks/bash_command_validator.py .claude/settings.json CLAUDE.md
git commit -m "feat: enforce bash command standards via hook"
```

---

## Task 4: Audit Existing Hooks

**Objective**: Review existing hooks against Anthropic best practices

**Files**:
- Read: `.claude/hooks/activity-logger.py`
- Read: `.claude/hooks/context-validator.py`
- Read: `.claude/hooks/git-commit-hook.sh`
- Read: `.claude/hooks/subagent-state-tracker.py`
- Read: `.claude/hooks/token-limiter.py`
- Modify: `.claude/settings.json` (disable incompatible hooks)
- Create: `docs/research/hook-audit-results.md`

### Step 1: Read each existing hook

```bash
for hook in activity-logger.py context-validator.py git-commit-hook.sh subagent-state-tracker.py token-limiter.py; do
  echo "=== $hook ==="
  head -50 .claude/hooks/$hook
done
```

### Step 2: Categorize hooks by compliance

**Create**: `docs/research/hook-audit-results.md`

```markdown
# Hook Audit Results

## Hooks Reviewed

### activity-logger.py
**Purpose**: [Describe what it does]
**Compliance**: [KEEP/MODIFY/REMOVE]
**Reasoning**: [Why]

### context-validator.py
**Purpose**: [Describe]
**Compliance**: [KEEP/MODIFY/REMOVE]
**Reasoning**: [Check if interferes with native context loading]

### git-commit-hook.sh
**Purpose**: [Describe]
**Compliance**: [KEEP/MODIFY/REMOVE]
**Reasoning**: [Git safety hooks are likely okay]

### subagent-state-tracker.py
**Purpose**: [Describe]
**Compliance**: [KEEP/MODIFY/REMOVE]
**Reasoning**: [Does it track deprecated concepts?]

### token-limiter.py
**Purpose**: [Describe]
**Compliance**: [KEEP/MODIFY/REMOVE]
**Reasoning**: [May conflict with native token management]

## Recommendations

**KEEP**:
- [List hooks to keep]

**MODIFY**:
- [List hooks to update]

**REMOVE**:
- [List hooks to disable]
```

### Step 3: Disable questionable hooks

**File**: `.claude/settings.json`

**For each hook marked REMOVE**, comment out or remove from PreToolUse array

**Example**:
```json
// DISABLED: May conflict with native context loading
// {
//   "matcher": "",
//   "hooks": [
//     {
//       "type": "command",
//       "command": "python3 .claude/hooks/context-validator.py"
//     }
//   ]
// }
```

### Step 4: Commit hook audit

```bash
git add docs/research/hook-audit-results.md .claude/settings.json
git commit -m "docs: audit existing hooks, disable incompatible ones"
```

---

## Task 5: Deprecate Custom Modules System

**Objective**: Move `.claude/modules/` to archive, extract useful content

**Files**:
- Create: `.claude/archive/deprecated-modules/` directory
- Move: `.claude/modules/*` → `.claude/archive/deprecated-modules/`
- Create: `.claude/archive/deprecated-modules/README.md`
- Extract: Useful content to `docs/`
- Remove: References from `context-map.json`

### Step 1: Create archive directory

```bash
mkdir -p .claude/archive/deprecated-modules
```

### Step 2: Move modules to archive

```bash
mv .claude/modules/* .claude/archive/deprecated-modules/
```

### Step 3: Create deprecation README

**File**: `.claude/archive/deprecated-modules/README.md`

```markdown
# Deprecated Modules (Archived 2025-11-13)

## Why Deprecated

These modules were part of a custom context-loading system built before:
- Anthropic native context loading
- Official Claude Code plugin system
- Superpowers plugin workflow

## Superseded By

- **Modules** → Native Claude Code context loading + official plugins
- **Context-map.json** → Native automatic context management
- **Custom triggers** → Claude decides what context to load

## Historical Value

These modules contain useful reference information that has been:
- Extracted to `docs/` where still relevant
- Superseded by newer documentation
- Preserved here for historical reference

## Migration

**Database Module**:
- Schema reference → `docs/database-schema.md` (if needed)

**API Module**:
- Specification → OpenAPI/Swagger docs (auto-generated)
- Guide → `backend/README.md`

**Frontend Module**:
- Architecture → `docs/frontend/architecture.md`
- Guide → `frontend/README.md`

**Import Module**:
- Commands → `backend/app/data_import/README.md`

**Testing Module**:
- Guide → Covered in test files and `backend/README.md`

## Do Not Use

These files should not be loaded or referenced in current development.
Use the locations listed in Migration section instead.
```

### Step 4: Extract database schema if needed

**Check if useful**:
```bash
head -100 .claude/archive/deprecated-modules/database/SCHEMA_REFERENCE.md
```

**If contains useful schema info not in code**, extract to:
**File**: `docs/database-schema.md`

```markdown
# Database Schema Reference

[Extract useful schema documentation from deprecated module]

**See Also**: Backend models (`backend/app/models.py`) for authoritative schema
```

### Step 5: Update or remove context-map.json

**File**: `.claude/context-map.json`

**Option A: Remove file entirely** (if Claude Code doesn't need it)
```bash
mv .claude/context-map.json .claude/archive/deprecated-context-map.json
```

**Option B: Remove module references** (if keeping file for other reasons)

Remove or comment out the entire `task_based_loading` section that references modules.

**Decision**: Based on research in Task 1, determine if context-map.json is needed at all.

### Step 6: Remove module directory

```bash
rmdir .claude/modules
```

**Expected**: Should be empty after moving contents

### Step 7: Commit deprecation

```bash
git add .claude/archive/deprecated-modules/ .claude/context-map.json docs/
git status  # Review what's being committed
git commit -m "refactor: deprecate custom modules system, rely on native context loading"
```

---

## Task 6: Add CHANGELOG.md Automation

**Objective**: Create CHANGELOG.md with automation hook for future versioning

**Files**:
- Create: `CHANGELOG.md`
- Create: `.claude/hooks/changelog_updater.py`
- Create: `.claude/commands/update-changelog.md`

### Step 1: Create initial CHANGELOG.md

**File**: `CHANGELOG.md`

```markdown
# Changelog

All notable changes to Mids Hero Web will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project will follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once launched.

## [Unreleased]

### Added
- Superpowers plugin integration for structured development
- Frontend development skill for systematic UI building
- Documentation standards to prevent drift
- Bash command validator hook
- Official Anthropic plugin integration (frontend-design, code-review)

### Changed
- Modernized `.claude/` infrastructure to use native Claude Code features
- Deprecated custom modules system in favor of native context loading
- Updated all READMEs to reflect current project state

### Fixed
- Documentation drift from workflow evolution

## [0.1.0] - 2025-11-13 - Backend Complete

### Added
- FastAPI backend with 100% API coverage
- I12 streaming parser for City of Heroes data
- Database schema with PostgreSQL
- Comprehensive calculation engine with 100% test coverage
- Multi-tier caching (LRU + Redis)
- GitHub Actions CI/CD pipeline
- High-performance data import (360K+ records, <1GB memory)

### Technical Details
- Import speed: 1500 records/second
- API response time: <100ms average
- Cache hit rate: >90%
- Backend test coverage: ~85%
- Calculation test coverage: 100%

---

**Project Status**: Backend 100% complete, Frontend in development

**Tech Stack**: FastAPI, PostgreSQL, React 19, Next.js, TypeScript
```

### Step 2: Create changelog updater command

**File**: `.claude/commands/update-changelog.md`

```markdown
# Update Changelog

Update CHANGELOG.md with new version entry.

## Usage

Tell Claude: "Update changelog for version X.Y.Z" or "Add changelog entry for [feature]"

## Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

**Version Entry**:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Modifications to existing features

### Deprecated
- Features being phased out

### Removed
- Deleted features

### Fixed
- Bug fixes

### Security
- Security fixes
```

## Semantic Versioning

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Guidelines

- Write in **present tense** ("Added," "Fixed," "Changed")
- Use **backticks** for code/commands
- Include **links** to PRs or issues when relevant
- Keep **entries concise** (one line per change)
- **Technical details** in sub-bullets if needed
- Move items from **[Unreleased]** to version section on release

## Example Entry

```markdown
## [1.0.0] - 2025-12-01

### Added
- User authentication with JWT tokens
- Build sharing via unique URLs
- Real-time build validation

### Changed
- Migrated from Create React App to Next.js 14
- Improved API response time by 40%

### Fixed
- Power calculation accuracy for damage bonuses
- Enhancement set bonus stacking rules

### Security
- Fixed XSS vulnerability in build name input ([#123](link))
```
```

### Step 3: Create optional automation hook (future)

**File**: `.claude/hooks/changelog_updater.py`

```python
#!/usr/bin/env python3
"""
Changelog Updater Hook (Optional - for future automation)

Automatically suggests changelog entries based on commit messages.
Currently disabled - use '/update-changelog' command instead.
"""

import json
import sys
from datetime import datetime

# TODO: Enable this hook when versioning starts
# For now, manual changelog updates via /update-changelog command

def main():
    """Placeholder for future changelog automation."""
    # Would analyze commit messages and suggest changelog entries
    # Not active yet - project hasn't launched with versioning
    sys.exit(0)

if __name__ == "__main__":
    main()
```

### Step 4: Document changelog workflow

**File**: `CLAUDE.md`

**Add section after "Essential Commands"**:

```markdown
## 📝 Changelog

Update CHANGELOG.md for significant changes:

```bash
# Manual updates (current approach)
# Tell Claude: "Update changelog for version X.Y.Z"
# Or: "Add changelog entry for [feature]"

# Changelog follows Keep a Changelog format
# Uses Semantic Versioning (MAJOR.MINOR.PATCH)
```

**Note**: Full versioning starts after v1.0.0 launch
```

### Step 5: Commit changelog setup

```bash
git add CHANGELOG.md .claude/commands/update-changelog.md .claude/hooks/changelog_updater.py CLAUDE.md
git commit -m "feat: add CHANGELOG.md with update workflow"
```

---

## Task 7: Clean Up Configuration Files

**Objective**: Simplify settings.json and remove unused configuration

**Files**:
- Modify: `.claude/settings.json`
- Remove or archive: `.claude/context-map.json` (if not needed)
- Create: `.claude/settings-backup-2025-11-13.json` (safety backup)

### Step 1: Backup current settings

```bash
cp .claude/settings.json .claude/settings-backup-2025-11-13.json
git add .claude/settings-backup-2025-11-13.json
git commit -m "chore: backup settings before cleanup"
```

### Step 2: Review settings.json against research

**Based on Task 1 research**, identify:
- Official fields to keep
- Custom fields that may be incompatible
- Deprecated fields to remove

### Step 3: Create simplified settings.json

**File**: `.claude/settings.json`

**Keep only**:
- Essential project configuration
- Hooks that passed audit (Task 4)
- Official settings from Anthropic docs

**Example simplified structure**:
```json
{
  "version": "1.0",
  "description": "Claude Code settings for Mids Hero Web",
  "last_updated": "2025-11-13",

  "project": {
    "name": "mids-hero-web",
    "type": "web-application",
    "primary_languages": ["python", "typescript", "sql"]
  },

  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/bash_command_validator.py",
            "description": "Enforce command standards"
          }
        ]
      },
      {
        "matcher": "Bash(git commit:*)",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/git-commit-hook.sh",
            "timeout_seconds": 10
          }
        ]
      }
    ]
  },

  "safety_features": {
    "confirm_destructive_operations": true,
    "prevent_main_commits": true,
    "require_feature_branches": true
  }
}
```

**Note**: Remove complex sections like:
- `context_management` (rely on native)
- `token_limits` (rely on native)
- `tool_loadouts` (rely on native)
- `context_offloading` (rely on native)
- `session_thresholds` (rely on native)

### Step 4: Test simplified configuration

**Start Claude Code and verify**:
- Bash validator hook still works
- Git commit hook still works
- No errors about missing fields

### Step 5: Archive context-map.json if not needed

**Based on Task 1 research**:

**If context-map.json is NOT needed by Claude Code**:
```bash
mv .claude/context-map.json .claude/archive/deprecated-context-map.json
```

**If it IS needed**, simplify by removing module references (already done in Task 5).

### Step 6: Commit configuration cleanup

```bash
git add .claude/settings.json
git status  # Review changes
git commit -m "refactor: simplify settings.json, rely on native Claude Code features"
```

---

## Task 8: Update Documentation

**Objective**: Update all documentation to reflect modernized infrastructure

**Files**:
- Modify: `.claude/README.md`
- Modify: `CLAUDE.md`
- Modify: `docs/PROJECT_STATUS.md`
- Create: `docs/CLAUDE-INFRASTRUCTURE-MODERNIZATION-SUMMARY.md`

### Step 1: Update .claude/README.md

**File**: `.claude/README.md`

**Rewrite to reflect current state**:

```markdown
# .claude/ Directory

**Purpose**: Claude Code configuration and project-specific customization

**Last Updated**: 2025-11-13

## Structure

```
.claude/
├── skills/                    # Project-specific skills
│   └── frontend-development/  # Frontend orchestration skill
├── commands/                  # Slash commands
│   ├── code-review.md        # PR review automation
│   └── update-changelog.md   # Changelog management
├── hooks/                     # Event hooks
│   ├── bash_command_validator.py  # Command standards enforcement
│   └── git-commit-hook.sh         # Git safety checks
├── workflows/                 # Workflow documentation
│   ├── claude/               # Claude-specific workflows
│   └── github/               # GitHub Actions docs
├── archive/                   # Deprecated/archived files
│   ├── deprecated-modules/   # Old custom context system
│   └── old-state/            # Historical state files
├── settings.json             # Claude Code configuration
└── README.md                 # This file
```

## Official Plugins

This project uses official Anthropic plugins:

- **superpowers** - Planning and execution workflow
- **frontend-design** - Distinctive UI generation (via superpowers)
- **code-review** - Automated PR review

Access via global plugin cache, not project-local.

## Custom Configuration

### Skills
- `skills/frontend-development/` - Orchestrates frontend epic development

### Commands
- `/code-review` - Multi-agent PR review with confidence scoring
- `/update-changelog` - Manage CHANGELOG.md entries

### Hooks
- Bash command validator - Enforces `fd`, `rg`, `trash`, `uv` usage
- Git commit hook - Prevents direct commits to `main`

## Removed/Deprecated

**As of 2025-11-13**:
- ❌ Custom modules system → Native context loading
- ❌ context-map.json → Native automatic context
- ❌ Custom token management → Native management
- ❌ Manual context triggers → Claude decides context

See `archive/deprecated-modules/README.md` for migration details.

## Development Workflow

**Frontend Development**:
1. Tell Claude: "start epic 1.1" or describe task
2. Claude invokes `skills/frontend-development/`
3. Workflow: Plan → Approve → Execute → Review

**Code Review**:
1. Create PR
2. Tell Claude: `/code-review`
3. Multi-agent review with confidence-scored feedback

**Changelog**:
1. Tell Claude: "update changelog for version X.Y.Z"
2. Follows Keep a Changelog format

## Best Practices

- ✅ Rely on native Claude Code features for context
- ✅ Use official plugins when available
- ✅ Keep configuration simple
- ✅ Document custom hooks/commands
- ❌ Don't create custom context-loading systems
- ❌ Don't manually manage tokens/context

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Superpowers Plugin](https://github.com/chadmcrowell/superpowers)
- [Frontend Design Plugin](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design)
- [Code Review Plugin](https://github.com/anthropics/claude-code/tree/main/plugins/code-review)
```

### Step 2: Update CLAUDE.md with final changes

**File**: `CLAUDE.md`

**Verify all updates from previous tasks are present**:
- ✅ Superpowers workflow documented
- ✅ Command standards section updated (bash validation)
- ✅ Code review command mentioned
- ✅ Changelog workflow mentioned
- ✅ Key Locations point to current structure

### Step 3: Update PROJECT_STATUS.md

**File**: `docs/PROJECT_STATUS.md`

**Add to "Recent Changes" section**:

```markdown
### November 2025

- ✅ Completed documentation housekeeping
- ✅ Modernized `.claude/` infrastructure
- ✅ Adopted official Anthropic plugins (frontend-design, code-review)
- ✅ Implemented bash command validator hook
- ✅ Deprecated custom modules/context-map system
- ✅ Added CHANGELOG.md with update workflow
- ✅ Simplified settings.json to rely on native features
```

### Step 4: Create modernization summary

**File**: `docs/CLAUDE-INFRASTRUCTURE-MODERNIZATION-SUMMARY.md`

```markdown
# Claude Infrastructure Modernization Summary

**Date**: 2025-11-13
**Status**: Complete

## What Was Changed

### Deprecated
- ❌ Custom modules system (`.claude/modules/`)
- ❌ Custom context-map.json triggers
- ❌ Manual token management configuration
- ❌ Outdated content referencing old workflows

### Added
- ✅ Bash command validator hook (enforces `fd`, `rg`, `trash`, `uv`)
- ✅ Code review command integration
- ✅ CHANGELOG.md with update workflow
- ✅ Simplified settings.json relying on native features

### Migrated
- Useful schema info → `docs/database-schema.md` (if needed)
- API specification → OpenAPI/Swagger (auto-generated)
- Frontend architecture → `docs/frontend/architecture.md`
- Import guides → `backend/app/data_import/README.md`

## Why These Changes

**Alignment with Anthropic Best Practices**:
- Use native context loading instead of custom systems
- Adopt official plugins (frontend-design, code-review)
- Enforce standards via hooks, not documentation
- Simplify configuration

**Pre-Modernization Issues**:
- Custom modules from pre-superpowers era
- Unclear if hooks were compatible
- Potential conflicts with native features
- Documentation drift

## Benefits

**Developer Experience**:
- Clearer which features are native vs custom
- Automatic command validation (no manual checking)
- Official plugins for common tasks
- Simpler configuration

**Maintenance**:
- Less custom infrastructure to maintain
- Aligned with Anthropic updates
- Clear documentation of what's custom

**Performance**:
- Native context loading is optimized
- No custom overhead for token management
- Official plugins are maintained by Anthropic

## Migration from Old System

**If You Have Old Context**:

Old modules content moved to `.claude/archive/deprecated-modules/`

**Find Information**:
- Database schema → `docs/database-schema.md` or `backend/app/models.py`
- API docs → `http://localhost:8000/docs` (OpenAPI/Swagger)
- Frontend architecture → `docs/frontend/architecture.md`
- Import commands → `backend/app/data_import/README.md`

**Don't Use**:
- `.claude/modules/*` (archived)
- `.claude/context-map.json` (removed or simplified)
- References to "sub-agents" (use official plugins)

## Current Infrastructure

**Official Plugins** (via superpowers):
- frontend-design
- code-review

**Custom Configuration**:
- Bash command validator hook
- Git commit safety hook
- Frontend development skill (`.claude/skills/frontend-development/`)

**Documentation**:
- `CHANGELOG.md` - Version tracking
- `.claude/README.md` - Infrastructure overview
- `CLAUDE.md` - Main entry point

## Testing the Changes

**Verify Bash Validator**:
```bash
# This should be blocked:
# echo '{"tool_name": "Bash", "tool_input": {"command": "grep foo bar"}}' | python3 .claude/hooks/bash_command_validator.py
```

**Verify Code Review**:
```bash
# In PR context:
# /code-review
```

**Verify Context Loading**:
- Claude should automatically load relevant context
- No manual "load module X" needed

## Questions?

See:
- `.claude/README.md` - Infrastructure overview
- `docs/research/claude-code-best-practices.md` - Research findings
- `docs/research/hook-audit-results.md` - Hook compliance audit
- `docs/CLAUDE-INFRASTRUCTURE-REVIEW.md` - Original analysis

## Rollback

If issues arise, restore from backup:
```bash
# Settings backup available at:
# .claude/settings-backup-2025-11-13.json

# Modules archived at:
# .claude/archive/deprecated-modules/
```

---

**Modernization completed 2025-11-13**
**All changes committed with detailed messages**
```

### Step 5: Commit documentation updates

```bash
git add .claude/README.md CLAUDE.md docs/PROJECT_STATUS.md docs/CLAUDE-INFRASTRUCTURE-MODERNIZATION-SUMMARY.md
git commit -m "docs: update all documentation for modernized infrastructure"
```

---

## Task 9: Verification & Testing

**Objective**: Verify all changes work correctly

**Files**: None (testing only)

### Step 1: Verify bash validator blocks commands

**Test grep**:
```bash
# Tell Claude: "run grep to search for 'test'"
# Expected: Blocked with message about using rg
```

**Test find**:
```bash
# Tell Claude: "use find to locate files"
# Expected: Blocked with message about using fd
```

**Test rm -rf**:
```bash
# Tell Claude: "remove directory with rm -rf"
# Expected: Blocked with message about using trash
```

**Test pip**:
```bash
# Tell Claude: "install package with pip"
# Expected: Blocked with message about using uv
```

### Step 2: Verify allowed commands work

```bash
# Tell Claude: "use rg to search for 'test'"
# Expected: Works without error

# Tell Claude: "use fd to find Python files"
# Expected: Works without error
```

### Step 3: Verify git safety

```bash
# Try to commit to main (in test branch):
# Tell Claude: "commit to main branch"
# Expected: Blocked by git-commit-hook.sh
```

### Step 4: Verify context loading

**Test automatic context**:
- Tell Claude about a database task
- Verify Claude loads relevant context automatically
- No manual "load module" needed

### Step 5: Verify commands exist

```bash
ls -la .claude/commands/
# Expected: code-review.md, update-changelog.md
```

### Step 6: Verify documentation accuracy

**Read through**:
- `CLAUDE.md` - Verify all references are current
- `.claude/README.md` - Verify structure matches reality
- `docs/PROJECT_STATUS.md` - Verify status is accurate

### Step 7: Check for broken links

```bash
# Use grep to find markdown links:
rg '\[.*\]\(.*\.md\)' CLAUDE.md .claude/README.md docs/*.md
```

**Verify each link points to existing file**

### Step 8: Run health check

```bash
just health
```

**Expected**: All checks pass

### Step 9: Document verification results

**Create**: `docs/research/modernization-verification.md`

```markdown
# Infrastructure Modernization Verification

**Date**: 2025-11-13

## Tests Performed

### Bash Validator
- [x] Blocks `grep` ✅
- [x] Blocks `find` ✅
- [x] Blocks `rm -rf` ✅
- [x] Blocks `pip` ✅
- [x] Allows `rg` ✅
- [x] Allows `fd` ✅

### Git Safety
- [x] Blocks commits to main ✅

### Context Loading
- [x] Automatic context works ✅
- [x] No errors about missing modules ✅

### Commands
- [x] `/code-review` command exists ✅
- [x] `/update-changelog` command exists ✅

### Documentation
- [x] All links valid ✅
- [x] Structure matches reality ✅
- [x] No outdated references ✅

### Health Check
- [x] `just health` passes ✅

## Issues Found

[List any issues discovered]

## Conclusion

Infrastructure modernization complete and verified.
All systems functional with native Claude Code features.
```

### Step 10: Commit verification

```bash
git add docs/research/modernization-verification.md
git commit -m "test: verify infrastructure modernization"
```

---

## Task 10: Create Final PR

**Objective**: Create pull request for infrastructure modernization

**Files**: None (git operations only)

### Step 1: Ensure all changes committed

```bash
git status
# Expected: Nothing to commit, working tree clean
```

### Step 2: Review commit history

```bash
git log --oneline -20
```

**Expected commits**:
1. docs: research Claude Code best practices
2. feat: add code-review plugin command
3. feat: enforce bash command standards via hook
4. docs: audit existing hooks, disable incompatible ones
5. refactor: deprecate custom modules system
6. feat: add CHANGELOG.md with update workflow
7. refactor: simplify settings.json
8. docs: update all documentation
9. test: verify infrastructure modernization

### Step 3: Push branch

```bash
git push -u origin feature/claude-infrastructure-modernization
```

### Step 4: Create pull request

```bash
gh pr create --title "refactor: modernize .claude/ infrastructure" --body "$(cat <<'EOF'
## Summary

Modernizes `.claude/` infrastructure to align with Anthropic best practices and official plugin ecosystem.

## Changes

### Deprecated
- ❌ Custom modules system → Native context loading
- ❌ context-map.json triggers → Native automatic context
- ❌ Manual token management → Native management

### Added
- ✅ Bash command validator hook (enforces fd, rg, trash, uv)
- ✅ Code review command integration (/code-review)
- ✅ CHANGELOG.md with update workflow
- ✅ Official plugin integration (frontend-design, code-review)

### Audited
- ✅ Existing hooks reviewed for Anthropic compliance
- ✅ Incompatible hooks disabled
- ✅ Configuration simplified

## Documentation

- `docs/CLAUDE-INFRASTRUCTURE-REVIEW.md` - Original analysis
- `docs/CLAUDE-INFRASTRUCTURE-MODERNIZATION-SUMMARY.md` - Summary of changes
- `docs/research/claude-code-best-practices.md` - Research findings
- `docs/research/hook-audit-results.md` - Hook audit
- `docs/research/modernization-verification.md` - Verification results

## Testing

- [x] Bash validator blocks forbidden commands
- [x] Git safety hook prevents main commits
- [x] Context loads automatically
- [x] Commands work as expected
- [x] Health check passes

## Migration

Old modules archived in `.claude/archive/deprecated-modules/`
All useful content extracted to appropriate `docs/` locations

## Benefits

- Aligned with Anthropic official practices
- Less custom infrastructure to maintain
- Automatic command validation
- Clearer what's native vs custom
- Official plugins for common tasks

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### Step 5: Add reviewers (if applicable)

```bash
# If you have specific reviewers:
# gh pr edit --add-reviewer @username
```

### Step 6: Link related issues

**If there's an issue for infrastructure modernization**:
```bash
# gh pr edit --add-label "refactor" --add-label "infrastructure"
```

### Step 7: Document PR creation

**Success message**:
```
Pull request created: #XXX
URL: https://github.com/woodrowpearson/mids-hero-web/pull/XXX
```

---

## Acceptance Criteria

**Checklist for completion**:

### Infrastructure
- [ ] Custom modules moved to archive
- [ ] Bash command validator enforcing standards
- [ ] Hooks audited for compliance
- [ ] Settings.json simplified
- [ ] Official plugins integrated
- [ ] CHANGELOG.md created

### Documentation
- [ ] All READMEs updated
- [ ] CLAUDE.md reflects new structure
- [ ] Research documented
- [ ] Migration paths clear
- [ ] Verification complete

### Testing
- [ ] Bash validator blocks forbidden commands
- [ ] Git safety works
- [ ] Context loads automatically
- [ ] Health check passes
- [ ] No broken documentation links

### Git
- [ ] All changes committed with clear messages
- [ ] PR created with detailed description
- [ ] No uncommitted changes

---

## Rollback Plan

**If something breaks**:

### Step 1: Restore settings backup
```bash
cp .claude/settings-backup-2025-11-13.json .claude/settings.json
```

### Step 2: Restore modules (if needed)
```bash
cp -r .claude/archive/deprecated-modules/* .claude/modules/
```

### Step 3: Restore context-map (if needed)
```bash
cp .claude/archive/deprecated-context-map.json .claude/context-map.json
```

### Step 4: Disable new hooks
Remove bash validator from settings.json PreToolUse

### Step 5: Document issue
Create GitHub issue with:
- What broke
- When it broke
- Error messages
- Rollback performed

---

## Post-Implementation

**After PR merges**:

1. **Update main branch**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Verify in clean session**:
   - Start new Claude session
   - Test bash validator
   - Test context loading
   - Test code review command

3. **Monitor for issues**:
   - Check for any errors in Claude output
   - Verify hooks don't slow down responses
   - Ensure context loading is working

4. **Update team** (if applicable):
   - Announce new `/code-review` command
   - Explain bash command changes (auto-enforced)
   - Share CHANGELOG workflow

---

**Plan Status**: Ready for Execution
**Created By**: superpowers:write-plan
**Date**: 2025-11-13
**Estimated Time**: 4-6 hours
**Can Be Done In Batches**: Yes (task by task with checkpoints)
