# Combat Attributes - Real-Time Stat Display

## Overview
- **Purpose**: Display live combat statistics that show current/active character stats in categorized format - what players see in-game via the Combat Attributes window (originally called "Real Numbers")
- **Used By**: Character statistics window, build analysis, power comparison, in-game stat verification
- **Complexity**: Medium
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Statistics.cs` - Display stat calculation methods
- **Related Files**:
  - `Core/Stats.cs` - Data structure classes for categorized stats
  - `Core/Base/Data_Classes/Character.cs` - `DisplayStats` property (Statistics instance)
  - `Core/Base/Data_Classes/Character.cs` - `Totals` and `TotalsCapped` (TotalStatistics)
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - UI display of totals
  - `Forms/Controls/DataView.cs` - `DisplayTotals()` method for rendering
  - `Forms/WindowMenuItems/frmStats.cs` - Power stat graphing window

### Combat Attributes Data Structure

```csharp
// From Core/Base/Data_Classes/Character.cs
public class Character
{
    public TotalStatistics Totals;        // Uncapped aggregate totals
    public TotalStatistics TotalsCapped;  // Capped by archetype limits
    public Statistics DisplayStats { get; }  // Formatted display values
}

// From Core/Statistics.cs
public class Statistics
{
    private readonly Character _character;

    // Display properties that format totals for UI
    public float EnduranceMaxEnd => _character.Totals.EndMax + 100f;
    public float EnduranceRecoveryNumeric => ...;
    public float HealthRegenHealthPerSec => ...;
    public float HealthHitpointsNumeric(bool uncapped) => ...;
    public float BuffToHit => _character.Totals.BuffToHit * 100f;
    public float BuffAccuracy => _character.Totals.BuffAcc * 100f;
    public float BuffDamage(bool uncapped) => ...;
    public float BuffHaste(bool uncapped) => ...;
    public float Defense(int dType) => _character.Totals.Def[dType] * 100f;
    public float DamageResistance(int dType, bool uncapped) => ...;
    public float Perception(bool uncapped) => ...;
    public float Speed(float iSpeed, Enums.eSpeedMeasure unit) => ...;
    // ... many more display methods
}

// From Core/Stats.cs - Display structure for categorization
public class Stats
{
    public class Display
    {
        // Offense
        public Accuracy Accuracy { get; set; }
        public DamageBuff DamageBuff { get; set; }
        public ToHit ToHit { get; set; }
        public Recharge Recharge { get; set; }

        // Defense
        public Defense Defense { get; set; }
        public Elusivity Elusivity { get; set; }
        public Resistance Resistance { get; set; }

        // Survivability
        public Absorb Absorb { get; set; }
        public HitPoints HitPoints { get; set; }
        public Regeneration Regeneration { get; set; }
        public Endurance Endurance { get; set; }
        public Recovery Recovery { get; set; }

        // Debuff Protection
        public DebuffResistance DebuffResistance { get; set; }
        public StatusProtection StatusProtection { get; set; }
        public StatusResistance StatusResistance { get; set; }

        // Misc
        public Movement Movement { get; set; }
        public Perception Perception { get; set; }
        public StealthRadius StealthRadius { get; set; }
        public Threat Threat { get; set; }

        // Debuffs
        public DefenseDebuff DefenseDebuff { get; set; }
        public ResistanceDebuff ResistanceDebuff { get; set; }
    }
}
```

### High-Level Algorithm

```
Combat Attributes Display Algorithm:

1. Data Source Preparation:
   - Read Character.Totals (uncapped values)
   - Read Character.TotalsCapped (capped by archetype)
   - Access Character.Archetype for caps and base values
   - Check active powers, toggles, and temporary buffs

