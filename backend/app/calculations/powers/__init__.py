"""
Power Calculations Module

Implements power-level calculations for damage, buffs, debuffs, control,
healing, endurance, and accuracy based on MidsReborn specifications.

Submodules:
    damage_calculator: Power damage calculation (Spec 02)
    buff_calculator: Buff/debuff calculation (Spec 03)
"""

from .buff_calculator import (
    AspectType,
    BuffDebuffCalculator,
    BuffDebuffEffect,
    BuffDebuffType,
    StackingMode,
    format_buff_display,
)
from .damage_calculator import (
    DamageCalculator,
    DamageMathMode,
    DamageReturnMode,
    DamageSummary,
    DamageType,
    DamageValue,
    PowerType,
)

__all__ = [
    # Damage calculator
    "DamageCalculator",
    "DamageMathMode",
    "DamageReturnMode",
    "DamageSummary",
    "DamageType",
    "DamageValue",
    "PowerType",
    # Buff/debuff calculator
    "AspectType",
    "BuffDebuffCalculator",
    "BuffDebuffEffect",
    "BuffDebuffType",
    "StackingMode",
    "format_buff_display",
]
