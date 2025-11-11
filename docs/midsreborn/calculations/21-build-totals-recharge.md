# Build Totals - Recharge (Global Recharge)

## Overview
- **Purpose**: Aggregate global recharge bonuses from all sources (set bonuses, Hasten, global IOs, Incarnates) to calculate the character's total recharge speed multiplier
- **Used By**: Power recharge calculations, DPS/DPA metrics, Hasten perma-check, build optimization, totals display
- **Complexity**: Medium
- **Priority**: CRITICAL
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `clsToonX.cs`
- **Class**: `clsToonX`
- **Methods**:
  - `GenerateBuffedPowerArray()` - Aggregates all global recharge sources
  - `ApplySetBonuses()` - Applies set bonus effects including recharge

### Supporting Locations
- **File**: `Core/Statistics.cs`
- **Class**: `Statistics`
- **Methods**:
  - `BuffHaste(bool uncapped)` - Returns global recharge percentage (capped or uncapped)

### Dependencies
- **Core/Base/Data_Classes/Character.cs**:
  - `TotalStatistics.BuffHaste` - Global recharge multiplier (stored as factor, e.g., 0.70 for +70%)
  - Aggregates from `_selfEnhance.Effect[Haste]` + `_selfBuffs.Effect[Haste]`
- **Core/Base/Data_Classes/Archetype.cs**:
  - `RechargeCap` - Maximum recharge speed multiplier (typically 5.0 for 400%, some ATs 5.0)
- **Core/Enums.cs**:
  - `eStatType.Haste` - Effect type enum for recharge speed bonuses
- **Core/Enhancement.cs**:
  - Global IOs like Luck of the Gambler +7.5% Recharge

### Algorithm Pseudocode

```
AGGREGATE_GLOBAL_RECHARGE(character):
    # Initialize global recharge accumulator
    globalRechargeBonus = 0.0

    # Step 1: Aggregate from enhancements (global IOs like LotG)
    FOR each power in character.powers:
        FOR each enhancement in power.slots:
            IF enhancement has global recharge effect:
                # Example: Luck of the Gambler +7.5% Recharge
                globalRechargeBonus += enhancement.GlobalRechargeValue

    # Step 2: Add set bonuses
    FOR each setBonus in character.setBonuses:
        FOR each effect in setBonus.effects:
            IF effect.Type == eEffectType.RechargeTime:
                # Set bonuses provide recharge as decimal (e.g., 0.0625 for +6.25%)
                globalRechargeBonus += effect.Magnitude

    # Step 3: Add power-based global recharge (Hasten)
    FOR each power in character.activePowers:
        IF power.IsActive AND power.ProvidesGlobalRecharge:
            # Hasten provides +70% global recharge when active
            globalRechargeBonus += power.GlobalRechargeBonus

    # Step 4: Add other buffs (Incarnate abilities, temporary powers, etc.)
    FOR each buff in character.activeBuffs:
        IF buff.Type == eEffectType.RechargeTime:
            globalRechargeBonus += buff.Magnitude

    # Step 5: Store as multiplicative factor
    # Internal storage: 0.70 represents +70% recharge
    character.Totals.BuffHaste = globalRechargeBonus

    # Step 6: Apply archetype cap
    # Most ATs: RechargeCap = 5.0 (represents 400% or 4x speed boost)
    # Cap is stored as (Cap - 1), so 5.0 - 1 = 4.0 max bonus
    character.TotalsCapped.BuffHaste = Math.Min(
        character.Totals.BuffHaste,
        character.Archetype.RechargeCap - 1
    )

    RETURN character.TotalsCapped.BuffHaste
```

### Display Formula

```
DISPLAY_RECHARGE_PERCENTAGE(buffHaste):
    # BuffHaste is stored as multiplicative factor (0.0 - 4.0)
    # Display as percentage: (1 + buffHaste) × 100
    # Example: 0.70 → (1 + 0.70) × 100 = 170%

    displayPercentage = (buffHaste + 1) × 100

    # At base (no bonuses): 0.0 → 100%
    # With Hasten only: 0.70 → 170%
    # At cap: 4.0 → 500% (most ATs capped at 400%)

    RETURN displayPercentage
```

