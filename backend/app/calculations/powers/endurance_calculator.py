"""
Power Endurance Calculator

Calculates endurance costs for powers and endurance recovery rates.
Implements MidsReborn's endurance calculation logic.

Based on:
    - MidsReborn Core/Base/Data_Classes/Power.cs (ToggleCost property, lines 391-392)
    - MidsReborn Core/Statistics.cs (EnduranceRecoveryNumeric, lines 35-51)
    - MidsReborn Core/Base/Data_Classes/Archetype.cs (BaseRecovery, lines 25, 167)
    - Specification: docs/midsreborn/calculations/06-power-endurance-recovery.md
"""

from dataclasses import dataclass
from enum import Enum

from ..core.effect import Effect
from ..core.effect_types import EffectType


class PowerType(Enum):
    """
    Power activation types from Enums.ePowerType.

    Maps to MidsReborn Core/Enums.cs ePowerType enumeration.
    """

    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"
    BOOST = "boost"


@dataclass
class ArchetypeEnduranceStats:
    """
    Endurance-related archetype properties.

    Maps to Archetype.cs BaseRecovery and RecoveryCap properties.

    Attributes:
        base_recovery: Base endurance recovery rate (typically 1.67 for all ATs)
        recovery_cap: Maximum recovery percentage (typically 5.0 = 500%)
    """

    base_recovery: float = 1.67  # Standard for all ATs (Archetype.cs line 25)
    recovery_cap: float = 5.0  # 500% max recovery (Archetype.cs line 37)


@dataclass
class EnduranceCostResult:
    """
    Result of endurance cost calculation.

    Attributes:
        base_cost: Original power endurance cost
        modified_cost: Cost after enhancements applied
        cost_per_second: For toggles, cost per second; for clicks, same as modified_cost
        discount_applied: Percentage discount from enhancements
        is_toggle: Whether this is a toggle power
    """

    base_cost: float
    modified_cost: float
    cost_per_second: float
    discount_applied: float
    is_toggle: bool


@dataclass
class RecoveryResult:
    """
    Result of recovery rate calculation.

    Attributes:
        recovery_total: Total recovery as multiplier (e.g., 1.35 = 135%)
        recovery_numeric: Endurance recovered per second
        recovery_percentage: Display percentage (e.g., 135.0%)
        is_capped: Whether recovery hit the archetype cap
        uncapped_percentage: What percentage would be without cap (if capped)
    """

    recovery_total: float
    recovery_numeric: float
    recovery_percentage: float
    is_capped: bool
    uncapped_percentage: float | None = None


@dataclass
class NetRecoveryResult:
    """
    Result of net recovery calculation.

    Attributes:
        endurance_usage: Total endurance drained per second by toggles
        net_recovery: Recovery minus usage (end/sec)
        is_positive: Whether net recovery is positive (sustainable)
        time_to_full: Seconds to recover from 0 to max
        time_to_zero: Seconds to drain from max to 0 (if negative net)
    """

    endurance_usage: float
    net_recovery: float
    is_positive: bool
    time_to_full: float
    time_to_zero: float


# Game constants from MidsReborn
BASE_MAGIC = 1.666667  # From Statistics.cs line 22
BASE_MAX_ENDURANCE = 100.0  # Standard base max endurance
BASE_RECOVERY = 1.67  # From Archetype.cs line 25


