# Power Accuracy/ToHit

## Overview
- **Purpose**: Calculate hit chance for attack powers, distinguishing between accuracy (multiplicative) and tohit (additive) mechanics
- **Used By**: Power tooltips, attack chance displays, combat effectiveness calculations, build optimization
- **Complexity**: Medium
- **Priority**: Critical
- **Status**: 🟡 Breadth Complete

## MidsReborn Implementation

### Primary Location
- **File**: `clsToonX.cs`
- **Method**: `GBPA_Pass4_ApplyAccuracy(ref IPower powerMath, ref IPower powerBuffed)`
- **Related Files**:
  - `Core/Enhancement.cs` - `ApplyED()` and `GetSchedule()` for accuracy enhancements
  - `Core/ConfigData.cs` - `ScalingToHit` property
  - `Core/ServerData.cs` - `BaseToHit` constant (default: 0.75 = 75%)
  - `Core/Base/Data_Classes/Effect.cs` - `RequiresToHitCheck` flag
  - `Core/Base/Data_Classes/Power.cs` - `Accuracy` property, `EntitiesAutoHit` enum

### Critical Distinction: Accuracy vs ToHit

**Accuracy (Multiplicative)**:
- Stored in: `Power.Accuracy` (base value, typically 1.0)
- Enhanced by: Accuracy enhancements from slotted IOs
- Buffed by: Global accuracy buffs (e.g., Tactics, Kismet +ToHit IO)
- Effect: Multiplies the final hit chance
- Variable: `powerMath.Accuracy` (enhancement bonus), `nAcc` (global buff)

**ToHit (Additive)**:
- Stored in: `MidsContext.Config.ScalingToHit` (default from `ServerData.BaseToHit` = 0.75)
- Buffed by: ToHit buffs (e.g., Build Up, Aim, Focused Accuracy)
- Effect: Adds to hit chance after accuracy multiplier
- Variable: `nToHit` (global buff)

## High-Level Algorithm

```
Power Accuracy/ToHit Calculation Process:

1. Get Base Accuracy:
   base_accuracy = power.Accuracy  // Typically 1.0, some powers 0.8-1.2

2. Calculate Enhancement Bonus (GBPA_Pass1_Enhancement):
   enhancement_accuracy = 0.0
   For each slotted enhancement:
     If power doesn't ignore accuracy enhancements:
       enhancement_accuracy += enhancement.GetEnhancementEffect(Accuracy)

3. Apply Enhancement Diversification (GBPA_Pass2_ApplyED):
   schedule = Enhancement.GetSchedule(Enums.eEnhance.Accuracy)  // Schedule A
   enhancement_accuracy = Enhancement.ApplyED(schedule, enhancement_accuracy)
   // ED reduces effectiveness above 70% bonus

4. Calculate Global Accuracy Buffs (GBPA_Pass3_ApplyBuffs):
   global_accuracy_buff = 0.0
   For each accuracy buff effect in build:
     If power doesn't ignore accuracy buffs:
       global_accuracy_buff += buff.magnitude
   // Examples: Kismet +ToHit IO (actually grants +accuracy), set bonuses

5. Calculate ToHit Buffs:
   global_tohit_buff = 0.0
   For each tohit buff effect in build:
     If power doesn't ignore tohit buffs:
       global_tohit_buff += buff.magnitude
   // Examples: Build Up, Aim, Focused Accuracy, Tactics

6. Calculate Final Accuracy (GBPA_Pass4_ApplyAccuracy):
   // Check if power can use buffs
   nAcc = power.IgnoreBuff(Accuracy) ? 0 : global_accuracy_buff
   nToHit = power.IgnoreBuff(ToHit) ? 0 : global_tohit_buff

   // Final accuracy value (used for display)
   final_accuracy = base_accuracy * (1 + enhancement_accuracy + nAcc) *
                    (ScalingToHit + nToHit)

   // Accuracy multiplier (without base tohit scaling)
   accuracy_mult = base_accuracy * (1 + enhancement_accuracy + nAcc)

7. Calculate Hit Chance:
   // Base tohit varies by enemy level relative to player
   // ScalingToHit = 0.75 (even level), 0.65 (-1 level), 0.56 (-2 level), etc.
   hit_chance = final_accuracy

   // Apply floor and ceiling (not explicitly in MidsReborn display,
   // but part of game mechanics)
   hit_chance = max(0.05, min(0.95, hit_chance))  // 5% floor, 95% ceiling

8. Handle Auto-Hit Powers:
   If power.EntitiesAutoHit != None:
     // Power automatically hits specified entities (Caster, Player, etc.)
     // No accuracy calculation needed
     // Common for self-buffs, PBAoE auras

   If NOT effect.RequiresToHitCheck:
     // Effect doesn't need tohit check (e.g., some debuffs)
     // Applied regardless of hit/miss
```