### Key Logic Snippets

**Global Recharge Aggregation:**
```csharp
// clsToonX.cs - Aggregating global recharge from all sources
Totals.BuffHaste = _selfEnhance.Effect[(int)Enums.eStatType.Haste] +
                   _selfBuffs.Effect[(int)Enums.eStatType.Haste];

// _selfEnhance: Global IOs (LotG +Recharge, etc.)
// _selfBuffs: Set bonuses, Hasten, Incarnate abilities
```

**Applying Archetype Cap:**
```csharp
// clsToonX.cs - Capping global recharge to archetype limit
TotalsCapped.BuffHaste = Math.Min(TotalsCapped.BuffHaste,
                                  Archetype.RechargeCap - 1);

// RechargeCap stored as 5.0 (represents 400% max for most ATs)
// Subtract 1 because BuffHaste is the bonus (not total multiplier)
// Result: BuffHaste capped at 4.0 (represents +400% or 5x speed)
```

**Default Archetype Recharge Cap:**
```csharp
// Core/Base/Data_Classes/Archetype.cs - Default caps
RechargeCap = 5f;  // 5.0 = 400% max recharge (4x speed boost + 1x base)

// Some ATs may have different caps (defined per archetype)
// Cap represents total multiplier: 5.0 = divide recharge by 5
```

**Display Conversion:**
```csharp
// Core/Statistics.cs - Converting to display percentage
public const float MaxHaste = 400f;  // Hard cap for display

public float BuffHaste(bool uncapped)
{
    return !uncapped
        ? Math.Min(MaxHaste, (_character.TotalsCapped.BuffHaste + 1) * 100)
        : (_character.Totals.BuffHaste + 1) * 100;
}

// uncapped = false: Returns capped value for gameplay
// uncapped = true: Returns actual value (may exceed cap for display)
```

**Integration with Power Recharge:**
```csharp
// Core/Base/Data_Classes/Effect.cs - Using global recharge in calculations
var globalRecharge = (MidsContext.Character.DisplayStats.BuffHaste(false) - 100) / 100;
var rechargeVal = Math.Abs(power.RechargeTime) < float.Epsilon
    ? 0
    : power.BaseRechargeTime / (power.BaseRechargeTime / power.RechargeTime - globalRecharge);

// Converts display percentage (170%) back to factor (0.70)
// Then applies to power's actual recharge calculation
```

## Game Mechanics Context

### Why This Calculation Exists

Global recharge is one of the most valuable stats in City of Heroes because:

1. **Universal Benefit**: Affects ALL powers simultaneously (unlike local enhancements)
2. **Multiplicative Stacking**: Combines with local enhancements for massive speed gains
3. **Build-Defining**: Many builds are designed around achieving specific global recharge thresholds

### Common Global Recharge Sources

#### 1. Hasten Power (Speed Pool)
- **Bonus**: +70% global recharge (+0.70 BuffHaste)
- **Duration**: 120 seconds
- **Base Recharge**: 120 seconds
- **Perma-Hasten**: Common build goal requiring ~120% total global recharge to make permanent

#### 2. Set Bonuses
- **Common Values**: +5%, +6.25%, +7.5%, +10%
- **Purple Sets**: Often +10% recharge at 5-6 slotted
- **Example**: 5× Luck of the Gambler sets = 5 × 7.5% = 37.5% global recharge

#### 3. Global IOs
- **Luck of the Gambler +Recharge**: +7.5% global recharge (unique IO)
- **Can slot in**: Any Defense power
- **Limit**: Rule of 5 prevents more than 5 of the same bonus type

