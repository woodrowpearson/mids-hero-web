# MidsReborn Calculation Engine - Reverse Engineering Design

**Date**: 2025-11-10
**Author**: Claude (with user guidance)
**Status**: Design Approved
**Epic**: Epic 3 - Backend API Development
**Related**: Task 3.2 - Build Simulation & Calculation Endpoints

---

## Executive Summary

This document outlines the comprehensive plan to reverse engineer the MidsReborn calculation engine and create documentation that will enable accurate Python reimplementation in Mids Hero Web. The approach is **top-down architecture mapping** with **breadth-first documentation**, prioritizing system-wide understanding before deep implementation details.

### Key Deliverables

1. **Repository Navigation Map** - Quick reference for finding any calculation in MidsReborn codebase
2. **Architecture Overview** - System-wide calculation flow from Build.cs downward
3. **43 Calculation Specifications** - Comprehensive coverage of all City of Heroes mechanics

### Timeline

- **Milestone 1** (Week 1): Foundation documents (navigation + architecture)
- **Milestone 2** (Weeks 2-4): All 43 specs at breadth level
- **Milestone 3** (Weeks 5-8): Priority specs with full implementation detail

---

## Background & Motivation

### Current State

- ✅ **Epic 2.6 Complete**: Production data imported (20 archetypes, 371 powersets, 2,285 powers)
- ✅ **Database Schema**: Full SQLAlchemy models with power_data JSONB column
- ⚠️ **Epic 3 Status**: Only 10% complete - basic CRUD endpoints exist, NO calculation logic
- ❌ **Calculation Engine**: Completely missing - placeholder code returns fake hardcoded data

### The Problem

City of Heroes calculations are **extremely complex**:
- Enhancement Diminishing Returns (ED) with 4 different schedule curves
- Archetype-specific modifiers for same power (Tanker vs Scrapper Invulnerability)
- Set bonus stacking with "Rule of 5" suppression
- Proc mechanics (flat % vs PPM) with AoE/recharge interactions
- Buff stacking rules (some additive, some multiplicative)
- Incarnate level shifts and scaling
- Pet/pseudopet calculations
- Exemplar/attuned behavior

**Without accurate calculations, Mids Hero Web cannot function as a build planner.**

### Why Reverse Engineering?

The MidsReborn C# codebase contains **15+ years of accumulated game mechanic knowledge**:
- Bug fixes and edge cases
- Undocumented game behavior ("bugs as features")
- Community-validated formulas
- Historical Issue X changes

Rather than rediscover this through trial-and-error, we'll systematically extract and document it.

---

## Goals & Non-Goals

### Goals

✅ **Documentation-First Approach**
- Create comprehensive specs for ALL calculations before implementation
- Enable any Python developer to implement calculations without C# knowledge
- Provide clear MidsReborn→Python translation guidance

✅ **Navigable Knowledge Base**
- Developer can find any calculation source in <2 minutes
- All file paths, class names, method names documented
- Dependency relationships mapped

✅ **Complete Coverage**
- 43 calculation specification documents covering entire game mechanic system
- From basic damage to complex Incarnate abilities
- Edge cases and special mechanics documented

✅ **Implementation-Ready Specs**
- Priority calculations include full algorithm pseudocode
- Test cases with known inputs/outputs from MidsReborn
- Python architecture guidance referencing existing models

### Non-Goals

❌ **Implementation** - This phase produces documentation only, not Python code
❌ **Testing** - Test strategies documented, but no test suites created
❌ **Performance** - Optimization is implementation-phase concern
❌ **UI/UX** - Focus is backend calculation logic only

---

## Architecture & Approach

### Top-Down Methodology

**Phase 1: Foundation** - Understand the big picture
- Map MidsReborn repository structure
- Identify entry points (Build.cs, clsToonX.cs, PowerEntry.cs)
- Trace calculation orchestration flow

