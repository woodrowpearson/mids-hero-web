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
| 🔴 Not Started | 0 | 0% |
| 🟡 Breadth Complete | 19 | 44.2% |
| 🟢 Depth Complete | 24 | 55.8% |

**Current Milestone**: 🚧 Milestone 3 (Depth Coverage) - **24/27 high-priority specs complete (88.9%)**!
**Latest**: Phase 3 complete - Enhancement & Endgame (Specs 11, 13, 23-25, 29, 32, 34)

**Progress**: All 8 Critical specs + 16 High Priority specs enhanced to depth level with ~40,193 lines of production-ready implementation details!

---

## All 43 Calculation Specifications

### Power System (9 specs) - Foundation Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 01 | [power-effects-core.md](calculations/01-power-effects-core.md) | 🟢 **Depth Complete** | Critical | Complex | IEffect interface, GroupedFx.cs - Foundation for all calculations |
| 02 | [power-damage.md](calculations/02-power-damage.md) | 🟢 **Depth Complete** | High | Medium | Damage calculation with AT scaling (~1,790 lines) |
| 03 | [power-buffs-debuffs.md](calculations/03-power-buffs-debuffs.md) | 🟢 **Depth Complete** | High | Medium | Buff/debuff mechanics and stacking (~1,800 lines) |
| 04 | [power-control-effects.md](calculations/04-power-control-effects.md) | 🟢 **Depth Complete** | High | Medium | Mez mechanics (hold, stun, sleep, etc.) (~1,410 lines) |
| 05 | [power-healing-absorption.md](calculations/05-power-healing-absorption.md) | 🟢 **Depth Complete** | High | Moderate | HP restoration and temp HP (~1,913 lines) |
| 06 | [power-endurance-recovery.md](calculations/06-power-endurance-recovery.md) | 🟢 **Depth Complete** | High | Simple | Endurance cost and recovery (~1,760 lines) |
| 07 | [power-recharge-modifiers.md](calculations/07-power-recharge-modifiers.md) | 🟢 **Depth Complete** | High | Medium | Local and global recharge (~2,800 lines) |
| 08 | [power-accuracy-tohit.md](calculations/08-power-accuracy-tohit.md) | 🟢 **Depth Complete** | High | Medium | Accuracy vs ToHit distinction (~1,750 lines) |
| 09 | [power-defense-resistance.md](calculations/09-power-defense-resistance.md) | 🟢 **Depth Complete** | High | Medium | Mitigation mechanics - defense/resistance/DDR (~2,023 lines) |

**Power System Summary**: ✅ **ALL 9 SPECS DEPTH COMPLETE!** All fundamental power mechanics documented with production-ready implementation details.

---

### Enhancement System (6 specs) - Slotting Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 10 | [enhancement-schedules.md](calculations/10-enhancement-schedules.md) | 🟢 **Depth Complete** | Critical | Complex | ED curves (Schedule A/B/C/D) - CRITICAL foundation (~1,276 lines) |
| 11 | [enhancement-slotting.md](calculations/11-enhancement-slotting.md) | 🟢 **Depth Complete** | High | Medium | How enhancements combine in slots (~1,400 lines) |
| 12 | [enhancement-io-procs.md](calculations/12-enhancement-io-procs.md) | 🟡 Breadth Complete | High | Complex | Damage/heal/endurance procs |
| 13 | [enhancement-set-bonuses.md](calculations/13-enhancement-set-bonuses.md) | 🟢 **Depth Complete** | High | Complex | Set activation and Rule of 5 (~1,936 lines) |
| 14 | [enhancement-special-ios.md](calculations/14-enhancement-special-ios.md) | 🟡 Breadth Complete | High | Medium | Global IOs (LotG, Stealth, etc.) |
| 15 | [enhancement-frankenslotting.md](calculations/15-enhancement-frankenslotting.md) | 🟡 Breadth Complete | Medium | Simple | Mixed set slotting strategies |

**Enhancement System Summary**: ✅ **3/6 SPECS DEPTH COMPLETE!** ED curves, slotting mechanics, and set bonuses documented with production-ready detail.

