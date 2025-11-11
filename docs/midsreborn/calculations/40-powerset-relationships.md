# Powerset Relationships

## Overview
- **Purpose**: Cross-powerset synergies, combo systems, mode-based power modifications (Dual Pistols ammo, Staff Fighting forms, Bio Armor adaptations)
- **Used By**: Powerset-specific mechanics, combo tracking systems, mode-dependent effect calculations
- **Complexity**: Medium-High
- **Priority**: Low
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/Base/Data_Classes/Character.cs` (mode tracking)
- **File**: `Core/Base/Data_Classes/Effect.cs` (conditional effect evaluation)
- **File**: `Core/Enums.cs` (`eSpecialCase` enum - lines 1006-1071)
- **Related Files**:
  - `BuildImportTools.cs` - Excludes mode toggle powers from import (lines 23-36)

### Mode and State Tracking

The `Character` class tracks various powerset-specific states:

**Bio Armor Adaptations** (lines 154-162, 690-700):
```csharp
public bool DefensiveAdaptation { get; private set; }
public bool EfficientAdaptation { get; private set; }
public bool OffensiveAdaptation { get; private set; }
public bool NotDefensiveAdaptation { get; private set; }
public bool NotDefensiveNorOffensiveAdaptation { get; private set; }
```

**Staff Fighting Forms** (lines 681-689):
```csharp
case "FORM_OF_THE_BODY":
    PerfectionType = "body";
case "FORM_OF_THE_MIND":
    PerfectionType = "mind";
case "FORM_OF_THE_SOUL":
    PerfectionType = "soul";
```

**Other Powerset States**:
- `Supremacy` - Mastermind inherent
- `PackMentality` / `NotPackMentality` - Beast Mastery
- `FastSnipe` / `NotFastSnipe` - Snipe instant-cast mode
- `PetTier2` / `PetTier3` - Mastermind upgrade states

### Special Case System

The `eSpecialCase` enum (lines 1006-1071) defines conditional effect triggers:

**Combo Systems**:
- `ComboLevel0`, `ComboLevel1`, `ComboLevel2`, `ComboLevel3` - Combo point tracking (Street Justice, Dual Blades)
- `NotComboLevel3` - Effects active when NOT at max combo

**Bio Armor Modes**:
- `DefensiveAdaptation` - Active in Defensive mode
- `EfficientAdaptation` - Active in Efficient mode
- `OffensiveAdaptation` - Active in Offensive mode
- `NotDefensiveAdaptation` - Active when NOT in Defensive
- `NotDefensiveNorOffensiveAdaptation` - Active only in Efficient mode

**Staff Fighting Forms**:
- `PerfectionOfBody0`-`PerfectionOfBody3` - Body form stack levels
- `PerfectionOfMind0`-`PerfectionOfMind3` - Mind form stack levels
- `PerfectionOfSoul0`-`PerfectionOfSoul3` - Soul form stack levels

**Beam Rifle States**:
- `NotDisintegrated` / `Disintegrated` - Target has Disintegration debuff
- `NotAccelerated` / `Accelerated` - Beam accelerated state
- `NotDelayed` / `Delayed` - Beam delayed state

**Fighting Pool Synergies**:
- `BoxingBuff` / `NotBoxingBuff` - Cross Punch synergy with Boxing
- `KickBuff` / `NotKickBuff` - Cross Punch synergy with Kick
- `CrossPunchBuff` / `NotCrossPunchBuff` - Reverse synergy

**Other Mechanics**:
- `FastMode` - Titan Weapons Momentum (reduces animation times)
- `ToHit97` - Effects active only at high ToHit (97%+)
- `TeamSize1`, `TeamSize2`, `TeamSize3` - Team size-dependent effects

### Effect Conditional Evaluation

`Effect.cs` evaluates these conditions in `GetConditionalMagnitude()` and `GetConditionalProc()` methods (lines 1876-2104, 2253-2400+):

```csharp
if (SpecialCase != Enums.eSpecialCase.None)
{
    switch (SpecialCase)
    {
        case Enums.eSpecialCase.DefensiveAdaptation:
            if (MidsContext.Character.DefensiveAdaptation)
                return Magnitude;
            return 0f;

        case Enums.eSpecialCase.ComboLevel3:
            // Effect only active at max combo points
            return Magnitude;

        case Enums.eSpecialCase.PerfectionOfBody2:
            if (MidsContext.Character.PerfectionType == "body")
                return Magnitude * (2 + 1); // Stack level 2
            return 0f;
    }
}
```

### Excluded Powers

`BuildImportTools.cs` excludes mode toggle powers from build imports since they're mutually exclusive:

```csharp
protected string[] ExcludePowers { get; } = {
    "Efficient_Adaptation", "Defensive_Adaptation", "Offensive_Adaptation", // Bio Armor
    "Form_of_the_Body", "Form_of_the_Mind", "Form_of_the_Soul", // Staff Fighting
    "Ammunition", // Dual Pistols ammo swap toggle
    // ... other inherent/auto powers
};
```

### High-Level Algorithm

```
Powerset Relationship Evaluation:
  1. Character state tracking:
     - Track active mode (Bio Armor adaptation, Staff Fighting form, etc.)
     - Track combo points (0-3 for Street Justice/Dual Blades)
     - Track conditional states (Disintegrated, Accelerated, FastMode, etc.)
     - Track team size, ToHit, pet upgrade levels

  2. Effect conditional evaluation:
     FOR each effect in power:
       IF effect.SpecialCase != None:
         CHECK character state against SpecialCase condition
         IF condition met:
           Apply effect with full magnitude
         ELSE:
           Skip effect (magnitude = 0)
       ELSE:
         Apply effect unconditionally

  3. Mode toggle handling:
     - Only ONE mode active per powerset (mutually exclusive)
     - Switching modes deactivates previous mode
     - Example: Bio Armor can be Defensive OR Efficient OR Offensive, never multiple

  4. Combo point tracking:
     - Certain powers grant combo points (0-3)
     - Other powers consume/require combo points
     - Effects scale with combo level (ComboLevel0 through ComboLevel3)

  5. Form/stack tracking (Staff Fighting):
     - Each form (Body/Mind/Soul) has stack levels (0-3)
     - Effects scale with stack level
     - Switching forms resets stacks to 0

  6. State-dependent power behavior:
     - Dual Pistols: Ammo swap changes damage type of ALL attacks
     - Titan Weapons: Momentum reduces cast times while active
     - Beam Rifle: Powers behave differently vs Disintegrated targets
     - Water Blast: Tidal Power changes cone to single-target and vice versa
