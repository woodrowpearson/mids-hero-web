"""
GroupedFx - Effect grouping and aggregation system

Maps to MidsReborn's GroupedFx class for aggregating effects from multiple sources.
Implements FxId composite key and stacking rules.
"""

from dataclasses import dataclass

from .effect import Effect
from .effect_types import DamageType, EffectType, MezType
from .enums import PvMode, SpecialCase, Stacking, ToWho


@dataclass
class FxId:
    """
    Effect identifier for grouping.

    Maps to MidsReborn's GroupedFx.FxId struct from GroupedFx.cs lines 7-25.
    Effects with identical FxId values are aggregated together.

    This acts as a composite key - effects must match ALL fields to be grouped.
    """

    effect_type: EffectType
    mez_type: MezType | None
    damage_type: DamageType | None
    et_modifies: EffectType | None  # For enhancement effects
    to_who: ToWho
    pv_mode: PvMode
    summon_id: int
    duration: float
    ignore_scaling: bool

    def to_tuple(self) -> tuple:
        """
        Convert to hashable tuple for use as dict key.

        Returns:
            Tuple of all FxId fields
        """
        return (
            self.effect_type,
            self.mez_type,
            self.damage_type,
            self.et_modifies,
            self.to_who,
            self.pv_mode,
            self.summon_id,
            self.duration,
            self.ignore_scaling,
        )

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        if not isinstance(other, FxId):
            return False
        return self.to_tuple() == other.to_tuple()

    def __repr__(self) -> str:
        return (
            f"FxId(type={self.effect_type.name}, "
            f"dmg={self.damage_type.name if self.damage_type else 'None'}, "
            f"mez={self.mez_type.name if self.mez_type else 'None'}, "
            f"to_who={self.to_who.name}, "
            f"pv_mode={self.pv_mode.name})"
        )


@dataclass
class GroupedEffect:
    """
    Aggregated effect group containing summed effects from multiple sources.

    Maps to MidsReborn's GroupedFx class from GroupedFx.cs lines 27-72.
    Contains the aggregated magnitude from all sources with matching FxId.
    """

    fx_id: FxId
    magnitude: float
    alias: str  # Display name like "Defense(Melee)"
    included_effects: list[int]  # Source effect IDs
    is_enhancement: bool
    special_case: SpecialCase
    is_aggregated: bool = False  # True if from multiple sources

    def add_effect(self, effect: Effect, stacking: Stacking) -> None:
        """
        Add another effect to this group using stacking rules.

        Implements MidsReborn's stacking logic from GroupedFx.cs.

        Args:
            effect: Effect to add to this group
            stacking: Stacking mode to apply (YES/STACK/REPLACE/NO)
        """
        if stacking == Stacking.YES or stacking == Stacking.STACK:
            # Additive stacking (most common)
            self.magnitude += effect.get_effective_magnitude()
        elif stacking == Stacking.REPLACE:
            # Replace with new value
            self.magnitude = effect.get_effective_magnitude()
        elif stacking == Stacking.NO:
            # Keep existing, ignore new
            pass

        self.included_effects.append(effect.unique_id)
        self.is_aggregated = len(self.included_effects) > 1

    def __repr__(self) -> str:
        return (
            f"GroupedEffect(alias={self.alias}, "
            f"mag={self.magnitude:.2f}, "
            f"sources={len(self.included_effects)})"
        )


