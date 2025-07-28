"""Recharge calculation module.

Implements recharge time calculations including enhancement effects,
global recharge bonuses, and caps.
"""

from app.calc.ed import apply_ed
from app.config.constants import GLOBAL_CAPS, POWER_MINIMUMS


def calc_recharge(
    base_recharge: float,
    recharge_enhancement: float,
    global_recharge: float = 0.0,
) -> float:
    """Calculate final recharge time after all bonuses.

    Formula: Final = Base / (1 + ED(RechEnh) + Buff%)
    Cap at +500% haste (recharge_cap)

    Args:
        base_recharge: Base recharge time in seconds
        recharge_enhancement: Total recharge enhancement % (before ED)
        global_recharge: Global recharge bonus % from set bonuses, Hasten, etc.

    Returns:
        Final recharge time in seconds
    """
    # Apply ED to recharge enhancement
    ed_recharge = apply_ed("A", recharge_enhancement)

    # Calculate total recharge bonus
    total_recharge_bonus = ed_recharge + global_recharge

    # Apply recharge cap (+500% = 5.0)
    recharge_cap = GLOBAL_CAPS["recharge_cap"]
    if total_recharge_bonus > recharge_cap:
        total_recharge_bonus = recharge_cap

    # Calculate final recharge time
    final_recharge = base_recharge / (1.0 + total_recharge_bonus)

    # Apply minimum recharge time
    min_recharge = POWER_MINIMUMS["recharge_time"]
    if final_recharge < min_recharge:
        final_recharge = min_recharge

    return final_recharge


def calc_chain_time(
    powers: list[dict],
    global_recharge: float = 0.0,
) -> dict:
    """Calculate timing for a power chain/rotation.

    Args:
        powers: List of power dicts with base_recharge, recharge_enhancement, activation_time
        global_recharge: Global recharge bonus %

    Returns:
        Dict with chain timing information
    """
    total_animation = 0.0
    max_recharge = 0.0
    chain_powers = []

    for power in powers:
        # Calculate enhanced recharge
        final_recharge = calc_recharge(
            power.get("base_recharge", 0.0),
            power.get("recharge_enhancement", 0.0),
            global_recharge,
        )

        # Track animation time
        activation = power.get("activation_time", 0.0)
        total_animation += activation

        # Track longest recharge
        if final_recharge > max_recharge:
            max_recharge = final_recharge

        chain_powers.append({
            "name": power.get("name", "Unknown"),
            "recharge": final_recharge,
            "activation": activation,
        })

    # Chain can repeat when longest recharge is ready
    chain_gap = max(0.0, max_recharge - total_animation)

    return {
        "powers": chain_powers,
        "total_animation": total_animation,
        "limiting_recharge": max_recharge,
        "gap_time": chain_gap,
        "seamless": chain_gap <= 0.0,
    }


def calc_perma_status(
    duration: float,
    recharge: float,
) -> dict:
    """Calculate whether a power can be made permanent.

    Args:
        duration: Power effect duration in seconds
        recharge: Power recharge time in seconds

    Returns:
        Dict with perma status information
    """
    # Power is perma if duration >= recharge
    is_perma = duration >= recharge

    # Calculate overlap or gap
    if is_perma:
        overlap = duration - recharge
        uptime_percent = 100.0
    else:
        overlap = 0.0
        uptime_percent = (duration / recharge) * 100.0 if recharge > 0 else 0.0

    # Calculate how much more recharge is needed for perma
    if not is_perma and duration > 0:
        # recharge_needed = base / (1 + bonus) = duration
        # base / duration = 1 + bonus
        # bonus = (base / duration) - 1
        current_bonus = (recharge / duration) - 1.0 if recharge > duration else 0.0
        needed_bonus = 0.0  # Already perma
    else:
        current_bonus = 0.0
        needed_bonus = 0.0

    return {
        "is_perma": is_perma,
        "uptime_percent": min(100.0, uptime_percent),
        "overlap_seconds": overlap,
        "gap_seconds": max(0.0, recharge - duration),
        "additional_recharge_needed": max(0.0, needed_bonus - current_bonus),
    }


def calc_activation_time(
    base_activation: float,
    animation_bonus: float = 0.0,
) -> float:
    """Calculate power activation/animation time.

    Note: Most powers don't have their activation time affected by enhancements,
    but some special cases exist.

    Args:
        base_activation: Base activation time in seconds
        animation_bonus: Any animation time reduction (rare)

    Returns:
        Final activation time in seconds
    """
    # Apply animation bonus (if any)
    final_activation = base_activation * (1.0 - animation_bonus)

    # Apply minimum activation time (arcanatime minimum)
    min_activation = POWER_MINIMUMS.get("activation_time", 0.132)
    if final_activation < min_activation:
        final_activation = min_activation

    return final_activation


def calc_dps_with_recharge(
    damage: float,
    recharge_time: float,
    activation_time: float,
) -> float:
    """Calculate damage per second accounting for recharge.

    Args:
        damage: Total damage dealt
        recharge_time: Recharge time in seconds
        activation_time: Activation time in seconds

    Returns:
        Damage per second
    """
    # Total cycle time
    cycle_time = recharge_time + activation_time

    # Avoid division by zero
    if cycle_time <= 0:
        return 0.0

    return damage / cycle_time