---

### Archetype System (3 specs) - AT Differentiation Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 16 | [archetype-modifiers.md](calculations/16-archetype-modifiers.md) | 🟢 **Depth Complete** | **CRITICAL** | Medium | AT scaling for damage/buffs/control (~1,850 lines) |
| 17 | [archetype-caps.md](calculations/17-archetype-caps.md) | 🟢 **Depth Complete** | **CRITICAL** | Simple | Defense/resistance/damage caps by AT (~1,942 lines) |
| 18 | [archetype-inherents.md](calculations/18-archetype-inherents.md) | 🟡 Breadth Complete | High | Complex | Fury, Defiance, Containment, Scourge, Domination, etc. - **10 primary inherents** |

**Archetype System Summary**: ✅ **2/3 CRITICAL SPECS DEPTH COMPLETE!** AT modifiers and caps fully documented with exact values for all archetypes.

---

### Build Aggregation (6 specs) - Totals Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 19 | [build-totals-defense.md](calculations/19-build-totals-defense.md) | 🟢 **Depth Complete** | **CRITICAL** | Medium | Aggregate defense (typed + positional) (~2,468 lines) |
| 20 | [build-totals-resistance.md](calculations/20-build-totals-resistance.md) | 🟢 **Depth Complete** | **CRITICAL** | Medium | Aggregate resistance by type (~1,660 lines) |
| 21 | [build-totals-recharge.md](calculations/21-build-totals-recharge.md) | 🟢 **Depth Complete** | **CRITICAL** | Simple | Global recharge aggregation (~322 lines) |
| 22 | [build-totals-damage.md](calculations/22-build-totals-damage.md) | 🟢 **Depth Complete** | **CRITICAL** | Medium | Global damage bonuses (~964 lines) |
| 23 | [build-totals-accuracy.md](calculations/23-build-totals-accuracy.md) | 🟢 **Depth Complete** | High | Simple | Global accuracy/tohit aggregation (~1,276 lines) |
| 24 | [build-totals-other-stats.md](calculations/24-build-totals-other-stats.md) | 🟢 **Depth Complete** | High | Medium | HP, endurance, recovery, regen, movement, perception (~950 lines) |

**Build Aggregation Summary**: ✅ **ALL 6 SPECS DEPTH COMPLETE!** All user-facing build stats documented with production-ready implementation details.

---

### Stacking & Interaction (4 specs) - Rules Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 25 | [buff-stacking-rules.md](calculations/25-buff-stacking-rules.md) | 🟢 **Depth Complete** | High | Complex | Additive/multiplicative/best-value stacking + Rule of 5 (~1,714 lines) |
| 26 | [diminishing-returns.md](calculations/26-diminishing-returns.md) | 🟡 Breadth Complete | Medium | Medium | DDR, Elusivity (PvP), Proc caps, Status resistance - BEYOND ED |
| 27 | [suppression-mechanics.md](calculations/27-suppression-mechanics.md) | 🟡 Breadth Complete | Low | Moderate | eSuppress flags - combat/stealth/travel suppression |
| 28 | [combat-attributes.md](calculations/28-combat-attributes.md) | 🟡 Breadth Complete | Medium | Medium | Real-time stat display - "Real Numbers" window replication |

**Stacking & Interaction Summary**: ✅ **1/4 HIGH-PRIORITY SPEC DEPTH COMPLETE!** Buff stacking rules documented with exact stacking modes and Rule of 5 implementation.

---

### Incarnate System (3 specs) - Endgame Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 29 | [incarnate-alpha-shifts.md](calculations/29-incarnate-alpha-shifts.md) | 🟢 **Depth Complete** | High | Medium | 8 Alpha types, level shift +1/+2/+3, ED applies (~1,474 lines) |
| 30 | [incarnate-abilities.md](calculations/30-incarnate-abilities.md) | 🟡 Breadth Complete | Medium | Complex | 9 non-alpha slots: Interface, Judgment, Destiny, Lore, Hybrid, Genesis, Vitae, Omega, Stance |
| 31 | [incarnate-core-radial.md](calculations/31-incarnate-core-radial.md) | 🟡 Breadth Complete | Low | Medium | Core (focused) vs Radial (broad) branching at T3+ |

