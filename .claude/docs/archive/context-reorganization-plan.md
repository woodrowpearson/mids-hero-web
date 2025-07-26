# Claude Context Reorganization Plan

## Current Issues & Solutions

### 🔴 Problems Identified

1. **Missing Referenced Directories**
   - CLAUDE.md references `.claude/epics/` but it doesn't exist
   - Epic information scattered in progress.json

2. **Empty/Unused Directories**
   - `.claude/memory/` - empty and purpose unclear
   - `.claude/templates/` - empty and unused

3. **Redundant Configuration**
   - Two settings files (local and debug) with potential conflicts
   - No clear loading priority documented

4. **Context Overflow Risk**
   - No explicit size limits per file
   - Shared directory could grow unbounded
   - No automatic pruning strategy

5. **Unclear Dependencies**
   - Files reference each other without clear hierarchy
   - No dependency graph maintained

## 🎯 Reorganization Strategy

### 1. **Simplified Directory Structure**

```
.claude/
├── README.md                    # How Claude context works (NEW)
├── settings.json               # Unified settings (CONSOLIDATED)
├── context-map.json            # Explicit loading rules (NEW)
│
├── core/                       # Always loaded (< 10K total)
│   ├── project-guide.md        # Essential info (from CLAUDE.md)
│   └── quick-reference.md      # Key commands only
│
├── modules/                    # Task-specific contexts (loaded on-demand)
│   ├── database/              
│   │   ├── guide.md           # Database work guide
│   │   └── schema.md          # Current schema reference
│   ├── import/
│   │   ├── guide.md           # Import system guide
│   │   └── commands.md        # Import command reference
│   ├── api/
│   │   ├── guide.md           # API development guide
│   │   └── spec.md            # Current API specification
│   └── frontend/
│       ├── guide.md           # Frontend development guide
│       └── architecture.md    # Component architecture
│
├── workflows/                  # Standard procedures
│   ├── daily.md               # Daily development workflow
│   ├── release.md             # Release procedures
│   └── troubleshooting.md     # Common issues & solutions
│
├── automation/                 # Scripts and commands
│   ├── README.md              # Command documentation
│   ├── commit-push.sh         # Consolidated from ucp.sh
│   ├── update-progress.sh     # Progress tracking
│   └── session/               # Session management commands
│
└── state/                     # Project state (git-ignored)
    ├── progress.json          # Project progress
    ├── current-session.json   # Active session
    └── sessions/              # Session history
```

### 2. **Context Loading Rules (context-map.json)**

```json
{
  "version": "1.0",
  "max_tokens": {
    "total": 128000,
    "warning": 90000,
    "auto_prune": 110000
  },
  "loading_rules": {
    "always": [
      ".claude/core/project-guide.md",
      ".claude/core/quick-reference.md"
    ],
    "on_task": {
      "database": [
        ".claude/modules/database/guide.md",
        ".claude/modules/database/schema.md"
      ],
      "import": [
        ".claude/modules/import/guide.md",
        ".claude/modules/import/commands.md"
      ],
      "api": [
        ".claude/modules/api/guide.md",
        ".claude/modules/api/spec.md"
      ],
      "frontend": [
        ".claude/modules/frontend/guide.md",
        ".claude/modules/frontend/architecture.md"
      ]
    },
    "on_reference": {
      "workflow": ".claude/workflows/",
      "automation": ".claude/automation/"
    },
    "never_auto_load": [
      ".claude/state/",
      ".claude/automation/*.sh"
    ]
  },
  "file_limits": {
    "core": 5000,
    "module": 10000,
    "workflow": 5000
  }
}
```

### 3. **Migration Steps**

#### Phase 1: Prepare New Structure
```bash
# Create new directories
mkdir -p .claude/docs
mkdir -p .claude/core
mkdir -p .claude/modules/{database,import,api,frontend}
mkdir -p .claude/workflows
mkdir -p .claude/automation/session
mkdir -p .claude/state/sessions

# Move context architecture docs
# (Already created in .claude/docs/)
```

#### Phase 2: Consolidate and Split Files
- Split CLAUDE.md into:
  - `.claude/core/project-guide.md` (essential info only)
  - `.claude/core/quick-reference.md` (commands)
  - Module-specific content to respective guides

- Consolidate shared/ directory into modules/
- Merge duplicate functionality
- Remove redundant content

#### Phase 3: Update References
- Update all file references to new paths
- Create explicit dependencies in context-map.json
- Update CLAUDE.md to be a thin pointer file

#### Phase 4: Implement Loading Logic
- Create .claude/README.md explaining the system
- Implement token counting in key files
- Add file size warnings

### 4. **Content Guidelines**

#### Core Files (< 5K tokens each):
- **project-guide.md**: Project overview, tech stack, critical rules
- **quick-reference.md**: Most-used commands, health checks

#### Module Files (< 10K tokens each):
- **guide.md**: How to work in this domain
- **schema/spec/architecture.md**: Current state reference

#### Workflow Files (< 5K tokens each):
- Step-by-step procedures
- Checklists
- No redundant explanations

### 5. **Benefits**

1. **Reduced Context Size**: Core context ~10K (down from ~15K+)
2. **Clear Loading Strategy**: Explicit rules in context-map.json
3. **No Redundancy**: Single source of truth for each topic
4. **Scalable**: Easy to add new modules
5. **Maintainable**: Clear boundaries and size limits

### 6. **Implementation Timeline**

1. **Immediate**: Create documentation and plan
2. **Next**: Reorganize existing files
3. **Then**: Update all references
4. **Finally**: Test and optimize

## Next Steps

1. Review and approve this plan
2. Execute reorganization
3. Update CLAUDE.md to reference new structure
4. Test context loading with various tasks
5. Monitor token usage and adjust limits