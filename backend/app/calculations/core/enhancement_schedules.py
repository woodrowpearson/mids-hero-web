"""
Enhancement Diversification (ED) Schedules

Implements the four ED curves that apply diminishing returns to enhancements.
Maps to MidsReborn's Enhancement.cs ApplyED() function.

ED was introduced in Issue 5 (September 2005) to prevent "six-slotting" and
force build diversification.
"""

from enum import Enum
from typing import Optional, Tuple

from .constants import (
    ED_SCHEDULE_A_THRESH_1, ED_SCHEDULE_A_THRESH_2, ED_SCHEDULE_A_THRESH_3,
    ED_SCHEDULE_B_THRESH_1, ED_SCHEDULE_B_THRESH_2, ED_SCHEDULE_B_THRESH_3,
    ED_SCHEDULE_C_THRESH_1, ED_SCHEDULE_C_THRESH_2, ED_SCHEDULE_C_THRESH_3,
    ED_SCHEDULE_D_THRESH_1, ED_SCHEDULE_D_THRESH_2, ED_SCHEDULE_D_THRESH_3,
    ED_EFFICIENCY_REGION_1, ED_EFFICIENCY_REGION_2,
    ED_EFFICIENCY_REGION_3, ED_EFFICIENCY_REGION_4
)


class EDSchedule(Enum):
    """
    Enhancement Diversification schedules.

    Maps to MidsReborn's Enums.eSchedule enum.
    Each attribute type uses one of four ED curves.
    """
    NONE = -1  # No ED applied
    A = 0  # Standard: Damage, Accuracy, Recharge, Heal, etc.
    B = 1  # Defensive: Defense, Resistance, ToHit, Range (most aggressive)
    C = 2  # Interrupt: Interrupt time reduction only (lenient)
    D = 3  # Special Mez: Afraid and Confused only (very lenient)
    MULTIPLE = 4  # Enhancement affects multiple schedules


# ED threshold data from Maths.mhd
# Tuple format: (threshold_1, threshold_2, threshold_3)
ED_THRESHOLDS = {
    EDSchedule.A: (ED_SCHEDULE_A_THRESH_1, ED_SCHEDULE_A_THRESH_2, ED_SCHEDULE_A_THRESH_3),
    EDSchedule.B: (ED_SCHEDULE_B_THRESH_1, ED_SCHEDULE_B_THRESH_2, ED_SCHEDULE_B_THRESH_3),
    EDSchedule.C: (ED_SCHEDULE_C_THRESH_1, ED_SCHEDULE_C_THRESH_2, ED_SCHEDULE_C_THRESH_3),
    EDSchedule.D: (ED_SCHEDULE_D_THRESH_1, ED_SCHEDULE_D_THRESH_2, ED_SCHEDULE_D_THRESH_3),
}


def apply_ed(schedule: EDSchedule, value: float) -> float:
    """
    Apply Enhancement Diversification to an enhancement value.

    Implements MidsReborn's Enhancement.cs ApplyED() function with exact logic.

    ED uses a piecewise linear function with four regions:
    - Region 1 (below thresh1): 100% efficiency (no ED)
    - Region 2 (thresh1 to thresh2): 90% efficiency (light ED)
    - Region 3 (thresh2 to thresh3): 70% efficiency (medium ED)
    - Region 4 (above thresh3): 15% efficiency (heavy ED)

    Args:
        schedule: Which ED curve to use (A/B/C/D)
        value: Total enhancement value (e.g., 0.999 for three SOs)

    Returns:
        Enhancement value after ED diminishing returns

    Examples:
        >>> apply_ed(EDSchedule.A, 1.0)  # Three SOs in damage
        0.95
        >>> apply_ed(EDSchedule.B, 1.0)  # Three SOs in defense
        0.62
        >>> apply_ed(EDSchedule.A, 2.0)  # Six SOs in damage
        1.10
    """
    if schedule in (EDSchedule.NONE, EDSchedule.MULTIPLE):
        return 0.0

    if schedule not in ED_THRESHOLDS:
        raise ValueError(f"Invalid ED schedule: {schedule}")

    thresh1, thresh2, thresh3 = ED_THRESHOLDS[schedule]

    # Region 1: Below first threshold - no ED (100% efficiency)
    if value <= thresh1:
        return value

    # Pre-calculate cumulative ED values at each threshold
    # This matches MidsReborn's approach for efficiency
    edm1 = thresh1  # Value at end of Region 1
    edm2 = thresh1 + (thresh2 - thresh1) * ED_EFFICIENCY_REGION_2  # End of Region 2
    edm3 = edm2 + (thresh3 - thresh2) * ED_EFFICIENCY_REGION_3  # End of Region 3

    # Region 2: Light ED (90% efficiency)
    if value <= thresh2:
        return edm1 + (value - thresh1) * ED_EFFICIENCY_REGION_2

    # Region 3: Medium ED (70% efficiency)
    if value <= thresh3:
        return edm2 + (value - thresh2) * ED_EFFICIENCY_REGION_3

    # Region 4: Heavy ED (15% efficiency)
    return edm3 + (value - thresh3) * ED_EFFICIENCY_REGION_4


