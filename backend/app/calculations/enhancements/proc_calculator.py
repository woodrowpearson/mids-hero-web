"""
Proc Chance Calculator

Calculates probability of proc IO effects activating using PPM (Procs Per Minute)
system with recharge/cast time/area factor modifiers.

Based on:
    - MidsReborn Core/Base/Data_Classes/Effect.cs (ActualProbability, lines 347-381)
    - MidsReborn Core/Base/Data_Classes/Power.cs (AoEModifier, lines 617-619)
    - Specification: docs/midsreborn/calculations/34-proc-chance-formulas.md
"""

from dataclasses import dataclass, field
from enum import Enum


class PowerType(Enum):
    """Power activation types for proc calculation."""

    CLICK = "click"
    TOGGLE = "toggle"
    AUTO = "auto"


class EffectArea(Enum):
    """Effect area types for proc calculation."""

    SINGLE = "single"  # Single target
    SPHERE = "sphere"  # Spherical AoE
    CONE = "cone"  # Cone AoE


@dataclass
class ProcEnhancement:
    """
    Represents a proc IO enhancement with PPM value.

    Attributes:
        name: Enhancement name
        procs_per_minute: PPM value (0 = legacy flat %, >0 = PPM system)
        base_probability: Legacy flat % chance (0.0-1.0)
        effect_id: For character-specific modifiers (rare)
    """

    name: str
    procs_per_minute: float  # 0 = legacy flat %, >0 = PPM system
    base_probability: float = 0.0  # Legacy flat % (0.0-1.0)
    effect_id: str = ""  # For character-specific modifiers


@dataclass
class PowerProcContext:
    """
    Power properties needed for proc calculation.

    Attributes:
        power_type: Click, Toggle, or Auto
        base_recharge_time: Unmodified recharge in seconds
        current_recharge_time: With enhancements (not global recharge)
        cast_time: Activation time in seconds
        effect_area: Single, Sphere, or Cone
        radius: For AoE powers (feet)
        arc: For cone powers (0-360 degrees)
    """

    power_type: PowerType
    base_recharge_time: float
    current_recharge_time: float
    cast_time: float
    effect_area: EffectArea
    radius: float = 0.0
    arc: int = 0


@dataclass
class CharacterProcContext:
    """
    Character properties affecting proc chance.

    Attributes:
        global_recharge_bonus: From Hasten, set bonuses, etc. (decimal, e.g., 0.7 = +70%)
        effect_modifiers: EffectId -> modifier (rare character-specific bonuses)
    """

    global_recharge_bonus: float = 0.0
    effect_modifiers: dict[str, float] = field(default_factory=dict)


@dataclass
class ProcCalculationResult:
    """
    Result of proc chance calculation with breakdown.

    Attributes:
        proc_chance: Final probability (0.0-1.0)
        aoe_modifier: AoE modifier value
        area_factor: Area factor used in formula
        effective_recharge: Recharge value used in calculation
        min_cap: Minimum proc chance cap
        min_cap_applied: Whether minimum cap was enforced
        max_cap_applied: Whether maximum cap (90%) was enforced
        calculation_method: Which formula was used
    """

    proc_chance: float
    aoe_modifier: float
    area_factor: float
    effective_recharge: float
    min_cap: float
    min_cap_applied: bool
    max_cap_applied: bool
    calculation_method: str