```

## Game Mechanics Context

**Why This Exists:**

Many City of Heroes powersets have internal synergies or mode-based mechanics that change how powers behave:

1. **Mode Systems**: Some powersets have mutually exclusive modes that alter all other powers in the set
   - Bio Armor: Choose Defensive (more resist/defense), Efficient (less endurance cost), or Offensive (more damage)
   - Staff Fighting: Build stacks in Body/Mind/Soul forms for different bonuses
   - Dual Pistols: Swap ammo types to change damage type of all attacks

2. **Combo Systems**: Powers that build up points and others that consume them
   - Street Justice: Build combo points with fast attacks, spend on finishers for extra damage
   - Dual Blades: Attack chains grant combo bonuses based on sequence used
   - Savage Melee: Blood Frenzy stacks modify power behavior

3. **Conditional Effects**: Powers that behave differently based on target/character state
   - Beam Rifle: Extra damage vs targets with Disintegration debuff
   - Titan Weapons: Momentum state reduces animation times
   - Water Blast: Tidal Power changes AoE pattern of attacks

**Historical Context:**

- **Launch (2004)**: Original game had simple powersets with no internal synergies
- **Issue 11 (2007)**: Dual Blades introduced first combo system
- **Issue 16 (2009)**: Dual Pistols added first mode-swap mechanic (ammo types)
- **Issue 21 (2011)**: Street Justice refined combo system with visible combo point tracking
- **Issue 22 (2012)**: Staff Fighting added form stacking system
- **Issue 24 (2013)**: Titan Weapons introduced momentum mechanic
- **Homecoming (2019+)**: Bio Armor added adaptation modes, Beam Rifle added conditional mechanics

**Known Quirks:**

1. **Mode exclusivity not enforced in data**: Bio Armor adaptations are three separate toggle powers. The game engine enforces mutual exclusivity, but the power data doesn't explicitly show this. MidsReborn tracks which mode is active via character state.

2. **Combo points are ephemeral**: Unlike other buffs, combo points aren't persistent effects - they're state tracked by the engine. MidsReborn uses `eSpecialCase.ComboLevel0-3` to simulate effects at different combo levels.

3. **Dual Pistols ammo swap is complex**: The "Swap Ammo" power doesn't directly modify other powers. Instead, each attack power has THREE complete effect sets (one per ammo type), and the active ammo determines which set applies. This triplicates effect data.

4. **Staff Fighting forms stack**: Unlike Bio Armor modes (which are mutually exclusive), Staff Fighting forms STACK. You can have 3 stacks of Body form for maximum effect. Each stack level has a separate `SpecialCase` value.

5. **Titan Weapons Momentum is time-limited**: Momentum doesn't last forever - it has a duration. MidsReborn uses `FastMode` to represent "has Momentum active" but doesn't model the decay timer.

6. **Cross-power synergies**: Fighting pool has unique synergies where taking Boxing AND Kick makes Cross Punch stronger. This requires tracking which powers are taken in the build, not just which are active.

7. **Set bonuses can be powerset-specific**: Some IO set bonuses say "+10% recharge to Fire Blast powers" or "+5% defense to Pets". These require checking the powerset of each power when applying bonuses. Not yet implemented in MidsReborn.

8. **Mastermind pet upgrades are global**: Taking "Equip Robot" affects ALL robot pets, even future ones. The upgrade state is tracked on the character, not per-pet.

## Python Implementation Notes

### Proposed Architecture

```python
# dataclasses for powerset state tracking
@dataclass
class PowersetState:
    """Tracks mode-based and conditional states for powersets"""

    # Bio Armor adaptations (mutually exclusive)
    defensive_adaptation: bool = False
    efficient_adaptation: bool = False
    offensive_adaptation: bool = False

    # Staff Fighting forms and stacks
    perfection_type: str | None = None  # "body", "mind", "soul", or None
    perfection_stacks: int = 0  # 0-3

    # Combo point tracking
    combo_level: int = 0  # 0-3 (Street Justice, Dual Blades)

    # Beam Rifle states
    disintegrated: bool = False
    accelerated: bool = False
    delayed: bool = False

    # Titan Weapons momentum
    fast_mode: bool = False  # Has Momentum active

    # Fighting pool synergies
    has_boxing: bool = False
    has_kick: bool = False
    has_cross_punch: bool = False

    # Mastermind states
    supremacy: bool = False
    pet_tier2_upgrade: bool = False  # Has Equip/Train power
    pet_tier3_upgrade: bool = False  # Has Upgrade power

    # Beast Mastery
    pack_mentality: bool = False

    # Sniper mechanics
    fast_snipe: bool = False  # Has 22%+ ToHit bonus for instant snipes

    # Team/target context
    team_size: int = 1  # 1-8
    tohit_percent: float = 75.0  # For ToHit97 condition

    def set_adaptation(self, mode: str) -> None:
        """Set Bio Armor adaptation (mutually exclusive)"""
        self.defensive_adaptation = (mode == "defensive")
        self.efficient_adaptation = (mode == "efficient")
        self.offensive_adaptation = (mode == "offensive")

    def set_staff_form(self, form: str, stacks: int = 0) -> None:
        """Set Staff Fighting form and stack level"""
        if form in ("body", "mind", "soul"):
            self.perfection_type = form
            self.perfection_stacks = min(max(stacks, 0), 3)
        else:
            self.perfection_type = None
            self.perfection_stacks = 0

    def track_combo_points(self, level: int) -> None:
        """Set combo level (0-3)"""
        self.combo_level = min(max(level, 0), 3)


