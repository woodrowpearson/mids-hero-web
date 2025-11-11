# Build Totals - Damage

## Overview
- **Purpose**: Aggregate and display global damage buff totals from all sources including set bonuses, global IOs, incarnate powers, and archetype inherents - enforces AT-specific damage caps
- **Used By**: Build totals display, power damage calculations, DPS estimation, build optimization
- **Complexity**: Medium-High
- **Priority**: CRITICAL
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Stats.cs`
- **Class**: `DamageBuff` - Stores base, current, and maximum damage buff values
- **Related Files**:
  - `Core/Base/Data_Classes/Archetype.cs` - `DamageCap` property defines AT-specific damage caps
  - `Core/Base/Data_Classes/Character.cs` - Inherent state flags (Fury, Defiance, Domination)
  - `Core/Base/Data_Classes/Effect.cs` - `eEffectType.DamageBuff` effects
  - `Core/GroupedFx.cs` - Aggregates damage buff effects from multiple sources
  - `clsToonX.cs` - Total damage buff calculation and cap enforcement

### Data Structures

**DamageBuff Class** (`Stats.cs`):
```csharp
public class DamageBuff
{
    public float Base { get; set; }      // Base damage buff (usually 0)
    public float Current { get; set; }   // Current uncapped damage buff
    public float Maximum { get; set; }   // AT-specific damage cap
}
```

**Archetype Damage Cap** (`Archetype.cs`):
```csharp
public float DamageCap { get; set; }  // Default: 4.0 (400%)
```

**Character Inherent Flags** (`Character.cs`):
```csharp
public bool Defiance { get; private set; }        // Blaster damage buff
public bool Domination { get; private set; }      // Dominator damage buff
public bool Assassination { get; private set; }   // Stalker critical
public bool Scourge { get; private set; }         // Corruptor damage bonus
public bool Containment { get; private set; }     // Controller double damage
public bool CriticalHits { get; private set; }    // Scrapper critical
```

## High-Level Algorithm

```
Global Damage Buff Calculation Process:

1. Initialize Damage Buff Totals:
   damage_buff = 0.0
   damage_buff_by_type[ALL_DAMAGE_TYPES] = 0.0

2. Aggregate Set Bonuses:
   For each equipped enhancement set:
     For each bonus in set:
       If bonus.EffectType == DamageBuff:
         If bonus.DamageType == ALL:
           damage_buff += bonus.Magnitude
         Else:
           damage_buff_by_type[bonus.DamageType] += bonus.Magnitude

3. Aggregate Global IOs:
   For each slotted IO enhancement:
     If IO has global damage buff:
       If IO.DamageType == ALL:
         damage_buff += IO.Magnitude
       Else:
         damage_buff_by_type[IO.DamageType] += IO.Magnitude

4. Aggregate Incarnate Powers:
   For each active incarnate power:
     For each effect in power.Effects:
       If effect.EffectType == DamageBuff && effect.ToWho == Self:
         If effect.DamageType == ALL:
           damage_buff += effect.Magnitude
         Else:
           damage_buff_by_type[effect.DamageType] += effect.Magnitude

5. Aggregate Power-Granted Buffs:
   For each active toggle/auto power:
     For each effect in power.Effects:
       If effect.EffectType == DamageBuff && effect.ToWho == Self:
         If effect.DamageType == ALL:
           damage_buff += effect.Magnitude
         Else:
           damage_buff_by_type[effect.DamageType] += effect.Magnitude

6. Apply Archetype Inherents:
   If Character.Defiance == true:
     # Blaster Defiance grants damage buff based on attack chain
     # Simplified: assume average 10% damage buff when active
     damage_buff += 0.10

   If Character.Domination == true:
     # Dominator Domination mode (doubles control magnitude, buffs damage)
     damage_buff += 0.30  # ~30% damage increase when Domination is active

   # Note: Fury (Brute), Scourge (Corruptor), Containment (Controller),
   # Assassination (Stalker), Critical Hits (Scrapper) are handled in
   # per-power damage calculations, not global damage buff

7. Apply Damage Cap:
   damage_cap = MidsContext.Character.Archetype.DamageCap

   # Cap general damage buff
   capped_damage_buff = min(damage_buff, damage_cap - 1.0)

   # Cap typed damage buffs
   For each damage_type in damage_buff_by_type:
     capped_damage_buff_by_type[damage_type] = min(
       damage_buff_by_type[damage_type],
       damage_cap - 1.0
     )