**Phase 2: Breadth Coverage** - Survey the landscape
- Create 43 calculation specs at high level
- Document WHAT exists and WHERE it lives
- Identify dependencies and relationships

**Phase 3: Depth Detail** - Implementation-ready specs
- Priority calculations get full algorithm detail
- Extract C# code snippets with line numbers
- Write Python implementation guides

### MidsReborn Codebase Structure

```
/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/
├── Core/
│   ├── Build.cs                    # Master build orchestrator (104 KB)
│   ├── clsToonX.cs                 # Character/build state (165 KB)
│   ├── PowerEntry.cs               # Individual power calculations (17 KB)
│   ├── Enhancement.cs              # Enhancement logic (16 KB)
│   ├── EnhancementSet.cs           # Set bonuses (17 KB)
│   ├── I9Slot.cs                   # Slotting mechanics (26 KB)
│   ├── GroupedFx.cs                # Effect grouping (105 KB)
│   ├── Stats.cs                    # Build totals (24 KB)
│   ├── DatabaseAPI.cs              # Data access layer (136 KB)
│   └── Base/
│       └── Master_Classes/
│           └── Utilities.cs        # Helper functions
├── Data/                           # JSON data files (ignored - using City of Data)
└── Forms/                          # UI code (not relevant)
```

**Key Entry Points**:
1. `Build.cs` - Orchestrates all build calculations
2. `clsToonX.cs` - Maintains character state, triggers recalculations
3. `PowerEntry.cs` - Calculates individual power stats with enhancements
4. `Stats.cs` - Aggregates powers into build totals

---

## Documentation Structure

### Repository Layout

```
docs/midsreborn/
├── 00-navigation-map.md              # START HERE - Find anything fast
├── 01-architecture-overview.md       # How the system fits together
├── 02-calculation-index.md           # Master list of all 43 specs with status
└── calculations/
    ├── 01-power-effects-core.md
    ├── 02-power-damage.md
    ├── 03-power-buffs-debuffs.md
    ├── 04-power-control-effects.md
    ├── 05-power-healing-absorption.md
    ├── 06-power-endurance-recovery.md
    ├── 07-power-recharge-modifiers.md
    ├── 08-power-accuracy-tohit.md
    ├── 09-power-defense-resistance.md
    ├── 10-enhancement-schedules.md
    ├── 11-enhancement-slotting.md
    ├── 12-enhancement-io-procs.md
    ├── 13-enhancement-set-bonuses.md
    ├── 14-enhancement-special-ios.md
    ├── 15-enhancement-frankenslotting.md
    ├── 16-archetype-modifiers.md
    ├── 17-archetype-caps.md
    ├── 18-archetype-inherents.md
    ├── 19-build-totals-defense.md
    ├── 20-build-totals-resistance.md
    ├── 21-build-totals-recharge.md
    ├── 22-build-totals-damage.md
    ├── 23-build-totals-accuracy.md
    ├── 24-build-totals-other-stats.md
    ├── 25-buff-stacking-rules.md
    ├── 26-diminishing-returns.md
    ├── 27-suppression-mechanics.md
    ├── 28-combat-attributes.md
    ├── 29-incarnate-alpha-shifts.md
    ├── 30-incarnate-abilities.md
    ├── 31-incarnate-core-radial.md
    ├── 32-pet-calculations.md
    ├── 33-pseudopet-mechanics.md
    ├── 34-proc-chance-formulas.md
    ├── 35-proc-interactions.md
    ├── 36-enhancement-boosters.md
    ├── 37-attuned-ios.md
    ├── 38-purple-pvp-ios.md
    ├── 39-power-customization.md
    ├── 40-powerset-relationships.md
    ├── 41-level-scaling.md
    ├── 42-exemplar-mechanics.md
    └── 43-special-cases.md
```

### Calculation Specification Template

Each of the 43 calculation specs follows this standard format:

