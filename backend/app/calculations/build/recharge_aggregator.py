"""
Recharge Aggregation - Build-level recharge time calculations

Implements global recharge reduction for City of Heroes builds.
Maps to MidsReborn's clsToonX.cs recharge calculation logic.

Global Recharge in CoH:
- Recharge reduction bonuses stack ADD IT IVELY
- Hard cap at +400% (total 500% speed = 1/5 recharge time)
- Formula: ReducedTime = BaseTime / (1 + GlobalRecharge)

Key mechanic: More recharge = faster power recycling.

Example:
- Power has 120s base recharge
- Character has 70% global recharge
- Reduced time = 120 / (1 + 0.70) = 120 / 1.70 = 70.6s

For "perma" powers (always ready):
- Need: ReducedTime ≤ PowerDuration
- Example: Hasten (120s duration) needs ≤120s recharge
- With 70% global: 120s / 1.70 = 70.6s → Perma!
"""

from dataclasses import dataclass
from typing import List, Optional

from app.calculations.core import ArchetypeType, get_archetype_caps


# Global recharge cap constant
RECHARGE_CAP = 4.00  # +400% (total 500% speed)


@dataclass
class RechargeValues:
    """
    Complete recharge values for a build.

    Stores global recharge reduction and provides methods for
    calculating reduced recharge times.

    Attributes:
        global_recharge: Global recharge bonus (0.0-4.0 scale, e.g., 0.70 = 70%)
        archetype: Optional archetype for cap enforcement
    """
    global_recharge: float = 0.0
    archetype: Optional[ArchetypeType] = None

    @classmethod
    def empty(cls, archetype: Optional[ArchetypeType] = None) -> 'RechargeValues':
        """
        Create empty recharge values (zero global recharge).

        Args:
            archetype: Optional archetype for cap enforcement

        Returns:
            RechargeValues with zero recharge
        """
        return cls(global_recharge=0.0, archetype=archetype)

    def get_global_recharge(self) -> float:
        """
        Get global recharge bonus value.

        Returns:
            Global recharge value (0.0-4.0 scale)
        """
        return self.global_recharge

    def set_global_recharge(self, value: float) -> None:
        """
        Set global recharge bonus value.

        Args:
            value: Global recharge value (0.0-4.0 scale)
        """
        self.global_recharge = value

    def add_recharge(self, value: float) -> None:
        """
        Add recharge bonus to global total.

        Args:
            value: Recharge bonus to add (can be negative for debuffs)
        """
        self.global_recharge += value

    def apply_cap(self) -> 'RechargeValues':
        """
        Apply recharge cap (+400%).

        Recharge has a hard cap of +400% (4.00 on 0.0-1.0 scale).
        Values above this are clamped.

        Returns:
            Self for chaining
        """
        if self.archetype is None:
            # Apply generic cap even without archetype
            self.global_recharge = min(self.global_recharge, RECHARGE_CAP)
        else:
            # Use archetype caps system
            caps = get_archetype_caps(self.archetype)
            self.global_recharge = caps.apply_recharge_cap(self.global_recharge)

        return self

    def is_at_cap(self, tolerance: float = 0.001) -> bool:
        """
        Check if global recharge is at cap (+400%).

        Args:
            tolerance: Floating-point comparison tolerance

        Returns:
            True if at or above cap
        """
        return self.global_recharge >= (RECHARGE_CAP - tolerance)

    def calculate_reduced_recharge(self, base_recharge: float) -> float:
        """
        Calculate reduced recharge time for a power.

        Formula: ReducedTime = BaseTime / (1 + GlobalRecharge)

        Args:
            base_recharge: Base recharge time in seconds

        Returns:
            Reduced recharge time in seconds

        Examples:
            >>> # Hasten with 70% global recharge
            >>> values = RechargeValues(global_recharge=0.70)
            >>> values.calculate_reduced_recharge(120.0)
            70.588...  # ~70.6 seconds

            >>> # Power at recharge cap (400%)
            >>> values = RechargeValues(global_recharge=4.00)
            >>> values.calculate_reduced_recharge(120.0)
            24.0  # 120 / 5 = 24 seconds
        """
        if base_recharge <= 0:
            return 0.0

        # Formula: ReducedTime = BaseTime / (1 + GlobalRecharge)
        return base_recharge / (1.0 + self.global_recharge)

    def is_power_perma(
        self,
        base_recharge: float,
        power_duration: float
    ) -> bool:
        """
        Check if a power is "perma" (always ready/active).

        A power is perma when: ReducedRecharge ≤ Duration

        Args:
            base_recharge: Base recharge time in seconds
            power_duration: Power duration/uptime in seconds

        Returns:
            True if power can be maintained permanently

        Examples:
            >>> # Hasten: 120s duration, 450s base recharge
            >>> values = RechargeValues(global_recharge=0.70)
            >>> values.is_power_perma(450.0, 120.0)
            False  # 450/1.70 = 264.7s > 120s

            >>> # Need ~275% recharge for perma-Hasten
            >>> values = RechargeValues(global_recharge=2.75)
            >>> values.is_power_perma(450.0, 120.0)
            True  # 450/3.75 = 120s ≤ 120s
        """
        reduced_recharge = self.calculate_reduced_recharge(base_recharge)
        return reduced_recharge <= power_duration

    def calculate_recharge_needed_for_perma(
        self,
        base_recharge: float,
        power_duration: float
    ) -> float:
        """
        Calculate global recharge needed for power to be perma.

        Formula: NeededRecharge = (BaseRecharge / Duration) - 1

        Args:
            base_recharge: Base recharge time in seconds
            power_duration: Power duration/uptime in seconds

        Returns:
            Global recharge bonus needed (0.0+ scale)

        Examples:
            >>> # Hasten: 450s recharge, 120s duration
            >>> values = RechargeValues()
            >>> values.calculate_recharge_needed_for_perma(450.0, 120.0)
            2.75  # Need 275% global recharge
        """
        if power_duration <= 0:
            return float('inf')

        # Formula: NeededRecharge = (BaseRecharge / Duration) - 1
        return (base_recharge / power_duration) - 1.0


