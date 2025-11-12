"""
Build Totals - Main aggregation class for all build statistics

Implements build-level total calculations for City of Heroes builds.
Maps to MidsReborn's clsToonX.cs BuildTotals functionality.

This class aggregates:
- Defense (typed + positional, "highest wins")
- Resistance (typed, additive stacking)
- Other stats (damage, recharge, accuracy, etc.) - to be added in future batches

Serves as the central calculation engine for a complete character build.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.calculations.core import ArchetypeType
from .defense_aggregator import (
    DefenseType,
    DefenseValues,
    aggregate_defense_bonuses,
    calculate_effective_defense
)
from .resistance_aggregator import (
    ResistanceType,
    ResistanceValues,
    aggregate_resistance_bonuses
)


@dataclass
class BuildTotals:
    """
    Complete build statistics aggregator.

    Aggregates all character build statistics including defense, resistance,
    damage, recharge, accuracy, and more.

    Attributes:
        archetype: Character archetype for cap enforcement
        defense: Aggregated defense values
        resistance: Aggregated resistance values
    """
    archetype: ArchetypeType
    defense: DefenseValues = field(default_factory=lambda: DefenseValues.empty())
    resistance: ResistanceValues = field(default_factory=lambda: ResistanceValues.empty())

    def __post_init__(self):
        """Initialize with archetype-specific empty values."""
        if self.defense.archetype is None:
            self.defense = DefenseValues.empty(self.archetype)
        if self.resistance.archetype is None:
            self.resistance = ResistanceValues.empty(self.archetype)

    def add_defense_bonuses(self, bonuses: List[Dict[DefenseType, float]]) -> None:
        """
        Add defense bonuses to build totals.

        Args:
            bonuses: List of defense bonus dicts
        """
        aggregated = aggregate_defense_bonuses(bonuses, self.archetype)
        # Merge into existing defense
        for defense_type in aggregated.typed.keys():
            self.defense.add_defense(defense_type, aggregated.typed[defense_type])
        for defense_type in aggregated.positional.keys():
            self.defense.add_defense(defense_type, aggregated.positional[defense_type])

    def add_resistance_bonuses(self, bonuses: List[Dict[ResistanceType, float]]) -> None:
        """
        Add resistance bonuses to build totals.

        Args:
            bonuses: List of resistance bonus dicts
        """
        aggregated = aggregate_resistance_bonuses(bonuses, self.archetype)
        # Merge into existing resistance
        for resistance_type in aggregated.values.keys():
            self.resistance.add_resistance(resistance_type, aggregated.values[resistance_type])

    def calculate_effective_defense_against(
        self,
        typed_defense: DefenseType,
        positional_defense: DefenseType
    ) -> float:
        """
        Calculate effective defense against a specific attack type.

        Uses the "highest wins" rule - takes the higher of typed vs positional.

        Args:
            typed_defense: The attack's damage type (e.g., SMASHING)
            positional_defense: The attack's delivery method (e.g., MELEE)

        Returns:
            Effective defense value (0.0-1.0)

        Examples:
            >>> # Against a melee smashing attack
            >>> totals.calculate_effective_defense_against(
            ...     DefenseType.SMASHING,
            ...     DefenseType.MELEE
            ... )
            0.40  # Whichever is higher
        """
        typed_val = self.defense.get_defense(typed_defense)
        positional_val = self.defense.get_defense(positional_defense)
        return calculate_effective_defense(typed_val, positional_val)

    def get_resistance_against(self, resistance_type: ResistanceType) -> float:
        """
        Get resistance against a specific damage type.

        Args:
            resistance_type: The damage type

        Returns:
            Resistance value (0.0-1.0)
        """
        return self.resistance.get_resistance(resistance_type)

    def apply_all_caps(self) -> None:
        """
        Apply all archetype-specific caps to build totals.

        This should be called after all bonuses have been added.
        """
        self.defense.apply_caps()
        self.resistance.apply_caps()

    def get_summary(self) -> Dict:
        """
        Get human-readable summary of build totals.

        Returns:
            Dict with formatted build statistics
        """
        return {
            "archetype": self.archetype.value,
            "defense": {
                "typed": {
                    dt.value: {
                        "value": self.defense.get_defense(dt),
                        "percentage": f"{self.defense.get_defense(dt) * 100:.2f}%",
                        "at_soft_cap": self.defense.is_at_soft_cap(dt)
                    }
                    for dt in [
                        DefenseType.SMASHING,
                        DefenseType.LETHAL,
                        DefenseType.FIRE,
                        DefenseType.COLD,
                        DefenseType.ENERGY,
                        DefenseType.NEGATIVE_ENERGY,
                        DefenseType.TOXIC,
                        DefenseType.PSIONIC
                    ]
                },
                "positional": {
                    dt.value: {
                        "value": self.defense.get_defense(dt),
                        "percentage": f"{self.defense.get_defense(dt) * 100:.2f}%",
                        "at_soft_cap": self.defense.is_at_soft_cap(dt)
                    }
                    for dt in [DefenseType.MELEE, DefenseType.RANGED, DefenseType.AOE]
                }
            },
            "resistance": {
                rt.value: {
                    "value": self.resistance.get_resistance(rt),
                    "percentage": f"{self.resistance.get_resistance(rt) * 100:.2f}%",
                    "at_cap": self.resistance.is_at_cap(rt)
                }
                for rt in [
                    ResistanceType.SMASHING,
                    ResistanceType.LETHAL,
                    ResistanceType.FIRE,
                    ResistanceType.COLD,
                    ResistanceType.ENERGY,
                    ResistanceType.NEGATIVE_ENERGY,
                    ResistanceType.TOXIC,
                    ResistanceType.PSIONIC
                ]
            }
        }


def create_build_totals(archetype: ArchetypeType) -> BuildTotals:
    """
    Factory function to create a BuildTotals instance.

    Args:
        archetype: Character archetype

    Returns:
        BuildTotals instance initialized for the archetype

    Examples:
        >>> from app.calculations.core import ArchetypeType
        >>> totals = create_build_totals(ArchetypeType.SCRAPPER)
        >>> totals.archetype
        <ArchetypeType.SCRAPPER: 'Scrapper'>
    """
    return BuildTotals(archetype=archetype)
