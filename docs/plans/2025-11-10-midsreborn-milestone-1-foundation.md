# MidsReborn Documentation - Milestone 1: Foundation

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create navigation map and architecture overview to enable fast code lookup and system understanding for the MidsReborn calculation engine reverse engineering project.

**Architecture:** Documentation-only milestone creating three foundation documents: (1) navigation map with full directory tree and quick lookup, (2) architecture overview tracing Build.cs calculation flow, (3) calculation index tracking all 43 specs with status.

**Tech Stack:** Markdown documentation, ripgrep for code search, manual C# code analysis

**Related Design Doc:** `docs/plans/2025-11-10-midsreborn-calculation-reverse-engineering-design.md`

---

## Task 1: Create Directory Structure

**Files:**
- Create: `docs/midsreborn/`
- Create: `docs/midsreborn/calculations/`

**Step 1: Create base directories**

```bash
mkdir -p docs/midsreborn/calculations
```

**Step 2: Verify structure**

Run: `ls -la docs/midsreborn`
Expected: Directory exists with `calculations/` subdirectory

**Step 3: Commit**

```bash
git add docs/midsreborn/
git commit -m "docs: create MidsReborn documentation structure

- docs/midsreborn/ for reverse engineering docs
- docs/midsreborn/calculations/ for 43 calculation specs

Related: Epic 3 Task 3.2 - Build Simulation & Calculation Endpoints"
```

---

## Task 2: Create Navigation Map

**Files:**
- Create: `docs/midsreborn/00-navigation-map.md`

**Step 1: Map MidsReborn directory structure**

Run: `tree -L 2 /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core` (or use `ls -R` if tree not available)

Capture output for directory tree section.

**Step 2: Get file sizes for key files**

Run:
```bash
cd /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core
ls -lh Build.cs clsToonX.cs PowerEntry.cs Enhancement.cs EnhancementSet.cs I9Slot.cs GroupedFx.cs Stats.cs DatabaseAPI.cs
```

**Step 3: Write navigation map document**

Create `docs/midsreborn/00-navigation-map.md` with this structure:

``````markdown
# MidsReborn Repository Navigation Map

**Last Updated:** 2025-11-10
**MidsReborn Path:** `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn`

## Purpose

Quick reference guide for finding calculation code in the MidsReborn C# codebase. Use this to locate specific functionality within 2 minutes.

---

## Directory Structure

```
Core/
├── Build.cs (104 KB) - Master build orchestrator
├── clsToonX.cs (165 KB) - Character/build state management
├── PowerEntry.cs (17 KB) - Individual power calculations
├── Enhancement.cs (16 KB) - Enhancement logic & ED curves
├── EnhancementSet.cs (17 KB) - Set bonus calculations
├── I9Slot.cs (26 KB) - Slotting mechanics
├── GroupedFx.cs (105 KB) - Effect grouping/aggregation
├── Stats.cs (24 KB) - Build stat totals
├── DatabaseAPI.cs (136 KB) - Data access layer
├── Enums.cs (50 KB) - Enumerations and constants
├── Expressions.cs (37 KB) - Expression parsing
├── Modifiers.cs (7 KB) - Stat modifier utilities
├── PowerSet.cs (10 KB) - Powerset container
├── Recipe.cs (8 KB) - Crafting recipes
├── Requirement.cs (9 KB) - Power requirements
└── Base/
    ├── Data_Classes/ - Data structures
    ├── Master_Classes/ - Core utilities
    └── [other subdirectories]
```

## Quick Lookup Table

| Looking For | Primary File(s) | Notes |
|-------------|----------------|-------|
| **Damage calculations** | PowerEntry.cs, Build.cs | Power-level + build aggregation |
| **Enhancement ED curves** | Enhancement.cs | Schedule A/B/C/D |
| **Set bonuses** | EnhancementSet.cs, Build.cs | Individual sets + rule of 5 |
| **Slotting logic** | I9Slot.cs, PowerEntry.cs | How enhancements slot |
| **Archetype modifiers** | Build.cs, DatabaseAPI.cs | AT scaling factors |
| **Build stat totals** | Stats.cs, Build.cs | Defense, resistance, damage, etc. |
| **Effect system** | GroupedFx.cs | Power effects and grouping |
| **Buff stacking** | Build.cs, GroupedFx.cs | How buffs combine |
| **Power requirements** | Requirement.cs | Level, prereqs, etc. |
| **Data loading** | DatabaseAPI.cs | Loading from JSON/MHD |
| **Proc calculations** | Enhancement.cs, PowerEntry.cs | PPM and flat % |
| **Incarnate abilities** | Build.cs, clsToonX.cs | Alpha shifts, slots |
| **Pet stats** | SummonedEntity.cs | Pet calculations |

