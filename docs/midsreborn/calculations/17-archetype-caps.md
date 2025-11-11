# Archetype Caps

## Overview
- **Purpose**: Define and enforce archetype-specific caps on defense, resistance, damage, HP, recovery, and regeneration to maintain game balance
- **Used By**: Build totals, power calculations, character stats display, survivability calculations
- **Complexity**: Medium
- **Priority**: CRITICAL
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Archetype.cs`
- **Related Files**:
  - `clsToonX.cs` - Cap enforcement in `TotalsCapped` calculation
  - `Core/Statistics.cs` - Capped vs uncapped display
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - UI display of caps
  - `Forms/OptionsMenuItems/DbEditor/frmEditArchetype.cs` - Archetype editor

### Archetype Cap Properties

Each archetype defines maximum values for various character attributes:

```csharp
// From Core/Base/Data_Classes/Archetype.cs
public class Archetype
{
    public float DamageCap { get; set; }      // Damage buff cap (4.0 = 400%)
    public float ResCap { get; set; }         // Resistance cap (0.75-0.9 = 75-90%)
    public float HPCap { get; set; }          // Max hit points (varies by AT)
    public float RecoveryCap { get; set; }    // Endurance recovery cap (multiplier)
    public float RegenCap { get; set; }       // HP regeneration cap (multiplier)
    public float RechargeCap { get; set; }    // Recharge speed cap (multiplier)
    public float PerceptionCap { get; set; }  // Perception range cap

    // Default values (constructor)
    public Archetype()
    {
        DamageCap = 4f;        // 400% default
        ResCap = 0.9f;         // 90% default
        HPCap = 5000f;         // 5000 HP default
        RecoveryCap = 5f;      // 500% recovery
        RegenCap = 20f;        // 2000% regen
        RechargeCap = 5f;      // 500% recharge
        PerceptionCap = 1153f; // ~1150 feet
    }
}
```

### High-Level Algorithm

```
Archetype Caps Application Process:

1. Calculate Uncapped Values:
   - Sum all buffs from powers, sets, incarnates
   - Apply enhancement bonuses
   - Apply global modifiers
   - Store in Character.Totals (uncapped)

2. Apply Archetype Caps:
   - Damage: cap at Archetype.DamageCap
   - Resistance: cap at Archetype.ResCap per damage type
   - HP: cap at Archetype.HPCap
   - Recovery: cap at Archetype.RecoveryCap
   - Regeneration: cap at Archetype.RegenCap
   - Recharge: cap at Archetype.RechargeCap
   - Store in Character.TotalsCapped (game values)

3. Display Both Values:
   - Show uncapped value (for build analysis)
   - Show capped value (actual in-game value)
   - Indicate when cap is reached
   - Show archetype cap reference
```

## Archetype Cap Values

### Damage Caps

Damage caps represent the maximum total damage (base + buffs) a character can achieve.

| Archetype | Damage Cap | Notes |
|-----------|------------|-------|
| Brute | 775% | Highest damage cap due to Fury mechanic |
| Blaster | 500% | High cap for primary damage dealers |
| Scrapper | 500% | High melee damage cap |
| Stalker | 500% | High burst damage cap |
| Corruptor | 500% | High ranged damage cap |
| Tanker | 400% | Lower due to survivability focus |
| Defender | 400% | Support-focused, lower damage |
| Controller | 400% | Control-focused, lower damage |
| Dominator | 400% | Control-focused with moderate damage |
| Mastermind | 400% | Pet-focused, lower personal damage |
| Peacebringer | 400% | Balanced hybrid |
| Warshade | 400% | Balanced hybrid |
| Sentinel | 400% | Balanced ranged/defense hybrid |

**Key Mechanics**:
- Base damage is 100% (unslotted, unbuffed)
- Damage cap includes base, so 500% cap = 100% base + 400% bonus
- Buffs beyond cap are wasted
- Some temporary powers can exceed cap

**Code Implementation**:
```csharp
// From clsToonX.cs
TotalsCapped.BuffDam = Math.Min(TotalsCapped.BuffDam, Archetype.DamageCap - 1);

// Note: Subtracts 1 because base damage (1.0) is separate
// So 4.0 cap - 1.0 base = 3.0 (300%) bonus max
```

### Resistance Caps

Resistance caps limit how much damage mitigation from resistance a character can achieve.

| Archetype | Resistance Cap | Notes |
|-----------|----------------|-------|
| Tanker | 90% | Highest survivability, primary role |
| Brute | 90% | Tanker-level survivability |
| Peacebringer | 85% | Kheldian special case |
| Warshade | 85% | Kheldian special case |
| Scrapper | 75% | Melee with moderate survivability |
| Stalker | 75% | Melee with moderate survivability |
| Sentinel | 75% | Ranged with moderate survivability |
| Blaster | 75% | Damage-focused with lower survivability |
| Defender | 75% | Support-focused |
| Controller | 75% | Control-focused |
| Corruptor | 75% | Damage/support hybrid |
| Dominator | 75% | Control/damage hybrid |
| Mastermind | 75% | Pet-focused |

**Key Mechanics**:
- Cap applies per damage type (Smashing, Lethal, Fire, Cold, Energy, Negative, Psionic, Toxic)
- Resistance buffs beyond cap are wasted
- Unresistable damage ignores resistance entirely
- Resistance reduces damage taken: 75% res = take 25% damage = 4x effective HP

**Code Implementation**:
```csharp
// From clsToonX.cs
for (var index = 0; index < TotalsCapped.Res.Length; index++)
{
    TotalsCapped.Res[index] = Math.Min(TotalsCapped.Res[index], Archetype.ResCap);
}
```

**Display Format**:
```csharp
// From Forms/WindowMenuItems/frmTotalsV2.cs
resValueUncapped > resValue & resValue > 0
    ? $"{resValueUncapped:##0.##}% resistance (capped at {Archetype.ResCap * 100:##0.##}%)"
    : $"{resValue:##0.##}% resistance ({atName} cap: {Archetype.ResCap * 100:##0.##}%)"
```

### Defense "Cap" (Soft Cap vs Hard Cap)

Defense is unique: it has NO archetype-specific hard cap for gameplay, but has a "soft cap" based on ToHit mechanics.

**Soft Cap**: 45% defense vs even-level enemies
- Enemies have 50% base ToHit
- 45% defense → 50% - 45% = 5% hit chance (minimum)
- This is the "soft cap" because you've reduced hit chance by 90%

**Hard Caps** (MidsReborn display/calculation only):
| Archetype | Display Cap | Notes |
|-----------|-------------|-------|
| Tanker | 225% | Display limit only |
| Brute | 225% | Display limit only |
| Scrapper | 200% | Display limit only |
| Stalker | 200% | Display limit only |
| Peacebringer | 200% | Display limit only |
| Warshade | 200% | Display limit only |
| Others | 175% | Display limit only |

**Key Mechanics**:
- Defense past 45% helps vs higher-level enemies (+tohit)
- Defense past 45% helps vs enemies with +tohit buffs
- Defense debuffs can drop you below soft cap (defense cascade)
- Defense Debuff Resistance (DDR) prevents cascade deaths

**Why Soft Cap Matters**:
```
Enemy ToHit: 50% (even level)
Your Defense: 0%  → 50% hit chance → take 100% of attacks
Your Defense: 22.5% → 27.5% hit chance → take 55% of attacks
Your Defense: 45% → 5% hit chance → take 10% of attacks (5% floor)

Going from 0% to 45% defense = 10x survivability vs attacks
Going from 45% to 90% defense = minimal benefit (already at floor)
```

### HP Caps

HP caps limit maximum hit points from +MaxHP buffs.

| Archetype | HP Cap | Notes |
|-----------|--------|-------|
| Tanker | ~3534 | Highest base HP and cap |
| Brute | ~3212 | High HP for survivability |
| Scrapper | ~2409 | Moderate melee HP |
| Stalker | ~2091 | Lower melee HP (stealth focus) |
| Sentinel | ~2409 | Moderate ranged HP |
| Defender | ~1874 | Support role, lower HP |
| Controller | ~1874 | Control role, lower HP |
| Blaster | ~1874 | Damage role, lowest HP |
| Corruptor | ~1874 | Damage/support hybrid |
| Dominator | ~1874 | Control/damage hybrid |
| Mastermind | ~1874 | Pet-focused, lowest personal HP |
| Peacebringer | varies | Form-dependent |
| Warshade | varies | Form-dependent |

**Key Mechanics**:
- Base HP varies by archetype and level
- +MaxHP buffs increase HP pool
- Accolades (Atlas Medallion, Portal Jockey) add +MaxHP
- HP cap is absolute maximum from all sources
- Default cap in code: 5000 HP (overridden per AT)

**Code Implementation**:
```csharp
// From clsToonX.cs
if (Archetype.HPCap > 0)
    TotalsCapped.HPMax = Math.Min(TotalsCapped.HPMax, Archetype.HPCap);
