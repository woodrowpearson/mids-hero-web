"""
Accuracy & ToHit Aggregation - Build-level accuracy/tohit calculations

Implements accuracy and tohit aggregation for City of Heroes builds.
Maps to MidsReborn's clsToonX.cs GenerateBuildBuffs() and CalcStatTotals() for accuracy/tohit.

CRITICAL DISTINCTION - Accuracy vs ToHit:
===========================================
**Accuracy (Multiplicative)**:
- Multiplies the final accuracy calculation
- Comes from: Set bonuses, Kismet IO, Incarnate abilities
- NOT subject to Enhancement Diversification
- Applied as: (1 + enhancement_accuracy + global_accuracy)
- Example sources:
  * Thunderstrike 5-set bonus: +9% accuracy
  * Kismet +ToHit IO: +6% accuracy (despite the name!)
  * Alpha Incarnate: +5% accuracy

**ToHit (Additive)**:
- Adds to hit chance after accuracy multiplier
- Comes from: Power buffs (Tactics, Build Up, Aim), some set bonuses
- Applied as: (ScalingToHit + global_tohit)
- Example sources:
  * Tactics toggle: +7% tohit (when slotted)
  * Build Up: +20% tohit (temporary)
  * Set bonuses: +3% tohit

FORMULA: base_accuracy * (1 + slotted + global_acc) * (base_tohit + global_tohit)

Maps to:
- File: clsToonX.cs
- Lines 660-662: Accuracy aggregation from enhancements
- Lines 764, 767: Final BuffAcc and BuffToHit calculation
- Lines 1995-1999: Application to individual powers
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AccuracySource(Enum):
    """Source types for accuracy and tohit bonuses"""
    SET_BONUS = "set_bonus"  # Enhancement set bonuses
    SPECIAL_IO = "special_io"  # Special IOs (Kismet, etc.)
    POWER_BUFF = "power_buff"  # Active power buffs (Tactics, Build Up, Aim)
    INCARNATE = "incarnate"  # Incarnate slot bonuses
    ENHANCEMENT = "enhancement"  # Direct enhancement bonuses


@dataclass
class AccuracyContribution:
    """
    Individual contribution to global accuracy or tohit.
    Used for detailed breakdowns in UI tooltips.

    Maps to entries in build_accuracy_contributions table.

    Attributes:
        source_name: Name of the source (e.g., "Thunderstrike", "Kismet +ToHit", "Tactics")
        source_type: Category of source (SET_BONUS, SPECIAL_IO, POWER_BUFF, etc.)
        is_accuracy: True = accuracy (multiplicative), False = tohit (additive)
        magnitude: Bonus value as decimal (e.g., 0.09 for 9%)
        power_name: If from power buff, which power granted it (optional)
    """
    source_name: str
    source_type: AccuracySource
    is_accuracy: bool
    magnitude: float
    power_name: Optional[str] = None

    def __str__(self) -> str:
        """Format for display"""
        buff_type = "Accuracy" if self.is_accuracy else "ToHit"
        power_info = f" ({self.power_name})" if self.power_name else ""
        return f"{self.source_name}{power_info}: +{self.magnitude * 100:.2f}% {buff_type}"


@dataclass
class GlobalAccuracyTotals:
    """
    Aggregated global accuracy and tohit bonuses.
    Maps to MidsReborn's Totals.BuffAcc and Totals.BuffToHit.

    Stored in build_totals_accuracy table with detailed contributions
    in build_accuracy_contributions table.

    Attributes:
        accuracy: Total global accuracy bonus (multiplicative) - e.g., 0.09 = 9%
        tohit: Total global tohit bonus (additive) - e.g., 0.20 = 20%
        accuracy_contributions: Detailed breakdown for accuracy
        tohit_contributions: Detailed breakdown for tohit
    """
    accuracy: float = 0.0
    tohit: float = 0.0
    accuracy_contributions: List[AccuracyContribution] = field(default_factory=list)
    tohit_contributions: List[AccuracyContribution] = field(default_factory=list)

    @property
    def accuracy_percentage(self) -> float:
        """
        Display value for UI (convert decimal to percentage).
        Maps to Statistics.BuffAccuracy in MidsReborn.
        """
        return self.accuracy * 100.0

    @property
    def tohit_percentage(self) -> float:
        """
        Display value for UI (convert decimal to percentage).
        Maps to Statistics.BuffToHit in MidsReborn.
        """
        return self.tohit * 100.0

    def get_accuracy_for_power(self, power_ignores_buffs: bool) -> float:
        """
        Get accuracy bonus for specific power, respecting ignore flags.

        Some powers ignore global accuracy buffs (auto-hit powers, pet summons).
        Maps to clsToonX.cs line 1996.

        Args:
            power_ignores_buffs: True if power has IgnoreBuff(Accuracy) flag

        Returns:
            Accuracy bonus to apply (0.0 if power ignores buffs)
        """
        return 0.0 if power_ignores_buffs else self.accuracy

    def get_tohit_for_power(self, power_ignores_buffs: bool) -> float:
        """
        Get tohit bonus for specific power, respecting ignore flags.

        Maps to clsToonX.cs line 1995.

        Args:
            power_ignores_buffs: True if power has IgnoreBuff(ToHit) flag

        Returns:
            ToHit bonus to apply (0.0 if power ignores buffs)
        """
        return 0.0 if power_ignores_buffs else self.tohit

    def __str__(self) -> str:
        """
        Format like MidsReborn totals display.
        Matches frmTotals.cs display format.
        """
        return f"Accuracy: {self.accuracy_percentage:.2f}%, ToHit: {self.tohit_percentage:.2f}%"


class BuildAccuracyCalculator:
    """
    Calculates global accuracy and tohit from all sources in a build.
    Maps to MidsReborn's GenerateBuildBuffs and CalcStatTotals for accuracy/tohit.

    Usage:
        calculator = BuildAccuracyCalculator()
        totals = calculator.calculate_accuracy_totals(
            set_bonuses=build.active_set_bonuses,
            special_ios=build.special_ios,
            power_buffs=build.active_power_buffs,
            incarnate_bonuses=build.incarnate_bonuses
        )
        print(totals)  # "Accuracy: 38.00%, ToHit: 7.00%"
    """

    def calculate_accuracy_totals(
        self,
        set_bonuses: List[Dict],
        special_ios: List[Dict],
        power_buffs: List[Dict],
        incarnate_bonuses: List[Dict]
    ) -> GlobalAccuracyTotals:
        """
        Aggregate global accuracy and tohit from all sources.

        Implements algorithm from clsToonX.cs lines 660-662 (aggregation)
        and lines 764, 767 (final totals calculation).

        Args:
            set_bonuses: List of active set bonus effects
                Format: [{"name": "Thunderstrike", "type": "accuracy", "magnitude": 0.09}, ...]
            special_ios: List of special IO effects (Kismet, etc.)
                Format: [{"name": "Kismet +ToHit", "type": "accuracy", "magnitude": 0.06}, ...]
            power_buffs: List of active power buffs (Tactics, Build Up, etc.)
                Format: [{"power": "Tactics", "type": "tohit", "magnitude": 0.07}, ...]
            incarnate_bonuses: List of incarnate accuracy/tohit bonuses
                Format: [{"slot": "Alpha", "type": "accuracy", "magnitude": 0.05}, ...]

        Returns:
            GlobalAccuracyTotals with aggregated values and detailed breakdown

        Raises:
            ValueError: If magnitude values are invalid (negative or > 2.0)
        """
        accuracy_total = 0.0
        tohit_total = 0.0
        accuracy_contributions: List[AccuracyContribution] = []
        tohit_contributions: List[AccuracyContribution] = []

        # Variables mirror MidsReborn's _selfEnhance.Effect and _selfBuffs.Effect
        # Map to clsToonX.cs lines 764, 767
        enhance_accuracy = 0.0  # _selfEnhance.Effect[(int)eStatType.BuffAcc]
        buff_accuracy = 0.0  # _selfBuffs.Effect[(int)eStatType.BuffAcc]
        buff_tohit = 0.0  # _selfBuffs.Effect[(int)eStatType.ToHit]

        # STEP 1: Aggregate set bonus accuracy/tohit
        for bonus in set_bonuses:
            magnitude = bonus["magnitude"]
            self._validate_magnitude(magnitude)

            if bonus.get("type") == "accuracy":
                buff_accuracy += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=bonus["name"],
                    source_type=AccuracySource.SET_BONUS,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif bonus.get("type") == "tohit":
                buff_tohit += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=bonus["name"],
                    source_type=AccuracySource.SET_BONUS,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # STEP 2: Aggregate special IO accuracy/tohit
        for io in special_ios:
            magnitude = io["magnitude"]
            self._validate_magnitude(magnitude)

            if io.get("type") == "accuracy":
                enhance_accuracy += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=io["name"],
                    source_type=AccuracySource.SPECIAL_IO,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif io.get("type") == "tohit":
                buff_tohit += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=io["name"],
                    source_type=AccuracySource.SPECIAL_IO,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # STEP 3: Aggregate power buff tohit (typically temporary buffs)
        for buff in power_buffs:
            magnitude = buff["magnitude"]
            self._validate_magnitude(magnitude)

            if buff.get("type") == "tohit":
                buff_tohit += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=buff.get("power", "Unknown"),
                    source_type=AccuracySource.POWER_BUFF,
                    is_accuracy=False,
                    magnitude=magnitude,
                    power_name=buff.get("power")
                ))
            # Some powers grant accuracy buffs (rare)
            elif buff.get("type") == "accuracy":
                buff_accuracy += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=buff.get("power", "Unknown"),
                    source_type=AccuracySource.POWER_BUFF,
                    is_accuracy=True,
                    magnitude=magnitude,
                    power_name=buff.get("power")
                ))

        # STEP 4: Aggregate incarnate accuracy/tohit
        for bonus in incarnate_bonuses:
            magnitude = bonus["magnitude"]
            self._validate_magnitude(magnitude)

            if bonus.get("type") == "accuracy":
                buff_accuracy += magnitude
                accuracy_contributions.append(AccuracyContribution(
                    source_name=bonus.get("slot", "Incarnate"),
                    source_type=AccuracySource.INCARNATE,
                    is_accuracy=True,
                    magnitude=magnitude
                ))
            elif bonus.get("type") == "tohit":
                buff_tohit += magnitude
                tohit_contributions.append(AccuracyContribution(
                    source_name=bonus.get("slot", "Incarnate"),
                    source_type=AccuracySource.INCARNATE,
                    is_accuracy=False,
                    magnitude=magnitude
                ))

        # STEP 5: Calculate final totals
        # Maps to clsToonX.cs lines 764, 767
        # Totals.BuffAcc = _selfEnhance.Effect[BuffAcc] + _selfBuffs.Effect[BuffAcc]
        # Totals.BuffToHit = _selfBuffs.Effect[ToHit]
        accuracy_total = enhance_accuracy + buff_accuracy
        tohit_total = buff_tohit

        # No caps or diminishing returns!
        # Unlike defense (45% soft cap) or resistance (75-90% hard cap),
        # accuracy and tohit have no aggregation limits.
        # Final hit chance is capped at 5%-95% per attack, but totals are uncapped.

        return GlobalAccuracyTotals(
            accuracy=accuracy_total,
            tohit=tohit_total,
            accuracy_contributions=accuracy_contributions,
            tohit_contributions=tohit_contributions
        )

    def _validate_magnitude(self, magnitude: float) -> None:
        """
        Validate magnitude value.

        Args:
            magnitude: Bonus magnitude to validate

        Raises:
            ValueError: If magnitude is invalid
        """
        if magnitude < 0.0 or magnitude > 2.0:
            raise ValueError(f"Invalid magnitude: {magnitude} (must be 0.0-2.0)")

    def format_accuracy_breakdown(self, totals: GlobalAccuracyTotals) -> str:
        """
        Format detailed breakdown for display.
        Useful for "hover to see sources" tooltip in totals window.

        Matches frmTotals.cs tooltip formatting.

        Args:
            totals: GlobalAccuracyTotals to format

        Returns:
            Multi-line string with formatted breakdown

        Example:
            Total Accuracy: 38.00%
              Thunderstrike: +9.00%
              Decimation: +9.00%
              Kismet +ToHit: +6.00%

            Total ToHit: 7.00%
              Tactics: +7.00%
        """
        lines = []
        lines.append(f"Total Accuracy: {totals.accuracy_percentage:.2f}%")
        if totals.accuracy_contributions:
            for contrib in totals.accuracy_contributions:
                lines.append(f"  {contrib.source_name}: +{contrib.magnitude * 100:.2f}%")
        else:
            lines.append("  (No accuracy bonuses)")

        lines.append(f"\nTotal ToHit: {totals.tohit_percentage:.2f}%")
        if totals.tohit_contributions:
            for contrib in totals.tohit_contributions:
                power_info = f" ({contrib.power_name})" if contrib.power_name else ""
                lines.append(f"  {contrib.source_name}{power_info}: +{contrib.magnitude * 100:.2f}%")
        else:
            lines.append("  (No tohit bonuses)")

        return "\n".join(lines)
