# Enhancement Frankenslotting

## Overview
- **Purpose**: Document the strategy of mixing enhancement pieces from different sets without completing any set for bonuses
- **Used By**: Build optimizers seeking maximum enhancement values, min/max players, pure damage builds
- **Complexity**: Simple (strategy more than algorithm)
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: Not a specific algorithm - this is a player strategy enabled by the slotting system
- **Related Systems**:
  - `Core/Build.cs` - `PowerActiveSpecialSetBonuses()` - Lines tracking which set bonuses are active
  - Enhancement slotting UI allows mixing any compatible enhancements
  - Set bonus calculation only activates when threshold is reached (2, 3, 4, 5, or 6 pieces)

### How It Works in MidsReborn

The planner doesn't have special "frankenslotting" code - it simply allows players to:

1. **Slot any compatible enhancement** in any power
2. **Track set completion** separately from enhancement values
3. **Show both paths**:
   - Total enhancement values from individual pieces
   - Set bonuses IF thresholds are met
4. **Allow comparison** between frankenslotted vs set-bonus approaches

Key code concept from `Build.cs`:
```csharp
// Set bonuses only activate when SlottedCount >= required threshold
if (s.SetInfo[i].SlottedCount >= enhancementSet.Bonus[j].Slotted)
{
    // Apply set bonus
}
```

If you never reach the threshold (e.g., only 1 piece from each set), no set bonuses activate - but you still get the raw enhancement values.

## Game Mechanics Context

### What is Frankenslotting?