```

### Recovery Caps

Recovery caps limit endurance recovery rate (endurance per second).

| Archetype | Recovery Cap | End/sec | Notes |
|-----------|--------------|---------|-------|
| Controller | 1200% | 12.51/s | Highest for support ATs |
| Dominator | 1200% | 12.51/s | High for control ATs |
| Mastermind | 1200% | 12.51/s | Pet management needs |
| Defender | 1000% | 10.42/s | High for support AT |
| Tanker | 800% | 8.34/s | Standard melee |
| Brute | 800% | 8.34/s | Standard melee |
| Scrapper | 800% | 8.34/s | Standard melee |
| Stalker | 800% | 8.34/s | Standard melee |
| Sentinel | 800% | 8.34/s | Standard ranged |
| Blaster | 800% | 8.34/s | Standard damage |
| Corruptor | 800% | 8.34/s | Standard damage/support |
| Peacebringer | 800% | 8.34/s | Standard hybrid |
| Warshade | 800% | 8.34/s | Standard hybrid |

**Key Mechanics**:
- Base recovery: 1.67 end/sec (100%)
- Recovery cap is percentage of base (500% = 8.34 end/sec)
- Physical Perfection, Stamina, set bonuses stack additively
- Recovery debuffs can reduce below 0% (no recovery)

**Code Implementation**:
```csharp
// From clsToonX.cs
TotalsCapped.EndRec = Math.Min(TotalsCapped.EndRec, Archetype.RecoveryCap - 1);
```

**Default value**: 5f (500% = 5x base recovery)

### Regeneration Caps

Regeneration caps limit HP regeneration rate (% of max HP per second).

| Archetype | Regen Cap | Notes |
|-----------|-----------|-------|
| Scrapper | 3000% | Highest regen potential |
| Stalker | 3000% | Highest regen potential |
| Tanker | 2500% | High regen for survivability |
| Brute | 2500% | High regen for survivability |
| Defender | 2000% | Standard regen cap |
| Controller | 2000% | Standard regen cap |
| Blaster | 2000% | Standard regen cap |
| Corruptor | 2000% | Standard regen cap |
| Dominator | 2000% | Standard regen cap |
| Mastermind | 2000% | Standard regen cap |
| Sentinel | 2000% | Standard regen cap |
| Peacebringer | 2000% | Standard regen cap |
| Warshade | 2000% | Standard regen cap |

**Key Mechanics**:
- Base regeneration: 100% HP per 240 seconds = 0.417% HP/sec
- Regen cap is percentage of base
- 3000% regen = 30x base = 12.5% HP/sec = full HP in 8 seconds
- Health auto power, set bonuses, Instant Healing stack additively
- Regeneration debuffs can reduce below 0% (negative regen)

**Code Implementation**:
```csharp
// From clsToonX.cs
TotalsCapped.HPRegen = Math.Min(TotalsCapped.HPRegen, Archetype.RegenCap - 1);
```

**Default value**: 20f (2000% = 20x base regen)

### Recharge Caps

Recharge caps limit how fast powers can recharge.

| Archetype | Recharge Cap | Notes |
|-----------|--------------|-------|
| All | 500% | Universal cap |

**Key Mechanics**:
- Base recharge: 100% (unmodified power recharge time)
- +Recharge buffs reduce recharge time
- Formula: ActualRecharge = BaseRecharge / (1 + BonusRecharge)
- 400% +recharge → 5x faster recharge → 1/5th recharge time
- Hasten, Speed Boost, set bonuses stack additively
- Recharge debuffs can slow powers below base

**Code Implementation**:
```csharp
// From clsToonX.cs
TotalsCapped.BuffHaste = Math.Min(TotalsCapped.BuffHaste, Archetype.RechargeCap - 1);
```

**Default value**: 5f (500% = 5x recharge speed → 1/5th recharge time)

### Perception Cap

Perception caps limit how far a character can see/target.

| Archetype | Perception Cap | Notes |
|-----------|----------------|-------|
| All | ~1153 feet | Universal cap |

**Key Mechanics**:
- Base perception: ~500 feet
- Tactics, +Perception IOs increase range
- Stealth/invisibility reduce enemy perception of you
- Perception cap prevents infinite sight range

**Default value**: 1153f (feet)

## Why Caps Exist (Game Balance)

### 1. Prevent God-Mode

Without caps, characters could stack buffs infinitely:
- Infinite resistance = invincible
- Infinite damage = one-shot everything
- Infinite recovery = unlimited endurance
- This would trivialize all content

### 2. Archetype Identity

Different caps reinforce archetype roles:
- Tankers have 90% resistance cap → best survivability
- Brutes have 775% damage cap → highest damage potential
- Blasters have 500% damage cap but 75% resistance → glass cannon
- Controllers have 1200% recovery cap → sustained support/control

### 3. Diminishing Returns

Caps create natural breakpoints for build planning:
- Softcapping defense at 45% is a goal
- Reaching resistance cap is build achievement
- Damage cap requires team buffs (not solo achievable)
- This creates build diversity and teamwork value

### 4. Power Balance

Caps prevent certain powers from being overpowered:
- Rage (80% damage buff) would be broken without damage cap
- Instant Healing would be broken without regen cap
- Invincibility would be broken without defense/resistance caps

## Cap Display in UI

### Capped vs Uncapped Values

MidsReborn displays both values to show:
1. **Uncapped**: What you have from all sources (useful for analysis)
2. **Capped**: What actually applies in game (game mechanics)

**Display Patterns**:

**When NOT at cap**:
```
75.0% Fire resistance (Tanker cap: 90%)
```

**When AT cap reached**:
```
95.2% Fire resistance (capped at 90%)
```

**Code Implementation**:
```csharp
// From Forms/WindowMenuItems/frmTotalsV2.cs
if (uncappedValue > cappedValue && cappedValue > 0)
{
    // Show both uncapped and cap
    tooltip = $"{uncappedValue:##0.##}% resistance (capped at {Archetype.ResCap * 100:##0.##}%)";
}
else
{
    // Show current and cap reference
    tooltip = $"{cappedValue:##0.##}% resistance ({atName} cap: {Archetype.ResCap * 100:##0.##}%)";
}
```

### Color Coding

Some builds use color to indicate cap status:
- Green: Below 75% of cap (room to grow)
- Yellow: 75-99% of cap (approaching cap)
- Red: At or over cap (wasted buffs)

### Cap Indicators

Graphical displays (bars, meters) show:
- Current value as fill
- Cap as maximum bar size
- Overflow as different color (wasted)

## Soft Caps vs Hard Caps

### Hard Caps (Absolute Maximum)

**Enforced by game engine**, cannot exceed:
- Resistance: 75-90% per archetype
- Damage: 400-775% per archetype
- HP: Varies per archetype
- Recovery: 800-1200% per archetype
- Regeneration: 2000-3000% per archetype
- Recharge: 500% universal

**Implementation**: `Math.Min(value, cap)`

### Soft Caps (Optimal Target)

**Not enforced**, but diminishing returns past this point:
- Defense: 45% (vs even-level enemies)
  - Past 45%, only helps vs higher level or +tohit enemies
  - Minimal benefit vs standard enemies
- Recharge: ~123% (+recharge) for perma-Hasten
  - Enough to chain Hasten indefinitely
  - More recharge helps other powers but Hasten is key benchmark

**Why soft caps matter**:
- Build planning targets (45% defense is common goal)
- Cost-benefit analysis (going past soft cap is expensive)
- Power selection decisions (worth sacrificing slots?)

## Example: Archetype Comparison

Let's compare three archetypes building for survivability:

### Tanker (Invulnerability)
- Resistance cap: 90%
- Can reach 90% S/L resistance easily
- Moderate defense (30-35%)
- HP cap: ~3534
- Result: Extremely tanky, minimal damage

### Scrapper (Super Reflexes)
- Resistance cap: 75% (rarely reached)
- High defense (45%+ S/L/E/N, softcapped positional)
- Moderate resistance (20-30%)
- HP cap: ~2409
- Result: Defense-based tank, high damage

### Blaster (No secondary survivability set)
- Resistance cap: 75%
- Typically 0-20% defense from pool powers
- Typically 0-30% resistance from pool powers
- HP cap: ~1874
- Result: Glass cannon, relies on killing first

**Build Planning Impact**:
- Tanker: Stack resistance to 90% cap, HP bonuses
- Scrapper: Stack defense to 45% soft cap, DDR critical
- Blaster: Focus on damage cap (500%), minimal survivability

## Edge Cases and Special Mechanics

### 1. Temporary Power Cap Overrides

Some temporary powers ignore caps:
- Inspiration stacking can exceed caps temporarily
- Some event buffs ignore resistance caps
- Code handles this with special flags

### 2. PvP Caps

PvP has different caps:
- Defense has diminishing returns (no 45% soft cap)
- Resistance more valuable in PvP
- Damage caps may differ
- Healing caps exist in PvP

### 3. Kheldian Form Caps

Peacebringers/Warshades change caps when shapeshifting:
- Human form: Standard caps
- Dwarf form: Higher resistance cap (85%)
- Nova form: Standard caps (damage focused)

### 4. Incarnate Powers

Incarnate abilities can:
- Provide buffs that push to cap
- Some Incarnate powers ignore caps (special case)
- Destiny buffs are carefully balanced around caps

### 5. Cap Overflow Waste

Going over cap wastes power picks:
- If at 90% resistance, adding +10% resistance = 0 benefit
- Build planning must account for cap limits
- Some sets give multiple attributes to avoid waste

## Implementation in Mids Hero Web

### Database Schema

```sql
-- Archetype caps stored per archetype
CREATE TABLE archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    damage_cap FLOAT NOT NULL DEFAULT 4.0,    -- 400%
    res_cap FLOAT NOT NULL DEFAULT 0.75,      -- 75%
    hp_cap FLOAT NOT NULL DEFAULT 2000,
    recovery_cap FLOAT NOT NULL DEFAULT 5.0,  -- 500%
    regen_cap FLOAT NOT NULL DEFAULT 20.0,    -- 2000%
    recharge_cap FLOAT NOT NULL DEFAULT 5.0,  -- 500%
    perception_cap FLOAT NOT NULL DEFAULT 1153.0
);
```

### Python Calculation Code

```python
# backend/app/calculations/archetype_caps.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class ArchetypeCaps:
    """Archetype-specific caps for character attributes"""

    name: str
    damage_cap: float = 4.0        # 400% (base + 300% bonus)
    resistance_cap: float = 0.75   # 75%
    hp_cap: float = 2000.0
    recovery_cap: float = 5.0      # 500%
    regeneration_cap: float = 20.0 # 2000%
    recharge_cap: float = 5.0      # 500%
    perception_cap: float = 1153.0

    def apply_damage_cap(self, damage_bonus: float) -> float:
        """
        Apply damage cap to damage bonus

        Args:
            damage_bonus: Total damage bonus (base is separate)

        Returns:
            Capped damage bonus
        """
        # Damage cap includes base (1.0), so max bonus is cap - 1
        max_bonus = self.damage_cap - 1.0
        return min(damage_bonus, max_bonus)

    def apply_resistance_cap(self, resistance: float) -> float:
        """
        Apply resistance cap

        Args:
            resistance: Resistance value (0.0 to 1.0+)

        Returns:
            Capped resistance (0.0 to res_cap)
        """
        return min(resistance, self.resistance_cap)

    def apply_hp_cap(self, hp: float) -> float:
        """Apply HP cap"""
        return min(hp, self.hp_cap)

    def apply_recovery_cap(self, recovery_bonus: float) -> float:
        """
        Apply recovery cap

        Args:
            recovery_bonus: Recovery bonus as multiplier

        Returns:
            Capped recovery bonus
        """
        max_bonus = self.recovery_cap - 1.0
        return min(recovery_bonus, max_bonus)

    def apply_regeneration_cap(self, regen_bonus: float) -> float:
        """
        Apply regeneration cap

        Args:
            regen_bonus: Regeneration bonus as multiplier

        Returns:
            Capped regeneration bonus
        """
        max_bonus = self.regeneration_cap - 1.0
        return min(regen_bonus, max_bonus)

    def apply_recharge_cap(self, recharge_bonus: float) -> float:
        """
        Apply recharge cap

        Args:
            recharge_bonus: Recharge bonus as multiplier

        Returns:
            Capped recharge bonus
        """
        max_bonus = self.recharge_cap - 1.0
        return min(recharge_bonus, max_bonus)

    def is_at_cap(self, value: float, cap: float, tolerance: float = 0.01) -> bool:
        """
        Check if value is at cap (within tolerance)

        Args:
            value: Current value
            cap: Cap value
            tolerance: How close to cap counts as "at cap"

        Returns:
            True if at cap
        """
        return abs(value - cap) <= tolerance or value > cap


# Archetype cap definitions (from game data)
ARCHETYPE_CAPS: Dict[str, ArchetypeCaps] = {
    "Tanker": ArchetypeCaps(
        name="Tanker",
        damage_cap=4.0,
        resistance_cap=0.90,
        hp_cap=3534.0,
        recovery_cap=5.0,
        regeneration_cap=21.0,  # 2500% (21 - 1 = 20)
    ),
    "Scrapper": ArchetypeCaps(
        name="Scrapper",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=2409.0,
        recovery_cap=5.0,
        regeneration_cap=26.0,  # 3000% (26 - 1 = 25)
    ),
    "Blaster": ArchetypeCaps(
        name="Blaster",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=5.0,
        regeneration_cap=20.0,
    ),
    "Brute": ArchetypeCaps(
        name="Brute",
        damage_cap=7.75,
        resistance_cap=0.90,
        hp_cap=3212.0,
        recovery_cap=5.0,
        regeneration_cap=21.0,
    ),
    # ... other archetypes
}


def get_archetype_caps(archetype_name: str) -> ArchetypeCaps:
    """Get archetype caps by name"""
    return ARCHETYPE_CAPS.get(archetype_name, ArchetypeCaps(name=archetype_name))
```

### API Endpoint

```python
# backend/app/api/endpoints/archetypes.py

@router.get("/archetypes/{archetype_id}/caps")
async def get_archetype_caps(
    archetype_id: int,
    db: Session = Depends(get_db)
):
    """Get archetype cap values"""
    archetype = db.query(Archetype).filter(Archetype.id == archetype_id).first()
    if not archetype:
        raise HTTPException(status_code=404, detail="Archetype not found")

    return {
        "name": archetype.name,
        "caps": {
            "damage": {
                "value": archetype.damage_cap,
                "display": f"{int(archetype.damage_cap * 100)}%"
            },
            "resistance": {
                "value": archetype.res_cap,
                "display": f"{int(archetype.res_cap * 100)}%"
            },
            "hp": {
                "value": archetype.hp_cap,
                "display": f"{int(archetype.hp_cap)} HP"
            },
            "recovery": {
                "value": archetype.recovery_cap,
                "display": f"{int(archetype.recovery_cap * 100)}%"
            },
            "regeneration": {
                "value": archetype.regen_cap,
                "display": f"{int(archetype.regen_cap * 100)}%"
            },
            "recharge": {
                "value": archetype.recharge_cap,
                "display": f"{int(archetype.recharge_cap * 100)}%"
            }
        }
    }