### Key Calculation Code

**Final Accuracy Application** (`clsToonX.cs:GBPA_Pass4_ApplyAccuracy`):
```csharp
var nToHit = !powerMath.IgnoreBuff(Enums.eEnhance.ToHit) ? 0 : _selfBuffs.Effect[(int)Enums.eStatType.ToHit];
var nAcc = !powerMath.IgnoreBuff(Enums.eEnhance.Accuracy) ? 0 : _selfBuffs.Effect[(int)Enums.eStatType.BuffAcc];
powerBuffed.Accuracy = powerBuffed.Accuracy * (1 + powerMath.Accuracy + nAcc) * (MidsContext.Config.ScalingToHit + nToHit);
powerBuffed.AccuracyMult = powerBuffed.Accuracy * (1 + powerMath.Accuracy + nAcc);
```

**Enhancement Diversification for Accuracy**:
```csharp
powerMath.Accuracy = Enhancement.ApplyED(Enhancement.GetSchedule(Enums.eEnhance.Accuracy), powerMath.Accuracy);
```

**Base ToHit Value** (`Core/ServerData.cs`):
```csharp
public float BaseToHit { get; set; } = 0.75f;  // 75% base hit chance vs even-level enemy
```

**ScalingToHit Configuration** (`Core/ConfigData.cs`):
```csharp
public float ScalingToHit { get; set; } = DatabaseAPI.ServerData.BaseToHit;
// User can adjust for different enemy levels:
// +4 level: 0.48 (48%)
// +3 level: 0.52
// +2 level: 0.56
// +1 level: 0.60
// Even level: 0.75
// -1 level: 0.65
// etc.
```

## Game Mechanics Context

**Why This Exists:**

In City of Heroes, the accuracy/tohit system determines whether an attack successfully hits a target. This dual system creates strategic depth:

1. **Accuracy (Multiplicative)**: Represents how well-aimed or precise an attack is. Slotting accuracy enhancements improves your base hit rate multiplicatively, which is more valuable against higher-defense enemies.

2. **ToHit (Additive)**: Represents temporary combat advantages (aim, focus, tactics). ToHit buffs add directly to hit chance, making them powerful but subject to the 95% hit cap.

3. **Enemy Level Scaling**: The `ScalingToHit` value decreases when fighting higher-level enemies, representing increased difficulty. Players must slot accuracy or use tohit buffs to compensate.

4. **Defense Interaction**: Enemy defense subtracts from hit chance additively (like negative tohit), making accuracy more valuable against high-defense targets since it's applied multiplicatively.

**Historical Context:**

- **Launch (2004)**: Original system with simple accuracy calculation. Base hit rate was 75% vs even-level enemies.

- **Issue 5 (2005)**: Enhancement Diversification (ED) introduced diminishing returns on accuracy enhancements. Before ED, 6-slotting accuracy gave 200% bonus; after ED, same slotting gives ~95% bonus.

- **Issue 7 (2006)**: Invention Origin enhancements introduced, including accuracy/tohit set bonuses. Distinction between accuracy (multiplicative) and tohit (additive) became more important for build optimization.

- **Issue 9 (2007)**: Invention system expanded with unique IOs like Kismet +ToHit (which actually grants +6% accuracy, not tohit, despite the name - a historical quirk).

- **Homecoming (2019+)**: Tohit/accuracy mechanics unchanged from live, but new IOs and set bonuses created more build diversity.

**Known Quirks:**

1. **Kismet +ToHit IO Misnomer**: Despite the name "Kismet: Accuracy/Tohit/+ToHit", the unique proc grants +6% accuracy (multiplicative), not +6% tohit (additive). This is a legacy naming issue from when the distinction wasn't well-understood.