8. Store Results:
   Stats.Display.DamageBuff.Base = 0.0
   Stats.Display.DamageBuff.Current = capped_damage_buff
   Stats.Display.DamageBuff.Maximum = damage_cap - 1.0

9. Display Format:
   Display: "+{capped_damage_buff * 100}% / {damage_cap * 100}%"
   Example: "+95.0% / 400%" (95% damage buff, 400% cap)
   If at cap: Highlight in UI (red or warning color)
```

## Damage Buff Sources

### Set Bonuses

Enhancement sets provide global damage buffs at specific tier levels:

**Common Set Bonus Patterns**:
- **+5% damage (Smashing)** - 2-piece bonus (common in melee sets)
- **+6.25% damage (All)** - 3-piece bonus (rare, high-value sets)
- **+10% damage (Specific Type)** - 5-piece bonus (high-tier sets)

**Set Bonus Application**:
- Set bonuses apply globally to all powers
- Typed damage buffs (e.g., +Fire damage) only apply to powers with that damage type
- "All damage" buffs apply to all damage types
- Set bonuses are always active (not suppressible)

### Global IOs

Special IOs that provide global damage buffs:

**Global Damage IO Examples**:
- **Gaussian's Synchronized Fire-Control**: Build Up proc + recharge (no damage buff)
- **Most Damage IOs are enhancement-only** (not global)
- **Rare exceptions**: Some purple sets have global damage components

**Note**: Most damage IOs only enhance the power they're slotted in, not global damage.

### Incarnate Powers

Incarnate abilities that grant global damage buffs:

**Interface Incarnate**:
- **Degenerative Interface**: No damage buff (DoT + resist debuff)
- **Reactive Interface**: No direct damage buff (Fire DoT)
- **Most Interfaces**: Provide damage via DoT procs, not global buffs

**Hybrid Incarnate**:
- **Assault Radial Embodiment**: +Damage buff to self and team
- **Melee Radial Embodiment**: +Damage buff when near enemies

**Note**: Most global damage buffs from Incarnates come from Hybrid slot.

### Power-Granted Buffs

Some powers grant self damage buffs:

**Build Up / Aim Powers**:
- **Build Up**: +80% damage, +20% ToHit for 10 seconds (NOT global - per-power)
- **Aim**: +62.5% damage, +20% ToHit for 10 seconds (NOT global - per-power)

**Toggle/Auto Powers**:
- **Assault** (Leadership pool): +10.5% damage (global)
- **Domination** (Dominator inherent): +30% damage when active (global)
- **Rage** (Super Strength): +80% damage while active (NOT global - per-power)

**Important**: Only persistent toggle/auto powers with global effects contribute to build totals. Temporary click buffs (Build Up, Aim) are typically NOT included in base build totals.

## Archetype-Specific Inherents

### Damage-Affecting Inherents

**Fury (Brute)**:
- **Type**: Progressive damage buff bar (0-100%)
- **Effect**: +0% to +200% damage based on Fury bar
- **Calculation**: NOT a global damage buff - tracked separately
- **Cap Interaction**: Brute damage cap is 775% to accommodate Fury
- **MidsReborn Handling**: User can set Fury % in build settings

**Defiance (Blaster)**:
- **Type**: Attack chain-based damage buff
- **Effect**: Variable +damage based on recent attacks
- **Calculation**: Simplified average ~10% in MidsReborn
- **Cap Interaction**: Standard 500% cap
- **MidsReborn Handling**: Toggle on/off, applies global damage buff

**Domination (Dominator)**:
- **Type**: Toggle mode (activated by building Domination bar)
- **Effect**: +30% damage, doubles control magnitude
- **Calculation**: Global damage buff when active
- **Cap Interaction**: Standard 400% cap
- **MidsReborn Handling**: Toggle on/off, applies global damage buff

**Scourge (Corruptor)**:
- **Type**: Chance for double damage on low-HP targets
- **Effect**: NOT a damage buff - probability-based damage multiplier
- **Calculation**: Handled in per-power damage calculation
- **Cap Interaction**: Does not count toward damage cap
- **MidsReborn Handling**: Toggle affects per-power damage display

**Containment (Controller)**:
- **Type**: Double damage on controlled targets
- **Effect**: NOT a damage buff - conditional damage multiplier
- **Calculation**: Handled in per-power damage calculation
- **Cap Interaction**: Does not count toward damage cap
- **MidsReborn Handling**: Toggle affects per-power damage display

**Critical Hits (Scrapper/Stalker)**:
- **Type**: Chance for critical damage
- **Effect**: NOT a damage buff - probability-based damage multiplier
- **Calculation**: Handled in per-power damage calculation
- **Cap Interaction**: Does not count toward damage cap
- **MidsReborn Handling**: Toggle affects per-power damage display

**Key Distinction**: Only Defiance and Domination are modeled as global damage buffs. Other inherents (Fury, Scourge, Containment, Crits) are modeled as per-power multipliers or damage bar mechanics.

## Archetype Damage Caps

Damage caps represent the maximum total damage buff (base 100% + buffs) achievable:

| Archetype | Damage Cap | Base + Max Buff | Typical Use Case |
|-----------|------------|-----------------|------------------|
| **Brute** | 775% | 100% + 675% | Fury mechanic requires high cap |
| **Blaster** | 500% | 100% + 400% | Primary damage dealer |
| **Scrapper** | 500% | 100% + 400% | High melee damage |
| **Stalker** | 500% | 100% + 400% | Burst damage + crits |
| **Corruptor** | 500% | 100% + 400% | Ranged damage + buffs |
| **Tanker** | 400% | 100% + 300% | Survivability focus |
| **Defender** | 400% | 100% + 300% | Support focus |
| **Controller** | 400% | 100% + 300% | Control focus |
| **Dominator** | 400% | 100% + 300% | Control + moderate damage |
| **Mastermind** | 400% | 100% + 300% | Pet-focused |
| **Peacebringer** | 400% | 100% + 300% | Balanced hybrid |
| **Warshade** | 400% | 100% + 300% | Balanced hybrid |
| **Sentinel** | 400% | 100% + 300% | Balanced ranged/defense |

**Cap Mechanics**:
- Base damage is always 100% (unslotted, unbuffed)
- Enhancement damage bonuses (e.g., 95% from slotting) DO count toward cap
- Set bonuses, global IOs, inherents count toward cap
- Cap is enforced AFTER all sources are summed
- Display shows: Current buff % / Cap %

## Typed vs. All-Damage Buffs

### Damage Type Categories

**Primary Damage Types**:
- Smashing
- Lethal
- Fire
- Cold
- Energy
- Negative Energy
- Toxic
- Psionic

**Positional Types** (not damage types, used for defense):
- Melee
- Ranged
- AoE

**Special**:
- All Damage (applies to all types)

### Buff Application Rules

```
Damage Buff Application Logic:

