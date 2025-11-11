"""
Test Effect System - Core effect representation and aggregation

Tests based on Spec 01 Section 4 test cases.
Validates Effect class, FxId grouping, and EffectAggregator.
"""

import pytest
from app.calculations.core import (
    Effect,
    EffectType,
    DamageType,
    MezType,
    ToWho,
    PvMode,
    Stacking,
    EffectAggregator
)


class TestEffectCreation:
    """Test Suite: Effect Creation and Basic Properties"""

    def test_effect_basic_properties(self):
        """
        Test 1: Basic damage effect (50 magnitude, 0 duration, 100% probability)

        From Spec 01, Section 4, Test Case 1.
        """
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=50.0,
            damage_type=DamageType.FIRE,
            duration=0.0,
            probability=1.0
        )

        assert effect.effect_type == EffectType.DAMAGE
        assert effect.magnitude == 50.0
        assert effect.damage_type == DamageType.FIRE
        assert effect.duration == 0.0
        assert effect.probability == 1.0
        assert effect.is_permanent()
        assert not effect.is_proc()

    def test_effect_dot_with_probability(self):
        """
        Test 2: DoT effect (10 magnitude, 10s duration, 0.5 probability)

        From Spec 01, Section 4, Test Case 2.
        """
        effect = Effect(
            unique_id=2,
            effect_type=EffectType.DAMAGE,
            magnitude=10.0,
            damage_type=DamageType.TOXIC,
            duration=10.0,
            probability=0.5
        )

        assert effect.magnitude == 10.0
        assert effect.duration == 10.0
        assert effect.probability == 0.5
        assert effect.is_temporary()
        assert effect.is_proc()


