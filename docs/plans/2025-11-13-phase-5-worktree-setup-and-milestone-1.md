# Phase 5: Worktree Setup & Milestone 1 Execution

**Date**: 2025-11-13
**Author**: Claude
**Status**: Ready for Execution
**Epic**: Epic 3 - Backend API Development
**Parent Document**: [MidsReborn Calculation Reverse Engineering Design](./2025-11-10-midsreborn-calculation-reverse-engineering-design.md)
**Phase**: 5 of 6 (Worktree Setup → Milestone 1 Foundation)

---

## Executive Summary

This plan details the execution of Phase 5, which bridges the approved design document into actual implementation. The phase focuses on:

1. **Worktree Setup** - Create isolated workspace for documentation work
2. **Milestone 1 Execution** - Foundation documents (navigation + architecture)
3. **Process Establishment** - Workflows for the remaining 43 calculation specs

**Timeline**: 5-7 days (1 week sprint)

**Deliverables**:
- ✅ Clean git worktree for documentation work
- ✅ Navigation map (`00-navigation-map.md`)
- ✅ Architecture overview (`01-architecture-overview.md`)
- ✅ Calculation index (`02-calculation-index.md`)
- ✅ Documentation workflow established

---

## Context & Prerequisites

### What Came Before

The [master design document](./2025-11-10-midsreborn-calculation-reverse-engineering-design.md) established:
- **Top-down methodology**: Architecture → Breadth → Depth
- **43 calculation specifications** to be created
- **3 milestone structure**: Foundation → Breadth → Depth
- **Documentation-first approach**: Specs before implementation

### Why Worktree?

The documentation effort will:
- Generate 46 markdown files (3 foundation + 43 specs)
- Span multiple weeks of work
- Benefit from isolated workspace
- Keep main branch clean during long-running work
- Allow easy experimentation without affecting production

### Prerequisites

- ✅ Master design document approved
- ✅ MidsReborn codebase accessible at `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn`
- ✅ Project repository at `/home/user/mids-hero-web`
- ⚠️ Current branch: `claude/phase-5-planning-document-01BqETFsJCvC3QFDojSfWcaL`
- ⚠️ Must create feature branch for worktree: `feature/midsreborn-calculation-docs`

---

## Phase 5 Objectives

### Primary Goals

1. **Establish Clean Workspace**
   - Create git worktree for documentation work
   - Set up directory structure in `docs/midsreborn/`
   - Ensure no interference with main development

2. **Complete Milestone 1 Foundation**
   - Navigation map for rapid MidsReborn codebase lookup
   - Architecture overview showing calculation flow
   - Master index tracking all 43 specs

3. **Prove the Process**
   - Validate documentation template works
   - Confirm analysis workflow is efficient
   - Establish quality standards in practice

### Success Criteria

✅ **Technical Success**:
- Worktree created and functional
- All 3 foundation documents complete
- Can navigate to any MidsReborn calculation in <2 minutes

✅ **Process Success**:
- Documentation workflow tested and refined
- Time estimates validated (or adjusted)
- Ready to scale to 43 specs in Milestone 2

✅ **Quality Success**:
- Documents follow approved template
- Code references accurate (file paths, class names)
- Clear, actionable information for Python developers

---

## Detailed Task Breakdown

### Task 1: Git Worktree Setup (1-2 hours)

#### Objective
Create isolated workspace for documentation without polluting main branch.

#### Steps

**1.1 Create Feature Branch**
```bash
cd /home/user/mids-hero-web
git checkout main
git pull origin main
git checkout -b feature/midsreborn-calculation-docs
git push -u origin feature/midsreborn-calculation-docs
```

**1.2 Create Worktree**
```bash
# Create worktree in parallel directory
cd /home/user/mids-hero-web
git worktree add ../mids-hero-web-docs feature/midsreborn-calculation-docs

# Verify worktree
git worktree list
```

**1.3 Set Up Documentation Structure**
```bash
cd ../mids-hero-web-docs
mkdir -p docs/midsreborn/calculations
touch docs/midsreborn/.gitkeep
```