2. **Auto-Hit Powers**: Powers with `EntitiesAutoHit` flag automatically hit specified entities (usually self for buffs). These powers ignore accuracy entirely and display "Auto" in hit chance.

3. **RequiresToHitCheck Flag**: Individual effects within a power can have `RequiresToHitCheck = false`, meaning that effect applies even on a miss. Common for secondary debuff effects (e.g., -defense debuff that makes subsequent attacks more likely to hit).

4. **Hit Chance Floor (5%) and Ceiling (95%)**: Game engine enforces minimum 5% hit chance (can never miss 100% of time) and maximum 95% hit chance (can never hit 100% of time). MidsReborn doesn't display these caps but they exist in actual gameplay.

5. **Streakbreaker System**: Game has hidden "streakbreaker" that forces a hit after consecutive misses when hit chance > 75%. Not modeled in MidsReborn since it's RNG mitigation, not true probability.

6. **Accuracy vs Tohit Display**: MidsReborn displays final accuracy value (after multiplication and scaling), which can be confusing. Real hit chance = (displayed_accuracy - enemy_defense), clamped to 5%-95%.

7. **Schedule A ED Curve**: Accuracy uses Enhancement Schedule A (same as damage), meaning diminishing returns start at 70% enhancement bonus. Three even-level SOs (33.3% each) = 99.9% total → ~95% after ED → ~46% final accuracy bonus.

8. **Power-Specific Accuracy Modifiers**: Some powers have base accuracy != 1.0. For example:
   - Sniper attacks: 1.20 (20% more accurate)
   - Some AoEs: 0.80-0.90 (slightly less accurate)
   - Typical single-target: 1.00 (baseline)

9. **PvP Accuracy Suppression**: In PvP, accuracy calculations use different formulas with diminishing returns. MidsReborn doesn't fully model PvP accuracy differences.

## Python Implementation Notes

**Proposed Architecture:**