#### 4. Incarnate Abilities
- **Agility Core/Radial**: +10% to +20% global recharge (depending on tier)
- **Spiritual Core/Radial**: +5% to +20% global recharge (depending on tier)
- **Stacks with**: All other sources

#### 5. Temporary Powers and Buffs
- **Team Buffs**: Speed Boost (+50% recharge), Chrono Shift, etc.
- **Temporary Powers**: Various event rewards
- **Rare**: Most builds don't rely on these for permanent bonuses

### Recharge Cap Mechanics

**Most Archetypes:**
- **Cap**: 400% recharge speed (5.0 multiplier)
- **Effect**: Power recharges 5× faster (80% reduction)
- **Example**: 60s power → 12s at cap

**Storage vs Display:**
- **Stored**: `BuffHaste = 4.0` (the bonus factor)
- **Displayed**: `(4.0 + 1) × 100 = 500%`
- **Actual Cap**: 400% for most ATs (stored as 5.0, display shows 400% max)

**Archetype Variations:**
- Most ATs: 400% cap (5.0 multiplier)
- Some ATs may have 500% cap (6.0 multiplier) - depends on archetype definition
- Cap includes ALL recharge bonuses (local + global combined)

### Additive Stacking of Global Sources

**All global recharge sources stack additively:**

```
Example Build:
- Hasten: +70%
- 5× LotG +Recharge IOs: 5 × 7.5% = +37.5%
- Set Bonuses: +6.25% + +6.25% + +10% = +22.5%
- Spiritual Alpha (T4): +20%

Total Global Recharge: 70 + 37.5 + 22.5 + 20 = 150%
Stored as: BuffHaste = 1.50
Display: (1.50 + 1) × 100 = 250%
```

**Then combines multiplicatively with local recharge:**

```
Power with 100% local recharge enhancement:
- Local multiplier: 1 + 1.00 = 2.0
- Global multiplier: 1 + 1.50 = 2.5
- Total multiplier: 2.0 × 2.5 = 5.0
- 60s power → 60 / 5.0 = 12s actual recharge
```

### Perma-Hasten Threshold

**Goal**: Make Hasten permanent (recharges before duration expires)

**Calculation:**
```
Hasten Duration: 120s
Hasten Base Recharge: 120s
Hasten Cast Time: ~1.17s (animation)

Required: 120s / (1 + globalRecharge) ≤ 120s - 1.17s
Simplified: globalRecharge ≥ 0.0098 / 0.9902 ≈ 0.01

But accounting for local recharge:
- With 3 Recharge IOs (~95% after ED):
  Local multiplier: 1.95
  Required global: 120 / 1.95 ≤ 118.83
  61.54s ≤ 118.83s (easily met)

Practical perma-Hasten:
- Need ~70% global recharge with good local slotting
- Or ~100-120% global recharge with minimal local slotting
```

### Known Quirks

1. **Hasten Toggle State**:
   - Build planner often shows Hasten as "always active" for calculations
   - Real game: Must track Hasten uptime manually
   - Some builds achieve true perma-Hasten, others have gaps

2. **Rule of 5**:
   - Maximum 5 identical set bonuses count
   - Example: 6× +6.25% recharge set bonuses → only 5 count (+31.25% not +37.5%)
   - LotG +Recharge: Each IO is unique, all 5 count

3. **Global vs Local Confusion**:
   - Players often confuse "recharge reduction" (local) with "recharge speed" (global)
   - Both affect recharge time but calculated differently

4. **Display Anomalies**:
   - Some displays show "200%" (100% bonus) as "2x speed"
   - Others show "200%" as "divide recharge by 2"
   - MidsReborn: Uses percentage format consistently

5. **Incarnate Stacking**:
   - Only one Alpha slot active at a time
   - Spiritual + Agility: Can't have both simultaneously
   - Choose based on build needs

## Python Implementation Guide

### Proposed Architecture

**Location**: `backend/app/game_logic/calculations/build_totals_recharge.py`