## Key Entry Points

### 1. Build.cs - Master Orchestrator

**Purpose:** Coordinates all build-level calculations
**Size:** 104 KB
**Key Methods:**
- Build state management
- Stat aggregation
- Set bonus application
- Build validation

**When to start here:** Understanding high-level calculation flow

### 2. clsToonX.cs - Character State

**Purpose:** Manages character/build state and triggers recalculations
**Size:** 165 KB
**Key Methods:**
- Character data storage
- Power selection
- Enhancement slotting
- State change triggers

**When to start here:** Understanding build data structure

### 3. PowerEntry.cs - Power Calculations

**Purpose:** Calculates individual power stats with enhancements
**Size:** 17 KB
**Key Methods:**
- Power effect calculation
- Enhancement application
- Power stat display

**When to start here:** Understanding individual power mechanics

### 4. Enhancement.cs - Enhancement Logic

**Purpose:** Enhancement math including ED curves
**Size:** 16 KB
**Key Methods:**
- ED curve application
- Enhancement value calculation
- Schedule determination

**When to start here:** Understanding enhancement diminishing returns

## Common Calculation Patterns

### Finding Damage Calculation

1. Start: `PowerEntry.cs` - individual power damage
2. Then: `Build.cs` - archetype scaling + global damage buffs
3. Also: `DatabaseAPI.cs` - base power data

### Finding Set Bonus Calculation

1. Start: `EnhancementSet.cs` - individual set bonuses
2. Then: `Build.cs` - rule of 5 suppression + aggregation
3. Also: `I9Slot.cs` - which sets are slotted

### Finding Buff Stacking Logic

1. Start: `GroupedFx.cs` - effect grouping rules
2. Then: `Build.cs` - buff aggregation
3. Also: `Stats.cs` - final stat totals

## File Size Reference

Files ordered by size (largest = most complex):

| File | Size | Complexity |
|------|------|------------|
| clsToonX.cs | 165 KB | Very High |
| DatabaseAPI.cs | 136 KB | High |
| GroupedFx.cs | 105 KB | Very High |
| Build.cs | 104 KB | Very High |
| Enums.cs | 50 KB | Medium |
| Expressions.cs | 37 KB | High |
| I9Slot.cs | 26 KB | Medium |
| Stats.cs | 24 KB | Medium |
| EnhancementSet.cs | 17 KB | Medium |
| PowerEntry.cs | 17 KB | Medium |
| Enhancement.cs | 16 KB | Medium |

---

## Usage Tips

1. **Find by keyword**: Use ripgrep in MidsReborn directory
   ```bash
   rg "damage.*scale" /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core
   ```

2. **Trace dependencies**: Check `using` statements at top of file

3. **Understand flow**: Start with entry point, follow method calls

4. **Check enums**: `Enums.cs` defines constants used throughout

5. **Data structures**: Look in `Base/Data_Classes/` for models

---

## Verification

**Test Navigation Speed:**
- Given: "Where is damage calculated?"
- Lookup: Quick Lookup Table → PowerEntry.cs, Build.cs
- Time: < 30 seconds ✓

- Given: "How does Rule of 5 work?"
- Lookup: Quick Lookup Table → EnhancementSet.cs, Build.cs
- Time: < 30 seconds ✓

---

## Next Steps

After familiarizing with navigation:
1. Read `01-architecture-overview.md` for system-wide calculation flow
2. Use `02-calculation-index.md` to track documentation progress
3. Start with calculation specs in `calculations/` directory
``````

**Step 4: Verify document**

Run: `wc -l docs/midsreborn/00-navigation-map.md`
Expected: ~200+ lines

**Step 5: Commit**

```bash
git add docs/midsreborn/00-navigation-map.md
git commit -m "docs: add MidsReborn navigation map

Complete directory structure with file sizes
Quick lookup table for common calculations
Key entry points and usage patterns

Enables finding any calculation in <2 minutes

Related: Milestone 1 - Foundation"
```

---

## Task 3: Create Architecture Overview

**Files:**
- Create: `docs/midsreborn/01-architecture-overview.md`

