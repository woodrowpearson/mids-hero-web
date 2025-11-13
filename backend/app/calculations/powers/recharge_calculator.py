"""
Power Recharge Calculator

Calculates actual recharge time for powers based on base recharge, local enhancements,
and global recharge bonuses. Implements MidsReborn's recharge calculation logic.

Based on:
    - MidsReborn clsToonX.cs (GBPA methods, lines 1157-1160, 1369-1374, 1409-1412)
    - MidsReborn Core/Statistics.cs (BuffHaste, lines 231-236)
    - MidsReborn Core/Enhancement.cs (ApplyED, Schedule A)
    - Specification: docs/midsreborn/calculations/07-power-recharge-modifiers.md
"""

from dataclasses import dataclass

from ..core.enhancement_schedules import EDSchedule, apply_ed


@dataclass
class RechargeCalculationResult:
    """
    Complete result of power recharge calculation.

    Attributes:
        base_recharge: Original power recharge time (seconds)
        local_recharge_bonus_pre_ed: Local enhancement bonus before ED
        local_recharge_bonus_after_ed: Local enhancement bonus after ED
        local_recharge_multiplier: Local multiplier (1 + local_bonus)
        global_recharge_bonus: Global recharge bonus from character
        global_recharge_multiplier: Global multiplier (1 + global_bonus)
        total_multiplier: Combined multiplier (local × global)
        actual_recharge: Final recharge time after all bonuses
        is_capped: Whether recharge hit archetype cap
        archetype_cap: AT's recharge cap value (e.g., 5.0 = 400%)
    """

    base_recharge: float
    local_recharge_bonus_pre_ed: float
    local_recharge_bonus_after_ed: float
    local_recharge_multiplier: float
    global_recharge_bonus: float
    global_recharge_multiplier: float
    total_multiplier: float
    actual_recharge: float
    is_capped: bool
    archetype_cap: float