**1.4 Create Initial Commit**
```bash
cd ../mids-hero-web-docs
git add docs/midsreborn/
git commit -m "docs(midsreborn): initialize calculation documentation structure"
git push origin feature/midsreborn-calculation-docs
```

#### Validation
- [ ] Worktree appears in `git worktree list`
- [ ] Can switch between main repo and worktree
- [ ] Directory structure exists
- [ ] Initial commit pushed successfully

#### Risks & Mitigations
- **Risk**: Worktree conflicts with existing work
  - **Mitigation**: Use clean feature branch, separate directory
- **Risk**: Confusion about which workspace is active
  - **Mitigation**: Always check `pwd` and `git branch` before commits

---

### Task 2: Navigation Map Creation (2-3 hours)

#### Objective
Create `00-navigation-map.md` - the "phone book" for MidsReborn calculations.

#### Steps

**2.1 Analyze MidsReborn Directory Structure**
```bash
# From main repo (has access to external/)
cd /home/user/mids-hero-web
tree -L 3 external/dev/MidsReborn/MidsReborn/Core/ -I 'obj|bin'
ls -lh external/dev/MidsReborn/MidsReborn/Core/*.cs
```

**2.2 Create File Inventory**
For each key file, document:
- Full path relative to MidsReborn root
- File size (KB)
- Primary purpose (1 sentence)
- Key classes/methods (just names)
- Related files

Priority files:
- `Core/Build.cs`
- `Core/clsToonX.cs`
- `Core/PowerEntry.cs`
- `Core/Enhancement.cs`
- `Core/EnhancementSet.cs`
- `Core/I9Slot.cs`
- `Core/GroupedFx.cs`
- `Core/Stats.cs`
- `Core/DatabaseAPI.cs`

**2.3 Create Calculation Lookup Table**
Map common calculation queries to file locations:
- "Damage calculation" → `PowerEntry.cs`, `Build.cs`
- "Enhancement ED curves" → `Enhancement.cs`
- "Set bonuses" → `EnhancementSet.cs`
- "Archetype modifiers" → `clsToonX.cs`, `DatabaseAPI.cs`
- etc.

**2.4 Document Search Patterns**
Provide ripgrep examples for finding code:
```bash
# Find damage calculations
rg "damage.*scale" Core/

# Find ED curve implementation
rg "enhancement.*diminish|ED.*curve" Core/

# Find set bonus logic
rg "set.*bonus|SetBonus" Core/
```

**2.5 Write Navigation Map Document**
Follow this structure:
```markdown
# MidsReborn Navigation Map

## Quick Start
[TL;DR lookup table]

## Directory Structure
[Full tree with annotations]

## Key Files Reference
[Detailed file-by-file breakdown]

## Calculation Lookup Guide
[Query → File mapping]

## Search Patterns
[Ripgrep commands for common tasks]

## Related Resources
[Links to other docs]
```

#### Validation
- [ ] All Core directory files documented
- [ ] Lookup table has 20+ entries
- [ ] Can find any calculation in <2 minutes using map
- [ ] Search patterns tested and work

#### Deliverable
Complete `docs/midsreborn/00-navigation-map.md` (~1000-1500 lines)

---

### Task 3: Architecture Overview Creation (3-4 hours)

#### Objective
Create `01-architecture-overview.md` - understand how calculations flow through the system.

#### Steps

**3.1 Trace Primary Calculation Flow**

Start at `Build.cs` and trace downward:
```bash
# Read Build.cs to understand entry points
rg "public.*Calculate|Update.*Build" external/dev/MidsReborn/MidsReborn/Core/Build.cs

# Find power calculation orchestration
rg "PowerEntry.*Calculate" external/dev/MidsReborn/MidsReborn/Core/Build.cs

# Trace to Stats.cs for aggregation
rg "Stats.*Update|Calculate.*Totals" external/dev/MidsReborn/MidsReborn/Core/
```

**3.2 Document Major Subsystems**

Identify and document:
1. **Build Management** (`Build.cs`, `clsToonX.cs`)
   - Character state management
   - Build recalculation triggers
   - Data persistence