**Step 1: Analyze Build.cs structure**

Run: `rg "class Build" -A 50 /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Build.cs | head -100`

Identify key methods and their purposes.

**Step 2: Trace calculation flow**

Search for methods that orchestrate calculations:
```bash
rg "(Calculate|Compute|Update).*Stats?" /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn/Core/Build.cs
```

**Step 3: Write architecture overview**

Create `docs/midsreborn/01-architecture-overview.md`:

``````markdown
# MidsReborn Calculation Architecture Overview

**Last Updated:** 2025-11-10
**Status:** Initial mapping

## Purpose

Understand the high-level calculation flow in MidsReborn, from build creation to stat display. This document traces the path from `Build.cs` through all major subsystems.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        clsToonX.cs                          │
│                   (Character State Manager)                 │
│  - Stores character data (AT, level, powers, slots)        │
│  - Triggers recalculation on any change                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                         Build.cs                            │
│                  (Master Orchestrator)                      │
│  1. Aggregates all power effects                           │
│  2. Applies archetype modifiers                            │
│  3. Calculates set bonuses                                 │
│  4. Computes build totals                                  │
└──────┬────────────┬────────────┬─────────────┬──────────────┘
       │            │            │             │
       ▼            ▼            ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│PowerEntry│  │Enhancement│  │GroupedFx │  │  Stats   │
│   .cs    │  │   .cs     │  │   .cs    │  │   .cs    │
│          │  │           │  │          │  │          │
│Individual│  │ED Curves  │  │  Effect  │  │  Build   │
│  Power   │  │Slotting   │  │ Grouping │  │  Totals  │
│  Calcs   │  │Set Bonus  │  │ Stacking │  │ Display  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
       │            │            │             │
       └────────────┴────────────┴─────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      DatabaseAPI.cs                         │
│                   (Data Access Layer)                       │
│  - Loads power data from JSON                              │
│  - Provides archetype modifiers                            │
│  - Supplies enhancement set definitions                    │
└─────────────────────────────────────────────────────────────┘
```

## Calculation Flow

### Phase 1: Build Initialization

**Entry Point:** `clsToonX.cs` - Character creation or load

1. **Load Archetype**
   - Retrieve AT from DatabaseAPI
   - Set base stats (HP, END, damage scale, etc.)
   - Apply archetype modifiers

2. **Initialize Powers**
   - Create PowerEntry for each selected power
   - Set base power values from database
   - Mark power level and slot counts

### Phase 2: Power Calculation

**Entry Point:** `PowerEntry.cs` - Individual power stats

For each power:

1. **Load Base Effects**
   - Get effects from power data (damage, buff, control, etc.)
   - Apply power level scaling

2. **Apply Enhancements**
   - For each slotted enhancement:
     - Calculate value with ED curve (`Enhancement.cs`)
     - Add to effect totals
   - Check for set bonuses (`EnhancementSet.cs`)

3. **Apply Archetype Modifiers**
   - Scale damage by AT damage scale
   - Scale buffs/debuffs by AT modifiers
   - Apply control duration modifiers

4. **Store Power Stats**
   - Final damage, accuracy, recharge, endurance cost
   - Buff/debuff values
   - Control magnitudes and durations

### Phase 3: Build Aggregation

**Entry Point:** `Build.cs` - Build-wide calculations

1. **Aggregate Power Effects**
   - Collect all buffs from all powers
   - Group by effect type (`GroupedFx.cs`)
   - Apply stacking rules

2. **Calculate Set Bonuses**
   - For each enhancement set:
     - Check how many pieces slotted
     - Activate appropriate bonuses
   - Apply "Rule of 5" suppression
   - Add to global buffs

3. **Compute Build Totals**
   - Defense: Sum all defense buffs by type
   - Resistance: Sum all resistance buffs
   - Damage: Global + type-specific bonuses
   - Recharge: Global recharge reduction
   - Other stats: HP, END, recovery, regen
   - **Apply caps** (defense 45%, resistance 75%, etc.)

4. **Format for Display**
   - Convert to percentages where appropriate
   - Round to display precision
   - Store in Stats.cs for UI

### Phase 4: Incremental Updates

**Trigger:** Any build change (slot enhancement, pick power, etc.)

MidsReborn recalculates affected parts only:
- Slotting change → Recalc that power + set bonuses + build totals
- Pick power → Recalc build totals only
- Change level → Recalc everything

**Optimization:** Minimal recalculation, not full rebuild

---

## Key Subsystems

### Enhancement System

**Files:** Enhancement.cs, EnhancementSet.cs, I9Slot.cs

**Purpose:** Calculate enhancement values with ED, set bonuses

**Key Concepts:**
- **ED Schedules**: A (Damage), B (Defense), C (Misc), D (Ignored)
- **Set Bonuses**: 2/3/4/5/6-piece bonuses
- **Rule of 5**: Max 5 of same set bonus
- **Slotting**: How enhancements fit into powers

**Flow:**
```
Enhancement Value → ED Curve → Modified Value
                                      ↓
                         Apply to Power Effect
                                      ↓
         Check Set Completion → Grant Set Bonuses