```markdown
# [Calculation Name]

## Overview
- **Purpose**: What this calculation does in game terms
- **Used By**: Which systems depend on this
- **Complexity**: Simple/Medium/Complex
- **Priority**: Critical/High/Medium/Low for initial implementation

## MidsReborn Implementation

### Primary Location
- **File**: `Core/[FileName.cs]`
- **Class**: `ClassName`
- **Methods**:
  - `MethodName()` - Lines XXX-YYY
  - `OtherMethod()` - Lines ZZZ-AAA

### Dependencies
- Related classes and their roles
- Data structures used (enums, constants, lookup tables)
- External data sources (DatabaseAPI calls, config files)

### Algorithm Pseudocode
```
FUNCTION CalculateSomething(input_params):
    // Step-by-step logic extracted from C#
    // Include all branches, edge cases, special handling
    RETURN result
```

### Key Logic Snippets
```csharp
// Actual C# code excerpts showing critical calculations
// With line numbers and file references
```

## Game Mechanics Context
- Why this calculation exists (game balance, power fantasy, etc.)
- Historical context if relevant (Issue X changes, etc.)
- Known quirks or "bugs as features"

## Python Implementation Guide

### Proposed Architecture
- Where in Mids Hero Web this should live
- Suggested Python module/class structure
- Dependencies on other calculations

### Implementation Notes
- Gotchas to watch for (C# vs Python differences)
- Edge cases to test
- Performance considerations
- Validation strategy (how to verify correctness)

### Test Cases
- Known inputs and expected outputs
- Edge cases to cover
- Comparison data from MidsReborn

## References
- Related calculation specs
- Forum posts/wikis explaining mechanic
- MidsReborn GitHub issues if relevant
```

---

## Calculation Specifications Breakdown

### Power System (9 specs)

**01-power-effects-core.md** - Foundation of all calculations
- IEffect interface and effect types
- GroupedFx.cs effect grouping/aggregation
- How powers store and apply effects

**02-power-damage.md** - Damage calculation all types
- Base damage values from power data
- Scale values and archetype modifiers
- Damage type (smashing, lethal, fire, cold, energy, negative, toxic, psionic)

**03-power-buffs-debuffs.md** - Buff/debuff mechanics
- Positive and negative modifiers
- Duration, magnitude, probability
- Buff categories and how they stack

**04-power-control-effects.md** - Mez mechanics
- Hold, stun, sleep, immobilize, confuse, fear, placate
- Magnitude vs protection
- Duration and resistance

**05-power-healing-absorption.md** - HP restoration
- Healing over time vs instant
- Absorption mechanics (temp HP)
- Regeneration rate modifications

**06-power-endurance-recovery.md** - Endurance management
- Endurance cost calculations
- Recovery rate buffs
- Endurance drain/sap mechanics

**07-power-recharge-modifiers.md** - Recharge time
- Base recharge from power data
- Recharge reduction buffs (both local and global)
- Recharge floors and caps

**08-power-accuracy-tohit.md** - Hit chance calculation
- Accuracy vs ToHit (different mechanics)
- Accuracy multipliers from enhancements
- ToHit buffs and Defense interaction

**09-power-defense-resistance.md** - Mitigation
- Defense by damage type
- Resistance by damage type
- DDR (Defense Debuff Resistance)

### Enhancement System (6 specs)

**10-enhancement-schedules.md** - ED curves (CRITICAL)
- Schedule A, B, C, D curves
- Diminishing returns formulas
- How different attributes use different schedules

**11-enhancement-slotting.md** - How enhancements work
- Slot allocation by power
- Enhancement level effectiveness
- Combining multiple enhancements

**12-enhancement-io-procs.md** - All proc types
- Damage procs (flat % vs PPM)
- Heal procs
- Endurance procs
- Other special procs (knockdown, etc.)

**13-enhancement-set-bonuses.md** - Set bonus mechanics (CRITICAL)
- How set bonuses activate (2/3/4/5/6 piece)
- Rule of 5 suppression
- Global vs local bonuses