**Incarnate System Summary**: ✅ **1/3 HIGH-PRIORITY SPEC DEPTH COMPLETE!** Alpha slot documented with exact boost values, level shift formulas, and purple patch scaling.

---

### Special Systems (7 specs) - Advanced Features Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 32 | [pet-calculations.md](calculations/32-pet-calculations.md) | 🟢 **Depth Complete** | High | Complex | Summoned entities with inheritance + slotting (~2,040 lines) |
| 33 | [pseudopet-mechanics.md](calculations/33-pseudopet-mechanics.md) | 🟡 Breadth Complete | Medium | Complex | Invisible pseudopets for power delivery |
| 34 | [proc-chance-formulas.md](calculations/34-proc-chance-formulas.md) | 🟢 **Depth Complete** | High | Complex | PPM formula with recharge/cast/area factors (~2,085 lines) |
| 35 | [proc-interactions.md](calculations/35-proc-interactions.md) | 🟡 Breadth Complete | Low | Low-Moderate | Independent rolling, unique restrictions, mutex system |
| 36 | [enhancement-boosters.md](calculations/36-enhancement-boosters.md) | 🟡 Breadth Complete | Low | Simple | +5 catalyst mechanics |
| 37 | [attuned-ios.md](calculations/37-attuned-ios.md) | 🟡 Breadth Complete | Medium | Medium | Level-scaling enhancements - NO exemplar penalty |
| 38 | [purple-pvp-ios.md](calculations/38-purple-pvp-ios.md) | 🟡 Breadth Complete | Medium | Medium | Purple (rare) and PvP IO sets - Rule of 5 exempt |

**Special Systems Summary**: ✅ **2/7 HIGH-PRIORITY SPECS DEPTH COMPLETE!** Pet calculations and proc chance formulas documented with exact PPM formulas and pet inheritance rules.

---

### Edge Cases (5 specs) - Special Mechanics Layer

| # | Specification | Status | Priority | Complexity | Notes |
|---|---------------|--------|----------|------------|-------|
| 39 | [power-customization.md](calculations/39-power-customization.md) | 🟡 Breadth Complete | Low | Simple | VFX (no calc impact), power replacements (patron pools), alternate animations |
| 40 | [powerset-relationships.md](calculations/40-powerset-relationships.md) | 🟡 Breadth Complete | Low | Medium | Cross-powerset synergies, combo systems, mode toggles (Bio Armor, Staff Fighting, Dual Pistols) |
| 41 | [level-scaling.md](calculations/41-level-scaling.md) | 🟡 Breadth Complete | Medium | Medium | Modifier table level lookup (55×60), Purple Patch formulas, Incarnate level shifts |
| 42 | [exemplar-mechanics.md](calculations/42-exemplar-mechanics.md) | 🟡 Breadth Complete | Low | Medium | Exemplar down/sidekick up level adjustments - power/enhancement/set bonus availability |
| 43 | [special-cases.md](calculations/43-special-cases.md) | 🟡 Breadth Complete | Low | Medium | Unique mechanics, bugs-as-features, name fixes, Arcana Time, pool prerequisites |

**Edge Cases Summary**: **BATCH 8 COMPLETE!** - All 5 Edge Cases specs complete! Spec 41 (Level Scaling) documents modifier table system (55 levels × 60 archetypes), Purple Patch mechanics (ToHit/damage/debuff scaling by level difference), and Incarnate level shift integration (+1 to +3). Spec 42 (Exemplar Mechanics) documents ExempHigh/ExempLow/ForceLevel system, power availability checks, enhancement penalties (with exemptions for attuned/purple/PvP IOs), and set bonus rules. Spec 43 (Special Cases) documents 65+ special case flags (eSpecialCase enum), import string fixes, Arcana Time (132ms server tick quantization), pool prerequisites, and one-off mechanics. Specs 39-40 document VFX customization, power replacements, and powerset relationships. **ALL 43 SPECS NOW COMPLETE AT BREADTH LEVEL!**

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
