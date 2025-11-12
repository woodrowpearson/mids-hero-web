# Milestone 2: Breadth Coverage - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create all 43 calculation specification documents at breadth level (overview, location, high-level pseudocode, game context)

**Architecture:** Top-down documentation approach - survey the entire calculation landscape before diving deep. Each spec documents WHAT exists and WHERE it lives in MidsReborn C# codebase, enabling future Python implementation.

**Tech Stack:** Markdown documentation, ripgrep for code search, MidsReborn C# codebase analysis

**Context:** This builds on Milestone 1 (navigation map, architecture overview, calculation index). We're creating the foundation for all 43 calculation specs that will eventually enable Python reimplementation.

---

## Overview

Milestone 2 creates **breadth-level specifications** for all 43 calculations. Each spec will have:
- ✅ Overview (purpose, dependencies, complexity, priority)
- ✅ Primary location (file, class, method names - no line numbers yet)
- ✅ High-level pseudocode (major steps, not full detail)
- ✅ Game mechanics context (what and why)
- ⏭️ Detailed algorithm (defer to Milestone 3)
- ⏭️ C# code snippets (defer to Milestone 3)
- ⏭️ Full Python implementation guide (defer to Milestone 3)

**Total Deliverable:** 43 specification files in `docs/midsreborn/calculations/`

**Estimated Effort:** 3-4 weeks (1-2 hours per spec average)

---

## Batch Strategy

Work through specs in **logical groups** to maximize knowledge reuse:

**Batch 1:** Power System (Specs 01-09) - 9 specs
**Batch 2:** Enhancement System (Specs 10-15) - 6 specs
**Batch 3:** Archetype System (Specs 16-18) - 3 specs
**Batch 4:** Build Aggregation (Specs 19-24) - 6 specs
**Batch 5:** Stacking & Interaction (Specs 25-28) - 4 specs
**Batch 6:** Incarnate System (Specs 29-31) - 3 specs
**Batch 7:** Special Systems (Specs 32-38) - 7 specs
**Batch 8:** Edge Cases (Specs 39-43) - 5 specs

---

## Batch 1: Power System (Specs 01-09)

### Task 1.1: Create Spec 01 - Power Effects Core

**Files:**
- Create: `docs/midsreborn/calculations/01-power-effects-core.md`
- Reference: MidsReborn `Core/Base/Data_Classes/Effect.cs`, `Core/GroupedFx.cs`
- Update: `docs/midsreborn/02-calculation-index.md` (status to 🟡)

**Step 1: Search MidsReborn for IEffect interface**

```bash
cd /Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn
rg "interface IEffect|class.*Effect" Core/Base/Data_Classes/Effect.cs -A 5
rg "enum.*EffectType" Core/ -A 20
```

Expected: Find IEffect interface definition, effect type enumeration

**Step 2: Search for effect grouping logic**

```bash
rg "class GroupedFx" Core/GroupedFx.cs -A 10
rg "GroupEffects|CombineEffects" Core/GroupedFx.cs
```

Expected: Find GroupedFx class and effect aggregation methods

**Step 3: Create breadth-level spec**

Create `docs/midsreborn/calculations/01-power-effects-core.md` with:

```markdown
# Power Effects Core

## Overview
- **Purpose**: Foundation of all game effect calculations - IEffect interface and effect grouping/aggregation system
- **Used By**: All power calculations, build totals, set bonuses
- **Complexity**: Complex
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Class**: `IEffect` (interface)
- **Related Files**:
  - `Core/GroupedFx.cs` - Effect grouping and aggregation
  - `Core/Enums.cs` - eEffectType enumeration

### Effect Types
- Damage (Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic)
- Defense (by type and position)
- Resistance
- Heal, Regeneration
- Endurance, Recovery
- ToHit, Accuracy
- Recharge
- Control effects (Hold, Stun, Sleep, Immobilize, Confuse, Fear, Placate)
- Movement (Speed, Jump, Fly)
- [50+ total effect types]

### High-Level Algorithm

```
IEffect Interface Structure:
  - EffectType: What kind of effect (damage, defense, etc.)
  - Magnitude: Strength of effect
  - Duration: How long it lasts
  - Probability: Chance to occur (for procs)
  - Aspect: Sub-type (damage type, defense type, etc.)

