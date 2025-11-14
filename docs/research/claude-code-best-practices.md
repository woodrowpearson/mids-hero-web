# Claude Code Best Practices Research

**Date**: 2025-11-13
**Source**: Official Anthropic Claude Code Documentation (https://code.claude.com/docs/)

## Executive Summary

Claude Code provides native context loading, plugin management, and comprehensive hook systems. Custom context-loading infrastructure (like modules/context-map.json) is **not necessary** and should be replaced with native features.

---

## Hooks

### Official Hook Types

Claude Code supports 9 official hook events:

| Event | Timing | Primary Use Case |
|-------|--------|-----------------|
| `PreToolUse` | Before tool execution | Permission control, input validation, blocking |
| `PostToolUse` | After tool completion | Output verification, feedback |
| `UserPromptSubmit` | Before prompt processing | Validation, context injection |
| `Stop` | When agent finishes | Intelligent continuation decisions |
| `SubagentStop` | When subagent finishes | Task completion evaluation |
| `Notification` | When notifications occur | Alert handling |
| `SessionStart` | Session initialization | Context loading, setup |
| `SessionEnd` | Session termination | Cleanup operations |
| `PreCompact` | Before context compacting | Pre-compaction logic |

### Hook Configuration Structure

Hooks are defined in `settings.json`:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "bash-command",
            "timeout_seconds": 10,
            "continue_on_error": false,
            "description": "What this hook does"
          }
        ]
      }
    ]
  }
}
```

**Key Features**:
- Matchers support exact strings, regex patterns, and wildcards (`*`)
- Hook `type` can be `"command"` (bash) or `"prompt"` (LLM-based)
- Exit codes: 0 = success, 2 = blocking error, other = non-blocking error
- JSON input via stdin, JSON output for sophisticated control
- `$CLAUDE_PROJECT_DIR` environment variable for project root

### Recommended Hook Applications

1. **Automatic Formatting**: Apply tools like `prettier` or `gofmt` post-edit
2. **Logging**: Track executed commands for compliance
3. **Code Quality Feedback**: Validate outputs against conventions
4. **Access Control**: Block modifications to production/sensitive files
5. **Notifications**: Customize input-awaiting alerts

### Best Practices

- **Configuration Storage**: Project-specific hooks in `.claude/settings.json`, globally-applicable in `~/.claude/settings.json`
- **Command Integration**: Use JSON processing (jq, Python) for sophisticated filtering
- **Testing**: Verify hook behavior manually before deployment
- **Security**: Hooks run with your credentials—review thoroughly, validate inputs, use absolute paths
- **Debugging**: Use `claude --debug` to inspect execution details

### Deprecated Patterns

**None explicitly mentioned**, but focus is on:
- Modern command-based hooks using JSON processing
- Native tool integration rather than custom wrappers

---

## Plugins

### Plugin Architecture

Plugins follow standardized structure:

```
my-plugin/
├── .claude-plugin/plugin.json    # Metadata (name, version, author)
├── commands/                      # Custom slash commands
├── agents/                        # Agent definitions
├── skills/                        # Agent Skills
└── hooks/                         # Event handlers
```

### Installation Scope

**Project/Repository Level** (`.claude/settings.json`):
- Teams configure plugins in version-controlled repository
- Auto-installs when team members trust the folder
- Ensures consistent tooling across team

**User Level** (`~/.claude/settings.json`):
- Individual developer installs via `/plugin install`
- Persists in local Claude Code environment
- Personal tools not shared with team

### Plugin Management

**Installation via Marketplaces**:
1. Add marketplace: `/plugin marketplace add <url>`
2. Browse: `/plugin` (interactive)
3. Install: `/plugin install <plugin-name>`
4. Enable/disable/uninstall as needed

**Configuration** in `settings.json`:
```json
{
  "enabledPlugins": {
    "marketplace-name": ["plugin-1", "plugin-2"]
  },
  "extraKnownMarketplaces": [
    {
      "name": "company-plugins",
      "url": "https://github.com/company/plugins"
    }
  ]
}
```

### Best Practices

1. **Test locally first**: Use development marketplaces to iterate
2. **Version properly**: Apply semantic versioning in plugin manifest
3. **Document thoroughly**: Include README with installation/usage
4. **Organize thoughtfully**: Structure by functionality, not component type
5. **Validate structure**: Directories at plugin root, not nested in `.claude-plugin/`

### Official Anthropic Plugins

**Available via Superpowers Marketplace**:
- `superpowers` - Planning and execution workflow
- `frontend-design` - Distinctive UI generation
- `code-review` - Automated PR review (via superpowers:code-reviewer subagent)

**Note**: Official plugins are typically installed globally via plugin cache, not project-local.

---

## Settings.json Configuration

### Official Schema Fields

**Core Settings**:
- `model` - Override default Claude model
- `apiKeyHelper` - Custom authentication script
- `env` - Environment variables for every session
- `cleanupPeriodDays` - Transcript retention (default: 30)

**Permission & Access Control**:
```json
{
  "permissions": {
    "allow": ["Read(*)", "Edit(*)", "Bash(*)"],
    "ask": ["Write(*)", "Bash(rm *)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)", "Read(./.env.*)"]
  },
  "additionalDirectories": ["/path/to/extra/workspace"],
  "defaultMode": "acceptEdits",
  "disableBypassPermissionsMode": true
}
```

**Git & Collaboration**:
- `includeCoAuthoredBy` - Toggle Claude co-author byline (default: true)

**User Experience**:
- `companyAnnouncements` - Random startup messages
- `statusLine` - Custom context display via command/script
- `outputStyle` - Adjust system prompt behavior

**Advanced Integration**:
- `hooks` - Event handlers (PreToolUse, PostToolUse, etc.)
- `disableAllHooks` - Disable hooks globally

**Plugin Management**:
- `enabledPlugins` - Control plugin activation
- `extraKnownMarketplaces` - Additional plugin sources

**Sandbox Configuration** (macOS/Linux):
```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker"],
    "allowUnsandboxedCommands": false,
    "network": {
      "allowUnixSockets": ["~/.ssh/agent-socket"],
      "allowLocalBinding": true
    }
  }
}
```

### Settings Hierarchy (Highest to Lowest Priority)

1. **Enterprise managed policies** (`managed-settings.json`) — cannot be overridden
2. **Command-line arguments** — temporary session overrides
3. **Local project settings** (`.claude/settings.local.json`) — personal, untracked
4. **Shared project settings** (`.claude/settings.json`) — team, version-controlled
5. **User settings** (`~/.claude/settings.json`) — personal global defaults

### Deprecated Fields

- ❌ `ignorePatterns` → Use `permissions.deny` with Read rules instead

### What Claude Code Handles Natively

**Built-in (No Custom Config Needed)**:
- File reading/writing (Read, Edit, Write tools)
- Pattern matching (Glob, Grep tools)
- Bash command execution with sandboxing
- Jupyter notebook modification
- Web fetching and searching
- Slash command execution
- Sub-agent task delegation
- **Context loading** (automatic, see below)
- **Token management** (native)
- **Permission management** (native)

**Custom Configuration Required For**:
- Custom authentication schemes (`apiKeyHelper`)
- Advanced workflow hooks (`hooks` configuration)
- Custom status displays (`statusLine`)
- Specialized output formatting (`outputStyle`)
- Third-party integrations beyond default MCP servers

---

## Context Loading

### How It Works

**Automatic and Native**: Claude Code automatically loads all relevant memory files into context upon launch. Files are discovered hierarchically from working directory upward.

**CLAUDE.md Files**:
- Serve as instruction repositories at different organizational levels
- Support imports using `@path/to/import` syntax (relative or absolute)
- Searched recursively from current directory upward
- Subdirectory CLAUDE.md files loaded only when accessing those subtrees
- **This is the official way to provide context**

### context-map.json

**Status**: ❌ **NOT MENTIONED IN OFFICIAL DOCUMENTATION**

This suggests it's a custom implementation, not part of Claude Code's native features. Native context loading handles this automatically.

### Best Practices

1. **Specificity**: Use precise instructions ("Apply 2-space indentation" not "code well")
2. **Organization**: Structure as bullet points under descriptive markdown headings
3. **Regular Updates**: Review and refresh as projects evolve
4. **Content Strategy**: Include frequently used commands, coding standards, architectural patterns
5. **Imports**: Use `@path/to/import` for modular memory files
6. **Bootstrap**: Use `/init` command to create initial project memory
7. **Management**: Use `/memory` slash command or `#` shortcut

