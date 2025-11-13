"""
Power Damage Calculator

Calculates damage output for attack powers including base damage, archetype scaling,
and enhancement bonuses. Implements MidsReborn's damage calculation logic.

Based on:
    - MidsReborn Core/Base/Data_Classes/Power.cs (FXGetDamageValue, lines 861-940)
    - MidsReborn Core/Base/Data_Classes/Effect.cs (GetDamage, lines 2782-2817)
    - Specification: docs/midsreborn/calculations/02-power-damage.md
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from ..core.effect import Effect
from ..core.effect_types import DamageType as CoreDamageType
from ..core.effect_types import EffectType
from ..core.enums import ToWho


class DamageType(Enum):
    """
    Damage types from MidsReborn eDamage enum.

    Maps to Core/Enums.cs eDamage enumeration.
    """

    NONE = "none"
    SMASHING = "smashing"
    LETHAL = "lethal"
    FIRE = "fire"
    COLD = "cold"
    ENERGY = "energy"
    NEGATIVE = "negative"
    TOXIC = "toxic"
    PSIONIC = "psionic"
    SPECIAL = "special"
    # Positional indicators (not actual damage types)
    MELEE = "melee"
    RANGED = "ranged"
    AOE = "aoe"

    @classmethod
    def from_core_damage_type(cls, core_type: Optional[CoreDamageType]) -> "DamageType":
        """Convert core DamageType to power DamageType."""
        if core_type is None:
            return cls.NONE
        # Map core damage type enum to power damage type enum
        mapping = {
            CoreDamageType.NONE: cls.NONE,
            CoreDamageType.SMASHING: cls.SMASHING,
            CoreDamageType.LETHAL: cls.LETHAL,
            CoreDamageType.FIRE: cls.FIRE,
            CoreDamageType.COLD: cls.COLD,
            CoreDamageType.ENERGY: cls.ENERGY,
            CoreDamageType.NEGATIVE: cls.NEGATIVE,
            CoreDamageType.TOXIC: cls.TOXIC,
            CoreDamageType.PSIONIC: cls.PSIONIC,
        }
        return mapping.get(core_type, cls.NONE)


class PowerType(Enum):
    """Power activation types."""

    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"
    BOOST = "boost"


class DamageMathMode(Enum):
    """How to handle probabilistic damage."""

    AVERAGE = "average"  # Include procs weighted by probability
    MINIMUM = "minimum"  # Exclude procs (guaranteed damage only)


class DamageReturnMode(Enum):
    """What value to return."""

    NUMERIC = "numeric"  # Raw damage number
    DPS = "dps"  # Damage per second
    DPA = "dpa"  # Damage per activation


@dataclass
class DamageValue:
    """
    Single damage value of specific type.

    Maps to MidsReborn's Damage struct (Effect.cs lines 2899-2903).

    Attributes:
        damage_type: Type of damage
        value: Amount of damage
        ticks: For DoT effects (0 = instant damage)
        is_percentage: For percentage-based damage
    """

    damage_type: DamageType
    value: float
    ticks: int = 0
    is_percentage: bool = False

    @property
    def per_tick(self) -> float:
        """Damage per tick for DoT."""
        return self.value / self.ticks if self.ticks > 0 else self.value


@dataclass
class DamageSummary:
    """
    Aggregated damage across all types from a power.

    Maps to output of Power.GetDamageTip() (Power.cs lines 942-1025).

    Attributes:
        by_type: Dictionary mapping damage type to total value
        total: Sum of all damage
        has_pvp_difference: True if PvE/PvP differ
        has_toggle_enhancements: True if toggle has enhancement effects
        activate_period: For toggles, time between ticks
    """

    by_type: dict[DamageType, float]
    total: float
    has_pvp_difference: bool = False
    has_toggle_enhancements: bool = False
    activate_period: Optional[float] = None

    def __str__(self) -> str:
        """Format like MidsReborn: 'Fire(42.5), Energy(28.3)'"""
        parts = [
            f"{dtype.value.title()}({val:.2f})"
            for dtype, val in self.by_type.items()
            if val > 0.01
        ]
        return ", ".join(parts) if parts else "0"

    def format_tooltip(self) -> str:
        """
        Generate tooltip like MidsReborn GetDamageTip().

        Format matches Power.cs lines 1019-1022.
        """
        if not self.by_type:
            return ""

        lines = []

        # Toggle note
        if self.has_toggle_enhancements and self.activate_period:
            lines.append(f"Applied every {self.activate_period:.1f} s:")

        # Total with breakdown
        total_line = f"Total: {self.total:.2f}"
        breakdown = ", ".join(
            [
                f"{dtype.value.title()}: {val:.2f}"
                for dtype, val in self.by_type.items()
            ]
        )
        lines.append(f"{total_line} ({breakdown})")

        # PvP difference note
        if self.has_pvp_difference:
            lines.append("This power deals different damage in PvP and PvE modes.")

        return "\n".join(lines)


class DamageCalculator:
    """
    Calculates power damage output.

    Implementation based on:
        - Power.cs FXGetDamageValue() lines 861-940
        - Effect.cs GetDamage() lines 2782-2817
    """

    # Constants from MidsReborn
    PROBABILITY_THRESHOLD = 0.999000012874603  # Line 878, 2785
    TOGGLE_ENHANCEMENT_TICK_RATE = 10.0  # Line 894, 2804
    EPSILON_DISPLAY = 0.0001  # Line 962
    EPSILON_VALUE = 1e-7  # float.Epsilon equivalent

    def __init__(
        self,
        archetype_damage_cap: float = 4.0,
        damage_math_mode: DamageMathMode = DamageMathMode.AVERAGE,
    ):
        """
        Initialize damage calculator.

        Args:
            archetype_damage_cap: AT damage buff cap (4.0 = 400%, from Archetype.cs line 39)
            damage_math_mode: How to handle probabilistic damage
        """
        self.damage_cap = archetype_damage_cap
        self.damage_math_mode = damage_math_mode

    def calculate_power_damage(
        self,
        power_effects: list[Effect],
        power_type: PowerType,
        power_recharge_time: float = 0.0,
        power_cast_time: float = 0.0,
        power_interrupt_time: float = 0.0,
        power_activate_period: float = 0.0,
        damage_return_mode: DamageReturnMode = DamageReturnMode.NUMERIC,
    ) -> DamageSummary:
        """
        Calculate total damage from all effects in a power.

        Implementation from Power.cs FXGetDamageValue() lines 861-940.

        Args:
            power_effects: All Effect objects from power
            power_type: Toggle, Click, Auto, etc.
            power_recharge_time: Base recharge in seconds
            power_cast_time: Animation time in seconds
            power_interrupt_time: Interrupt time in seconds
            power_activate_period: For toggles, time between ticks
            damage_return_mode: NUMERIC, DPS, or DPA

        Returns:
            DamageSummary with totals by type
        """
        damage_by_type: dict[DamageType, float] = {}
        total_damage = 0.0
        has_pvp_difference = False
        has_toggle_enhancements = False

        for effect in power_effects:
            # STEP 1: Filter to damage effects (line 877)
            if effect.effect_type != EffectType.DAMAGE:
                continue

            # STEP 2: Check probability threshold (line 878)
            if self.damage_math_mode == DamageMathMode.MINIMUM:
                if not (abs(effect.probability) > self.PROBABILITY_THRESHOLD):
                    continue

            # STEP 3: Exclusion checks (lines 879-880)
            # Skip self-targeted special damage (healing displayed as damage)
            # Note: SPECIAL is not in core DamageType enum, so we check via attribute
            if (
                hasattr(effect, "is_special_damage")
                and effect.is_special_damage
                and effect.to_who == ToWho.SELF
            ):
                continue

            if effect.probability <= 0:
                continue

            # STEP 4: Get enhanced magnitude (line 885)
            # buffed_magnitude already includes enhancements and AT scaling
            effect_damage = effect.get_effective_magnitude()

            # STEP 5: Check if this is a cancel-on-miss DoT
            is_cancel_on_miss_dot = (
                effect.ticks > 1
                and hasattr(effect, "cancel_on_miss")
                and effect.cancel_on_miss
                and self.damage_math_mode == DamageMathMode.AVERAGE
                and effect.probability < 1
            )

            # STEP 6: Apply probability (lines 887-890)
            # Skip probability for cancel-on-miss DoTs (geometric series handles it)
            if self.damage_math_mode == DamageMathMode.AVERAGE and not is_cancel_on_miss_dot:
                effect_damage *= effect.probability

            # STEP 7: Toggle enhancement scaling (lines 892-895)
            # Toggle enhancement effects tick every 10s regardless of activate period
            if power_type == PowerType.TOGGLE and effect.is_enhancement_effect:
                effect_damage *= power_activate_period / self.TOGGLE_ENHANCEMENT_TICK_RATE
                has_toggle_enhancements = True

            # STEP 8: Handle DoT ticking (lines 897-904)
            if effect.ticks > 1:
                # Cancel-on-miss DoTs use geometric series for expected ticks
                # This formula already includes probability, so we skipped STEP 6
                if is_cancel_on_miss_dot:
                    # Expected ticks = (1 - p^n) / (1 - p)
                    # This gives expected number of ticks that land
                    expected_ticks = (1 - pow(effect.probability, effect.ticks)) / (
                        1 - effect.probability
                    )
                    effect_damage *= expected_ticks
                else:
                    # Standard tick multiplication
                    effect_damage *= effect.ticks

            # STEP 8: Accumulate total
            total_damage += effect_damage

            # STEP 9: Track by damage type
            damage_type = DamageType.from_core_damage_type(effect.damage_type)
            if damage_type not in damage_by_type:
                damage_by_type[damage_type] = 0.0
            damage_by_type[damage_type] += effect_damage

        # STEP 10: Apply return mode (lines 909-937)
        divisor = 1.0

        if damage_return_mode == DamageReturnMode.DPS:
            # Damage per second
            if power_type == PowerType.TOGGLE and power_activate_period > 0:
                divisor = power_activate_period
            else:
                total_time = (
                    power_recharge_time + power_cast_time + power_interrupt_time
                )
                if total_time > 0:
                    divisor = total_time

        elif damage_return_mode == DamageReturnMode.DPA:
            # Damage per activation
            if power_type == PowerType.TOGGLE and power_activate_period > 0:
                divisor = power_activate_period
            elif power_cast_time > 0:
                divisor = power_cast_time

        if divisor > 0 and divisor != 1.0:
            total_damage /= divisor
            damage_by_type = {
                dtype: val / divisor for dtype, val in damage_by_type.items()
            }

        return DamageSummary(
            by_type=damage_by_type,
            total=total_damage,
            has_pvp_difference=has_pvp_difference,
            has_toggle_enhancements=has_toggle_enhancements,
            activate_period=power_activate_period
            if power_type == PowerType.TOGGLE
            else None,
        )

    def calculate_effect_damage(self, effect: Effect) -> Optional[DamageValue]:
        """
        Calculate damage from single effect.

        Implementation from Effect.cs GetDamage() lines 2782-2817.

        Args:
            effect: Effect object

        Returns:
            DamageValue or None if effect doesn't produce damage
        """
        # STEP 1: Exclusion checks (lines 2784-2791)
        if effect.effect_type != EffectType.DAMAGE:
            return None

        if self.damage_math_mode == DamageMathMode.MINIMUM:
            if not (abs(effect.probability) > self.PROBABILITY_THRESHOLD):
                return None

        # Skip self-targeted special damage
        if (
            hasattr(effect, "is_special_damage")
            and effect.is_special_damage
            and effect.to_who == ToWho.SELF
        ):
            return None

        if effect.probability <= 0:
            return None

        # STEP 2: Get enhanced magnitude (line 2795)
        effect_dmg = effect.get_effective_magnitude()

        # STEP 3: Apply probability (lines 2797-2800)
        if self.damage_math_mode == DamageMathMode.AVERAGE:
            effect_dmg *= effect.probability

        # STEP 4: Handle ticks (lines 2807-2814)
        if effect.ticks > 1:
            if (
                hasattr(effect, "cancel_on_miss")
                and effect.cancel_on_miss
                and self.damage_math_mode == DamageMathMode.AVERAGE
                and effect.probability < 1
            ):
                # Geometric series for cancel-on-miss DoT
                expected_ticks = (1 - pow(effect.probability, effect.ticks)) / (
                    1 - effect.probability
                )
                effect_dmg *= expected_ticks
            else:
                effect_dmg *= effect.ticks

        # STEP 5: Return damage value (line 2816)
        damage_type = DamageType.from_core_damage_type(effect.damage_type)
        return DamageValue(
            damage_type=damage_type, value=effect_dmg, ticks=effect.ticks
        )
