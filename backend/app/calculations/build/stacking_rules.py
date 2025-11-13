"""
Buff Stacking Rules - Effect aggregation and stacking logic

Implements MidsReborn's GroupedFx.cs and Build.cs stacking behavior:
- 6 stacking modes (additive, multiplicative, best value)
- Rule of 5 for set bonuses
- FxIdentifier for effect grouping
- GroupedEffect aggregation

Based on Spec 25: docs/midsreborn/calculations/25-buff-stacking-rules.md
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from ..core.effect import Effect
from ..core.effect_types import EffectType
from ..core.enums import PvMode, Stacking, ToWho


class StackingMode(Enum):
    """
    How multiple instances of the same buff combine.

    Maps to determined behavior from GroupedFx.cs stacking logic.
    """

    ADDITIVE = "additive"  # Sum all magnitudes (most common)
    MULTIPLICATIVE = "multiplicative"  # Multiply (1+mag) factors
    BEST_VALUE = "best_value"  # Take maximum magnitude only
    IGNORE = "ignore"  # Deprecated, treated as BEST_VALUE
    STACK = "stack"  # Same as ADDITIVE
    REPLACE = "replace"  # New value replaces old


@dataclass(frozen=True)
class FxIdentifier:
    """
    Uniquely identifies a buff/debuff type for grouping.

    Maps to GroupedFx.FxId struct (GroupedFx.cs lines 82-98).

    Effects must match ALL fields to be grouped together:
    - Defense(Smashing) != Defense(Lethal) (different damage_type)
    - Self buff != Team buff (different target)
    """

    effect_type: EffectType
    damage_type: str | None
    mez_type: str | None
    modifies_type: EffectType | None
    target: ToWho
    pv_mode: PvMode
    summon_id: int
    duration: float
    ignore_scaling: bool

    def __hash__(self) -> int:
        """Make hashable for use as dict key."""
        return hash(
            (
                self.effect_type,
                self.damage_type,
                self.mez_type,
                self.modifies_type,
                self.target,
                self.pv_mode,
                self.summon_id,
                self.duration,
                self.ignore_scaling,
            )
        )


@dataclass
class GroupedEffect:
    """
    Aggregated effect after stacking.

    Maps to GroupedFx class (GroupedFx.cs lines 111-118).

    Attributes:
        identifier: FxIdentifier for this group
        base_magnitude: Sum of base magnitudes
        enhanced_magnitude: Final magnitude after stacking
        included_effects: Source effect unique_ids
        is_enhancement: From enhancement special
        is_aggregated: Multiple effects combined
        stacking_mode: How effects were combined
    """

    identifier: FxIdentifier
    base_magnitude: float
    enhanced_magnitude: float
    included_effects: list[int]
    is_enhancement: bool
    is_aggregated: bool
    stacking_mode: StackingMode

    def __str__(self) -> str:
        """Format for display."""
        sign = "+" if self.enhanced_magnitude >= 0 else ""
        percent = self.enhanced_magnitude * 100
        return f"{sign}{percent:.2f}% {self.identifier.effect_type.value}"


class BuffStackingCalculator:
    """
    Handles buff/debuff stacking logic.

    Maps to GroupedFx and Build classes from MidsReborn.

    Usage:
        calc = BuffStackingCalculator(rule_of_5_enabled=True)
        grouped = calc.group_effects(all_effects)
        total_defense = calc.get_stat_total(grouped, EffectType.DEFENSE)
    """

    def __init__(self, rule_of_5_enabled: bool = True):
        """
        Initialize calculator.

        Args:
            rule_of_5_enabled: Apply Rule of 5 to set bonuses
        """
        self.rule_of_5_enabled = rule_of_5_enabled
        self.set_bonus_counts: dict[int, int] = defaultdict(int)

        # Stacking mode lookup table
        # From GroupedFx.cs and Effect.cs behavior analysis
        self._stacking_modes: dict[EffectType, StackingMode] = {
            EffectType.DEFENSE: StackingMode.ADDITIVE,
            EffectType.RESISTANCE: StackingMode.ADDITIVE,
            EffectType.RECHARGE_TIME: StackingMode.ADDITIVE,
            EffectType.ACCURACY: StackingMode.ADDITIVE,
            EffectType.TO_HIT: StackingMode.ADDITIVE,
            EffectType.RECOVERY: StackingMode.ADDITIVE,
            EffectType.REGENERATION: StackingMode.ADDITIVE,
            EffectType.ENDURANCE_DISCOUNT: StackingMode.ADDITIVE,
            EffectType.HIT_POINTS: StackingMode.ADDITIVE,
            EffectType.SPEED_RUNNING: StackingMode.ADDITIVE,
            EffectType.SPEED_FLYING: StackingMode.ADDITIVE,
            EffectType.SPEED_JUMPING: StackingMode.ADDITIVE,
            EffectType.MEZ: StackingMode.ADDITIVE,
            EffectType.MEZ_RESIST: StackingMode.ADDITIVE,
            EffectType.DAMAGE_BUFF: StackingMode.MULTIPLICATIVE,
        }

    def determine_stacking_mode(
        self, effect_type: EffectType, stacking_flag: Stacking
    ) -> StackingMode:
        """
        Determine how this effect type stacks.

        From GroupedFx.cs stacking determination logic.

        Args:
            effect_type: Type of effect
            stacking_flag: Stacking flag from effect data

        Returns:
            Stacking mode to use

        Examples:
            >>> calc = BuffStackingCalculator()
            >>> calc.determine_stacking_mode(EffectType.DEFENSE, Stacking.YES)
            <StackingMode.ADDITIVE: 'additive'>
            >>> calc.determine_stacking_mode(EffectType.DEFENSE, Stacking.NO)
            <StackingMode.BEST_VALUE: 'best_value'>
        """
        # Check stacking flag first
        if stacking_flag == Stacking.NO:
            return StackingMode.BEST_VALUE
        elif stacking_flag == Stacking.REPLACE:
            return StackingMode.REPLACE

        # Look up effect type in table
        return self._stacking_modes.get(effect_type, StackingMode.ADDITIVE)

    def apply_stacking(self, effects: list[Effect], mode: StackingMode) -> float:
        """
        Apply stacking rules to calculate total magnitude.

        From GroupedFx.cs lines 130-184.

        Args:
            effects: List of effects to stack
            mode: Stacking mode to use

        Returns:
            Final stacked magnitude

        Raises:
            ValueError: If effects list is empty

        Examples:
            >>> effects = [Effect(..., magnitude=0.10), Effect(..., magnitude=0.05)]
            >>> calc.apply_stacking(effects, StackingMode.ADDITIVE)
            0.15
        """
        if not effects:
            raise ValueError("Cannot apply stacking to empty effect list")

        if len(effects) == 1:
            return effects[0].buffed_magnitude or effects[0].magnitude

        if mode == StackingMode.ADDITIVE or mode == StackingMode.STACK:
            # Sum all magnitudes
            return sum(
                e.buffed_magnitude if e.buffed_magnitude is not None else e.magnitude
                for e in effects
            )

        elif mode == StackingMode.MULTIPLICATIVE:
            # (1 + mag1) * (1 + mag2) * ... - 1
            product = 1.0
            for effect in effects:
                mag = (
                    effect.buffed_magnitude
                    if effect.buffed_magnitude is not None
                    else effect.magnitude
                )
                product *= 1.0 + mag
            return product - 1.0

        elif mode == StackingMode.BEST_VALUE or mode == StackingMode.IGNORE:
            # Take maximum magnitude
            return max(
                e.buffed_magnitude if e.buffed_magnitude is not None else e.magnitude
                for e in effects
            )

        elif mode == StackingMode.REPLACE:
            # Last effect wins
            e = effects[-1]
            return e.buffed_magnitude if e.buffed_magnitude is not None else e.magnitude

        else:
            raise ValueError(f"Unknown stacking mode: {mode}")

    def apply_rule_of_five(self, set_bonus_power_id: int) -> bool:
        """
        Check if this set bonus should be included (Rule of 5).

        From Build.cs lines 1321-1370.

        Only first 5 instances of same set bonus count, 6+ suppressed.

        Args:
            set_bonus_power_id: Power ID of set bonus

        Returns:
            True if should include, False if suppressed

        Examples:
            >>> calc = BuffStackingCalculator()
            >>> for i in range(6):
            ...     included = calc.apply_rule_of_five(12345)
            ...     print(f"Instance {i+1}: {included}")
            Instance 1: True
            Instance 2: True
            Instance 3: True
            Instance 4: True
            Instance 5: True
            Instance 6: False
        """
        if not self.rule_of_5_enabled:
            return True  # Always include if rule disabled

        # Increment counter for this power ID
        self.set_bonus_counts[set_bonus_power_id] += 1
        current_count = self.set_bonus_counts[set_bonus_power_id]

        # Include if this is instance 1-5, suppress if 6+
        return current_count < 6

    def filter_set_bonuses(self, effects: list[Effect]) -> list[Effect]:
        """
        Apply Rule of 5 to set bonus effects.

        From Build.cs GetSetBonusVirtualPower() method.

        Args:
            effects: All effects including set bonuses

        Returns:
            Filtered list with 6+ instances suppressed
        """
        if not self.rule_of_5_enabled:
            return effects

        # Reset counters
        self.set_bonus_counts.clear()

        filtered = []
        for effect in effects:
            # Only apply Rule of 5 to set bonuses
            if not hasattr(effect, "source_type") or effect.source_type != "set_bonus":
                filtered.append(effect)
                continue

            # Check if this instance should be included
            power_id = getattr(effect, "source_power_id", None)
            if power_id is None:
                filtered.append(effect)  # No power ID, include by default
                continue

            if self.apply_rule_of_five(power_id):
                filtered.append(effect)
            # else: suppress (don't add to filtered list)

        return filtered

    def create_identifier(self, effect: Effect) -> FxIdentifier:
        """
        Create FxIdentifier for grouping.

        From GroupedFx.cs FxId struct creation.

        Args:
            effect: Effect to create identifier for

        Returns:
            FxIdentifier for grouping

        Examples:
            >>> effect = Effect(unique_id=1, effect_type=EffectType.DEFENSE, ...)
            >>> calc.create_identifier(effect)
            FxIdentifier(effect_type=<EffectType.DEFENSE>, ...)
        """
        return FxIdentifier(
            effect_type=effect.effect_type,
            damage_type=effect.damage_type.value if effect.damage_type else None,
            mez_type=effect.mez_type.value if effect.mez_type else None,
            modifies_type=effect.et_modifies,
            target=effect.to_who,
            pv_mode=effect.pv_mode,
            summon_id=effect.summon_id,
            duration=effect.duration,
            ignore_scaling=effect.ignore_scaling,
        )

    def group_effects(self, effects: list[Effect]) -> list[GroupedEffect]:
        """
        Group effects by identifier and apply stacking rules.

        Main entry point for buff stacking calculation.
        From GroupedFx.cs GroupEffects() method.

        Args:
            effects: All effects to group and stack

        Returns:
            List of grouped effects with combined magnitudes

        Examples:
            >>> effects = [
            ...     Effect(unique_id=1, effect_type=EffectType.DEFENSE, magnitude=0.10),
            ...     Effect(unique_id=2, effect_type=EffectType.DEFENSE, magnitude=0.05),
            ... ]
            >>> grouped = calc.group_effects(effects)
            >>> len(grouped)
            1
            >>> grouped[0].enhanced_magnitude
            0.15
        """
        if not effects:
            return []

        # Phase 1: Apply Rule of 5 to set bonuses
        filtered_effects = self.filter_set_bonuses(effects)

        # Phase 2: Group by FxIdentifier
        groups: dict[FxIdentifier, list[Effect]] = defaultdict(list)
        for effect in filtered_effects:
            fx_id = self.create_identifier(effect)
            groups[fx_id].append(effect)

        # Phase 3: Apply stacking to each group
        grouped_effects = []
        for fx_id, effect_list in groups.items():
            # Determine stacking mode (use first effect's flag)
            mode = self.determine_stacking_mode(
                fx_id.effect_type, effect_list[0].stacking
            )

            # Calculate stacked magnitude
            try:
                total_magnitude = self.apply_stacking(effect_list, mode)
            except ValueError as e:
                # Should not happen since we filtered empty lists above
                print(f"Error stacking effects for {fx_id}: {e}")
                continue

            # Create grouped effect
            grouped = GroupedEffect(
                identifier=fx_id,
                base_magnitude=sum(e.magnitude for e in effect_list),
                enhanced_magnitude=total_magnitude,
                included_effects=[e.unique_id for e in effect_list],
                is_enhancement=effect_list[0].is_enhancement_effect,
                is_aggregated=(len(effect_list) > 1),
                stacking_mode=mode,
            )
            grouped_effects.append(grouped)

        return grouped_effects

    def get_stat_total(
        self,
        grouped_effects: list[GroupedEffect],
        effect_type: EffectType,
        damage_type: str | None = None,
    ) -> float:
        """
        Get total magnitude for specific stat.

        Args:
            grouped_effects: All grouped effects from build
            effect_type: Stat to query
            damage_type: Specific damage type (if applicable)

        Returns:
            Total magnitude for this stat (0 if not found)

        Examples:
            >>> grouped = calc.group_effects(effects)
            >>> calc.get_stat_total(grouped, EffectType.DEFENSE, "All")
            0.15
        """
        total = 0.0
        for grouped in grouped_effects:
            if grouped.identifier.effect_type == effect_type:
                # Check damage type if specified
                if damage_type is not None:
                    if grouped.identifier.damage_type != damage_type:
                        continue
                total += grouped.enhanced_magnitude

        return total

    def calculate_build_totals(
        self,
        power_effects: list[Effect],
        set_bonus_effects: list[Effect],
        incarnate_effects: list[Effect] | None = None,
    ) -> list[GroupedEffect]:
        """
        Calculate total buffs/debuffs for entire build.

        From Build.cs build totals aggregation.

        Args:
            power_effects: Effects from powers (toggles, clicks)
            set_bonus_effects: Effects from enhancement sets
            incarnate_effects: Effects from incarnate powers

        Returns:
            List of grouped effects representing build totals

        Examples:
            >>> calc = BuffStackingCalculator()
            >>> grouped = calc.calculate_build_totals(
            ...     power_effects=[...],
            ...     set_bonus_effects=[...],
            ...     incarnate_effects=[...]
            ... )
        """
        # Combine all effects
        all_effects = []
        all_effects.extend(power_effects)
        all_effects.extend(set_bonus_effects)
        if incarnate_effects:
            all_effects.extend(incarnate_effects)

        # Group and stack
        return self.group_effects(all_effects)
