"""Game constants for calculations.

All constants are based on Homecoming 2025.7.1111 data.
These values can be overridden for testing.
"""


# Enhancement Diversification (ED) Schedules
ED_SCHEDULES = {
    "A": {
        "thresholds": [0.0, 0.95, 1.70, 2.60],
        "multipliers": [1.0, 0.9, 0.7, 0.15],
    },
    "B": {
        "thresholds": [0.0, 0.40, 0.80, 1.20],
        "multipliers": [1.0, 0.9, 0.7, 0.15],
    },
    "C": {
        "thresholds": [0.0, 0.25, 0.50, 0.75],
        "multipliers": [1.0, 0.9, 0.7, 0.15],
    },
}

# ED Schedule assignments by enhancement type
ED_SCHEDULE_TYPES = {
    "damage": "A",
    "accuracy": "A",
    "endurance": "A",
    "recharge": "A",
    "heal": "A",
    "defense": "B",
    "defense_buff": "B",
    "resistance": "B",
    "resistance_buff": "B",
    "tohit_buff": "B",
    "defense_debuff": "B",
    "resistance_debuff": "B",
    "tohit_debuff": "B",
    "range": "C",
    "cone": "C",
    "aoe": "C",
}

# Archetype-specific caps
ARCHETYPE_CAPS = {
    "Blaster": {
        "damage_cap": 4.0,  # 400%
        "resistance_cap": 0.75,  # 75%
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,  # 95%
        "base_hp": 1204.8,
    },
    "Controller": {
        "damage_cap": 3.0,  # 300%
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1017.4,
    },
    "Defender": {
        "damage_cap": 3.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1017.4,
    },
    "Scrapper": {
        "damage_cap": 4.0,
        "resistance_cap": 0.75,
        "hp_cap": 2088,
        "defense_hard_cap": 0.95,
        "base_hp": 1338.6,
    },
    "Tanker": {
        "damage_cap": 3.0,
        "resistance_cap": 0.90,  # 90%
        "hp_cap": 3534,
        "defense_hard_cap": 0.95,
        "base_hp": 1874.1,
    },
    "Brute": {
        "damage_cap": 6.0,  # 600%
        "resistance_cap": 0.90,
        "hp_cap": 3212,
        "defense_hard_cap": 0.95,
        "base_hp": 1499.3,
    },
    "Stalker": {
        "damage_cap": 4.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1204.8,
    },
    "Mastermind": {
        "damage_cap": 3.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 803.2,
    },
    "Dominator": {
        "damage_cap": 3.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1017.4,
    },
    "Corruptor": {
        "damage_cap": 4.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1070.9,
    },
    "Arachnos Soldier": {
        "damage_cap": 4.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1070.9,
    },
    "Arachnos Widow": {
        "damage_cap": 4.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1017.4,
    },
    "Peacebringer": {
        "damage_cap": 3.0,
        "resistance_cap": 0.85,  # 85%
        "hp_cap": 2088,
        "defense_hard_cap": 0.95,
        "base_hp": 1070.9,
    },
    "Warshade": {
        "damage_cap": 3.0,
        "resistance_cap": 0.85,
        "hp_cap": 2088,
        "defense_hard_cap": 0.95,
        "base_hp": 1070.9,
    },
    "Sentinel": {
        "damage_cap": 4.0,
        "resistance_cap": 0.75,
        "hp_cap": 1606,
        "defense_hard_cap": 0.95,
        "base_hp": 1204.8,
    },
}

# Global caps applicable to all archetypes
GLOBAL_CAPS = {
    "recharge_cap": 5.0,  # +500% max global recharge
    "defense_hard_cap": 0.95,  # 95% hard cap all ATs
    "defense_soft_cap_pve": 0.45,  # 45% soft cap PvE
    "defense_soft_cap_pvp": 0.45,  # 45% soft cap PvP
    "endurance_min_cost_factor": 0.1,  # Minimum 10% of base cost
    "accuracy_cap": 0.95,  # 95% max final tohit
    "tohit_floor": 0.05,  # 5% min final tohit
}

# PvP modifiers
PVP_MODIFIERS = {
    "damage_modifier": 0.5,  # Damage halved in PvP
    "heal_modifier": 0.5,  # Healing halved in PvP
    "mez_duration_modifier": 0.5,  # Mez durations halved
}

# Damage types
DAMAGE_TYPES = [
    "smashing",
    "lethal",
    "fire",
    "cold",
    "energy",
    "negative",
    "toxic",
    "psionic",
]

# Defense types
DEFENSE_TYPES = ["melee", "ranged", "aoe"]

# Positional types for powers
POSITIONAL_TYPES = ["melee", "ranged", "aoe"]

# Enhancement grade multipliers
ENHANCEMENT_GRADE_MULTIPLIERS = {
    "TO": {"damage": 0.08333, "accuracy": 0.08333, "endurance": 0.08333},  # 8.33%
    "DO": {"damage": 0.16666, "accuracy": 0.16666, "endurance": 0.16666},  # 16.66%
    "SO": {"damage": 0.33333, "accuracy": 0.33333, "endurance": 0.33333},  # 33.33%
    "IO": {
        # Level-based, typically 11.7% to 42.4%
        # This will be calculated based on level
    },
}

# Base endurance values
BASE_ENDURANCE = {
    "max": 100.0,
    "recovery_rate": 1.67,  # per second
}