class EffectAggregator:
    """
    Aggregates effects from multiple sources applying stacking rules.

    Maps to MidsReborn's GroupedFx aggregation logic.
    Groups effects by FxId composite key and sums magnitudes.
    """

    def group_effects(self, effects: list[Effect]) -> dict[FxId, GroupedEffect]:
        """
        Group and aggregate effects by FxId.

        Follows MidsReborn's GroupedFx.cs constructor logic at lines 72-106.

        Process:
        1. For each effect, create FxId composite key
        2. If FxId not seen before, create new GroupedEffect
        3. If FxId already exists, add to existing group using stacking rules
        4. Return dictionary of all grouped effects

        Args:
            effects: List of all Effect objects from all sources

        Returns:
            Dictionary keyed by FxId, values are GroupedEffect
        """
        groups: dict[FxId, GroupedEffect] = {}

        for effect in effects:
            # Create FxId for this effect
            fx_id = self._create_fx_id(effect)

            if fx_id not in groups:
                # First effect of this type - create new group
                groups[fx_id] = GroupedEffect(
                    fx_id=fx_id,
                    magnitude=effect.get_effective_magnitude(),
                    alias=effect.get_display_alias(),
                    included_effects=[effect.unique_id],
                    is_enhancement=effect.is_enhancement_effect,
                    special_case=effect.special_case,
                    is_aggregated=False,
                )
            else:
                # Additional effect of same type - aggregate
                groups[fx_id].add_effect(effect, effect.stacking)

        return groups

    def _create_fx_id(self, effect: Effect) -> FxId:
        """
        Create FxId composite key from effect properties.

        Args:
            effect: Effect to create ID for

        Returns:
            FxId for grouping
        """
        return FxId(
            effect_type=effect.effect_type,
            mez_type=effect.mez_type,
            damage_type=effect.damage_type,
            et_modifies=effect.et_modifies,
            to_who=effect.to_who,
            pv_mode=effect.pv_mode,
            summon_id=effect.summon_id,
            duration=effect.duration,
            ignore_scaling=effect.ignore_scaling,
        )

    def apply_archetype_scaling(
        self, groups: dict[FxId, GroupedEffect], at_scales: dict[EffectType, float]
    ) -> dict[FxId, GroupedEffect]:
        """
        Apply archetype-specific scaling to grouped effects.

        Multiplies magnitude by AT scale factor unless ignore_scaling is True.

        Args:
            groups: Grouped effects
            at_scales: AT scale factors per effect type

        Returns:
            New dictionary with scaled grouped effects
        """
        scaled_groups = {}

        for fx_id, group in groups.items():
            # Skip if effect ignores scaling
            if fx_id.ignore_scaling:
                scaled_groups[fx_id] = group
                continue

            # Apply AT scale if available
            if fx_id.effect_type in at_scales:
                scaled_group = GroupedEffect(
                    fx_id=group.fx_id,
                    magnitude=group.magnitude * at_scales[fx_id.effect_type],
                    alias=group.alias,
                    included_effects=group.included_effects.copy(),
                    is_enhancement=group.is_enhancement,
                    special_case=group.special_case,
                    is_aggregated=group.is_aggregated,
                )
                scaled_groups[fx_id] = scaled_group
            else:
                scaled_groups[fx_id] = group

        return scaled_groups

    def apply_caps(
        self, groups: dict[FxId, GroupedEffect], caps: dict[EffectType, float]
    ) -> dict[FxId, GroupedEffect]:
        """
        Apply archetype caps to grouped effects.

        Limits magnitude to archetype-specific maximum values.

        Args:
            groups: Grouped effects
            caps: Maximum values per effect type

        Returns:
            New dictionary with capped grouped effects
        """
        capped_groups = {}

        for fx_id, group in groups.items():
            if fx_id.effect_type in caps:
                cap = caps[fx_id.effect_type]
                capped_magnitude = min(group.magnitude, cap)

                capped_group = GroupedEffect(
                    fx_id=group.fx_id,
                    magnitude=capped_magnitude,
                    alias=group.alias,
                    included_effects=group.included_effects.copy(),
                    is_enhancement=group.is_enhancement,
                    special_case=group.special_case,
                    is_aggregated=group.is_aggregated,
                )
                capped_groups[fx_id] = capped_group
            else:
                capped_groups[fx_id] = group

        return capped_groups

    def get_effects_by_type(
        self, groups: dict[FxId, GroupedEffect], effect_type: EffectType
    ) -> list[GroupedEffect]:
        """
        Filter grouped effects by effect type.

        Convenience method for getting all effects of a specific type.

        Args:
            groups: Grouped effects
            effect_type: Type to filter by

        Returns:
            List of grouped effects matching the type
        """
        return [
            group for fx_id, group in groups.items() if fx_id.effect_type == effect_type
        ]

    def get_total_magnitude(
        self, groups: dict[FxId, GroupedEffect], effect_type: EffectType
    ) -> float:
        """
        Get sum of all magnitudes for an effect type.

        Convenience method for totaling effects (e.g., total defense).

        Args:
            groups: Grouped effects
            effect_type: Type to sum

        Returns:
            Sum of all magnitudes for the effect type
        """
        effects = self.get_effects_by_type(groups, effect_type)
        return sum(effect.magnitude for effect in effects)
