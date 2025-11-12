"""
Damage Aggregation - Build-level damage buff calculations

Implements global damage buffs for City of Heroes builds.
Maps to MidsReborn's clsToonX.cs damage buff calculation logic.

Damage Buffs in CoH:
- Damage buffs stack ADDITIVELY
- Cap varies by archetype (Blasters: 500%, Scrappers: 400%, etc.)
- Heuristic modes for character build display:
  - MAX: Assumes all buffs active (Fury 100%, Aim+BU, etc.)
  - AVG: Assumes realistic sustained values (Fury 50%, etc.)
  - MIN: Base values only (no temporary buffs)

Key mechanic: Damage = BaseDamage × (1 + DamageBuff)

Example:
- Power does 100 base damage
- Character has 95% damage buff (global + enhancements)
- Final damage = 100 × (1 + 0.95) = 195 damage
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from app.calculations.core import ArchetypeType, get_archetype_caps


class DamageHeuristic(Enum):
    """
    Damage calculation heuristic mode.

    Determines which temporary buffs to include in damage calculations.
    """
    MAX = "Max"  # All buffs active (Fury 100%, all temp buffs)
    AVG = "Average"  # Realistic sustained values (Fury 50%, typical uptime)
    MIN = "Min"  # Base values only (no temporary buffs)


@dataclass
class DamageBuffSource:
    """
    A source of damage buff for tracking.

    Attributes:
        name: Source name (e.g., "Fury", "Aim", "Enhancement")
        value: Damage buff value (0.0-1.0 scale)
        is_temporary: Whether this is a temporary/clickable buff
        avg_multiplier: Multiplier for AVG mode (0.0-1.0, e.g., 0.5 for 50% uptime)
    """
    name: str
    value: float
    is_temporary: bool = False
    avg_multiplier: float = 1.0  # Used for AVG heuristic


@dataclass
class DamageValues:
    """
    Complete damage buff values for a build.

    Stores damage buffs from various sources and provides methods for
    calculating total damage with different heuristics.

    Attributes:
        base_damage_buff: Base damage buff (always applied)
        buff_sources: List of all damage buff sources
        archetype: Optional archetype for cap enforcement
    """
    base_damage_buff: float = 0.0
    buff_sources: List[DamageBuffSource] = None
    archetype: Optional[ArchetypeType] = None

    def __post_init__(self):
        """Initialize buff_sources list if not provided."""
        if self.buff_sources is None:
            self.buff_sources = []

    @classmethod
    def empty(cls, archetype: Optional[ArchetypeType] = None) -> 'DamageValues':
        """
        Create empty damage values (zero damage buff).

        Args:
            archetype: Optional archetype for cap enforcement

        Returns:
            DamageValues with zero damage buff
        """
        return cls(base_damage_buff=0.0, buff_sources=[], archetype=archetype)

    def add_buff(
        self,
        name: str,
        value: float,
        is_temporary: bool = False,
        avg_multiplier: float = 1.0
    ) -> None:
        """
        Add a damage buff source.

        Args:
            name: Source name
            value: Damage buff value (0.0-1.0 scale)
            is_temporary: Whether this is a temporary buff
            avg_multiplier: Multiplier for AVG mode (0.0-1.0)
        """
        source = DamageBuffSource(
            name=name,
            value=value,
            is_temporary=is_temporary,
            avg_multiplier=avg_multiplier
        )
        self.buff_sources.append(source)

    def calculate_total_damage_buff(
        self,
        heuristic: DamageHeuristic = DamageHeuristic.MAX
    ) -> float:
        """
        Calculate total damage buff with given heuristic.

        Args:
            heuristic: Which heuristic mode to use

        Returns:
            Total damage buff value (0.0+ scale)

        Examples:
            >>> # Brute with Fury and enhancements
            >>> values = DamageValues.empty()
            >>> values.add_buff("Enhancement", 0.95, is_temporary=False)
            >>> values.add_buff("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)
            >>> values.calculate_total_damage_buff(DamageHeuristic.MAX)
            1.75  # 95% + 80% = 175%
            >>> values.calculate_total_damage_buff(DamageHeuristic.AVG)
            1.35  # 95% + (80% * 0.5) = 135%
            >>> values.calculate_total_damage_buff(DamageHeuristic.MIN)
            0.95  # Only enhancement (not temporary)
        """
        total = self.base_damage_buff

        for source in self.buff_sources:
            if heuristic == DamageHeuristic.MAX:
                # Include all buffs
                total += source.value
            elif heuristic == DamageHeuristic.AVG:
                # Apply multiplier to temporary buffs
                if source.is_temporary:
                    total += source.value * source.avg_multiplier
                else:
                    total += source.value
            elif heuristic == DamageHeuristic.MIN:
                # Only non-temporary buffs
                if not source.is_temporary:
                    total += source.value

        return total

    def apply_cap(self, damage_buff: float) -> float:
        """
        Apply archetype-specific damage cap.

        Args:
            damage_buff: Damage buff value to cap

        Returns:
            Capped damage buff value
        """
        if self.archetype is None:
            return damage_buff

        caps = get_archetype_caps(self.archetype)
        return caps.apply_damage_cap(damage_buff)

    def get_capped_damage_buff(
        self,
        heuristic: DamageHeuristic = DamageHeuristic.MAX
    ) -> float:
        """
        Get total damage buff with heuristic AND archetype cap applied.

        Args:
            heuristic: Which heuristic mode to use

        Returns:
            Capped damage buff value

        Examples:
            >>> # Blaster at damage cap (500% = 4.0)
            >>> values = DamageValues.empty(ArchetypeType.BLASTER)
            >>> values.add_buff("Enhancement", 0.95)
            >>> values.add_buff("Aim", 0.625, is_temporary=True)
            >>> values.add_buff("Build Up", 1.00, is_temporary=True)
            >>> uncapped = values.calculate_total_damage_buff(DamageHeuristic.MAX)
            >>> # uncapped would be 2.575 (257.5%)
            >>> capped = values.get_capped_damage_buff(DamageHeuristic.MAX)
            >>> # capped at archetype limit
        """
        total = self.calculate_total_damage_buff(heuristic)
        return self.apply_cap(total)

    def is_at_cap(
        self,
        heuristic: DamageHeuristic = DamageHeuristic.MAX,
        tolerance: float = 0.001
    ) -> bool:
        """
        Check if damage buff is at archetype cap for given heuristic.

        Args:
            heuristic: Which heuristic mode to check
            tolerance: Floating-point comparison tolerance

        Returns:
            True if at or above cap
        """
        if self.archetype is None:
            return False

        caps = get_archetype_caps(self.archetype)
        total = self.calculate_total_damage_buff(heuristic)

        return total >= (caps.damage_cap - tolerance)

    def get_all_heuristics(self) -> Dict[DamageHeuristic, float]:
        """
        Get damage buff values for all heuristic modes.

        Returns:
            Dict mapping heuristic to capped damage buff value

        Examples:
            >>> values = DamageValues.empty()
            >>> values.add_buff("Enhancement", 0.95)
            >>> values.add_buff("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)
            >>> values.get_all_heuristics()
            {
                DamageHeuristic.MAX: 1.75,
                DamageHeuristic.AVG: 1.35,
                DamageHeuristic.MIN: 0.95
            }
        """
        return {
            DamageHeuristic.MAX: self.get_capped_damage_buff(DamageHeuristic.MAX),
            DamageHeuristic.AVG: self.get_capped_damage_buff(DamageHeuristic.AVG),
            DamageHeuristic.MIN: self.get_capped_damage_buff(DamageHeuristic.MIN)
        }


def aggregate_damage_buffs(
    buff_sources: List[DamageBuffSource],
    archetype: Optional[ArchetypeType] = None
) -> DamageValues:
    """
    Aggregate multiple damage buff sources into DamageValues.

    Damage buffs stack ADDITIVELY up to the archetype cap.

    Args:
        buff_sources: List of damage buff sources
        archetype: Optional archetype for cap enforcement

    Returns:
        DamageValues with aggregated buffs

    Examples:
        >>> # Scrapper with enhancement + Fury (if Brute secondary)
        >>> sources = [
        ...     DamageBuffSource("Enhancement", 0.95, is_temporary=False),
        ...     DamageBuffSource("Fury", 0.80, is_temporary=True, avg_multiplier=0.5)
        ... ]
        >>> result = aggregate_damage_buffs(sources, ArchetypeType.SCRAPPER)
        >>> result.calculate_total_damage_buff(DamageHeuristic.MAX)
        1.75  # 95% + 80%
    """
    result = DamageValues.empty(archetype)
    result.buff_sources = buff_sources.copy()

    return result


def calculate_damage_with_buff(
    base_damage: float,
    damage_buff: float
) -> float:
    """
    Calculate final damage with damage buff applied.

    Formula: FinalDamage = BaseDamage × (1 + DamageBuff)

    Args:
        base_damage: Base damage value
        damage_buff: Damage buff value (0.0+ scale)

    Returns:
        Final damage value

    Examples:
        >>> # 100 base damage with 95% buff
        >>> calculate_damage_with_buff(100.0, 0.95)
        195.0

        >>> # At Blaster damage cap (500%)
        >>> calculate_damage_with_buff(100.0, 4.00)
        500.0
    """
    if base_damage <= 0:
        return 0.0

    return base_damage * (1.0 + damage_buff)