def get_schedule(enhance_type: str, enhance_subtype: Optional[int] = None) -> EDSchedule:
    """
    Determine which ED schedule applies to an enhancement type.

    Maps to MidsReborn's Enhancement.cs GetSchedule() function.

    Args:
        enhance_type: Enhancement attribute (e.g., "Damage", "Defense")
        enhance_subtype: For Mez, the mez type (4=Afraid, 5=Confused)

    Returns:
        EDSchedule enum value

    Examples:
        >>> get_schedule("Damage")
        EDSchedule.A
        >>> get_schedule("Defense")
        EDSchedule.B
        >>> get_schedule("Mez", 4)  # Afraid
        EDSchedule.D
        >>> get_schedule("Mez", 1)  # Hold
        EDSchedule.A
    """
    # Schedule B - Defensive attributes (most aggressive ED)
    if enhance_type == "Defense":
        return EDSchedule.B

    # Schedule C - Interrupt time (lenient ED)
    if enhance_type == "Interrupt":
        return EDSchedule.C

    # Schedule D - Special mez types only (very lenient)
    if enhance_type == "Mez":
        # Mez subtypes: 0=Sleep, 1=Hold, 2=Stun, 3=Immobilize,
        #                4=Afraid, 5=Confused
        # Only Afraid (4) and Confused (5) use Schedule D
        if enhance_subtype in (4, 5):
            return EDSchedule.D
        # All other mez types use Schedule A
        return EDSchedule.A

    # Schedule B - Other defensive attributes
    if enhance_type in ("Range", "Resistance", "ToHit"):
        return EDSchedule.B

    # Schedule A - Default for all other attributes
    # Includes: Damage, Accuracy, Recharge, Heal, Endurance Mod,
    #           Recovery, Regeneration, Hit Points, Speed, Slow, Absorb, etc.
    return EDSchedule.A


def calculate_ed_loss(schedule: EDSchedule, value: float) -> Tuple[float, float, float]:
    """
    Calculate how much enhancement value is lost to ED.

    Args:
        schedule: ED schedule to apply
        value: Pre-ED enhancement value

    Returns:
        Tuple of (post_ed_value, pre_ed_value, percent_lost)

    Examples:
        >>> calculate_ed_loss(EDSchedule.A, 2.0)
        (1.10, 2.0, 45.0)  # Six-slotting loses 45%!
        >>> calculate_ed_loss(EDSchedule.B, 1.0)
        (0.62, 1.0, 38.0)  # Defense loses 38% at 100%
    """
    post_ed = apply_ed(schedule, value)
    loss = value - post_ed
    percent_lost = (loss / value * 100.0) if value > 0 else 0.0
    return post_ed, value, percent_lost


def get_ed_region(schedule: EDSchedule, value: float) -> int:
    """
    Determine which ED region a value falls into.

    Args:
        schedule: ED schedule
        value: Enhancement value

    Returns:
        Region number (1-4):
        - 1: No ED (100% efficiency)
        - 2: Light ED (90% efficiency)
        - 3: Medium ED (70% efficiency)
        - 4: Heavy ED (15% efficiency)
    """
    if schedule not in ED_THRESHOLDS:
        return 1

    thresh1, thresh2, thresh3 = ED_THRESHOLDS[schedule]

    if value <= thresh1:
        return 1
    elif value <= thresh2:
        return 2
    elif value <= thresh3:
        return 3
    else:
        return 4


def get_ed_efficiency(schedule: EDSchedule, value: float) -> float:
    """
    Get the efficiency multiplier at a given enhancement value.

    Args:
        schedule: ED schedule
        value: Enhancement value

    Returns:
        Efficiency multiplier (1.0, 0.90, 0.70, or 0.15)
    """
    region = get_ed_region(schedule, value)

    if region == 1:
        return ED_EFFICIENCY_REGION_1
    elif region == 2:
        return ED_EFFICIENCY_REGION_2
    elif region == 3:
        return ED_EFFICIENCY_REGION_3
    else:  # region == 4
        return ED_EFFICIENCY_REGION_4
