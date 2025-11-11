# Build Totals - Other Stats

## Overview
- **Purpose**: Aggregate and display all remaining character stats shown in build planner totals (HP, endurance, recovery, regen, movement speeds, perception, stealth, threat)
- **Used By**: Build planner interface, power tooltips, character comparison tools
- **Complexity**: Medium
- **Priority**: Critical
- **Status**: Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `clsToonX.cs`
- **Class**: `clsToonX`
- **Primary Methods**:
  - `GenerateBuffedPowerArray()` - Lines ~3000-4000+ (main calculation loop)
  - HP/End calculations in stats aggregation section
  - Movement speed calculations with caps
- **File**: `Core/Statistics.cs`
- **Class**: `Statistics`
- **Display Methods**:
  - `HealthHitpointsPercentage` - HP as % of base
  - `EnduranceMaxEnd` - Max endurance
  - `HealthRegenHealthPerSec` - HP/sec regen rate
  - `EnduranceRecoveryNumeric` - End/sec recovery rate
  - Base constants for movement speeds

### Dependencies
- **Data Structures**:
  - `Character.TotalStatistics` class - Stores all aggregated stats
  - `Archetype` class - AT-specific base values and caps
  - `DatabaseAPI.ServerData` - Base movement speeds and caps
- **Related Calculations**:
  - Enhancement effects (buffs to these stats)
  - Set bonuses (common source of HP/recovery/regen bonuses)
  - AT scaling (different base values and caps per AT)

### Algorithm Pseudocode

