"""
Core calculation components - Effect system, enums, and aggregation.
"""

from .effect_types import EffectType, DamageType, MezType
from .enums import ToWho, PvMode, Stacking, SpecialCase, Suppress
from .effect import Effect
from .grouped_fx import FxId, GroupedEffect, EffectAggregator
from .enhancement_schedules import EDSchedule, apply_ed, get_schedule, calculate_ed_loss
from .archetype_modifiers import (
    ModifierTable,
    ArchetypeModifiers,
    calculate_effect_magnitude
)
from .archetype_caps import (
    ArchetypeType,
    ArchetypeCaps,
    get_archetype_caps,
    apply_cap,
    is_at_cap
)
from . import constants

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