2. **Power System** (`PowerEntry.cs`, `DatabaseAPI.cs`)
   - Power data loading
   - Effect application
   - Level scaling

3. **Enhancement System** (`Enhancement.cs`, `EnhancementSet.cs`, `I9Slot.cs`)
   - Slotting mechanics
   - ED curve application
   - Set bonus calculation

4. **Effect System** (`GroupedFx.cs`)
   - Effect grouping
   - Buff/debuff aggregation
   - Combat attribute calculation

5. **Aggregation System** (`Stats.cs`)
   - Build totals calculation
   - Cap enforcement
   - Display formatting

**3.3 Create Call Graph Diagrams**

Document key flows:
```
Build Calculation Flow:
Build.RecalculateBuild()
  ├─> clsToonX.UpdateBuild()
  ├─> PowerEntry.CalculatePower()
  │     ├─> Enhancement.ApplyED()
  │     ├─> EnhancementSet.GetSetBonuses()
  │     └─> GroupedFx.AggregateEffects()
  └─> Stats.CalculateTotals()
        ├─> Stats.CalculateDefense()
        ├─> Stats.CalculateResistance()
        ├─> Stats.CalculateRecharge()
        └─> Stats.CalculateDamage()
```

**3.4 Document Data Flow**

Trace how data moves:
```
Database (JSON/SQLite)
  ↓ DatabaseAPI.cs
Power/Enhancement Raw Data
  ↓ Build.cs / clsToonX.cs
Character Build State
  ↓ PowerEntry.cs
Individual Power Stats (with enhancements)
  ↓ GroupedFx.cs
Aggregated Effects
  ↓ Stats.cs
Build Totals (displayed in UI)
```

**3.5 Identify Key Algorithms**

Document major calculation algorithms:
- Enhancement Diminishing Returns (ED)
- Set Bonus Stacking (Rule of 5)
- Archetype Modifier Application
- Buff Stacking Rules
- Proc Chance Calculation
- Incarnate Level Shifts

**3.6 Document Dependencies**

Map which files depend on which:
```
Build.cs
  └─> requires clsToonX.cs, PowerEntry.cs, Stats.cs

PowerEntry.cs
  └─> requires Enhancement.cs, GroupedFx.cs, DatabaseAPI.cs

Enhancement.cs
  └─> requires EnhancementSet.cs, I9Slot.cs
```

**3.7 Write Architecture Document**

Follow this structure:
```markdown
# MidsReborn Architecture Overview

## System Overview
[High-level description]

## Calculation Flow
[Primary flow diagrams]

## Major Subsystems
[Detailed subsystem descriptions]

## Data Flow
[How data moves through system]

## Key Algorithms
[Core calculation algorithms]

## Dependency Graph
[What depends on what]

## Python Implementation Considerations
[How this maps to our architecture]
```

#### Validation
- [ ] Calculation flow traced from Build.cs to Stats.cs
- [ ] All 5 major subsystems documented
- [ ] Call graph diagrams accurate
- [ ] Dependencies mapped
- [ ] Clear enough for Python implementation planning

#### Deliverable
Complete `docs/midsreborn/01-architecture-overview.md` (~1500-2000 lines)

---

### Task 4: Calculation Index Creation (1-2 hours)

#### Objective
Create `02-calculation-index.md` - master tracking document for all 43 specs.

#### Steps

**4.1 Create Spec List Template**

For each of the 43 specs (already defined in master doc):
```markdown
### [XX] - [Calculation Name] (`XX-calculation-name.md`)

**Status**: 🔴 Not Started | 🟡 Breadth Complete | 🟢 Depth Complete
**Priority**: Critical | High | Medium | Low
**Complexity**: Simple | Medium | Complex
**Est. Breadth**: X hours
**Est. Depth**: X hours (priority specs only)
**Dependencies**: [List of other spec numbers this depends on]
**MidsReborn Files**: [Primary file paths]

**Overview**: One sentence describing what this calculation does.

**Progress Notes**:
- YYYY-MM-DD: [Latest status update]
```

**4.2 Assign Priorities**