1. For each power with damage effects:
   total_buff = 0.0

2. Apply "All Damage" buffs:
   total_buff += global_all_damage_buff

3. Apply typed damage buffs matching power's damage type:
   For each damage_effect in power:
     damage_type = damage_effect.DamageType
     total_buff += global_typed_damage_buff[damage_type]

4. Cap the total:
   capped_buff = min(total_buff, archetype.DamageCap - 1.0)

5. Apply to power damage:
   final_damage = base_damage * (1.0 + capped_buff)
```

**Example**:
- Power: Fire Blast (Fire damage)
- Global buffs: +20% All Damage, +10% Fire Damage, +5% Smashing Damage
- Applied buffs: +20% (All) + +10% (Fire) = +30% total
- Smashing buff does NOT apply (wrong damage type)

## Integration Points

### With Power Damage (Spec 02)

Build totals damage buffs feed into individual power damage calculations:

```
Power Final Damage = Power_Base_Damage
                   * (1 + Power_Enhancement_Damage_Bonus)
                   * (1 + Build_Total_Damage_Buff)
                   * (1 + Temporary_Buffs)  # Build Up, Aim, etc.
                   * Archetype_Damage_Modifier
                   * (capped at Archetype.DamageCap)
```

**Key Points**:
- Build total damage buff is a multiplier applied to enhanced power damage
- Cap is enforced on the TOTAL (enhancements + global buffs + temp buffs)
- See Spec 02 for full power damage calculation

### With Archetype Caps (Spec 17)

Archetype caps define the maximum achievable damage buff:

```
Cap Enforcement:
- Damage cap stored in Archetype.DamageCap
- Default: 4.0 (400% = 100% base + 300% buffs)
- Brutes: 7.75 (775% = 100% base + 675% buffs)
- Blasters/Scrappers/Stalkers/Corruptors: 5.0 (500% = 100% base + 400% buffs)