**Module Structure**:
```python
# build_totals_recharge.py
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class GlobalRechargeSource:
    """Represents a single source of global recharge."""
    source_type: str  # "set_bonus", "global_io", "hasten", "incarnate", "buff"
    source_name: str
    bonus_value: float  # Stored as decimal (0.075 for +7.5%)
    is_active: bool = True

@dataclass
class GlobalRechargeResult:
    """Result of global recharge aggregation."""
    total_uncapped: float  # Total bonus before cap
    total_capped: float    # Total bonus after archetype cap
    display_percentage: float  # Display value (e.g., 170.0 for +70%)
    sources: List[GlobalRechargeSource]
    is_capped: bool
    archetype_cap: float
    perma_hasten_achieved: bool

class BuildTotalsRechargeCalculator:
    """Aggregates global recharge bonuses from all sources."""

    # Constants
    HASTEN_BONUS = 0.70  # +70% global recharge
    HASTEN_DURATION = 120.0  # seconds
    HASTEN_BASE_RECHARGE = 120.0  # seconds
    DEFAULT_RECHARGE_CAP = 5.0  # Most ATs (represents 400%)

    def __init__(self):
        """Initialize calculator."""
        pass

    def aggregate_global_recharge(
        self,
        set_bonuses: List[float],
        global_ios: List[float],
        hasten_active: bool,
        incarnate_bonuses: List[float],
        other_buffs: List[float],
        archetype_recharge_cap: float = 5.0
    ) -> GlobalRechargeResult:
        """
        Aggregate all global recharge sources.

        Args:
            set_bonuses: List of set bonus values (e.g., [0.0625, 0.075, 0.10])
            global_ios: List of global IO values (e.g., [0.075, 0.075] for 2× LotG)
            hasten_active: Whether Hasten power is active
            incarnate_bonuses: List of Incarnate ability bonuses
            other_buffs: List of other global recharge buffs
            archetype_recharge_cap: AT-specific cap (default 5.0 for 400%)

        Returns:
            GlobalRechargeResult with aggregated values
        """
        pass

    def calculate_display_percentage(self, buff_haste: float) -> float:
        """
        Convert BuffHaste factor to display percentage.

        Args:
            buff_haste: Global recharge factor (e.g., 0.70 for +70%)

        Returns:
            Display percentage (e.g., 170.0)
        """
        return (buff_haste + 1.0) * 100.0

    def check_perma_hasten(
        self,
        global_recharge: float,
        local_recharge: float = 0.95
    ) -> bool:
        """
        Check if build achieves permanent Hasten.

        Args:
            global_recharge: Total global recharge bonus (excluding Hasten)
            local_recharge: Local recharge in Hasten (default ~95% from 3 IOs)

        Returns:
            True if Hasten is permanent
        """
        # Hasten recharge calculation
        local_multiplier = 1.0 + local_recharge
        global_multiplier = 1.0 + global_recharge
        total_multiplier = local_multiplier * global_multiplier

        actual_recharge = self.HASTEN_BASE_RECHARGE / total_multiplier

        # Allow 1-2 second buffer for animation time
        return actual_recharge <= (self.HASTEN_DURATION - 2.0)

    def apply_rule_of_5(self, bonuses: List[float]) -> List[float]:
        """
        Apply Rule of 5: Max 5 identical set bonuses count.

        Args:
            bonuses: List of set bonus values

        Returns:
            List with only first 5 of each unique value counting
        """
        bonus_counts = {}
        result = []

        for bonus in bonuses:
            count = bonus_counts.get(bonus, 0)
            if count < 5:
                result.append(bonus)
                bonus_counts[bonus] = count + 1

        return result
```

### Dependencies on Other Calculations

- **Spec 07** (Power Recharge Modifiers): Uses global recharge in final calculation
- **Spec 10** (Enhancement Schedules): ED doesn't apply to global recharge (only local)
- **Spec 17** (Archetype Caps): Defines recharge cap per archetype
- **Spec 22** (Build Totals - Other): Similar aggregation pattern for damage, tohit, etc.