class EnduranceCalculator:
    """
    Calculate power endurance costs and recovery rates.

    Implementation based on:
        - Statistics.cs (lines 22, 35-51)
        - Archetype.cs (lines 25, 167)
        - Power.cs (lines 391-392)

    The calculator handles three main calculations:
    1. Power endurance costs (with toggle conversion)
    2. Endurance recovery rates (with archetype caps)
    3. Net recovery analysis (sustainability check)
    """

    def __init__(self, archetype_stats: ArchetypeEnduranceStats | None = None):
        """
        Initialize calculator with archetype endurance properties.

        Args:
            archetype_stats: Archetype endurance properties (recovery, cap).
                           If None, uses default values (1.67 recovery, 5.0 cap).
        """
        self.at_stats = archetype_stats or ArchetypeEnduranceStats()

    def calculate_power_cost(
        self,
        base_end_cost: float,
        activate_period: float,
        power_type: PowerType,
        end_discount_effects: list[Effect],
    ) -> EnduranceCostResult:
        """
        Calculate modified endurance cost for a power.

        Implementation from Power.cs lines 391-392 (ToggleCost property).

        Args:
            base_end_cost: Power's base endurance cost
            activate_period: For toggles, seconds between ticks
            power_type: Click, Toggle, Auto, etc.
            end_discount_effects: List of eEffectType.EnduranceDiscount effects

        Returns:
            EnduranceCostResult with cost details

        Example:
            >>> calc = EnduranceCalculator()
            >>> # Toggle power Tough: 0.26 cost, 0.5s period
            >>> result = calc.calculate_power_cost(
            ...     base_end_cost=0.26,
            ...     activate_period=0.5,
            ...     power_type=PowerType.TOGGLE,
            ...     end_discount_effects=[]
            ... )
            >>> result.cost_per_second
            0.52
        """
        is_toggle = power_type == PowerType.TOGGLE

        # STEP 1: For toggles, convert to cost per second
        # Power.cs lines 391-392: ToggleCost = EndCost / ActivatePeriod
        if is_toggle and activate_period > 0:
            cost_per_second = base_end_cost / activate_period
        else:
            cost_per_second = base_end_cost

        # STEP 2: Sum all endurance discount bonuses
        # EnduranceDiscount effects reduce cost
        total_discount = sum(
            e.buffed_magnitude
            for e in end_discount_effects
            if e.effect_type == EffectType.ENDURANCE_DISCOUNT
        )

        # STEP 3: Apply discount to cost
        # Discount is percentage reduction: 0.42 = 42% reduction
        modified_cost = cost_per_second * (1.0 - total_discount)

        # STEP 4: Ensure non-negative (cost can't be negative)
        final_cost = max(0.0, modified_cost)

        return EnduranceCostResult(
            base_cost=base_end_cost,
            modified_cost=final_cost,
            cost_per_second=cost_per_second,
            discount_applied=total_discount,
            is_toggle=is_toggle,
        )

    def calculate_recovery_rate(
        self, recovery_effects: list[Effect], max_endurance: float
    ) -> RecoveryResult:
        """
        Calculate endurance recovery rate.

        Implementation from Statistics.cs lines 37-39, 69-77.

        Formula from Statistics.cs line 37:
            EnduranceRecoveryNumeric = EnduranceRecovery(false)
                * (_character.Archetype.BaseRecovery * BaseMagic)
                * (_character.TotalsCapped.EndMax / 100 + 1)

        Args:
            recovery_effects: List of eEffectType.Recovery effects
            max_endurance: Character's current maximum endurance

        Returns:
            RecoveryResult with recovery calculations

        Example:
            >>> calc = EnduranceCalculator()
            >>> # Stamina: +25% recovery
            >>> stamina = Effect(
            ...     unique_id=1,
            ...     effect_type=EffectType.RECOVERY,
            ...     magnitude=0.25
            ... )
            >>> result = calc.calculate_recovery_rate([stamina], 100.0)
            >>> result.recovery_numeric
            6.958334
        """
        # STEP 1: Start at 100% base recovery (1.0)
        recovery_total = 1.0

        # STEP 2: Add all recovery modifiers
        # Recovery effects are percentages (e.g., Stamina = +0.25 for 25%)
        for effect in recovery_effects:
            if effect.effect_type == EffectType.RECOVERY:
                recovery_total += effect.magnitude

        # Track uncapped value for display
        uncapped_percentage = recovery_total * 100.0

        # STEP 2b: Apply recovery cap
        # Most archetypes cap at 500% (5.0)
        recovery_total_capped = min(recovery_total, self.at_stats.recovery_cap)
        is_capped = recovery_total > self.at_stats.recovery_cap

        # STEP 3: Calculate max endurance multiplier
        # Higher max endurance increases recovery rate
        # Formula: (max_end / 100) + 1
        max_end_multiplier = (max_endurance / BASE_MAX_ENDURANCE) + 1.0

        # STEP 4: Calculate numeric recovery per second
        # Formula from Statistics.cs line 37
        recovery_numeric = (
            recovery_total_capped
            * self.at_stats.base_recovery
            * BASE_MAGIC
            * max_end_multiplier
        )

        # STEP 5: Calculate display percentage
        recovery_percentage = recovery_total_capped * 100.0

        return RecoveryResult(
            recovery_total=recovery_total_capped,
            recovery_numeric=recovery_numeric,
            recovery_percentage=recovery_percentage,
            is_capped=is_capped,
            uncapped_percentage=uncapped_percentage if is_capped else None,
        )

    def calculate_max_endurance(self, endurance_effects: list[Effect]) -> float:
        """
        Calculate maximum endurance from Endurance effects.

        Implementation from Statistics.cs line 35:
            EnduranceMaxEnd = _character.Totals.EndMax + 100f

        Args:
            endurance_effects: List of eEffectType.Endurance effects

        Returns:
            Maximum endurance value

        Example:
            >>> calc = EnduranceCalculator()
            >>> # IO set bonus: +10.0 max endurance
            >>> bonus = Effect(
            ...     unique_id=1,
            ...     effect_type=EffectType.ENDURANCE,
            ...     magnitude=10.0
            ... )
            >>> calc.calculate_max_endurance([bonus])
            110.0
        """
        max_end = BASE_MAX_ENDURANCE

        # Add all endurance bonuses (flat additions, not percentages)
        for effect in endurance_effects:
            if effect.effect_type == EffectType.ENDURANCE:
                max_end += effect.magnitude

        return max_end

    def calculate_endurance_usage(self, toggle_costs: list[float]) -> float:
        """
        Calculate total endurance usage from all active toggles.

        Implementation from Statistics.cs line 51:
            EnduranceUsage = _character.Totals.EndUse

        Args:
            toggle_costs: List of toggle power costs (already in end/sec)

        Returns:
            Total endurance drained per second

        Example:
            >>> calc = EnduranceCalculator()
            >>> # Three toggles: Tough, Weave, Combat Jumping
            >>> calc.calculate_endurance_usage([0.30, 0.26, 0.07])
            0.63
        """
        return sum(toggle_costs)

    def calculate_net_recovery(
        self, recovery_numeric: float, toggle_costs: list[float], max_endurance: float
    ) -> NetRecoveryResult:
        """
        Calculate net endurance recovery (recovery - usage).

        Implementation from Statistics.cs lines 41-49:
            - EnduranceRecoveryNet (line 43)
            - EnduranceTimeToFull (line 41)
            - EnduranceTimeToZero (line 47)

        Args:
            recovery_numeric: Endurance recovered per second
            toggle_costs: List of all active toggle costs (end/sec)
            max_endurance: Maximum endurance

        Returns:
            NetRecoveryResult with net calculations

        Example:
            >>> calc = EnduranceCalculator()
            >>> # Recovery: 7.53 end/sec, Usage: 0.63 end/sec
            >>> result = calc.calculate_net_recovery(
            ...     recovery_numeric=7.53,
            ...     toggle_costs=[0.30, 0.26, 0.07],
            ...     max_endurance=100.0
            ... )
            >>> result.is_positive
            True
            >>> result.net_recovery
            6.9
        """
        # STEP 1: Sum toggle usage
        endurance_usage = self.calculate_endurance_usage(toggle_costs)

        # STEP 2: Calculate net recovery
        # From Statistics.cs line 43:
        # EnduranceRecoveryNet = EnduranceRecoveryNumeric - EnduranceUsage
        net_recovery = recovery_numeric - endurance_usage

        # STEP 3: Determine if positive or negative
        is_positive = net_recovery > 0

        # STEP 4: Calculate time to full
        # From Statistics.cs line 41:
        # EnduranceTimeToFull = EnduranceMaxEnd / EnduranceRecoveryNumeric
        if recovery_numeric > 0:
            time_to_full = max_endurance / recovery_numeric
        else:
            time_to_full = float("inf")

        # STEP 5: Calculate time to zero (if negative)
        # From Statistics.cs line 47:
        # EnduranceTimeToZero = EnduranceMaxEnd / -(EnduranceRecoveryNumeric - EnduranceUsage)
        if net_recovery < 0:
            time_to_zero = max_endurance / abs(net_recovery)
        else:
            time_to_zero = float("inf")

        return NetRecoveryResult(
            endurance_usage=endurance_usage,
            net_recovery=net_recovery,
            is_positive=is_positive,
            time_to_full=time_to_full,
            time_to_zero=time_to_zero,
        )

    def format_endurance_display(self, cost: float, is_toggle: bool = False) -> str:
        """
        Format endurance cost for display matching MidsReborn style.

        Args:
            cost: Endurance cost value
            is_toggle: Whether this is a toggle power

        Returns:
            Formatted string: "{cost:.2f}" or "{cost:.2f}/s" for toggles

        Example:
            >>> calc = EnduranceCalculator()
            >>> calc.format_endurance_display(13.0, is_toggle=False)
            '13.00'
            >>> calc.format_endurance_display(0.52, is_toggle=True)
            '0.52/s'
        """
        if is_toggle:
            return f"{cost:.2f}/s"
        else:
            return f"{cost:.2f}"