class RechargeCalculator:
    """
    Calculate power recharge times with local and global bonuses.

    Implementation based on:
        - clsToonX.cs GBPA pipeline
        - Enhancement.cs ApplyED (Schedule A for recharge)
        - Statistics.cs BuffHaste calculation

    The calculator handles:
    1. Local recharge enhancements (with ED)
    2. Global recharge bonuses (Hasten, set bonuses, etc.)
    3. Archetype recharge caps
    """

    def calculate_recharge(
        self,
        base_recharge: float,
        local_bonuses: list[float],
        global_bonus: float,
        archetype_cap: float = 5.0,
    ) -> RechargeCalculationResult:
        """
        Calculate actual recharge time for a power.

        Implementation from clsToonX.cs lines 1157-1160, 1374, 1409-1412.

        Formula:
            ActualRecharge = BaseRecharge / (LocalMultiplier × GlobalMultiplier)
            Where:
                LocalMultiplier = 1 + ApplyED(Schedule A, Sum(LocalBonuses))
                GlobalMultiplier = 1 + GlobalBonus

        Args:
            base_recharge: Power's BaseRechargeTime (e.g., 60.0 seconds)
            local_bonuses: List of recharge enhancement values (e.g., [0.424, 0.424])
            global_bonus: Character's BuffHaste from build totals (e.g., 0.70 for Hasten)
            archetype_cap: AT-specific cap (default 5.0 = 400%)

        Returns:
            RechargeCalculationResult with all intermediate and final values

        Example:
            >>> calc = RechargeCalculator()
            >>> # 60s power with 2× L50 Recharge IOs and Hasten
            >>> result = calc.calculate_recharge(
            ...     base_recharge=60.0,
            ...     local_bonuses=[0.424, 0.424],
            ...     global_bonus=0.70,
            ...     archetype_cap=5.0
            ... )
            >>> result.actual_recharge
            16.15
        """
        # STEP 1: Handle zero-recharge powers (auto powers, toggles)
        # From clsToonX.cs - check for float.Epsilon
        if abs(base_recharge) < 1e-7:
            return RechargeCalculationResult(
                base_recharge=0.0,
                local_recharge_bonus_pre_ed=0.0,
                local_recharge_bonus_after_ed=0.0,
                local_recharge_multiplier=1.0,
                global_recharge_bonus=0.0,
                global_recharge_multiplier=1.0,
                total_multiplier=1.0,
                actual_recharge=0.0,
                is_capped=False,
                archetype_cap=archetype_cap,
            )

        # STEP 2: Sum local recharge enhancements (pre-ED)
        # From GBPA_Pass1_EnhancePreED
        local_bonus_pre_ed = sum(local_bonuses)

        # STEP 3: Apply Enhancement Diversification (ED) to local bonuses
        # From GBPA_Pass2_ApplyED - RechargeTime uses Schedule A
        # Schedule A is the standard ED curve (same as damage, accuracy, etc.)
        local_bonus_after_ed = apply_ed(EDSchedule.A, local_bonus_pre_ed)

        # STEP 4: Convert local bonus to multiplier
        # From GBPA_Pass5_MultiplyPreBuff line 1409
        # powerBuffed.RechargeTime /= powerMath.RechargeTime
        # powerMath.RechargeTime contains (1 + local_bonus_after_ed)
        local_multiplier = 1.0 + local_bonus_after_ed

        # STEP 5: Convert global bonus to multiplier
        # global_bonus is stored as decimal (0.70 for +70%)
        # From Statistics.cs BuffHaste calculation
        global_multiplier = 1.0 + global_bonus

        # STEP 6: Calculate combined multiplier
        # Local and global multiply together
        total_multiplier = local_multiplier * global_multiplier

        # STEP 7: Calculate actual recharge time
        # Formula: ActualRecharge = BaseRecharge / TotalMultiplier
        # From GBPA_Pass5_MultiplyPreBuff
        actual_recharge = base_recharge / total_multiplier

        # STEP 8: Apply archetype cap
        # From GBPA_ApplyArchetypeCaps line 1157-1160
        # Cap is on the final recharge time (not the multiplier)
        # RechargeCap = 5.0 means power can't recharge faster than base/5
        min_recharge = base_recharge / archetype_cap
        is_capped = actual_recharge < min_recharge

        if is_capped:
            actual_recharge = min_recharge

        return RechargeCalculationResult(
            base_recharge=base_recharge,
            local_recharge_bonus_pre_ed=local_bonus_pre_ed,
            local_recharge_bonus_after_ed=local_bonus_after_ed,
            local_recharge_multiplier=local_multiplier,
            global_recharge_bonus=global_bonus,
            global_recharge_multiplier=global_multiplier,
            total_multiplier=total_multiplier,
            actual_recharge=actual_recharge,
            is_capped=is_capped,
            archetype_cap=archetype_cap,
        )

    def calculate_global_recharge(
        self,
        set_bonuses: list[float],
        hasten_active: bool = False,
        other_buffs: list[float] | None = None,
    ) -> float:
        """
        Calculate total global recharge bonus from all sources.

        Implementation from clsToonX.cs lines 763-866:
            Totals.BuffHaste = _selfEnhance.Effect[Haste] + _selfBuffs.Effect[Haste]

        Args:
            set_bonuses: List of set bonus recharge values (e.g., [0.075, 0.0625, ...])
            hasten_active: Whether Hasten power is active (+70%)
            other_buffs: Other global recharge buffs (Incarnate, team buffs, etc.)

        Returns:
            Total global recharge bonus as decimal (e.g., 0.825 for +82.5%)

        Example:
            >>> calc = RechargeCalculator()
            >>> # 5× LotG (+37.5%) + 4× +6.25% sets (+25%) + Hasten (+70%)
            >>> global_bonus = calc.calculate_global_recharge(
            ...     set_bonuses=[0.075] * 5 + [0.0625] * 4,
            ...     hasten_active=True
            ... )
            >>> global_bonus
            1.325
        """
        total = 0.0

        # Add set bonuses (subject to Rule of 5)
        total += sum(set_bonuses)

        # Add Hasten if active (+70% global recharge)
        if hasten_active:
            total += 0.70

        # Add other buffs (Incarnate abilities, team buffs, etc.)
        if other_buffs:
            total += sum(other_buffs)

        return total

    def check_perma_hasten(
        self,
        global_recharge_without_hasten: float,
        local_recharge_in_hasten: float = 0.95,
    ) -> tuple[bool, float]:
        """
        Check if Hasten can be permanent.

        Hasten details:
            - Duration: 120 seconds
            - Base Recharge: 120 seconds
            - Cast Time: ~1.17 seconds
            - Provides: +70% global recharge

        For perma-Hasten:
            - Hasten must recharge in ≤ 118.83 seconds (120s - 1.17s cast)
            - Need: 120 / (local_mult × global_mult) ≤ 118.83

        Args:
            global_recharge_without_hasten: Global recharge excluding Hasten's +70%
            local_recharge_in_hasten: Local recharge slotted in Hasten power
                                     (default 0.95 = ~95% after ED from 3 SOs)

        Returns:
            Tuple of (is_perma, actual_recharge_time)

        Example:
            >>> calc = RechargeCalculator()
            >>> # 82.5% global without Hasten, 95% local in Hasten
            >>> is_perma, recharge = calc.check_perma_hasten(0.825, 0.95)
            >>> is_perma
            True
            >>> recharge
            33.71
        """
        HASTEN_DURATION = 120.0
        HASTEN_BASE_RECHARGE = 120.0
        HASTEN_CAST_TIME = 1.17
        BUFFER = 2.0  # Safety buffer for lag/animation

        # Calculate multipliers
        local_mult = 1.0 + local_recharge_in_hasten
        global_mult = 1.0 + global_recharge_without_hasten
        total_mult = local_mult * global_mult

        # Calculate actual recharge time
        actual_recharge = HASTEN_BASE_RECHARGE / total_mult

        # Check if recharges before duration expires
        max_allowed_recharge = HASTEN_DURATION - HASTEN_CAST_TIME - BUFFER
        is_perma = actual_recharge <= max_allowed_recharge

        return is_perma, actual_recharge

    def format_recharge_display(self, recharge_time: float) -> str:
        """
        Format recharge time for display matching MidsReborn style.

        Args:
            recharge_time: Recharge time in seconds

        Returns:
            Formatted string: "{time:.2f}s"

        Example:
            >>> calc = RechargeCalculator()
            >>> calc.format_recharge_display(16.15)
            '16.15s'
            >>> calc.format_recharge_display(0.0)
            'N/A'
        """
        if recharge_time <= 0:
            return "N/A"
        return f"{recharge_time:.2f}s"

    def format_global_recharge_display(self, global_bonus: float) -> str:
        """
        Format global recharge bonus for display.

        Converts from storage format (decimal) to display format (percentage).
        From Statistics.cs line 231-236:
            Display = (BuffHaste + 1) × 100

        Args:
            global_bonus: Global recharge bonus as decimal (e.g., 0.70)

        Returns:
            Formatted percentage string (e.g., "170.0%")

        Example:
            >>> calc = RechargeCalculator()
            >>> calc.format_global_recharge_display(0.70)
            '170.0%'
            >>> calc.format_global_recharge_display(1.525)
            '252.5%'
        """
        percentage = (global_bonus + 1.0) * 100
        return f"{percentage:.1f}%"


