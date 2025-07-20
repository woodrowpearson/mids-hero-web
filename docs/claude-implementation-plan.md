# Claude Code Workflow & Calculation Logic Implementation Plan

## Overview
This document outlines a comprehensive plan to:
1. Complete the Claude Code agent workflow implementation
2. Implement the full calculation logic for the Mids Hero Web application

## Part 1: Claude Code Workflow Implementation

### Task 1: Infrastructure Setup
**Goal**: Ensure all directories and base files exist and are properly configured

#### Sub-tasks:
1.1. Create missing directories
   - Create `.claude/state/logs/` for hook logging
   - Create `.claude/state/sessions/` if not exists
   - Create `.claude/automation/temp/` for temporary processing

1.2. Consolidate configuration files
   - Remove duplicate `settings-hooks.json` 
   - Ensure all hooks are defined in `settings.json`
   - Create `requirements-context.txt` for Python dependencies

1.3. Implement health check system
   - Create `.claude/automation/health-check.py`
   - Verify all hooks are executable
   - Check directory permissions
   - Validate configuration integrity

### Task 2: Advanced Context Management Features
**Goal**: Implement sophisticated context loading and pruning strategies

#### Sub-tasks:
2.1. Implement dynamic tool loadout system
   - Create `.claude/automation/tool-selector.py`
   - Load tools based on current task context
   - Limit to <30 tools per session
   - Cache tool definitions for efficiency

2.2. Create context offloading mechanism
   - Implement `.claude/automation/context-offloader.py`
   - Automatically move verbose output to scratchpad
   - Create context summarization for long sessions
   - Implement retrieval for offloaded content

2.3. Enhance progressive loading
   - Create `.claude/automation/context-loader.py`
   - Implement keyword-based module detection
   - Add context priority scoring
   - Implement smart pruning at 90K tokens

2.4. Implement context quarantine
   - Create subagent configuration for specialized tasks
   - Implement parallel context processing
   - Create isolation boundaries for different modules

### Task 3: Enhanced Hook System
**Goal**: Create comprehensive automation through hooks

#### Sub-tasks:
3.1. Enhance existing hooks
   - Add error handling to all hooks
   - Implement retry logic for failed operations
   - Add performance monitoring

3.2. Create new hooks
   - `pre-session-hook.py`: Initialize session state
   - `context-summarizer.py`: Summarize context at intervals
   - `progress-tracker.py`: Auto-update progress.json
   - `quality-checker.py`: Run tests/lint before commits

3.3. Implement hook orchestration
   - Create `.claude/automation/hook-manager.py`
   - Handle hook dependencies
   - Implement hook failure recovery
   - Add hook performance metrics

### Task 4: Git Commit Hooks
**Goal**: Enforce workflow and quality standards

#### Sub-tasks:
4.1. Create pre-commit hooks
   - `.git/hooks/pre-commit`: Run quality checks
   - Verify branch naming convention
   - Check for TODO items completion
   - Run linting and type checking
   - Ensure CLAUDE.md is under 5K tokens

4.2. Create commit-msg hooks
   - `.git/hooks/commit-msg`: Validate message format
   - Enforce conventional commits
   - Add issue number requirements
   - Append Claude signature when appropriate

4.3. Create post-commit hooks
   - `.git/hooks/post-commit`: Update progress tracking
   - Log commit to session history
   - Update `.claude/state/progress.json`
   - Trigger context pruning if needed

4.4. Create push hooks
   - `.git/hooks/pre-push`: Final quality gates
   - Ensure all tests pass
   - Check for uncommitted changes
   - Validate PR readiness

### Task 5: Session Management
**Goal**: Implement comprehensive session tracking

#### Sub-tasks:
5.1. Create session manager
   - `.claude/automation/session-manager.py`
   - Auto-create session on start
   - Track all operations per session
   - Generate session summaries

5.2. Implement progress tracking
   - Auto-update `progress.json` on task completion
   - Create progress visualization
   - Implement milestone tracking
   - Add time tracking per task

5.3. Create session archival
   - Archive completed sessions
   - Compress old session data
   - Implement session search
   - Create session replay capability

## Part 2: Calculation Logic Implementation

### Task 1: Core Architecture Design
**Goal**: Design scalable calculation system architecture

#### Sub-tasks:
1.1. Create calculation module structure
   - `backend/app/services/calculations/`
   - `├── core/` (base classes and interfaces)
   - `├── powers/` (power-specific calculations)
   - `├── enhancements/` (enhancement system)
   - `├── buffs/` (buff/debuff management)
   - `├── attributes/` (character attributes)
   - `└── formulas/` (calculation formulas)

