# Claude Code Context Loading Architecture
Last Updated: 2025-11-19 20:27:56 UTC

## Overview

This document explains how Claude Code loads and manages context in the Mids Hero Web project, with visual diagrams and best practices for context management.

## Context Loading Flow

```mermaid
graph TD
    Start[Claude Session Start] --> Load[Load Core Context]

    Load --> Core[CLAUDE.md<br/>~5K tokens<br/>Always Loaded]
    Load --> Settings[.claude/settings.local.json<br/>Configuration]

    Settings --> Rules{Loading Rules}

    Rules --> Shared[.claude/shared/*<br/>Architecture Docs<br/>On-Demand]
    Rules --> Agents[.claude/agents/*<br/>Specialized Contexts<br/>Task-Specific]
    Rules --> Commands[.claude/commands/*<br/>Pre-approved Scripts<br/>As Referenced]
    Rules --> Progress[.claude/progress.json<br/>Project State<br/>When Relevant]

    Core --> Workflow[.claude/development-workflow.md<br/>Standard Procedures]
    Core --> Just[justfile<br/>Command Reference]

    Shared --> SharedFiles[architecture.md<br/>database-design.md<br/>api-specifications.md<br/>backend-overview.md<br/>data-flow.md<br/>context-management.md<br/>import-commands-reference.md]

    Agents --> AgentFiles[database-agent.md<br/>i12-import-agent.md]

    Commands --> CommandFiles[update-progress.sh<br/>ucp.sh<br/>debug-session.sh<br/>session-*.md]

    style Core fill:#ff9999
    style Settings fill:#99ccff
    style Shared fill:#99ff99
    style Agents fill:#ffcc99
    style Commands fill:#cc99ff
```

## Context Hierarchy and Dependencies

```mermaid
graph TB
    subgraph "Always Loaded (Core Context)"
        CLAUDE[CLAUDE.md<br/>Project Guide]
        Settings[settings.local.json<br/>Configuration]
    end

    subgraph "On-Demand Context"
        subgraph "Shared Architecture"
            Arch[architecture.md]
            DB[database-design.md]
            API[api-specifications.md]
            Backend[backend-overview.md]
            Flow[data-flow.md]
        end

        subgraph "Specialized Agents"
            DBAgent[database-agent.md]
            I12Agent[i12-import-agent.md]
        end

        subgraph "Workflow & Commands"
            Workflow[development-workflow.md]
            Commands[Custom Commands]
            Sessions[Session Management]
        end
    end

    subgraph "Project State"
        Progress[progress.json]
        CurrentSession[.current-session]
    end

    CLAUDE --> Workflow
    CLAUDE --> Arch
    Settings --> Commands
    Workflow --> Sessions
    Arch --> DB
    Arch --> API
    Arch --> Backend
    Backend --> Flow
    DBAgent --> DB
    I12Agent --> Flow

    style CLAUDE fill:#ff6666
    style Settings fill:#6666ff
```

## Token Management Strategy

```mermaid
graph LR
    subgraph "Token Budget (128K Total)"
        Core[Core Context<br/>5-10K tokens]
        Active[Active Context<br/>20-40K tokens]
        Working[Working Memory<br/>40-80K tokens]
        Reserve[Reserve<br/>8K tokens]
    end

    subgraph "Auto Management"
        Monitor[Token Monitor]
        Warn[Warning at 90K]
        Compact[Auto-compact at 110K]
    end

    Monitor --> Core
    Monitor --> Active
    Monitor --> Working

    Warn --> Alert[User Alert]
    Compact --> Prune[Context Pruning]

    style Core fill:#99ff99
    style Active fill:#ffff99
    style Working fill:#ff9999
    style Reserve fill:#cccccc
```

## Context Loading Decision Tree

```mermaid
graph TD
    Start[New Claude Session] --> CheckTask{What's the task?}

    CheckTask -->|Database Work| LoadDB[Load database-agent.md<br/>+ database-design.md]
    CheckTask -->|Import Work| LoadImport[Load i12-import-agent.md<br/>+ import-commands-reference.md]
    CheckTask -->|API Development| LoadAPI[Load api-specifications.md<br/>+ backend-overview.md]
    CheckTask -->|General Dev| LoadCore[Load only core context]

    LoadDB --> CheckTokens{Token Check}
    LoadImport --> CheckTokens
    LoadAPI --> CheckTokens
    LoadCore --> CheckTokens

    CheckTokens -->|Under 50K| Proceed[Proceed with task]
    CheckTokens -->|50K-90K| WarnUser[Warn user<br/>Suggest pruning]
    CheckTokens -->|Over 90K| AutoPrune[Auto-prune<br/>Non-essential context]

    WarnUser --> Proceed
    AutoPrune --> Proceed

    style CheckTask fill:#ffcc99
    style CheckTokens fill:#ff9999
    style Proceed fill:#99ff99
```

## Session Lifecycle

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant Context
    participant Sessions

    User->>Claude: Start new session
    Claude->>Context: Load CLAUDE.md
    Claude->>Context: Load settings.local.json
    Context->>Claude: Core context ready

    User->>Claude: /project:session-start feature-x
    Claude->>Sessions: Create session file
    Claude->>Sessions: Set .current-session
    Sessions->>Claude: Session initialized

    loop During Work
        User->>Claude: Make changes
        Claude->>Context: Load relevant docs as needed
        User->>Claude: /project:session-update
        Claude->>Sessions: Update session progress
    end

    User->>Claude: /project:session-end
    Claude->>Sessions: Finalize session
    Claude->>Sessions: Clear .current-session
    Sessions->>Claude: Session archived
```

## Best Practices for Context Management

### 1. **Modular Loading**
- Core context (CLAUDE.md) stays under 5K tokens
- Load specialized contexts only when needed
- Use agent-specific contexts for focused work

### 2. **Clear Boundaries**
- Shared: Architecture and design docs
- Agents: Task-specific guidance
- Commands: Automation scripts
- Sessions: Work tracking

### 3. **Token Efficiency**
- Monitor token usage continuously
- Prune context between unrelated tasks
- Use references instead of duplicating content

### 4. **Explicit Dependencies**
- CLAUDE.md references other docs but doesn't include them
- Agents reference shared architecture as needed
- Commands are loaded only when invoked

### 5. **Progressive Loading**
- Start with minimal context
- Load additional context based on task
- Unload when switching contexts

## Context Loading Rules

1. **Always Load**:
   - CLAUDE.md (project guide)
   - settings.local.json (configuration)

2. **Load on Reference**:
   - Files mentioned in CLAUDE.md
   - Dependencies of loaded files

3. **Load on Task**:
   - Relevant agent context
   - Associated shared documentation

4. **Never Auto-Load**:
   - Session files (privacy)
   - Command scripts (until invoked)
   - Debug configurations (unless debugging)

## Failure Points and Mitigations

### Common Failures:
1. **Context Overflow**: Too many files loaded
   - Mitigation: Auto-pruning, token monitoring

2. **Stale Context**: Outdated information
   - Mitigation: Progress tracking, session management

3. **Missing Context**: Required info not loaded
   - Mitigation: Clear dependency mapping

4. **Conflicting Context**: Contradictory information
   - Mitigation: Single source of truth principle

### Solutions:
- Use `.claude/shared/` for canonical documentation
- Keep CLAUDE.md as the primary entry point
- Implement clear loading priorities
- Regular context maintenance and updates