```

## Dependencies

**Depends On**:
- Spec 16: Archetype Stats (Base archetype values)
- Spec 01: Power Effects Core (Effects that need capping)
- Spec 03: Power Buffs/Debuffs (Buff values that hit caps)

**Used By**:
- Spec 19: Build Totals Display (Show capped vs uncapped)
- Spec 09: Power Defense/Resistance (Resistance cap enforcement)
- Spec 08: Power Damage Calculation (Damage cap enforcement)
- Spec 32: Survivability Index (Capped values for EHP)
- All build calculation endpoints

## Testing Strategy

**Unit Tests**:
```python
def test_apply_resistance_cap_tanker():
    """Tanker resistance caps at 90%"""
    caps = ARCHETYPE_CAPS["Tanker"]
    assert caps.apply_resistance_cap(0.85) == 0.85  # Below cap
    assert caps.apply_resistance_cap(0.90) == 0.90  # At cap
    assert caps.apply_resistance_cap(0.95) == 0.90  # Over cap

def test_apply_resistance_cap_scrapper():
    """Scrapper resistance caps at 75%"""
    caps = ARCHETYPE_CAPS["Scrapper"]
    assert caps.apply_resistance_cap(0.70) == 0.70  # Below cap
    assert caps.apply_resistance_cap(0.75) == 0.75  # At cap
    assert caps.apply_resistance_cap(0.90) == 0.75  # Over cap (would be 90% on Tanker)

def test_apply_damage_cap_brute():
    """Brute damage caps at 775%"""
    caps = ARCHETYPE_CAPS["Brute"]
    # Damage cap is total (base + bonus), so max bonus is cap - 1
    assert caps.apply_damage_cap(5.0) == 5.0   # 600% bonus, below 675% max
    assert caps.apply_damage_cap(6.75) == 6.75 # 675% bonus, at cap
    assert caps.apply_damage_cap(7.0) == 6.75  # 700% bonus, over cap

def test_defense_soft_cap():
    """Defense has soft cap at 45%, no hard cap"""
    # Defense doesn't use archetype caps (no hard cap)
    # Just verify soft cap calculation
    defense = 0.45
    enemy_tohit = 0.50
    hit_chance = max(0.05, enemy_tohit - defense)
    assert hit_chance == 0.05  # Hit floor
```

**Integration Tests**:
- Compare capped values to MidsReborn for known builds
- Test builds at cap (Tanker with 90% resistance)
- Test builds over cap (show overflow correctly)
- Test builds well below cap (show room to grow)

## References

- **Related Specs**:
  - Spec 16: Archetype Stats
  - Spec 09: Power Defense/Resistance
  - Spec 08: Power Damage Calculation
  - Spec 19: Build Totals Display
  - Spec 32: Survivability Index
- **MidsReborn Files**:
  - `Core/Base/Data_Classes/Archetype.cs` - Cap properties
  - `clsToonX.cs` - Cap enforcement
  - `Core/Statistics.cs` - Capped calculation
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - Display
- **Game Documentation**:
  - City of Heroes Wiki - "Limits"
  - Paragon Wiki - "Damage Caps", "Resistance Caps"
  - City of Data - Cap formulas and values

---

**Document Status**: 🟢 Depth Complete - Comprehensive cap mechanics with source verification
**Implementation Status**: Not implemented (Python code examples provided)
**Last Updated**: 2025-11-11

---

# DEPTH COVERAGE - MILESTONE 3

## Section 1: Detailed Algorithm

### Complete Cap Application Algorithm

Archetype caps are applied as the **final step** in the character totals calculation pipeline, after all buffs, enhancements, and modifiers have been accumulated.

**Complete Calculation Flow**:
```
1. Base Values (from Archetype)
   ↓
2. Power Effects (from all active powers)
   ↓
3. Enhancement Bonuses (from slotted enhancements)
   ↓
4. Enhancement Diversification (ED caps per enhancement type)
   ↓
5. Set Bonuses (from IO sets)
   ↓
6. Global Modifiers (Incarnate abilities, temp powers)
   ↓
7. Archetype Modifiers (ATMod scaling - see Spec 16)
   ↓
8. PvP Diminishing Returns (if in PvP mode)
   ↓
9. ARCHETYPE CAPS ← This spec (final enforcement)
   ↓
10. TotalsCapped (actual in-game values)
```

### Cap Application Pseudocode

```python
def apply_archetype_caps(totals: CharacterTotals, archetype: Archetype) -> CharacterTotals:
    """
    Apply archetype-specific caps to all character attributes.

    This is the FINAL step in totals calculation - all values are
    computed, now we enforce maximum limits per archetype.

    Args:
        totals: Uncapped totals from all sources
        archetype: Character's archetype with cap definitions

    Returns:
        Capped totals (actual in-game values)
    """
    capped = totals.copy()

    # Damage buff cap (note: cap includes base 100%, so max bonus = cap - 1)
    # Example: 4.0 cap means 400% total = 100% base + 300% bonus max
    capped.damage_bonus = min(totals.damage_bonus, archetype.damage_cap - 1.0)

    # Resistance cap (applied per damage type)
    for damage_type in DamageType:
        capped.resistance[damage_type] = min(
            totals.resistance[damage_type],
            archetype.resistance_cap
        )

    # HP cap (absolute maximum hit points)
    if archetype.hp_cap > 0:  # Some ATs may have no cap (legacy/pet)
        capped.hp_max = min(totals.hp_max, archetype.hp_cap)
        # Absorb cannot exceed max HP
        capped.absorb = min(capped.absorb, capped.hp_max)

    # Recovery cap (endurance per second, cap includes base)
    capped.recovery_bonus = min(
        totals.recovery_bonus,
        archetype.recovery_cap - 1.0
    )

    # Regeneration cap (HP per second, cap includes base)
    capped.regeneration_bonus = min(
        totals.regeneration_bonus,
        archetype.regeneration_cap - 1.0
    )

    # Recharge cap (power recharge speed)
    capped.recharge_bonus = min(
        totals.recharge_bonus,
        archetype.recharge_cap - 1.0
    )

    # Perception cap (sight range in feet)
    capped.perception = min(totals.perception, archetype.perception_cap)

    # Movement caps (not archetype-specific, use global maxes)
    capped.run_speed = min(totals.run_speed, totals.max_run_speed)
    capped.jump_speed = min(totals.jump_speed, totals.max_jump_speed)
    capped.fly_speed = min(totals.fly_speed, totals.max_fly_speed)
    capped.jump_height = min(totals.jump_height, MAX_JUMP_HEIGHT)

    return capped
```

### Complete Archetype Cap Table

Based on analysis of MidsReborn `Archetype.cs` default values and game balance data:

| Archetype | Damage | Resistance | HP Cap | Regen | Recovery | Recharge | Perception |
|-----------|--------|------------|--------|-------|----------|----------|------------|
| **Tanker** | 400% | 90% | 3534 | 2500% | 800% | 500% | 1153 ft |
| **Brute** | 775% | 90% | 3212 | 2500% | 800% | 500% | 1153 ft |
| **Scrapper** | 500% | 75% | 2409 | 3000% | 800% | 500% | 1153 ft |
| **Stalker** | 500% | 75% | 2091 | 3000% | 800% | 500% | 1153 ft |
| **Blaster** | 500% | 75% | 1874 | 2000% | 800% | 500% | 1153 ft |
| **Sentinel** | 500% | 75% | 2409 | 2000% | 800% | 500% | 1153 ft |
| **Defender** | 400% | 75% | 1874 | 2000% | 1000% | 500% | 1153 ft |
| **Controller** | 400% | 75% | 1874 | 2000% | 1200% | 500% | 1153 ft |
| **Corruptor** | 500% | 75% | 1874 | 2000% | 800% | 500% | 1153 ft |
| **Dominator** | 400% | 75% | 1874 | 2000% | 1200% | 500% | 1153 ft |
| **Mastermind** | 400% | 75% | 1874 | 2000% | 1200% | 500% | 1153 ft |
| **Peacebringer** | 400% | 85% | 2250* | 2000% | 800% | 500% | 1153 ft |
| **Warshade** | 400% | 85% | 2250* | 2000% | 800% | 500% | 1153 ft |

*Kheldian HP caps vary by form (Human/Dwarf/Nova)

**Key Insights**:
- **Brute unique**: Only AT with 775% damage cap (due to Fury mechanic)
- **Resistance tiers**: 90% (Tanker/Brute), 85% (Kheldians), 75% (all others)
- **Regen tiers**: 3000% (Scrapper/Stalker), 2500% (Tanker/Brute), 2000% (all others)
- **Recovery tiers**: 1200% (Controller/Dominator/MM), 1000% (Defender), 800% (all others)
- **Recharge/Perception**: Universal caps (500% recharge, 1153 ft perception)

### Defense "Cap" - Soft Cap vs Hard Cap

Defense is **unique** among attributes - it has NO archetype-specific hard cap in gameplay, only a "soft cap" based on ToHit mechanics.

**Soft Cap Calculation**:
```python
def calculate_hit_chance(enemy_tohit: float, defense: float) -> float:
    """
    Calculate final hit chance after defense.

    The 5% floor creates the "soft cap" at 45% defense.
    """
    hit_chance = enemy_tohit - defense

    # Apply ToHit floor (cannot go below 5%)
    return max(0.05, hit_chance)

# Examples:
# Even-level enemy (50% base ToHit):
calculate_hit_chance(0.50, 0.00)  # = 0.50 (50% hit chance)
calculate_hit_chance(0.50, 0.20)  # = 0.30 (30% hit chance)
calculate_hit_chance(0.50, 0.45)  # = 0.05 (5% hit chance) ← SOFT CAP
calculate_hit_chance(0.50, 0.60)  # = 0.05 (5% hit chance - floor)
calculate_hit_chance(0.50, 0.90)  # = 0.05 (5% hit chance - floor)

# Why 45% is the soft cap:
# 50% base - 45% defense = 5% → hit floor reached
# Additional defense provides NO benefit vs even-level enemies
# BUT helps vs +level enemies or enemies with +ToHit buffs
```

**MidsReborn Display Caps** (not gameplay caps):
```python
# From MidsReborn source - these are UI/display limits only
DEFENSE_DISPLAY_CAPS = {
    "Tanker": 2.25,    # 225%
    "Brute": 2.25,     # 225%
    "Scrapper": 2.00,  # 200%
    "Stalker": 2.00,   # 200%
    "Peacebringer": 2.00,
    "Warshade": 2.00,
    "Others": 1.75     # 175%
}
# These caps do NOT apply in-game, only for Mids display purposes
```

### Cap Stacking Order Example

Complete example showing how a Tanker's resistance accumulates and hits cap:

```python
# Example: Tanker with Invulnerability calculating Smashing resistance

# Step 1: Base value (all characters start at 0%)
smashing_res = 0.0

# Step 2: Power effects (Invincibility power)
smashing_res += 0.075  # 7.5% base resistance
# Result: 0.075 (7.5%)

# Step 3: Enhancement (3x Resistance SO at 42.4% each)
enhancement_bonus = 3 * 0.424  # 127.2% enhancement
# Apply ED (diminishing returns after 100%)
ed_enhanced = apply_ed(enhancement_bonus)  # ~105% after ED
smashing_res_enhanced = smashing_res * (1 + ed_enhanced)
smashing_res = smashing_res_enhanced
# Result: 0.154 (15.4%)

# Step 4: More powers (Temp Invulnerability, Tough, etc.)
smashing_res += 0.225  # Temp Invuln (enhanced)
smashing_res += 0.158  # Tough (enhanced)
smashing_res += 0.195  # Resist Physical Damage (enhanced)
smashing_res += 0.135  # Resist Elements (partial)
# Result: 0.867 (86.7%)

