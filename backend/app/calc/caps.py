"""Archetype cap enforcement module.

Implements cap enforcement for various stats based on archetype limits.
"""


from app.config.constants import ARCHETYPE_CAPS, GLOBAL_CAPS


class CapError(Exception):
    """Raised when an unknown stat type is provided for capping."""
    pass


def apply_archetype_caps(
    stats: dict[str, float],
    archetype: str,
) -> dict[str, float]:
    """Apply archetype-specific caps to stats.

    Args:
        stats: Dictionary of stat names to values
        archetype: Character archetype name

    Returns:
        Dictionary with capped values

    Raises:
        CapError: If an unknown stat type is provided
    """
    # Get archetype cap data
    at_caps = ARCHETYPE_CAPS.get(archetype)
    if not at_caps:
        raise CapError(f"Unknown archetype: {archetype}")

    capped_stats = {}

    for stat_name, value in stats.items():
        # Determine which cap to apply based on stat name
        if "damage" in stat_name.lower():
            cap = at_caps.get("damage_cap", 4.0)
            capped_value = min(value, cap)

        elif any(resist in stat_name.lower() for resist in [
            "smashing", "lethal", "fire", "cold", "energy",
            "negative", "toxic", "psionic", "resistance"
        ]):
            cap = at_caps.get("resistance_cap", 0.75)
            # Resistance is percentage, so cap at percentage value
            capped_value = min(value, cap * 100)

        elif "defense" in stat_name.lower():
            cap = GLOBAL_CAPS.get("defense_hard_cap", 0.95)
            # Defense is percentage, so cap at percentage value
            capped_value = min(value, cap * 100)

        elif "hp" in stat_name.lower() or "hit_points" in stat_name.lower():
            cap = at_caps.get("hp_cap", 1606)
            capped_value = min(value, cap)

        elif "recharge" in stat_name.lower():
            cap = GLOBAL_CAPS.get("recharge_cap", 5.0)
            # Recharge bonus is multiplicative
            capped_value = min(value, cap)

        elif "accuracy" in stat_name.lower() or "tohit" in stat_name.lower():
            cap = GLOBAL_CAPS.get("accuracy_cap", 0.95)
            floor = GLOBAL_CAPS.get("tohit_floor", 0.05)
            # ToHit is capped between floor and cap
            capped_value = max(floor * 100, min(value, cap * 100))

        else:
            # No cap found for this stat, return as-is
            capped_value = value

        capped_stats[stat_name] = capped_value

    return capped_stats


def check_defense_caps(
    defense_values: dict[str, float],
    warnings: list | None = None,
) -> dict[str, float]:
    """Check and cap defense values.

    Args:
        defense_values: Dict of defense type to value
        warnings: Optional list to append warnings to

    Returns:
        Capped defense values
    """
    hard_cap = GLOBAL_CAPS["defense_hard_cap"] * 100  # Convert to percentage
    soft_cap_pve = GLOBAL_CAPS["defense_soft_cap_pve"] * 100

    capped = {}

    for def_type, value in defense_values.items():
        # Apply hard cap
        capped_value = min(value, hard_cap)
        capped[def_type] = capped_value

        # Add warnings if applicable
        if warnings is not None:
            if value > hard_cap:
                warnings.append({
                    "type": "defense_hard_cap",
                    "message": f"{def_type} defense exceeds hard cap of {hard_cap}%",
                    "original": value,
                    "capped": capped_value,
                })
            elif value > soft_cap_pve:
                warnings.append({
                    "type": "defense_soft_cap",
                    "message": f"{def_type} defense exceeds soft cap of {soft_cap_pve}%",
                    "value": value,
                })

    return capped


def check_resistance_caps(
    resistance_values: dict[str, float],
    archetype: str,
    warnings: list | None = None,
) -> dict[str, float]:
    """Check and cap resistance values.

    Args:
        resistance_values: Dict of damage type to resistance value
        archetype: Character archetype
        warnings: Optional list to append warnings to

    Returns:
        Capped resistance values
    """
    # Get archetype resistance cap
    at_caps = ARCHETYPE_CAPS.get(archetype, {})
    res_cap = at_caps.get("resistance_cap", 0.75) * 100  # Convert to percentage

    capped = {}

    for dmg_type, value in resistance_values.items():
        # Resistance can be negative (vulnerability)
        if value > res_cap:
            capped_value = res_cap
            if warnings is not None:
                warnings.append({
                    "type": "resistance_cap",
                    "message": f"{dmg_type} resistance exceeds cap of {res_cap}%",
                    "original": value,
                    "capped": capped_value,
                })
        else:
            capped_value = value

        capped[dmg_type] = capped_value

    return capped


def check_damage_cap(
    damage_multiplier: float,
    archetype: str,
) -> float:
    """Check and cap damage multiplier.

    Args:
        damage_multiplier: Current damage multiplier (1.0 = 100%)
        archetype: Character archetype

    Returns:
        Capped damage multiplier
    """
    at_caps = ARCHETYPE_CAPS.get(archetype, {})
    damage_cap = at_caps.get("damage_cap", 4.0)

    return min(damage_multiplier, damage_cap)


def calculate_effective_stats(
    base_stats: dict[str, float],
    enhancements: dict[str, float],
    set_bonuses: dict[str, float],
    global_bonuses: dict[str, float],
    archetype: str,
) -> dict[str, dict[str, float]]:
    """Calculate effective stats after all bonuses and caps.

    Args:
        base_stats: Base stat values
        enhancements: Enhancement bonuses (post-ED)
        set_bonuses: Set bonus values
        global_bonuses: Global bonuses from powers, accolades, etc.
        archetype: Character archetype

    Returns:
        Dict with 'uncapped' and 'capped' stat dictionaries
    """
    # Combine all bonuses
    combined_stats = {}

    # Get all unique stat names
    all_stats = set()
    all_stats.update(base_stats.keys())
    all_stats.update(enhancements.keys())
    all_stats.update(set_bonuses.keys())
    all_stats.update(global_bonuses.keys())

    # Calculate combined values
    for stat in all_stats:
        base = base_stats.get(stat, 0.0)
        enh = enhancements.get(stat, 0.0)
        set_bon = set_bonuses.get(stat, 0.0)
        global_bon = global_bonuses.get(stat, 0.0)

        # For most stats, bonuses are additive
        if any(x in stat.lower() for x in ["damage", "recharge", "accuracy", "endurance"]):
            # These are multipliers
            combined_stats[stat] = base + enh + set_bon + global_bon
        else:
            # These are flat additions
            combined_stats[stat] = base + enh + set_bon + global_bon

    # Apply caps
    capped_stats = apply_archetype_caps(combined_stats, archetype)

    return {
        "uncapped": combined_stats,
        "capped": capped_stats,
    }