def aggregate_recharge_bonuses(
    recharge_bonuses: List[float],
    archetype: Optional[ArchetypeType] = None
) -> RechargeValues:
    """
    Aggregate multiple recharge bonuses into final recharge values.

    Recharge bonuses stack ADDITIVELY up to the +400% cap.

    Args:
        recharge_bonuses: List of recharge bonus values (0.0-1.0 scale)
        archetype: Optional archetype for cap enforcement

    Returns:
        RechargeValues with aggregated bonuses

    Examples:
        >>> # Hasten (70%) + Speed Boost (50%) + IO bonuses (20%)
        >>> bonuses = [0.70, 0.50, 0.20]
        >>> result = aggregate_recharge_bonuses(bonuses)
        >>> result.get_global_recharge()
        1.40  # 140% total recharge

        >>> # Extreme case: multiple bonuses exceeding cap
        >>> bonuses = [4.00, 1.00, 1.00]  # 600% total
        >>> result = aggregate_recharge_bonuses(bonuses)
        >>> result.get_global_recharge()
        4.00  # Capped at 400%
    """
    result = RechargeValues.empty(archetype)

    # Sum all recharge bonuses (additive stacking)
    for bonus in recharge_bonuses:
        result.add_recharge(bonus)

    # Apply cap (+400%)
    result.apply_cap()

    return result


def calculate_recharge_time(
    base_recharge: float,
    global_recharge: float
) -> float:
    """
    Calculate reduced recharge time with global recharge bonus.

    Formula: ReducedTime = BaseTime / (1 + GlobalRecharge)

    Args:
        base_recharge: Base recharge time in seconds
        global_recharge: Global recharge bonus (0.0-4.0 scale)

    Returns:
        Reduced recharge time in seconds

    Examples:
        >>> # Hasten with 70% global recharge
        >>> calculate_recharge_time(450.0, 0.70)
        264.705...  # ~265 seconds

        >>> # At recharge cap (400%)
        >>> calculate_recharge_time(120.0, 4.00)
        24.0  # 120 / 5 = 24 seconds
    """
    if base_recharge <= 0:
        return 0.0

    return base_recharge / (1.0 + global_recharge)