Based on master doc (Appendix A):
- **Critical**: 01-09, 10-11, 16-17, 19-24 (26 specs)
- **High**: 12-13, 25 (3 specs)
- **Medium**: 18, 29-35 (9 specs)
- **Low**: 36-43 (8 specs)

**4.3 Estimate Effort**

Conservative estimates:
- **Simple spec (breadth)**: 1-2 hours
- **Medium spec (breadth)**: 2-3 hours
- **Complex spec (breadth)**: 3-4 hours
- **Priority spec (depth)**: +4-8 hours on top of breadth

**4.4 Document Dependencies**

Example:
- Spec 02 (Power Damage) depends on Spec 01 (Power Effects Core)
- Spec 11 (Enhancement Slotting) depends on Spec 10 (Enhancement Schedules)
- Spec 19-24 (Build Totals) depend on Specs 01-11

**4.5 Create Status Dashboard**

Add summary section:
```markdown
## Status Dashboard

**Overall Progress**: 0/43 specs complete (0%)

**By Phase**:
- Milestone 1 (Foundation): ✅ 3/3 complete (100%)
- Milestone 2 (Breadth): 🔴 0/43 complete (0%)
- Milestone 3 (Depth): 🔴 0/26 complete (0%)

**By Priority**:
- Critical: 0/26 (0%)
- High: 0/3 (0%)
- Medium: 0/9 (0%)
- Low: 0/8 (0%)

**Last Updated**: YYYY-MM-DD
```

**4.6 Add Workflow Section**

Document how to update the index:
```markdown
## How to Use This Index

### Starting a New Spec
1. Find spec in list below
2. Check dependencies are complete
3. Update status to 🟡 In Progress
4. Add start date to Progress Notes

### Completing Breadth Phase
1. Verify all required sections present
2. Update status to 🟡 Breadth Complete
3. Add completion date to Progress Notes
4. Update dashboard counts

### Completing Depth Phase (Priority Specs Only)
1. Verify algorithm, code snippets, tests present
2. Update status to 🟢 Depth Complete
3. Add completion date to Progress Notes
4. Update dashboard counts
```

**4.7 Write Index Document**

Structure:
```markdown
# MidsReborn Calculation Index

## Status Dashboard
[Current progress]

## How to Use This Index
[Workflow instructions]

## Calculation Specifications

### Power System (01-09)
[9 spec entries]

### Enhancement System (10-15)
[6 spec entries]

### Archetype System (16-18)
[3 spec entries]

### Build Aggregation (19-24)
[6 spec entries]

### Stacking & Interaction (25-28)
[4 spec entries]

### Incarnate System (29-31)
[3 spec entries]

### Special Systems (32-38)
[7 spec entries]

### Edge Cases (39-43)
[5 spec entries]

## Appendix: Dependency Graph
[Visual representation of spec dependencies]
```

#### Validation
- [ ] All 43 specs listed with required fields
- [ ] Priorities assigned correctly
- [ ] Effort estimates reasonable
- [ ] Dependencies documented
- [ ] Status dashboard functional
- [ ] Workflow documented

#### Deliverable
Complete `docs/midsreborn/02-calculation-index.md` (~800-1000 lines)

---

### Task 5: Process Documentation & Handoff (1 hour)

#### Objective
Document the workflow for Milestone 2 (Breadth Coverage) and prepare for execution.

#### Steps

**5.1 Create Workflow Document**