2. Category Organization:
   The display groups stats into logical categories:

   OFFENSE:
   - Damage Buff: Total damage bonus (+100% base = 200% damage)
   - To-Hit Buff: Accuracy before hit check (+ToHit)
   - Accuracy Buff: Accuracy multiplier (affects final hit chance)
   - Recharge Speed: Power recharge rate (+Recharge)
   - Endurance Discount: Endurance cost reduction
   - Range: Power range modification

   DEFENSE:
   - Defense (Typed): S/L/F/C/E/N/P/T (8 types)
   - Defense (Positional): Melee/Ranged/AoE (3 positions)
   - Elusivity: Additional defense layer (rare)
   - Resistance (Typed): S/L/F/C/E/N/T/P (8 types)

   MOVEMENT:
   - Run Speed: Current run speed (ft/s, mph, etc.)
   - Jump Speed: Jump velocity
   - Jump Height: Jump height
   - Fly Speed: Flight speed

   SURVIVABILITY:
   - Max HP: Total hit points
   - Regeneration: HP regeneration rate (%/sec and HP/sec)
   - Max Endurance: Total endurance pool
   - Recovery: End recovery rate (%/sec and End/sec)
   - Absorb: Damage absorption (temporary HP layer)

   STATUS PROTECTION:
   - Mez Protection: Hold, Sleep, Stun, Immob, Confuse, Fear, etc.
   - Magnitude values (typically 0-50+)
   - Protection prevents mez if mag >= enemy mez magnitude

   STATUS RESISTANCE:
   - Mez Resistance: Reduces mez duration (0-100%)
   - Formula: actual_duration = base_duration * (1 - resistance)

   DEBUFF RESISTANCE:
   - Defense Debuff Resistance (DDR): Protects defense (cap: 95%)
   - Recharge Resistance: Protects recharge speed
   - Recovery Resistance: Protects endurance recovery
   - Regeneration Resistance: Protects HP regeneration
   - ToHit Resistance: Protects to-hit buffs
   - (All except DDR cap at 100%)

   MISC:
   - Perception: Vision radius (detect stealth)
   - Stealth (PvE): Stealth radius vs NPCs
   - Stealth (PvP): Stealth radius vs players
   - Threat Level: Aggro generation (taunt/placate modifier)

3. Value Formatting:
   FOR EACH stat category:
     FOR EACH stat in category:
       - Get raw value from Totals or TotalsCapped
       - Apply formatting rules:
         * Percentages: multiply by 100, show as "%"
         * Absolute values: show with units (HP, ft/s, etc.)
         * Per-second rates: show "/s" suffix
       - Check if capped:
         IF uncapped > capped:
           Display: "75.0% (90.0% capped)"
         ELSE:
           Display: "75.0%"
       - Add contextual info:
         * Archetype cap for resistance/damage
         * Soft cap indicator for defense (45%)
         * Base values for comparison

4. Active vs Theoretical Display:
   Mids shows TWO modes:

   a. Build Totals (Permanent):
      - All toggles assumed ON
      - All auto powers active
      - Set bonuses included
      - Global IOs included
      - NO click buffs (unless permanent)
      - This is "always active" state

   b. With Temporary Buffs:
      - Include click buffs (e.g., Build Up, Aim)
      - Include Incarnate powers (Destiny, etc.)
      - Include team buffs (optional)
      - This is "theoretical maximum" state

5. Color Coding / Highlighting:
   - Green: Soft cap reached (defense 45%+, resistance at cap)
   - Yellow: Good but not capped
   - White: Normal values
   - Red: Below expected (gaps in defense, low resistance)
   - Blue: Special values (DDR, elusivity)

6. Tooltip / Expanded Info:
   On hover, show:
   - Source breakdown (which powers/sets contribute)
   - Cap information (archetype caps, soft caps)
   - Comparison to base (e.g., "+200% from base")
   - Effective value (e.g., "45% defense = 10% hit chance")

7. Display Rendering:
   - Organize into tabbed or accordion UI
   - Show most important stats first (Defense, Resistance, HP)
   - Allow sorting/filtering by category
   - Provide export/copy functionality
   - Update in real-time when build changes
```

### Stat Category Breakdown

**Offense Stats** (frmTotalsV2.cs display):
```csharp
// Damage
public float BuffDamage(bool uncapped)
{
    return !uncapped
        ? Math.Min(_character.Archetype?.DamageCap * 100 ?? float.PositiveInfinity,
                   (_character.TotalsCapped.BuffDam + 1) * 100)
        : (_character.Totals.BuffDam + 1) * 100;
}

