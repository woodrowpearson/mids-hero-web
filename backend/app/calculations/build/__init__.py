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
from .recharge_aggregator import (
    RechargeValues,
    aggregate_recharge_bonuses,
    calculate_recharge_time,
    RECHARGE_CAP
)
from .damage_aggregator import (
    DamageValues,
    DamageHeuristic,
    DamageBuffSource,
    aggregate_damage_buffs,
    calculate_damage_with_buff
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
    # Recharge
    "RechargeValues",
    "aggregate_recharge_bonuses",
    "calculate_recharge_time",
    "RECHARGE_CAP",
    # Damage
    "DamageValues",
    "DamageHeuristic",
    "DamageBuffSource",
    "aggregate_damage_buffs",
    "calculate_damage_with_buff",
    # Build Totals
    "BuildTotals",
    "create_build_totals",
]