```pseudocode
# MAX HP CALCULATION
function CalculateMaxHP():
    base_hp = archetype.Hitpoints  # e.g. 1606 for Tanker, 1017 for Blaster at level 50
    hp_bonuses = SumAllEffects(StatType.HPMax)  # From powers, enhancements, sets

    # Calculate uncapped total
    totals.HPMax = base_hp + hp_bonuses

    # Apply AT-specific cap (if enabled)
    if caps_enabled:
        totals_capped.HPMax = min(totals.HPMax, archetype.HPCap)  # e.g. 3212 for Tanker, 2088 for Blaster

        # Absorb (temp HP) is capped at max HP
        totals_capped.Absorb = min(totals.Absorb, totals_capped.HPMax)

# HP REGENERATION CALCULATION
function CalculateHPRegen():
    regen_buff_percent = SumAllEffects(StatType.HPRegen)  # e.g. 2.5 for 250%

    # Store as multiplier (not including base)
    totals.HPRegen = regen_buff_percent

    # Apply AT-specific regen cap
    totals_capped.HPRegen = min(totals.HPRegen, archetype.RegenCap - 1)
    # RegenCap is stored as total multiplier (e.g. 20.0 = 2000%)
    # Subtract 1 because base 100% is separate

    # For display: convert to HP/sec
    total_regen_multiplier = 1.0 + totals_capped.HPRegen
    hp_per_sec = total_regen_multiplier * archetype.BaseRegen * 1.666667
    # BaseRegen is typically 1.0
    # 1.666667 is the magic constant that converts regen % to HP/sec

    # For display: can also show as percentage
    hp_percent = (totals_capped.HPMax / archetype.Hitpoints) * 100.0

# MAX ENDURANCE CALCULATION
function CalculateMaxEndurance():
    base_end = 100.0  # All ATs start with 100 end
    end_bonuses = SumMaxEndEffects()  # From Accolades, IO bonuses

    totals.EndMax = end_bonuses  # Stored as bonus only

    # For display
    max_end_display = 100.0 + totals.EndMax  # e.g. 110, 120, etc.

# ENDURANCE RECOVERY CALCULATION
function CalculateEndRecovery():
    recovery_buff_percent = SumAllEffects(StatType.EndRec)  # e.g. 0.95 for 95%

    # Store as multiplier (not including base)
    totals.EndRec = recovery_buff_percent

    # Apply AT-specific recovery cap
    totals_capped.EndRec = min(totals.EndRec, archetype.RecoveryCap - 1)
    # RecoveryCap is typically 5.0 (500% total including base 100%)

    # For display: convert to End/sec
    total_recovery_multiplier = 1.0 + totals_capped.EndRec
    base_recovery_rate = archetype.BaseRecovery * 1.666667
    # BaseRecovery is typically 1.67 for most ATs
    # 1.666667 magic constant again

    max_end_for_calc = totals_capped.EndMax / 100.0 + 1.0
    end_per_sec = total_recovery_multiplier * base_recovery_rate * max_end_for_calc
    # Max end bonuses also increase recovery rate proportionally

    # For display: can also show as percentage
    recovery_percent = total_recovery_multiplier * 100.0

# MOVEMENT SPEEDS CALCULATION
function CalculateMovementSpeeds():
    # RUN SPEED
    base_run = DatabaseAPI.ServerData.BaseRunSpeed  # 21.0 ft/sec
    run_buff = max(SumAllEffects(StatType.RunSpeed), -0.9)  # Can't go below -90%
    totals.RunSpd = (1.0 + run_buff) * base_run

    # Calculate max run speed cap (soft cap that can be increased)
    max_run = DatabaseAPI.ServerData.MaxRunSpeed  # 58.65 ft/sec
    max_run_buff = SumAllEffects(StatType.MaxRunSpeed)  # From Swift, Speed IOs
    totals.MaxRunSpd = max_run + (max_run_buff * base_run)

    # Apply hard cap (absolute maximum)
    totals.MaxRunSpd = min(totals.MaxRunSpd, DatabaseAPI.ServerData.MaxMaxRunSpeed)  # 166.257 ft/sec
    totals.RunSpd = min(totals.RunSpd, DatabaseAPI.ServerData.MaxMaxRunSpeed)

    # Apply soft cap to capped totals
    totals_capped.RunSpd = min(totals.RunSpd, totals.MaxRunSpd)

    # JUMP SPEED (similar pattern)
    base_jump = DatabaseAPI.ServerData.BaseJumpSpeed  # 22.275 ft/sec
    jump_buff = max(SumAllEffects(StatType.JumpSpeed), -0.9)
    totals.JumpSpd = (1.0 + jump_buff) * base_jump

    max_jump = DatabaseAPI.ServerData.MaxJumpSpeed  # 114.4 ft/sec
    max_jump_buff = SumAllEffects(StatType.MaxJumpSpeed)
    totals.MaxJumpSpd = max_jump + (max_jump_buff * base_jump)
    totals.MaxJumpSpd = min(totals.MaxJumpSpd, DatabaseAPI.ServerData.MaxMaxJumpSpeed)  # 176.358 ft/sec
    totals.JumpSpd = min(totals.JumpSpd, DatabaseAPI.ServerData.MaxMaxJumpSpeed)

    totals_capped.JumpSpd = min(totals.JumpSpd, totals.MaxJumpSpd)

    # JUMP HEIGHT
    base_jump_height = DatabaseAPI.ServerData.BaseJumpHeight  # 4.0 ft
    jump_height_buff = max(SumAllEffects(StatType.JumpHeight), -0.9)
    totals.JumpHeight = (1.0 + jump_height_buff) * base_jump_height

    # Jump height has only a hard cap (no soft cap system)
    totals_capped.JumpHeight = min(totals.JumpHeight, DatabaseAPI.ServerData.MaxJumpHeight)  # 200.0 ft

    # FLY SPEED (similar pattern, but can be disabled)
    can_fly = CheckHasFlyPower()  # Check if character has any fly powers active

    if can_fly:
        base_fly = DatabaseAPI.ServerData.BaseFlySpeed  # 31.5 ft/sec
        fly_buff = max(SumAllEffects(StatType.FlySpeed), -0.9)
        totals.FlySpd = (1.0 + fly_buff) * base_fly

        max_fly = DatabaseAPI.ServerData.MaxFlySpeed  # 58.65 ft/sec (same as run)
        max_fly_buff = SumAllEffects(StatType.MaxFlySpeed)
        totals.MaxFlySpd = max_fly + (max_fly_buff * base_fly)
        totals.MaxFlySpd = min(totals.MaxFlySpd, DatabaseAPI.ServerData.MaxMaxFlySpeed)  # 257.985 ft/sec
        totals.FlySpd = min(totals.FlySpd, DatabaseAPI.ServerData.MaxMaxFlySpeed)

        totals_capped.FlySpd = min(totals.FlySpd, totals.MaxFlySpd)
    else:
        totals.FlySpd = 0
        totals_capped.FlySpd = 0

# PERCEPTION CALCULATION
function CalculatePerception():
    base_perception = DatabaseAPI.ServerData.BasePerception  # 500 ft for most ATs
    perception_buff = SumAllEffects(StatType.Perception)  # As decimal (0.2 = +20%)

    totals.Perception = base_perception * (1.0 + perception_buff)

    # Apply AT-specific perception cap
    totals_capped.Perception = min(totals.Perception, archetype.PerceptionCap)  # 1153 ft default

# STEALTH CALCULATION
function CalculateStealth():
    # Stealth is stored as radius values (in feet)
    # Higher = more visible, lower = stealthier
    # Separate values for PvE and PvP

    totals.StealthPvE = SumAllEffects(StatType.StealthPvE)  # Negative values increase stealth
    totals.StealthPvP = SumAllEffects(StatType.StealthPvP)

    # Stealth has no caps (additive stacking)

# THREAT LEVEL CALCULATION
function CalculateThreatLevel():
    threat_buff = SumAllEffects(StatType.ThreatLevel)  # Multiplier

    # Threat is relative to base (1.0)
    # Tanker taunt auras give high positive
    # Stealth powers give negative
    # No explicit caps

    totals.ThreatLevel = threat_buff

# ABSORB (Temp HP) CALCULATION
function CalculateAbsorb():
    absorb_total = SumAllEffects(StatType.Absorb)

    # Some absorb effects are % of max HP
    if effect.DisplayPercentage:
        absorb_total *= totals.HPMax

    totals.Absorb = absorb_total

    # Absorb is capped at max HP (see CalculateMaxHP above)
```