# Base movement speeds (in mph)
BASE_MOVEMENT = {
    "run_speed": 14.32,  # Base run speed in mph (matches MidsReborn)
    "fly_speed": 0.0,    # Only if flight power active
    "jump_height": 8.0,  # Base jump height in feet
    "jump_speed": 14.32, # Base jump speed in mph
}

# Stealth and perception base values
BASE_STEALTH_PERCEPTION = {
    "stealth_pve": 0.0,
    "stealth_pvp": 0.0,
    "perception_pve": 500.0,
    "perception_pvp": 1153.0,
}

# Base ToHit values
BASE_TOHIT = {
    "pve_even": 0.75,  # 75% base chance vs even-level
    "pvp": 0.50,       # 50% base in PvP
    "level_modifier": 0.05,  # ±5% per level difference
    "floor": 0.05,     # 5% minimum hit chance
    "ceiling": 0.95,   # 95% maximum hit chance
}

# Set bonus stacking rules
SET_BONUS_RULES = {
    "max_same_set": 5,  # Maximum 5 of the same set
    "unique_bonus_per_set": True,  # Each unique bonus from a set counts once
}

# Power minimum values
POWER_MINIMUMS = {
    "recharge_time": 0.5,  # seconds
    "activation_time": 0.132,  # seconds (arcanatime minimum)
}

# Experience table by level (for exemplaring calculations)
EXPERIENCE_TABLE = {
    1: 0,
    2: 106,
    3: 337,
    4: 582,
    5: 800,
    10: 5796,
    15: 20643,
    20: 51933,
    25: 108934,
    30: 203188,
    35: 348259,
    40: 561136,
    45: 864410,
    50: 1353550,
}


def get_archetype_cap(archetype: str, cap_type: str) -> float:
    """Get a specific cap for an archetype.

    Args:
        archetype: The archetype name
        cap_type: The type of cap (damage_cap, resistance_cap, etc.)

    Returns:
        The cap value, or a default if not found
    """
    at_caps = ARCHETYPE_CAPS.get(archetype, {})
    return at_caps.get(cap_type, GLOBAL_CAPS.get(cap_type, 0.0))


def get_ed_schedule(enhancement_type: str) -> dict[str, list]:
    """Get the ED schedule for a given enhancement type.

    Args:
        enhancement_type: The type of enhancement (damage, accuracy, etc.)

    Returns:
        The ED schedule dict with thresholds and multipliers
    """
    schedule_letter = ED_SCHEDULE_TYPES.get(enhancement_type, "A")
    return ED_SCHEDULES.get(schedule_letter, ED_SCHEDULES["A"])


# Archetype heal modifiers (multiplier for heal powers)
ARCHETYPE_HEAL_MODIFIERS = {
    "Blaster": 0.60,      # 60% of base heal
    "Controller": 1.00,    # 100% of base heal
    "Defender": 1.00,      # 100% of base heal
    "Scrapper": 0.60,      # 60% of base heal
    "Tanker": 0.60,        # 60% of base heal
    "Brute": 0.60,         # 60% of base heal
    "Stalker": 0.60,       # 60% of base heal
    "Mastermind": 1.00,    # 100% of base heal
    "Dominator": 0.80,     # 80% of base heal
    "Corruptor": 1.00,     # 100% of base heal
    "Arachnos Soldier": 0.80,  # 80% of base heal
    "Arachnos Widow": 0.80,    # 80% of base heal
    "Peacebringer": 0.80,  # 80% of base heal
    "Warshade": 0.80,      # 80% of base heal
    "Sentinel": 0.70,      # 70% of base heal
}

# Base heal values by level (for 1.0 heal scale)
# These are approximate values based on the game's healing formula
HEAL_BASE_BY_LEVEL = {
    1: 35.795,    # Level 1 base heal
    5: 53.693,
    10: 89.488,
    15: 125.283,
    20: 161.078,
    25: 196.873,
    30: 232.668,
    35: 268.463,
    40: 304.258,
    45: 340.053,
    50: 357.95,   # Level 50 base heal
}

# Buff caps (percentage values)
BUFF_CAPS = {
    "damage": 400.0,       # Varies by archetype, this is a fallback
    "tohit": 200.0,        # +200% ToHit buff cap
    "accuracy": 200.0,     # +200% Accuracy buff cap
    "recharge": 500.0,     # +500% Recharge buff cap
    "hp": 200.0,          # +200% Max HP buff cap
    "regeneration": 2000.0,  # +2000% Regeneration buff cap
    "recovery": 500.0,     # +500% Recovery buff cap
    "run_speed": 300.0,    # +300% Run Speed cap
    "fly_speed": 300.0,    # +300% Fly Speed cap
    "jump_height": 300.0,  # +300% Jump Height cap
    "jump_speed": 300.0,   # +300% Jump Speed cap
    "endurance_cost": 90.0,  # Max 90% endurance cost reduction
}

# Debuff resistance caps (percentage values)
DEBUFF_RESISTANCE_CAPS = {
    "damage": 100.0,       # 100% damage debuff resistance
    "tohit": 100.0,        # 100% ToHit debuff resistance
    "accuracy": 100.0,     # 100% Accuracy debuff resistance
    "defense": 100.0,      # 100% Defense debuff resistance
    "regeneration": 100.0, # 100% Regen debuff resistance
    "recovery": 100.0,     # 100% Recovery debuff resistance
    "recharge": 100.0,     # 100% Recharge debuff resistance
    "movement": 100.0,     # 100% Movement debuff resistance
    "endurance": 100.0,    # 100% Endurance debuff resistance
    "hp": 100.0,          # 100% HP debuff resistance
}