// To-Hit
public float BuffToHit => _character.Totals.BuffToHit * 100f;

// Accuracy
public float BuffAccuracy => _character.Totals.BuffAcc * 100f;

// Recharge (Haste)
public float BuffHaste(bool uncapped)
{
    return !uncapped
        ? Math.Min(MaxHaste, (_character.TotalsCapped.BuffHaste + 1) * 100)
        : (_character.Totals.BuffHaste + 1) * 100;
}

// Constants
public const float MaxHaste = 400f;  // 400% recharge cap
```

**Defense Stats**:
```csharp
// Defense by type
public float Defense(int dType)
{
    return _character.Totals.Def[dType] * 100f;
}

// Resistance by type (capped per archetype)
public float DamageResistance(int dType, bool uncapped)
{
    return uncapped
        ? _character.Totals.Res[dType] * 100f
        : _character.TotalsCapped.Res[dType] * 100f;
}
```

**Movement Stats**:
```csharp
// Run Speed
public float MovementRunSpeed(Enums.eSpeedMeasure sType, bool uncapped)
{
    var iSpeed = uncapped
        ? MidsContext.Character?.Totals.RunSpd
        : MidsContext.Character?.TotalsCapped.RunSpd;
    return Speed(iSpeed ?? 0, sType);
}

// Speed conversion
public float Speed(float iSpeed, Enums.eSpeedMeasure unit)
{
    return unit switch
    {
        Enums.eSpeedMeasure.FeetPerSecond => iSpeed,
        Enums.eSpeedMeasure.MetersPerSecond => iSpeed * 0.3048f,
        Enums.eSpeedMeasure.MilesPerHour => iSpeed * 0.6818182f,
        Enums.eSpeedMeasure.KilometersPerHour => iSpeed * 1.09728f,
        _ => iSpeed
    };
}
```

**Survivability Stats**:
```csharp
// Hit Points
public float HealthHitpointsNumeric(bool uncapped)
{
    return uncapped
        ? _character.Totals.HPMax
        : _character.TotalsCapped.HPMax;
}

// Regeneration (HP per second)
public float HealthRegenHPPerSec =>
    (float)(HealthRegen(false) * _character.Archetype.BaseRegen * 1.66666662693024
            * HealthHitpointsNumeric(false) / 100.0);

// Endurance
public float EnduranceMaxEnd => _character.Totals.EndMax + 100f;

// Recovery (End per second)
public float EnduranceRecoveryNumeric =>
    EnduranceRecovery(false) * (_character.Archetype.BaseRecovery * 1.666667f)
    * (_character.TotalsCapped.EndMax / 100 + 1);
```

### Display Formatting Examples

```
Offense:
  Damage:        +200.00% (Scrapper cap: 500%)
  To-Hit:        +22.50%
  Accuracy:      +15.00%
  Recharge:      +125.00%
  End Discount:  -35.00%

Defense:
  Smashing:      45.12% (Soft Cap)
  Lethal:        45.12% (Soft Cap)
  Fire:          32.50%
  Cold:          32.50%
  Energy:        28.75%
  Negative:      28.75%
  Psionic:       15.00%
  Melee:         45.00% (Soft Cap)
  Ranged:        38.50%
  AoE:           35.00%

Resistance:
  Smashing:      75.00% (Scrapper cap: 75%)
  Lethal:        75.00% (Scrapper cap: 75%)
  Fire:          45.00%
  Cold:          45.00%
  Energy:        30.00%
  Negative:      30.00%
  Psionic:       0.00%
  Toxic:         0.00%

Movement:
  Run Speed:     92.50 ft/s (62.97 mph)
  Jump Speed:    48.00 ft/s
  Jump Height:   12.00 ft
  Fly Speed:     58.65 ft/s

Survivability:
  Max HP:        2409.0 HP
  Regeneration:  250.00% (20.08 HP/s)
  Max End:       110.00 End
  Recovery:      150.00% (2.50 End/s)
  Absorb:        0.00 HP

