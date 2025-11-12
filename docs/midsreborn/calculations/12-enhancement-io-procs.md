# Enhancement IO Procs

## Overview
- **Purpose**: Calculate proc chances and effects for IO enhancements with special effects that trigger probabilistically
- **Used By**: Enhancement slotting, power effect calculations, build planning
- **Complexity**: Moderate to Complex
- **Priority**: High
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Effect.cs`
- **Properties**: `ProcsPerMinute`, `BaseProbability`, `ActualProbability`, `MinProcChance`, `MaxProcChance`
- **Related Files**:
  - `Core/Enhancement.cs` - `IsProc` flag, `EffectChance` property
  - `Core/PowerEntry.cs` - `HasProc()`, `ProcInclude` for proc toggling
  - `Core/IEffect.cs` - `MinProcChance` interface property

### Proc Types

**Flat Percentage Procs**:
- Legacy proc system (pre-PPM)
- Fixed probability (e.g., 20%, 33.3%)
- Stored in `BaseProbability` field
- Simple chance check per activation

**PPM (Procs Per Minute) System**:
- Modern proc system introduced in Issue 24
- Probability varies based on:
  - Power recharge time
  - Power cast time
  - Power area effect radius
  - Global recharge buffs
- Designed to normalize proc performance across power types
- Prevents abuse with fast-recharging powers

**Common Proc Types**:
- **Damage Procs**: Additional damage on activation (e.g., Hecatomb: Chance for Negative Damage)
- **Heal Procs**: Chance for heal (e.g., Numina's Convalescence: +Regen/+Recovery)
- **Endurance Procs**: Chance for endurance discount or recovery
- **Status/Mez Procs**: Chance for Hold, Stun, etc.
- **Buff/Debuff Procs**: Chance for temporary buff or enemy debuff

### High-Level Algorithm

```
PPM Calculation Process (ActualProbability getter in Effect.cs):

1. Check if ProcsPerMinute > 0:
   - If no, use BaseProbability (flat percentage)
   - If yes, proceed with PPM calculation

2. Calculate Area Factor:
   areaFactor = power.AoEModifier * 0.75 + 0.25

   - Single target powers: AoEModifier = 1.0 → areaFactor = 1.0
   - AoE powers: AoEModifier > 1.0 → areaFactor > 1.0
   - Reduces proc chance for powers that hit multiple targets

3. Calculate Effective Recharge:
   globalRecharge = (BuffHaste - 100) / 100

   For Click Powers:
     rechargeVal = BaseRechargeTime / (BaseRechargeTime/ActualRecharge - globalRecharge)

   For Auto/Toggle Powers:
     Use fixed 10-second check interval

4. Calculate Base Probability:
   For Click Powers:
     probability = PPM * (rechargeVal + castTime) / (60 * areaFactor)

   For Auto/Toggle Powers:
     probability = PPM * 10 / (60 * areaFactor)

5. Apply Min/Max Caps:
   MinProcChance = PPM * 0.015 + 0.05  (e.g., 3.5 PPM → 10.25% min)
   MaxProcChance = 0.9 (90% cap)

   probability = clamp(probability, MinProcChance, MaxProcChance)

6. Apply Character Modifiers:
   If character has ModifyEffects for this EffectId:
     probability += ModifyEffects[EffectId]

7. Final Clamp:
   return clamp(probability, 0, 1)