```python
# backend/app/calculations/accuracy.py

from dataclasses import dataclass
from typing import Optional
from .enhancement_diversification import apply_ed, get_schedule, ScheduleType
from enum import Enum

class EntityType(Enum):
    """Entities that can be auto-hit"""
    NONE = "none"
    CASTER = "caster"
    PLAYER = "player"
    CRITTER = "critter"
    ANY = "any"

@dataclass
class AccuracyResult:
    """
    Result of accuracy/tohit calculation
    Maps to MidsReborn's powerBuffed.Accuracy and AccuracyMult
    """
    final_accuracy: float  # Base * (1 + enh + buff) * (scalingToHit + tohitBuff)
    accuracy_mult: float   # Base * (1 + enh + buff) - without tohit scaling
    base_accuracy: float   # Power's base accuracy (typically 1.0)
    enhancement_bonus: float  # After ED
    global_accuracy_buff: float  # From set bonuses, Kismet, etc.
    global_tohit_buff: float  # From Build Up, Aim, Tactics, etc.
    scaling_tohit: float  # Base tohit for enemy level (0.75 default)
    is_auto_hit: bool = False  # True if power auto-hits

    @property
    def hit_chance_vs_even_defense(self) -> float:
        """
        Hit chance vs enemy with no defense at same level
        Applies 5%-95% floor/ceiling
        """
        if self.is_auto_hit:
            return 1.0
        chance = self.final_accuracy
        return max(0.05, min(0.95, chance))

    def hit_chance_vs_defense(self, enemy_defense: float) -> float:
        """
        Hit chance vs enemy with specific defense value

        Args:
            enemy_defense: Enemy defense value (0.0-1.0+)

        Returns:
            Hit chance (0.05-0.95)
        """
        if self.is_auto_hit:
            return 1.0
        chance = self.final_accuracy - enemy_defense
        return max(0.05, min(0.95, chance))

    def __str__(self) -> str:
        """Format like MidsReborn display"""
        if self.is_auto_hit:
            return "Auto"
        return f"{self.final_accuracy * 100:.2f}%"

class AccuracyCalculator:
    """
    Calculates power accuracy and hit chance
    Maps to MidsReborn's GBPA_Pass4_ApplyAccuracy and related methods
    """

    # Scaling tohit values for different enemy level differences
    SCALING_TOHIT_BY_LEVEL_DIFF = {
        4: 0.48,   # +4 enemies (very hard to hit)
        3: 0.52,   # +3 enemies
        2: 0.56,   # +2 enemies
        1: 0.60,   # +1 enemies
        0: 0.75,   # Even level (base)
        -1: 0.65,  # -1 enemies (easier)
        -2: 0.70,  # -2 enemies
        -3: 0.75,  # -3 enemies
    }

    def __init__(self,
                 base_tohit: float = 0.75,
                 enemy_level_diff: int = 0):
        """
        Args:
            base_tohit: Base tohit from ServerData (default 0.75 = 75%)
            enemy_level_diff: Enemy level - player level (0 = even, +4 = +4 level)
        """
        self.base_tohit = base_tohit
        self.scaling_tohit = self.SCALING_TOHIT_BY_LEVEL_DIFF.get(
            enemy_level_diff, base_tohit
        )

    def calculate_accuracy(self,
                          power_base_accuracy: float,
                          enhancement_accuracy: float,
                          global_accuracy_buffs: float = 0.0,
                          global_tohit_buffs: float = 0.0,
                          ignores_accuracy_buffs: bool = False,
                          ignores_tohit_buffs: bool = False,
                          auto_hit_entities: EntityType = EntityType.NONE) -> AccuracyResult:
        """
        Calculate final accuracy and hit chance

        Args:
            power_base_accuracy: Power's base accuracy (typically 1.0)
            enhancement_accuracy: Total accuracy from slotted enhancements (pre-ED)
            global_accuracy_buffs: Sum of global accuracy bonuses (Kismet, sets, etc.)
            global_tohit_buffs: Sum of global tohit bonuses (Build Up, Aim, etc.)
            ignores_accuracy_buffs: If True, power ignores global accuracy buffs
            ignores_tohit_buffs: If True, power ignores global tohit buffs
            auto_hit_entities: If not NONE, power auto-hits specified entities

        Returns:
            AccuracyResult with final values
        """
        # Check for auto-hit
        is_auto_hit = auto_hit_entities != EntityType.NONE

        # Apply Enhancement Diversification to slotted enhancements
        schedule = get_schedule(ScheduleType.ACCURACY)
        enhancement_after_ed = apply_ed(schedule, enhancement_accuracy)

        # Apply global buffs (respecting ignore flags)
        nAcc = 0.0 if ignores_accuracy_buffs else global_accuracy_buffs
        nToHit = 0.0 if ignores_tohit_buffs else global_tohit_buffs

        # Calculate accuracy multiplier (without tohit scaling)
        accuracy_mult = power_base_accuracy * (1.0 + enhancement_after_ed + nAcc)

        # Calculate final accuracy (with tohit scaling and buffs)
        final_accuracy = accuracy_mult * (self.scaling_tohit + nToHit)

        return AccuracyResult(
            final_accuracy=final_accuracy,
            accuracy_mult=accuracy_mult,
            base_accuracy=power_base_accuracy,
            enhancement_bonus=enhancement_after_ed,
            global_accuracy_buff=nAcc,
            global_tohit_buff=nToHit,
            scaling_tohit=self.scaling_tohit,
            is_auto_hit=is_auto_hit
        )

    def calculate_required_accuracy_for_hitchance(self,
                                                  target_hit_chance: float,
                                                  enemy_defense: float = 0.0,
                                                  global_accuracy_buffs: float = 0.0,
                                                  global_tohit_buffs: float = 0.0) -> float:
        """
        Calculate required base accuracy enhancement to achieve target hit chance
        Useful for build optimization tools

        Args:
            target_hit_chance: Desired hit chance (0.0-0.95)
            enemy_defense: Enemy defense value
            global_accuracy_buffs: Global accuracy bonuses from build
            global_tohit_buffs: Global tohit bonuses from build

        Returns:
            Required enhancement_accuracy (pre-ED) to achieve target
        """
        # Clamp target to valid range
        target = max(0.05, min(0.95, target_hit_chance))

        # Work backwards from final formula
        # target = base * (1 + enh + globalAcc) * (scalingToHit + globalToHit) - defense
        # Solve for enh:
        # enh = [(target + defense) / (scalingToHit + globalToHit) - base] / base - globalAcc

        tohit_total = self.scaling_tohit + global_tohit_buffs
        if tohit_total <= 0:
            return float('inf')  # Impossible to hit

        # Assume base accuracy = 1.0 for typical power
        base = 1.0
        required_mult = (target + enemy_defense) / tohit_total
        required_enh = (required_mult / base) - 1.0 - global_accuracy_buffs

        # This gives us post-ED value; need to invert ED curve for pre-ED
        # For simplicity, return post-ED value (caller can manually slot)
        return max(0.0, required_enh)
```