```

### Effect System

**Files:** GroupedFx.cs, IEffect.cs

**Purpose:** Group and aggregate power effects

**Key Concepts:**
- **Effect Types**: Damage, Buff, Debuff, Control, Heal, etc.
- **Grouping**: Same effect type from multiple powers
- **Stacking**: How effects combine (add vs multiply)

**Flow:**
```
Power Effects → Group by Type → Apply Stacking Rules → Final Values
```

### Archetype System

**Files:** Build.cs, DatabaseAPI.cs

**Purpose:** Apply AT-specific modifiers

**Key Concepts:**
- **Damage Scale**: Tanker 0.8, Scrapper 1.125, Blaster 1.0, etc.
- **Buff/Debuff Modifiers**: Controllers buff more, Defenders debuff more
- **Caps**: Different by AT (Tanker defense 45%, resistance 90%)

**Flow:**
```
Base Power Value → AT Modifier → Scaled Value
                                      ↓
                          Check AT Cap → Capped Value
```

---

## Data Dependencies

### DatabaseAPI.cs - The Data Source

All calculations depend on data loaded from:
- **Powers JSON**: Base power stats, effects, requirements
- **Archetypes JSON**: AT modifiers, scales, caps
- **Enhancements JSON**: Enhancement sets, bonuses, schedules
- **Other Data**: Salvage, recipes, summons, etc.

**Critical Path:**
```
DatabaseAPI.LoadDatabase()
     ↓
Parse JSON Files
     ↓
Build In-Memory Cache
     ↓
Provide to Calculation System
```

---

## Calculation Triggers

**When calculations happen:**

| Trigger | What Recalculates | Entry Point |
|---------|-------------------|-------------|
| Slot enhancement | Power + Sets + Build | `clsToonX.cs` → `Build.cs` |
| Pick power | Build totals only | `clsToonX.cs` → `Build.cs` |
| Change level | Everything | `clsToonX.cs` → Full rebuild |
| Change AT | Everything | `clsToonX.cs` → Full rebuild |
| Respec | Everything | `clsToonX.cs` → Full rebuild |

---

## Performance Considerations

1. **Incremental Updates**: Only recalc what changed
2. **Caching**: Store computed values until invalidated
3. **Lazy Calculation**: Don't calc until needed for display
4. **Batching**: Group multiple changes before recalc

---

## Python Implementation Implications

When reimplementing in Python:

1. **Separation of Concerns**
   - Keep power calculation separate from build aggregation
   - Use clear interfaces between subsystems

2. **Data Layer**
   - Our PostgreSQL database replaces DatabaseAPI
   - Power.power_data JSONB contains effects
   - Archetype.damage_scale contains modifiers

3. **Calculation Engine**
   - Stateless functions for calculations
   - Clear inputs/outputs
   - Easy to test

4. **Suggested Architecture**
   ```
   backend/app/calculations/
   ├── power_calculator.py      # PowerEntry.cs equivalent
   ├── enhancement_ed.py         # Enhancement.cs ED curves
   ├── set_bonuses.py            # EnhancementSet.cs logic
   ├── build_aggregator.py       # Build.cs orchestration
   ├── effect_stacking.py        # GroupedFx.cs rules
   └── archetype_modifiers.py    # AT scaling
   ```

---

## Next Steps

1. Read individual calculation specs in `calculations/` directory
2. Start with core system specs (01-09) for power effects
3. Reference this document for understanding how parts fit together

---

## Open Questions

**To investigate in detailed specs:**
- How exactly does Rule of 5 work? (EnhancementSet.cs)
- What are the ED curve formulas for each schedule? (Enhancement.cs)
- How do procs calculate PPM? (Enhancement.cs, PowerEntry.cs)
- How does buff stacking work for different effect types? (GroupedFx.cs)
- What are the exact AT modifier values? (DatabaseAPI.cs)
``````

**Step 4: Verify document**

Run: `wc -l docs/midsreborn/01-architecture-overview.md`
Expected: ~300+ lines

**Step 5: Commit**

```bash
git add docs/midsreborn/01-architecture-overview.md
git commit -m "docs: add MidsReborn architecture overview