Create `docs/midsreborn/WORKFLOW.md`:
```markdown
# MidsReborn Documentation Workflow

## Daily Workflow for Breadth Phase

1. **Choose Next Spec** (5 min)
   - Open `02-calculation-index.md`
   - Find next spec with dependencies met
   - Update status to 🟡 In Progress

2. **Analyze MidsReborn Code** (30-60 min)
   - Use `00-navigation-map.md` to find files
   - Read relevant C# code
   - Use ripgrep to find related methods
   - Take notes on key algorithms

3. **Write Spec Document** (30-60 min)
   - Follow template from master design doc
   - Complete breadth-level sections
   - Skip depth-level details (defer to Milestone 3)

4. **Update Index** (5 min)
   - Mark spec as 🟡 Breadth Complete
   - Update dashboard counts
   - Commit changes

5. **Commit & Continue**
   - Commit spec document
   - Move to next spec

## Tools Reference

### Finding Code
```bash
# Use navigation map first
# Then use ripgrep for specific searches
rg "pattern" external/dev/MidsReborn/MidsReborn/Core/
```

### Reading Files
```bash
# VS Code with C# extension
code external/dev/MidsReborn/MidsReborn/Core/[File].cs
```

### Updating Progress
```bash
# After completing spec
cd /home/user/mids-hero-web-docs
git add docs/midsreborn/
git commit -m "docs(midsreborn): complete spec XX - [name]"
git push origin feature/midsreborn-calculation-docs
```

## Quality Checklist

Before marking spec as Breadth Complete:
- [ ] Overview section complete
- [ ] Primary location documented (file, class, methods)
- [ ] High-level pseudocode present
- [ ] Game mechanics context explained
- [ ] References to related specs
- [ ] Index updated

## Tips for Efficiency

- Work in batches (3-5 specs per session)
- Related specs together (e.g., all Build Totals)
- Use ripgrep extensively
- Don't deep-dive in breadth phase
- If stuck >1 hour, mark unclear and move on
```

**5.2 Create Branch Handoff Document**

Document current state for next session:
```markdown
# Phase 5 Handoff

**Date Completed**: 2025-11-XX
**Branch**: feature/midsreborn-calculation-docs
**Worktree**: /home/user/mids-hero-web-docs

## Completed
- ✅ Worktree setup
- ✅ Navigation map
- ✅ Architecture overview
- ✅ Calculation index

## Ready for Milestone 2
- All 43 specs defined and prioritized
- Workflow documented
- Foundation complete

## Next Steps
1. Begin breadth coverage of specs 01-43
2. Follow workflow in WORKFLOW.md
3. Update index as specs complete
4. Target: All 43 specs at breadth level in 3 weeks

## Git Commands for Next Session
```bash
# Resume work
cd /home/user/mids-hero-web-docs
git pull origin feature/midsreborn-calculation-docs

# Continue work...

# When breadth complete
git push origin feature/midsreborn-calculation-docs
gh pr create --title "docs: MidsReborn calculation specifications (breadth coverage)"
```
```

**5.3 Update Main Project Progress**

Update `.claude/state/progress.json` in main repo:
```json
{
  "epic_3_backend_api": {
    "status": "in_progress",
    "completion": 27,
    "tasks": {
      "task_3_2_calculation_engine": {
        "status": "in_progress",
        "subtasks": {
          "reverse_engineering_docs": {
            "status": "in_progress",
            "milestone_1_foundation": "complete",
            "milestone_2_breadth": "ready",
            "milestone_3_depth": "blocked_by_milestone_2"
          }
        }
      }
    }
  }
}
```

#### Validation
- [ ] Workflow document clear and actionable
- [ ] Handoff document complete
- [ ] Progress updated in main repo
- [ ] Ready to begin Milestone 2

#### Deliverable
- `docs/midsreborn/WORKFLOW.md`
- Handoff notes
- Updated progress tracking

---

## Timeline & Milestones

### Day 1: Worktree Setup (2-3 hours)
- Morning: Git worktree creation and validation
- Afternoon: Directory structure and initial commits

**Checkpoint**: Worktree operational, can commit/push

### Day 2-3: Navigation Map (4-6 hours)
- Day 2 AM: MidsReborn directory analysis
- Day 2 PM: File inventory and lookup table
- Day 3 AM: Search patterns and documentation
- Day 3 PM: Review and refinement

**Checkpoint**: Can find any calculation in <2 minutes

### Day 4-5: Architecture Overview (6-8 hours)
- Day 4 AM: Trace calculation flow
- Day 4 PM: Document major subsystems
- Day 5 AM: Create diagrams and dependency maps
- Day 5 PM: Write and review document

**Checkpoint**: Understand how calculations flow through system

### Day 6: Calculation Index (3-4 hours)
- Morning: Create index structure, assign priorities
- Afternoon: Estimate effort, document workflow