**14-enhancement-special-ios.md** - Unique IOs
- Global recharge (e.g., Luck of the Gambler 7.5%)
- Unique effects (e.g., Stealth IO)
- Proc-only enhancements

**15-enhancement-frankenslotting.md** - Mixed sets
- Combining pieces from multiple sets
- When set bonuses don't apply
- Optimization strategies

### Archetype System (3 specs)

**16-archetype-modifiers.md** - AT scaling (CRITICAL)
- Damage scale by AT
- Buff/debuff modifiers by AT
- Control duration modifiers
- Same power, different stats per AT

**17-archetype-caps.md** - Stat limits by AT (CRITICAL)
- Defense caps (45% for most, higher for Tankers)
- Resistance caps (75% for most, 90% for Tankers)
- Damage caps
- Recharge caps (if any)

**18-archetype-inherents.md** - Inherent powers
- Fury (Brute)
- Defiance (Blaster)
- Containment (Controller)
- Critical Hit (Scrapper/Stalker)
- Gauntlet (Tanker)
- Vigilance (Defender)
- Scourge (Corruptor)
- Domination (Dominator)
- Supremacy (Mastermind)

### Build Aggregation (6 specs)

**19-build-totals-defense.md** - Aggregate defense
- Summing defense bonuses from all sources
- Typed vs positional defense
- Displaying in UI

**20-build-totals-resistance.md** - Aggregate resistance
- Summing resistance from all sources
- Damage type breakdown
- Cap enforcement

**21-build-totals-recharge.md** - Global recharge
- How recharge buffs combine
- Displaying as +% or seconds
- Effect on all powers

**22-build-totals-damage.md** - Damage bonus totals
- Global damage buffs
- Type-specific damage (e.g., +fire damage)
- Melee/ranged/AoE categories

**23-build-totals-accuracy.md** - Accuracy/ToHit totals
- Global accuracy bonuses
- ToHit buffs
- Display format

**24-build-totals-other-stats.md** - Everything else
- HP, endurance, recovery, regeneration
- Movement speed
- Perception, stealth
- Various resistances (slow, recharge debuff, etc.)

### Stacking & Interaction (4 specs)

**25-buff-stacking-rules.md** - How buffs combine
- Additive vs multiplicative
- Same-source vs different-source
- Power-specific rules

**26-diminishing-returns.md** - DR beyond ED
- Any other diminishing return mechanics
- Soft caps vs hard caps

**27-suppression-mechanics.md** - Power suppression
- Certain powers suppress in combat
- Travel power suppression
- Stealth suppression

**28-combat-attributes.md** - Real Numbers
- How MidsReborn mimics in-game combat attributes window
- All visible stats and their calculations

### Incarnate System (3 specs)

**29-incarnate-alpha-shifts.md** - Level shifts
- How level shifts affect calculations
- Effective level for powers
- Enemy level considerations

**30-incarnate-abilities.md** - Incarnate slots
- Judgment (ranged AoE)
- Interface (damage proc)
- Destiny (team buff)
- Lore (pet summon)
- Hybrid (toggle buff)

**31-incarnate-core-radial.md** - Path calculations
- Core vs Radial differences
- Tier progression
- Combining with regular powers

### Special Systems (7 specs)

**32-pet-calculations.md** - Summoned entities
- Pet stat scaling with player level
- Pet enhancement interactions
- Mastermind supremacy

**33-pseudopet-mechanics.md** - Pseudopets
- Powers that summon invisible pseudopets
- Damage/buff delivery via pseudopet
- Why this matters for calculations

**34-proc-chance-formulas.md** - Proc mechanics
- Flat percentage procs
- PPM (Procs Per Minute) formula
- How recharge affects PPM

**35-proc-interactions.md** - Proc edge cases
- AoE factor in PPM calculation
- Multiple targets
- Proc on hit vs proc on cast