# Step 5: Set bonuses (from multiple IO sets)
smashing_res += 0.06   # 6% from set bonuses
# Result: 0.927 (92.7%)

# Step 6: Team buffs (Sonic Dispersion from teammate)
smashing_res += 0.15   # 15% from team buff
# Result: 1.077 (107.7%) ← OVER CAP!

# Step 7: Archetype cap enforcement (THIS SPEC)
smashing_res = min(smashing_res, 0.90)  # Tanker cap
# FINAL: 0.90 (90%) - capped

# Wasted bonus: 0.177 (17.7%) - buffs that provide no benefit
```

## Section 2: C# Implementation Details

### Source File: Archetype.cs

**Location**: `/MidsReborn/Core/Base/Data_Classes/Archetype.cs`

**Key Properties** (lines 23-44):
```csharp
public class Archetype
{
    // Cap properties (stored as multipliers, not percentages)
    public float DamageCap { get; set; }      // e.g., 4.0 = 400%
    public float ResCap { get; set; }         // e.g., 0.75 = 75%
    public float HPCap { get; set; }          // e.g., 3534.0 HP
    public float RecoveryCap { get; set; }    // e.g., 5.0 = 500%
    public float RegenCap { get; set; }       // e.g., 20.0 = 2000%
    public float RechargeCap { get; set; }    // e.g., 5.0 = 500%
    public float PerceptionCap { get; set; }  // e.g., 1153.0 feet

    // Default constructor (lines 21-58)
    public Archetype()
    {
        // Default values (overridden per archetype in database)
        DamageCap = 4f;          // 400% damage (typical)
        ResCap = 0.9f;           // 90% resistance (default, actual varies)
        HPCap = 5000f;           // 5000 HP (default, actual varies)
        RecoveryCap = 5f;        // 500% recovery
        RegenCap = 20f;          // 2000% regeneration (default, actual varies)
        RechargeCap = 5f;        // 500% recharge (universal)
        PerceptionCap = 1153f;   // ~1153 feet (universal)

        BaseRecovery = 1.67f;    // 1.67 end/sec base
        BaseRegen = 1f;          // 100% base regen
        BaseThreat = 1f;         // 1.0 threat multiplier
        Playable = true;
        Hitpoints = 5000;        // Base HP (varies by AT)
    }
}
```

**Binary Serialization** (lines 89-115):
```csharp
// Archetype data is loaded from binary .mhd file
public Archetype(BinaryReader reader) : this()
{
    DisplayName = reader.ReadString();
    Hitpoints = reader.ReadInt32();
    HPCap = reader.ReadSingle();              // Line 93
    DescLong = reader.ReadString();
    ResCap = reader.ReadSingle();             // Line 95
    // ... origin array ...
    ClassName = reader.ReadString();
    ClassType = (Enums.eClassType)reader.ReadInt32();
    Column = reader.ReadInt32();
    DescShort = reader.ReadString();
    PrimaryGroup = reader.ReadString();
    SecondaryGroup = reader.ReadString();
    Playable = reader.ReadBoolean();
    RechargeCap = reader.ReadSingle();        // Line 107
    DamageCap = reader.ReadSingle();          // Line 108
    RecoveryCap = reader.ReadSingle();        // Line 109
    RegenCap = reader.ReadSingle();           // Line 110
    BaseRecovery = reader.ReadSingle();
    BaseRegen = reader.ReadSingle();
    BaseThreat = reader.ReadSingle();
    PerceptionCap = reader.ReadSingle();      // Line 114
}
```

**Key Insight**: Cap values are stored in binary database file (`EClasses.mhd`) and loaded at startup. The order in binary format is critical for compatibility.

### Source File: clsToonX.cs (Cap Application)

**Location**: `/MidsReborn/clsToonX.cs`

**Cap Enforcement Method** (approximate line 2500+):
```csharp
private void CalculateTotals()
{
    // ... (steps 1-8: accumulate all bonuses) ...

    // Apply PvP diminishing returns (if in PvP mode)
    ApplyPvpDr();

    // Copy uncapped totals
    TotalsCapped.Assign(Totals);

    // ARCHETYPE CAP ENFORCEMENT (Step 9)
    // ===================================

    // Damage cap (subtract 1 because base damage is separate)
    TotalsCapped.BuffDam = Math.Min(
        TotalsCapped.BuffDam,
        Archetype.DamageCap - 1
    );

    // Recharge cap (subtract 1 because base recharge is separate)
    TotalsCapped.BuffHaste = Math.Min(
        TotalsCapped.BuffHaste,
        Archetype.RechargeCap - 1
    );

    // Regeneration cap (subtract 1 because base regen is separate)
    TotalsCapped.HPRegen = Math.Min(
        TotalsCapped.HPRegen,
        Archetype.RegenCap - 1
    );

    // Recovery cap (subtract 1 because base recovery is separate)
    TotalsCapped.EndRec = Math.Min(
        TotalsCapped.EndRec,
        Archetype.RecoveryCap - 1
    );

    // Resistance cap (per damage type)
    for (var index = 0; index < TotalsCapped.Res.Length; index++)
    {
        TotalsCapped.Res[index] = Math.Min(
            TotalsCapped.Res[index],
            Archetype.ResCap
        );
    }

    // HP cap (if defined for archetype)
    if (Archetype.HPCap > 0)
    {
        TotalsCapped.HPMax = Math.Min(
            TotalsCapped.HPMax,
            Archetype.HPCap
        );

        // Absorb cannot exceed max HP
        TotalsCapped.Absorb = Math.Min(
            TotalsCapped.Absorb,
            TotalsCapped.HPMax
        );
    }

    // Movement caps (global, not archetype-specific)
    TotalsCapped.RunSpd = Math.Min(
        TotalsCapped.RunSpd,
        Totals.MaxRunSpd
    );
    TotalsCapped.JumpSpd = Math.Min(
        TotalsCapped.JumpSpd,
        Totals.MaxJumpSpd
    );
    TotalsCapped.FlySpd = Math.Min(
        TotalsCapped.FlySpd,
        Totals.MaxFlySpd
    );
    TotalsCapped.JumpHeight = Math.Min(
        TotalsCapped.JumpHeight,
        DatabaseAPI.ServerData.MaxJumpHeight  // 300 feet
    );

    // Perception cap
    TotalsCapped.Perception = Math.Min(
        TotalsCapped.Perception,
        Archetype.PerceptionCap
    );
}
```

**Critical Implementation Notes**:

1. **Subtract 1 for "bonus" caps**: Damage, Recharge, Regen, Recovery caps include base value (100%), so max bonus = cap - 1.0
   - Example: `DamageCap = 4.0` → max bonus = 3.0 (300%) + 1.0 base = 4.0 total

2. **Resistance uses direct cap**: Resistance cap is the absolute value, not bonus
   - Example: `ResCap = 0.75` → 75% max resistance (no base to subtract)

3. **HP cap is absolute**: HP cap is the total HP value, includes base HP
   - Example: `HPCap = 2409` → 2409 HP max (Scrapper level 50 cap)

4. **Absorb limited to HP**: Absorb (temporary HP) cannot exceed max HP cap

5. **Defense has NO cap**: Defense is not capped in this method (soft cap is from ToHit floor)

### Source File: frmEditArchetype.cs (Editor)

**Location**: `/MidsReborn/Forms/OptionsMenuItems/DbEditor/frmEditArchetype.cs`

**Display Format** (lines 240-244):
```csharp
// Caps are stored as multipliers, displayed as percentages
txtResCap.Text = Convert.ToString(
    MyAT.ResCap * 100f,          // 0.75 → 75
    CultureInfo.InvariantCulture
);
txtDamCap.Text = Convert.ToString(
    MyAT.DamageCap * 100f,       // 4.0 → 400
    CultureInfo.InvariantCulture
);
```

**Save Format** (lines 134-153):
```csharp
// User enters percentages, stored as multipliers
var num6 = Convert.ToSingle(txtResCap.Text);  // Read "75"
if (num6 < 1.0)
    num6 = 1f;
MyAT.ResCap = num6 / 100f;  // Store as 0.75

var num7 = Convert.ToSingle(txtDamCap.Text);  // Read "400"
if (num7 < 1.0)
    num7 = 1f;
MyAT.DamageCap = num7 / 100f;  // Store as 4.0

var num10 = Convert.ToSingle(txtRegCap.Text);  // Read "3000"
if (num10 < 1.0)
    num10 = 1f;
MyAT.RegenCap = num10 / 100f;  // Store as 30.0 (but default is 20.0)
```

### Edge Cases Found in Source

1. **Legacy HP Cap Check** (`if (Archetype.HPCap > 0)`):
   - Older/pet archetypes may have HPCap = 0 (no cap)
   - Modern archetypes always have HPCap defined

2. **Percentage Display Division**:
   - All caps stored as multipliers (4.0, 0.75, 20.0)
   - UI divides/multiplies by 100 for display
   - Regen/Recovery: 20.0 stored → 2000% displayed

3. **Recharge Cap Confusion**:
   - RechargeCap = 5.0 means 500% recharge SPEED
   - This translates to ~80% recharge TIME reduction
   - Formula: `actual_recharge = base / (1 + bonus)`
   - 400% bonus → actual = base / 5.0 = 20% of original time

4. **PvP Mode Special Handling**:
   - `ApplyPvpDr()` called BEFORE cap enforcement
   - PvP diminishing returns reduce uncapped values
   - Then archetype caps applied to DR-reduced values
   - Order matters: DR first, then caps

## Section 3: Database Schema

### Primary Table: `archetypes`

The `archetypes` table already stores archetype data from Spec 16, but needs cap columns added:

```sql
-- Extend existing archetypes table with cap columns
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS damage_cap FLOAT NOT NULL DEFAULT 4.0;
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS resistance_cap FLOAT NOT NULL DEFAULT 0.75;
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS hp_cap FLOAT NOT NULL DEFAULT 2000.0;
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS recovery_cap FLOAT NOT NULL DEFAULT 5.0;
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS regeneration_cap FLOAT NOT NULL DEFAULT 20.0;
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS recharge_cap FLOAT NOT NULL DEFAULT 5.0;
ALTER TABLE archetypes ADD COLUMN IF NOT EXISTS perception_cap FLOAT NOT NULL DEFAULT 1153.0;

-- Complete table structure
CREATE TABLE IF NOT EXISTS archetypes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    class_name VARCHAR(50) NOT NULL UNIQUE,  -- Internal name (e.g., "Class_Tanker")
    display_name VARCHAR(50) NOT NULL,       -- Display name (e.g., "Tanker")
    class_type VARCHAR(20) NOT NULL,         -- Hero, Villain, HeroEpic, VillainEpic
    playable BOOLEAN NOT NULL DEFAULT true,

    -- Base stats (from Spec 16)
    base_hit_points INTEGER NOT NULL,
    base_recovery FLOAT NOT NULL DEFAULT 1.67,
    base_regeneration FLOAT NOT NULL DEFAULT 1.0,
    base_threat FLOAT NOT NULL DEFAULT 1.0,

    -- Archetype caps (this spec)
    damage_cap FLOAT NOT NULL DEFAULT 4.0,         -- 400%
    resistance_cap FLOAT NOT NULL DEFAULT 0.75,    -- 75%
    hp_cap FLOAT NOT NULL DEFAULT 2000.0,
    recovery_cap FLOAT NOT NULL DEFAULT 5.0,       -- 500%
    regeneration_cap FLOAT NOT NULL DEFAULT 20.0,  -- 2000%
    recharge_cap FLOAT NOT NULL DEFAULT 5.0,       -- 500%
    perception_cap FLOAT NOT NULL DEFAULT 1153.0,  -- feet

    -- Metadata
    description_short TEXT,
    description_long TEXT,
    primary_group VARCHAR(50),    -- e.g., "Tanker_Def"
    secondary_group VARCHAR(50),  -- e.g., "Tanker_Res"
    column_position INTEGER,      -- UI display order

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookups
CREATE INDEX idx_archetypes_name ON archetypes(name);
CREATE INDEX idx_archetypes_class_name ON archetypes(class_name);
CREATE INDEX idx_archetypes_playable ON archetypes(playable) WHERE playable = true;
```

### Reference Table: `attribute_caps` (Optional)

For extensibility, create a separate table for attribute-specific caps:

```sql
-- Optional: Separate table for fine-grained cap control
CREATE TABLE IF NOT EXISTS attribute_caps (
    id SERIAL PRIMARY KEY,
    archetype_id INTEGER NOT NULL REFERENCES archetypes(id) ON DELETE CASCADE,
    attribute_type VARCHAR(50) NOT NULL,  -- 'damage', 'resistance', 'hp', etc.
    cap_value FLOAT NOT NULL,
    pvp_cap_value FLOAT,                  -- Different cap in PvP mode (future)
    notes TEXT,

    UNIQUE(archetype_id, attribute_type)
);