### Implementation Notes

#### C# vs Python Gotchas

1. **Storage Format**:
   - C# stores BuffHaste as decimal factor (0.70 for +70%)
   - Display converts to percentage: (0.70 + 1) × 100 = 170%
   - Python should maintain same storage for consistency

2. **Additive Stacking**:
   - All global recharge sources add together
   - Then cap is applied to total
   - Don't cap individual sources before summing

3. **Hasten State Management**:
   - Build planner assumes Hasten active (toggle on)
   - Real game has uptime/downtime
   - Provide both "Hasten active" and "Hasten inactive" calculations

#### Edge Cases to Test

1. **No Global Recharge**: Character with zero global bonuses (BuffHaste = 0.0)
2. **Hasten Only**: Just Hasten active (+70%)
3. **Set Bonuses Only**: Multiple set bonuses, no Hasten
4. **Rule of 5**: More than 5 identical set bonuses
5. **Exceeding Cap**: Build with >400% global recharge
6. **Perma-Hasten Edge**: Exactly at perma-Hasten threshold
7. **Incarnate Stacking**: Multiple Incarnate bonuses (only one should count)
8. **Negative Recharge**: Debuffs that reduce global recharge (rare)

#### Performance Considerations

- Global recharge calculated once per build update
- Cache result until build changes (enhancement changes, power toggles)
- Pre-calculate common thresholds (perma-Hasten, softcap, etc.)
- Consider batch processing for build optimizer

#### Validation Strategy

**Test Against MidsReborn**:
1. Create build with known global recharge sources
2. Record displayed global recharge percentage
3. Verify Python calculation matches exactly

**Example Test Case**:
```python
def test_global_recharge_with_hasten_and_sets():
    calc = BuildTotalsRechargeCalculator()

    # Build: Hasten + 5× LotG +Recharge + 3× +6.25% set bonuses
    result = calc.aggregate_global_recharge(
        set_bonuses=[0.0625, 0.0625, 0.0625],  # 3× +6.25%
        global_ios=[0.075, 0.075, 0.075, 0.075, 0.075],  # 5× LotG
        hasten_active=True,
        incarnate_bonuses=[],
        other_buffs=[],
        archetype_recharge_cap=5.0
    )

    # Expected:
    # Set bonuses: 3 × 6.25% = 18.75%
    # LotG IOs: 5 × 7.5% = 37.5%
    # Hasten: 70%
    # Total: 126.25%

    assert abs(result.total_uncapped - 1.2625) < 0.001
    assert abs(result.display_percentage - 226.25) < 0.1
    assert not result.is_capped
    assert result.perma_hasten_achieved
```

### Test Cases

#### Test Case 1: No Global Recharge
```
Input:
- Set Bonuses: []
- Global IOs: []
- Hasten Active: False
- Incarnate Bonuses: []
- Other Buffs: []
- Archetype Cap: 5.0

Expected Output:
- Total Uncapped: 0.0
- Total Capped: 0.0
- Display Percentage: 100.0
- Is Capped: False
- Perma Hasten: False
```

#### Test Case 2: Hasten Only
```
Input:
- Set Bonuses: []
- Global IOs: []
- Hasten Active: True
- Incarnate Bonuses: []
- Other Buffs: []
- Archetype Cap: 5.0

Expected Output:
- Total Uncapped: 0.70
- Total Capped: 0.70
- Display Percentage: 170.0
- Is Capped: False
- Perma Hasten: False (needs more global)
```

#### Test Case 3: Perma-Hasten Build
```
Input:
- Set Bonuses: [0.0625, 0.0625, 0.0625, 0.0625]  # 4× +6.25%
- Global IOs: [0.075, 0.075, 0.075, 0.075, 0.075]  # 5× LotG
- Hasten Active: True
- Incarnate Bonuses: [0.20]  # Spiritual T4
- Other Buffs: []
- Archetype Cap: 5.0

Calculation:
- Set Bonuses: 4 × 6.25% = 25%
- LotG IOs: 5 × 7.5% = 37.5%
- Hasten: 70%
- Incarnate: 20%
- Total: 152.5%

Expected Output:
- Total Uncapped: 1.525
- Total Capped: 1.525
- Display Percentage: 252.5
- Is Capped: False
- Perma Hasten: True
```