### Key Logic Snippets

**HP Calculation** (clsToonX.cs, ~line 3500):
```csharp
Totals.HPMax = _selfBuffs.Effect[(int)Enums.eStatType.HPMax] + (Archetype?.Hitpoints ?? 0);

// Later, apply cap
TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap);
TotalsCapped.Absorb = Math.Min(TotalsCapped.Absorb, TotalsCapped.HPMax);
```

**Regen/Recovery Caps** (clsToonX.cs, ~line 3600):
```csharp
TotalsCapped.HPRegen = Math.Min(TotalsCapped.HPRegen, Archetype.RegenCap - 1);
TotalsCapped.EndRec = Math.Min(TotalsCapped.EndRec, Archetype.RecoveryCap - 1);
```

**Movement Speed Calculations** (clsToonX.cs, ~line 3450):
```csharp
Totals.FlySpd = (1 + Math.Max(_selfBuffs.Effect[(int)Enums.eStatType.FlySpeed], -0.9f)) * Statistics.BaseFlySpeed;
Totals.RunSpd = (1 + Math.Max(_selfBuffs.Effect[(int)Enums.eStatType.RunSpeed], -0.9f)) * Statistics.BaseRunSpeed;
Totals.JumpSpd = (1 + Math.Max(_selfBuffs.Effect[(int)Enums.eStatType.JumpSpeed], -0.9f)) * Statistics.BaseJumpSpeed;
Totals.JumpHeight = (1 + Math.Max(_selfBuffs.Effect[(int)Enums.eStatType.JumpHeight], -0.9f)) * Statistics.BaseJumpHeight;

Totals.MaxFlySpd = Statistics.MaxFlySpeed + _selfBuffs.Effect[(int)Enums.eStatType.MaxFlySpeed] * Statistics.BaseFlySpeed;
Totals.MaxRunSpd = Statistics.MaxRunSpeed + _selfBuffs.Effect[(int)Enums.eStatType.MaxRunSpeed] * Statistics.BaseRunSpeed;
Totals.MaxJumpSpd = Statistics.MaxJumpSpeed + _selfBuffs.Effect[(int)Enums.eStatType.MaxJumpSpeed] * Statistics.BaseJumpSpeed;

// Apply MaxMax (hard caps)
Totals.FlySpd = Math.Min(Totals.FlySpd, DatabaseAPI.ServerData.MaxMaxFlySpeed);
Totals.RunSpd = Math.Min(Totals.RunSpd, DatabaseAPI.ServerData.MaxMaxRunSpeed);
Totals.JumpSpd = Math.Min(Totals.JumpSpd, DatabaseAPI.ServerData.MaxMaxJumpSpeed);

// Apply soft caps
TotalsCapped.RunSpd = Math.Min(TotalsCapped.RunSpd, Totals.MaxRunSpd);
TotalsCapped.JumpSpd = Math.Min(TotalsCapped.JumpSpd, Totals.MaxJumpSpd);
TotalsCapped.FlySpd = Math.Min(TotalsCapped.FlySpd, Totals.MaxFlySpd);
TotalsCapped.JumpHeight = Math.Min(TotalsCapped.JumpHeight, DatabaseAPI.ServerData.MaxJumpHeight);
```

