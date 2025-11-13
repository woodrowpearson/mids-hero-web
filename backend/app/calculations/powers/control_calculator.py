"""
Control/Mez Effect Calculator

Calculates control effect application including magnitude vs protection,
duration, stacking, and resistance mechanics.

Based on MidsReborn's Effect.cs and Enums.cs implementation.
"""

from dataclasses import dataclass
from enum import Enum


class MezType(Enum):
    """All mez/control effect types (maps to eMez enum in MidsReborn)"""

    NONE = "none"
    CONFUSED = "confused"
    HELD = "held"
    IMMOBILIZED = "immobilized"
    KNOCKBACK = "knockback"
    KNOCKUP = "knockup"
    PLACATE = "placate"
    REPEL = "repel"
    SLEEP = "sleep"
    STUNNED = "stunned"
    TAUNT = "taunt"
    TERRORIZED = "terrorized"
    UNTOUCHABLE = "untouchable"
    TELEPORT = "teleport"
    TOGGLE_DROP = "toggle_drop"
    AFRAID = "afraid"
    AVOID = "avoid"
    COMBAT_PHASE = "combat_phase"
    ONLY_AFFECTS_SELF = "only_affects_self"


# Mezzes where duration can be enhanced (from Enums.cs lines 1436-1439)
DURATION_ENHANCEABLE_MEZZES = {
    MezType.CONFUSED,
    MezType.HELD,
    MezType.IMMOBILIZED,
    MezType.PLACATE,
    MezType.SLEEP,
    MezType.STUNNED,
    MezType.TAUNT,
    MezType.TERRORIZED,
    MezType.UNTOUCHABLE,
}


@dataclass
class MezEffect:
    """
    Represents a mez/control effect.

    Extends base Effect with mez-specific properties.
    Maps to MidsReborn's Effect class with EffectType = Mez.
    """

    mez_type: MezType
    magnitude: float
    duration: float = 0.0
    scale: float = 1.0
    stacks: bool = False
    ignore_ed: bool = False

    def is_duration_enhanceable(self) -> bool:
        """Check if this mez type can have duration enhanced"""
        return self.mez_type in DURATION_ENHANCEABLE_MEZZES

    def scaled_magnitude(
        self, at_scale: float = 1.0, modifier_table_scale: float = 1.0
    ) -> float:
        """
        Calculate final magnitude with archetype and modifier table scaling.

        Formula from Effect.cs line 407:
            Magnitude = Scale * nMagnitude * ModifierTableValue

        Args:
            at_scale: Archetype's mez scale modifier
            modifier_table_scale: Modifier table value for caster level

        Returns:
            Final magnitude value
        """
        return self.magnitude * self.scale * at_scale * modifier_table_scale

    def effective_duration(
        self,
        at_duration_scale: float = 1.0,
        duration_enhancement: float = 0.0,
        target_resistance: float = 0.0,
    ) -> float:
        """
        Calculate effective duration after all modifiers.

        Args:
            at_duration_scale: Archetype's duration scale
            duration_enhancement: Total duration enhancement bonus (e.g., 0.95 for 95%)
            target_resistance: Target's mez resistance (0.0 to 1.0)

        Returns:
            Effective duration in seconds
        """
        # Base duration with AT scale
        base = self.duration * at_duration_scale

        # Apply duration enhancement (only if mez type allows it)
        if self.is_duration_enhanceable():
            base = base * (1.0 + duration_enhancement)

        # Apply target resistance (reduces duration)
        final = base * (1.0 - target_resistance)

        return max(0.0, final)


@dataclass
class MezProtection:
    """
    Status protection values (magnitude-based).

    Protection prevents mez from being applied.
    All values are additive from multiple sources.
    """

    confused: float = 0.0
    held: float = 0.0
    immobilized: float = 0.0
    knockback: float = 0.0
    knockup: float = 0.0
    sleep: float = 0.0
    stunned: float = 0.0
    terrorized: float = 0.0
    placate: float = 0.0
    taunt: float = 0.0
    repel: float = 0.0
    teleport: float = 0.0
    toggle_drop: float = 0.0
    afraid: float = 0.0
    avoid: float = 0.0
    untouchable: float = 0.0

    def get_protection(self, mez_type: MezType) -> float:
        """Get protection value for specific mez type"""
        protection_map = {
            MezType.CONFUSED: self.confused,
            MezType.HELD: self.held,
            MezType.IMMOBILIZED: self.immobilized,
            MezType.KNOCKBACK: self.knockback,
            MezType.KNOCKUP: self.knockup,
            MezType.SLEEP: self.sleep,
            MezType.STUNNED: self.stunned,
            MezType.TERRORIZED: self.terrorized,
            MezType.PLACATE: self.placate,
            MezType.TAUNT: self.taunt,
            MezType.REPEL: self.repel,
            MezType.TELEPORT: self.teleport,
            MezType.TOGGLE_DROP: self.toggle_drop,
            MezType.AFRAID: self.afraid,
            MezType.AVOID: self.avoid,
            MezType.UNTOUCHABLE: self.untouchable,
        }
        return protection_map.get(mez_type, 0.0)