Top-down calculation flow from Build.cs through subsystems
Key subsystems: Enhancement, Effect, Archetype
Data dependencies and calculation triggers
Python implementation guidance

Traces calculation orchestration path

Related: Milestone 1 - Foundation"
```

---

## Task 4: Create Calculation Index

**Files:**
- Create: `docs/midsreborn/02-calculation-index.md`

**Step 1: Write calculation index with status tracking**

Create `docs/midsreborn/02-calculation-index.md`:

``````markdown
# MidsReborn Calculation Specifications Index

**Last Updated:** 2025-11-10
**Total Specs:** 43
**Status Legend:** ❌ Not Started | 🟡 Breadth Complete | ✅ Depth Complete

## Purpose

Master index tracking all 43 calculation specification documents. Use this to monitor documentation progress and find specific calculation specs.

---

## Status Summary

| Status | Count | Percentage |
|--------|-------|------------|
| ❌ Not Started | 43 | 100% |
| 🟡 Breadth Complete | 0 | 0% |
| ✅ Depth Complete | 0 | 0% |

**Current Phase:** Milestone 1 - Foundation

---

## Power System (Specs 01-09)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 01 | [power-effects-core.md](calculations/01-power-effects-core.md) | ❌ | Critical | High | IEffect interface, GroupedFx |
| 02 | [power-damage.md](calculations/02-power-damage.md) | ❌ | Critical | Medium | Base damage, scaling |
| 03 | [power-buffs-debuffs.md](calculations/03-power-buffs-debuffs.md) | ❌ | Critical | Medium | Buff/debuff mechanics |
| 04 | [power-control-effects.md](calculations/04-power-control-effects.md) | ❌ | High | Medium | Mez mechanics |
| 05 | [power-healing-absorption.md](calculations/05-power-healing-absorption.md) | ❌ | Medium | Low | HP restoration |
| 06 | [power-endurance-recovery.md](calculations/06-power-endurance-recovery.md) | ❌ | Medium | Low | END management |
| 07 | [power-recharge-modifiers.md](calculations/07-power-recharge-modifiers.md) | ❌ | High | Medium | Recharge calculations |
| 08 | [power-accuracy-tohit.md](calculations/08-power-accuracy-tohit.md) | ❌ | High | Medium | Hit chance |
| 09 | [power-defense-resistance.md](calculations/09-power-defense-resistance.md) | ❌ | Critical | Medium | Mitigation |

## Enhancement System (Specs 10-15)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 10 | [enhancement-schedules.md](calculations/10-enhancement-schedules.md) | ❌ | Critical | High | ED curves A/B/C/D |
| 11 | [enhancement-slotting.md](calculations/11-enhancement-slotting.md) | ❌ | Critical | Medium | How slotting works |
| 12 | [enhancement-io-procs.md](calculations/12-enhancement-io-procs.md) | ❌ | High | High | All proc types |
| 13 | [enhancement-set-bonuses.md](calculations/13-enhancement-set-bonuses.md) | ❌ | High | High | Set bonuses, Rule of 5 |
| 14 | [enhancement-special-ios.md](calculations/14-enhancement-special-ios.md) | ❌ | Medium | Medium | Unique IOs |
| 15 | [enhancement-frankenslotting.md](calculations/15-enhancement-frankenslotting.md) | ❌ | Low | Low | Mixed sets |

## Archetype System (Specs 16-18)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 16 | [archetype-modifiers.md](calculations/16-archetype-modifiers.md) | ❌ | Critical | Medium | AT scaling |
| 17 | [archetype-caps.md](calculations/17-archetype-caps.md) | ❌ | Critical | Low | Stat limits by AT |
| 18 | [archetype-inherents.md](calculations/18-archetype-inherents.md) | ❌ | Medium | High | Inherent powers |

## Build Aggregation (Specs 19-24)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 19 | [build-totals-defense.md](calculations/19-build-totals-defense.md) | ❌ | Critical | Medium | Aggregate defense |
| 20 | [build-totals-resistance.md](calculations/20-build-totals-resistance.md) | ❌ | Critical | Medium | Aggregate resistance |
| 21 | [build-totals-recharge.md](calculations/21-build-totals-recharge.md) | ❌ | Critical | Medium | Global recharge |
| 22 | [build-totals-damage.md](calculations/22-build-totals-damage.md) | ❌ | Critical | Medium | Damage bonuses |
| 23 | [build-totals-accuracy.md](calculations/23-build-totals-accuracy.md) | ❌ | High | Low | Accuracy/ToHit |
| 24 | [build-totals-other-stats.md](calculations/24-build-totals-other-stats.md) | ❌ | High | Medium | HP, END, recovery, etc. |

## Stacking & Interaction (Specs 25-28)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 25 | [buff-stacking-rules.md](calculations/25-buff-stacking-rules.md) | ❌ | High | High | How buffs combine |
| 26 | [diminishing-returns.md](calculations/26-diminishing-returns.md) | ❌ | Low | Low | DR beyond ED |
| 27 | [suppression-mechanics.md](calculations/27-suppression-mechanics.md) | ❌ | Low | Low | Power suppression |
| 28 | [combat-attributes.md](calculations/28-combat-attributes.md) | ❌ | Medium | Medium | Real Numbers |

## Incarnate System (Specs 29-31)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 29 | [incarnate-alpha-shifts.md](calculations/29-incarnate-alpha-shifts.md) | ❌ | Medium | Medium | Level shifts |
| 30 | [incarnate-abilities.md](calculations/30-incarnate-abilities.md) | ❌ | Medium | High | Incarnate slots |
| 31 | [incarnate-core-radial.md](calculations/31-incarnate-core-radial.md) | ❌ | Low | Medium | Path calculations |

## Special Systems (Specs 32-38)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 32 | [pet-calculations.md](calculations/32-pet-calculations.md) | ❌ | Medium | High | Summoned entities |
| 33 | [pseudopet-mechanics.md](calculations/33-pseudopet-mechanics.md) | ❌ | Low | Medium | Pseudopets |
| 34 | [proc-chance-formulas.md](calculations/34-proc-chance-formulas.md) | ❌ | High | High | PPM vs flat % |
| 35 | [proc-interactions.md](calculations/35-proc-interactions.md) | ❌ | Medium | High | Proc edge cases |
| 36 | [enhancement-boosters.md](calculations/36-enhancement-boosters.md) | ❌ | Low | Low | +5 mechanics |
| 37 | [attuned-ios.md](calculations/37-attuned-ios.md) | ❌ | Low | Medium | Attuned scaling |
| 38 | [purple-pvp-ios.md](calculations/38-purple-pvp-ios.md) | ❌ | Low | Low | Special IO types |

## Edge Cases (Specs 39-43)

| # | Spec | Status | Priority | Complexity | Notes |
|---|------|--------|----------|------------|-------|
| 39 | [power-customization.md](calculations/39-power-customization.md) | ❌ | Low | Low | Cosmetic changes |
| 40 | [powerset-relationships.md](calculations/40-powerset-relationships.md) | ❌ | Low | Low | Set interactions |
| 41 | [level-scaling.md](calculations/41-level-scaling.md) | ❌ | Medium | Medium | Level-based changes |
| 42 | [exemplar-mechanics.md](calculations/42-exemplar-mechanics.md) | ❌ | Low | Medium | Level reduction |
| 43 | [special-cases.md](calculations/43-special-cases.md) | ❌ | Low | Medium | Unique mechanics |

---

## Priority Groupings

### Phase 1: Core Foundation (Implement First)
**Specs:** 01-09, 10-11, 16-17, 19-24
**Rationale:** Essential for any build calculations

### Phase 2: Advanced Features
**Specs:** 12-13, 18, 25, 28, 34
**Rationale:** Set bonuses, procs, buff stacking

### Phase 3: Special Systems
**Specs:** 29-33, 35
**Rationale:** Incarnates, pets, proc edge cases

### Phase 4: Edge Cases
**Specs:** 14-15, 26-27, 36-43
**Rationale:** Nice-to-have, rare scenarios

---

## Progress Tracking

**Update this table as specs are completed:**

| Milestone | Target | Actual | Completion Date |
|-----------|--------|--------|-----------------|
| Milestone 1: Foundation | 3 docs | 3 docs | 2025-11-10 |
| Milestone 2: Breadth (All 43 specs at high level) | 43 specs 🟡 | 0 specs | TBD |
| Milestone 3: Depth (Priority specs detailed) | 25 specs ✅ | 0 specs | TBD |

---

## How to Update This Index

**When starting a spec:**
1. Change status from ❌ to 🟡 (breadth)
2. Update Status Summary counts
3. Commit change

**When completing breadth:**
1. Verify spec has: Overview, Primary Location, High-level Pseudocode, Game Context
2. Status remains 🟡
3. Update Progress Tracking

**When completing depth:**
1. Change status from 🟡 to ✅
2. Verify spec has: Full algorithm, C# snippets, Python guide, Test cases
3. Update Status Summary and Progress Tracking
4. Commit change

---

## Quick Commands

**Find a spec:**
```bash
grep -i "damage" docs/midsreborn/02-calculation-index.md
```

**Check progress:**
```bash
grep -c "✅" docs/midsreborn/02-calculation-index.md
```

**List not started:**
```bash
grep "❌" docs/midsreborn/02-calculation-index.md
```
``````

**Step 2: Verify document**

Run: `wc -l docs/midsreborn/02-calculation-index.md`
Expected: ~200+ lines

**Step 3: Commit**

```bash
git add docs/midsreborn/02-calculation-index.md
git commit -m "docs: add MidsReborn calculation index