**Perception/Stealth/Threat** (clsToonX.cs, ~line 3480):
```csharp
Totals.Perception = Statistics.BasePerception * (1 + _selfBuffs.Effect[(int)Enums.eStatType.Perception]);
Totals.StealthPvE = _selfBuffs.Effect[(int)Enums.eStatType.StealthPvE];
Totals.StealthPvP = _selfBuffs.Effect[(int)Enums.eStatType.StealthPvP];
Totals.ThreatLevel = _selfBuffs.Effect[(int)Enums.eStatType.ThreatLevel];

// Perception cap
TotalsCapped.Perception = Math.Min(TotalsCapped.Perception, Archetype.PerceptionCap);
```

**Display Methods** (Statistics.cs):
```csharp
public float HealthHitpointsPercentage => (float)(_character.TotalsCapped.HPMax / (double)_character.Archetype.Hitpoints * 100.0);

public float HealthRegenHealthPerSec => (float)(HealthRegen(false) * (double)_character.Archetype.BaseRegen * 1.66666662693024);

private float HealthRegen(bool uncapped)
{
    return uncapped ? _character.Totals.HPRegen + 1f : _character.TotalsCapped.HPRegen + 1f;
}

public float EnduranceMaxEnd => _character.Totals.EndMax + 100f;

public float EnduranceRecoveryNumeric => EnduranceRecovery(false) * (_character.Archetype.BaseRecovery * BaseMagic) * (_character.TotalsCapped.EndMax / 100 + 1);

private float EnduranceRecovery(bool uncapped)
{
    return uncapped ? _character.Totals.EndRec + 1f : _character.TotalsCapped.EndRec + 1f;
}
```

**Base Speed Constants** (Statistics.cs):
```csharp
public static readonly float BaseRunSpeed = DatabaseAPI.ServerData.BaseRunSpeed;  // 21.0
public static readonly float BaseJumpSpeed = DatabaseAPI.ServerData.BaseJumpSpeed;  // 22.275
public static readonly float BaseJumpHeight = DatabaseAPI.ServerData.BaseJumpHeight;  // 4.0
public static readonly float BaseFlySpeed = DatabaseAPI.ServerData.BaseFlySpeed;  // 31.5
internal const float BaseMagic = 1.666667f;  // Recovery/regen conversion constant
public static readonly float BasePerception = DatabaseAPI.ServerData.BasePerception;  // 500
```

**Archetype Base Values** (Archetype.cs):
```csharp
public int Hitpoints { get; set; }  // Base HP (varies by AT)
public float HPCap { get; set; }  // Max HP cap (varies by AT)
public float BaseRecovery { get; set; }  // Usually 1.67
public float BaseRegen { get; set; }  // Usually 1.0
public float RecoveryCap { get; set; }  // Usually 5.0 (500% total)
public float RegenCap { get; set; }  // Usually 20.0 (2000% total) for most, 30.0 for some
public float PerceptionCap { get; set; }  // Usually 1153 ft
public float BaseThreat { get; set; }  // Varies by AT (Tankers = 4.0, others = 1.0)
```

## Game Mechanics Context

### Why These Stats Matter

**Hit Points (HP)**:
- HP determines survivability - how much damage you can take before defeat
- Base HP varies significantly by AT (Tankers/Brutes highest, Blasters/Defenders lowest)
- HP bonuses from Accolades (+10% from Atlas Medallion, +20% from Freedom Phalanx Reserve) are critical
- Set bonuses typically give +1.5% to +3% HP per bonus
- Percentage display helps compare across ATs (200% HP means double base)

**HP Regeneration**:
- Determines how fast you passively recover HP
- Base regen is 100% = 5% of max HP every 12 seconds
- Expressed as HP/sec in build planner (easier to understand than %)
- Regen caps vary by AT: most are 2000%, but some (Willpower users, Regen users) can go higher
- Fast Healing, Health, regen IOs, and Miracle/Numina uniques are main sources
- Diminishing value at high HP (40 HP/sec matters more at 1000 HP than 3000 HP)

