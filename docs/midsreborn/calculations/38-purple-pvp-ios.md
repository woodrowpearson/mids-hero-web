# Purple (Rare) and PvP IO Sets

## Overview
- **Purpose**: Handle special high-end enhancement sets with unique properties - Purple (Rare) sets and PvP IO sets
- **Used By**: Enhancement set bonus calculation, set selection UI, build optimization, Rule of 5 exemption logic
- **Complexity**: Medium
- **Priority**: Medium
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `Core/EnhancementSet.cs`
- **Method**: `GetEnhancementSetRarity()` (line 149-154)
- **Related Files**:
  - `Core/Recipe.cs` - `RecipeRarity` enum (lines 8-14)
  - `Core/Enums.cs` - `eSetType` enum (lines 952-1004)
  - `Core/DatabaseAPI.cs` - Purple set detection logic (lines 786-850)
  - `Forms/OptionsMenuItems/DbEditor/frmSetEditPvP.Designer.cs` - PvP set editor UI

### Set Rarity Classification

**Recipe Rarity Enum** (`Recipe.cs`, lines 8-14):
```csharp
public enum RecipeRarity
{
    Common,      // Standard IOs
    Uncommon,    // Uncommon IOs
    Rare,        // Rare IOs
    UltraRare    // Purple sets, PvP sets, ATOs, Winter sets
}
```

**Set Type Enum** (`Enums.cs`, lines 952-1004):
Purple and PvP sets are classified by power category (MeleeST, RangedAoE, Defense, etc.) AND by Archetype-specific types:
```csharp
public enum eSetType
{
    // Standard categories (0-35)
    Untyped, MeleeST, RangedST, RangedAoE, MeleeAoE, Snipe, Pets,
    Defense, Resistance, Heal, Hold, Stun, Immob, Slow, Sleep,
    Fear, Confuse, Flight, Jump, Run, Teleport, DefDebuff, EndMod,
    Knockback, Threat, ToHit, ToHitDeb, PetRech, Travel, AccHeal,
    AccDefDeb, AccToHitDeb, UniversalDamage,

    // Archetype-specific categories (36-47) - Used for ATOs and PvP sets
    Arachnos, Blaster, Brute, Controller, Corruptor, Defender,
    Dominator, Kheldian, Mastermind, Scrapper, Stalker, Tanker, Sentinel,

    // Travel without Sprint (48-51)
    RunNoSprint, JumpNoSprint, FlightNoSprint, TeleportNoSprint
}
```

### High-Level Algorithm

```
Purple Set Detection:
  1. Get enhancement from set (typically first enhancement)
  2. Look up Recipe for that enhancement
  3. Check Recipe.Rarity == RecipeRarity.UltraRare
  4. Filter out ATOs (SetType in Archetype range)
  5. Filter out Winter Event sets (by name pattern)
  6. Remaining UltraRare sets are Purple sets

PvP Set Detection:
  1. Check if set has PvP-specific editing UI (frmSetEditPvP)
  2. PvP sets have dual-aspect IOs (e.g., Accuracy/Damage/Endurance in one)
  3. PvP sets typically have 11 bonus slots vs 5 for standard sets
  4. Special bonus array: InitBonusPvP() resizes Bonus array to 11 items

Set Rarity Determination (EnhancementSet.GetEnhancementSetRarity):
  INPUT: EnhancementSet

  1. Get first enhancement index from Enhancements array
  2. Look up enhancement in Database.Enhancements
  3. Get RecipeIDX from enhancement
  4. Look up recipe in Database.Recipes
  5. Return recipe.Rarity.ToString()

  OUTPUT: "Common", "Uncommon", "Rare", or "UltraRare"

Purple IO Detection (DatabaseAPI.EnhIsSuperiorIO, lines 790-801):
  INPUT: enhIdx (enhancement index)

  1. Validate enhancement index
  2. Get enhancement data
  3. Get recipe data via RecipeIDX
  4. Check: Rarity == UltraRare AND NOT ATO AND NOT WinterEvent
  5. Return boolean

  OUTPUT: True if Purple IO, False otherwise

Rule of 5 Exemption:
  Purple and PvP sets are EXEMPT from Rule of 5 suppression
  - Each unique Purple set counts separately
  - Each unique PvP set counts separately
  - Standard sets: Only 5 instances of same bonus type count
  - Purple/PvP: ALL instances count, no suppression

  Example:
    - 5x Apocalypse set bonuses: All 5 count (exempt)
    - 3x Ragnarok set bonuses: All 3 count (exempt)
    - 8x Crushing Impact set bonuses: Only 5 count (not exempt)
```

