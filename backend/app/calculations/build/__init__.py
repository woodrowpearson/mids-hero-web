"""
Build-level calculations - Aggregation of all character statistics
"""

from .defense_aggregator import (
    DefenseType,
    DefenseValues,
    aggregate_defense_bonuses,
    calculate_effective_defense,
    DEFENSE_SOFT_CAP
)
from .resistance_aggregator import (
    ResistanceType,
    ResistanceValues,
    aggregate_resistance_bonuses,
    calculate_damage_reduction
)
from .build_totals import (
    BuildTotals,
    create_build_totals
)

__all__ = [
    # Defense
    "DefenseType",
    "DefenseValues",
    "aggregate_defense_bonuses",
    "calculate_effective_defense",
    "DEFENSE_SOFT_CAP",
    # Resistance
    "ResistanceType",
    "ResistanceValues",
    "aggregate_resistance_bonuses",
    "calculate_damage_reduction",
    # Build Totals
    "BuildTotals",
    "create_build_totals",
]