GroupedFx Aggregation:
  1. Collect all effects from all sources
  2. Group by (EffectType, Aspect) tuple
  3. Apply stacking rules per effect type:
     - Additive: Defense, Resistance (sum all)
     - Multiplicative: Some damage buffs
     - Best-value-only: Some unique effects
  4. Return aggregated effects per type
```

### Dependencies
- Base for all power calculations
- Used by PowerEntry.cs for individual power stats
- Used by Stats.cs for build totals
- Set bonuses add effects to global pool

## Game Mechanics Context

**Why This Exists:**
City of Heroes uses a unified effect system where all game mechanics (damage, buffs, debuffs, control, movement) are represented as IEffect objects. This allows:
- Consistent handling of all power effects
- Easy aggregation from multiple sources (powers, set bonuses, incarnates)
- Flexible stacking rules per effect type

**Historical Context:**
The effect system was fundamental to CoH's design from launch. GroupedFx became critical when set bonuses were introduced (Issue 9), requiring complex effect aggregation with the "Rule of 5" suppression.

**Known Quirks:**
- Some effects stack additively, others multiplicatively - must check per type
- Rule of 5 suppression only applies to certain bonus types
- Pseudopets deliver effects differently than direct power effects

## Python Implementation Notes

**Proposed Architecture:**
```python
# backend/app/calculations/effects.py

class EffectType(Enum):
    DAMAGE = "damage"
    DEFENSE = "defense"
    RESISTANCE = "resistance"
    # ... all 50+ types

class Effect:
    effect_type: EffectType
    magnitude: float
    duration: float
    probability: float
    aspect: str  # "smashing", "melee", etc.

class EffectAggregator:
    def group_effects(effects: list[Effect]) -> dict:
        # Group by (type, aspect)
        # Apply stacking rules
        # Return aggregated values
```

**Implementation Priority:** Critical - implement first before any power calculations

## References
- Related specs: All power specs (02-09), build totals (19-24)
- MidsReborn files: Effect.cs, GroupedFx.cs, Enums.cs
```

**Step 4: Update calculation index**

Edit `docs/midsreborn/02-calculation-index.md`:
- Change spec 01 status from 🔴 to 🟡
- Update progress summary: "Breadth Complete: 1"

**Step 5: Commit**

```bash
git add docs/midsreborn/calculations/01-power-effects-core.md docs/midsreborn/02-calculation-index.md
git commit -m "docs: add breadth spec for power effects core (01/43)"
```

---

### Task 1.2: Create Spec 02 - Power Damage

**Files:**
- Create: `docs/midsreborn/calculations/02-power-damage.md`
- Reference: MidsReborn `Core/PowerEntry.cs`, `Core/Build.cs`
- Update: `docs/midsreborn/02-calculation-index.md`

**Step 1: Search for damage calculation methods**

```bash
rg "damage.*scale|CalculateDamage" Core/PowerEntry.cs Core/Build.cs -i
rg "BaseDamage|DamageScale" Core/Base/Data_Classes/Archetype.cs -i
```

**Step 2: Create spec following template from spec 01**

Focus on:
- Base damage from Power data
- Archetype damage scale multiplication
- Enhancement bonuses (reference spec 10 for ED)
- Damage types (smashing, lethal, fire, cold, energy, negative, toxic, psionic)

**Step 3: Update index and commit**

```bash
git add docs/midsreborn/calculations/02-power-damage.md docs/midsreborn/02-calculation-index.md
git commit -m "docs: add breadth spec for power damage (02/43)"
```

---

### Task 1.3: Create Spec 03 - Power Buffs/Debuffs

**Files:**
- Create: `docs/midsreborn/calculations/03-power-buffs-debuffs.md`
- Reference: MidsReborn `Core/PowerEntry.cs`, `Core/GroupedFx.cs`