class TestEffectAggregation:
    """Test Suite: Effect Grouping and Aggregation"""

    def test_grouping_sum_aggregation(self):
        """
        Test 3: GroupedFx sum aggregation (3 effects → 120 total)

        From Spec 01, Section 4, Test Case 3.
        Three defense effects should sum: 50 + 40 + 30 = 120
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=50.0,
                to_who=ToWho.SELF,
                pv_mode=PvMode.ANY
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=40.0,
                to_who=ToWho.SELF,
                pv_mode=PvMode.ANY
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.DEFENSE,
                magnitude=30.0,
                to_who=ToWho.SELF,
                pv_mode=PvMode.ANY
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        # Should be exactly 1 group (all same type/target/mode)
        assert len(groups) == 1

        # Get the single grouped effect
        grouped = list(groups.values())[0]

        # Verify sum
        assert grouped.magnitude == 120.0
        assert grouped.is_aggregated
        assert len(grouped.included_effects) == 3

    def test_grouping_max_aggregation(self):
        """
        Test 4: GroupedFx max aggregation (3 effects → 50 max)

        From Spec 01, Section 4, Test Case 4.
        With REPLACE stacking, only the last value should be kept.
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=30.0,
                damage_type=DamageType.FIRE,
                stacking=Stacking.REPLACE
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE,
                magnitude=40.0,
                damage_type=DamageType.FIRE,
                stacking=Stacking.REPLACE
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.DAMAGE,
                magnitude=50.0,
                damage_type=DamageType.FIRE,
                stacking=Stacking.REPLACE
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        # Should be exactly 1 group
        assert len(groups) == 1

        # Get the single grouped effect
        grouped = list(groups.values())[0]

        # With REPLACE mode, last value wins
        assert grouped.magnitude == 50.0

    def test_to_who_filtering(self):
        """
        Test 5: ToWho filtering (Self vs Target)

        From Spec 01, Section 4, Test Case 5.
        Effects with different ToWho should create separate groups.
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DEFENSE,
                magnitude=20.0,
                to_who=ToWho.SELF
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DEFENSE,
                magnitude=15.0,
                to_who=ToWho.TARGET
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        # Should be 2 separate groups (different ToWho)
        assert len(groups) == 2

        # Verify each group has correct magnitude
        for fx_id, grouped in groups.items():
            if fx_id.to_who == ToWho.SELF:
                assert grouped.magnitude == 20.0
            elif fx_id.to_who == ToWho.TARGET:
                assert grouped.magnitude == 15.0

    def test_pv_mode_filtering(self):
        """
        Test 6: PvMode filtering (PvE vs PvP)

        From Spec 01, Section 4, Test Case 6.
        Effects with different PvMode should create separate groups.
        """
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=100.0,
                damage_type=DamageType.ENERGY,
                pv_mode=PvMode.PVE
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.DAMAGE,
                magnitude=70.0,
                damage_type=DamageType.ENERGY,
                pv_mode=PvMode.PVP
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        # Should be 2 separate groups (different PvMode)
        assert len(groups) == 2

        # Verify each group has correct magnitude
        for fx_id, grouped in groups.items():
            if fx_id.pv_mode == PvMode.PVE:
                assert grouped.magnitude == 100.0
            elif fx_id.pv_mode == PvMode.PVP:
                assert grouped.magnitude == 70.0


class TestEffectValidation:
    """Test Suite: Effect Property Validation"""

    def test_probability_validation(self):
        """Test probability must be between 0 and 1"""
        with pytest.raises(ValueError, match="Probability must be 0-1"):
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=100.0,
                probability=1.5  # Invalid
            )

        with pytest.raises(ValueError, match="Probability must be 0-1"):
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=100.0,
                probability=-0.1  # Invalid
            )

    def test_duration_validation(self):
        """Test duration cannot be negative"""
        with pytest.raises(ValueError, match="Duration cannot be negative"):
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=100.0,
                duration=-1.0  # Invalid
            )

    def test_scale_validation(self):
        """Test scale must be positive"""
        with pytest.raises(ValueError, match="Scale must be positive"):
            Effect(
                unique_id=1,
                effect_type=EffectType.DAMAGE,
                magnitude=100.0,
                scale=0.0  # Invalid
            )


class TestEffectMethods:
    """Test Suite: Effect Helper Methods"""

    def test_get_effective_magnitude(self):
        """Test effective magnitude returns buffed value if available"""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=15.0,
            buffed_magnitude=25.0  # Enhanced
        )

        assert effect.get_effective_magnitude() == 25.0

    def test_get_effective_magnitude_unbuffed(self):
        """Test effective magnitude returns base value if no buffed value"""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=15.0
        )

        assert effect.get_effective_magnitude() == 15.0

    def test_apply_at_scaling(self):
        """Test archetype scaling application"""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=15.0,
            scale=1.0
        )

        # Apply 0.75 AT scale
        scaled = effect.apply_at_scaling(0.75)
        assert scaled == 11.25

    def test_ignore_scaling(self):
        """Test ignore_scaling bypasses AT modifiers"""
        effect = Effect(
            unique_id=1,
            effect_type=EffectType.DEFENSE,
            magnitude=15.0,
            ignore_scaling=True
        )

        # Even with 0.5 AT scale, should return unchanged
        scaled = effect.apply_at_scaling(0.5)
        assert scaled == 15.0

    def test_get_display_alias(self):
        """Test display name generation"""
        # With damage type
        effect1 = Effect(
            unique_id=1,
            effect_type=EffectType.DAMAGE,
            magnitude=100.0,
            damage_type=DamageType.FIRE
        )
        assert effect1.get_display_alias() == "Damage(Fire)"

        # With mez type
        effect2 = Effect(
            unique_id=2,
            effect_type=EffectType.MEZ,
            magnitude=3.0,
            mez_type=MezType.HOLD
        )
        assert effect2.get_display_alias() == "Mez(Hold)"

        # No aspect
        effect3 = Effect(
            unique_id=3,
            effect_type=EffectType.REGENERATION,
            magnitude=10.0
        )
        assert effect3.get_display_alias() == "Regeneration"


class TestStackingModes:
    """Test Suite: Stacking Mode Behavior"""

    def test_stacking_yes(self):
        """Test YES stacking mode (additive)"""
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.RESISTANCE,
                magnitude=30.0,
                stacking=Stacking.YES
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.RESISTANCE,
                magnitude=20.0,
                stacking=Stacking.YES
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        grouped = list(groups.values())[0]
        assert grouped.magnitude == 50.0  # 30 + 20

    def test_stacking_no(self):
        """Test NO stacking mode (first only)"""
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.RANGE,
                magnitude=50.0,
                stacking=Stacking.NO
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.RANGE,
                magnitude=100.0,
                stacking=Stacking.NO
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        grouped = list(groups.values())[0]
        assert grouped.magnitude == 50.0  # First only

    def test_stacking_replace(self):
        """Test REPLACE stacking mode (last wins)"""
        effects = [
            Effect(
                unique_id=1,
                effect_type=EffectType.SPEED_RUNNING,
                magnitude=10.0,
                stacking=Stacking.REPLACE
            ),
            Effect(
                unique_id=2,
                effect_type=EffectType.SPEED_RUNNING,
                magnitude=20.0,
                stacking=Stacking.REPLACE
            ),
            Effect(
                unique_id=3,
                effect_type=EffectType.SPEED_RUNNING,
                magnitude=15.0,
                stacking=Stacking.REPLACE
            )
        ]

        aggregator = EffectAggregator()
        groups = aggregator.group_effects(effects)

        grouped = list(groups.values())[0]
        assert grouped.magnitude == 15.0  # Last value
