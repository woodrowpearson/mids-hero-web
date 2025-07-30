# Claude Context System Overview

## How Context Loading Works Now

```mermaid
graph TB
    subgraph "Session Start"
        User[User starts Claude] --> Core[Load Core Context<br/>~10K tokens total]
        Core --> CLAUDE[CLAUDE.md<br/>2K tokens]
        Core --> Settings[settings.json<br/>3K tokens]
        Core --> Map[context-map.json<br/>2K tokens]
        Core --> Auto[Auto-loaded files<br/>3K tokens]
    end
    
    subgraph "Task Declaration"
        User2[User: 'I need to work on X'] --> Detect{Detect Keywords}
        Detect -->|"database"| LoadDB[Load Database Module<br/>+15K tokens]
        Detect -->|"import"| LoadImport[Load Import Module<br/>+15K tokens]
        Detect -->|"api"| LoadAPI[Load API Module<br/>+15K tokens]
        Detect -->|"frontend"| LoadFE[Load Frontend Module<br/>+15K tokens]
    end
    
    subgraph "Working Context"
        LoadDB --> Work[Total: ~25K tokens<br/>Core + Module]
        LoadImport --> Work
        LoadAPI --> Work
        LoadFE --> Work
        Work --> Available[103K tokens available<br/>for conversation]
    end
    
    style Core fill:#99ff99
    style Work fill:#ffff99
    style Available fill:#99ccff
```

## Token Budget Visualization

```mermaid
pie title "128K Token Allocation"
    "Core Context" : 10
    "Active Module" : 15
    "Conversation" : 80
    "Safety Reserve" : 23
```

## Context Loading Decision Flow

```mermaid
flowchart LR
    Start[Session Start] --> LoadCore[Load CLAUDE.md]
    LoadCore --> CheckTask{Task Mentioned?}
    
    CheckTask -->|Yes| LoadModule[Load Relevant Module]
    CheckTask -->|No| WaitTask[Wait for Task Declaration]
    
    LoadModule --> CheckTokens{Under 50K?}
    WaitTask --> UserSays[User Declares Task]
    UserSays --> LoadModule
    
    CheckTokens -->|Yes| Ready[Ready to Work]
    CheckTokens -->|No| Prune[Prune Old Context]
    Prune --> Ready
    
    Ready --> Monitor[Monitor Token Usage]
    Monitor -->|90K Warning| Alert[Alert User]
    Monitor -->|110K Limit| AutoPrune[Auto-prune]
    
    style LoadCore fill:#99ff99
    style Ready fill:#99ff99
    style Alert fill:#ffcc99
    style AutoPrune fill:#ff9999
```

## File Organization Map

```mermaid
graph TD
    subgraph ".claude/"
        README[README.md<br/>System Explanation]
        Settings[settings.json<br/>Behavior Config]
        Map[context-map.json<br/>Loading Rules]
        
        subgraph "core/"
            Guide[project-guide.md<br/>Essential Info]
            Quick[quick-reference.md<br/>Common Commands]
        end
        
        subgraph "modules/"
            subgraph "database/"
                DBGuide[guide.md<br/>How to Work]
                DBSchema[schema-reference.md<br/>Table Details]
            end
            
            subgraph "import/"
                ImpGuide[guide.md<br/>Import Process]
                ImpCmd[commands-reference.md<br/>CLI Reference]
            end
            
            subgraph "api/"
                APIGuide[guide.md]
                APISpec[specification.md]
            end
            
            subgraph "frontend/"
                FEGuide[guide.md]
                FEArch[architecture.md]
            end
        end
        
        subgraph "workflows/"
            Daily[daily.md<br/>Dev Workflow]
            Trouble[troubleshooting.md<br/>Fix Issues]
            Release[release.md<br/>Deploy Process]
        end
        
        subgraph "automation/"
            Scripts[Shell Scripts<br/>Pre-approved]
            Session[session/<br/>Session Mgmt]
        end
        
        subgraph "state/"
            Progress[progress.json<br/>Project State]
            Current[current-session.json<br/>Active Work]
        end
    end
    
    style README fill:#ff9999
    style Settings fill:#99ccff
    style Map fill:#99ff99
```

## Benefits Realized

### Before (Monolithic)
- 15K+ tokens always loaded
- Information scattered
- No clear loading strategy
- Context overflow common

### After (Modular)
- 10K core + task modules
- Clear organization
- Explicit loading rules
- Efficient token usage

## Quick Reference

| Command | Purpose | Context Loaded |
|---------|---------|----------------|
| "work on database" | Database tasks | +database module |
| "import data" | Import operations | +import module |
| "build API" | API development | +api module |
| "React component" | Frontend work | +frontend module |
| "fix error" | Debugging | +troubleshooting |

## Key Files

1. **CLAUDE.md** - Your entry point (2K tokens)
2. **.claude/README.md** - How this system works
3. **.claude/context-map.json** - All loading rules
4. **.claude/core/** - Always loaded essentials
5. **.claude/modules/** - Task-specific contexts

---
*This reorganization reduces context size by 33% while improving clarity and maintainability.*