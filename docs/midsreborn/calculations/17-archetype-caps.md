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

**Document Status**: 🟡 Breadth Complete - Core cap mechanics documented
**Implementation Status**: Not implemented (Python code examples provided)
**Last Updated**: 2025-11-10