### Key Insight

**Custom context-loading systems (modules, context-map.json, manual triggers) are unnecessary.** Claude Code's native memory system handles context automatically and efficiently.

---

## Recommendations for Mids Hero Web

### ✅ Keep

1. **Git commit hook** - Safety check preventing commits to main
2. **Superpowers plugin** - Already using official plugin system
3. **Frontend development skill** - Project-specific, valuable orchestration

### ⚠️ Modify

1. **settings.json** - Simplify by removing:
   - Custom token management config (native handles this)
   - Custom context offloading (native handles this)
   - Session thresholds (native handles this)
   - Tool loadouts (native handles this)

2. **Existing hooks** - Audit against official patterns:
   - Ensure proper JSON I/O
   - Use exit codes correctly
   - Add timeout configurations
   - Add descriptions

### ❌ Remove/Deprecate

1. **`.claude/modules/`** - Replace with native context loading via CLAUDE.md
2. **`.claude/context-map.json`** - Not part of native system, unnecessary
3. **Custom context validators** - Native system handles validation
4. **Token limiters** - Native token management is superior
5. **Subagent state trackers** - If tracking deprecated concepts

### ✅ Add

1. **Bash command validator hook** - Enforce `fd`, `rg`, `trash`, `uv` via PreToolUse hook
2. **CHANGELOG.md** - Version tracking following Keep a Changelog format
3. **Official plugin commands** - Slash commands for code-review, etc.
4. **Simplified settings.json** - Keep only essential project config

---

## References

- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide.md)
- [Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [Plugins](https://code.claude.com/docs/en/plugins.md)
- [Settings](https://code.claude.com/docs/en/settings.md)
- [Memory](https://code.claude.com/docs/en/memory.md)
- [Claude Code Documentation Map](https://code.claude.com/docs/en/claude_code_docs_map.md)