**Step 1: Search for buff/debuff mechanics**

```bash
rg "buff|debuff" Core/PowerEntry.cs Core/GroupedFx.cs -i | head -30
rg "Magnitude.*Duration" Core/Base/Data_Classes/Effect.cs
```

**Step 2-3: Create spec and commit**

Similar pattern to specs 01-02.

---

### Task 1.4: Create Spec 04 - Power Control Effects

**Files:**
- Create: `docs/midsreborn/calculations/04-power-control-effects.md`

**Step 1: Search for control/mez mechanics**

```bash
rg "Hold|Stun|Sleep|Immobilize|Confuse|Fear" Core/Base/Data_Classes/Effect.cs
rg "mezz|control.*magnitude" Core/ -i
```

**Step 2-3: Create spec and commit**

---

### Task 1.5: Create Spec 05 - Power Healing/Absorption

**Files:**
- Create: `docs/midsreborn/calculations/05-power-healing-absorption.md`

**Step 1: Search for healing mechanics**

```bash
rg "Heal|Regeneration|Absorption" Core/Base/Data_Classes/Effect.cs
rg "CalculateHeal|HitPoints" Core/PowerEntry.cs
```

**Step 2-3: Create spec and commit**

---

### Task 1.6: Create Spec 06 - Power Endurance/Recovery

**Files:**
- Create: `docs/midsreborn/calculations/06-power-endurance-recovery.md`

**Step 1: Search for endurance mechanics**

```bash
rg "Endurance|EndCost|Recovery" Core/PowerEntry.cs Core/Base/Data_Classes/Power.cs
```

**Step 2-3: Create spec and commit**

---

### Task 1.7: Create Spec 07 - Power Recharge Modifiers

**Files:**
- Create: `docs/midsreborn/calculations/07-power-recharge-modifiers.md`

**Step 1: Search for recharge calculations**

```bash
rg "Recharge|RechargeTime" Core/PowerEntry.cs Core/Enhancement.cs
rg "GlobalRecharge" Core/Stats.cs
```

**Step 2-3: Create spec and commit**

---

### Task 1.8: Create Spec 08 - Power Accuracy/ToHit

**Files:**
- Create: `docs/midsreborn/calculations/08-power-accuracy-tohit.md`

**Step 1: Search for accuracy vs tohit**

```bash
rg "Accuracy|ToHit" Core/PowerEntry.cs Core/Enhancement.cs
```

**Step 2-3: Create spec and commit**

---

### Task 1.9: Create Spec 09 - Power Defense/Resistance

**Files:**
- Create: `docs/midsreborn/calculations/09-power-defense-resistance.md`

**Step 1: Search for defense/resistance**

```bash
rg "Defense|Resistance" Core/PowerEntry.cs Core/Stats.cs
rg "DefenseType|ResistanceType" Core/Enums.cs
```

**Step 2-3: Create spec and commit**

---

### Batch 1 Complete - Checkpoint

After Task 1.9, verify:
- ✅ 9 spec files created in `docs/midsreborn/calculations/`
- ✅ Index shows specs 01-09 as 🟡 Breadth Complete
- ✅ Progress summary: "Breadth Complete: 9 / 43 (21%)"
- ✅ All committed to git

**Pause for review** before proceeding to Batch 2.

---

## Batch 2: Enhancement System (Specs 10-15)

### Task 2.1: Create Spec 10 - Enhancement Schedules (ED Curves)

**Files:**
- Create: `docs/midsreborn/calculations/10-enhancement-schedules.md`
- Reference: MidsReborn `Core/Enhancement.cs` (CRITICAL FILE)

**Step 1: Search for ED implementation**

```bash
rg "ApplyED|Schedule" Core/Enhancement.cs -A 10
rg "SCHEDULE_A|SCHEDULE_B|SCHEDULE_C|SCHEDULE_D" Core/Enhancement.cs
```

Expected: Find ED curve implementation - this is CRITICAL

**Step 2: Create comprehensive spec**