**Max Endurance**:
- Base is 100 for all ATs
- Only bonuses are from Accolades (+5 from Demonic, +10 from Freedom Phalanx Reserve)
- Critical quality of life stat - more endurance = longer fights before rest
- Max end bonuses also proportionally increase recovery rate

**Endurance Recovery**:
- Determines how fast you regain endurance
- Base recovery is 100% = 1.67 end/sec for most ATs
- Recovery bonuses are CRITICAL for high-end-cost builds (toggles, attack chains)
- Common sources: Stamina, Performance Shifter proc, Miracle/Numina uniques, set bonuses
- Recovery caps at 500% (8.35 end/sec base) for most ATs
- Can display capped vs uncapped to show if you're hitting cap

**Movement Speeds**:
- Three-tier cap system: base speed → soft cap → hard cap
- Soft cap can be increased by powers (Swift + Speed IO bonuses)
- Hard cap is absolute maximum (can't exceed even with bugs)
- Run speed: 21 → 58.65 → 166.257 ft/sec
- Jump speed: 22.275 → 114.4 → 176.358 ft/sec
- Fly speed: 31.5 → 58.65 → 257.985 ft/sec (1.5x run base)
- Speed buffs have floor at -90% (can't reduce below 10% of base)
- Jump height: 4 → 200 ft (simple system, no soft cap)

**Perception**:
- How far you can see enemies (base 500 ft)
- Matters for spotting stealthed enemies in PvP
- Increased by Tactics, +Perception IOs
- Capped at 1153 ft for most ATs
- Rarely displayed in builds (low priority stat)

**Stealth**:
- Reduces enemy detection range (separate PvE and PvP values)
- Measured in feet (larger negative = harder to detect)
- Stealth IO gives -35 ft, Hide powers give -500+ ft
- No caps (stacks additively)
- PvP stealth values typically lower than PvE

**Threat Level**:
- Affects enemy targeting priority (aggro)
- Tankers have 4x base threat, most others have 1x
- Taunt auras add +4 to +5 threat
- Stealth powers reduce threat (-4 to -5)
- Rarely displayed (mostly relevant for tanks/brutes)

**Absorb (Temporary HP)**:
- Shield that absorbs damage before HP is touched
- Capped at current max HP (can't have more absorb than HP)
- Some effects give flat absorb, others give % of max HP
- Example: Frostwork gives absorb equal to ~20% of target's max HP

### Historical Context

**Magic Number 1.666667**:
- This constant appears in regen and recovery calculations
- Converts percentage-based modifiers to per-second rates
- Based on game tick rate and balance decisions from original CoH development
- Never explained in game, discovered by players through testing

**Movement Speed Formula Evolution**:
- Original CoH had simpler speed caps
- Issue 5 (ED) introduced the soft cap system for movement
- Hard caps prevent exploits from stacking extreme speed buffs
- Fly speed base is 1.5x run speed (balance: fly is safer, should be slower relatively)

**HP Caps by AT**:
- Tanker: 3212 HP (200% of 1606 base)
- Scrapper/Brute: 2409 HP (200% of 1204 base)
- Blaster: 2088 HP (205% of 1017 base) - slightly higher cap % to compensate for low base
- Defender: 1874 HP (200% of 937 base)
- Reaching HP cap requires significant investment (Accolades + set bonuses + incarnate)

**Regen Caps**:
- Most ATs: 2000% (30x base, ~100 HP/sec for most builds at cap)
- Willpower/Regen users: 3000% (special benefit for those sets)
- Reaching cap is rare outside specialized regen builds
- At 2000%, you recover 5% HP every 0.6 seconds

**Recovery Caps**:
- All ATs: 500% total (4x base recovery)
- Much easier to cap than regen (common in heavily IO'd builds)
- At cap: ~8.35 end/sec, which sustains most attack chains + toggles
- Builds with Performance Shifter proc often cap recovery

## Python Implementation Guide

### Proposed Architecture

**Module**: `backend/app/calculations/build_aggregation/other_stats.py`

**Integration Points**:
- Requires archetype data (base values, caps)
- Requires server data (movement speed constants)
- Requires effect aggregation system (sum buffs by stat type)
- Outputs displayed in build totals API endpoint

**Data Flow**:
```
Character Build → Effect Aggregation → Stat Calculations → Apply AT Caps → Format for Display
```

### Implementation Notes

**Key Classes/Functions**:
```python
class OtherStatCalculator:
    def __init__(self, archetype, effects, server_data):
        self.archetype = archetype
        self.effects = effects  # Aggregated effects by stat type
        self.server_data = server_data
        self.totals = {}
        self.totals_capped = {}

    def calculate_all(self):
        """Calculate all other stats in dependency order"""
        self.calculate_hp()
        self.calculate_endurance()
        self.calculate_movement()
        self.calculate_perception_stealth_threat()
        return {
            'uncapped': self.totals,
            'capped': self.totals_capped,
            'display': self.format_for_display()
        }

    def calculate_hp(self):
        """Max HP, regen, absorb"""
        # HP Max
        base_hp = self.archetype.hitpoints
        hp_bonuses = self.sum_effects('hp_max')
        self.totals['hp_max'] = base_hp + hp_bonuses
        self.totals_capped['hp_max'] = min(self.totals['hp_max'], self.archetype.hp_cap)

        # HP Regen (stored as multiplier, not including base)
        regen_buff = self.sum_effects('hp_regen')
        self.totals['hp_regen'] = regen_buff
        self.totals_capped['hp_regen'] = min(regen_buff, self.archetype.regen_cap - 1.0)

        # Absorb
        absorb = self.sum_effects('absorb', hp_max=self.totals['hp_max'])
        self.totals['absorb'] = absorb
        self.totals_capped['absorb'] = min(absorb, self.totals_capped['hp_max'])

    def calculate_endurance(self):
        """Max endurance and recovery"""
        # Max End (bonuses only, base 100 added in display)
        end_bonuses = self.sum_effects('end_max')
        self.totals['end_max'] = end_bonuses

        # End Recovery (stored as multiplier, not including base)
        recovery_buff = self.sum_effects('end_recovery')
        self.totals['end_recovery'] = recovery_buff
        self.totals_capped['end_recovery'] = min(recovery_buff, self.archetype.recovery_cap - 1.0)

    def calculate_movement(self):
        """Run, jump, fly speeds and jump height"""
        for speed_type in ['run', 'jump', 'fly']:
            self._calculate_speed(speed_type)
        self._calculate_jump_height()

    def _calculate_speed(self, speed_type):
        """Generic speed calculation with soft/hard caps"""
        base_speed = getattr(self.server_data, f'base_{speed_type}_speed')
        speed_buff = max(self.sum_effects(f'{speed_type}_speed'), -0.9)

        # Calculate buffed speed
        speed = (1.0 + speed_buff) * base_speed

        # Calculate soft cap (can be increased)
        max_speed = getattr(self.server_data, f'max_{speed_type}_speed')
        max_speed_buff = self.sum_effects(f'max_{speed_type}_speed')
        soft_cap = max_speed + (max_speed_buff * base_speed)

        # Apply hard cap to soft cap
        hard_cap = getattr(self.server_data, f'max_max_{speed_type}_speed')
        soft_cap = min(soft_cap, hard_cap)

        # Apply hard cap to speed
        speed = min(speed, hard_cap)

        # Store results
        self.totals[f'{speed_type}_speed'] = speed
        self.totals[f'max_{speed_type}_speed'] = soft_cap
        self.totals_capped[f'{speed_type}_speed'] = min(speed, soft_cap)

    def format_for_display(self):
        """Convert internal values to user-friendly display"""
        return {
            'hp': {
                'max': round(self.totals_capped['hp_max'], 1),
                'max_uncapped': round(self.totals['hp_max'], 1),
                'percent_of_base': round(self.totals_capped['hp_max'] / self.archetype.hitpoints * 100, 1),
                'regen_hp_per_sec': self._regen_hp_per_sec(capped=True),
                'regen_hp_per_sec_uncapped': self._regen_hp_per_sec(capped=False),
                'regen_percent': round((1.0 + self.totals_capped['hp_regen']) * 100, 1),
                'absorb': round(self.totals_capped['absorb'], 1)
            },
            'endurance': {
                'max': 100.0 + self.totals['end_max'],
                'recovery_per_sec': self._recovery_end_per_sec(capped=True),
                'recovery_per_sec_uncapped': self._recovery_end_per_sec(capped=False),
                'recovery_percent': round((1.0 + self.totals_capped['end_recovery']) * 100, 1)
            },
            'movement': {
                'run_speed': round(self.totals_capped['run_speed'], 2),
                'run_speed_cap': round(self.totals['max_run_speed'], 2),
                'jump_speed': round(self.totals_capped['jump_speed'], 2),
                'jump_height': round(self.totals_capped['jump_height'], 2),
                'fly_speed': round(self.totals_capped['fly_speed'], 2)
            },
            'perception': round(self.totals_capped['perception'], 1),
            'stealth_pve': round(self.totals['stealth_pve'], 1),
            'stealth_pvp': round(self.totals['stealth_pvp'], 1),
            'threat': round(self.totals['threat'], 2)
        }

    def _regen_hp_per_sec(self, capped=True):
        """Convert regen multiplier to HP/sec"""
        regen = self.totals_capped['hp_regen'] if capped else self.totals['hp_regen']
        total_multiplier = 1.0 + regen
        return round(total_multiplier * self.archetype.base_regen * 1.666667, 2)

    def _recovery_end_per_sec(self, capped=True):
        """Convert recovery multiplier to End/sec"""
        recovery = self.totals_capped['end_recovery'] if capped else self.totals['end_recovery']
        end_max = self.totals_capped['end_max'] if capped else self.totals['end_max']

        total_multiplier = 1.0 + recovery
        base_rate = self.archetype.base_recovery * 1.666667
        max_end_mult = (end_max / 100.0) + 1.0

        return round(total_multiplier * base_rate * max_end_mult, 2)
```

**Data Requirements**:

Archetype data:
```python
{
    "hitpoints": 1606,  # Base HP at level 50
    "hp_cap": 3212.0,   # Max HP cap
    "base_regen": 1.0,  # Base regen multiplier
    "regen_cap": 20.0,  # Max regen (2000% including base 100%)
    "base_recovery": 1.67,  # Base recovery multiplier
    "recovery_cap": 5.0,    # Max recovery (500% including base 100%)
    "perception_cap": 1153.0,  # Max perception distance
    "base_threat": 4.0  # Tanker = 4, most others = 1
}
```

Server data constants:
```python
{
    "base_run_speed": 21.0,
    "max_run_speed": 58.65,
    "max_max_run_speed": 166.257,
    "base_jump_speed": 22.275,
    "max_jump_speed": 114.4,
    "max_max_jump_speed": 176.358,
    "base_jump_height": 4.0,
    "max_jump_height": 200.0,
    "base_fly_speed": 31.5,
    "max_fly_speed": 58.65,
    "max_max_fly_speed": 257.985,
    "base_perception": 500.0
}
```

**Edge Cases to Handle**:

1. **Percentage-based Absorb**: Some absorb effects give % of max HP, not flat values
   - Check effect.display_percentage flag
   - Multiply by current max HP if true

2. **Fly Speed When No Fly Power**: Set to 0 if character has no active fly powers
   - Need power activation tracking

3. **Movement Speed Floor**: Can't reduce below 10% of base (-90% debuff floor)
   - Use `max(speed_buff, -0.9)` before applying

4. **Max Endurance Affects Recovery Rate**: Higher max end = higher recovery rate
   - Proportional increase: (max_end / 100 + 1)

5. **Capped vs Uncapped Display**: UI should show both values if player is hitting caps
   - Shows what they're losing to caps
   - Encourages diversifying bonuses

6. **AT-Specific Caps**: Different ATs have different values
   - Tanker: 3212 HP cap, 4.0 base threat
   - Blaster: 2088 HP cap, 1.0 base threat
   - Must load from archetype data, not hardcode

**Testing Strategy**:

1. **Unit Tests**:
   - Test each stat type calculation individually
   - Test cap application (below cap, at cap, above cap)
   - Test movement speed soft/hard cap interaction
   - Test percentage-based absorb calculation

2. **Integration Tests**:
   - Compare Python output to MidsReborn for sample builds
   - Test Tanker at HP cap (should show 3212)
   - Test Speed build hitting run speed caps
   - Test Regen build hitting regen cap

3. **Known Test Cases**:
```python
# Tanker with Accolades
{
    "archetype": "Tanker",
    "effects": {
        "hp_max": 482,  # 30% from Accolades (1606 * 0.3)
    },
    "expected": {
        "hp_max": 2088,  # 1606 + 482
        "hp_percent": 130.0
    }
}

# Blaster at HP cap
{
    "archetype": "Blaster",
    "effects": {
        "hp_max": 1071,  # Enough to cap (1017 base, 2088 cap)
    },
    "expected": {
        "hp_max": 2088,  # Capped
        "hp_max_uncapped": 2088
    }
}

# Speed build
{
    "archetype": "Scrapper",
    "effects": {
        "run_speed": 0.95,  # 95% run speed
        "max_run_speed": 0.5,  # 50% increased cap
    },
    "expected": {
        "run_speed": 40.95,  # (1 + 0.95) * 21
        "run_speed_capped": 40.95,  # Under soft cap
        "max_run_speed": 69.15  # 58.65 + (0.5 * 21)
    }
}

# Recovery cap
{
    "archetype": "Defender",
    "effects": {
        "end_recovery": 4.5,  # 450% recovery
    },
    "expected": {
        "end_recovery_percent": 500.0,  # Capped at 500%
        "end_recovery_per_sec": 8.35  # At cap
    }
}
```

### Performance Considerations

- These calculations are lightweight (no loops, just arithmetic)
- Cache archetype and server data (loaded once at startup)
- Calculate all stats in one pass (avoid re-aggregating effects)
- Round display values only in formatting step (keep full precision internally)

### C# vs Python Gotchas

1. **Float Precision**: C# uses `float` (32-bit), Python uses `float` (64-bit)
   - Should match closely, but round display values to avoid confusion
   - Magic constant 1.666667 may differ slightly in last decimal

2. **Min/Max Functions**: Direct equivalents in both languages
   - C#: `Math.Min(a, b)`, `Math.Max(a, b)`
   - Python: `min(a, b)`, `max(a, b)`

3. **Null Safety**: C# uses null-coalescing (`Archetype?.Hitpoints ?? 0`)
   - Python: Use `getattr(archetype, 'hitpoints', 0)` or `archetype.hitpoints if archetype else 0`

4. **Integer Division**: Max end is integer in some places
   - Be explicit: `int(max_end)` or `float(max_end)` as needed

## References

### Related Calculation Specs
- **Spec 01**: Power Effects Core (effect types and stacking)
- **Spec 16**: Archetype Modifiers (AT scaling that affects these stats)
- **Spec 17**: Archetype Caps (HP/regen/recovery caps by AT)
- **Spec 19-23**: Other Build Totals (defense, resistance, recharge, damage, accuracy)

### MidsReborn Code References
- `clsToonX.cs` - Main calculation loop
- `Core/Statistics.cs` - Display value formatting
- `Core/Base/Data_Classes/Archetype.cs` - AT data structure
- `Core/Base/Data_Classes/Character.cs` - TotalStatistics structure
- `Core/Stats.cs` - Modern stats display structure

### Key Constants & Formulas
- HP Regen: `(1 + regen_buff) * base_regen * 1.666667` = HP/sec
- End Recovery: `(1 + recovery_buff) * base_recovery * 1.666667 * (1 + max_end/100)` = End/sec
- Movement Speed: `(1 + speed_buff) * base_speed`, capped at soft cap, hard cap
- Perception: `base_perception * (1 + perception_buff)`, capped at AT cap

### Game Balance Notes
- HP cap prevents extreme tankiness (even Tankers cap at ~3200 HP)
- Recovery cap prevents infinite endurance builds
- Regen cap prevents unkillable regen builds (but cap is very high)
- Movement caps prevent speed exploits and maintain game balance
- Soft caps can be increased (reward for slotting Swift, etc.)
- Hard caps are absolute (prevent bugs/exploits)

---

**Document Status**: 🟡 Breadth Complete - Ready for Milestone 2 tracking
**Implementation Priority**: Critical - User-facing stats displayed in all builds
**Next Steps**:
1. Implement in `backend/app/calculations/build_aggregation/other_stats.py`
2. Add archetype data with all base values and caps
3. Add server data constants for movement speeds
4. Create unit tests for each stat type
5. Integration test with MidsReborn comparison builds
6. Add to build totals API endpoint