**Frankenslotting** (named after Frankenstein's monster - assembled from disparate parts) is the strategy of:

1. **Mixing pieces from multiple sets** in the same power
2. **Deliberately NOT completing any set** (avoiding 2/3/4/5/6 piece thresholds)
3. **Maximizing raw enhancement values** instead of pursuing set bonuses
4. **Cherry-picking the best pieces** from each set for specific attributes

### Example: Damage Attack Slotting

**Traditional Set Slotting** (6 slots):
```
Complete Set: 6x "Crushing Impact" (Level 50)
- Accuracy/Damage
- Damage/Endurance
- Damage/Recharge
- Accuracy/Damage/Recharge
- Accuracy/Damage/Endurance
- Damage/Endurance/Recharge

Enhancement Values: ~95% damage, ~95% accuracy, ~95% recharge, ~95% endurance reduction
Set Bonuses: 7% accuracy, 5% recharge, 2.5% damage, etc.
```

**Frankenslotted Approach** (6 slots):
```
1x Crushing Impact: Damage/Recharge (best dam/rech piece)
1x Mako's Bite: Damage/Recharge (different set, similar values)
1x Kinetic Combat: Damage/Recharge (yet another set)
1x Touch of Death: Damage/Endurance (best dam/end piece)
1x Thunderstrike: Damage/Accuracy (best dam/acc piece)
1x Generic Damage IO (pure damage)

Enhancement Values: ~100%+ damage, ~100%+ recharge, ~100%+ accuracy, ~95% endurance
Set Bonuses: NONE (no set has 2+ pieces)
```

### Why Frankenslot?

**Advantages**:
1. **Higher raw values**: Mixing the best pieces from multiple sets often gives higher enhancement percentages
2. **Target specific attributes**: Can fine-tune exact stats you want (e.g., damage + recharge, skip accuracy)
3. **Cheaper**: Often use common IO sets instead of expensive purple/PvP sets
4. **Flexibility**: No commitment to completing a set - can change pieces easily
5. **ED efficiency**: Can hit ED caps on specific attributes more precisely

**Disadvantages**:
1. **No set bonuses**: Miss out on global bonuses (defense, recharge, HP, etc.)
2. **No Rule of 5 consideration**: Set bonuses can stack up to 5x - frankenslotting gives up this entirely
3. **Build-wide optimization**: Set bonuses often provide build-wide benefits that frankenslotting can't match

### When to Frankenslot

**Good Candidates**:
- **Pure damage powers**: When you just want maximum damage/recharge/accuracy on a single power
- **Attacks you don't care about**: Powers that aren't build-defining
- **Budget builds**: Using common IOs instead of expensive sets
- **Specific attribute targets**: Need exactly 95% recharge, not 85% or 105%
- **Powers with limited slots**: Can't complete a set anyway with only 3-4 slots

**Bad Candidates**:
- **Build-defining powers**: Where you're slotting expensive sets for the bonuses
- **Defense/resistance builds**: Set bonuses are critical for softcapping defense
- **Global recharge builds**: Perma-hasten requires stacking multiple +recharge set bonuses
- **Powers where you have 6 slots**: Usually better to complete a set

### Common Frankenslotting Patterns

**Pattern 1: Damage/Recharge Focus**
```
Goal: Maximum damage + recharge, don't care about accuracy
- 3x Damage/Recharge pieces (from 3 different sets)
- 1x Damage/Endurance piece
- 1x Pure Damage IO
- 1x Pure Recharge IO
```

**Pattern 2: Proc Monster**
```
Goal: Maximum procs, minimal enhancement
- 4-5x Proc IOs (damage procs from different sets)
- 1-2x Accuracy/Damage for basic slotting
```

**Pattern 3: "Good Enough" Slotting**
```
Goal: Hit ED caps cheaply
- Mix common IO pieces to reach ~95% in key attributes
- Don't worry about set bonuses
- Save influence for other powers
```

## Calculations: Frankenslotting vs Set Bonuses

### Enhancement Value Calculation

Frankenslotting doesn't change HOW enhancements calculate - it's just a slotting strategy:

```
For each slot in power:
    For each aspect in enhancement (damage, accuracy, recharge, etc.):
        Add enhancement value to aspect total

Apply ED curve to each aspect total
Apply to power's base values
```

The calculation is the same whether you slot 6 pieces from one set or 6 pieces from 6 different sets.

### Comparison Framework

When evaluating frankenslotting vs set bonuses:

1. **Calculate enhancement values** (both approaches likely similar, frankenslotting often slightly higher)
2. **Calculate set bonuses** (traditional approach only)
3. **Compare power-specific performance** (damage per activation, DPS, endurance efficiency)
4. **Compare build-wide impact** (set bonuses affect entire build, not just one power)

**Example Math**:

Power: Blast attack, 100 base damage, 2.0s recharge, 1.0 accuracy

**Frankenslotted** (105% damage, 100% recharge):
- Damage: 100 × (1 + ED(105%)) = 100 × 1.95 = 195 damage
- Recharge: 2.0s / (1 + ED(100%)) = 2.0s / 1.70 = 1.18s
- DPA: 195 / 1.18 = 165.25 DPA
- Set bonuses: NONE

**Set Bonuses** (95% damage, 95% recharge, +5% global recharge, +2.5% global damage):
- Damage: 100 × (1 + ED(95%) + 0.025) = 100 × 1.925 = 192.5 damage
- Recharge: 2.0s / (1 + ED(95%) + 0.05) = 2.0s / 1.72 = 1.16s
- DPA: 192.5 / 1.16 = 165.95 DPA
- Set bonuses: Apply to ALL powers in build

**Result**: For this ONE power, frankenslotting is slightly better. But set bonuses improve ALL powers, making the traditional approach better for the overall build.

### Strategic Decision Tree

```
START: Should I frankenslot this power?

IF power has 3 or fewer slots:
    → YES - Can't complete set anyway

ELSE IF build needs set bonuses (defense, global recharge, etc.):
    → NO - Set bonuses critical for build function

ELSE IF power is pure damage and you don't care about build-wide stats:
    → MAYBE - Compare enhancement values

ELSE IF you're on a budget:
    → YES - Common IOs are cheaper than rare sets

ELSE IF you're min/maxing one specific power:
    → YES - Frankenslotting can squeeze out a few extra percent

DEFAULT:
    → NO - Set bonuses usually provide more value
```

## Player Strategy Considerations

### Build Philosophy Impact

**Set Bonus Builds** (traditional approach):
- Focus on stacking specific bonuses (defense, recharge, etc.)
- Plan slotting across entire build
- Rule of 5 considerations
- More expensive (rare sets)
- Higher defense/recharge caps

**Frankenslotted Builds** (optimization approach):
- Focus on individual power performance
- Less concerned with build-wide synergy
- More flexible power-by-power
- Cheaper (common IOs)
- Lower defense/recharge caps

### Hybrid Approaches

Most advanced builds use BOTH strategies:

**Typical Pattern**:
```
Important Powers (with 5-6 slots):
- Complete expensive sets (purple, winter, PvP)
- Stack set bonuses for defense, recharge, damage

Less Important Powers (with 3-4 slots):
- Frankenslot with common IOs
- Maximize power performance cheaply
- Don't worry about set bonuses

Utility Powers (with 1-2 slots):
- Single IOs or procs
- Not worth frankenslotting or sets
```

### Mids Reborn Display

The planner shows both approaches equally:

1. **Enhancement values**: Always shown, regardless of set completion
2. **Set bonuses**: Only shown when threshold reached
3. **Totals display**: Shows combined effect of enhancements + set bonuses
4. **Comparison**: Players can easily try both approaches and compare

No special frankenslotting mode needed - just slot pieces from different sets and watch set bonuses disappear while enhancement values remain.

## Python Implementation Guide

### Proposed Architecture

Frankenslotting isn't a separate calculation - it's just a slotting pattern. The Python implementation needs:

**Location**: `backend/app/services/build/`

**No special frankenslotting calculator needed** - just ensure:

1. **Enhancement value calculation** works correctly (spec 11)
2. **Set bonus detection** only activates at thresholds (spec 13)
3. **UI allows mixing sets** without warnings or restrictions
4. **Comparison tools** let players evaluate both approaches

### Implementation Notes

**What NOT to do**:
- Don't create a "frankenslotting calculator" - it's just a strategy
- Don't validate or restrict mixing sets - that's the whole point
- Don't assume frankenslotting is always better or worse

**What TO do**:
- Calculate enhancement values from individual pieces (regardless of set)
- Track set completion separately
- Show both enhancement values AND set bonuses clearly
- Provide comparison tools for players to evaluate trade-offs

### Test Cases

**Test Case 1: Pure Frankenslotting**
```python
power = Blast()
power.add_slot(Enhancement("Crushing Impact", "Damage/Recharge"))
power.add_slot(Enhancement("Mako's Bite", "Damage/Recharge"))
power.add_slot(Enhancement("Kinetic Combat", "Damage/Recharge"))

# Expected:
# - enhancement_values = {damage: ~105%, recharge: ~95%}
# - set_bonuses = [] (no sets have 2+ pieces)
```

**Test Case 2: Set Completion**
```python
power = Blast()
power.add_slot(Enhancement("Crushing Impact", "Acc/Dam"))
power.add_slot(Enhancement("Crushing Impact", "Dam/End"))
power.add_slot(Enhancement("Crushing Impact", "Dam/Rech"))

# Expected:
# - enhancement_values = {damage: ~95%, accuracy: ~32%, recharge: ~32%, endurance: ~66%}
# - set_bonuses = [Crushing Impact 2-piece, Crushing Impact 3-piece]
```

**Test Case 3: Hybrid Approach**
```python
power = Blast()
power.add_slot(Enhancement("Crushing Impact", "Acc/Dam"))
power.add_slot(Enhancement("Crushing Impact", "Dam/End"))
power.add_slot(Enhancement("Mako's Bite", "Dam/Rech"))
power.add_slot(Enhancement("Kinetic Combat", "Dam/Rech"))

# Expected:
# - enhancement_values = {damage: ~100%+, accuracy: ~32%, recharge: ~66%, endurance: ~33%}
# - set_bonuses = [Crushing Impact 2-piece] (only set with 2+ pieces)
```

### Validation Strategy

**Compare frankenslotted vs set-bonused approaches**:

1. Build the same character in both Mids Reborn and Mids Hero Web
2. Slot one power with frankenslotting (6 different sets, 1 piece each)
3. Verify:
   - Enhancement values match between tools
   - Set bonuses show NONE in both tools
   - Power stats (damage, recharge, etc.) match
4. Change to traditional slotting (6 pieces, 1 set)
5. Verify:
   - Enhancement values similar (within ED curve differences)
   - Set bonuses activate in both tools
   - Build totals include set bonuses

## References

### Related Calculation Specs
- **Spec 10**: Enhancement ED Curves (how enhancement values scale)
- **Spec 11**: Enhancement Slotting (how multiple enhancements combine)
- **Spec 13**: Set Bonuses (when sets activate vs when they don't)
- **Spec 25**: Buff Stacking Rules (how set bonuses stack with enhancements)

### Community Resources
- **City of Heroes Forums**: Numerous "frankenslotting vs sets" threads
- **Mids Reborn Forum**: Build optimization discussions
- **Homecoming Wiki**: Enhancement value tables for comparing pieces
- **Reddit /r/Cityofheroes**: Regular frankenslotting advice threads

### Key Design Principles

1. **Frankenslotting is a strategy, not a mechanic** - the game doesn't know or care if you're mixing sets
2. **Trade-off is always the same**: Higher single-power values vs build-wide bonuses
3. **No "correct" answer** - depends on build goals, budget, and play style
4. **Hybrid approaches are common** - most builds use both strategies on different powers
5. **Mids Reborn doesn't judge** - just shows the math for whatever you slot

---

**Document Status**: 🟡 Breadth Complete - Frankenslotting strategy documented
**Implementation Ready**: Yes - no special code needed, just ensure slotting/set bonus calculations work
**Related Documents**: `10-enhancement-schedules.md`, `11-enhancement-slotting.md`, `13-enhancement-set-bonuses.md`