Cap is enforced BEFORE applying to power damage:
  capped_buff = min(total_damage_buff, archetype.DamageCap - 1.0)
```

**Important**: The cap value includes base damage (100%), so a 400% cap means +300% from buffs.

### With Set Bonuses (Spec 13)

Set bonuses are the primary source of global damage buffs:

```
Set Bonus Damage Buff Aggregation:
1. For each enhancement set equipped:
   If set has N pieces slotted:
     For each tier from 2 to N:
       If bonus[tier].EffectType == DamageBuff:
         Add bonus[tier].Magnitude to appropriate damage buff total

2. Set bonuses stack from different sets
3. Same set in different powers: Rule of 5 (max 5 instances of same bonus)
```

**Example**:
- Slotting 5x "Crushing Impact" (Melee set) in 3 different powers
- 3-piece bonus: +9% Smashing damage (per set)
- Total: +27% Smashing damage from all 3 sets (3 x +9%)
- Rule of 5: Limited to 5 instances max

### With Enhancement Special IOs (Spec 14)

Some IOs provide global damage buffs:

```
Global IO Damage Buff Application:
1. Check if IO has "IgnoreED" flag and global application
2. If IO.EffectType == DamageBuff && IO.Buffable == false:
   # This is a global damage buff IO
   Add IO.Magnitude to damage buff total
3. Most damage IOs only enhance slotted power, not global
```

**Note**: Very few IOs provide global damage buffs. Most damage IOs are power-specific enhancements.

### With Archetype Inherents (Spec 18)

Inherent powers affect damage calculations differently:

**Global Damage Buffs** (included in build totals):
- Defiance (Blaster): ~+10% average damage buff
- Domination (Dominator): +30% damage when active

**Per-Power Multipliers** (NOT in build totals):
- Fury (Brute): Separate damage bar mechanic
- Scourge (Corruptor): Chance for double damage
- Containment (Controller): Double damage on controlled targets
- Critical Hits (Scrapper/Stalker): Chance for critical damage

**See Spec 18** for detailed inherent mechanics.

## UI Display Requirements

### Build Totals Window

**Damage Buff Display**:
```
┌─────────────────────────────────────┐
│ Damage                              │
│   All Damage: +32.5% / 300%        │
│   Smashing:   +18.0% / 300%        │
│   Lethal:     +12.0% / 300%        │
│   Fire:       +25.5% / 300%        │
│   Cold:       +10.0% / 300%        │
│   Energy:     +15.0% / 300%        │
│   Negative:   +8.0%  / 300%        │
│   Toxic:      +5.0%  / 300%        │
│   Psionic:    +0.0%  / 300%        │
│                                     │
│ [AT Cap: 400% (Tanker)]            │
└─────────────────────────────────────┘
```

**Color Coding**:
- **Green**: Buff % < 50% of cap (plenty of room)
- **Yellow**: Buff % between 50-90% of cap (approaching cap)
- **Red**: Buff % >= 90% of cap (at or near cap)

**Tooltip Details**:
- Hover over damage buff to see source breakdown
- Show set bonuses, global IOs, incarnate powers, inherents
- Indicate which buffs count toward cap

### Power Display

When viewing individual power damage, show how global buffs apply:

```
Power: Fire Blast
Base Damage: 62.56 (Fire)
Enhanced: 121.99 (+95% enhancement)
Global Buffs: +57.5% (+32.5% All, +25% Fire)
Final Damage: 192.14
  = 62.56 * 1.95 (enhancements) * 1.575 (global buffs)
```

## Edge Cases and Special Considerations

### 1. Multiple Damage Types in One Power

**Scenario**: Power deals multiple damage types (e.g., 50 Smashing + 50 Fire)

**Handling**:
```
For each damage component:
  Apply "All Damage" buff
  Apply typed buff matching component's damage type

Example:
  Power: 50 Smashing + 50 Fire
  Global Buffs: +20% All, +10% Smashing, +15% Fire

  Smashing Component: 50 * (1 + 0.20 + 0.10) = 65
  Fire Component: 50 * (1 + 0.20 + 0.15) = 67.5
  Total: 132.5 damage