**36-enhancement-boosters.md** - Catalysts and boosters
- +5 enhancement mechanics
- Stat bonuses from boosting
- Cost vs benefit

**37-attuned-ios.md** - Attuned enhancements
- Scale with character level
- No exemplar penalty
- Effectiveness curves

**38-purple-pvp-ios.md** - Special IO types
- Purple IOs (very rare sets)
- PvP IOs
- Unique properties

### Edge Cases (5 specs)

**39-power-customization.md** - Cosmetic changes
- Alternate animations
- No redraw
- Effect on gameplay (usually none)

**40-powerset-relationships.md** - Set interactions
- How primary/secondary interact
- Power pool availability
- Epic/Patron pools

**41-level-scaling.md** - Level-based changes
- How powers scale 1-50
- Base stats by level
- Exemplar effects

**42-exemplar-mechanics.md** - Level reduction
- Which powers/slots available when exemplared
- Enhancement effectiveness when exemplared
- Set bonus suppression

**43-special-cases.md** - Everything else
- Unique power mechanics
- Known bugs that are features
- Historical oddities preserved

---

## Execution Plan

### Milestone 1: Foundation (Week 1)

**Goal**: Create navigation and architecture foundation

**Tasks**:
1. Create `docs/midsreborn/` directory structure
2. Write `00-navigation-map.md`:
   - Full directory tree of MidsReborn/Core
   - File sizes and purposes
   - Quick lookup table (e.g., "Damage calculation → PowerEntry.cs, Build.cs")
3. Write `01-architecture-overview.md`:
   - Trace calculation flow from Build.cs
   - Document major subsystems and dependencies
   - Create call graph diagrams
4. Write `02-calculation-index.md`:
   - List all 43 calculation specs
   - Status tracking (Not Started/In Progress/Breadth Complete/Depth Complete)
   - Priority assignments

**Deliverable**: Any developer can navigate MidsReborn codebase within 2 minutes

### Milestone 2: Breadth Coverage (Weeks 2-4)

**Goal**: Create all 43 calculation specs at high level

**For each spec, complete**:
- ✅ Overview section (purpose, dependencies, complexity, priority)
- ✅ Primary location (file, class, method names - no line numbers yet)
- ✅ High-level pseudocode (major steps, not full detail)
- ✅ Game mechanics context (what and why)
- ⏭️ Detailed algorithm (defer to Milestone 3)
- ⏭️ C# code snippets (defer to Milestone 3)
- ⏭️ Full Python implementation guide (defer to Milestone 3)

**Process**:
- Work through specs in numerical order
- Use ripgrep to find relevant C# files
- Read C# code for understanding, don't deep-dive yet
- Update `02-calculation-index.md` as specs progress

**Deliverable**: Complete map of WHAT calculations exist and WHERE they live

### Milestone 3: Depth Detail (Weeks 5-8)

**Goal**: Priority calculations ready for Python implementation

**Priority Order** (based on implementation criticality):

**Phase 1: Core Power System** (Specs 01-09)
- Foundation for everything else
- Must be correct before anything else works

**Phase 2: Enhancement Schedules** (Specs 10-11)
- ED curves are critical for accuracy
- Slotting mechanics needed for any build

**Phase 3: Archetype System** (Specs 16-17)
- AT modifiers and caps differentiate archetypes
- Essential for correct power display

**Phase 4: Build Totals** (Specs 19-24)
- User-facing calculations
- What players see in build planner

**Phase 5: Remaining Specs** (As needed)
- Set bonuses, procs, incarnates
- Special mechanics and edge cases

**For each priority spec, complete**:
- ✅ Full algorithm pseudocode with all branches
- ✅ Actual C# code snippets with line numbers
- ✅ Comprehensive Python implementation guide
- ✅ Test cases with known inputs/outputs
- ✅ Validation strategy

**Deliverable**: Implementation-ready specifications for priority calculations

---

## Quality Standards

### Documentation Requirements

