"""Healing calculations for powers that restore hit points."""
from dataclasses import dataclass
from typing import Optional

from app.calc.ed import apply_ed
from app.config.constants import ARCHETYPE_HEAL_MODIFIERS, HEAL_BASE_BY_LEVEL
from app.core.enums import Archetype


@dataclass
class HealOverTimeResult:
    """Result of heal over time calculation."""
    ticks: int
    heal_per_tick: float
    total_healing: float
    duration: float
    interval: float


def calc_base_heal(
    heal_scale: float,
    archetype: Archetype,
    level: int
) -> float:
    """
    Calculate base heal amount from heal scale.
    
    Args:
        heal_scale: The power's heal scale (e.g., 0.3 for 30%)
        archetype: The character's archetype
        level: The character's level (1-50)
        
    Returns:
        Base heal amount before enhancements
    """
    # Get base heal value for level
    # This represents the base heal at level 50 for a 1.0 scale
    base_heal_at_level = HEAL_BASE_BY_LEVEL.get(level, HEAL_BASE_BY_LEVEL[50])
    
    # Get archetype modifier
    archetype_name = archetype.value if hasattr(archetype, 'value') else str(archetype)
    archetype_modifier = ARCHETYPE_HEAL_MODIFIERS.get(
        archetype_name, 
        ARCHETYPE_HEAL_MODIFIERS["Defender"]
    )
    
    # Calculate final base heal
    return base_heal_at_level * heal_scale * archetype_modifier


def calc_final_healing(
    base_heal: float,
    heal_enhancement: float,
    global_heal_buff: float,
    archetype: Archetype
) -> float:
    """
    Calculate final healing amount with enhancements and buffs.
    
    Args:
        base_heal: Base heal amount
        heal_enhancement: Total heal enhancement percentage (0.95 = 95%)
        global_heal_buff: Global heal buffs from sets/powers (0.15 = 15%)
        archetype: Character archetype (for potential caps)
        
    Returns:
        Final heal amount after all modifiers
    """
    # Apply ED to heal enhancement (Schedule A)
    ed_enhancement = apply_ed('A', heal_enhancement)
    
    # Calculate total multiplier
    total_multiplier = 1 + ed_enhancement + global_heal_buff
    
    # Apply multiplier to base heal
    final_heal = base_heal * total_multiplier
    
    # Healing doesn't have caps like damage, but ensure non-negative
    return max(0.0, final_heal)


def calc_heal_over_time(
    heal_scale: float,
    duration: float,
    interval: float,
    archetype: Archetype,
    level: int,
    heal_enhancement: float = 0.0,
    global_heal_buff: float = 0.0
) -> HealOverTimeResult:
    """
    Calculate healing over time effects.
    
    Args:
        heal_scale: Heal scale per tick
        duration: Total duration in seconds
        interval: Time between heal ticks in seconds
        archetype: Character archetype
        level: Character level
        heal_enhancement: Heal enhancement percentage
        global_heal_buff: Global heal buffs
        
    Returns:
        HealOverTimeResult with tick information
    """
    # Calculate number of ticks
    ticks = int(duration / interval)
    
    # Calculate base heal per tick
    base_heal_per_tick = calc_base_heal(heal_scale, archetype, level)
    
    # Apply enhancements to get final heal per tick
    heal_per_tick = calc_final_healing(
        base_heal_per_tick,
        heal_enhancement,
        global_heal_buff,
        archetype
    )
    
    # Calculate total healing
    total_healing = heal_per_tick * ticks
    
    return HealOverTimeResult(
        ticks=ticks,
        heal_per_tick=heal_per_tick,
        total_healing=total_healing,
        duration=duration,
        interval=interval
    )