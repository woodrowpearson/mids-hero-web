"""Damage calculation module.

Implements damage calculations including enhancement effects,
global buffs, and archetype caps.
"""


from app.calc.ed import apply_ed
from app.config.constants import PVP_MODIFIERS, get_archetype_cap
from app.core.enums import BuffMode, DamageType


def calc_final_damage(
    base_damage: float,
    damage_enhancement: float,
    global_damage_buff: float,
    archetype: str,
    damage_type: DamageType | None = None,  # noqa: ARG001
    is_pvp: bool = False,
    buff_mode: BuffMode = BuffMode.NORMAL,  # noqa: ARG001
) -> float:
    """Calculate final damage after all modifiers.

    Formula: Final = Base × (1 + ED(DmgEnh) + Buff%)
    Args:
        base_damage: Base damage value from power
        damage_enhancement: Total damage enhancement % (before ED)
        global_damage_buff: Global damage buff % from set bonuses, etc.
        archetype: Character archetype name
        damage_type: Type of damage (optional, for future resistance calcs)
        is_pvp: Whether this is PvP combat
        buff_mode: Whether calculating buff or debuff values

    Returns:
        Final damage value after all calculations
    """
    # Apply ED to damage enhancement
    ed_damage = apply_ed("A", damage_enhancement)

    # Calculate total damage multiplier
    total_multiplier = 1.0 + ed_damage + global_damage_buff

    # Apply archetype damage cap
    damage_cap = get_archetype_cap(archetype, "damage_cap")
    if total_multiplier > damage_cap:
        total_multiplier = damage_cap

    # Calculate final damage
    final_damage = base_damage * total_multiplier

    # Apply PvP modifier if applicable
    if is_pvp:
        final_damage *= PVP_MODIFIERS["damage_modifier"]

    return final_damage


def calc_damage_with_resistance(
    damage: float,
    target_resistance: float,
    damage_type: DamageType,  # noqa: ARG001
    is_pvp: bool = False,  # noqa: ARG001
) -> float:
    """Calculate damage after target resistance.

    Args:
        damage: Incoming damage amount
        target_resistance: Target's resistance % for this damage type
        damage_type: Type of damage being dealt
        is_pvp: Whether this is PvP combat

    Returns:
        Damage after resistance is applied
    """
    # Resistance is capped at 90% for most ATs, 95% in some cases
    # Negative resistance (vulnerability) can increase damage
    resistance_factor = 1.0 - (target_resistance / 100.0)

    # Ensure minimum damage (5% gets through at 95% resistance)
    if resistance_factor < 0.05:
        resistance_factor = 0.05

    # Negative resistance can increase damage up to 300%
    if resistance_factor > 3.0:
        resistance_factor = 3.0

    return damage * resistance_factor


def calc_critical_damage(
    base_damage: float,
    critical_chance: float,
    critical_severity: float = 1.0,
    archetype: str = "",
) -> dict[str, float]:
    """Calculate critical hit damage.

    Args:
        base_damage: Base damage amount
        critical_chance: Chance to critical (0.0 to 1.0)
        critical_severity: Critical damage multiplier (default 1.0 = +100%)
        archetype: Character archetype (for special critical rules)

    Returns:
        Dict with 'average' damage and 'critical' damage
    """
    # Scrappers have inherent critical chance
    if archetype == "Scrapper":
        if critical_chance < 0.05:
            critical_chance = 0.05  # Base 5% critical

    # Stalkers have different critical mechanics
    elif archetype == "Stalker":
        # Stalkers have guaranteed criticals from hide
        # This is simplified - actual mechanics are more complex
        pass

    critical_damage = base_damage * (1.0 + critical_severity)
    average_damage = base_damage * (1.0 - critical_chance) + critical_damage * critical_chance

    return {
        "average": average_damage,
        "critical": critical_damage,
        "chance": critical_chance,
    }


def calc_damage_scale_to_damage(
    damage_scale: float,
    archetype: str,
    level: int,
    power_type: str = "ranged",
) -> float:
    """Convert damage scale to actual damage value.

    Args:
        damage_scale: Damage scale value from power data
        archetype: Character archetype
        level: Character level
        power_type: Type of power (melee, ranged, etc.)

    Returns:
        Base damage value
    """
    # Simplified damage tables - actual game uses complex tables
    # These are approximate values for level 50
    archetype_modifiers = {
        "Blaster": {"melee": 1.125, "ranged": 1.125},
        "Controller": {"melee": 0.550, "ranged": 0.550},
        "Defender": {"melee": 0.550, "ranged": 0.650},
        "Scrapper": {"melee": 1.125, "ranged": 0.500},
        "Tanker": {"melee": 0.800, "ranged": 0.500},
        "Brute": {"melee": 0.750, "ranged": 0.500},
        "Stalker": {"melee": 1.000, "ranged": 0.600},
        "Mastermind": {"melee": 0.550, "ranged": 0.550},
        "Dominator": {"melee": 1.050, "ranged": 0.950},
        "Corruptor": {"melee": 0.750, "ranged": 0.750},
        "Sentinel": {"melee": 0.950, "ranged": 0.950},
    }

    # Get archetype modifier
    at_mods = archetype_modifiers.get(archetype, {"melee": 1.0, "ranged": 1.0})
    modifier = at_mods.get(power_type, 1.0)

    # Base damage at level 50 is approximately 55.61
    base_damage_50 = 55.61

    # Simple level scaling (actual game uses complex tables)
    level_modifier = level / 50.0

    return damage_scale * base_damage_50 * modifier * level_modifier