-- Index for fast cap lookups
CREATE INDEX idx_attribute_caps_archetype ON attribute_caps(archetype_id);
CREATE INDEX idx_attribute_caps_attribute ON attribute_caps(attribute_type);
```

### Seed Data: Complete Archetype Caps

```sql
-- Seed data with exact cap values (from MidsReborn defaults and game data)
INSERT INTO archetypes (
    name, class_name, display_name, class_type, playable,
    base_hit_points, base_recovery, base_regeneration, base_threat,
    damage_cap, resistance_cap, hp_cap, recovery_cap, regeneration_cap,
    recharge_cap, perception_cap,
    description_short, primary_group, secondary_group
) VALUES
    -- Tanker
    ('Tanker', 'Class_Tanker', 'Tanker', 'Hero', true,
     1874, 1.67, 1.0, 4.0,                    -- base stats (threat = 4x)
     4.0, 0.90, 3534.0, 5.0, 21.0, 5.0, 1153.0,  -- caps (21.0 = 2500% regen)
     'Tough melee combatant with exceptional survivability',
     'Tanker_Def', 'Tanker_Res'),

    -- Brute
    ('Brute', 'Class_Brute', 'Brute', 'Villain', true,
     1499, 1.67, 1.0, 2.5,                    -- base stats
     7.75, 0.90, 3212.0, 5.0, 21.0, 5.0, 1153.0,  -- caps (775% damage!)
     'Fury-driven melee warrior with high damage potential',
     'Brute_Def', 'Brute_Res'),

    -- Scrapper
    ('Scrapper', 'Class_Scrapper', 'Scrapper', 'Hero', true,
     1338, 1.67, 1.0, 1.0,                    -- base stats
     5.0, 0.75, 2409.0, 5.0, 31.0, 5.0, 1153.0,  -- caps (31.0 = 3000% regen)
     'Balanced melee combatant with high critical hit rate',
     'Scrapper_Def', 'Scrapper_Res'),

    -- Stalker
    ('Stalker', 'Class_Stalker', 'Stalker', 'Villain', true,
     1204, 1.67, 1.0, 0.75,                   -- base stats
     5.0, 0.75, 2091.0, 5.0, 31.0, 5.0, 1153.0,  -- caps
     'Stealthy assassin with burst damage from Hide',
     'Stalker_Def', 'Stalker_Res'),

    -- Blaster
    ('Blaster', 'Class_Blaster', 'Blaster', 'Hero', true,
     1070, 1.67, 1.0, 1.0,                    -- base stats
     5.0, 0.75, 1874.0, 5.0, 20.0, 5.0, 1153.0,  -- caps
     'Ranged damage specialist with devastating attacks',
     'Blaster_Ranged', 'Blaster_Support'),

    -- Defender
    ('Defender', 'Class_Defender', 'Defender', 'Hero', true,
     1070, 1.67, 1.0, 1.0,                    -- base stats
     4.0, 0.75, 1874.0, 10.0, 20.0, 5.0, 1153.0,  -- caps (1000% recovery)
     'Team support specialist with powerful buffs and heals',
     'Defender_Buff', 'Defender_Ranged'),

    -- Controller
    ('Controller', 'Class_Controller', 'Controller', 'Hero', true,
     1070, 1.67, 1.0, 1.0,                    -- base stats
     4.0, 0.75, 1874.0, 12.0, 20.0, 5.0, 1153.0,  -- caps (1200% recovery!)
     'Battlefield control specialist with holds and immobilizes',
     'Controller_Control', 'Controller_Buff'),

    -- Corruptor
    ('Corruptor', 'Class_Corruptor', 'Corruptor', 'Villain', true,
     1070, 1.67, 1.0, 1.0,                    -- base stats
     5.0, 0.75, 1874.0, 5.0, 20.0, 5.0, 1153.0,   -- caps
     'Ranged damage dealer with secondary support powers',
     'Corruptor_Ranged', 'Corruptor_Buff'),

    -- Dominator
    ('Dominator', 'Class_Dominator', 'Dominator', 'Villain', true,
     1070, 1.67, 1.0, 1.0,                    -- base stats
     4.0, 0.75, 1874.0, 12.0, 20.0, 5.0, 1153.0,  -- caps (1200% recovery)
     'Control specialist with assault secondary and Domination mechanic',
     'Dominator_Control', 'Dominator_Assault'),

    -- Mastermind
    ('Mastermind', 'Class_Mastermind', 'Mastermind', 'Villain', true,
     803, 1.67, 1.0, 0.5,                     -- base stats (lowest HP/threat)
     4.0, 0.75, 1874.0, 12.0, 20.0, 5.0, 1153.0,  -- caps (1200% recovery)
     'Pet commander with multiple henchmen and support powers',
     'Mastermind_Pets', 'Mastermind_Buff'),

    -- Sentinel
    ('Sentinel', 'Class_Sentinel', 'Sentinel', 'Hero', true,
     1338, 1.67, 1.0, 1.0,                    -- base stats
     5.0, 0.75, 2409.0, 5.0, 20.0, 5.0, 1153.0,   -- caps
     'Ranged damage dealer with defensive secondary (Homecoming)',
     'Sentinel_Ranged', 'Sentinel_Def'),

    -- Peacebringer
    ('Peacebringer', 'Class_Peacebringer', 'Peacebringer', 'HeroEpic', true,
     1017, 1.67, 1.0, 1.0,                    -- base stats (form-dependent)
     4.0, 0.85, 2250.0, 5.0, 20.0, 5.0, 1153.0,   -- caps (85% res!)
     'Kheldian shapeshifter with Human/Dwarf/Nova forms',
     'Kheldian', 'Kheldian'),

    -- Warshade
    ('Warshade', 'Class_Warshade', 'Warshade', 'HeroEpic', true,
     1017, 1.67, 1.0, 1.0,                    -- base stats (form-dependent)
     4.0, 0.85, 2250.0, 5.0, 20.0, 5.0, 1153.0,   -- caps (85% res!)
     'Kheldian shapeshifter with corpse-powered abilities',
     'Kheldian', 'Kheldian');

-- Insert attribute caps for special cases
INSERT INTO attribute_caps (archetype_id, attribute_type, cap_value, notes)
SELECT id, 'defense_display', 2.25, 'Mids display cap (not gameplay cap)'
FROM archetypes WHERE name IN ('Tanker', 'Brute');

INSERT INTO attribute_caps (archetype_id, attribute_type, cap_value, notes)
SELECT id, 'defense_display', 2.00, 'Mids display cap (not gameplay cap)'
FROM archetypes WHERE name IN ('Scrapper', 'Stalker', 'Peacebringer', 'Warshade');

INSERT INTO attribute_caps (archetype_id, attribute_type, cap_value, notes)
SELECT id, 'defense_display', 1.75, 'Mids display cap (not gameplay cap)'
FROM archetypes WHERE name NOT IN ('Tanker', 'Brute', 'Scrapper', 'Stalker', 'Peacebringer', 'Warshade');
```

### Indexes and Constraints

```sql
-- Ensure cap values are within reasonable ranges
ALTER TABLE archetypes ADD CONSTRAINT chk_damage_cap
    CHECK (damage_cap >= 1.0 AND damage_cap <= 10.0);

ALTER TABLE archetypes ADD CONSTRAINT chk_resistance_cap
    CHECK (resistance_cap >= 0.0 AND resistance_cap <= 1.0);

ALTER TABLE archetypes ADD CONSTRAINT chk_hp_cap
    CHECK (hp_cap >= 0.0 AND hp_cap <= 10000.0);

ALTER TABLE archetypes ADD CONSTRAINT chk_recovery_cap
    CHECK (recovery_cap >= 1.0 AND recovery_cap <= 50.0);

ALTER TABLE archetypes ADD CONSTRAINT chk_regeneration_cap
    CHECK (regeneration_cap >= 1.0 AND regeneration_cap <= 100.0);

ALTER TABLE archetypes ADD CONSTRAINT chk_recharge_cap
    CHECK (recharge_cap >= 1.0 AND recharge_cap <= 10.0);

-- Create view for easy cap lookups
CREATE OR REPLACE VIEW archetype_caps_display AS
SELECT
    id,
    name,
    display_name,
    (damage_cap * 100)::INTEGER AS damage_cap_pct,
    (resistance_cap * 100)::INTEGER AS resistance_cap_pct,
    hp_cap,
    (recovery_cap * 100)::INTEGER AS recovery_cap_pct,
    (regeneration_cap * 100)::INTEGER AS regeneration_cap_pct,
    (recharge_cap * 100)::INTEGER AS recharge_cap_pct,
    perception_cap
FROM archetypes
WHERE playable = true
ORDER BY class_type, name;
```

## Section 4: Test Cases

### Test Case 1: Tanker Resistance Cap (90%)

```python
def test_tanker_resistance_cap():
    """Tanker resistance caps at 90%, highest in game"""
    tanker = get_archetype("Tanker")

    # Build with high resistance (Invulnerability + buffs)
    totals = CharacterTotals()
    totals.resistance[DamageType.SMASHING] = 0.85  # 85% from powers
    totals.resistance[DamageType.LETHAL] = 0.85

    # Apply caps
    capped = apply_archetype_caps(totals, tanker)

    # Below cap - should be unchanged
    assert capped.resistance[DamageType.SMASHING] == 0.85
    assert capped.resistance[DamageType.LETHAL] == 0.85

    # Add team buff pushing over cap
    totals.resistance[DamageType.SMASHING] = 1.05  # 105% (over cap!)
    capped = apply_archetype_caps(totals, tanker)

    # Should be capped at 90%
    assert capped.resistance[DamageType.SMASHING] == 0.90
    assert capped.resistance[DamageType.LETHAL] == 0.85  # Still below
```

### Test Case 2: Scrapper Resistance Cap (75%)

```python
def test_scrapper_resistance_cap():
    """Scrapper resistance caps at 75%, lower than Tanker"""
    scrapper = get_archetype("Scrapper")

    # Same 85% resistance that was fine for Tanker
    totals = CharacterTotals()
    totals.resistance[DamageType.SMASHING] = 0.85

    capped = apply_archetype_caps(totals, scrapper)

    # Scrapper caps at 75%, so 85% gets reduced
    assert capped.resistance[DamageType.SMASHING] == 0.75

    # Verify 15% waste (85% - 75% cap = 10% wasted)
    wasted = totals.resistance[DamageType.SMASHING] - capped.resistance[DamageType.SMASHING]
    assert wasted == 0.10  # 10% resistance provides no benefit
```

### Test Case 3: Brute Damage Cap (775%)

```python
def test_brute_damage_cap():
    """Brute has unique 775% damage cap (highest in game)"""
    brute = get_archetype("Brute")

    # Brute with high Fury + buffs
    totals = CharacterTotals()
    totals.damage_bonus = 5.0  # 500% bonus (600% total with base)

    capped = apply_archetype_caps(totals, brute)

    # Below cap (775% = 7.75 - 1 = 6.75 max bonus)
    assert capped.damage_bonus == 5.0

    # At Fury cap with team buffs
    totals.damage_bonus = 7.0  # 700% bonus (800% total - over cap!)
    capped = apply_archetype_caps(totals, brute)

    # Should cap at 6.75 (675% bonus + 100% base = 775% total)
    assert capped.damage_bonus == 6.75