**Checkpoint**: All 43 specs tracked and ready

### Day 7: Process Documentation (2-3 hours)
- Morning: Create workflow guide
- Afternoon: Handoff documentation and progress update

**Checkpoint**: Ready for Milestone 2 execution

**Total Estimated Time**: 17-24 hours (spread over 5-7 days)

---

## Resource Requirements

### Access Requirements
- ✅ Read access to MidsReborn codebase
- ✅ Write access to mids-hero-web repository
- ✅ Git worktree capabilities

### Tool Requirements
- ✅ ripgrep (`rg`) for code search
- ✅ VS Code or editor with C# syntax highlighting
- ✅ Git CLI for worktree management
- ✅ Markdown editor for documentation

### Knowledge Requirements
- ✅ Basic C# reading comprehension
- ✅ Git worktree concepts
- ✅ City of Heroes game mechanics (helpful but not required)

---

## Quality Standards

### Documentation Requirements

**All Foundation Documents Must Have**:
- Clear purpose statement
- Navigable structure (TOC, headers)
- Accurate file paths and references
- Examples where helpful
- Links to related documents

**Navigation Map Requirements**:
- Complete file inventory
- Accurate file sizes and descriptions
- Working ripgrep examples
- Lookup table with 20+ entries

**Architecture Overview Requirements**:
- Complete calculation flow traced
- All major subsystems documented
- Call graphs accurate
- Dependencies mapped

**Calculation Index Requirements**:
- All 43 specs listed
- Status tracking functional
- Priorities assigned
- Effort estimates present

### Review Criteria

Before marking Milestone 1 complete:
- [ ] All 3 documents exist and are complete
- [ ] Navigation map tested (can find 10 random calculations in <2 min each)
- [ ] Architecture overview validated (calculation flow correct)
- [ ] Index functional (can update status, track progress)
- [ ] Workflow documented and tested
- [ ] No broken links or references
- [ ] Formatting consistent across documents

---

## Risk Management

### Risk: Worktree Complexity

**Problem**: Team unfamiliar with git worktrees
**Impact**: Confusion, accidental commits to wrong branch
**Probability**: Medium
**Mitigation**:
- Document worktree commands clearly
- Always check `pwd` and `git branch` before commits
- Use separate terminal window for worktree work
**Contingency**: Can abandon worktree and work on regular feature branch

### Risk: MidsReborn Codebase Complexity

**Problem**: C# code harder to understand than expected
**Impact**: Delays in navigation map and architecture docs
**Probability**: Medium
**Mitigation**:
- Focus on WHAT not HOW in foundation phase
- Use ripgrep to find patterns, not deep-dive code
- Document unknowns as "needs further investigation"
**Contingency**: Spend more time on specific subsystems in Milestone 2

### Risk: Scope Creep in Foundation

**Problem**: Getting too detailed in foundation docs
**Impact**: Spending days on navigation/architecture instead of hours
**Probability**: High
**Mitigation**:
- Strict timeboxing (navigation: 6 hours max, architecture: 8 hours max)
- Focus on breadth, not depth
- "Good enough" is sufficient for foundation
**Contingency**: Mark sections as "to be expanded in Milestone 2/3"

### Risk: Estimation Accuracy

**Problem**: Time estimates for 43 specs may be wrong
**Impact**: Milestone 2 takes longer than expected
**Probability**: Medium
**Mitigation**:
- Track actual time for first 5 specs
- Adjust estimates in index based on reality
- Prioritize critical specs first
**Contingency**: Re-scope Milestone 3 (fewer specs get full depth)

---

## Success Criteria

### Phase 5 Complete When:

✅ **Worktree Success**:
- Git worktree created and functional
- Can commit and push from worktree
- No conflicts with main development work

✅ **Navigation Success**:
- Navigation map complete and accurate
- Can find any calculation source in <2 minutes
- Ripgrep examples all work

✅ **Architecture Success**:
- Architecture overview traces full calculation flow
- All major subsystems documented
- Dependency graph clear

