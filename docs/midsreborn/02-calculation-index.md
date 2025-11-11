# MidsReborn Calculation Engine - Calculation Index

**Purpose**: Master list of all 43 calculation specifications with status tracking
**Last Updated**: 2025-11-10
**Prerequisites**: Read `00-navigation-map.md` and `01-architecture-overview.md` first

---

## How to Use This Index

This document tracks all 43 calculation specifications that will document the MidsReborn calculation engine.

**Status Definitions**:
- 🔴 **Not Started**: Specification hasn't been created yet
- 🟡 **Breadth Complete**: High-level spec exists (purpose, location, pseudocode, game context)
- 🟢 **Depth Complete**: Full implementation-ready spec (detailed algorithm, C# snippets, Python guide, test cases)

**Priority Levels**:
- **Critical**: Must be implemented first - foundation for everything else
- **High**: Core build planning features
- **Medium**: Advanced features, specific builds
- **Low**: Edge cases, rare scenarios

---

## Progress Summary

| Status | Count | Percentage |
|--------|-------|------------|
| 🔴 Not Started | 23 | 53% |
| 🟡 Breadth Complete | 20 | 47% |
| 🟢 Depth Complete | 0 | 0% |

**Current Milestone**: Milestone 2 (Breadth Coverage) - Creating all 43 specs

**Next Milestone**: Milestone 2 (Breadth Coverage) - Create all 43 specs at high level

---

## All 43 Calculation Specifications

### Power System (9 specs) - Foundation Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 01 | [power-effects-core.md](calculations/01-power-effects-core.md) | 🟡 Breadth Complete | Critical | Complex | IEffect interface, GroupedFx.cs - Foundation for all calculations |
| 02 | [power-damage.md](calculations/02-power-damage.md) | 🟡 Breadth Complete | Critical | Medium | Damage calculation with AT scaling |
| 03 | [power-buffs-debuffs.md](calculations/03-power-buffs-debuffs.md) | 🟡 Breadth Complete | Critical | Medium | Buff/debuff mechanics and stacking |
| 04 | [power-control-effects.md](calculations/04-power-control-effects.md) | 🟡 Breadth Complete | High | Medium | Mez mechanics (hold, stun, sleep, etc.) |
| 05 | [power-healing-absorption.md](calculations/05-power-healing-absorption.md) | 🟡 Breadth Complete | High | Moderate | HP restoration and temp HP |
| 06 | [power-endurance-recovery.md](calculations/06-power-endurance-recovery.md) | 🟡 Breadth Complete | Critical | Simple | Endurance cost and recovery |
| 07 | [power-recharge-modifiers.md](calculations/07-power-recharge-modifiers.md) | 🟡 Breadth Complete | Critical | Medium | Local and global recharge |
| 08 | [power-accuracy-tohit.md](calculations/08-power-accuracy-tohit.md) | 🟡 Breadth Complete | Critical | Medium | Accuracy vs ToHit distinction |
| 09 | [power-defense-resistance.md](calculations/09-power-defense-resistance.md) | 🟡 Breadth Complete | Critical | Medium | Mitigation mechanics - defense/resistance/DDR |

**Power System Summary**: These 9 specs cover all fundamental power mechanics. Critical for any build calculations. **BATCH 1 COMPLETE - All 9 Power System specs at breadth level!**

---

### Enhancement System (6 specs) - Slotting Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 10 | [enhancement-schedules.md](calculations/10-enhancement-schedules.md) | 🟡 Breadth Complete | Critical | Complex | ED curves (Schedule A/B/C/D) - CRITICAL foundation |
| 11 | [enhancement-slotting.md](calculations/11-enhancement-slotting.md) | 🟡 Breadth Complete | Critical | Medium | How enhancements combine in slots |
| 12 | [enhancement-io-procs.md](calculations/12-enhancement-io-procs.md) | 🟡 Breadth Complete | High | Complex | Damage/heal/endurance procs |
| 13 | [enhancement-set-bonuses.md](calculations/13-enhancement-set-bonuses.md) | 🟡 Breadth Complete | High | Complex | Set activation and Rule of 5 |
| 14 | [enhancement-special-ios.md](calculations/14-enhancement-special-ios.md) | 🟡 Breadth Complete | High | Medium | Global IOs (LotG, Stealth, etc.) |
| 15 | [enhancement-frankenslotting.md](calculations/15-enhancement-frankenslotting.md) | 🟡 Breadth Complete | Medium | Simple | Mixed set slotting strategies |

**Enhancement System Summary**: ED curves (spec 10) are absolutely critical. Set bonuses (spec 13) are core to build planning. **BATCH 2 COMPLETE - All 6 Enhancement System specs at breadth level including CRITICAL ED curves!**

---

### Archetype System (3 specs) - AT Differentiation Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 16 | [archetype-modifiers.md](calculations/16-archetype-modifiers.md) | 🟡 Breadth Complete | **CRITICAL** | Medium | AT scaling for damage/buffs/control - **FOUNDATION MECHANIC** |
| 17 | [archetype-caps.md](calculations/17-archetype-caps.md) | 🟡 Breadth Complete | **CRITICAL** | Simple | Defense/resistance/damage caps by AT - **CRITICAL FOR BUILD DISPLAY** |
| 18 | [archetype-inherents.md](calculations/18-archetype-inherents.md) | 🟡 Breadth Complete | High | Complex | Fury, Defiance, Containment, Scourge, Domination, etc. - **10 primary inherents** |

**Archetype System Summary**: Spec 16 (AT Modifiers) is **CRITICAL** - without it, all ATs show same damage/buff values. Spec 17 (caps) also critical for correct display. Inherents (spec 18) document 10 primary AT-defining mechanics. **BATCH 3 COMPLETE - All 3 Archetype System specs at breadth level!**

---

### Build Aggregation (6 specs) - Totals Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 19 | [build-totals-defense.md](calculations/19-build-totals-defense.md) | 🔴 Not Started | Critical | Medium | Aggregate defense (typed + positional) |
| 20 | [build-totals-resistance.md](calculations/20-build-totals-resistance.md) | 🔴 Not Started | Critical | Medium | Aggregate resistance by type |
| 21 | [build-totals-recharge.md](calculations/21-build-totals-recharge.md) | 🟡 Breadth Complete | **CRITICAL** | Simple | Global recharge aggregation - **Hasten, sets, LotG, Incarnate** |
| 22 | [build-totals-damage.md](calculations/22-build-totals-damage.md) | 🔴 Not Started | Critical | Medium | Global damage bonuses |
| 23 | [build-totals-accuracy.md](calculations/23-build-totals-accuracy.md) | 🟡 Breadth Complete | **CRITICAL** | Simple | Global accuracy (multiplicative) vs tohit (additive) - **CRITICAL distinction** |
| 24 | [build-totals-other-stats.md](calculations/24-build-totals-other-stats.md) | 🔴 Not Started | Critical | Medium | HP, endurance, recovery, regen, etc. |

**Build Aggregation Summary**: All 6 specs are critical - these are what users see in the build planner interface.

---

### Stacking & Interaction (4 specs) - Rules Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 25 | [buff-stacking-rules.md](calculations/25-buff-stacking-rules.md) | 🔴 Not Started | High | Complex | Additive vs multiplicative stacking |
| 26 | [diminishing-returns.md](calculations/26-diminishing-returns.md) | 🔴 Not Started | Medium | Medium | DR beyond ED (if any) |
| 27 | [suppression-mechanics.md](calculations/27-suppression-mechanics.md) | 🔴 Not Started | Low | Medium | Combat suppression, travel power suppression |
| 28 | [combat-attributes.md](calculations/28-combat-attributes.md) | 🔴 Not Started | Medium | Complex | Real Numbers display mimicry |

**Stacking & Interaction Summary**: Buff stacking (spec 25) is high priority. Others can be deferred to later phases.

---

### Incarnate System (3 specs) - Endgame Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 29 | [incarnate-alpha-shifts.md](calculations/29-incarnate-alpha-shifts.md) | 🔴 Not Started | Medium | Medium | Level shifts and scaling |
| 30 | [incarnate-abilities.md](calculations/30-incarnate-abilities.md) | 🔴 Not Started | Medium | Complex | Judgment, Interface, Destiny, Lore, Hybrid |
| 31 | [incarnate-core-radial.md](calculations/31-incarnate-core-radial.md) | 🔴 Not Started | Low | Medium | Core vs Radial path differences |

**Incarnate System Summary**: Important for endgame builds but can be implemented after core system works.

---

### Special Systems (7 specs) - Advanced Features Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 32 | [pet-calculations.md](calculations/32-pet-calculations.md) | 🔴 Not Started | Medium | Complex | Summoned entities (Masterminds, etc.) |
| 33 | [pseudopet-mechanics.md](calculations/33-pseudopet-mechanics.md) | �4 Not Started | Medium | Complex | Invisible pseudopets for power delivery |
| 34 | [proc-chance-formulas.md](calculations/34-proc-chance-formulas.md) | 🔴 Not Started | High | Complex | Flat % vs PPM formulas |
| 35 | [proc-interactions.md](calculations/35-proc-interactions.md) | 🔴 Not Started | High | Complex | AoE factor, multi-target, etc. |
| 36 | [enhancement-boosters.md](calculations/36-enhancement-boosters.md) | 🔴 Not Started | Low | Simple | +5 catalyst mechanics |
| 37 | [attuned-ios.md](calculations/37-attuned-ios.md) | 🔴 Not Started | Medium | Medium | Level-scaling enhancements |
| 38 | [purple-pvp-ios.md](calculations/38-purple-pvp-ios.md) | 🔴 Not Started | Low | Simple | Special IO types |

**Special Systems Summary**: Proc formulas (specs 34-35) are high priority for build optimization. Pet calculations needed for Masterminds.

---

### Edge Cases (5 specs) - Special Mechanics Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 39 | [power-customization.md](calculations/39-power-customization.md) | 🔴 Not Started | Low | Simple | Cosmetic changes (usually no calc impact) |
| 40 | [powerset-relationships.md](calculations/40-powerset-relationships.md) | 🔴 Not Started | Low | Simple | Primary/secondary/pool interactions |
| 41 | [level-scaling.md](calculations/41-level-scaling.md) | 🔴 Not Started | Medium | Medium | Power scaling 1-50 |
| 42 | [exemplar-mechanics.md](calculations/42-exemplar-mechanics.md) | 🔴 Not Started | Medium | Complex | Level reduction effects |
| 43 | [special-cases.md](calculations/43-special-cases.md) | 🔴 Not Started | Low | Varies | Unique mechanics, bugs-as-features |

**Edge Cases Summary**: Mostly low priority except level scaling (spec 41) and exemplar mechanics (spec 42) for level-agnostic builds.

---

## Implementation Priority Order

Based on dependencies and user value, implement in this order:

### Phase 1: Core Foundation (Critical - Week 1-2)
```
Specs 01-09: Power System
Specs 10-11: ED Curves & Slotting
Specs 16-17: Archetype Modifiers & Caps
```
**Why**: Foundation for all calculations. Nothing works without these.

### Phase 2: Build Totals (Critical - Week 3)
```
Specs 19-24: Build Aggregation
```
**Why**: User-facing stats. What players see in build planner.

### Phase 3: Set Bonuses & Procs (High - Week 4-5)
```
Spec 13: Set Bonuses
Specs 12, 34-35: Proc Mechanics
Spec 25: Buff Stacking Rules
```
**Why**: Core build planning features. Set bonuses are huge part of builds.

### Phase 4: Advanced Features (Medium - Week 6-7)
```
Spec 18: Archetype Inherents
Specs 29-31: Incarnate System
Specs 32-33: Pet Calculations
Specs 37, 41-42: Attuned IOs, Level Scaling, Exemplar
```
**Why**: Important for specific builds and endgame content.

### Phase 5: Edge Cases (Low - Week 8+)
```
Specs 14-15: Special IOs, Frankenslotting
Specs 26-28: DR, Suppression, Combat Attributes
Specs 36, 38-40, 43: Boosters, Special IOs, Customization, Special Cases
```
**Why**: Nice-to-have features. Polish and completeness.

---

## Specification Template

When creating a new spec, use this template (from the main plan document):

```markdown
# [Calculation Name]

## Overview
- **Purpose**: What this calculation does in game terms
- **Used By**: Which systems depend on this
- **Complexity**: Simple/Medium/Complex
- **Priority**: Critical/High/Medium/Low
- **Status**: Not Started / Breadth Complete / Depth Complete

## MidsReborn Implementation

### Primary Location
- **File**: Core/[FileName.cs]
- **Class**: ClassName
- **Methods**:
  - MethodName() - Lines XXX-YYY
  - OtherMethod() - Lines ZZZ-AAA

### Dependencies
- Related classes and their roles
- Data structures used
- External data sources

### Algorithm Pseudocode
[Step-by-step logic extracted from C#]

### Key Logic Snippets
[Actual C# code excerpts with line numbers]

## Game Mechanics Context
- Why this calculation exists
- Historical context
- Known quirks

## Python Implementation Guide

### Proposed Architecture
- Where in Mids Hero Web this should live
- Suggested Python module/class structure
- Dependencies on other calculations

### Implementation Notes
- C# vs Python gotchas
- Edge cases to test
- Performance considerations
- Validation strategy

### Test Cases
- Known inputs and expected outputs
- Edge cases
- Comparison data from MidsReborn

## References
- Related calculation specs
- Forum posts/wikis
- MidsReborn GitHub issues
```

---

## Milestone Tracking

### Milestone 1: Foundation (Week 1) ✅ IN PROGRESS

**Goal**: Create navigation and architecture foundation

**Tasks**:
- ✅ Create docs/midsreborn/ directory structure
- ✅ Write 00-navigation-map.md
- ✅ Write 01-architecture-overview.md
- ✅ Write 02-calculation-index.md (this document)

**Status**: **Complete when this document is finalized**

---

### Milestone 2: Breadth Coverage (Weeks 2-4) 🔴 NOT STARTED

**Goal**: Create all 43 calculation specs at high level

**Target**: All specs show 🟡 Breadth Complete status

**Process**:
1. Work through specs in numerical order
2. For each spec, complete:
   - ✅ Overview section
   - ✅ Primary location (file, class, method names)
   - ✅ High-level pseudocode
   - ✅ Game mechanics context
   - ⏭️ Defer detailed algorithm to Milestone 3
   - ⏭️ Defer C# snippets to Milestone 3
   - ⏭️ Defer full Python guide to Milestone 3
3. Update this index as specs progress

**Completion Criteria**:
- All 43 spec files exist
- Each has Overview, Primary Location, High-level Pseudocode, Game Context
- Index shows 100% breadth coverage

---

### Milestone 3: Depth Detail (Weeks 5-8) 🔴 NOT STARTED

**Goal**: Priority calculations ready for Python implementation

**Target**: Specs 01-11, 16-17, 19-24 show 🟢 Depth Complete status

**Process**:
1. Focus on Critical priority specs first
2. For each spec, add:
   - ✅ Full algorithm pseudocode with all branches
   - ✅ Actual C# code snippets with line numbers
   - ✅ Comprehensive Python implementation guide
   - ✅ Test cases with known inputs/outputs
   - ✅ Validation strategy
3. Update status in index

**Completion Criteria**:
- 27 priority specs have full implementation detail
- Specs are implementation-ready (developer can code without reading C#)
- Test cases provide validation approach

---

## How to Update This Index

When working on a specification:

1. **Starting a spec** (breadth level):
   - Change status from 🔴 to 🟡
   - Update progress summary counts
   - Create the spec file in `calculations/` directory

2. **Completing breadth coverage**:
   - Ensure spec has: Overview, Primary Location, High-level Pseudocode, Game Context
   - Verify status is 🟡 Breadth Complete

3. **Adding depth detail**:
   - Change status from 🟡 to 🟢 when full detail added
   - Ensure spec has: Full algorithm, C# snippets, Python guide, test cases
   - Update progress summary counts

4. **Regular updates**:
   - Update this index at end of each work session
   - Keep progress summary accurate
   - Note any blockers or issues in spec-specific Notes column

---

## Quick Reference: Spec Locations

All 43 specification files will be created in:
```
docs/midsreborn/calculations/
├── 01-power-effects-core.md
├── 02-power-damage.md
├── 03-power-buffs-debuffs.md
... [all 43 specs]
└── 43-special-cases.md
```

---

## Questions & Clarifications

**Q: Do all 43 specs need full depth detail?**
A: No. Only Critical and High priority specs (27 total) need full depth in Milestone 3. Medium/Low priority specs stay at breadth level until needed.

**Q: Can I implement before all specs are complete?**
A: Yes, but complete breadth coverage (Milestone 2) first to understand dependencies. Then implement as depth specs are completed.

**Q: What if I discover more calculations?**
A: Add them to this index with status "Not Started". Don't let scope creep delay breadth coverage.

**Q: How do I validate calculations are correct?**
A: Each depth spec includes test cases comparing Python output to MidsReborn output for same inputs.

---

## Maintenance Notes

**When to Update This Document**:
- After completing any specification (update status and progress)
- When discovering new calculations (add to appropriate category)
- When priorities change based on implementation needs
- Weekly progress review

**Current Version**: Milestone 1 - Foundation complete
**Last Status Update**: 2025-11-10

---

**Document Status**: ✅ Complete - Calculation index established with tracking system
**Related Documents**: `00-navigation-map.md`, `01-architecture-overview.md`, `calculations/*.md`
