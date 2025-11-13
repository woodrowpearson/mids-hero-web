"""
Buff/Debuff Calculator

Calculates buff and debuff magnitudes with enhancements, archetype scaling,
target resistance, and stacking rules.

Based on:
    - MidsReborn Core/Base/Data_Classes/Effect.cs (BuffedMag calculation, lines 401-416)
    - MidsReborn Core/GroupedFx.cs (Buff aggregation and stacking)
    - Specification: docs/midsreborn/calculations/03-power-buffs-debuffs.md
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

from ..core.effect import Effect
from ..core.effect_types import EffectType
from ..core.enums import Stacking, ToWho


class BuffDebuffType(Enum):
    """
    Buff/debuff effect types matching relevant eEffectType values.

    Maps to subset of MidsReborn's Enums.eEffectType that represent buffs/debuffs.
    """

    DAMAGE_BUFF = "DamageBuff"
    DEFENSE = "Defense"
    RESISTANCE = "Resistance"
    TO_HIT = "ToHit"
    ACCURACY = "Accuracy"
    RECHARGE_TIME = "RechargeTime"
    ENDURANCE_DISCOUNT = "EnduranceDiscount"
    RECOVERY = "Recovery"
    REGENERATION = "Regeneration"
    HIT_POINTS = "HitPoints"
    MEZ_RESIST = "MezResist"
    RES_EFFECT = "ResEffect"  # Debuff resistance
    SPEED_RUNNING = "SpeedRunning"
    SPEED_FLYING = "SpeedFlying"
    SPEED_JUMPING = "SpeedJumping"
    RANGE = "Range"
    PERCEPTION_RADIUS = "PerceptionRadius"
    STEALTH = "Stealth"
    ELUSIVITY = "Elusivity"

    @classmethod
    def from_effect_type(cls, effect_type: EffectType) -> Optional["BuffDebuffType"]:
        """Convert core EffectType to BuffDebuffType if applicable."""
        mapping = {
            EffectType.DAMAGE_BUFF: cls.DAMAGE_BUFF,
            EffectType.DEFENSE: cls.DEFENSE,
            EffectType.RESISTANCE: cls.RESISTANCE,
            EffectType.TO_HIT: cls.TO_HIT,
            EffectType.ACCURACY: cls.ACCURACY,
            EffectType.RECHARGE_TIME: cls.RECHARGE_TIME,
            EffectType.ENDURANCE_DISCOUNT: cls.ENDURANCE_DISCOUNT,
            EffectType.RECOVERY: cls.RECOVERY,
            EffectType.REGENERATION: cls.REGENERATION,
            EffectType.HIT_POINTS: cls.HIT_POINTS,
            EffectType.MEZ_RESIST: cls.MEZ_RESIST,
            EffectType.RES_EFFECT: cls.RES_EFFECT,
            EffectType.SPEED_RUNNING: cls.SPEED_RUNNING,
            EffectType.SPEED_FLYING: cls.SPEED_FLYING,
            EffectType.SPEED_JUMPING: cls.SPEED_JUMPING,
            EffectType.RANGE: cls.RANGE,
            EffectType.PERCEPTION_RADIUS: cls.PERCEPTION_RADIUS,
            EffectType.STEALTH: cls.STEALTH,
            EffectType.ELUSIVITY: cls.ELUSIVITY,
        }
        return mapping.get(effect_type)


class AspectType(Enum):
    """
    Aspect variations for buff/debuff calculations.

    Maps to MidsReborn's Enums.eAspect enum.
    """

    RES = "Res"  # Resistance (current value)
    MAX = "Max"  # Maximum value
    ABS = "Abs"  # Absolute value
    STR = "Str"  # Strength/base value (default for most buffs)
    CUR = "Cur"  # Current value


class StackingMode(Enum):
    """How multiple buff/debuff instances combine."""

    ADDITIVE = "additive"  # Sum all magnitudes
    MULTIPLICATIVE = "multiplicative"  # (1+m1)*(1+m2)*...-1
    BEST_VALUE = "best_value"  # Take maximum only


@dataclass
class BuffDebuffEffect:
    """
    Represents a buff or debuff effect with calculation state.

    Wraps the core Effect class with buff/debuff specific properties
    and calculated values.

    Attributes:
        effect: Core Effect object
        buff_debuff_type: Classified buff/debuff type
        base_magnitude: Base magnitude before enhancements
        enhanced_magnitude: After enhancements
        final_magnitude: After resistance (for debuffs)
        duration: Effect duration in seconds
    """

    effect: Effect
    buff_debuff_type: BuffDebuffType
    base_magnitude: Decimal = Decimal("0.0")
    enhanced_magnitude: Decimal = Decimal("0.0")
    final_magnitude: Decimal = Decimal("0.0")
    duration: Decimal = Decimal("0.0")

    def __post_init__(self):
        """Initialize from effect."""
        self.duration = Decimal(str(self.effect.duration))

    def is_buff(self) -> bool:
        """Check if this is a buff (positive effect on self/ally)."""
        return self.effect.to_who in [ToWho.SELF, ToWho.TEAM]

    def is_debuff(self) -> bool:
        """Check if this is a debuff (effect on enemy)."""
        return self.effect.to_who == ToWho.TARGET

    def is_permanent(self) -> bool:
        """Check if effect is permanent (duration = 0)."""
        return self.duration == 0

    def get_grouping_key(self) -> tuple:
        """
        Get composite key for grouping effects.

        Effects with same key are aggregated together.
        Matches GroupedFx.FxId structure from MidsReborn.

        Returns:
            Tuple of (effect_type, damage_type, mez_type, to_who, pv_mode)
        """
        damage_type_value = self.effect.damage_type.value if self.effect.damage_type else None
        mez_type_value = self.effect.mez_type.value if self.effect.mez_type else None

        return (
            self.buff_debuff_type,
            damage_type_value,
            mez_type_value,
            self.effect.to_who,
            self.effect.pv_mode,
        )


class BuffDebuffCalculator:
    """
    Handles buff/debuff magnitude calculation and aggregation.

    Implementation based on:
        - Effect.cs Mag property (lines 401-414)
        - Effect.cs BuffedMag property (line 416)
        - GroupedFx.cs aggregation logic
    """

    # Stacking mode mappings from Spec 03
    STACKING_MODES: dict[BuffDebuffType, StackingMode] = {
        BuffDebuffType.DEFENSE: StackingMode.ADDITIVE,
        BuffDebuffType.RESISTANCE: StackingMode.ADDITIVE,
        BuffDebuffType.DAMAGE_BUFF: StackingMode.MULTIPLICATIVE,
        BuffDebuffType.TO_HIT: StackingMode.ADDITIVE,
        BuffDebuffType.ACCURACY: StackingMode.ADDITIVE,
        BuffDebuffType.RECHARGE_TIME: StackingMode.ADDITIVE,
        BuffDebuffType.RECOVERY: StackingMode.ADDITIVE,
        BuffDebuffType.REGENERATION: StackingMode.ADDITIVE,
        BuffDebuffType.ENDURANCE_DISCOUNT: StackingMode.ADDITIVE,
        BuffDebuffType.HIT_POINTS: StackingMode.ADDITIVE,
        BuffDebuffType.MEZ_RESIST: StackingMode.ADDITIVE,
        BuffDebuffType.RES_EFFECT: StackingMode.ADDITIVE,
        BuffDebuffType.SPEED_RUNNING: StackingMode.ADDITIVE,
        BuffDebuffType.SPEED_FLYING: StackingMode.ADDITIVE,
        BuffDebuffType.SPEED_JUMPING: StackingMode.ADDITIVE,
        BuffDebuffType.RANGE: StackingMode.ADDITIVE,
    }

    def calculate_magnitude(
        self,
        effect: Effect,
        enhancement_bonus: Decimal,
        at_modifier: Decimal,
        target_resistance: Decimal = Decimal("0.0"),
    ) -> dict[str, Decimal]:
        """
        Calculate final buff/debuff magnitude.

        Implementation from Effect.cs Mag property (lines 401-414).

        Args:
            effect: Effect object
            enhancement_bonus: Enhancement bonus (0.0 to 1.0+, after ED)
            at_modifier: Archetype modifier from modifier table
            target_resistance: Target's resistance to this debuff (0.0 to 1.0)

        Returns:
            Dict with 'base_mag', 'enhanced_mag', 'final_mag', 'duration'

        Raises:
            ValueError: If inputs are invalid
        """
        if enhancement_bonus < 0:
            raise ValueError(
                f"Enhancement bonus cannot be negative: {enhancement_bonus}"
            )
        if at_modifier <= 0:
            raise ValueError(f"AT modifier must be positive: {at_modifier}")
        if not (0 <= target_resistance <= 1):
            raise ValueError(
                f"Target resistance must be 0-1: {target_resistance}"
            )

        # STEP 1: Calculate base magnitude
        # From Effect.cs line 407: Scale * nMagnitude * DatabaseAPI.GetModifier(this)
        base_mag = Decimal(str(effect.scale)) * Decimal(str(effect.magnitude)) * at_modifier

        # STEP 2: Apply enhancements if buffable
        # Most buffs/debuffs have buffable = True
        if effect.buffable:
            enhanced_mag = base_mag * (Decimal("1.0") + enhancement_bonus)
        else:
            enhanced_mag = base_mag

        # STEP 3: Apply target resistance (for debuffs only)
        # From Effect.cs - resistible flag controls this
        final_mag = enhanced_mag
        is_debuff = effect.to_who == ToWho.TARGET
        if effect.resistible and is_debuff:
            # Target resistance reduces magnitude
            # resistance is 0.0 to 1.0 (0% to 100%)
            final_mag = enhanced_mag * (Decimal("1.0") - target_resistance)

        # STEP 4: Duration (usually not enhanced for buffs/debuffs)
        duration = Decimal(str(effect.duration))

        return {
            "base_mag": base_mag,
            "enhanced_mag": enhanced_mag,
            "final_mag": final_mag,
            "duration": duration,
        }

    def determine_stacking_mode(
        self, buff_type: BuffDebuffType, stacking_flag: Stacking
    ) -> StackingMode:
        """
        Determine how this effect type stacks.

        Args:
            buff_type: Type of buff/debuff
            stacking_flag: Stacking flag from effect data

        Returns:
            Stacking mode to use
        """
        # If explicitly set to No, use best value only
        if stacking_flag == Stacking.NO:
            return StackingMode.BEST_VALUE

        # Use type-specific stacking mode if available
        if buff_type in self.STACKING_MODES:
            return self.STACKING_MODES[buff_type]

        # Default to additive
        return StackingMode.ADDITIVE

    def apply_stacking(
        self, effects: list[BuffDebuffEffect], mode: StackingMode
    ) -> Decimal:
        """
        Apply stacking rules to calculate total magnitude.

        Args:
            effects: List of same-type effects to stack
            mode: Stacking mode to apply

        Returns:
            Total stacked magnitude
        """
        if not effects:
            return Decimal("0.0")

        if len(effects) == 1:
            return effects[0].final_magnitude

        if mode == StackingMode.ADDITIVE:
            # Sum all magnitudes
            total = sum(e.final_magnitude for e in effects)
            return total

        elif mode == StackingMode.MULTIPLICATIVE:
            # (1 + mag1) * (1 + mag2) * ... - 1
            # Used for damage buffs
            product = Decimal("1.0")
            for effect in effects:
                product *= Decimal("1.0") + effect.final_magnitude
            total = product - Decimal("1.0")
            return total

        elif mode == StackingMode.BEST_VALUE:
            # Take maximum magnitude
            total = max(e.final_magnitude for e in effects)
            return total

        return Decimal("0.0")

    def group_effects(
        self, effects: list[BuffDebuffEffect]
    ) -> dict[tuple, list[BuffDebuffEffect]]:
        """
        Group effects by type, aspect, and target.

        Implementation from GroupedFx.cs grouping logic.

        Args:
            effects: List of all buff/debuff effects

        Returns:
            Dictionary keyed by grouping tuple
        """
        groups: dict[tuple, list[BuffDebuffEffect]] = {}

        for effect in effects:
            key = effect.get_grouping_key()

            if key not in groups:
                groups[key] = []

            groups[key].append(effect)

        return groups

    def aggregate_effects(
        self, effects: list[BuffDebuffEffect]
    ) -> dict[tuple, Decimal]:
        """
        Aggregate effects with stacking rules applied.

        Main entry point for buff/debuff aggregation.

        Args:
            effects: List of all buff/debuff effects

        Returns:
            Dictionary mapping effect key to total magnitude
        """
        groups = self.group_effects(effects)
        aggregated: dict[tuple, Decimal] = {}

        for key, effect_list in groups.items():
            # Determine stacking mode for this group
            mode = self.determine_stacking_mode(
                effect_list[0].buff_debuff_type, effect_list[0].effect.stacking
            )

            # Apply stacking
            total_mag = self.apply_stacking(effect_list, mode)

            aggregated[key] = total_mag

        return aggregated

    def calculate_buffed_effect(
        self,
        effect: Effect,
        enhancement_bonus: Decimal,
        at_modifier: Decimal,
        target_resistance: Decimal = Decimal("0.0"),
    ) -> BuffDebuffEffect:
        """
        Calculate complete buff/debuff effect with all modifiers.

        Convenience method that wraps calculate_magnitude and creates
        a BuffDebuffEffect with all calculated values.

        Args:
            effect: Effect object
            enhancement_bonus: Enhancement bonus (after ED)
            at_modifier: Archetype modifier
            target_resistance: Target's resistance to debuffs

        Returns:
            BuffDebuffEffect with all calculations complete
        """
        # Classify effect type
        buff_type = BuffDebuffType.from_effect_type(effect.effect_type)
        if buff_type is None:
            raise ValueError(
                f"Effect type {effect.effect_type} is not a buff/debuff type"
            )

        # Calculate magnitudes
        result = self.calculate_magnitude(
            effect=effect,
            enhancement_bonus=enhancement_bonus,
            at_modifier=at_modifier,
            target_resistance=target_resistance,
        )

        # Create BuffDebuffEffect with results
        buff_effect = BuffDebuffEffect(
            effect=effect,
            buff_debuff_type=buff_type,
            base_magnitude=result["base_mag"],
            enhanced_magnitude=result["enhanced_mag"],
            final_magnitude=result["final_mag"],
            duration=result["duration"],
        )

        return buff_effect


def format_buff_display(
    buff_type: BuffDebuffType,
    magnitude: Decimal,
    damage_type: str | None = None,
    mez_type: str | None = None,
) -> str:
    """
    Format buff/debuff for display.

    Matches MidsReborn's GetDamageTip() formatting.

    Args:
        buff_type: Type of buff/debuff
        magnitude: Magnitude value
        damage_type: Damage type aspect (if applicable)
        mez_type: Mez type aspect (if applicable)

    Returns:
        Formatted string like "Defense(Melee): 27.06%"

    Examples:
        >>> format_buff_display(BuffDebuffType.DEFENSE, Decimal("0.2706"), "Melee")
        'Defense(Melee): 27.06%'
        >>> format_buff_display(BuffDebuffType.RECHARGE_TIME, Decimal("0.70"))
        'Recharge: +70.00%'
    """
    # Base name - handle camelCase properly
    # First convert camelCase to snake_case, then to Title Case
    import re

    # Insert space before capital letters (for camelCase like "RechargeTime")
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', buff_type.value)
    name = name.replace("_", " ").title()

    # Add aspect if present
    if damage_type:
        name = f"{name}({damage_type})"
    elif mez_type:
        name = f"{name}({mez_type})"

    # Format percentage
    percent = float(magnitude) * 100.0
    sign = "+" if magnitude >= 0 else ""

    return f"{name}: {sign}{percent:.2f}%"