```

### Test Case 4: Blaster Damage Cap (500%)

```python
def test_blaster_damage_cap():
    """Blaster caps at 500%, much lower than Brute"""
    blaster = get_archetype("Blaster")

    # Blaster with full buffs
    totals = CharacterTotals()
    totals.damage_bonus = 5.0  # 500% bonus (600% total)

    capped = apply_archetype_caps(totals, blaster)

    # Blaster caps at 500% total = 5.0 - 1 = 4.0 max bonus
    assert capped.damage_bonus == 4.0

    # Massive waste compared to if this were a Brute
    assert totals.damage_bonus - capped.damage_bonus == 1.0  # 100% wasted
```

### Test Case 5: Defense Soft Cap (45%)

```python
def test_defense_soft_cap():
    """Defense has soft cap at 45% (vs even-level enemies)"""
    # Defense is NOT capped by archetype, but by ToHit floor

    # Even-level enemy (50% base ToHit)
    enemy_tohit = 0.50

    # Test various defense values
    test_cases = [
        (0.00, 0.50),   # 0% def → 50% hit chance
        (0.20, 0.30),   # 20% def → 30% hit chance
        (0.45, 0.05),   # 45% def → 5% hit chance (SOFT CAP)
        (0.60, 0.05),   # 60% def → 5% hit chance (floor)
        (0.90, 0.05),   # 90% def → 5% hit chance (floor)
    ]

    for defense, expected_hit_chance in test_cases:
        hit_chance = max(0.05, enemy_tohit - defense)
        assert hit_chance == expected_hit_chance

    # Key insight: defense past 45% provides NO benefit vs even-level
    # BUT helps vs +level enemies or enemies with +ToHit buffs
```

### Test Case 6: Defense vs Higher Level Enemies

```python
def test_defense_vs_higher_level():
    """Defense past soft cap helps vs higher-level enemies"""

    # +1 level enemy (55% ToHit)
    enemy_tohit_plus1 = 0.55

    # 45% defense (soft cap vs even-level)
    defense_soft_cap = 0.45
    hit_chance_at_soft_cap = max(0.05, enemy_tohit_plus1 - defense_soft_cap)
    assert hit_chance_at_soft_cap == 0.10  # 10% hit chance

    # 55% defense (over soft cap)
    defense_over_cap = 0.55
    hit_chance_over_cap = max(0.05, enemy_tohit_plus1 - defense_over_cap)
    assert hit_chance_over_cap == 0.05  # Back to floor

    # Extra defense DOES help vs higher-level enemies!
    benefit = hit_chance_at_soft_cap - hit_chance_over_cap
    assert benefit == 0.05  # 5% fewer hits with extra defense
```

### Test Case 7: Scrapper Regeneration Cap (3000%)

```python
def test_scrapper_regeneration_cap():
    """Scrapper/Stalker have highest regen cap at 3000%"""
    scrapper = get_archetype("Scrapper")

    # Willpower Scrapper with Heavy regen slotting
    totals = CharacterTotals()
    totals.regeneration_bonus = 25.0  # 2500% bonus

    capped = apply_archetype_caps(totals, scrapper)

    # Below cap (3000% = 31.0 - 1 = 30.0 max bonus)
    assert capped.regeneration_bonus == 25.0

    # With team buffs (Regeneration Aura)
    totals.regeneration_bonus = 32.0  # 3200% bonus
    capped = apply_archetype_caps(totals, scrapper)

    # Should cap at 30.0 (3000%)
    assert capped.regeneration_bonus == 30.0
```

### Test Case 8: Tanker Regeneration Cap (2500%)

```python
def test_tanker_regeneration_cap():
    """Tanker has lower regen cap than Scrapper (2500% vs 3000%)"""
    tanker = get_archetype("Tanker")

    # Same 2500% regen bonus as Scrapper test
    totals = CharacterTotals()
    totals.regeneration_bonus = 25.0

    capped = apply_archetype_caps(totals, tanker)

    # Tanker caps at 2500% (21.0 - 1 = 20.0)
    # So 25.0 gets reduced to 20.0
    assert capped.regeneration_bonus == 20.0

    # 500% regen wasted (difference from Scrapper cap)
    assert totals.regeneration_bonus - capped.regeneration_bonus == 5.0
```

### Test Case 9: Controller Recovery Cap (1200%)

```python
def test_controller_recovery_cap():
    """Controller/Dominator/MM have highest recovery cap (1200%)"""
    controller = get_archetype("Controller")

    # Heavy endurance build with Physical Perfection + Performance Shifter procs
    totals = CharacterTotals()
    totals.recovery_bonus = 10.0  # 1000% bonus

    capped = apply_archetype_caps(totals, controller)

    # Below cap (1200% = 12.0 - 1 = 11.0 max bonus)
    assert capped.recovery_bonus == 10.0

    # With all recovery bonuses
    totals.recovery_bonus = 12.0  # 1200% bonus (at cap)
    capped = apply_archetype_caps(totals, controller)

    # Should cap at 11.0 (1200% total)
    assert capped.recovery_bonus == 11.0
```

### Test Case 10: Defender Recovery Cap (1000%)

```python
def test_defender_recovery_cap():
    """Defender has lower recovery cap than Controller (1000% vs 1200%)"""
    defender = get_archetype("Defender")

    # Same 1000% recovery as Controller test
    totals = CharacterTotals()
    totals.recovery_bonus = 10.0

    capped = apply_archetype_caps(totals, defender)

    # Defender caps at 1000% (10.0 - 1 = 9.0 max bonus)
    # So 10.0 bonus gets reduced to 9.0
    assert capped.recovery_bonus == 9.0
```

### Test Case 11: Over-Cap Values (Waste Calculation)

```python
def test_over_cap_waste():
    """Calculate how much bonus is wasted when over cap"""
    blaster = get_archetype("Blaster")

    # Blaster with massive buffs from team (Fulcrum Shift stack)
    totals = CharacterTotals()
    totals.damage_bonus = 6.0  # 600% bonus (700% total)

    capped = apply_archetype_caps(totals, blaster)

    # Blaster caps at 400% bonus (5.0 - 1 = 4.0)
    assert capped.damage_bonus == 4.0

    # Calculate waste
    wasted_bonus = totals.damage_bonus - capped.damage_bonus
    assert wasted_bonus == 2.0  # 200% damage bonus provides NO benefit

    wasted_percentage = (wasted_bonus / totals.damage_bonus) * 100
    assert wasted_percentage == pytest.approx(33.33, rel=0.01)  # ~33% wasted
```

### Test Case 12: HP Cap with Absorb

```python
def test_hp_cap_with_absorb():
    """HP cap limits both max HP and absorb shield"""
    scrapper = get_archetype("Scrapper")

    # Scrapper with massive +MaxHP bonuses
    totals = CharacterTotals()
    totals.hp_max = 2500.0  # Over cap (Scrapper cap is 2409)
    totals.absorb = 500.0   # Absorb shield

    capped = apply_archetype_caps(totals, scrapper)

    # HP capped at archetype limit
    assert capped.hp_max == 2409.0

    # Absorb also limited to max HP
    assert capped.absorb == min(500.0, capped.hp_max)
    assert capped.absorb == 500.0  # Still valid

    # Test absorb exceeding HP cap
    totals.absorb = 3000.0  # Huge absorb shield
    capped = apply_archetype_caps(totals, scrapper)

    # Absorb cannot exceed max HP
    assert capped.absorb == capped.hp_max
    assert capped.absorb == 2409.0
```

### Test Case 13: PvE vs PvP Caps (Future)

```python
def test_pve_vs_pvp_caps():
    """
    PvP has different cap mechanics (future implementation)

    Note: Current implementation does not have separate PvP caps,
    but PvP diminishing returns are applied BEFORE archetype caps.
    """
    tanker = get_archetype("Tanker")

    # PvE mode (standard caps)
    totals_pve = CharacterTotals()
    totals_pve.resistance[DamageType.SMASHING] = 0.95
    totals_pve.pvp_mode = False

    capped_pve = apply_archetype_caps(totals_pve, tanker)
    assert capped_pve.resistance[DamageType.SMASHING] == 0.90  # 90% cap

    # PvP mode (diminishing returns applied first, then caps)
    totals_pvp = CharacterTotals()
    totals_pvp.resistance[DamageType.SMASHING] = 0.95
    totals_pvp.pvp_mode = True

    # Apply PvP DR BEFORE caps (not shown here)
    # totals_pvp_dr = apply_pvp_dr(totals_pvp)
    # Then apply caps
    # capped_pvp = apply_archetype_caps(totals_pvp_dr, tanker)

    # In PvP, 95% resistance might DR down to 75%, then cap at 90%
    # (exact PvP DR formulas in separate spec)
```

### Test Case 14: Recharge Cap and Perma-Hasten

```python
def test_recharge_cap_perma_hasten():
    """Recharge cap at 500% enables perma-Hasten"""
    any_archetype = get_archetype("Scrapper")

    # Build with heavy recharge (purple sets, LotG, Hasten)
    totals = CharacterTotals()
    totals.recharge_bonus = 3.0  # 300% recharge bonus

    capped = apply_archetype_caps(totals, any_archetype)

    # Below cap (500% = 5.0 - 1 = 4.0 max bonus)
    assert capped.recharge_bonus == 3.0

    # Calculate actual recharge time
    base_recharge = 100.0  # 100 second power
    actual_recharge = base_recharge / (1 + capped.recharge_bonus)
    assert actual_recharge == 25.0  # 25 seconds (4x faster)

    # Perma-Hasten requires ~123% global recharge
    # Hasten itself: 120s recharge, 120s duration
    hasten_recharge = 120.0
    hasten_duration = 120.0
    required_recharge = (hasten_recharge / hasten_duration) - 1.0
    assert required_recharge == pytest.approx(0.0)  # Need 0% at minimum

    # With 70% recharge: 120s / 1.70 = 70.6s (perma with 120s duration)
    # Need gap to activate, so ~100-123% recommended
```

## Section 5: Python Implementation

### Core Data Structures

```python
# backend/app/calculations/archetype_caps.py

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
import math


class Attribute(Enum):
    """Attributes that have archetype-specific caps"""
    DAMAGE = "damage"
    RESISTANCE = "resistance"
    HP = "hp"
    RECOVERY = "recovery"
    REGENERATION = "regeneration"
    RECHARGE = "recharge"
    PERCEPTION = "perception"


class DamageType(Enum):
    """Damage types for resistance caps"""
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    PSIONIC = "psionic"
    TOXIC = "toxic"