@dataclass
class MezResistance:
    """
    Status resistance values (percentage-based).

    Resistance reduces duration, not magnitude.
    All values are 0.0 to 1.0 (0% to 100%).
    """

    confused: float = 0.0
    held: float = 0.0
    immobilized: float = 0.0
    knockback: float = 0.0
    knockup: float = 0.0
    sleep: float = 0.0
    stunned: float = 0.0
    terrorized: float = 0.0
    placate: float = 0.0
    taunt: float = 0.0
    repel: float = 0.0

    def get_resistance(self, mez_type: MezType) -> float:
        """Get resistance value for specific mez type (0.0 to 1.0)"""
        resistance_map = {
            MezType.CONFUSED: self.confused,
            MezType.HELD: self.held,
            MezType.IMMOBILIZED: self.immobilized,
            MezType.KNOCKBACK: self.knockback,
            MezType.KNOCKUP: self.knockup,
            MezType.SLEEP: self.sleep,
            MezType.STUNNED: self.stunned,
            MezType.TERRORIZED: self.terrorized,
            MezType.PLACATE: self.placate,
            MezType.TAUNT: self.taunt,
            MezType.REPEL: self.repel,
        }
        return resistance_map.get(mez_type, 0.0)


class ControlCalculator:
    """
    Calculate mez application and duration.

    Production-ready implementation with full error handling.
    Maps to MidsReborn's mez calculation logic.
    """

    def __init__(self) -> None:
        """Initialize calculator with standard protection values."""
        self.standard_protection = self._init_standard_protection()

    @staticmethod
    def _init_standard_protection() -> dict[str, dict[MezType, float]]:
        """
        Initialize standard NPC protection values.

        From game data:
        - Minions: Mag 1
        - Lieutenants: Mag 2
        - Bosses: Mag 3 (Issue 3+)
        - Elite Bosses: Mag 6
        - AVs: Mag 50 (effectively immune)
        """
        return {
            "minion": {
                MezType.HELD: 1.0,
                MezType.STUNNED: 1.0,
                MezType.IMMOBILIZED: 1.0,
                MezType.SLEEP: 1.0,
                MezType.CONFUSED: 1.0,
                MezType.TERRORIZED: 1.0,
            },
            "lieutenant": {
                MezType.HELD: 2.0,
                MezType.STUNNED: 2.0,
                MezType.IMMOBILIZED: 2.0,
                MezType.SLEEP: 2.0,
                MezType.CONFUSED: 2.0,
                MezType.TERRORIZED: 2.0,
            },
            "boss": {
                MezType.HELD: 3.0,
                MezType.STUNNED: 3.0,
                MezType.IMMOBILIZED: 3.0,
                MezType.SLEEP: 3.0,
                MezType.CONFUSED: 3.0,
                MezType.TERRORIZED: 3.0,
            },
            "elite_boss": {
                MezType.HELD: 6.0,
                MezType.STUNNED: 6.0,
                MezType.IMMOBILIZED: 6.0,
                MezType.SLEEP: 6.0,
            },
            "av": {
                MezType.HELD: 50.0,
                MezType.STUNNED: 50.0,
                MezType.IMMOBILIZED: 50.0,
                MezType.SLEEP: 50.0,
            },
        }

    def applies(
        self,
        mez: MezEffect,
        protection: MezProtection,
        at_scale: float = 1.0,
        modifier_table_scale: float = 1.0,
        caster_level: int = 50,
        target_level: int = 50,
    ) -> bool:
        """
        Check if mez magnitude overcomes protection.

        Includes purple patch and all modifiers.

        Args:
            mez: The mez effect being applied
            protection: Target's status protection
            at_scale: Caster's archetype mez scale
            modifier_table_scale: Modifier table value for caster level
            caster_level: Caster's level
            target_level: Target's level

        Returns:
            True if mez will be applied

        Raises:
            ValueError: If mez type is invalid or parameters out of range
        """
        if not isinstance(mez.mez_type, MezType):
            raise ValueError(f"Invalid mez type: {mez.mez_type}")

        if at_scale <= 0:
            raise ValueError(f"AT scale must be positive, got {at_scale}")

        # Calculate effective magnitude with all modifiers
        effective_mag = mez.scaled_magnitude(
            at_scale=at_scale, modifier_table_scale=modifier_table_scale
        )

        # Apply purple patch
        level_diff = target_level - caster_level
        purple_patch = self._calculate_purple_patch(level_diff)
        final_mag = effective_mag * purple_patch

        # Check vs protection (must be STRICTLY GREATER THAN)
        prot_mag = protection.get_protection(mez.mez_type)

        return final_mag > prot_mag

    def calculate_duration(
        self,
        mez: MezEffect,
        resistance: MezResistance,
        at_duration_scale: float = 1.0,
        duration_enhancement: float = 0.0,
        caster_level: int = 50,
        target_level: int = 50,
    ) -> float:
        """
        Calculate final mez duration with all modifiers.

        Args:
            mez: The mez effect
            resistance: Target's mez resistance
            at_duration_scale: Caster's AT duration scale
            duration_enhancement: Total duration enhancement (post-ED)
            caster_level: Caster's level
            target_level: Target's level

        Returns:
            Final duration in seconds

        Raises:
            ValueError: If parameters are invalid
        """
        if duration_enhancement < 0:
            raise ValueError(
                f"Duration enhancement cannot be negative: {duration_enhancement}"
            )

        if at_duration_scale <= 0:
            raise ValueError(f"AT duration scale must be positive: {at_duration_scale}")

        # Get target resistance
        target_res = resistance.get_resistance(mez.mez_type)

        if not (0 <= target_res <= 1):
            raise ValueError(f"Resistance must be 0-1, got {target_res}")

        # Calculate duration
        duration = mez.effective_duration(
            at_duration_scale=at_duration_scale,
            duration_enhancement=duration_enhancement,
            target_resistance=target_res,
        )

        # Apply purple patch to duration
        level_diff = target_level - caster_level
        purple_patch = self._calculate_purple_patch(level_diff)
        final_duration = duration * purple_patch

        return max(0.0, final_duration)

    def stack_magnitude(
        self,
        mezzes: list[MezEffect],
        at_scale: float = 1.0,
        modifier_table_scale: float = 1.0,
    ) -> dict[MezType, float]:
        """
        Stack mez magnitudes for same type.

        Args:
            mezzes: List of active mez effects
            at_scale: Archetype scale
            modifier_table_scale: Modifier table scale

        Returns:
            Dict mapping MezType to total stacked magnitude
        """
        stacked: dict[MezType, float] = {}

        for mez in mezzes:
            if mez.stacks:
                mag = mez.scaled_magnitude(at_scale, modifier_table_scale)

                if mez.mez_type not in stacked:
                    stacked[mez.mez_type] = 0.0
                stacked[mez.mez_type] += mag

        return stacked

    @staticmethod
    def _calculate_purple_patch(level_diff: int) -> float:
        """
        Calculate purple patch modifier for level difference.

        Purple patch: level difference affects mez magnitude and duration.

        Args:
            level_diff: Target level - Caster level

        Returns:
            Modifier value (0.48 to 1.5)
        """
        if level_diff > 0:
            # Target is higher level - reduces effectiveness
            return max(0.48, 1.0 - (level_diff * 0.1))
        else:
            # Target is lower level - increases effectiveness (capped)
            return min(1.5, 1.0 + (abs(level_diff) * 0.1))

    def check_breakpoint(
        self, total_magnitude: float, target_rank: str, mez_type: MezType
    ) -> bool:
        """
        Check if magnitude breaks through target's protection.

        Common breakpoints:
        - Mag 2: Breaks through lieutenants
        - Mag 3: Breaks through bosses
        - Mag 6: Breaks through elite bosses
        - Mag 50+: Required for AVs

        Args:
            total_magnitude: Total mez magnitude (after stacking)
            target_rank: 'minion', 'lieutenant', 'boss', 'elite_boss', 'av'
            mez_type: Type of mez being checked

        Returns:
            True if magnitude overcomes protection

        Raises:
            ValueError: If target_rank is unknown
        """
        if target_rank not in self.standard_protection:
            raise ValueError(f"Unknown target rank: {target_rank}")

        rank_protection = self.standard_protection[target_rank]
        protection_value = rank_protection.get(mez_type, 0.0)

        return total_magnitude > protection_value


