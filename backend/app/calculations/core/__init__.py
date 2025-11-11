"""
Core calculation components - Effect system, enums, and aggregation.
"""

from .effect_types import EffectType, DamageType, MezType
from .enums import ToWho, PvMode, Stacking, SpecialCase, Suppress
from .effect import Effect
from .grouped_fx import FxId, GroupedEffect, EffectAggregator

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
]
