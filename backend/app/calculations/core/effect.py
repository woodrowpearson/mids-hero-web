"""
Effect Class - Core game effect representation

Maps to MidsReborn's Effect class implementing IEffect interface.
Complete property set from Core/IEffect.cs.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from .effect_types import EffectType, DamageType, MezType
from .enums import ToWho, PvMode, Stacking, SpecialCase, Suppress


@dataclass
class Effect:
    """
    Represents a single game effect (damage, buff, debuff, control, etc.).

    Maps to MidsReborn's Effect class implementing IEffect interface.
    Complete property set from Core/IEffect.cs lines 6-130.

    Core properties (always required):
        unique_id: Unique identifier for this effect instance
        effect_type: Primary effect type (85 possible values)
        magnitude: Base (unenhanced) magnitude

    All other properties have sensible defaults.
    """

    # Core identification
    unique_id: int
    effect_type: EffectType
    magnitude: float  # Base (unenhanced) magnitude

    # Effect aspects (optional sub-types)
    damage_type: Optional[DamageType] = None
    mez_type: Optional[MezType] = None
    et_modifies: Optional[EffectType] = None  # For enhancement effects

    # Magnitude variations
    buffed_magnitude: Optional[float] = None  # Enhanced magnitude
    magnitude_percent: Optional[float] = None  # As percentage for display

    # Duration and probability
    duration: float = 0.0  # Seconds (0 = instant/permanent)
    probability: float = 1.0  # 1.0 = always, <1.0 = proc
    base_probability: float = 1.0
    procs_per_minute: Optional[float] = None  # For PPM procs

    # Targeting and context
    to_who: ToWho = ToWho.TARGET
    pv_mode: PvMode = PvMode.ANY

    # Scaling and modification
    scale: float = 1.0  # AT scaling multiplier
    modifier_table: str = "Melee_Ones"  # AT modifier table name
    modifier_table_id: int = 0  # AT modifier table ID
    ignore_scaling: bool = False  # Exempt from AT scaling
    ignore_ed: bool = False  # Exempt from Enhancement Diversification

    # Stacking and suppression
    stacking: Stacking = Stacking.YES
    suppression: Suppress = Suppress.NONE
    buffable: bool = True  # Can be enhanced by buffs
    resistible: bool = True  # Can be resisted

    # Special mechanics
    special_case: SpecialCase = SpecialCase.NONE
    summon: Optional[str] = None  # Pet/pseudopet ID
    summon_id: int = 0  # Numeric summon ID
    delayed_time: float = 0.0  # Delay before effect applies
    ticks: int = 0  # Number of times effect ticks (for DoTs)

    # Enhancement integration
    is_enhancement_effect: bool = False

    # Power attribute modifications (for ModifyAttrib effects)
    # These store original and modified values for power attributes
    atr_orig_accuracy: float = 0.0
    atr_orig_cast_time: float = 0.0
    atr_orig_recharge_time: float = 0.0
    atr_orig_endurance_cost: float = 0.0
    atr_orig_range: float = 0.0
    atr_orig_radius: float = 0.0
    atr_orig_arc: float = 0.0
    atr_orig_max_targets: int = 0
    atr_orig_effect_area: str = ""
    atr_orig_requires_line_of_sight: bool = False
    atr_orig_activate_period: float = 0.0
    atr_orig_interrupt_time: float = 0.0

    atr_mod_accuracy: float = 0.0
    atr_mod_cast_time: float = 0.0
    atr_mod_recharge_time: float = 0.0
    atr_mod_endurance_cost: float = 0.0
    atr_mod_range: float = 0.0
    atr_mod_radius: float = 0.0
    atr_mod_arc: float = 0.0
    atr_mod_max_targets: int = 0
    atr_mod_effect_area: str = ""
    atr_mod_requires_line_of_sight: bool = False
    atr_mod_activate_period: float = 0.0
    atr_mod_interrupt_time: float = 0.0

    # Source tracking
    effect_id: Optional[str] = None  # Original effect ID from game data
    power_id: Optional[int] = None  # Associated power ID

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate properties after initialization."""
        if not (0 <= self.probability <= 1):
            raise ValueError(
                f"Probability must be 0-1, got {self.probability}"
            )
        if not (0 <= self.base_probability <= 1):
            raise ValueError(
                f"Base probability must be 0-1, got {self.base_probability}"
            )
        if self.duration < 0:
            raise ValueError(
                f"Duration cannot be negative, got {self.duration}"
            )
        if self.scale <= 0:
            raise ValueError(
                f"Scale must be positive, got {self.scale}"
            )

    # Convenience methods

    def is_permanent(self) -> bool:
        """
        Check if effect is permanent (duration = 0).

        Returns:
            True if duration is 0 (instant/permanent effect)
        """
        return self.duration == 0.0

    def is_temporary(self) -> bool:
        """
        Check if effect is temporary (duration > 0).

        Returns:
            True if duration is greater than 0
        """
        return self.duration > 0.0

    def is_proc(self) -> bool:
        """
        Check if effect is a proc (probability < 1.0).

        Returns:
            True if probability is less than 1.0
        """
        return self.probability < 1.0

    def get_effective_magnitude(self) -> float:
        """
        Get magnitude to use in calculations.

        Returns enhanced magnitude if available, otherwise base magnitude.

        Returns:
            Effective magnitude value
        """
        if self.buffed_magnitude is not None:
            return self.buffed_magnitude
        return self.magnitude

    def apply_at_scaling(self, at_scale: float) -> float:
        """
        Apply archetype scaling to magnitude.

        If ignore_scaling is True, returns effective magnitude unchanged.
        Otherwise applies: magnitude × effect.scale × at_scale

        Args:
            at_scale: Archetype's scale for this effect type

        Returns:
            Scaled magnitude
        """
        if self.ignore_scaling:
            return self.get_effective_magnitude()

        return self.get_effective_magnitude() * self.scale * at_scale

    def get_display_alias(self) -> str:
        """
        Generate human-readable display name for this effect.

        Format: "EffectType(Aspect)" where aspect is damage/mez type.

        Examples:
            - Defense effect with melee: "Defense(Melee)"
            - Damage with fire: "Damage(Fire)"
            - Hold effect: "Mez(Hold)"
            - Regen with no aspect: "Regeneration"

        Returns:
            Human-readable effect name
        """
        base_name = self.effect_type.name.replace("_", " ").title()

        if self.damage_type and self.damage_type != DamageType.NONE:
            return f"{base_name}({self.damage_type.name.title()})"
        elif self.mez_type and self.mez_type != MezType.NONE:
            return f"{base_name}({self.mez_type.name.title()})"
        else:
            return base_name

    def __repr__(self) -> str:
        """String representation for debugging."""
        mag_str = (
            f"{self.buffed_magnitude:.2f}"
            if self.buffed_magnitude is not None
            else f"{self.magnitude:.2f}"
        )
        return (
            f"Effect(id={self.unique_id}, "
            f"type={self.effect_type.name}, "
            f"mag={mag_str}, "
            f"to_who={self.to_who.name})"
        )