```

### 2. Damage Buff Stacking

**Set Bonus Stacking**:
- Different sets: Stack fully
- Same set in different powers: Rule of 5 applies
- Same bonus type from different sources: All stack

**Example**:
```
3x "Crushing Impact" sets: +9% Smashing each = +27% total
2x "Kinetic Combat" sets: +6.25% Smashing each = +12.5% total
Total Smashing Damage Buff: +39.5%
```

### 3. Temporary Buffs vs. Permanent Buffs

**Build Totals Include**:
- Set bonuses (always active)
- Global IOs (always active)
- Toggle/Auto powers (assumed always on)
- Incarnate powers (assumed always active)
- Archetype inherents (if toggled on in UI)

**Build Totals Exclude**:
- Click buffs (Build Up, Aim) - shown separately per power
- Temporary buffs from inspirations
- Team buffs from other players

### 4. PvP vs. PvE Damage Buffs

**PvP Diminishing Returns**:
- In PvP, damage buffs are subject to diminishing returns
- MidsReborn typically calculates PvE values
- PvP toggle may apply different calculations

**Note**: Most builds and calculations assume PvE context.

### 5. Fury (Brute Special Case)

**Fury Mechanics**:
- Fury is NOT a damage buff in the traditional sense
- Fury is a separate damage bar (0-100%)
- At 100% Fury: ~+200% damage (effectively doubles damage)
- Fury damage IS subject to the 775% damage cap

**MidsReborn Handling**:
```
Fury Slider (0-100%):
  fury_damage_bonus = fury_percentage * 2.0
  # If Fury = 75%, damage bonus = +150%

Total Damage:
  damage_with_fury = base_damage * (1 + fury_bonus + other_buffs)
  capped_damage = min(damage_with_fury, 7.75)  # 775% Brute cap
```

### 6. Damage Cap Reached

**What Happens at Cap**:
- Additional damage buffs have no effect
- Cap is enforced before damage calculation
- UI should warn when at/near cap
- Build optimization: Stop stacking damage, focus on recharge/accuracy

**Indicator**:
```
If current_damage_buff >= (archetype.DamageCap - 1.0):
  Display warning: "Damage cap reached!"
  Suggest: "Consider recharge or accuracy enhancements instead"
```

## Testing and Validation

### Test Cases

**Test 1: Basic Damage Buff Aggregation**
```
Setup:
  - Archetype: Scrapper (500% cap)
  - Set Bonuses: +15% All Damage
  - Global IO: +5% Smashing Damage
  - No inherents active

Expected:
  - All Damage: +15% / 400%
  - Smashing Damage: +20% (+15% All + 5% Smashing) / 400%
  - Other types: +15% / 400%
```

**Test 2: Damage Cap Enforcement**
```
Setup:
  - Archetype: Tanker (400% cap)
  - Set Bonuses: +50% All Damage
  - Global IOs: +30% All Damage
  - Incarnate: +25% All Damage
  - Total uncapped: +105% (exceeds 300% cap for Tanker)

Expected:
  - Displayed: +100% / 300% (capped at 300%)
  - UI shows red warning: "Damage cap reached"
```

**Test 3: Typed Damage Buff Application**
```
Setup:
  - Power: Fire Blast (62.56 Fire damage)
  - Enhancements: +95% damage
  - Global Buffs: +20% All Damage, +15% Fire Damage, +10% Smashing Damage

Expected:
  - Applied buffs: +35% (+20% All + 15% Fire, Smashing ignored)
  - Enhanced damage: 62.56 * 1.95 = 121.99
  - Final damage: 121.99 * 1.35 = 164.69
```

**Test 4: Brute Fury Mechanics**
```
Setup:
  - Archetype: Brute (775% cap)
  - Fury: 75%
  - Set Bonuses: +40% All Damage
  - Enhancements: +95% damage in power

Expected:
  - Fury damage bonus: +150% (75% * 2.0)
  - Total damage buffs: +95% (enhancements) + 150% (Fury) + 40% (sets) = +285%
  - Total damage: 385% (100% base + 285% buffs)
  - Under 775% cap: No capping
```

**Test 5: Domination Active**
```
Setup:
  - Archetype: Dominator (400% cap)
  - Domination: Active (+30% damage)
  - Set Bonuses: +25% All Damage

Expected:
  - Total damage buff: +55% (+30% Domination + 25% sets)
  - Display: +55% / 300%
  - Under cap: OK