@dataclass
class ArchetypeCaps:
    """
    Archetype-specific caps for character attributes.

    All cap values are stored as multipliers:
    - 4.0 = 400% damage cap
    - 0.75 = 75% resistance cap
    - 20.0 = 2000% regeneration cap

    Note: Many caps include base value, so max bonus = cap - 1.0
    """

    archetype_name: str

    # Caps (stored as multipliers, matching MidsReborn format)
    damage_cap: float = 4.0          # 400% (includes 100% base)
    resistance_cap: float = 0.75     # 75%
    hp_cap: float = 2000.0           # Absolute HP value
    recovery_cap: float = 5.0        # 500% (includes 100% base)
    regeneration_cap: float = 20.0   # 2000% (includes 100% base)
    recharge_cap: float = 5.0        # 500% (includes 100% base)
    perception_cap: float = 1153.0   # Feet

    # Display cap for defense (Mids display only, not gameplay)
    defense_display_cap: float = 1.75  # 175% default

    def apply_damage_cap(self, damage_bonus: float) -> float:
        """
        Apply damage cap to damage bonus.

        Args:
            damage_bonus: Total damage bonus (base 100% is separate)

        Returns:
            Capped damage bonus

        Example:
            Blaster with 500% bonus → caps at 400% (5.0 - 1 = 4.0)
        """
        max_bonus = self.damage_cap - 1.0
        return min(damage_bonus, max_bonus)

    def apply_resistance_cap(self, resistance: float, damage_type: Optional[DamageType] = None) -> float:
        """
        Apply resistance cap.

        Resistance cap is absolute (not bonus), so no subtraction.

        Args:
            resistance: Resistance value (0.0 to 1.0+)
            damage_type: Specific damage type (for future per-type caps)

        Returns:
            Capped resistance (0.0 to resistance_cap)

        Example:
            Scrapper with 85% resistance → caps at 75% (0.75)
        """
        return min(resistance, self.resistance_cap)

    def apply_hp_cap(self, hp: float) -> float:
        """
        Apply HP cap.

        HP cap is absolute maximum hit points.

        Args:
            hp: Current hit points

        Returns:
            Capped HP

        Example:
            Scrapper with 2500 HP → caps at 2409 HP
        """
        if self.hp_cap <= 0:
            return hp  # No cap (legacy/pet archetypes)
        return min(hp, self.hp_cap)

    def apply_recovery_cap(self, recovery_bonus: float) -> float:
        """
        Apply recovery cap.

        Args:
            recovery_bonus: Recovery bonus as multiplier

        Returns:
            Capped recovery bonus

        Example:
            Controller with 1000% bonus → caps at 1100% (12.0 - 1 = 11.0)
        """
        max_bonus = self.recovery_cap - 1.0
        return min(recovery_bonus, max_bonus)

    def apply_regeneration_cap(self, regen_bonus: float) -> float:
        """
        Apply regeneration cap.

        Args:
            regen_bonus: Regeneration bonus as multiplier

        Returns:
            Capped regeneration bonus

        Example:
            Scrapper with 3200% bonus → caps at 3000% (31.0 - 1 = 30.0)
        """
        max_bonus = self.regeneration_cap - 1.0
        return min(regen_bonus, max_bonus)

    def apply_recharge_cap(self, recharge_bonus: float) -> float:
        """
        Apply recharge cap.

        Args:
            recharge_bonus: Recharge bonus as multiplier

        Returns:
            Capped recharge bonus

        Example:
            Any AT with 500% bonus → caps at 400% (5.0 - 1 = 4.0)
        """
        max_bonus = self.recharge_cap - 1.0
        return min(recharge_bonus, max_bonus)

    def apply_perception_cap(self, perception: float) -> float:
        """
        Apply perception cap.

        Args:
            perception: Perception range in feet

        Returns:
            Capped perception
        """
        return min(perception, self.perception_cap)

    def is_at_cap(self, value: float, attribute: Attribute, tolerance: float = 0.01) -> bool:
        """
        Check if value is at cap (within tolerance).

        Args:
            value: Current value
            attribute: Which attribute to check
            tolerance: How close to cap counts as "at cap"

        Returns:
            True if at cap
        """
        cap = self._get_cap_for_attribute(attribute)
        return abs(value - cap) <= tolerance or value > cap

    def calculate_waste(self, uncapped: float, attribute: Attribute) -> float:
        """
        Calculate how much bonus is wasted due to cap.

        Args:
            uncapped: Uncapped value
            attribute: Which attribute

        Returns:
            Amount over cap (wasted)
        """
        cap = self._get_cap_for_attribute(attribute)
        if uncapped <= cap:
            return 0.0
        return uncapped - cap

    def _get_cap_for_attribute(self, attribute: Attribute) -> float:
        """Get cap value for specific attribute"""
        cap_map = {
            Attribute.DAMAGE: self.damage_cap - 1.0,
            Attribute.RESISTANCE: self.resistance_cap,
            Attribute.HP: self.hp_cap,
            Attribute.RECOVERY: self.recovery_cap - 1.0,
            Attribute.REGENERATION: self.regeneration_cap - 1.0,
            Attribute.RECHARGE: self.recharge_cap - 1.0,
            Attribute.PERCEPTION: self.perception_cap,
        }
        return cap_map[attribute]

    def to_display_dict(self) -> Dict[str, str]:
        """
        Convert caps to display-friendly format (percentages).

        Returns:
            Dictionary with formatted cap values
        """
        return {
            "damage": f"{int(self.damage_cap * 100)}%",
            "resistance": f"{int(self.resistance_cap * 100)}%",
            "hp": f"{int(self.hp_cap)} HP",
            "recovery": f"{int(self.recovery_cap * 100)}%",
            "regeneration": f"{int(self.regeneration_cap * 100)}%",
            "recharge": f"{int(self.recharge_cap * 100)}%",
            "perception": f"{int(self.perception_cap)} ft",
        }


# Archetype cap definitions (from MidsReborn source and game data)
ARCHETYPE_CAPS: Dict[str, ArchetypeCaps] = {
    "Tanker": ArchetypeCaps(
        archetype_name="Tanker",
        damage_cap=4.0,
        resistance_cap=0.90,
        hp_cap=3534.0,
        recovery_cap=5.0,
        regeneration_cap=21.0,  # 2500% (stored as 21.0 in Mids)
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=2.25,
    ),
    "Brute": ArchetypeCaps(
        archetype_name="Brute",
        damage_cap=7.75,  # UNIQUE: 775% damage cap
        resistance_cap=0.90,
        hp_cap=3212.0,
        recovery_cap=5.0,
        regeneration_cap=21.0,  # 2500%
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=2.25,
    ),
    "Scrapper": ArchetypeCaps(
        archetype_name="Scrapper",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=2409.0,
        recovery_cap=5.0,
        regeneration_cap=31.0,  # UNIQUE: 3000% regen cap
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=2.00,
    ),
    "Stalker": ArchetypeCaps(
        archetype_name="Stalker",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=2091.0,
        recovery_cap=5.0,
        regeneration_cap=31.0,  # 3000% regen cap
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=2.00,
    ),
    "Blaster": ArchetypeCaps(
        archetype_name="Blaster",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=5.0,
        regeneration_cap=20.0,  # 2000%
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Defender": ArchetypeCaps(
        archetype_name="Defender",
        damage_cap=4.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=10.0,  # 1000% recovery cap
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Controller": ArchetypeCaps(
        archetype_name="Controller",
        damage_cap=4.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=12.0,  # UNIQUE: 1200% recovery cap
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Corruptor": ArchetypeCaps(
        archetype_name="Corruptor",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=5.0,
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Dominator": ArchetypeCaps(
        archetype_name="Dominator",
        damage_cap=4.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=12.0,  # 1200% recovery cap
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Mastermind": ArchetypeCaps(
        archetype_name="Mastermind",
        damage_cap=4.0,
        resistance_cap=0.75,
        hp_cap=1874.0,
        recovery_cap=12.0,  # 1200% recovery cap
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Sentinel": ArchetypeCaps(
        archetype_name="Sentinel",
        damage_cap=5.0,
        resistance_cap=0.75,
        hp_cap=2409.0,
        recovery_cap=5.0,
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=1.75,
    ),
    "Peacebringer": ArchetypeCaps(
        archetype_name="Peacebringer",
        damage_cap=4.0,
        resistance_cap=0.85,  # Kheldian: 85% resistance cap
        hp_cap=2250.0,
        recovery_cap=5.0,
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=2.00,
    ),
    "Warshade": ArchetypeCaps(
        archetype_name="Warshade",
        damage_cap=4.0,
        resistance_cap=0.85,  # Kheldian: 85% resistance cap
        hp_cap=2250.0,
        recovery_cap=5.0,
        regeneration_cap=20.0,
        recharge_cap=5.0,
        perception_cap=1153.0,
        defense_display_cap=2.00,
    ),
}


def get_archetype_caps(archetype_name: str) -> ArchetypeCaps:
    """
    Get archetype caps by name.

    Args:
        archetype_name: Archetype name (e.g., "Tanker", "Scrapper")

    Returns:
        ArchetypeCaps instance

    Raises:
        KeyError: If archetype not found
    """
    if archetype_name not in ARCHETYPE_CAPS:
        raise KeyError(f"Unknown archetype: {archetype_name}")
    return ARCHETYPE_CAPS[archetype_name]


def apply_all_caps(
    totals: Dict[str, any],
    archetype_caps: ArchetypeCaps
) -> Dict[str, any]:
    """
    Apply all archetype caps to character totals.

    This is the main entry point for cap enforcement.

    Args:
        totals: Uncapped character totals (dict with all attributes)
        archetype_caps: Archetype cap definitions

    Returns:
        Capped totals (actual in-game values)
    """
    capped = totals.copy()

    # Apply each cap
    if "damage_bonus" in capped:
        capped["damage_bonus"] = archetype_caps.apply_damage_cap(
            capped["damage_bonus"]
        )

    if "resistance" in capped:
        for damage_type in DamageType:
            key = f"resistance_{damage_type.value}"
            if key in capped:
                capped[key] = archetype_caps.apply_resistance_cap(
                    capped[key], damage_type
                )

    if "hp_max" in capped:
        capped["hp_max"] = archetype_caps.apply_hp_cap(capped["hp_max"])
        # Absorb cannot exceed max HP
        if "absorb" in capped:
            capped["absorb"] = min(capped["absorb"], capped["hp_max"])

    if "recovery_bonus" in capped:
        capped["recovery_bonus"] = archetype_caps.apply_recovery_cap(
            capped["recovery_bonus"]
        )

    if "regeneration_bonus" in capped:
        capped["regeneration_bonus"] = archetype_caps.apply_regeneration_cap(
            capped["regeneration_bonus"]
        )

    if "recharge_bonus" in capped:
        capped["recharge_bonus"] = archetype_caps.apply_recharge_cap(
            capped["recharge_bonus"]
        )

    if "perception" in capped:
        capped["perception"] = archetype_caps.apply_perception_cap(
            capped["perception"]
        )

    return capped


# Defense soft cap helpers
def calculate_hit_chance(enemy_tohit: float, defense: float) -> float:
    """
    Calculate hit chance after defense with ToHit floor.

    Args:
        enemy_tohit: Enemy's base ToHit (0.50 for even-level)
        defense: Character's defense value

    Returns:
        Final hit chance (minimum 5% floor)
    """
    hit_chance = enemy_tohit - defense
    return max(0.05, hit_chance)  # 5% ToHit floor


def is_defense_soft_capped(defense: float, enemy_tohit: float = 0.50) -> bool:
    """
    Check if defense is at soft cap (45% vs even-level enemies).

    Args:
        defense: Character's defense value
        enemy_tohit: Enemy ToHit (default 50% for even-level)

    Returns:
        True if at soft cap (hit chance at floor)
    """
    return calculate_hit_chance(enemy_tohit, defense) <= 0.05


def defense_soft_cap_for_enemy(enemy_tohit: float) -> float:
    """
    Calculate defense soft cap for specific enemy ToHit.

    Args:
        enemy_tohit: Enemy's ToHit value

    Returns:
        Defense value that reaches 5% hit floor
    """
    # Soft cap is when: enemy_tohit - defense = 0.05
    # So: defense = enemy_tohit - 0.05
    return enemy_tohit - 0.05
```

### Usage Examples

```python
# Example 1: Apply caps to a Tanker build
tanker_caps = get_archetype_caps("Tanker")

# Uncapped totals from all sources
totals = {
    "damage_bonus": 3.5,  # 350% bonus (450% total)
    "resistance_smashing": 0.95,  # 95% resistance (over cap!)
    "resistance_lethal": 0.88,
    "hp_max": 3200.0,
    "recovery_bonus": 4.0,
    "regeneration_bonus": 18.0,
    "recharge_bonus": 3.8,
    "perception": 1100.0,
}

# Apply all caps
capped_totals = apply_all_caps(totals, tanker_caps)