Status Protection:
  Hold:          12.98 mag
  Sleep:         12.98 mag
  Stun:          12.98 mag
  Immobilize:    12.98 mag
  Confuse:       0.00 mag
  Fear:          0.00 mag
  Knockback:     12.00 mag

Status Resistance:
  Hold:          0.00%
  Sleep:         0.00%
  Stun:          0.00%
  Immobilize:    0.00%
  Confuse:       0.00%
  Fear:          0.00%

Debuff Resistance:
  Defense:       95.00% (Capped)
  Recharge:      0.00%
  Recovery:      0.00%
  Regeneration:  0.00%
  To-Hit:        0.00%

Misc:
  Perception:    1149.00 ft
  Stealth (PvE): 0.00 ft
  Stealth (PvP): 0.00 ft
  Threat:        400.00% (Tanker taunt multiplier)
```

## Game Mechanics Context

### Why This Exists

**Historical Context**:

1. **Issue 5 (2005)**: City of Heroes added the "Real Numbers" window that showed actual character stats (previously hidden)
   - Players could finally see their exact defense, resistance, damage, etc.
   - Revolutionized build planning - players could now optimize numerically
   - Mids Reborn replicated this window for offline planning

2. **Issue 7 (2006)**: Combat Attributes window became essential tool
   - "Soft cap" knowledge spread (45% defense optimal)
   - Players used it to verify builds in-game
   - Mids needed to match in-game display exactly

3. **Issue 13 (2008)**: More stats added (DDR, elusivity, etc.)
   - Window grew more complex
   - Mids had to track all new stats

4. **Homecoming (2019+)**: Additional stats (toxic defense, new resistances)
   - Combat attributes is now definitive stat reference
   - Mids must stay in sync with game

**Why Players Use This**:

1. **Build Verification**: Check if build meets goals (45% def, 75% res, etc.)
2. **Gap Analysis**: Find weaknesses (0% psi defense, low DDR)
3. **Optimization**: See which stats are overcapped (wasted) vs undercapped
4. **Comparison**: Compare different builds side-by-side
5. **In-Game Sync**: Verify Mids build matches in-game stats

### Relationship to Other Systems

**Dependencies**:
- **Spec 19-24**: Build Totals (HP, Defense, Resistance, etc.) - source of all displayed values
- **Spec 16**: Archetype Modifiers - caps and base values for formatting
- **Spec 17**: Archetype Caps - cap enforcement shown in display
- **Spec 13**: Enhancement Set Bonuses - major contributor to stats
- **Spec 01**: Power Effects Core - aggregation of all effects into totals

**Used By**:
- Build comparison tools
- Export/import functions
- Optimization algorithms
- UI stat displays

### Known Quirks

1. **"Real Numbers" vs "Combat Attributes"**:
   - Original CoH called it "Real Numbers" (Issue 5-6)
   - Later renamed to "Combat Attributes" (Issue 7+)
   - Some players still call it "Real Numbers"
   - Mids uses both terms interchangeably

2. **Toggles Assumed Active**:
   - Build totals assume ALL toggles are ON
   - Real combat has toggles drop (detoggle)
   - This creates gap between "paper build" and "real survivability"
   - Players must account for detoggle risk

3. **Capped vs Uncapped Display**:
   - Some stats show both (e.g., "95.0% resistance (capped at 90%)")
   - Helps identify overcapping (wasted bonuses)
   - Important for build optimization

4. **Soft Cap Highlighting**:
   - Defense soft cap (45%) is visual target
   - Not a hard cap - values above 45% are useful
   - Players often mistake "soft cap" for "hard cap"

5. **Pet Stats Separate**:
   - Some powers summon pets with own stats
   - Pet combat attributes tracked separately
   - Mastermind builds need pet stat window
   - Build totals don't include pet stats

6. **Hidden Stats**:
   - Some stats exist but aren't displayed:
     * Internal recharge time
     * Animation time
     * Root time
   - Mids may expose these for advanced users

7. **Percentage vs Absolute**:
   - Some stats show percentage (75% resistance)
   - Others show absolute (2409 HP)
   - Conversion rules must match game exactly
   - Example: Regen is "250%" but also "20.08 HP/s"

## Python Implementation Notes

### Proposed Architecture

```python
# backend/app/calculations/combat_attributes.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class StatCategory(Enum):
    """Combat attribute categories for organization"""
    OFFENSE = "offense"
    DEFENSE = "defense"
    MOVEMENT = "movement"
    SURVIVABILITY = "survivability"
    STATUS_PROTECTION = "status_protection"
    STATUS_RESISTANCE = "status_resistance"
    DEBUFF_RESISTANCE = "debuff_resistance"
    MISC = "misc"