### Purple Sets (11 total)

Based on MidsReborn's purple set detection logic filtering UltraRare sets:

**Damage Sets**:
1. **Apocalypse** - Ranged Damage
2. **Armageddon** - PBAoE Damage
3. **Ragnarok** - Targeted AoE Damage
4. **Hecatomb** - Melee Damage
5. **Fury of the Gladiator** - PBAoE Damage (overlaps with PvP category)

**Control/Support Sets**:
6. **Fortunata Hypnosis** - Sleep
7. **Coercive Persuasion** - Confuse
8. **Unbreakable Constraint** - Hold
9. **Absolute Amazement** - Stun
10. **Gravitational Anchor** - Immobilize

**Other Purple Sets**:
11. **Shield Wall** - Defense (possibly) OR other purple sets

**Characteristics**:
- Level 50 only (LevelMin=50, LevelMax=50)
- Superior set bonuses (typically 50-100% higher than standard IOs)
- NO exemplar penalty (bonuses work at all levels)
- CAN be boosted with enhancement boosters
- Drop only from level 50+ enemies (no recipes to craft)
- RecipeRarity = UltraRare
- SetType matches power category (MeleeST, RangedAoE, etc.)

### PvP Sets (7+ total)

Based on MidsReborn's PvP set editor and special handling:

**Archetype-Specific PvP Sets**:
1. **Gladiator's Armor** - Defense/Resistance (Archetype-specific)
2. **Gladiator's Strike** - Melee attacks
3. **Javelin Volley** - Ranged attacks
4. **Fury of the Gladiator** - PBAoE attacks
5. **Panacea** - Healing
6. **Shield Wall** - Defense (if not Purple)
7. **Other Gladiator variants** - Various categories

**Characteristics**:
- Dual-aspect IOs (one enhancement affects multiple attributes)
  - Example: Accuracy/Damage/Endurance all in single IO
- Work in BOTH PvP AND PvE contexts
- NO exemplar penalty (bonuses work at all levels)
- 11 bonus slots (standard sets have 5)
  - InitBonusPvP() method resizes Bonus array to 11
- RecipeRarity = UltraRare
- Separate editor UI (frmSetEditPvP) vs standard set editor
- SetType can include Archetype-specific values (Arachnos, Blaster, etc.)
- Special PvMode handling (BonusItem.PvMode field)

### Dependencies