1.2. Define interfaces and base classes
   - `ICalculationEngine` interface
   - `BasePowerCalculator` abstract class
   - `IEnhancementDiversification` interface
   - `IBuffManager` interface
   - `IAttributeCalculator` interface

1.3. Create data models
   - `CalculationContext` for passing state
   - `PowerCalculationResult` for results
   - `BuffStack` for buff management
   - `AttributeSet` for character stats

### Task 2: Power Calculation System
**Goal**: Implement comprehensive power calculations

#### Sub-tasks:
2.1. Implement power type handlers
   - `TogglePowerCalculator`: Toggles with endurance drain
   - `AutoPowerCalculator`: Passive/auto powers
   - `ClickPowerCalculator`: Active click powers
   - `PetPowerCalculator`: Pet summoning powers

2.2. Create power effect processors
   - Damage calculation (scale with archetype modifiers)
   - Healing calculation
   - Control effect duration
   - Debuff magnitude calculation

2.3. Implement activation mechanics
   - Activation time processing
   - Animation time handling
   - Interrupt handling
   - Recharge calculation

### Task 3: Enhancement & ED System
**Goal**: Implement enhancement diversification

#### Sub-tasks:
3.1. Create ED calculator
   - Implement Schedule A (damage, accuracy, etc.)
   - Implement Schedule B (defense, resistance)
   - Implement Schedule C (special cases)
   - Handle multi-aspect enhancements

3.2. Implement enhancement types
   - Single-origin enhancements (SO)
   - Invention Origin (IO) sets
   - Hamidon Origin (HO) special rules
   - Archetype Origin (ATO) sets
   - Very Rare (Purple) sets

3.3. Create set bonus calculator
   - Track set completion (2-6 pieces)
   - Apply stacking rules (rule of 5)
   - Calculate global bonuses
   - Handle exemplar/malefactor scaling

### Task 4: Buff/Debuff System
**Goal**: Implement comprehensive buff management

#### Sub-tasks:
4.1. Create buff manager
   - Buff stacking rules
   - Duration tracking
   - Magnitude calculation
   - Conflict resolution

4.2. Implement buff categories
   - Damage buffs (melee, ranged, AoE)
   - Defense buffs (positional, typed)
   - Resistance buffs (damage types)
   - Status protection/resistance

4.3. Create debuff system
   - Resistance debuffs
   - Defense debuffs
   - Damage debuffs
   - Special debuffs (slow, -rech, etc.)

### Task 5: Character Attributes
**Goal**: Calculate all character attributes

#### Sub-tasks:
5.1. Implement base attributes
   - Hit Points (base + bonuses)
   - Endurance (max + recovery)
   - Movement (run, fly, jump)
   - Stealth/Perception radius

5.2. Create combat attributes
   - To-hit and accuracy
   - Damage bonuses by type
   - Recharge bonuses
   - Endurance discounts

5.3. Implement resistances
   - Damage resistance (8 types)
   - Status resistance
   - Debuff resistance
   - Resistance caps by AT

5.4. Create defense calculator
   - Positional defense (melee, ranged, AoE)
   - Typed defense (8 damage types)
   - Defense caps (soft/hard)
   - PvP defense scaling

## Implementation Schedule

### Phase 1: Claude Infrastructure (Week 1)
- Complete infrastructure setup
- Implement core context management
- Basic hook system enhancement

### Phase 2: Advanced Claude Features (Week 2)
- Context offloading and summarization
- Advanced hook orchestration
- Git workflow automation

### Phase 3: Calculation Architecture (Week 3)
- Design and implement core architecture
- Create base classes and interfaces
- Set up testing framework

### Phase 4: Core Calculations (Week 4-5)
- Implement power calculations
- Enhancement diversification
- Basic buff system

### Phase 5: Advanced Features (Week 6)
- Complete attribute calculations
- Advanced buff/debuff interactions
- Performance optimization

### Phase 6: Integration & Testing (Week 7)
- Integration with existing API
- Comprehensive testing
- Performance benchmarking

## Success Metrics

### Claude Workflow:
- Context stays under 90K tokens 95% of time
- All hooks execute successfully
- Zero commits to main branch
- Session tracking 100% accurate

### Calculation System:
- All calculations match game formulas
- Response time <30ms for 100 powers
- 100% test coverage
- Handles all edge cases

## Risk Mitigation

1. **Complexity Risk**: Start with simple calculations, add complexity incrementally
2. **Performance Risk**: Implement caching early, profile regularly
3. **Accuracy Risk**: Extensive testing against known game values
4. **Context Bloat**: Aggressive pruning and offloading strategies

## Next Steps

1. Create GitHub issues for each major task
2. Set up project board for tracking
3. Begin with infrastructure tasks
4. Implement in phases with regular testing