✅ **Index Success**:
- All 43 specs listed with metadata
- Status tracking functional
- Dashboard shows current progress

✅ **Process Success**:
- Workflow documented and validated
- Ready to begin Milestone 2
- Handoff clear for next session

### Validation Tests

**Navigation Test**:
- Given: "Where is damage calculation implemented?"
- Expected: Find answer in <2 minutes using navigation map
- Files: `PowerEntry.cs`, `Build.cs`, methods identified

**Architecture Test**:
- Given: "How does a power calculation become a build total?"
- Expected: Trace flow using architecture overview
- Path: Build.cs → PowerEntry.cs → GroupedFx.cs → Stats.cs

**Index Test**:
- Given: Need to implement enhancement schedules
- Expected: Find spec 10, check dependencies, see priority
- Result: Critical priority, depends on spec 01, estimated 3 hours breadth + 6 hours depth

---

## Handoff to Milestone 2

After Phase 5 completes, Milestone 2 (Breadth Coverage) begins.

### Milestone 2 Overview

**Goal**: Create all 43 calculation specs at breadth level

**Duration**: 3-4 weeks (43 specs × 2-3 hours average = 86-129 hours)

**Approach**:
- Work through specs in numerical order (respecting dependencies)
- Use workflow documented in WORKFLOW.md
- Update index as each spec completes
- Weekly progress reviews

**Entry Criteria** (Phase 5 outputs):
- ✅ Navigation map complete
- ✅ Architecture overview complete
- ✅ Calculation index ready
- ✅ Workflow documented

**Exit Criteria** (Milestone 2 outputs):
- ✅ All 43 specs exist
- ✅ Each spec has breadth-level content (overview, location, pseudocode, context)
- ✅ Index shows "Breadth Complete" for all specs
- ✅ Ready for Milestone 3 depth dive on priority specs

---

## Git Workflow

### Branch Strategy

```
main (production)
  └─> feature/midsreborn-calculation-docs (long-lived feature branch)
        └─> [worktree at ../mids-hero-web-docs]
```

### Commit Strategy

**Atomic Commits for Each Deliverable**:
```bash
# After completing navigation map
git add docs/midsreborn/00-navigation-map.md
git commit -m "docs(midsreborn): add navigation map for MidsReborn codebase"

# After completing architecture overview
git add docs/midsreborn/01-architecture-overview.md
git commit -m "docs(midsreborn): add architecture overview for calculation system"

# After completing calculation index
git add docs/midsreborn/02-calculation-index.md
git commit -m "docs(midsreborn): add calculation index tracking all 43 specs"

# After completing workflow
git add docs/midsreborn/WORKFLOW.md
git commit -m "docs(midsreborn): add documentation workflow guide"
```

### Push Strategy

**Push After Each Major Deliverable**:
- After navigation map complete: push
- After architecture overview complete: push
- After calculation index complete: push
- After workflow complete: push

**Benefits**:
- Regular backups
- Progress visible to team
- Can get early feedback

### PR Strategy

**When to Create PR**:
- After Milestone 1 complete (Phase 5)
- Draft PR initially
- Convert to ready when Milestone 2 complete
- Merge after Milestone 3 complete

**PR Description Template**:
```markdown
## MidsReborn Calculation Documentation

### Phase 5 - Milestone 1 Foundation

This PR adds foundation documentation for reverse engineering MidsReborn calculation engine.

**Deliverables**:
- Navigation map for rapid codebase lookup
- Architecture overview showing calculation flow
- Index tracking all 43 calculation specs
- Workflow guide for continued documentation

**Status**: Milestone 1 Complete (Foundation)
**Next**: Milestone 2 - Breadth coverage of all 43 specs

### Files Added
- `docs/midsreborn/00-navigation-map.md` - Quick reference for finding calculations
- `docs/midsreborn/01-architecture-overview.md` - System architecture and calculation flow
- `docs/midsreborn/02-calculation-index.md` - Master tracking for 43 specs
- `docs/midsreborn/WORKFLOW.md` - Documentation workflow guide

### Testing
- [x] Navigation map tested (can find calculations in <2 min)
- [x] Architecture flow validated against MidsReborn code
- [x] Index tracking functional
- [x] All links and references valid

### Related
- Parent Document: docs/plans/2025-11-10-midsreborn-calculation-reverse-engineering-design.md
- Epic: Epic 3 - Backend API Development
- Task: 3.2 - Build Simulation & Calculation Endpoints
```