This spec is **Critical priority** - needs extra detail even at breadth level:
- All 4 schedule curves (A, B, C, D)
- Thresholds and diminishing return factors
- Which attributes use which schedule
- Historical context (Issue 5 nerf)

**Step 3: Commit**

```bash
git add docs/midsreborn/calculations/10-enhancement-schedules.md docs/midsreborn/02-calculation-index.md
git commit -m "docs: add breadth spec for ED curves - CRITICAL (10/43)"
```

---

### Task 2.2: Create Spec 11 - Enhancement Slotting

**Files:**
- Create: `docs/midsreborn/calculations/11-enhancement-slotting.md`
- Reference: `Core/I9Slot.cs`, `Core/PowerEntry.cs`

**Step 1: Search for slotting mechanics**

```bash
rg "class I9Slot" Core/I9Slot.cs -A 20
rg "Slots\[|SlotCount" Core/PowerEntry.cs
```

**Step 2-3: Create spec and commit**

---

### Task 2.3: Create Spec 12 - Enhancement IO Procs

**Files:**
- Create: `docs/midsreborn/calculations/12-enhancement-io-procs.md`

**Step 1: Search for proc mechanics**

```bash
rg "proc|PPM|ProcChance" Core/Enhancement.cs Core/PowerEntry.cs -i
```

**Step 2-3: Create spec and commit**

---

### Task 2.4: Create Spec 13 - Enhancement Set Bonuses

**Files:**
- Create: `docs/midsreborn/calculations/13-enhancement-set-bonuses.md`
- Reference: `Core/EnhancementSet.cs`, `Core/Build.cs`

**Step 1: Search for set bonus logic**

```bash
rg "class EnhancementSet" Core/EnhancementSet.cs -A 20
rg "CalculateSetBonuses|Rule.*Five" Core/Build.cs
```

**Step 2-3: Create spec and commit**

---

### Task 2.5: Create Spec 14 - Enhancement Special IOs

**Files:**
- Create: `docs/midsreborn/calculations/14-enhancement-special-ios.md`

**Step 1: Search for unique IOs**

```bash
rg "LuckOfTheGambler|Global.*IO|UniqueIO" Core/Enhancement.cs Core/EnhancementSet.cs -i
```

**Step 2-3: Create spec and commit**

---

### Task 2.6: Create Spec 15 - Enhancement Frankenslotting

**Files:**
- Create: `docs/midsreborn/calculations/15-enhancement-frankenslotting.md`

**Step 1: Document frankenslotting strategy**

This is more strategy than algorithm - focus on:
- What it is (mixing set pieces without completing sets)
- When set bonuses don't apply
- Optimization approaches

**Step 2-3: Create spec and commit**

---

### Batch 2 Complete - Checkpoint

Verify:
- ✅ 6 specs created (10-15)
- ✅ Index shows 15 / 43 (35%) breadth complete
- ✅ All committed

**Pause for review** before Batch 3.

---

## Batch 3: Archetype System (Specs 16-18)

### Task 3.1: Create Spec 16 - Archetype Modifiers

**Files:**
- Create: `docs/midsreborn/calculations/16-archetype-modifiers.md`
- Reference: `Core/Base/Data_Classes/Archetype.cs`

**Step 1: Search for AT modifiers**

```bash
rg "class Archetype" Core/Base/Data_Classes/Archetype.cs -A 30
rg "DamageScale|BuffModifier|DebuffModifier" Core/Base/Data_Classes/Archetype.cs
```

**Step 2-3: Create spec and commit**

---

### Task 3.2: Create Spec 17 - Archetype Caps

**Files:**
- Create: `docs/midsreborn/calculations/17-archetype-caps.md`

**Step 1: Search for caps**

```bash
rg "DefenseCap|ResistanceCap|DamageCap" Core/Base/Data_Classes/Archetype.cs Core/Stats.cs
```

**Step 2-3: Create spec and commit**

---

### Task 3.3: Create Spec 18 - Archetype Inherents

**Files:**
- Create: `docs/midsreborn/calculations/18-archetype-inherents.md`

**Step 1: Search for inherent powers**