**Used By**:
- Set bonus aggregation system (must know which sets exempt from Rule of 5)
- Enhancement slot UI (display rarity colors/borders)
- Build optimization (purple/PvP sets valued differently)
- Exemplar calculation (these sets don't lose bonuses when exemplared)

**Depends On**:
- Enhancement database (enhancement to recipe mapping)
- Recipe database (rarity classification)
- Set type enum (category classification)

## Game Mechanics Context

**Why This Exists:**

City of Heroes has three tiers of high-end IO sets, each with special properties:

1. **Standard IO Sets**: Common/Uncommon/Rare recipes, work well, subject to Rule of 5
2. **Purple IO Sets**: Ultra-rare level 50 drops, superior bonuses, Rule of 5 exempt
3. **PvP IO Sets**: Ultra-rare PvP reward drops, dual-aspect enhancements, Rule of 5 exempt

The distinction matters because:
- **Build Planning**: Purple/PvP sets allow stacking multiple copies without suppression
- **Exemplaring**: Purple/PvP bonuses work at ALL levels, standard sets lose bonuses when exemplared below set level
- **Enhancement Boosting**: Purple sets CAN be boosted (unlike attuned IOs), increasing values +5 levels
- **Acquisition**: Purple sets drop randomly at 50+, PvP sets from PvP rewards, both very rare

**Historical Context:**

- **Issue 9 (May 2007)**: Invention Origin system introduced IO sets with Rule of 5 to prevent excessive stacking
- **Issue 12 (May 2008)**: Purple IO sets added as ultra-rare level 50+ drops, exempt from Rule of 5 to reward dedicated players
- **Issue 13 (December 2008)**: PvP IO sets added to incentivize PvP participation, also exempt from Rule of 5
- **Issue 18+ (2010-2012)**: Additional purple and PvP sets added to expand variety
- **Homecoming Era (2019+)**: Purple and PvP sets remain prestigious endgame goals, balanced by extreme rarity

**Design Philosophy**:
- Purple sets: Reward for endgame grinding (level 50+ content)
- PvP sets: Reward for PvP participation (arena/zone PvP)
- Both provide significant power increases while maintaining game balance through rarity
- Rule of 5 exemption allows creative build diversity without power creep

**Known Quirks:**

1. **PvP IO Dual Aspects**: A single PvP IO can enhance 3+ attributes (Acc/Dam/End), making them extremely slot-efficient. Standard IOs enhance 1-2 attributes maximum.

2. **Purple Set Level Requirement**: Purple sets are ONLY level 50, no level ranges. This is intentional - they represent "peak performance" enhancements.

3. **Rule of 5 Exemption Stacking**: You can slot 6x Apocalypse sets if you have enough power slots, and ALL set bonuses count. This is working as designed to reward players with full purple builds.

4. **Attuned vs Boosted**: Purple IOs CAN be boosted (+5 levels) but CANNOT be attuned. ATOs and Winter sets CAN be attuned but are already automatically scaled. This distinction affects optimal slotting strategies.

5. **PvP Set Category Overlap**: Some PvP sets (Gladiator's Armor) are categorized by Archetype (Tanker, Scrapper, etc.) rather than by power type (Defense, Resistance). This requires special handling in set selection UI.

6. **Rarity Color Coding**: In MidsReborn UI, sets are color-coded by rarity:
   - Common: White
   - Uncommon: Yellow
   - Rare: Orange
   - UltraRare (Purple/PvP): Purple/Red borders

7. **No Exemplar Loss**: Purple and PvP sets violate the normal exemplar rule where you lose set bonuses if you exemplar below (set level - 3). These sets work at ALL levels, even if you exemplar to level 1.

8. **Enhancement Boosters**: Purple sets can use enhancement boosters to get +5 level shift (50+5=55), increasing enhancement values by ~10%. This makes them even stronger than base purple IOs.

## Python Implementation Notes

### Proposed Architecture

**Set Rarity System**:
```python
from enum import Enum
from dataclasses import dataclass

class RecipeRarity(Enum):
    """Enhancement recipe rarity classification."""
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    ULTRA_RARE = 3  # Purple, PvP, ATO, Winter

class SetCategory(Enum):
    """Enhancement set special category."""
    STANDARD = "standard"      # Normal IO set
    PURPLE = "purple"          # Level 50 rare set
    PVP = "pvp"               # PvP reward set
    ATO = "ato"               # Archetype Origin
    WINTER = "winter"         # Winter Event set

@dataclass
class EnhancementSet:
    """Enhancement set with rarity classification."""
    uid: str
    display_name: str
    short_name: str
    set_type: str  # From eSetType enum
    level_min: int
    level_max: int
    rarity: RecipeRarity
    category: SetCategory
    enhancements: list[int]  # Enhancement indices
    bonuses: list[SetBonus]
    special_bonuses: list[SetBonus]

    def is_purple(self) -> bool:
        """Check if this is a Purple (rare) IO set."""
        return self.category == SetCategory.PURPLE

    def is_pvp(self) -> bool:
        """Check if this is a PvP IO set."""
        return self.category == SetCategory.PVP

    def is_rule_of_5_exempt(self) -> bool:
        """Check if this set is exempt from Rule of 5 suppression."""
        return self.category in (SetCategory.PURPLE, SetCategory.PVP)

    def works_when_exemplared(self) -> bool:
        """Check if set bonuses work at all levels when exemplared."""
        # Purple and PvP sets have no exemplar penalty
        return self.is_rule_of_5_exempt()

    def can_be_boosted(self) -> bool:
        """Check if enhancements can receive booster +5 treatment."""
        # Purple sets can be boosted, but ATOs/Winter are attuned
        return self.category == SetCategory.PURPLE

@dataclass
class SetBonus:
    """Individual set bonus for slotting N enhancements."""
    slotted_count: int  # 2, 3, 4, 5, 6 pieces slotted
    bonus_index: int
    pv_mode: str  # "Any", "PvE", "PvP"
    effects: list[Effect]  # Actual bonus effects
    alt_string: str = ""  # Alternative display text
```

### Key Functions

```python
def classify_set_category(
    enhancement_set: EnhancementSet,
    recipes: dict[int, Recipe],
    enhancements: dict[int, Enhancement]
) -> SetCategory:
    """
    Determine special category for enhancement set.

    Algorithm:
    1. Get first enhancement from set
    2. Look up recipe rarity
    3. If not UltraRare, return STANDARD
    4. If UltraRare, check set type and name patterns:
       - Archetype-specific SetType (36-47) -> ATO
       - Name contains "Winter" or seasonal -> WINTER
       - Has PvP-specific bonuses -> PVP
       - Otherwise -> PURPLE

    Returns:
        SetCategory enum value
    """
    pass

def is_rule_of_5_exempt(enhancement_set: EnhancementSet) -> bool:
    """
    Check if set is exempt from Rule of 5 suppression.

    Purple and PvP sets are exempt - each unique set counts separately
    in set bonus stacking, with no suppression limit.

    Returns:
        True if Purple or PvP set, False otherwise
    """
    return enhancement_set.category in (SetCategory.PURPLE, SetCategory.PVP)

def calculate_exemplar_set_bonuses(
    slotted_sets: list[EnhancementSet],
    current_level: int,
    exemplar_level: int | None
) -> list[Effect]:
    """
    Calculate set bonuses accounting for exemplar level.

    Standard sets: Lose bonuses if exemplar < (set_level - 3)
    Purple/PvP sets: Keep ALL bonuses regardless of exemplar level

    Algorithm:
    1. For each slotted set:
       a. If is_rule_of_5_exempt(): Include ALL bonuses
       b. Else: Check exemplar_level >= (set.level_min - 3)
    2. Apply Rule of 5 suppression to standard sets only
    3. Return aggregated effect list

    Returns:
        List of active set bonus effects
    """
    pass

def get_purple_sets() -> list[str]:
    """
    Return list of Purple IO set names.

    Returns:
        List of 11 purple set UIDs/names
    """
    return [
        "Apocalypse",
        "Armageddon",
        "Ragnarok",
        "Hecatomb",
        "Fortunata_Hypnosis",
        "Coercive_Persuasion",
        "Unbreakable_Constraint",
        "Absolute_Amazement",
        "Gravitational_Anchor",
        # Additional purple sets discovered during data import
    ]

def get_pvp_sets() -> list[str]:
    """
    Return list of PvP IO set names.

    Returns:
        List of 7+ PvP set UIDs/names
    """
    return [
        "Gladiators_Armor",
        "Gladiators_Strike",
        "Javelin_Volley",
        "Fury_of_the_Gladiator",
        "Panacea",
        # Additional PvP sets discovered during data import
    ]
```

### Data Structure Design

```python
# Set bonus tracking for Rule of 5 exemption
@dataclass
class SetBonusTracker:
    """Track set bonuses for Rule of 5 calculation."""
    bonus_type: str  # e.g., "defense_all", "recharge"
    magnitude: float
    source_set: EnhancementSet
    is_exempt: bool  # Purple/PvP sets are exempt

    def should_count_for_rule_of_5(self, existing_count: int) -> bool:
        """
        Determine if this bonus should count given existing bonuses.

        Returns:
            True if exempt OR existing_count < 5
        """
        return self.is_exempt or existing_count < 5

# PvP IO multi-aspect tracking
@dataclass
class PvPEnhancement:
    """PvP IO with multiple aspects in single enhancement."""
    enhancement_id: int
    aspects: list[str]  # e.g., ["Accuracy", "Damage", "Endurance"]
    schedules: dict[str, str]  # Aspect -> Schedule mapping

    def get_all_aspects(self) -> list[str]:
        """Return all aspects this single IO enhances."""
        return self.aspects
```

### Integration Points

1. **Set Bonus Aggregation**: Check `is_rule_of_5_exempt()` before applying suppression
2. **Exemplar Calculation**: Call `works_when_exemplared()` to determine bonus retention
3. **Enhancement Boosting**: Check `can_be_boosted()` before applying +5 level shift
4. **UI Display**: Use `category` for color coding and special badges
5. **Build Optimization**: Weight purple/PvP sets higher due to Rule of 5 exemption

### Testing Considerations

**Test Cases to Verify**:
1. Purple set detection from UltraRare recipe classification
2. PvP set detection from set type and editor metadata
3. Rule of 5 exemption: 6x same purple set all count
4. Rule of 5 normal: 6x same standard set only 5 count
5. Exemplar behavior: Purple/PvP bonuses at level 1, standard sets lose bonuses
6. Enhancement boosting: Purple sets accept boosters, attuned sets do not
7. PvP IO multi-aspect: Single IO enhances 3 different schedules

**Edge Cases**:
- Fury of the Gladiator (both Purple AND PvP category?)
- Archetype-specific PvP sets (SetType in 36-47 range)
- Mixed purple/standard set builds (rule of 5 per set, not global)

---

**Document Status**: 🟡 Breadth Complete - High-level algorithm and data structures defined
**Next Phase**: Depth specification in Milestone 3 (if Medium priority promoted to High)
**Dependencies**: Enhancement sets (Spec 28), Rule of 5 suppression (Spec 32), Exemplar system (Spec 33)
