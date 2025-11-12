"""
Archetype Caps - Maximum attribute values per archetype

Implements archetype-specific caps on defense, resistance, damage, HP, recovery, and regeneration.
Maps to MidsReborn's Archetype.cs cap properties and clsToonX.cs cap enforcement.

Different archetypes have different caps to maintain game balance and reinforce role identity.
"""

from dataclasses import dataclass
from enum import Enum


class ArchetypeType(Enum):
    """
    Archetype enumeration.

    Maps to playable archetypes in City of Heroes.
    """
    # Hero ATs
    TANKER = "Tanker"
    SCRAPPER = "Scrapper"
    DEFENDER = "Defender"
    CONTROLLER = "Controller"
    BLASTER = "Blaster"

    # Villain ATs
    BRUTE = "Brute"
    STALKER = "Stalker"
    CORRUPTOR = "Corruptor"
    DOMINATOR = "Dominator"
    MASTERMIND = "Mastermind"

    # Epic ATs
    PEACEBRINGER = "Peacebringer"
    WARSHADE = "Warshade"

    # Going Rogue ATs
    SENTINEL = "Sentinel"


@dataclass
class ArchetypeCaps:
    """
    Archetype cap values.

    Maps to MidsReborn's Archetype.cs properties.
    All caps are stored as multipliers (not percentages).

    Attributes:
        archetype: Archetype name
        damage_cap: Damage buff cap (4.0 = 400%)
        resistance_cap: Resistance cap (0.75 = 75%)
        defense_cap: Defense display cap (2.25 = 225%) - for display only
        hp_cap: Max hit points cap
        recovery_cap: Endurance recovery cap (5.0 = 500%)
        regeneration_cap: HP regeneration cap (20.0 = 2000%)
        recharge_cap: Recharge speed cap (5.0 = 500%)
        perception_cap: Perception range cap (feet)
    """
    archetype: ArchetypeType
    damage_cap: float = 4.0          # Default 400%
    resistance_cap: float = 0.75     # Default 75%
    defense_cap: float = 1.75        # Default 175% (display only)
    hp_cap: float = 5000.0           # Default 5000 HP
    recovery_cap: float = 5.0        # Default 500% (5x base)
    regeneration_cap: float = 20.0   # Default 2000% (20x base)
    recharge_cap: float = 5.0        # Default 500% (5x recharge speed)
    perception_cap: float = 1153.0   # Default ~1153 feet

    def apply_damage_cap(self, value: float) -> float:
        """
        Apply damage cap to a value.

        Args:
            value: Uncapped damage buff value

        Returns:
            Capped damage buff value

        Examples:
            >>> caps = ArchetypeCaps(ArchetypeType.BRUTE, damage_cap=7.75)
            >>> caps.apply_damage_cap(10.0)
            7.75
            >>> caps.apply_damage_cap(5.0)
            5.0
        """
        return min(value, self.damage_cap)

    def apply_resistance_cap(self, value: float) -> float:
        """
        Apply resistance cap to a value.

        Args:
            value: Uncapped resistance value (0.0-1.0 scale)

        Returns:
            Capped resistance value

        Examples:
            >>> caps = ArchetypeCaps(ArchetypeType.TANKER, resistance_cap=0.90)
            >>> caps.apply_resistance_cap(0.95)
            0.90
            >>> caps.apply_resistance_cap(0.75)
            0.75
        """
        return min(value, self.resistance_cap)

    def apply_defense_cap(self, value: float) -> float:
        """
        Apply defense cap to a value (display only).

        Note: Defense has no hard cap in gameplay, only soft cap at 45%.
        This cap is for display purposes only.

        Args:
            value: Uncapped defense value

        Returns:
            Capped defense value (for display)
        """
        return min(value, self.defense_cap)

    def apply_hp_cap(self, value: float) -> float:
        """
        Apply HP cap to a value.

        Args:
            value: Uncapped max HP value

        Returns:
            Capped max HP value
        """
        if self.hp_cap > 0:
            return min(value, self.hp_cap)
        return value

    def apply_recovery_cap(self, value: float) -> float:
        """
        Apply endurance recovery cap to a value.

        Args:
            value: Uncapped recovery multiplier

        Returns:
            Capped recovery multiplier
        """
        return min(value, self.recovery_cap)

    def apply_regeneration_cap(self, value: float) -> float:
        """
        Apply HP regeneration cap to a value.

        Args:
            value: Uncapped regeneration multiplier

        Returns:
            Capped regeneration multiplier
        """
        return min(value, self.regeneration_cap)

    def apply_recharge_cap(self, value: float) -> float:
        """
        Apply recharge speed cap to a value.

        Args:
            value: Uncapped recharge multiplier

        Returns:
            Capped recharge multiplier
        """
        return min(value, self.recharge_cap)


