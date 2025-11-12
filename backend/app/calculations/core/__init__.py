"""
Core calculation components - Effect system, enums, and aggregation.
"""

from . import constants
from .archetype_caps import (
    ArchetypeCaps,
    ArchetypeType,
    apply_cap,
    get_archetype_caps,
    is_at_cap,
)
from .archetype_modifiers import (
    ArchetypeModifiers,
    ModifierTable,
    calculate_effect_magnitude,
)
from .effect import Effect
from .effect_types import DamageType, EffectType, MezType
from .enhancement_schedules import EDSchedule, apply_ed, calculate_ed_loss, get_schedule
from .enums import PvMode, SpecialCase, Stacking, Suppress, ToWho
from .grouped_fx import EffectAggregator, FxId, GroupedEffect

__all__ = [
    # Effect types
    "EffectType",
    "DamageType",
    "MezType",
    # Enums
    "ToWho",
    "PvMode",
    "Stacking",
    "SpecialCase",
    "Suppress",
    # Core classes
    "Effect",
    "FxId",
    "GroupedEffect",
    "EffectAggregator",
    # Enhancement Diversification
    "EDSchedule",
    "apply_ed",
    "get_schedule",
    "calculate_ed_loss",
    # Archetype Modifiers
    "ModifierTable",
    "ArchetypeModifiers",
    "calculate_effect_magnitude",
    # Archetype Caps
    "ArchetypeType",
    "ArchetypeCaps",
    "get_archetype_caps",
    "apply_cap",
    "is_at_cap",
    # Constants module
    "constants",
]