print(capped_totals)
# {
#     "damage_bonus": 3.0,  # Capped at 300% bonus (400% total)
#     "resistance_smashing": 0.90,  # Capped at 90%
#     "resistance_lethal": 0.88,  # Below cap, unchanged
#     "hp_max": 3200.0,  # Below cap (3534), unchanged
#     "recovery_bonus": 4.0,  # Below cap, unchanged
#     "regeneration_bonus": 18.0,  # Below cap (20.0), unchanged
#     "recharge_bonus": 3.8,  # Below cap (4.0), unchanged
#     "perception": 1100.0,  # Below cap, unchanged
# }


# Example 2: Check if at cap
brute_caps = get_archetype_caps("Brute")
damage_bonus = 6.5

is_at_cap = brute_caps.is_at_cap(damage_bonus, Attribute.DAMAGE)
print(f"At damage cap: {is_at_cap}")  # False (cap is 6.75)

waste = brute_caps.calculate_waste(damage_bonus, Attribute.DAMAGE)
print(f"Wasted damage: {waste}")  # 0.0 (not over cap)


# Example 3: Defense soft cap
defense = 0.45
print(f"At soft cap: {is_defense_soft_capped(defense)}")  # True

hit_chance = calculate_hit_chance(0.50, defense)
print(f"Hit chance: {hit_chance * 100}%")  # 5.0%

# +2 level enemy (60% ToHit)
soft_cap_vs_plus2 = defense_soft_cap_for_enemy(0.60)
print(f"Soft cap vs +2: {soft_cap_vs_plus2 * 100}%")  # 55%
```

## Section 6: Integration Points

### Integration with Effect System (Spec 01)

Archetype caps are applied **after** all effect accumulation:

```python
# Calculation flow showing integration with Spec 01

# Step 1: Accumulate effects from all powers (Spec 01)
from app.calculations.effects import accumulate_effects

power_effects = accumulate_effects(active_powers)
# Returns: {
#     "damage": [effect1, effect2, ...],
#     "resistance_smashing": [effect3, effect4, ...],
#     ...
# }

# Step 2: Sum effects into totals
totals = sum_effects_to_totals(power_effects)
# Returns: {
#     "damage_bonus": 5.0,  # May be over cap
#     "resistance_smashing": 0.95,  # May be over cap
#     ...
# }

# Step 3: Apply archetype caps (THIS SPEC)
from app.calculations.archetype_caps import get_archetype_caps, apply_all_caps

archetype_caps = get_archetype_caps(character.archetype_name)
capped_totals = apply_all_caps(totals, archetype_caps)
# Returns: {
#     "damage_bonus": 4.0,  # Capped
#     "resistance_smashing": 0.75,  # Capped
#     ...
# }

# Step 4: Store both uncapped and capped values
character.totals_uncapped = totals
character.totals_capped = capped_totals  # Used for gameplay
```

### Integration with Archetype Modifiers (Spec 16)

Archetype modifiers scale effect values, caps limit final totals:

```python
# Calculation flow showing Spec 16 → Spec 17 integration

# Step 1: Get archetype modifiers (Spec 16)
from app.calculations.archetype_modifiers import get_archetype_modifiers

archetype = get_archetype("Tanker")
at_mods = get_archetype_modifiers(archetype)
# Returns: {
#     "damage": 0.80,  # 80% damage scale (Tanker penalty)
#     "resistance": 1.00,  # 100% resistance scale
#     "hp": 2.00,  # 200% HP scale (Tanker bonus)
#     ...
# }

# Step 2: Apply AT mods to base effects
base_damage_effect = 100.0  # Base damage from power
scaled_damage = base_damage_effect * at_mods["damage"]
# Result: 80.0 (Tanker does 80% damage)

# Step 3: Accumulate all scaled effects
totals = accumulate_all_scaled_effects(character)
# Result: {
#     "damage_bonus": 3.5,  # After ATMod scaling
#     "resistance_smashing": 0.95,  # After ATMod scaling
#     ...
# }

# Step 4: Apply archetype caps (THIS SPEC)
archetype_caps = get_archetype_caps(archetype)
capped_totals = apply_all_caps(totals, archetype_caps)
# Result: {
#     "damage_bonus": 3.0,  # Capped at 300% bonus
#     "resistance_smashing": 0.90,  # Capped at 90% (Tanker cap)
#     ...
# }

# Key insight: AT mods scale INPUTS, caps limit OUTPUTS
```

### Complete Calculation Flow Example

Full pipeline from powers to final capped values:

```python
# Complete calculation showing all specs working together

def calculate_character_totals(character: Character) -> CharacterTotals:
    """
    Complete calculation pipeline with all specs integrated.

    Spec 01: Power Effects Core
    Spec 03: Power Buffs/Debuffs
    Spec 05: Enhancement Effects
    Spec 16: Archetype Modifiers
    Spec 17: Archetype Caps (THIS SPEC)
    """

    # === STEP 1: Accumulate Effects (Spec 01) ===
    effects = []
    for power_entry in character.build.powers:
        power = power_entry.power

        # Get base effects
        base_effects = power.effects

        # Apply enhancements (Spec 05)
        enhanced_effects = apply_enhancements(
            base_effects,
            power_entry.slots
        )

        # Apply archetype modifiers (Spec 16)
        scaled_effects = apply_archetype_modifiers(
            enhanced_effects,
            character.archetype
        )

        effects.extend(scaled_effects)

    # === STEP 2: Sum all effects into totals ===
    totals = CharacterTotals()

    for effect in effects:
        if effect.type == EffectType.DAMAGE:
            totals.damage_bonus += effect.magnitude
        elif effect.type == EffectType.RESISTANCE:
            totals.resistance[effect.damage_type] += effect.magnitude
        elif effect.type == EffectType.MAX_HP:
            totals.hp_bonus += effect.magnitude
        # ... etc for all effect types

    # Calculate final HP (base * (1 + bonus))
    base_hp = character.archetype.base_hit_points * HP_LEVEL_SCALE[character.level]
    totals.hp_max = base_hp * (1 + totals.hp_bonus)

    # === STEP 3: Apply Enhancement Diversification ===
    # (If not already applied per-power)
    totals = apply_ed_to_totals(totals)

    # === STEP 4: Apply Global Modifiers ===
    # (Incarnate abilities, temp powers, etc.)
    totals = apply_global_modifiers(totals, character)

    # === STEP 5: Apply PvP DR (if in PvP mode) ===
    if character.pvp_mode:
        totals = apply_pvp_diminishing_returns(totals)

    # === STEP 6: Apply Archetype Caps (THIS SPEC) ===
    archetype_caps = get_archetype_caps(character.archetype_name)
    capped_totals = apply_all_caps(totals.to_dict(), archetype_caps)

    # === STEP 7: Store both uncapped and capped ===
    final_totals = CharacterTotals.from_dict(capped_totals)
    final_totals.uncapped = totals  # Keep uncapped for analysis

    return final_totals


# Usage
character = get_character(build_id=123)
totals = calculate_character_totals(character)

print(f"Damage bonus: {totals.damage_bonus * 100}%")
print(f"Resistance (S/L): {totals.resistance[DamageType.SMASHING] * 100}%")
print(f"HP: {totals.hp_max}")

# Show what's wasted (uncapped vs capped)
if totals.uncapped.damage_bonus > totals.damage_bonus:
    wasted = (totals.uncapped.damage_bonus - totals.damage_bonus) * 100
    print(f"⚠️ {wasted}% damage bonus wasted (over cap)")
```

### UI Integration (Build Display)

Display caps in build totals UI:

```python
# API endpoint for build totals with cap indicators

@router.get("/builds/{build_id}/totals")
async def get_build_totals(
    build_id: int,
    db: Session = Depends(get_db)
):
    """
    Get build totals with cap indicators.

    Returns both uncapped and capped values, plus cap info.
    """
    character = get_character(db, build_id)
    totals = calculate_character_totals(character)
    archetype_caps = get_archetype_caps(character.archetype_name)

    # Build response with cap indicators
    response = {
        "archetype": character.archetype_name,
        "level": character.level,
        "totals": {
            "damage": {
                "value": totals.damage_bonus,
                "display": f"{int(totals.damage_bonus * 100)}%",
                "uncapped": totals.uncapped.damage_bonus,
                "cap": archetype_caps.damage_cap - 1.0,
                "at_cap": archetype_caps.is_at_cap(
                    totals.damage_bonus,
                    Attribute.DAMAGE
                ),
                "wasted": archetype_caps.calculate_waste(
                    totals.uncapped.damage_bonus,
                    Attribute.DAMAGE
                ),
            },
            "resistance": {},
            # ... etc
        },
        "caps": archetype_caps.to_display_dict(),
    }

    # Add resistance for each damage type
    for damage_type in DamageType:
        res_value = totals.resistance[damage_type]
        res_uncapped = totals.uncapped.resistance[damage_type]

        response["totals"]["resistance"][damage_type.value] = {
            "value": res_value,
            "display": f"{int(res_value * 100)}%",
            "uncapped": res_uncapped,
            "cap": archetype_caps.resistance_cap,
            "at_cap": abs(res_value - archetype_caps.resistance_cap) < 0.01,
            "wasted": max(0, res_uncapped - archetype_caps.resistance_cap),
        }

    return response


# Frontend display (React component pseudocode)
function CapIndicator({ value, cap, uncapped }) {
    const atCap = Math.abs(value - cap) < 0.01 || value > cap;
    const wasted = Math.max(0, uncapped - cap);

    return (
        <div className={atCap ? "at-cap" : ""}>
            <span className="value">{value * 100}%</span>
            {atCap && (
                <span className="cap-indicator">
                    ⚠️ AT CAP ({cap * 100}%)
                </span>
            )}
            {wasted > 0 && (
                <span className="waste-indicator">
                    ({wasted * 100}% wasted)
                </span>
            )}
        </div>
    );
}
```

### Database Query Integration

Efficient cap lookups:

```sql
-- Query to get character totals with caps
SELECT
    b.id AS build_id,
    b.name AS build_name,
    a.name AS archetype,
    a.damage_cap,
    a.resistance_cap,
    a.hp_cap,
    a.recovery_cap,
    a.regeneration_cap,
    a.recharge_cap,

    -- Pre-calculate cap indicators
    CASE
        WHEN bt.damage_bonus >= (a.damage_cap - 1.0) THEN true
        ELSE false
    END AS damage_at_cap,

    CASE
        WHEN bt.resistance_smashing >= a.resistance_cap THEN true
        ELSE false
    END AS resistance_smashing_at_cap

FROM builds b
JOIN archetypes a ON b.archetype_id = a.id
LEFT JOIN build_totals bt ON bt.build_id = b.id
WHERE b.id = $1;
```

---

## Summary

This specification now includes:

1. ✅ **Complete cap table** for all primary/epic archetypes with exact values from MidsReborn source
2. ✅ **Detailed algorithm** with pseudocode showing cap application as final calculation step
3. ✅ **C# implementation details** with line numbers and actual source code from Archetype.cs and clsToonX.cs
4. ✅ **Database schema** with seed data for all archetypes and proper indexes
5. ✅ **14 comprehensive test cases** covering all cap types, edge cases, and over-cap scenarios
6. ✅ **Python implementation** with full ArchetypeCaps class and helper functions
7. ✅ **Integration points** with Spec 01 (Effects), Spec 16 (AT Mods), and complete calculation flow
8. ✅ **UI integration** examples for displaying caps and waste indicators

**Key Technical Insights**:
- Caps stored as multipliers (4.0 = 400%), not percentages
- "Bonus" caps (damage, regen, recovery, recharge) subtract 1.0 for base value
- Resistance/HP caps are absolute values (no subtraction)
- Defense has NO hard cap (only soft cap at 45% from ToHit floor)
- Cap enforcement is FINAL step after ATMods, ED, and PvP DR
- MidsReborn loads caps from binary .mhd file using BinaryReader

**Unique Cap Values Found**:
- Brute: 775% damage cap (only AT with this value)
- Scrapper/Stalker: 3000% regen cap (highest)
- Controller/Dominator/MM: 1200% recovery cap (highest)
- Kheldians: 85% resistance cap (between Tanker and others)
- All ATs: 500% recharge cap (universal)