@dataclass
class ConditionalEffect:
    """Effect that only applies under certain conditions"""

    effect_type: str
    magnitude: float
    special_case: str  # From eSpecialCase enum

    def evaluate_condition(self, state: PowersetState) -> bool:
        """Check if condition is met given current powerset state"""
        match self.special_case:
            case "DefensiveAdaptation":
                return state.defensive_adaptation
            case "EfficientAdaptation":
                return state.efficient_adaptation
            case "OffensiveAdaptation":
                return state.offensive_adaptation
            case "ComboLevel0":
                return state.combo_level == 0
            case "ComboLevel1":
                return state.combo_level == 1
            case "ComboLevel2":
                return state.combo_level == 2
            case "ComboLevel3":
                return state.combo_level == 3
            case "NotComboLevel3":
                return state.combo_level < 3
            case "PerfectionOfBody0":
                return state.perfection_type == "body" and state.perfection_stacks == 0
            case "PerfectionOfBody1":
                return state.perfection_type == "body" and state.perfection_stacks >= 1
            case "PerfectionOfBody2":
                return state.perfection_type == "body" and state.perfection_stacks >= 2
            case "PerfectionOfBody3":
                return state.perfection_type == "body" and state.perfection_stacks >= 3
            # ... similar for Mind and Soul forms
            case "Disintegrated":
                return state.disintegrated
            case "NotDisintegrated":
                return not state.disintegrated
            case "FastMode":
                return state.fast_mode
            case "BoxingBuff":
                return state.has_boxing
            case "KickBuff":
                return state.has_kick
            case "CrossPunchBuff":
                return state.has_cross_punch
            case "Supremacy":
                return state.supremacy
            case "PetTier2":
                return state.pet_tier2_upgrade
            case "PetTier3":
                return state.pet_tier3_upgrade
            case "PackMentality":
                return state.pack_mentality
            case "FastSnipe":
                return state.fast_snipe
            case "TeamSize1":
                return state.team_size >= 1
            case "TeamSize2":
                return state.team_size >= 2
            case "TeamSize3":
                return state.team_size >= 3
            case "ToHit97":
                return state.tohit_percent >= 97.0
            case _:
                return True  # Unknown conditions default to active

    def get_magnitude(self, state: PowersetState) -> float:
        """Get effective magnitude based on condition evaluation"""
        if self.evaluate_condition(state):
            # Special handling for stacking forms
            if "Perfection" in self.special_case and state.perfection_stacks > 0:
                # Magnitude scales with stack level
                # PerfectionOfBody2 means "at 2+ stacks", multiply by (stacks)
                if "2" in self.special_case:
                    return self.magnitude * 2
                elif "3" in self.special_case:
                    return self.magnitude * 3
                elif "1" in self.special_case:
                    return self.magnitude * 1
            return self.magnitude
        return 0.0