@dataclass
class CombatAttribute:
    """
    Single combat attribute with formatted display value
    Maps to one row in Combat Attributes window
    """
    name: str                    # "Smashing Defense"
    category: StatCategory       # DEFENSE
    value: float                 # Raw value (0.45 = 45%)
    display_value: str           # Formatted: "45.00%"
    tooltip: str                 # Extended info
    is_capped: bool = False      # True if at archetype cap
    uncapped_value: Optional[float] = None  # If overcapped
    color: str = "normal"        # "normal", "good", "excellent", "poor"

@dataclass
class CombatAttributeCategory:
    """
    Category of related combat attributes
    Maps to one section of Combat Attributes window
    """
    category: StatCategory
    display_name: str            # "Offense", "Defense", etc.
    attributes: List[CombatAttribute] = field(default_factory=list)
    expanded: bool = True        # UI collapsed/expanded state

@dataclass
class CombatAttributesDisplay:
    """
    Complete combat attributes display
    Maps to entire Combat Attributes window in MidsReborn
    """
    categories: List[CombatAttributeCategory] = field(default_factory=list)
    show_uncapped: bool = True   # Show overcapped values
    show_base_comparison: bool = False  # Show "+X from base"

class CombatAttributesCalculator:
    """
    Generates formatted combat attributes from build totals
    Maps to Statistics.cs display methods

    This class DOES NOT calculate totals - it formats them for display.
    Totals come from Specs 19-24 (Build Totals).
    """

    # Soft cap thresholds
    DEFENSE_SOFT_CAP = 0.45  # 45%

    # Display color thresholds
    DEFENSE_EXCELLENT = 0.45  # Soft cap
    DEFENSE_GOOD = 0.35       # Close to cap
    DEFENSE_POOR = 0.20       # Significant gaps

    def __init__(self, archetype_name: str, archetype_caps: Dict[str, float]):
        """
        Initialize combat attributes calculator

        Args:
            archetype_name: Name of archetype (for display)
            archetype_caps: Dict of caps (resistance_cap, damage_cap, etc.)
        """
        self.archetype_name = archetype_name
        self.archetype_caps = archetype_caps

    def create_offense_category(
        self,
        damage_buff: float,
        tohit_buff: float,
        accuracy_buff: float,
        recharge_buff: float,
        endurance_discount: float,
        range_buff: float
    ) -> CombatAttributeCategory:
        """
        Create offense category from build totals

        Args:
            damage_buff: Total damage buff (1.0 = +100% damage)
            tohit_buff: Total to-hit buff (0.225 = +22.5% tohit)
            accuracy_buff: Total accuracy buff (0.15 = +15% accuracy)
            recharge_buff: Total recharge buff (1.25 = +125% recharge)
            endurance_discount: Total end reduction (0.35 = -35% end cost)
            range_buff: Total range buff (0.2 = +20% range)

        Returns:
            CombatAttributeCategory with offense stats
        """
        category = CombatAttributeCategory(
            category=StatCategory.OFFENSE,
            display_name="Offense"
        )

        # Damage (show with archetype cap)
        damage_cap = self.archetype_caps.get("damage_cap", 4.0)  # 400%
        damage_pct = (damage_buff + 1.0) * 100  # +100% base
        is_capped = damage_pct >= damage_cap * 100

        category.attributes.append(CombatAttribute(
            name="Damage",
            category=StatCategory.OFFENSE,
            value=damage_buff,
            display_value=f"+{damage_pct:.2f}%",
            tooltip=f"Damage buff: +{damage_pct:.2f}% ({self.archetype_name} cap: {damage_cap*100:.0f}%)",
            is_capped=is_capped,
            color="excellent" if is_capped else "good" if damage_pct > 200 else "normal"
        ))

        # To-Hit
        tohit_pct = tohit_buff * 100
        category.attributes.append(CombatAttribute(
            name="To-Hit",
            category=StatCategory.OFFENSE,
            value=tohit_buff,
            display_value=f"+{tohit_pct:.2f}%",
            tooltip=f"To-Hit buff: +{tohit_pct:.2f}% (added before hit check)",
            color="excellent" if tohit_pct >= 20 else "good" if tohit_pct >= 10 else "normal"
        ))

        # Accuracy
        accuracy_pct = accuracy_buff * 100
        category.attributes.append(CombatAttribute(
            name="Accuracy",
            category=StatCategory.OFFENSE,
            value=accuracy_buff,
            display_value=f"+{accuracy_pct:.2f}%",
            tooltip=f"Accuracy buff: +{accuracy_pct:.2f}% (multiplies final hit chance)",
            color="good" if accuracy_pct >= 10 else "normal"
        ))

        # Recharge (cap at 400%)
        recharge_pct = (recharge_buff + 1.0) * 100
        is_recharge_capped = recharge_pct >= 400
        category.attributes.append(CombatAttribute(
            name="Recharge",
            category=StatCategory.OFFENSE,
            value=recharge_buff,
            display_value=f"+{recharge_pct:.2f}%",
            tooltip=f"Recharge speed: +{recharge_pct:.2f}% (global cap: 400%)",
            is_capped=is_recharge_capped,
            color="excellent" if is_recharge_capped else "good" if recharge_pct > 200 else "normal"
        ))

        # Endurance Discount
        end_pct = endurance_discount * 100
        category.attributes.append(CombatAttribute(
            name="End Discount",
            category=StatCategory.OFFENSE,
            value=endurance_discount,
            display_value=f"-{end_pct:.2f}%",
            tooltip=f"Endurance cost reduction: -{end_pct:.2f}%",
            color="excellent" if end_pct >= 30 else "good" if end_pct >= 15 else "normal"
        ))

        # Range
        range_pct = range_buff * 100
        category.attributes.append(CombatAttribute(
            name="Range",
            category=StatCategory.OFFENSE,
            value=range_buff,
            display_value=f"+{range_pct:.2f}%",
            tooltip=f"Power range: +{range_pct:.2f}%",
            color="good" if range_pct >= 20 else "normal"
        ))

        return category

    def create_defense_category(
        self,
        defense_values: Dict[str, float],  # {"smashing": 0.45, "melee": 0.45, ...}
    ) -> CombatAttributeCategory:
        """
        Create defense category from build totals

        Args:
            defense_values: Dict of defense values by type (0.45 = 45%)

        Returns:
            CombatAttributeCategory with defense stats
        """
        category = CombatAttributeCategory(
            category=StatCategory.DEFENSE,
            display_name="Defense"
        )

        # Typed defense
        typed_order = ["smashing", "lethal", "fire", "cold", "energy", "negative", "psionic", "toxic"]
        for defense_type in typed_order:
            if defense_type in defense_values:
                value = defense_values[defense_type]
                pct = value * 100
                is_soft_capped = value >= self.DEFENSE_SOFT_CAP

                color = "excellent" if is_soft_capped else \
                       "good" if value >= self.DEFENSE_GOOD else \
                       "poor" if value < self.DEFENSE_POOR else "normal"

                suffix = " (Soft Cap)" if is_soft_capped else ""

                category.attributes.append(CombatAttribute(
                    name=defense_type.capitalize(),
                    category=StatCategory.DEFENSE,
                    value=value,
                    display_value=f"{pct:.2f}%{suffix}",
                    tooltip=f"{defense_type.capitalize()} defense: {pct:.2f}% (Soft cap: 45%)",
                    is_capped=is_soft_capped,
                    color=color
                ))

        # Positional defense
        positional_order = ["melee", "ranged", "aoe"]
        for defense_type in positional_order:
            if defense_type in defense_values:
                value = defense_values[defense_type]
                pct = value * 100
                is_soft_capped = value >= self.DEFENSE_SOFT_CAP

                color = "excellent" if is_soft_capped else \
                       "good" if value >= self.DEFENSE_GOOD else \
                       "poor" if value < self.DEFENSE_POOR else "normal"

                suffix = " (Soft Cap)" if is_soft_capped else ""

                category.attributes.append(CombatAttribute(
                    name=defense_type.capitalize(),
                    category=StatCategory.DEFENSE,
                    value=value,
                    display_value=f"{pct:.2f}%{suffix}",
                    tooltip=f"{defense_type.capitalize()} defense: {pct:.2f}% (Soft cap: 45%)",
                    is_capped=is_soft_capped,
                    color=color
                ))

        return category

    def create_resistance_category(
        self,
        resistance_values: Dict[str, float],  # {"smashing": 0.75, ...}
        uncapped_resistance: Dict[str, float] = None
    ) -> CombatAttributeCategory:
        """
        Create resistance category from build totals

        Args:
            resistance_values: Capped resistance by type (0.75 = 75%)
            uncapped_resistance: Uncapped values if overcapped

        Returns:
            CombatAttributeCategory with resistance stats
        """
        category = CombatAttributeCategory(
            category=StatCategory.DEFENSE,  # Resistance shown in defense section
            display_name="Resistance"
        )

        resistance_cap = self.archetype_caps.get("resistance_cap", 0.75)
        typed_order = ["smashing", "lethal", "fire", "cold", "energy", "negative", "psionic", "toxic"]

        for res_type in typed_order:
            if res_type in resistance_values:
                capped_value = resistance_values[res_type]
                uncapped_value = uncapped_resistance.get(res_type, capped_value) if uncapped_resistance else capped_value

                capped_pct = capped_value * 100
                uncapped_pct = uncapped_value * 100
                is_capped = capped_value >= resistance_cap
                is_overcapped = uncapped_value > capped_value

                if is_overcapped:
                    display = f"{uncapped_pct:.2f}% (capped at {resistance_cap*100:.0f}%)"
                    tooltip = f"{res_type.capitalize()} resistance: {uncapped_pct:.2f}% (capped at {resistance_cap*100:.0f}%)"
                else:
                    display = f"{capped_pct:.2f}%"
                    tooltip = f"{res_type.capitalize()} resistance: {capped_pct:.2f}% ({self.archetype_name} cap: {resistance_cap*100:.0f}%)"

                color = "excellent" if is_capped else \
                       "good" if capped_value >= resistance_cap * 0.8 else \
                       "normal"

                category.attributes.append(CombatAttribute(
                    name=res_type.capitalize(),
                    category=StatCategory.DEFENSE,
                    value=capped_value,
                    display_value=display,
                    tooltip=tooltip,
                    is_capped=is_capped,
                    uncapped_value=uncapped_value if is_overcapped else None,
                    color=color
                ))

        return category

    def create_complete_display(
        self,
        build_totals: Dict[str, any]  # All totals from Specs 19-24
    ) -> CombatAttributesDisplay:
        """
        Create complete combat attributes display

        Args:
            build_totals: Dict containing all build totals:
                - damage_buff, tohit_buff, accuracy_buff, etc.
                - defense_values (dict by type)
                - resistance_values (dict by type)
                - hp_max, regen_rate, etc.

        Returns:
            Complete CombatAttributesDisplay
        """
        display = CombatAttributesDisplay()

        # Create all categories
        display.categories.append(
            self.create_offense_category(
                damage_buff=build_totals.get("damage_buff", 0.0),
                tohit_buff=build_totals.get("tohit_buff", 0.0),
                accuracy_buff=build_totals.get("accuracy_buff", 0.0),
                recharge_buff=build_totals.get("recharge_buff", 0.0),
                endurance_discount=build_totals.get("endurance_discount", 0.0),
                range_buff=build_totals.get("range_buff", 0.0)
            )
        )

        display.categories.append(
            self.create_defense_category(
                defense_values=build_totals.get("defense_values", {})
            )
        )

        display.categories.append(
            self.create_resistance_category(
                resistance_values=build_totals.get("resistance_values", {}),
                uncapped_resistance=build_totals.get("uncapped_resistance", {})
            )
        )

        # TODO: Add other categories:
        # - Movement (run/jump/fly speed)
        # - Survivability (HP, regen, endurance, recovery)
        # - Status Protection (mez mag protection)
        # - Status Resistance (mez duration resistance)
        # - Debuff Resistance (DDR, etc.)
        # - Misc (perception, stealth, threat)

        return display

    def format_for_ui(self, display: CombatAttributesDisplay) -> Dict[str, any]:
        """
        Format combat attributes for UI rendering

        Args:
            display: CombatAttributesDisplay to format

        Returns:
            Dict suitable for JSON serialization and UI rendering
        """
        return {
            "categories": [
                {
                    "name": cat.display_name,
                    "category": cat.category.value,
                    "expanded": cat.expanded,
                    "attributes": [
                        {
                            "name": attr.name,
                            "value": attr.value,
                            "display_value": attr.display_value,
                            "tooltip": attr.tooltip,
                            "is_capped": attr.is_capped,
                            "uncapped_value": attr.uncapped_value,
                            "color": attr.color
                        }
                        for attr in cat.attributes
                    ]
                }
                for cat in display.categories
            ],
            "show_uncapped": display.show_uncapped,
            "show_base_comparison": display.show_base_comparison
        }
