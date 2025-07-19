"""Enhancement Diversification (ED) calculations.

This module implements the Enhancement Diversification system from City of Heroes,
which applies diminishing returns to enhancement values.
"""

from typing import Dict, List

from app.config.constants import ED_SCHEDULES


def apply_ed(schedule: str, enhancement_value: float) -> float:
    """Apply Enhancement Diversification to an enhancement value.

    ED applies diminishing returns to enhancement values using a piecewise
    linear function with different reduction rates at different thresholds.

    Args:
        schedule: The ED schedule to use ('A', 'B', or 'C')
        enhancement_value: The total enhancement value before ED (as a decimal)

    Returns:
        The enhancement value after ED is applied

    Raises:
        ValueError: If the schedule is not recognized

    Examples:
        >>> apply_ed('A', 0.95)  # 95% enhancement
        0.95
        >>> apply_ed('A', 2.0)   # 200% enhancement
        1.835
    """
    # Negative values (debuffs) are not affected by ED
    if enhancement_value < 0:
        return enhancement_value

    # Get the schedule data
    if schedule not in ED_SCHEDULES:
        raise ValueError(f"Unknown ED schedule: {schedule}")

    schedule_data = ED_SCHEDULES[schedule]
    thresholds = schedule_data["thresholds"]
    multipliers = schedule_data["multipliers"]

    # Apply piecewise calculation
    total = 0.0
    remaining = enhancement_value

    for i in range(len(thresholds) - 1):
        # Calculate how much of this segment to use
        segment_start = thresholds[i]
        segment_end = thresholds[i + 1]
        segment_size = segment_end - segment_start
        
        # How much of the remaining value fits in this segment
        segment_amount = min(remaining, segment_size)
        
        # Apply the multiplier for this segment
        total += segment_amount * multipliers[i]
        
        # Reduce remaining by what we used
        remaining -= segment_amount
        
        # If we've used everything, we're done
        if remaining <= 0:
            break

    # If there's still value remaining, it goes in the final segment
    if remaining > 0:
        total += remaining * multipliers[-1]

    return total


def get_ed_schedule_for_type(enhancement_type: str) -> str:
    """Get the ED schedule letter for a given enhancement type.

    Args:
        enhancement_type: The type of enhancement (damage, accuracy, etc.)

    Returns:
        The schedule letter ('A', 'B', or 'C')
    """
    from app.config.constants import ED_SCHEDULE_TYPES
    
    return ED_SCHEDULE_TYPES.get(enhancement_type.lower(), "A")


def calculate_ed_for_enhancement_set(
    enhancements: Dict[str, float], 
    enhancement_types: Dict[str, str]
) -> Dict[str, float]:
    """Calculate ED for a set of enhancements.

    Args:
        enhancements: Dict mapping enhancement type to total value
        enhancement_types: Dict mapping enhancement type to ED schedule

    Returns:
        Dict mapping enhancement type to post-ED value
    """
    result = {}
    
    for enh_type, value in enhancements.items():
        schedule = enhancement_types.get(enh_type, "A")
        result[enh_type] = apply_ed(schedule, value)
    
    return result