class PowersetRelationshipCalculator:
    """Handles cross-powerset synergies and conditional mechanics"""

    def __init__(self):
        self.state = PowersetState()

    def update_from_build(self, build: 'CharacterBuild') -> None:
        """Update powerset state based on active powers in build"""

        # Check for Bio Armor modes
        if build.has_power("Defensive_Adaptation"):
            self.state.set_adaptation("defensive")
        elif build.has_power("Efficient_Adaptation"):
            self.state.set_adaptation("efficient")
        elif build.has_power("Offensive_Adaptation"):
            self.state.set_adaptation("offensive")

        # Check for Staff Fighting forms (assumes last activated)
        if build.has_power("Form_of_the_Body"):
            self.state.set_staff_form("body", stacks=1)  # Default to 1 stack
        elif build.has_power("Form_of_the_Mind"):
            self.state.set_staff_form("mind", stacks=1)
        elif build.has_power("Form_of_the_Soul"):
            self.state.set_staff_form("soul", stacks=1)

        # Check for Fighting pool powers
        self.state.has_boxing = build.has_power("Boxing")
        self.state.has_kick = build.has_power("Kick")
        self.state.has_cross_punch = build.has_power("Cross_Punch")

        # Check for Mastermind upgrades
        if build.archetype == "Mastermind":
            # Check for tier 2 upgrade power (varies by primary)
            tier2_powers = [
                "Equip_Mercenary", "Equip_Robot", "Equip_Thugs",
                "Enchant_Demon", "Enchant_Undead", "Train_Beasts", "Train_Ninjas"
            ]
            self.state.pet_tier2_upgrade = any(build.has_power(p) for p in tier2_powers)

            # Check for tier 3 upgrade power
            tier3_powers = [
                "Tactical_Upgrade", "Upgrade_Robot", "Upgrade_Equipment",
                "Abyssal_Empowerment", "Dark_Empowerment", "Tame_Beasts", "Kuji_In_Zen"
            ]
            self.state.pet_tier3_upgrade = any(build.has_power(p) for p in tier3_powers)

            self.state.supremacy = True  # Mastermind inherent

        # Check for Beast Mastery
        if build.has_power("Pack_Mentality"):
            self.state.pack_mentality = True

    def calculate_conditional_effects(
        self,
        power: 'Power',
        combo_level: int = 0,
        target_disintegrated: bool = False
    ) -> list[Effect]:
        """
        Calculate which conditional effects are active for a power

        Args:
            power: The power being evaluated
            combo_level: Current combo point level (0-3)
            target_disintegrated: Whether target has Disintegration debuff

        Returns:
            List of active effects with magnitudes adjusted for conditions
        """

        # Update conditional states
        self.state.track_combo_points(combo_level)
        self.state.disintegrated = target_disintegrated

        active_effects = []

        for effect in power.effects:
            if isinstance(effect, ConditionalEffect):
                magnitude = effect.get_magnitude(self.state)
                if magnitude > 0:
                    # Create active effect with conditional magnitude
                    active_effects.append(
                        Effect(
                            effect_type=effect.effect_type,
                            magnitude=magnitude,
                            duration=effect.duration,
                            # ... other properties
                        )
                    )
            else:
                # Unconditional effect, always active
                active_effects.append(effect)

        return active_effects

    def get_dual_pistols_effects(
        self,
        power: 'Power',
        ammo_type: str = "standard"
    ) -> list[Effect]:
        """
        Get effects for Dual Pistols power based on active ammo type

        Args:
            power: The Dual Pistols attack power
            ammo_type: "standard", "incendiary", or "cryo"

        Returns:
            List of effects for the specified ammo type
        """

        # Dual Pistols powers have multiple effect sets
        # Each ammo type activates a different set

        if ammo_type == "incendiary":
            # Fire damage + DoT
            return power.incendiary_effects
        elif ammo_type == "cryo":
            # Cold damage + -Recharge/-Speed
            return power.cryo_effects
        else:
            # Standard: Lethal damage
            return power.standard_effects