```

### PPM Formula Details

**For Click Powers**:
```
Proc Chance = (PPM × (RechargeTime + CastTime)) / (60 × AreaFactor)
```

**For Auto/Toggle Powers**:
```
Proc Chance = (PPM × 10) / (60 × AreaFactor)
```

Where:
- `PPM` = Procs Per Minute value from effect data
- `RechargeTime` = Actual power recharge (after all recharge buffs)
- `CastTime` = Power activation/cast time
- `AreaFactor` = 0.75 × AoEModifier + 0.25 (penalizes AoE powers)

**Recharge Calculation with Global Buffs**:
```
globalRecharge = (CharacterHaste% - 100) / 100
effectiveRecharge = BaseRecharge / (BaseRecharge/SlottedRecharge - globalRecharge)
```

This ensures global recharge buffs (like Hasten) don't unfairly increase proc chances beyond slotted recharge.

### Dependencies
- `Power.RechargeTime` - Base and actual recharge values
- `Power.CastTimeReal` - Power cast/activation time
- `Power.AoEModifier` - Area effect multiplier
- `Power.PowerType` - Click vs Auto/Toggle distinction
- `MidsContext.Character.DisplayStats.BuffHaste()` - Global recharge buffs
- `Enhancement.IsProc` - Flag marking enhancement as proc IO
- `PowerEntry.ProcInclude` - User toggle for including proc in calculations

## Game Mechanics Context

**Why Procs Exist:**
Invention Origin (IO) enhancements introduced in Issue 9 included special "proc" effects - bonus effects that have a chance to trigger when a power activates. This added strategic depth to slotting decisions beyond simple enhancement values.

**Historical Evolution:**
- **Issue 9-23**: Flat percentage procs (20%, 33.3%)
  - Problem: Extremely powerful in fast-recharging powers
  - Example: 33% proc in 1-second recharge power = 20 procs/minute
  - Same proc in 30-second power = 1.1 procs/minute

- **Issue 24+**: PPM (Procs Per Minute) system
  - Normalized proc performance across power types
  - Fast powers get lower % chance, slow powers get higher %
  - Result: Similar proc frequency regardless of power recharge

**PPM Design Goals:**
1. **Fairness**: All powers achieve similar procs/minute with same PPM value
2. **Anti-Abuse**: Prevent exploitation with fast-recharging powers
3. **AoE Balance**: Reduce proc chance for powers hitting multiple targets
4. **Predictability**: Players can calculate expected proc frequency

**Common PPM Values:**
- 1.0 PPM: Minor procs (weak damage, small buffs)
- 3.5 PPM: Standard damage procs (most purple sets)
- 4.5 PPM: Enhanced damage procs
- 6.0 PPM: Premium procs (very rare)

**Strategic Considerations:**
- **Proc vs Enhancement**: Proc IOs don't enhance power attributes
  - Damage proc adds flat damage roll but doesn't boost base damage
  - Must decide: proc for extra effect vs enhancement for bigger base effect

- **Power Selection for Procs**:
  - Long recharge powers: Higher proc % per activation
  - AoE powers: Lower proc % but hits multiple targets
  - Auto/toggle powers: Check every 10 seconds (10-second rule)

- **Proc Slotting Strategies**:
  - "Proc Bombs": Slot multiple procs in long-recharge AoE
  - "Proc Chains": Use procs to supplement damage in control powers
  - "Purple Procs": 3.5 PPM procs from purple sets (very valuable)

**Known Quirks:**
- **10-Second Rule**: Auto/toggle powers check procs every 10 seconds
  - Makes PPM calculation use fixed 10-second interval
  - Can make procs attractive in toggle debuff powers

- **Global Recharge Impact**:
  - More global recharge = slightly lower proc chance
  - Prevents Hasten from multiplicatively boosting proc frequency

- **AoE Modifier Edge Cases**:
  - Cones and targeted AoE have different modifiers
  - PBAoE (Point Blank AoE) typically has modifier ~1.5-2.0
  - Affects proc chance significantly in AoE-heavy builds

- **Min/Max Caps**:
  - Min proc chance scales with PPM (higher PPM = higher floor)
  - 90% cap prevents "guaranteed" procs even in very slow powers
  - Makes very long-recharge powers less attractive for proc slotting

**Proc Enhancement Mechanics:**
- Procs **do not** enhance or get enhanced by other slotting
- Damage procs use fixed damage tables (by level)
- Proc effects are separate power activations
- Multiple procs can trigger simultaneously
- Each proc rolls independently

**Player Impact:**
Proc calculation affects:
- **Slotting Decisions**: Whether to slot proc vs normal enhancement
- **Power Selection**: Choosing powers with favorable proc characteristics
- **Build Strategy**: Balancing global recharge vs proc effectiveness
- **DPS Calculation**: Adding proc damage to total damage output
- **Endurance Management**: Endurance discount procs in attack chains

## Notes for Implementation

**Key Data Structures:**
```python
# Enhancement flags
is_proc: bool                    # Marks enhancement as proc
effect_chance: float             # Base probability (legacy procs)

# Effect PPM properties
procs_per_minute: float          # PPM value (0 if flat percentage)
base_probability: float          # Flat % or initial value
min_proc_chance: float           # Calculated minimum
max_proc_chance: float = 0.9     # Fixed maximum (90%)

# Power properties needed
recharge_time: float             # Actual recharge after slotting
base_recharge_time: float        # Unslotted recharge
cast_time: float                 # Activation time
aoe_modifier: float              # Area effect multiplier
power_type: PowerType            # Click, Auto, Toggle

# Character context
global_haste_buff: float         # Total recharge buff from set bonuses, Hasten, etc.
modify_effects: dict             # Character-specific proc modifiers
```

**Implementation Priority:**
1. **Phase 1**: Basic proc flag and flat percentage (legacy procs)
2. **Phase 2**: PPM calculation for click powers (most common case)
3. **Phase 3**: Auto/toggle power 10-second rule
4. **Phase 4**: Global recharge interaction
5. **Phase 5**: Character-specific modifiers

**Testing Scenarios:**
- Flat percentage proc (33.3%) in various powers
- 3.5 PPM proc in 1-second recharge power vs 32-second recharge
- AoE power with different AoEModifier values
- High global recharge character (+200% recharge from Hasten + set bonuses)
- Auto/toggle power proc checks

**Common Player Questions:**
- "Why does my proc trigger less often with Hasten active?" → Global recharge impact
- "Why do procs work better in my nuke than my attack chain?" → Recharge time factor
- "Can I get a 100% chance proc?" → No, 90% max cap
- "Do procs benefit from damage buffs?" → No, fixed damage/effect tables