**Implementation Priority:**

**CRITICAL** - Implement in Phase 1 (Foundation). Required for:
- Power tooltips showing hit chance
- Attack effectiveness calculations
- Build optimization tools
- Combat simulation

**Key Implementation Steps:**

1. Define `EntityType` enum for auto-hit mechanics
2. Create `AccuracyResult` dataclass with hit chance methods
3. Implement `AccuracyCalculator.calculate_accuracy()` with core formula
4. Integrate with Enhancement Diversification (Spec 10) for accuracy ED
5. Add scaling tohit table for enemy level differences
6. Implement hit chance floor (5%) and ceiling (95%)
7. Add utility method for reverse calculation (required accuracy for target hit chance)
8. Handle auto-hit powers and effects that don't require tohit checks

**Testing Strategy:**

- Unit tests with known accuracy values:
  - Base 1.0 accuracy, no enhancements, even level: 75% hit chance
  - Base 1.0, +95% accuracy (3 SOs), even level: ~146% displayed accuracy
  - Base 1.2 (sniper), +95% accuracy, even level: ~175% displayed accuracy

- Test ED application:
  - +33.3% enhancement × 3 = +99.9% total → ~95% after ED
  - Verify schedule A ED curve is used

- Test global buffs:
  - Kismet +6% accuracy (multiplicative)
  - Build Up +20% tohit (additive)
  - Tactics +7% tohit (additive)

- Test enemy level scaling:
  - +4 enemies: ScalingToHit = 0.48
  - Even level: ScalingToHit = 0.75

- Test hit chance clamping:
  - Verify 95% ceiling with extreme accuracy
  - Verify 5% floor with negative tohit

- Integration tests comparing Python to MidsReborn for sample powers:
  - Standard attack (1.0 accuracy)
  - Sniper attack (1.2 accuracy)
  - AoE attack (0.8-0.9 accuracy)
  - Auto-hit buff (EntitiesAutoHit = Caster)

**Validation Data Sources:**

- MidsReborn accuracy tooltips for specific powers
- In-game Combat Attributes window "Last Hit Chance" value
- City of Data website power accuracy values
- Player guides documenting accuracy formulas and ED curves
- Paragon Wiki accuracy mechanics documentation

## References

- **Related Specs**:
  - Spec 01 (Power Effects Core) - Effect data structure, RequiresToHitCheck flag
  - Spec 10 (Enhancement Schedules) - ED curves for accuracy (Schedule A)
  - Spec 11 (Enhancement Types) - Accuracy enhancement type
  - Spec 16 (Archetype Modifiers) - No AT modifiers for accuracy (unlike damage)
  - Spec 22 (Build Totals - Accuracy/ToHit) - Global buff aggregation
  - Spec 35 (Defense Mechanics) - Defense reduces hit chance additively
- **MidsReborn Files**:
  - `clsToonX.cs` (GBPA_Pass4_ApplyAccuracy, GBPA_Pass1_Enhancement, GBPA_Pass2_ApplyED)
  - `Core/Enhancement.cs` (ApplyED, GetSchedule)
  - `Core/ConfigData.cs` (ScalingToHit property)
  - `Core/ServerData.cs` (BaseToHit constant)
  - `Core/Base/Data_Classes/Power.cs` (Accuracy, EntitiesAutoHit)
  - `Core/Base/Data_Classes/Effect.cs` (RequiresToHitCheck)
- **Game Documentation**:
  - Paragon Wiki - "Accuracy", "ToHit", "Streakbreaker"
  - Homecoming Wiki - "Accuracy Mechanics"
  - City of Data - Power accuracy values
  - Player guides on accuracy vs tohit distinction
