"""
Resistance Aggregation - Build-level resistance calculations

Implements resistance aggregation for City of Heroes builds.
Maps to MidsReborn's clsToonX.cs resistance calculation logic.

Resistance in CoH is damage type based (no positional resistance):
- Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic

Key mechanic: Resistance bonuses stack ADDITIVELY up to the archetype cap.

Example:
- Power 1 grants +30% S/L resistance
- Power 2 grants +20% S/L resistance
- Power 3 grants +25% S/L resistance
- Total: 30% + 20% + 25% = 75% resistance
- If Tanker (90% cap): 75% applies
- If Scrapper (75% cap): 75% applies (at cap!)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from app.calculations.core import ArchetypeType, get_archetype_caps


class ResistanceType(Enum):
    """
    Resistance type enumeration.

    All resistance is typed (damage type based).
    No positional resistance exists in City of Heroes.
    """
    SMASHING = "Smashing"
    LETHAL = "Lethal"
    FIRE = "Fire"
    COLD = "Cold"
    ENERGY = "Energy"
    NEGATIVE_ENERGY = "Negative Energy"
    TOXIC = "Toxic"
    PSIONIC = "Psionic"


# All resistance types
ALL_RESISTANCE_TYPES = {
    ResistanceType.SMASHING,
    ResistanceType.LETHAL,
    ResistanceType.FIRE,
    ResistanceType.COLD,
    ResistanceType.ENERGY,
    ResistanceType.NEGATIVE_ENERGY,
    ResistanceType.TOXIC,
    ResistanceType.PSIONIC
}


@dataclass
class ResistanceValues:
    """
    Complete resistance values for a build.

    Stores resistance values for all damage types.

    Attributes:
        values: Dict mapping resistance types to values (0.0-1.0 scale, e.g., 0.75 = 75%)
        archetype: Optional archetype for cap enforcement
    """
    values: Dict[ResistanceType, float] = field(default_factory=dict)
    archetype: Optional[ArchetypeType] = None

    @classmethod
    def empty(cls, archetype: Optional[ArchetypeType] = None) -> 'ResistanceValues':
        """
        Create empty resistance values (all zeros).

        Args:
            archetype: Optional archetype for cap enforcement

        Returns:
            ResistanceValues with all zeros
        """
        return cls(
            values={rt: 0.0 for rt in ALL_RESISTANCE_TYPES},
            archetype=archetype
        )

    def get_resistance(self, resistance_type: ResistanceType) -> float:
        """
        Get resistance value for a specific type.

        Args:
            resistance_type: Resistance type to query

        Returns:
            Resistance value (0.0-1.0 scale)
        """
        return self.values.get(resistance_type, 0.0)

    def set_resistance(self, resistance_type: ResistanceType, value: float) -> None:
        """
        Set resistance value for a specific type.

        Args:
            resistance_type: Resistance type to set
            value: Resistance value (0.0-1.0 scale)
        """
        self.values[resistance_type] = value

    def add_resistance(self, resistance_type: ResistanceType, value: float) -> None:
        """
        Add resistance value to a specific type.

        Args:
            resistance_type: Resistance type to modify
            value: Resistance value to add (can be negative for debuffs)
        """
        current = self.get_resistance(resistance_type)
        self.set_resistance(resistance_type, current + value)

    def apply_caps(self) -> 'ResistanceValues':
        """
        Apply archetype-specific resistance caps.

        Resistance has hard caps that vary by archetype:
        - Tanker/Brute: 90%
        - Kheldian: 85%
        - Others: 75%

        Returns:
            Self for chaining
        """
        if self.archetype is None:
            return self

        caps = get_archetype_caps(self.archetype)

        # Apply resistance cap to all types
        for resistance_type in ALL_RESISTANCE_TYPES:
            if resistance_type in self.values:
                self.values[resistance_type] = caps.apply_resistance_cap(
                    self.values[resistance_type]
                )

        return self

    def is_at_cap(self, resistance_type: ResistanceType, tolerance: float = 0.001) -> bool:
        """
        Check if resistance type is at cap for this archetype.

        Args:
            resistance_type: Resistance type to check
            tolerance: Floating-point comparison tolerance

        Returns:
            True if at or above cap
        """
        if self.archetype is None:
            return False

        caps = get_archetype_caps(self.archetype)
        value = self.get_resistance(resistance_type)
        return value >= (caps.resistance_cap - tolerance)


def aggregate_resistance_bonuses(
    resistance_bonuses: List[Dict[ResistanceType, float]],
    archetype: Optional[ArchetypeType] = None
) -> ResistanceValues:
    """
    Aggregate multiple resistance bonuses into final resistance values.

    Resistance bonuses stack ADDITIVELY up to the archetype cap.
    This is different from defense (which has no hard cap except display).

    Args:
        resistance_bonuses: List of resistance bonus dicts (ResistanceType -> value)
        archetype: Optional archetype for cap enforcement

    Returns:
        ResistanceValues with aggregated bonuses

    Examples:
        >>> # Power 1 grants +30% S/L resistance
        >>> power1 = {ResistanceType.SMASHING: 0.30, ResistanceType.LETHAL: 0.30}
        >>> # Power 2 grants +20% S/L resistance
        >>> power2 = {ResistanceType.SMASHING: 0.20, ResistanceType.LETHAL: 0.20}
        >>> # Power 3 grants +25% S/L resistance
        >>> power3 = {ResistanceType.SMASHING: 0.25, ResistanceType.LETHAL: 0.25}
        >>> result = aggregate_resistance_bonuses([power1, power2, power3])
        >>> result.get_resistance(ResistanceType.SMASHING)
        0.75
    """
    result = ResistanceValues.empty(archetype)

    # Sum all resistance bonuses (additive stacking)
    for bonus_dict in resistance_bonuses:
        for resistance_type, value in bonus_dict.items():
            result.add_resistance(resistance_type, value)

    # Apply archetype caps
    result.apply_caps()

    return result


def calculate_damage_reduction(resistance: float) -> float:
    """
    Calculate damage reduction from resistance value.

    Damage reduction is linear with resistance:
    - 0% resistance = 100% damage taken
    - 50% resistance = 50% damage taken
    - 75% resistance = 25% damage taken
    - 90% resistance = 10% damage taken

    Args:
        resistance: Resistance value (0.0-1.0 scale)

    Returns:
        Damage multiplier (0.0-1.0, where 0.25 = take 25% damage)

    Examples:
        >>> calculate_damage_reduction(0.75)  # 75% resistance
        0.25  # Take 25% damage
        >>> calculate_damage_reduction(0.90)  # 90% resistance
        0.10  # Take 10% damage
    """
    return 1.0 - resistance