# Error Handling


class RechargeCalculationError(Exception):
    """Base exception for recharge calculation errors."""

    pass


class InvalidRechargeConfigError(RechargeCalculationError):
    """Raised when recharge configuration is invalid."""

    pass


def validate_recharge_config(
    base_recharge: float,
    local_bonuses: list[float],
    global_bonus: float,
    archetype_cap: float,
) -> None:
    """
    Validate recharge calculation configuration.

    Args:
        base_recharge: Base recharge time
        local_bonuses: Local enhancement bonuses
        global_bonus: Global recharge bonus
        archetype_cap: Archetype recharge cap

    Raises:
        InvalidRechargeConfigError: If configuration is invalid

    Example:
        >>> validate_recharge_config(-1.0, [], 0.0, 5.0)
        Traceback (most recent call last):
        ...
        InvalidRechargeConfigError: Base recharge cannot be negative: -1.0
    """
    if base_recharge < 0:
        raise InvalidRechargeConfigError(
            f"Base recharge cannot be negative: {base_recharge}"
        )

    for bonus in local_bonuses:
        if bonus < 0:
            raise InvalidRechargeConfigError(f"Local bonus cannot be negative: {bonus}")

    if global_bonus < 0:
        raise InvalidRechargeConfigError(
            f"Global bonus cannot be negative: {global_bonus}"
        )

    if archetype_cap <= 0:
        raise InvalidRechargeConfigError(
            f"Archetype cap must be positive: {archetype_cap}"
        )