Master index for all 43 calculation specs
Status tracking with breadth/depth completion
Priority groupings for implementation phases
Progress tracking table

Provides central spec navigation and status visibility

Related: Milestone 1 - Foundation"
```

---

## Task 5: Update Progress and Create Milestone Summary

**Files:**
- Modify: `.claude/state/progress.json` (update epic3 with Milestone 1 completion)

**Step 1: Update progress.json**

Add Milestone 1 completion to epic3 section:

```json
"epic3": {
  "name": "Backend API",
  "status": "in_progress",
  "progress": 15,
  "milestones": {
    "midsreborn_docs_m1": {
      "name": "MidsReborn Docs - Milestone 1: Foundation",
      "status": "completed",
      "completion_date": "2025-11-10",
      "deliverables": [
        "00-navigation-map.md - Repository structure guide",
        "01-architecture-overview.md - Calculation flow from Build.cs",
        "02-calculation-index.md - 43 spec tracker"
      ]
    }
  }
}
```

**Step 2: Commit progress update**

```bash
git add .claude/state/progress.json
git commit -m "docs: mark Milestone 1 (Foundation) complete

MidsReborn documentation foundation established:
- Navigation map for fast code lookup
- Architecture overview of calculation flow
- Calculation index tracking 43 specs

Related: Epic 3 Task 3.2 - Build Simulation & Calculation Endpoints"
```

---

## Verification

**Milestone 1 Complete When:**

✅ `docs/midsreborn/` directory structure exists
✅ `00-navigation-map.md` provides <2min code lookup
✅ `01-architecture-overview.md` traces Build.cs → subsystems
✅ `02-calculation-index.md` lists all 43 specs with status
✅ All foundation docs committed to git
✅ Progress tracked in `.claude/state/progress.json`

**Test Navigation:**
- Open `00-navigation-map.md`
- Search for "damage" → Should find PowerEntry.cs, Build.cs quickly
- Search for "set bonus" → Should find EnhancementSet.cs quickly
- Time < 30 seconds per lookup ✓

**Test Understanding:**
- Read `01-architecture-overview.md`
- Should understand: Build.cs orchestrates, PowerEntry calcs individual powers, Enhancement applies ED
- Should see clear data flow diagram

**Test Tracking:**
- Open `02-calculation-index.md`
- Should see 43 specs listed
- Should have status tracking (currently all ❌)
- Should have priority groupings

---

## Next Steps

**After Milestone 1:**

1. **Milestone 2: Breadth Coverage** (Weeks 2-4)
   - Create all 43 calculation specs at high level
   - Each spec: Overview + Location + Pseudocode + Context
   - Work through specs 01-43 in order

2. **Milestone 3: Depth Detail** (Weeks 5-8)
   - Priority specs get full implementation detail
   - Phase 1: Specs 01-11 (Core + ED)
   - Phase 2: Specs 16-17, 19-24 (AT + Build Totals)
   - Remaining as needed

**Handoff:**
- This plan completes Milestone 1 only
- Separate plans needed for Milestones 2 and 3
- Or continue with breadth-first execution now