class KnockbackCalculator:
    """Special handling for knockback/knockup distance calculations"""

    @staticmethod
    def calculate_knockback_distance(
        magnitude: float, kb_protection: float
    ) -> tuple[str, float]:
        """
        Calculate knockback effect type and distance.

        In CoH, knockback magnitude directly determines distance.

        Args:
            magnitude: Knockback magnitude value
            kb_protection: Target's KB protection magnitude

        Returns:
            Tuple of (effect_type, distance)
            effect_type: "knockback", "knockdown", or "none"
            distance: Approximate knockback distance in game units
        """
        net_magnitude = magnitude - kb_protection

        if net_magnitude <= 0:
            return ("none", 0.0)
        elif net_magnitude < 1.0:
            # Partial protection reduces KB to knockdown
            return ("knockdown", 0.0)
        else:
            # Full knockback - magnitude ~= distance in feet
            distance = net_magnitude * 10.0  # Approximate
            return ("knockback", distance)

    @staticmethod
    def is_knockdown(kb_magnitude: float, kb_protection: float) -> bool:
        """
        Check if knockback is reduced to knockdown.

        In CoH, some KB protection doesn't prevent KB entirely,
        but reduces it to knockdown (minimal animation, no distance).

        Args:
            kb_magnitude: Incoming knockback magnitude
            kb_protection: Target's KB protection magnitude

        Returns:
            True if KB becomes knockdown (protection partial but not total)
        """
        # If protection is negative (knockdown enhancement)
        # or protection is very close to magnitude
        # knockback becomes knockdown
        return (kb_protection < 0) or (
            kb_protection > 0
            and kb_protection < kb_magnitude
            and kb_magnitude - kb_protection < 1.0
        )