# Error Handling


class EnduranceCalculationError(Exception):
    """Base exception for endurance calculation errors."""

    pass


class InvalidPowerConfigError(EnduranceCalculationError):
    """Raised when power configuration is invalid."""

    pass


class InvalidRecoveryConfigError(EnduranceCalculationError):
    """Raised when recovery configuration is invalid."""

    pass


def validate_power_endurance_config(
    base_end_cost: float, activate_period: float, power_type: PowerType
) -> None:
    """
    Validate power endurance configuration.

    Args:
        base_end_cost: Base endurance cost
        activate_period: Activate period for toggles
        power_type: Power type

    Raises:
        InvalidPowerConfigError: If configuration is invalid

    Example:
        >>> validate_power_endurance_config(-1.0, 0.5, PowerType.CLICK)
        Traceback (most recent call last):
        ...
        InvalidPowerConfigError: Base endurance cost cannot be negative: -1.0
    """
    if base_end_cost < 0:
        raise InvalidPowerConfigError(
            f"Base endurance cost cannot be negative: {base_end_cost}"
        )

    if power_type == PowerType.TOGGLE and activate_period <= 0:
        raise InvalidPowerConfigError(
            f"Toggle powers must have activate_period > 0, got {activate_period}"
        )


def validate_recovery_config(
    max_endurance: float, recovery_effects: list[Effect]
) -> None:
    """
    Validate recovery configuration.

    Args:
        max_endurance: Maximum endurance
        recovery_effects: List of recovery effects

    Raises:
        InvalidRecoveryConfigError: If configuration is invalid

    Example:
        >>> validate_recovery_config(-1.0, [])
        Traceback (most recent call last):
        ...
        InvalidRecoveryConfigError: Max endurance must be positive: -1.0
    """
    if max_endurance <= 0:
        raise InvalidRecoveryConfigError(
            f"Max endurance must be positive: {max_endurance}"
        )

    for effect in recovery_effects:
        if effect.effect_type == EffectType.RECOVERY:
            if effect.magnitude < -1.0:
                raise InvalidRecoveryConfigError(
                    f"Recovery effect magnitude too negative: {effect.magnitude}"
                )
