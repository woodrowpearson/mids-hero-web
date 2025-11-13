"""
Incarnate Alpha Slot Calculator

Implements Alpha slot level shifts and passive boosts for Mids Hero Web.
Based on MidsReborn implementation from frmIncarnate.cs, GroupedFx.cs, Effect.cs.

Based on Spec 29: docs/midsreborn/calculations/29-incarnate-alpha-shifts.md
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

from ..core.effect_types import EffectType


class AlphaType(Enum):
    """
    8 Alpha slot types with different passive boost focuses.

    From frmIncarnate.cs lines 68-76.
    """

    AGILITY = "agility"  # Endurance Discount, Defense, Recharge
    CARDIAC = "cardiac"  # Endurance Mod, Resistance, Endurance Discount
    INTUITION = "intuition"  # ToHit, Accuracy, Range
    MUSCULATURE = "musculature"  # Damage, Endurance Discount
    NERVE = "nerve"  # Accuracy, Confusion/Hold/Debuff
    RESILIENT = "resilient"  # Resistance, Endurance Discount, Healing
    SPIRITUAL = "spiritual"  # Healing, Recharge, Slow Resistance
    VIGOR = "vigor"  # Max HP, Recovery, Regeneration


class AlphaTier(Enum):
    """
    Alpha slot tiers - T1/T2 have no shift, T3/T4 provide +1 shift.

    Maps to MidsReborn's Enums.eAlphaOrder enum (Enums.cs lines 99-110).

    Each tier has:
        - tier_name: Internal name (snake_case)
        - tier_level: 1-4
        - provides_shift: Whether this tier provides level shift
    """

    T1_BOOST = ("boost", 1, False)
    T2_CORE_BOOST = ("core_boost", 2, False)
    T2_RADIAL_BOOST = ("radial_boost", 2, False)
    T3_TOTAL_CORE_REVAMP = ("total_core_revamp", 3, True)
    T3_PARTIAL_CORE_REVAMP = ("partial_core_revamp", 3, True)
    T3_TOTAL_RADIAL_REVAMP = ("total_radial_revamp", 3, True)
    T3_PARTIAL_RADIAL_REVAMP = ("partial_radial_revamp", 3, True)
    T4_CORE_PARAGON = ("core_paragon", 4, True)
    T4_RADIAL_PARAGON = ("radial_paragon", 4, True)

    def __init__(self, tier_name: str, tier_level: int, provides_shift: bool):
        self.tier_name = tier_name
        self.tier_level = tier_level
        self.provides_shift = provides_shift


@dataclass
class AlphaEffect:
    """
    Represents a single passive boost effect from Alpha slot.

    Attributes:
        effect_type: Type of boost (Damage, Defense, etc.)
        magnitude: Base boost value (0.33 = 33%)
        modifier_table: AT scaling table name
        ignore_ed: Whether to bypass ED curve (usually False)
        buffable: Whether effect can be enhanced (usually True)
        resistible: Whether effect can be resisted (usually False for self-buffs)
    """

    effect_type: EffectType
    magnitude: Decimal
    modifier_table: str = "Melee_Ones"
    ignore_ed: bool = False
    buffable: bool = True
    resistible: bool = False


@dataclass
class AlphaSlot:
    """
    Represents a complete Incarnate Alpha slot configuration.

    Attributes:
        alpha_type: Which Alpha (Musculature, Cardiac, etc.)
        tier: Which tier (T1-T4, Core/Radial)
        effects: List of passive boost effects
    """

    alpha_type: AlphaType
    tier: AlphaTier
    effects: list[AlphaEffect] = field(default_factory=list)

    def get_level_shift(
        self, has_lore_t4: bool = False, has_destiny_t4: bool = False
    ) -> int:
        """
        Calculate total level shift provided by this Alpha and other Incarnates.

        From GroupedFx.cs lines 2001-2003 and level shift stacking rules.

        Args:
            has_lore_t4: Whether Lore T4 is slotted
            has_destiny_t4: Whether Destiny T4 is slotted

        Returns:
            Total level shift (0-3)

        Examples:
            >>> alpha_t1 = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T1_BOOST)
            >>> alpha_t1.get_level_shift()
            0

            >>> alpha_t3 = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T3_PARTIAL_CORE_REVAMP)
            >>> alpha_t3.get_level_shift()
            1

            >>> alpha_t4 = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T4_CORE_PARAGON)
            >>> alpha_t4.get_level_shift(has_lore_t4=True, has_destiny_t4=True)
            3
        """
        if not self.tier.provides_shift:
            return 0

        # Base shift from Alpha
        shift = 1

        # Additional shifts only if Alpha is T4
        if self.tier.tier_level == 4:
            if has_lore_t4:
                shift += 1
            if has_lore_t4 and has_destiny_t4:
                shift += 1

        # Maximum +3
        return min(shift, 3)

    def get_effective_level(
        self, base_level: int, has_lore_t4: bool = False, has_destiny_t4: bool = False
    ) -> int:
        """
        Calculate effective character level including shifts.

        Args:
            base_level: Character's actual level (typically 50)
            has_lore_t4: Whether Lore T4 is slotted
            has_destiny_t4: Whether Destiny T4 is slotted

        Returns:
            Effective level (base_level + shift)

        Examples:
            >>> alpha = AlphaSlot(AlphaType.MUSCULATURE, AlphaTier.T4_CORE_PARAGON)
            >>> alpha.get_effective_level(50, has_lore_t4=True)
            52
        """
        shift = self.get_level_shift(has_lore_t4, has_destiny_t4)
        return base_level + shift


@dataclass
class BuildStats:
    """
    Represents character build statistics.

    Attributes:
        effective_level: Character level including shifts
        totals: Dictionary of stat totals {stat_key: value}
    """

    effective_level: int
    totals: dict[str, Decimal] = field(default_factory=dict)

    def copy(self) -> "BuildStats":
        """Create a deep copy of build stats."""
        return BuildStats(
            effective_level=self.effective_level, totals=self.totals.copy()
        )


class AlphaSlotCalculator:
    """
    Calculates Alpha slot effects on character builds.

    Handles level shifts, passive boosts, ED application, and stacking.

    From Effect.cs Mag/BuffedMag calculation and GroupedFx.cs level shift processing.
    """

    @staticmethod
    def apply_alpha_to_build(
        alpha_slot: AlphaSlot,
        build_stats: BuildStats,
        character_level: int,
        archetype_name: str,
        has_lore_t4: bool = False,
        has_destiny_t4: bool = False,
        ed_curve_func: Callable[[float], float] | None = None,
        at_modifier_func: Callable[[str, str, int], float] | None = None,
    ) -> BuildStats:
        """
        Apply Alpha slot effects to build statistics.

        From Effect.cs Mag calculation (lines 401-416) and
        Build.cs build totals aggregation.

        Args:
            alpha_slot: Selected Alpha slot
            build_stats: Current build statistics
            character_level: Character's base level
            archetype_name: Archetype (for modifier lookup)
            has_lore_t4: Whether Lore T4 is slotted
            has_destiny_t4: Whether Destiny T4 is slotted
            ed_curve_func: Function to apply ED curve (from Spec 10)
            at_modifier_func: Function to get AT modifiers (from Spec 16)

        Returns:
            Updated build statistics with Alpha applied

        Raises:
            ValueError: If invalid parameters provided

        Examples:
            >>> alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)
            >>> stats = BuildStats(effective_level=50)
            >>> updated = AlphaSlotCalculator.apply_alpha_to_build(
            ...     alpha, stats, 50, "Scrapper"
            ... )
            >>> updated.effective_level
            51
        """
        if character_level < 1 or character_level > 50:
            raise ValueError(f"Invalid character level: {character_level}")

        updated_stats = build_stats.copy()

        # Step 1: Apply level shift
        level_shift = alpha_slot.get_level_shift(has_lore_t4, has_destiny_t4)
        updated_stats.effective_level = character_level + level_shift

        # Step 2: Apply passive boosts
        for effect in alpha_slot.effects:
            # Skip level shift effects (handled above)
            if effect.effect_type == EffectType.LEVEL_SHIFT:
                continue

            base_mag = effect.magnitude

            # Step 3: Apply Enhancement Diversification
            # CRITICAL: Alpha bonuses ARE subject to ED!
            if effect.ignore_ed or ed_curve_func is None:
                enhanced_mag = base_mag
            else:
                enhanced_mag = Decimal(str(ed_curve_func(float(base_mag))))

            # Step 4: Apply Archetype Modifier
            if at_modifier_func is None:
                at_modifier = Decimal("1.0")
            else:
                at_modifier = Decimal(
                    str(
                        at_modifier_func(
                            archetype_name,
                            effect.modifier_table,
                            updated_stats.effective_level,
                        )
                    )
                )

            final_mag = enhanced_mag * at_modifier

            # Step 5: Add to build totals (additive stacking)
            effect_key = effect.effect_type.value
            if effect_key not in updated_stats.totals:
                updated_stats.totals[effect_key] = Decimal("0")

            updated_stats.totals[effect_key] += final_mag

        return updated_stats

    @staticmethod
    def get_purple_patch_damage_modifier(
        attacker_level: int, target_level: int
    ) -> Decimal:
        """
        Calculate purple patch damage modifier based on level difference.

        The "purple patch" is the level difference damage scaling system.

        Simplified formula for breadth implementation. Full formula in Spec 41.

        Args:
            attacker_level: Effective level (including shifts)
            target_level: Enemy level

        Returns:
            Damage multiplier (1.0 = even level, <1.0 = penalty, >1.0 = bonus)

        Examples:
            >>> # Even level
            >>> AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 50)
            Decimal('1.0')

            >>> # 2 levels above (bonus)
            >>> AlphaSlotCalculator.get_purple_patch_damage_modifier(52, 50)
            Decimal('1.10')

            >>> # 2 levels below (penalty)
            >>> AlphaSlotCalculator.get_purple_patch_damage_modifier(50, 52)
            Decimal('0.80')
        """
        level_diff = attacker_level - target_level

        if level_diff > 0:
            # Attacker higher level: damage bonus
            # +5% per level above target
            return Decimal("1.0") + (Decimal(str(level_diff)) * Decimal("0.05"))
        elif level_diff < 0:
            # Attacker lower level: damage penalty
            # -10% per level below target
            return Decimal("1.0") + (Decimal(str(level_diff)) * Decimal("0.10"))
        else:
            # Even level
            return Decimal("1.0")

    @staticmethod
    def get_purple_patch_tohit_modifier(
        attacker_level: int, target_level: int
    ) -> Decimal:
        """
        Calculate purple patch ToHit modifier based on level difference.

        Args:
            attacker_level: Effective level (including shifts)
            target_level: Enemy level

        Returns:
            ToHit modifier (additive to base 75% ToHit)

        Examples:
            >>> # Even level
            >>> AlphaSlotCalculator.get_purple_patch_tohit_modifier(50, 50)
            Decimal('0.0')

            >>> # 1 level above (bonus)
            >>> AlphaSlotCalculator.get_purple_patch_tohit_modifier(51, 50)
            Decimal('0.05')

            >>> # 1 level below (penalty)
            >>> AlphaSlotCalculator.get_purple_patch_tohit_modifier(50, 51)
            Decimal('-0.075')
        """
        level_diff = attacker_level - target_level

        if level_diff > 0:
            # +5% ToHit per level above target
            return Decimal(str(level_diff)) * Decimal("0.05")
        elif level_diff < 0:
            # -7.5% ToHit per level below target
            return Decimal(str(level_diff)) * Decimal("0.075")
        else:
            return Decimal("0.0")


class AlphaSlotFactory:
    """
    Factory for creating Alpha slot configurations from database data.

    Provides standard Alpha configurations with proper boost values.
    """

    # Standard boost values (before ED) by tier
    BOOST_VALUES = {
        1: Decimal("0.20"),  # T1: 20%
        2: Decimal("0.25"),  # T2: 25%
        3: Decimal("0.28"),  # T3: 28% (Total) or 33% (Partial)
        4: Decimal("0.33"),  # T4: 33%
    }

    @classmethod
    def create_musculature(cls, tier: AlphaTier) -> AlphaSlot:
        """
        Create Musculature Alpha (Damage + Endurance Discount).

        Args:
            tier: Which tier (T1-T4, Core/Radial)

        Returns:
            AlphaSlot configured for Musculature

        Examples:
            >>> alpha = AlphaSlotFactory.create_musculature(AlphaTier.T4_CORE_PARAGON)
            >>> alpha.alpha_type
            <AlphaType.MUSCULATURE: 'musculature'>
            >>> len(alpha.effects)
            2
        """
        effects = []

        # Damage boost (all tiers)
        damage_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
        if tier in [AlphaTier.T3_PARTIAL_CORE_REVAMP, AlphaTier.T4_CORE_PARAGON]:
            damage_mag = Decimal("0.33")  # Focused damage

        effects.append(
            AlphaEffect(
                effect_type=EffectType.DAMAGE_BUFF,
                magnitude=damage_mag,
                modifier_table="Melee_Ones",
                ignore_ed=False,
            )
        )

        # Endurance discount (Radial branches only)
        if "radial" in tier.tier_name.lower():
            end_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.20"))
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.ENDURANCE_DISCOUNT,
                    magnitude=end_mag,
                    modifier_table="Melee_Ones",
                    ignore_ed=False,
                )
            )

        # Level shift effect (T3+ only)
        if tier.provides_shift:
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.LEVEL_SHIFT,
                    magnitude=Decimal("1"),
                    modifier_table="Melee_Ones",
                    ignore_ed=True,
                )
            )

        return AlphaSlot(alpha_type=AlphaType.MUSCULATURE, tier=tier, effects=effects)

    @classmethod
    def create_spiritual(cls, tier: AlphaTier) -> AlphaSlot:
        """
        Create Spiritual Alpha (Recharge + Healing).

        Args:
            tier: Which tier (T1-T4, Core/Radial)

        Returns:
            AlphaSlot configured for Spiritual

        Examples:
            >>> alpha = AlphaSlotFactory.create_spiritual(AlphaTier.T4_CORE_PARAGON)
            >>> alpha.alpha_type
            <AlphaType.SPIRITUAL: 'spiritual'>
        """
        effects = []

        # Recharge boost (all tiers)
        recharge_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
        effects.append(
            AlphaEffect(
                effect_type=EffectType.RECHARGE_TIME,
                magnitude=recharge_mag,
                modifier_table="Melee_Ones",
                ignore_ed=False,
            )
        )

        # Healing boost (Radial branches or T4 Core)
        if "radial" in tier.tier_name.lower() or tier.tier_level == 4:
            heal_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.HEAL,
                    magnitude=heal_mag,
                    modifier_table="Melee_Ones",
                    ignore_ed=False,
                )
            )

        # Level shift effect (T3+ only)
        if tier.provides_shift:
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.LEVEL_SHIFT,
                    magnitude=Decimal("1"),
                    modifier_table="Melee_Ones",
                    ignore_ed=True,
                )
            )

        return AlphaSlot(alpha_type=AlphaType.SPIRITUAL, tier=tier, effects=effects)

    @classmethod
    def create_cardiac(cls, tier: AlphaTier) -> AlphaSlot:
        """
        Create Cardiac Alpha (Endurance Mod + Resistance + Endurance Discount).

        Args:
            tier: Which tier (T1-T4, Core/Radial)

        Returns:
            AlphaSlot configured for Cardiac
        """
        effects = []

        # Endurance modification (all tiers)
        end_mod_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.33"))
        effects.append(
            AlphaEffect(
                effect_type=EffectType.ENDURANCE,
                magnitude=end_mod_mag,
                modifier_table="Melee_Ones",
                ignore_ed=False,
            )
        )

        # Resistance (Core branches)
        if "core" in tier.tier_name.lower() or tier.tier_level == 4:
            res_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.25"))
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.RESISTANCE,
                    magnitude=res_mag,
                    modifier_table="Melee_Ones",
                    ignore_ed=False,
                )
            )

        # Endurance discount (Radial branches)
        if "radial" in tier.tier_name.lower():
            end_disc_mag = cls.BOOST_VALUES.get(tier.tier_level, Decimal("0.20"))
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.ENDURANCE_DISCOUNT,
                    magnitude=end_disc_mag,
                    modifier_table="Melee_Ones",
                    ignore_ed=False,
                )
            )

        # Level shift effect (T3+ only)
        if tier.provides_shift:
            effects.append(
                AlphaEffect(
                    effect_type=EffectType.LEVEL_SHIFT,
                    magnitude=Decimal("1"),
                    modifier_table="Melee_Ones",
                    ignore_ed=True,
                )
            )

        return AlphaSlot(alpha_type=AlphaType.CARDIAC, tier=tier, effects=effects)