```

### Validation Against Live Game

**Comparison Points**:
1. **Set Bonus Totals**: Verify set bonus damage buffs match live game Combat Attributes
2. **Damage Cap**: Verify powers stop gaining damage at AT-specific cap
3. **Typed Buffs**: Verify Fire damage buffs don't apply to Smashing powers
4. **Fury**: Verify Brute Fury slider produces correct damage increases

## Implementation Notes

### Database Schema

**Damage Buff Storage** (build_totals table):
```sql
CREATE TABLE build_damage_totals (
  build_id INTEGER REFERENCES builds(id),
  damage_buff_all REAL,       -- Global "all damage" buff %
  damage_buff_smashing REAL,
  damage_buff_lethal REAL,
  damage_buff_fire REAL,
  damage_buff_cold REAL,
  damage_buff_energy REAL,
  damage_buff_negative REAL,
  damage_buff_toxic REAL,
  damage_buff_psionic REAL,
  damage_cap REAL,             -- AT-specific damage cap
  at_cap BOOLEAN               -- Flag if at/near damage cap
);
```

### Calculation Order

**Critical**: Damage buffs must be calculated AFTER set bonuses and enhancements:

```
1. Load character archetype (get damage cap)
2. Calculate enhancement set bonuses
3. Calculate global IO bonuses
4. Calculate incarnate power bonuses
5. Calculate power-granted toggle/auto buffs
6. Apply archetype inherent modifiers (if active)
7. Sum all damage buffs by type
8. Apply damage cap
9. Store capped values in build totals
10. Use for individual power damage calculations
```

### Performance Considerations

**Caching**:
- Cache damage buff totals (recalculate only when build changes)
- Cache archetype damage cap (rarely changes)
- Invalidate cache on: slot change, power activation/deactivation, set change

## Related Specifications

- **Spec 02 (Power Damage)** - Uses global damage buffs in final damage calculation
- **Spec 03 (Power Buffs/Debuffs)** - Defines DamageBuff effect type
- **Spec 13 (Enhancement Set Bonuses)** - Primary source of global damage buffs
- **Spec 14 (Enhancement Special IOs)** - Global IO damage buffs
- **Spec 17 (Archetype Caps)** - Defines damage cap enforcement rules
- **Spec 18 (Archetype Inherents)** - Inherent-based damage buffs (Defiance, Domination, Fury)

## References

### MidsReborn Files

**Core Calculation**:
- `Core/Stats.cs` - DamageBuff data structure (lines 213-218)
- `Core/Base/Data_Classes/Archetype.cs` - DamageCap property (line 38)
- `Core/Base/Data_Classes/Character.cs` - Inherent state flags (Defiance, Domination, etc.)
- `Core/Base/Data_Classes/Effect.cs` - DamageBuff effect type handling
- `Core/GroupedFx.cs` - Effect aggregation with damage type differentiation

**UI Display**:
- `Forms/WindowMenuItems/frmTotalsV2.cs` - Build totals damage buff display
- `Forms/WindowMenuItems/frmSetViewer.cs` - Set bonus damage visualization

**Damage Types**:
- `Core/Enums.cs` - `eDamage` enum (lines ~1100+): Defines all damage types

### Game Mechanics

**City of Heroes Wiki**:
- Damage - https://homecoming.wiki/wiki/Damage
- Damage Cap - https://homecoming.wiki/wiki/Damage#Damage_Caps
- Enhancement Diversification - https://homecoming.wiki/wiki/Enhancement_Diversification

**Key Mechanics**:
- Damage buffs are multiplicative with base damage and enhancements
- Damage cap includes ALL sources: base (100%) + enhancements + buffs
- Typed damage buffs only apply to matching damage types
- "All damage" buffs apply to all damage types universally

## Summary

Build Totals - Damage aggregates global damage buffs from set bonuses, global IOs, incarnate powers, toggle/auto powers, and archetype inherents. The system tracks both "All Damage" buffs (apply to everything) and typed damage buffs (apply only to matching damage types). Damage cap enforcement varies by archetype (300% to 675% bonus damage) and is applied before final damage calculation. The UI displays current buff percentage vs. cap percentage for each damage type, with warnings when approaching or at cap. Critical integration points include power damage calculation (Spec 02), archetype caps (Spec 17), and archetype inherents (Spec 18).
