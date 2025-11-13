"""
Enhancement System - Slotting and Set Bonuses

Implements Phase 4 - Batch 4A of the calculation engine:
- Spec 11: Enhancement Slotting (max 6 slots, attuned, catalyzed, boosted)
- Spec 13: Set Bonuses (Rule of 5, PvE/PvP modes)
"""

from .set_bonuses import (
    BonusItem,
    EnhancementSet,
    PvMode,
    SetBonusCalculator,
    SlottedSet,
)
from .slotting import (
    EnhancementGrade,
    EnhancementType,
    RelativeLevel,
    Slot,
    SlotEntry,
    SlottedPower,
    SlottingCalculator,
)

__all__ = [
    # Slotting
    "Slot",
    "SlotEntry",
    "SlottedPower",
    "SlottingCalculator",
    "EnhancementGrade",
    "EnhancementType",
    "RelativeLevel",
    # Set Bonuses
    "BonusItem",
    "EnhancementSet",
    "SlottedSet",
    "SetBonusCalculator",
    "PvMode",
]