# Default cap values by archetype
# Based on Spec 17 data
ARCHETYPE_CAPS_DATA = {
    ArchetypeType.TANKER: ArchetypeCaps(
        archetype=ArchetypeType.TANKER,
        damage_cap=4.0,
        resistance_cap=0.90,
        defense_cap=2.25,
        hp_cap=3534.0,
        recovery_cap=8.0,
        regeneration_cap=25.0,
        recharge_cap=5.0
    ),
    ArchetypeType.BRUTE: ArchetypeCaps(
        archetype=ArchetypeType.BRUTE,
        damage_cap=7.75,  # Highest damage cap due to Fury
        resistance_cap=0.90,
        defense_cap=2.25,
        hp_cap=3212.0,
        recovery_cap=8.0,
        regeneration_cap=25.0,
        recharge_cap=5.0
    ),
    ArchetypeType.SCRAPPER: ArchetypeCaps(
        archetype=ArchetypeType.SCRAPPER,
        damage_cap=5.0,
        resistance_cap=0.75,
        defense_cap=2.00,
        hp_cap=2409.0,
        recovery_cap=8.0,
        regeneration_cap=30.0,  # Highest regen cap
        recharge_cap=5.0
    ),
    ArchetypeType.STALKER: ArchetypeCaps(
        archetype=ArchetypeType.STALKER,
        damage_cap=5.0,
        resistance_cap=0.75,
        defense_cap=2.00,
        hp_cap=2091.0,
        recovery_cap=8.0,
        regeneration_cap=30.0,  # Highest regen cap
        recharge_cap=5.0
    ),
    ArchetypeType.BLASTER: ArchetypeCaps(
        archetype=ArchetypeType.BLASTER,
        damage_cap=5.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=1874.0,
        recovery_cap=8.0,
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.DEFENDER: ArchetypeCaps(
        archetype=ArchetypeType.DEFENDER,
        damage_cap=4.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=1874.0,
        recovery_cap=10.0,  # Higher for support
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.CONTROLLER: ArchetypeCaps(
        archetype=ArchetypeType.CONTROLLER,
        damage_cap=4.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=1874.0,
        recovery_cap=12.0,  # Highest recovery cap
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.CORRUPTOR: ArchetypeCaps(
        archetype=ArchetypeType.CORRUPTOR,
        damage_cap=5.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=1874.0,
        recovery_cap=8.0,
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.DOMINATOR: ArchetypeCaps(
        archetype=ArchetypeType.DOMINATOR,
        damage_cap=4.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=1874.0,
        recovery_cap=12.0,  # High for control
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.MASTERMIND: ArchetypeCaps(
        archetype=ArchetypeType.MASTERMIND,
        damage_cap=4.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=1874.0,
        recovery_cap=12.0,  # High for pet management
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.SENTINEL: ArchetypeCaps(
        archetype=ArchetypeType.SENTINEL,
        damage_cap=4.0,
        resistance_cap=0.75,
        defense_cap=1.75,
        hp_cap=2409.0,
        recovery_cap=8.0,
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.PEACEBRINGER: ArchetypeCaps(
        archetype=ArchetypeType.PEACEBRINGER,
        damage_cap=4.0,
        resistance_cap=0.85,  # Kheldian special
        defense_cap=2.00,
        hp_cap=2091.0,  # Form-dependent
        recovery_cap=8.0,
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
    ArchetypeType.WARSHADE: ArchetypeCaps(
        archetype=ArchetypeType.WARSHADE,
        damage_cap=4.0,
        resistance_cap=0.85,  # Kheldian special
        defense_cap=2.00,
        hp_cap=2091.0,  # Form-dependent
        recovery_cap=8.0,
        regeneration_cap=20.0,
        recharge_cap=5.0
    ),
}


def get_archetype_caps(archetype: ArchetypeType) -> ArchetypeCaps:
    """
    Get cap values for an archetype.

    Args:
        archetype: Archetype enum value

    Returns:
        ArchetypeCaps instance with cap values

    Raises:
        ValueError: If archetype is not found

    Examples:
        >>> caps = get_archetype_caps(ArchetypeType.TANKER)
        >>> caps.resistance_cap
        0.90
        >>> caps = get_archetype_caps(ArchetypeType.BRUTE)
        >>> caps.damage_cap
        7.75
    """
    if archetype not in ARCHETYPE_CAPS_DATA:
        raise ValueError(f"Unknown archetype: {archetype}")

    return ARCHETYPE_CAPS_DATA[archetype]


def apply_cap(value: float, cap: float) -> float:
    """
    Apply a cap to a value (generic utility).

    Args:
        value: Uncapped value
        cap: Maximum allowed value

    Returns:
        Capped value

    Examples:
        >>> apply_cap(100.0, 75.0)
        75.0
        >>> apply_cap(50.0, 75.0)
        50.0
    """
    return min(value, cap)


def is_at_cap(value: float, cap: float, tolerance: float = 0.001) -> bool:
    """
    Check if a value is at or above the cap.

    Args:
        value: Value to check
        cap: Cap threshold
        tolerance: Floating-point comparison tolerance

    Returns:
        True if value >= cap (within tolerance)

    Examples:
        >>> is_at_cap(0.90, 0.90)
        True
        >>> is_at_cap(0.75, 0.90)
        False
        >>> is_at_cap(0.9001, 0.90, tolerance=0.001)
        True
    """
    return value >= (cap - tolerance)