#### Test Case 4: Exceeding Cap
```
Input:
- Set Bonuses: [0.10, 0.10, 0.10, 0.10, 0.10]  # 5× +10% (max by Rule of 5)
- Global IOs: [0.075, 0.075, 0.075, 0.075, 0.075]  # 5× LotG
- Hasten Active: True
- Incarnate Bonuses: [0.20]
- Other Buffs: [0.50]  # External buff (e.g., Speed Boost)
- Archetype Cap: 5.0

Calculation:
- Set Bonuses: 5 × 10% = 50%
- LotG IOs: 5 × 7.5% = 37.5%
- Hasten: 70%
- Incarnate: 20%
- Other Buffs: 50%
- Total Uncapped: 227.5%
- Cap: 400% (stored as 4.0)

Expected Output:
- Total Uncapped: 2.275
- Total Capped: 4.0 (capped)
- Display Percentage: 400.0 (display cap)
- Is Capped: True
- Perma Hasten: True
```

#### Test Case 5: Rule of 5 Applied
```
Input:
- Set Bonuses: [0.0625, 0.0625, 0.0625, 0.0625, 0.0625, 0.0625]  # 6× same bonus
- Global IOs: []
- Hasten Active: False
- Incarnate Bonuses: []
- Other Buffs: []
- Archetype Cap: 5.0

Calculation:
- 6 identical bonuses, Rule of 5 applies
- Only first 5 count: 5 × 6.25% = 31.25%

Expected Output:
- Total Uncapped: 0.3125
- Total Capped: 0.3125
- Display Percentage: 131.25
- Is Capped: False
- Perma Hasten: N/A
```

## References

### Related Calculation Specs
- **Spec 07**: Power Recharge Modifiers (uses global recharge in final calculation)
- **Spec 10**: Enhancement Schedules (ED applies to local, not global recharge)
- **Spec 17**: Archetype Caps (defines recharge cap per AT)
- **Spec 22**: Build Totals - Other (similar aggregation for damage, tohit, etc.)

### MidsReborn Code References
- `clsToonX.cs`: Lines 840-865 (Global recharge aggregation and capping)
- `Core/Statistics.cs`: Lines 26, 231-236 (BuffHaste display conversion)
- `Core/Base/Data_Classes/Character.cs`: TotalStatistics.BuffHaste definition
- `Core/Base/Data_Classes/Archetype.cs`: Line 40 (RechargeCap = 5f)

### Forum Posts & Wikis
- Paragon Wiki: [Recharge](https://archive.paragonwiki.com/wiki/Recharge)
- Homecoming Forums: [Global Recharge Guide](https://forums.homecomingservers.com/)
- City of Data: [Recharge Mechanics](https://cod.uberguy.net/)
- Reddit: [Perma-Hasten Build Guide](https://www.reddit.com/r/Cityofheroes/)

### Game Constants
- **Hasten Bonus**: +70% global recharge (+0.70 BuffHaste)
- **Hasten Duration**: 120 seconds
- **Hasten Base Recharge**: 120 seconds
- **Default Recharge Cap**: 5.0 (represents 400% for most ATs)
- **Display Cap**: 400% (MaxHaste constant)
- **LotG +Recharge**: +7.5% global recharge per IO (max 5)
- **Rule of 5**: Maximum 5 identical set bonuses count

---

**Document Status**: 🟡 Breadth Complete - High-level spec with pseudocode and game context
**Last Updated**: 2025-11-10
**Next Steps**: Add full implementation detail in Milestone 3 (depth pass)
