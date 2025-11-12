"""
Defense Aggregation - Build-level defense calculations

Implements defense aggregation for City of Heroes builds.
Maps to MidsReborn's clsToonX.cs defense calculation logic.

Defense in CoH has two classification systems:
1. **Typed Defense**: Smashing, Lethal, Fire, Cold, Energy, Negative, Toxic, Psionic
2. **Positional Defense**: Melee, Ranged, AoE

Key mechanic: When an attack comes in, the game checks BOTH typed and positional defense.
The HIGHER of the two values is used. This is the "highest wins" rule.

Example:
- You have 30% Smashing (typed) and 40% Melee (positional)
- An enemy makes a melee smashing attack
- Game checks: max(30%, 40%) = 40% defense applies
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from app.calculations.core import ArchetypeType, get_archetype_caps


class DefenseType(Enum):
    """
    Defense type enumeration.

    Typed defense protects against specific damage types.
    Positional defense protects against attack delivery methods.
    """
    # Typed Defense (damage type based)
    SMASHING = "Smashing"
    LETHAL = "Lethal"
    FIRE = "Fire"
    COLD = "Cold"
    ENERGY = "Energy"
    NEGATIVE_ENERGY = "Negative Energy"
    TOXIC = "Toxic"
    PSIONIC = "Psionic"

    # Positional Defense (attack vector based)
    MELEE = "Melee"
    RANGED = "Ranged"
    AOE = "AoE"


# Soft cap constant
DEFENSE_SOFT_CAP = 0.45  # 45% - Diminishing returns beyond this point

# Defense type categories
TYPED_DEFENSE_TYPES = {
    DefenseType.SMASHING,
    DefenseType.LETHAL,
    DefenseType.FIRE,
    DefenseType.COLD,
    DefenseType.ENERGY,
    DefenseType.NEGATIVE_ENERGY,
    DefenseType.TOXIC,
    DefenseType.PSIONIC
}

POSITIONAL_DEFENSE_TYPES = {
    DefenseType.MELEE,
    DefenseType.RANGED,
    DefenseType.AOE
}


@dataclass
class DefenseValues:
    """
    Complete defense values for a build.

    Stores both typed and positional defense values.

    Attributes:
        typed: Dict mapping typed defense types to values (0.0-1.0 scale, e.g., 0.30 = 30%)
        positional: Dict mapping positional defense types to values (0.0-1.0 scale)
        archetype: Optional archetype for cap enforcement
    """
    typed: Dict[DefenseType, float] = field(default_factory=dict)
    positional: Dict[DefenseType, float] = field(default_factory=dict)
    archetype: Optional[ArchetypeType] = None

    @classmethod
    def empty(cls, archetype: Optional[ArchetypeType] = None) -> 'DefenseValues':
        """
        Create empty defense values (all zeros).

        Args:
            archetype: Optional archetype for cap enforcement

        Returns:
            DefenseValues with all zeros
        """
        return cls(
            typed={dt: 0.0 for dt in TYPED_DEFENSE_TYPES},
            positional={dt: 0.0 for dt in POSITIONAL_DEFENSE_TYPES},
            archetype=archetype
        )

    def get_defense(self, defense_type: DefenseType) -> float:
        """
        Get defense value for a specific type.

        Args:
            defense_type: Defense type to query

        Returns:
            Defense value (0.0-1.0 scale)
        """
        if defense_type in self.typed:
            return self.typed[defense_type]
        elif defense_type in self.positional:
            return self.positional[defense_type]
        else:
            return 0.0

    def set_defense(self, defense_type: DefenseType, value: float) -> None:
        """
        Set defense value for a specific type.

        Args:
            defense_type: Defense type to set
            value: Defense value (0.0-1.0 scale)
        """
        if defense_type in TYPED_DEFENSE_TYPES:
            self.typed[defense_type] = value
        elif defense_type in POSITIONAL_DEFENSE_TYPES:
            self.positional[defense_type] = value

    def add_defense(self, defense_type: DefenseType, value: float) -> None:
        """
        Add defense value to a specific type.

        Args:
            defense_type: Defense type to modify
            value: Defense value to add (can be negative for debuffs)
        """
        current = self.get_defense(defense_type)
        self.set_defense(defense_type, current + value)

    def apply_caps(self) -> 'DefenseValues':
        """
        Apply archetype-specific defense caps.

        Note: Defense has no hard gameplay cap, only soft cap at 45%.
        The display cap (from ArchetypeCaps) is for UI purposes only.

        Returns:
            Self for chaining
        """
        if self.archetype is None:
            return self

        caps = get_archetype_caps(self.archetype)

        # Apply display cap to all typed defense
        for defense_type in TYPED_DEFENSE_TYPES:
            if defense_type in self.typed:
                self.typed[defense_type] = caps.apply_defense_cap(
                    self.typed[defense_type]
                )

        # Apply display cap to all positional defense
        for defense_type in POSITIONAL_DEFENSE_TYPES:
            if defense_type in self.positional:
                self.positional[defense_type] = caps.apply_defense_cap(
                    self.positional[defense_type]
                )

        return self

    def is_at_soft_cap(self, defense_type: DefenseType, tolerance: float = 0.001) -> bool:
        """
        Check if defense type is at soft cap (45%).

        Args:
            defense_type: Defense type to check
            tolerance: Floating-point comparison tolerance

        Returns:
            True if at or above soft cap
        """
        value = self.get_defense(defense_type)
        return value >= (DEFENSE_SOFT_CAP - tolerance)


def aggregate_defense_bonuses(
    defense_bonuses: List[Dict[DefenseType, float]],
    archetype: Optional[ArchetypeType] = None
) -> DefenseValues:
    """
    Aggregate multiple defense bonuses into final defense values.

    Defense bonuses stack additively with no diminishing returns.
    The soft cap (45%) is informational only - defense can exceed it.

    Args:
        defense_bonuses: List of defense bonus dicts (DefenseType -> value)
        archetype: Optional archetype for cap enforcement

    Returns:
        DefenseValues with aggregated bonuses

    Examples:
        >>> # Power grants +15% typed S/L defense
        >>> power_def = {DefenseType.SMASHING: 0.15, DefenseType.LETHAL: 0.15}
        >>> # IO bonus grants +5% positional melee defense
        >>> io_def = {DefenseType.MELEE: 0.05}
        >>> result = aggregate_defense_bonuses([power_def, io_def])
        >>> result.get_defense(DefenseType.SMASHING)
        0.15
        >>> result.get_defense(DefenseType.MELEE)
        0.05
    """
    result = DefenseValues.empty(archetype)

    # Sum all defense bonuses
    for bonus_dict in defense_bonuses:
        for defense_type, value in bonus_dict.items():
            result.add_defense(defense_type, value)

    # Apply archetype caps (display only)
    result.apply_caps()

    return result


def calculate_effective_defense(
    typed_defense: float,
    positional_defense: float
) -> float:
    """
    Calculate effective defense from typed and positional components.

    In City of Heroes, when an attack is made:
    - The attack has both a damage type AND a position (melee/ranged/aoe)
    - The game checks BOTH typed defense and positional defense
    - The HIGHER of the two is used

    This is the core "highest wins" mechanic.

    Args:
        typed_defense: Typed defense value (e.g., Smashing)
        positional_defense: Positional defense value (e.g., Melee)

    Returns:
        Effective defense value (higher of typed vs positional)

    Examples:
        >>> # Test 2 & 3 from plan: 30% typed, 40% positional → 40% applies
        >>> calculate_effective_defense(0.30, 0.40)
        0.40
        >>> # 45% typed, 20% positional → 45% applies
        >>> calculate_effective_defense(0.45, 0.20)
        0.45
    """
    return max(typed_defense, positional_defense)
