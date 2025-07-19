"""Endurance calculation module.

Implements endurance cost calculations including enhancement effects
and global buffs.
"""

from app.calc.ed import apply_ed
from app.config.constants import GLOBAL_CAPS


def calc_end_cost(
    base_cost: float,
    endurance_reduction: float,
    global_endurance_reduction: float = 0.0,
) -> float:
    """Calculate final endurance cost after reductions.

    Formula: Final = Base / (1 + ED(EndRdxEnh) + Buff%)
    With hard floor at 0.10 × Base (cannot free-cast)

    Args:
        base_cost: Base endurance cost of the power
        endurance_reduction: Total endurance reduction enhancement % (before ED)
        global_endurance_reduction: Global endurance reduction from set bonuses

    Returns:
        Final endurance cost after all reductions
    """
    # Apply ED to endurance reduction
    ed_endurance = apply_ed("A", endurance_reduction)
    
    # Calculate total reduction
    total_reduction = 1.0 + ed_endurance + global_endurance_reduction
    
    # Calculate final cost
    final_cost = base_cost / total_reduction
    
    # Apply minimum cost floor (10% of base)
    min_cost = base_cost * GLOBAL_CAPS["endurance_min_cost_factor"]
    if final_cost < min_cost:
        final_cost = min_cost
    
    return final_cost


def calc_endurance_per_second(
    endurance_cost: float,
    recharge_time: float,
    activation_time: float,
) -> float:
    """Calculate endurance cost per second (EPS).

    This is useful for comparing power efficiency.

    Args:
        endurance_cost: Endurance cost per activation
        recharge_time: Recharge time in seconds
        activation_time: Activation/cast time in seconds

    Returns:
        Endurance cost per second
    """
    # Total cycle time is recharge + activation
    cycle_time = recharge_time + activation_time
    
    # Avoid division by zero
    if cycle_time <= 0:
        return 0.0
    
    return endurance_cost / cycle_time


def calc_toggle_endurance(
    base_cost: float,
    endurance_reduction: float,
    tick_rate: float = 0.5,
) -> float:
    """Calculate endurance cost for toggle powers.

    Toggle powers typically drain endurance every tick (usually 0.5 seconds).

    Args:
        base_cost: Base endurance cost per tick
        endurance_reduction: Total endurance reduction enhancement %
        tick_rate: How often the toggle drains endurance (seconds)

    Returns:
        Endurance cost per second for the toggle
    """
    # Calculate cost per tick
    cost_per_tick = calc_end_cost(base_cost, endurance_reduction)
    
    # Convert to cost per second
    if tick_rate > 0:
        return cost_per_tick / tick_rate
    
    return cost_per_tick


def calc_endurance_recovery(
    base_recovery: float = 1.67,
    recovery_bonus: float = 0.0,
    max_endurance: float = 100.0,
) -> float:
    """Calculate endurance recovery rate.

    Args:
        base_recovery: Base recovery rate (default 1.67/sec)
        recovery_bonus: Total recovery bonus %
        max_endurance: Maximum endurance (affected by accolades)

    Returns:
        Endurance recovered per second
    """
    # Apply recovery bonus
    total_recovery = base_recovery * (1.0 + recovery_bonus)
    
    # Recovery is based on max endurance
    # Base recovery is 1.67% of max end per second
    recovery_rate = (total_recovery / 100.0) * max_endurance
    
    return recovery_rate


def calc_net_endurance(
    recovery_rate: float,
    toggle_costs: list[float],
    active_power_eps: float = 0.0,
) -> float:
    """Calculate net endurance gain/loss per second.

    Args:
        recovery_rate: Endurance recovery per second
        toggle_costs: List of endurance costs per second for active toggles
        active_power_eps: Average endurance per second from active powers

    Returns:
        Net endurance per second (positive = gaining, negative = losing)
    """
    total_drain = sum(toggle_costs) + active_power_eps
    return recovery_rate - total_drain


def can_sustain_toggles(
    recovery_rate: float,
    toggle_costs: list[float],
    safety_margin: float = 0.2,
) -> bool:
    """Check if current recovery can sustain toggle powers.

    Args:
        recovery_rate: Endurance recovery per second
        toggle_costs: List of endurance costs per second for toggles
        safety_margin: Required excess recovery (default 20%)

    Returns:
        True if toggles can be sustained with safety margin
    """
    total_toggle_cost = sum(toggle_costs)
    required_recovery = total_toggle_cost * (1.0 + safety_margin)
    
    return recovery_rate >= required_recovery