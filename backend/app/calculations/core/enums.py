"""
Supporting Enumerations for Effect System

Maps to MidsReborn's Enums.cs - ToWho, PvMode, Stacking, SpecialCase, etc.
"""

from enum import Enum


class ToWho(Enum):
    """
    Effect target designation.

    Maps to MidsReborn's Enums.eToWho enum.
    """

    TARGET = 0
    SELF = 1
    TEAM = 2
    AREA = 3
    UNSPECIFIED = 4


class PvMode(Enum):
    """
    PvE vs PvP context for effects.

    Maps to MidsReborn's Enums.ePvX enum.
    Effects can have different magnitudes in PvE vs PvP.
    """

    ANY = 0
    PVE = 1
    PVP = 2


class Stacking(Enum):
    """
    Stacking behavior for effects.

    Maps to MidsReborn's Enums.eStacking enum.

    NO: Effect does not stack - first instance only
    YES: Effect stacks additively (most common)
    STACK: Effect stacks (same as YES)
    REPLACE: New instance replaces old value
    """

    NO = 0
    YES = 1
    STACK = 2
    REPLACE = 3


class SpecialCase(Enum):
    """
    Special mechanics tied to archetype inherents.

    Maps to MidsReborn's Enums.eSpecialCase enum.
    """

    NONE = 0
    DEFIANCE = 1  # Blaster inherent
    DOMINATION = 2  # Dominator inherent
    SCOURGE = 3  # Corruptor inherent
    FURY = 4  # Brute inherent
    ASSASSINATION = 5  # Stalker inherent


class Suppress(Enum):
    """
    Suppression rules for effects.

    Maps to MidsReborn's Enums.eSuppress enum.
    Some effects are suppressed in combat or when other powers activate.
    """

    NONE = 0
    COMBAT = 1  # Suppressed when in combat
    MOVEMENT = 2  # Suppressed when moving
    HELD = 3  # Suppressed when held
    STUNNED = 4  # Suppressed when stunned
    SLEEP = 5  # Suppressed when sleeping
    IMMOBILIZE = 6  # Suppressed when immobilized