```

### Key Functions

**Core Functions**:
```python
def create_offense_category() -> CombatAttributeCategory
def create_defense_category() -> CombatAttributeCategory
def create_resistance_category() -> CombatAttributeCategory
def create_movement_category() -> CombatAttributeCategory
def create_survivability_category() -> CombatAttributeCategory
def create_status_protection_category() -> CombatAttributeCategory
def create_status_resistance_category() -> CombatAttributeCategory
def create_debuff_resistance_category() -> CombatAttributeCategory
def create_misc_category() -> CombatAttributeCategory

def create_complete_display() -> CombatAttributesDisplay
def format_for_ui() -> Dict[str, any]
```

**Helper Functions**:
```python
def determine_color(value: float, thresholds: Dict[str, float]) -> str
def format_percentage(value: float) -> str
def format_absolute(value: float, unit: str) -> str
def create_tooltip(name: str, value: float, cap: float, context: str) -> str
```

## Related Documentation

### Dependencies (Must Read First)
- Spec 19: Build Totals - HP & Absorb (HP display)
- Spec 20: Build Totals - Resistance (resistance display)
- Spec 21: Build Totals - Defense (defense display)
- Spec 22: Build Totals - Damage (damage buff display)
- Spec 23: Build Totals - Recharge (recharge display)
- Spec 24: Build Totals - Other Stats (movement, recovery, regen, etc.)
- Spec 16: Archetype Modifiers (base values)
- Spec 17: Archetype Caps (cap enforcement display)

### Dependents (Read After)
- Build comparison system (compare combat attributes side-by-side)
- Export functionality (export stats to text/JSON)
- Optimization algorithms (identify stat gaps)

### Related Specs
- Spec 01: Power Effects Core (source of effects that become stats)
- Spec 13: Enhancement Set Bonuses (major contributor to stats)

## References

- **MidsReborn Files**:
  - `Core/Statistics.cs` - Display calculation methods
  - `Core/Stats.cs` - Data structure for categorized stats
  - `Core/Base/Data_Classes/Character.cs` - Totals and DisplayStats
  - `Forms/WindowMenuItems/frmTotalsV2.cs` - UI display
  - `Forms/Controls/DataView.cs` - Display totals rendering
- **Game Documentation**:
  - City of Heroes Wiki: "Real Numbers", "Combat Attributes"
  - Paragon Wiki: "Combat Attributes Window"