class ProcChanceCalculator:
    """
    Calculate proc activation probability using PPM system.

    Implements Issue 24+ PPM (Procs Per Minute) formula with:
    - Area factor penalties for AoE powers
    - Minimum cap: PPM × 0.015 + 0.05
    - Maximum cap: 90%
    - Global recharge normalization
    """

    MAX_PROC_CHANCE: float = 0.9  # 90% hard cap

    def calculate_aoe_modifier(self, power: PowerProcContext) -> float:
        """
        Calculate AoE modifier based on effect area.

        Formula from Power.AoEModifier (Power.cs lines 617-619):
        - Single Target: 1.0
        - Sphere AoE: 1 + Radius × 0.15
        - Cone AoE: 1 + Radius × 0.15 - Radius × 0.000366669992217794 × (360 - Arc)

        Args:
            power: Power context with area properties

        Returns:
            AoE modifier value (1.0 for single target, >1.0 for AoE)
        """
        if power.effect_area == EffectArea.SINGLE:
            return 1.0

        elif power.effect_area == EffectArea.SPHERE:
            return 1.0 + power.radius * 0.15

        elif power.effect_area == EffectArea.CONE:
            # Cone formula includes arc penalty
            return (
                1.0
                + power.radius * 0.15
                - power.radius * 0.000366669992217794 * (360 - power.arc)
            )

        return 1.0

    def calculate_area_factor(self, power: PowerProcContext) -> float:
        """
        Convert AoE modifier to area factor used in proc formula.

        Formula: areaFactor = AoEModifier × 0.75 + 0.25

        This scales the modifier down and adds a base value.
        Result: Single target = 1.0, AoEs have factor > 1.0 (reduces proc chance)

        Args:
            power: Power context

        Returns:
            Area factor for proc formula
        """
        aoe_modifier = self.calculate_aoe_modifier(power)
        return aoe_modifier * 0.75 + 0.25

    def calculate_effective_recharge(
        self, power: PowerProcContext, character: CharacterProcContext
    ) -> float:
        """
        Calculate power's effective recharge removing global bonuses.

        This finds what the power's recharge would be with only enhancement
        slotting, before global recharge bonuses were applied. This prevents
        global recharge from artificially lowering proc chances.

        Formula:
            effective_recharge = base_recharge / (base_recharge / current_recharge - global_recharge)

        Args:
            power: Power context with recharge values
            character: Character context with global recharge

        Returns:
            Effective recharge in seconds
        """
        if abs(power.current_recharge_time) < 0.001:
            return 0.0

        # Work backwards from current recharge to find base + enhancement only
        denominator = (
            power.base_recharge_time / power.current_recharge_time
            - character.global_recharge_bonus
        )

        if abs(denominator) < 0.001:
            return power.base_recharge_time

        return power.base_recharge_time / denominator

    def calculate_min_proc_chance(self, ppm: float) -> float:
        """
        Calculate minimum proc chance cap.

        Formula: minChance = PPM × 0.015 + 0.05

        Ensures fast-recharging powers still have reasonable proc chance.

        Examples:
            1.0 PPM: 6.5%
            2.0 PPM: 8.0%
            3.5 PPM: 10.25%
            4.5 PPM: 11.75%

        Args:
            ppm: Procs Per Minute value

        Returns:
            Minimum proc chance (0.0-1.0)
        """
        if ppm <= 0:
            return 0.05  # 5% minimum for legacy procs

        return ppm * 0.015 + 0.05

    def calculate_proc_chance(
        self,
        proc: ProcEnhancement,
        power: PowerProcContext,
        character: CharacterProcContext,
    ) -> float:
        """
        Calculate final proc activation probability.

        Core PPM formula (Click powers):
            chance = PPM × (recharge + cast) / (60 × areaFactor)

        Toggle/Auto formula:
            chance = PPM × 10 / (60 × areaFactor)

        With minimum cap (PPM × 0.015 + 0.05) and maximum cap (90%).

        Args:
            proc: Proc enhancement with PPM value
            power: Power context
            character: Character context

        Returns:
            Probability of proc firing (0.0-1.0)
        """
        # Check for legacy flat % proc (pre-Issue 24 system)
        if proc.procs_per_minute <= 0:
            probability = proc.base_probability

        else:
            # PPM system calculation

            # Calculate area factor penalty for AoE powers
            area_factor = self.calculate_area_factor(power)

            # Calculate effective recharge (removing global bonuses)
            effective_recharge = self.calculate_effective_recharge(power, character)

            # Calculate proc chance based on power type
            if power.power_type == PowerType.CLICK:
                # Standard formula: scales with recharge + cast time
                probability = (
                    proc.procs_per_minute
                    * (effective_recharge + power.cast_time)
                    / (60.0 * area_factor)
                )

            else:  # Toggle or Auto
                # Fixed 10-second assumed interval
                probability = proc.procs_per_minute * 10.0 / (60.0 * area_factor)

            # Apply minimum cap
            min_chance = self.calculate_min_proc_chance(proc.procs_per_minute)
            probability = max(min_chance, probability)

            # Apply maximum cap (90%)
            probability = min(self.MAX_PROC_CHANCE, probability)

        # Apply character-specific effect modifiers (if any)
        if proc.effect_id and proc.effect_id in character.effect_modifiers:
            probability += character.effect_modifiers[proc.effect_id]

        # Final clamping to valid probability range
        return max(0.0, min(1.0, probability))

    def calculate_proc_chance_detailed(
        self,
        proc: ProcEnhancement,
        power: PowerProcContext,
        character: CharacterProcContext,
    ) -> ProcCalculationResult:
        """
        Calculate proc chance with detailed breakdown.

        Returns all intermediate values for debugging and display.

        Args:
            proc: Proc enhancement
            power: Power context
            character: Character context

        Returns:
            ProcCalculationResult with full calculation breakdown
        """
        aoe_modifier = self.calculate_aoe_modifier(power)
        area_factor = self.calculate_area_factor(power)
        effective_recharge = self.calculate_effective_recharge(power, character)
        min_cap = self.calculate_min_proc_chance(proc.procs_per_minute)

        # Calculate raw proc chance before caps
        if proc.procs_per_minute <= 0:
            raw_chance = proc.base_probability
            calculation_method = "legacy_flat"
        elif power.power_type == PowerType.CLICK:
            raw_chance = (
                proc.procs_per_minute
                * (effective_recharge + power.cast_time)
                / (60.0 * area_factor)
            )
            calculation_method = "ppm_click"
        else:
            raw_chance = proc.procs_per_minute * 10.0 / (60.0 * area_factor)
            calculation_method = "ppm_toggle_auto"

        # Check if caps applied
        min_cap_applied = proc.procs_per_minute > 0 and raw_chance < min_cap
        max_cap_applied = raw_chance > self.MAX_PROC_CHANCE

        # Calculate final chance with all modifiers
        final_chance = self.calculate_proc_chance(proc, power, character)

        return ProcCalculationResult(
            proc_chance=final_chance,
            aoe_modifier=aoe_modifier,
            area_factor=area_factor,
            effective_recharge=effective_recharge,
            min_cap=min_cap,
            min_cap_applied=min_cap_applied,
            max_cap_applied=max_cap_applied,
            calculation_method=calculation_method,
        )