---

## Appendix A: File Structure After Phase 5

```
/home/user/mids-hero-web/
├── docs/
│   ├── plans/
│   │   ├── 2025-11-10-midsreborn-calculation-reverse-engineering-design.md (existing)
│   │   └── 2025-11-13-phase-5-worktree-setup-and-milestone-1.md (this document)
│   └── midsreborn/
│       ├── 00-navigation-map.md (NEW - Task 2)
│       ├── 01-architecture-overview.md (NEW - Task 3)
│       ├── 02-calculation-index.md (NEW - Task 4)
│       ├── WORKFLOW.md (NEW - Task 5)
│       └── calculations/ (empty, ready for Milestone 2)
└── external/
    └── dev/
        └── MidsReborn/
            └── MidsReborn/
                └── Core/ (analysis target)

/home/user/mids-hero-web-docs/ (NEW - Task 1 - worktree)
└── [same structure as above, but isolated workspace]
```

---

## Appendix B: Tool Commands Reference

### Git Worktree Commands

```bash
# Create worktree
git worktree add <path> <branch>

# List worktrees
git worktree list

# Remove worktree
git worktree remove <path>

# Prune stale worktrees
git worktree prune
```

### MidsReborn Analysis Commands

```bash
# Find file by name
fd "Build.cs" external/dev/MidsReborn/

# Find all .cs files in Core
fd -e cs . external/dev/MidsReborn/MidsReborn/Core/

# Search for pattern in C# files
rg "Calculate.*Damage" external/dev/MidsReborn/ -t cs

# Count lines in file
wc -l external/dev/MidsReborn/MidsReborn/Core/Build.cs

# Get file size
ls -lh external/dev/MidsReborn/MidsReborn/Core/Build.cs
```

### Documentation Commands

```bash
# Create markdown file
touch docs/midsreborn/00-navigation-map.md

# Edit with VS Code
code docs/midsreborn/00-navigation-map.md

# Preview markdown (if using VS Code)
# Cmd/Ctrl + Shift + V
```

---

## Appendix C: Example Navigation Map Entry

```markdown
### Build.cs

**Path**: `Core/Build.cs`
**Size**: 104 KB (~3,500 lines)
**Purpose**: Master build orchestrator - manages character builds, coordinates all calculations

**Key Classes**:
- `Build` - Main build management class

**Key Methods**:
- `RecalculateBuild()` - Triggers full build recalculation
- `CalculatePowerStats()` - Individual power calculations
- `UpdateTotals()` - Aggregate build totals
- `ApplyArchetypeModifiers()` - Apply AT scaling

**Dependencies**:
- Uses: `clsToonX.cs`, `PowerEntry.cs`, `Stats.cs`, `DatabaseAPI.cs`
- Used by: Main application UI

**Related Calculations**:
- All power calculations start here
- Orchestrates enhancement application
- Coordinates archetype modifiers
- Triggers stats aggregation

**Search Patterns**:
```bash
# Find damage calculation code
rg "damage.*calc" external/dev/MidsReborn/MidsReborn/Core/Build.cs

# Find archetype modifier application
rg "archetype.*scale|AT.*modifier" external/dev/MidsReborn/MidsReborn/Core/Build.cs
```
```

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-13 | Claude | Initial Phase 5 planning document created |

---

## Approval & Sign-off

**Document Status**: ✅ Ready for Execution

**Prerequisites**:
- [x] Master design document approved
- [x] Branch strategy confirmed
- [x] MidsReborn codebase accessible
- [x] Timeline acceptable

**Next Action**: Begin Task 1 - Git Worktree Setup

**Estimated Start**: Immediate
**Estimated Completion**: 2025-11-20 (1 week)

---

*This document is part of the MidsReborn Calculation Documentation project. See parent document for full context.*