**All Specs Must Have**:
- ✅ Clear purpose statement (one sentence)
- ✅ MidsReborn file paths (relative to repository root)
- ✅ Class and method names
- ✅ Game mechanics explanation (WHY this exists)
- ✅ References to related specs

**Priority Specs Must Also Have**:
- ✅ Line numbers for C# code locations
- ✅ Full algorithm pseudocode (implementation-agnostic)
- ✅ Python architecture guidance
- ✅ Test cases for validation

### Code References

- All paths relative to `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn`
- Include line numbers for priority specs: `Build.cs:247-315`
- Link to Mids Hero Web models when relevant: `backend/app/models.py:Power`

### Pseudocode Standards

- Implementation-agnostic (no C# or Python specifics)
- Include all branches and edge cases
- Comment complex logic
- Use clear variable names

Example:
```
FUNCTION CalculatePowerDamage(power, archetype, enhancement_bonuses):
    base_damage = power.base_damage
    at_scale = archetype.damage_scale

    // Apply archetype modifier
    scaled_damage = base_damage * at_scale

    // Apply enhancements with ED curve
    total_bonus = ApplyEDCurve(enhancement_bonuses, Schedule.A)
    final_damage = scaled_damage * (1 + total_bonus)

    RETURN final_damage
```

### Python Implementation Guidance

- Reference existing Mids Hero Web architecture
- Suggest module/class placement
- Highlight C# vs Python gotchas
- Include validation approach

Example:
```python
# Proposed location: backend/app/calculations/power_damage.py

class PowerDamageCalculator:
    """Calculate power damage with AT scaling and enhancements."""

    def calculate(self, power: Power, archetype: Archetype,
                  enhancements: list[Enhancement]) -> float:
        # Implementation notes:
        # - Power.power_data['base_damage'] is Decimal, convert to float
        # - Archetype.damage_scale is Decimal
        # - Use EDCurve.apply() from enhancement_schedules.py
        pass
```

---

## Success Criteria

### Completion Criteria

✅ **Milestone 1 Complete When**:
- Navigation map covers all Core directory files
- Architecture overview traces Build.cs → all subsystems
- Calculation index lists all 43 specs with status tracking

✅ **Milestone 2 Complete When**:
- All 43 specs exist with Overview, Primary Location, High-level Pseudocode, Game Context
- Every calculation has documented source location
- Index shows "Breadth Complete" for all specs

✅ **Milestone 3 Complete When**:
- Priority specs (01-11, 16-17, 19-24) have full detail
- Each priority spec includes: full algorithm, C# snippets, Python guide, test cases
- Specs are implementation-ready (developer can code without reading C#)

### Validation Criteria

✅ **Navigation Test**:
- Given calculation name, developer finds source file in <2 minutes
- Navigation map has clear lookup paths

✅ **Understanding Test**:
- Developer with no C# knowledge can explain calculation from spec
- Game mechanics context provides "why" not just "how"

✅ **Implementation Test**:
- Priority specs contain enough detail to implement in Python
- Pseudocode translates cleanly to Python
- Test cases provide validation approach

---

## Risks & Mitigations

### Risk: Scope Creep

**Problem**: Discovering more calculations than anticipated
**Mitigation**: Stick to breadth-first approach - document existence before depth
**Indicator**: Calculation index grows beyond 43 specs
**Response**: Add to index but keep at breadth level for Milestone 2

### Risk: C# Code Complexity

**Problem**: Some MidsReborn code is difficult to understand
**Mitigation**: Focus on WHAT not HOW in breadth phase
**Indicator**: Spending >1 hour on single spec in breadth phase
**Response**: Document what's unclear, move on, revisit in depth phase

### Risk: Missing Game Knowledge

**Problem**: Not understanding WHY certain calculations exist
**Mitigation**: Use CoH wiki, forums, game data as references
**Indicator**: Can't explain game mechanic context
**Response**: Research or mark as "needs SME review"

### Risk: Documentation Drift

**Problem**: MidsReborn code changes, docs become outdated
**Mitigation**: Include line numbers and last-verified date
**Indicator**: C# code doesn't match documented behavior
**Response**: Update docs with version/commit reference

---

## Tools & Resources

### Analysis Tools

- **ripgrep (rg)**: Fast code search across MidsReborn codebase
- **C# Language Server** (optional): Code navigation and symbol lookup
- **git blame**: Understand code history and changes
- **VS Code**: Reading C# files with syntax highlighting

### Reference Materials

- **MidsReborn Repository**: `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn`
- **City of Data**: Production data already imported to database
- **CoH Wiki**: https://homecoming.wiki/ (game mechanics explanations)
- **MidsReborn Forums**: Community discussions on calculations
- **Mids Hero Web Models**: `backend/app/models.py` (our existing schema)

### Documentation Workflow

1. **Read C# file** using VS Code or Read tool
2. **Search patterns** with ripgrep (e.g., `rg "damage.*scale" Core/`)
3. **Extract pseudocode** from C# logic
4. **Write spec** following template
5. **Update index** with progress
6. **Commit regularly** to track progress

---

## Next Steps

After this design is approved:

1. **Phase 5: Worktree Setup** (using-git-worktrees skill)
   - Create isolated workspace for documentation work
   - Keep main branch clean during long documentation process

2. **Phase 6: Planning Handoff** (writing-plans skill)
   - Create detailed task breakdown for Milestone 1
   - Estimate effort for each specification
   - Set up tracking for 43-spec completion

3. **Begin Execution**
   - Start with Milestone 1 foundation documents
   - Progress through breadth coverage
   - Deep-dive priority specs

---

## Appendix A: Calculation Priority Matrix

| Priority | Calculation Specs | Rationale |
|----------|------------------|-----------|
| **Critical** | 01-09 (Power System)<br/>10-11 (ED & Slotting)<br/>16-17 (AT Modifiers & Caps)<br/>19-24 (Build Totals) | Foundation for all calculations, user-facing stats |
| **High** | 13 (Set Bonuses)<br/>12 (IO Procs)<br/>25 (Buff Stacking) | Core build planning features |
| **Medium** | 29-31 (Incarnates)<br/>32-35 (Pets & Procs)<br/>18 (Inherents) | Advanced features, specific builds |
| **Low** | 36-43 (Edge Cases) | Nice-to-have, rare scenarios |

---

## Appendix B: Example Spec Workflow

**Goal**: Document "10-enhancement-schedules.md"

1. **Read** `Core/Enhancement.cs` and search for "Schedule"
2. **Find** methods like `ApplyED()`, `GetSchedule()`, curves for A/B/C/D
3. **Extract** formulas for diminishing returns:
   ```csharp
   // Enhancement.cs:145-167
   public static float ApplyED(float bonus, Schedule schedule) {
       // Schedule A: 0.15, 1.0, 1.0
       // Schedule B: 0.15, 0.5, 1.0
       // etc.
   }
   ```
4. **Research** game mechanics - why ED exists (Issue 5 nerf)
5. **Write** pseudocode:
   ```
   FUNCTION ApplyED(total_bonus, schedule):
       IF total_bonus <= threshold1:
           RETURN total_bonus
       ELSE IF total_bonus <= threshold2:
           RETURN threshold1 + (total_bonus - threshold1) * factor1
       // ... more breakpoints
   ```
6. **Document** Python approach:
   ```python
   # backend/app/calculations/enhancement_schedules.py
   class EDCurve(Enum):
       SCHEDULE_A = (0.15, 1.0, 1.0)  # Damage, etc.
       SCHEDULE_B = (0.15, 0.5, 1.0)  # Defense, etc.
   ```
7. **Add test cases**: Known ED values (e.g., 95% bonus → actual 70% after ED)
8. **Update** `02-calculation-index.md` with status

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-10 | Claude | Initial design document created |