```

### Key Functions

1. **`PowersetState.set_adaptation(mode)`**: Set Bio Armor mode (mutually exclusive)
2. **`PowersetState.set_staff_form(form, stacks)`**: Set Staff Fighting form and stack level
3. **`PowersetState.track_combo_points(level)`**: Update combo level for combo systems
4. **`ConditionalEffect.evaluate_condition(state)`**: Check if effect's condition is met
5. **`ConditionalEffect.get_magnitude(state)`**: Get effective magnitude (0 if condition not met)
6. **`PowersetRelationshipCalculator.update_from_build(build)`**: Scan build for mode toggles
7. **`PowersetRelationshipCalculator.calculate_conditional_effects(power, ...)`**: Get active effects
8. **`PowersetRelationshipCalculator.get_dual_pistols_effects(power, ammo_type)`**: Handle ammo swap

### Integration Points

- **Spec 01 (Power Effects Core)**: Conditional effects extend base Effect system
- **Spec 18 (Inherent Powers)**: Fury, Domination bars use similar state tracking
- **Spec 03 (Damage Calculation)**: Combo levels affect damage magnitude
- **Spec 10 (Set Bonuses)**: Future powerset-specific set bonuses will use this system

### Testing Considerations

1. **Mode exclusivity**: Verify only one Bio Armor adaptation can be active
2. **Combo point boundary**: Test combo level 0, 1, 2, 3 (no overflow to 4)
3. **Form stacking**: Verify Staff Fighting forms stack correctly (0-3 stacks)
4. **Effect magnitude scaling**: Confirm PerfectionOfBody2 multiplies by 2
5. **Dual Pistols ammo swap**: Test all three ammo types produce different effects
6. **Mastermind upgrades**: Verify pet effects change based on upgrade powers taken
7. **Fighting pool synergies**: Confirm Cross Punch is stronger with Boxing AND Kick

### Future Extensions (Milestone 3)

- **Dual Pistols full implementation**: Model all three ammo effect sets per power
- **Water Blast Tidal Power**: Track which powers are modified by tidal state
- **Titan Weapons Momentum duration**: Model momentum decay timer
- **Powerset-specific set bonuses**: "+10% recharge to Fire Blast powers"
- **Stance/form UI tracking**: Allow user to select active mode in planner
- **Combo simulation**: Model optimal combo point usage in rotation