```bash
rg "Fury|Defiance|Containment|Critical|Gauntlet|Vigilance|Scourge|Domination|Supremacy" Core/ -i
```

**Step 2-3: Create spec and commit**

---

### Batch 3 Complete - Checkpoint

Verify: 18 / 43 (42%) complete

---

## Batch 4: Build Aggregation (Specs 19-24)

Follow similar pattern for specs 19-24:
- 19: Build Totals - Defense
- 20: Build Totals - Resistance
- 21: Build Totals - Recharge
- 22: Build Totals - Damage
- 23: Build Totals - Accuracy
- 24: Build Totals - Other Stats

All reference `Core/Stats.cs` heavily.

**Checkpoint:** 24 / 43 (56%) complete

---

## Batch 5: Stacking & Interaction (Specs 25-28)

- 25: Buff Stacking Rules
- 26: Diminishing Returns
- 27: Suppression Mechanics
- 28: Combat Attributes

**Checkpoint:** 28 / 43 (65%) complete

---

## Batch 6: Incarnate System (Specs 29-31)

- 29: Incarnate Alpha Shifts
- 30: Incarnate Abilities
- 31: Incarnate Core/Radial

Search pattern: `rg "Incarnate|Alpha|Judgment|Interface|Destiny|Lore|Hybrid" Core/`

**Checkpoint:** 31 / 43 (72%) complete

---

## Batch 7: Special Systems (Specs 32-38)

- 32: Pet Calculations
- 33: Pseudopet Mechanics
- 34: Proc Chance Formulas
- 35: Proc Interactions
- 36: Enhancement Boosters
- 37: Attuned IOs
- 38: Purple/PvP IOs

**Checkpoint:** 38 / 43 (88%) complete

---

## Batch 8: Edge Cases (Specs 39-43)

- 39: Power Customization
- 40: Powerset Relationships
- 41: Level Scaling
- 42: Exemplar Mechanics
- 43: Special Cases

**Final Checkpoint:** 43 / 43 (100%) breadth complete

---

## Milestone 2 Completion Criteria

✅ **All tasks complete when:**
1. All 43 spec files exist in `docs/midsreborn/calculations/`
2. Each spec has: Overview, Primary Location, High-Level Pseudocode, Game Context
3. Index shows 43 / 43 (100%) breadth complete
4. All specs committed to git with descriptive messages

✅ **Quality checks:**
- Each spec is 1-2 pages (breadth level, not depth)
- File paths are accurate
- Pseudocode captures major steps (not full implementation)
- Game context explains WHY calculation exists

---

## Estimated Timeline

**Assumptions:**
- 1-2 hours per spec average
- Work in batches (maximize knowledge reuse)
- Pause for review between batches

**Schedule:**
- Week 1: Batches 1-2 (15 specs) - Power System + Enhancements
- Week 2: Batches 3-4 (12 specs) - Archetypes + Build Totals
- Week 3: Batches 5-6 (7 specs) - Stacking + Incarnates
- Week 4: Batches 7-8 (12 specs) - Special Systems + Edge Cases

**Total: 3-4 weeks for breadth coverage**

---

## Next Steps After Milestone 2

With 100% breadth coverage complete:

1. **Review and prioritize** - Which specs need depth detail first?
2. **Milestone 3: Depth Detail** - Add full implementation detail to Critical/High priority specs
3. **Begin Python implementation** - Start coding with specs as guides

The breadth coverage creates a complete map of the calculation landscape, enabling informed decisions about implementation order and dependencies.

---

## Notes for Executor

**Remember:**
- Use ripgrep (`rg`) liberally - searching is faster than reading
- Focus on WHAT and WHERE, not full HOW (that's Milestone 3)
- Keep specs concise at breadth level (1-2 pages max)
- Update index after each spec
- Commit frequently with descriptive messages
- Pause between batches for review
- Ask questions if MidsReborn code is unclear

**MidsReborn base path:** `/Users/w/code/mids-hero-web/external/dev/MidsReborn/MidsReborn`

**Spec template:** See spec 01 as reference for structure and detail level
