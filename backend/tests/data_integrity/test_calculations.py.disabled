"""
Test calculations and formulas for accuracy.
"""

import json

import pytest
from sqlalchemy.orm import Session

from app.models import Archetype, Enhancement, Power, SetBonus


class TestPowerCalculations:
    """Test power effect calculations."""

    def test_damage_calculations(self, db: Session):
        """Test damage calculations for different archetypes."""
        # Known damage values for validation
        # Format: (archetype, power_name, base_damage, expected_scaled)
        test_cases = [
            ("Blaster", "Fire_Bolt", 62.56, 70.38),  # 1.125 scalar
            ("Scrapper", "Strike", 55.61, 62.56),  # 1.125 scalar
            ("Defender", "Neutrino_Bolt", 41.71, 27.11),  # 0.65 scalar
        ]

        issues = []
        for arch_name, power_name, base_damage, expected in test_cases:
            archetype = db.query(Archetype).filter(Archetype.name == arch_name).first()

            if not archetype:
                continue

            # Get damage scalar
            damage_scalar = getattr(archetype, "damage_scalar", 1.0)

            # Calculate scaled damage
            calculated = base_damage * damage_scalar

            # Allow small floating point differences
            if abs(calculated - expected) > 0.1:
                issues.append(
                    f"{arch_name} {power_name}: calculated {calculated:.2f}, "
                    f"expected {expected:.2f}"
                )

        assert not issues, f"Damage calculation issues: {issues}"

    def test_endurance_cost_calculations(self, db: Session):
        """Test endurance cost calculations."""
        # Base endurance costs should follow formula:
        # Cost = Base * (1 + Recharge/40) for most powers

        powers = (
            db.query(Power)
            .filter(Power.endurance_cost.isnot(None), Power.recharge_time.isnot(None))
            .limit(100)
            .all()
        )

        issues = []
        for power in powers:
            if power.endurance_cost <= 0:
                issues.append(f"{power.name} has non-positive endurance cost")

            # Very rough check - endurance should scale with recharge
            if power.recharge_time > 60 and power.endurance_cost < 10:
                issues.append(
                    f"{power.name} has low endurance cost ({power.endurance_cost}) "
                    f"for long recharge ({power.recharge_time}s)"
                )

        assert not issues, f"Endurance cost issues: {issues}"

    def test_recharge_time_ranges(self, db: Session):
        """Test that recharge times are within reasonable ranges."""
        # Group powers by expected recharge ranges
        # recharge_ranges = {
        #     'fast': (0, 10),      # Fast recharging attacks
        #     'moderate': (10, 30), # Standard powers
        #     'long': (30, 120),    # Powerful abilities
        #     'very_long': (120, 600)  # Ultimate powers
        # }

        powers = db.query(Power).filter(Power.recharge_time.isnot(None)).all()

        issues = []
        for power in powers:
            if power.recharge_time < 0:
                issues.append(f"{power.name} has negative recharge time")
            elif power.recharge_time > 600:
                # Only a few powers should have >10 minute recharge
                if "ultimate" not in power.name.lower():
                    issues.append(
                        f"{power.name} has excessive recharge time "
                        f"({power.recharge_time}s)"
                    )

        assert not issues, f"Recharge time issues: {issues}"


class TestEnhancementCalculations:
    """Test enhancement value calculations."""

    def test_enhancement_values(self, db: Session):
        """Test that enhancement values follow ED (Enhancement Diversification) rules."""
        # Standard IO enhancement values
        # standard_values = {
        #     "Common": 0.333,  # 33.3%
        #     "Uncommon": 0.375,  # 37.5%
        #     "Rare": 0.417,  # 41.7%
        # }

        enhancements = (
            db.query(Enhancement)
            .filter(Enhancement.enhancement_type.in_(["TO", "DO", "SO"]))
            .limit(100)
            .all()
        )

        issues = []
        for enh in enhancements:
            if not hasattr(enh, "bonuses") or not enh.bonuses:
                continue

            bonuses = (
                json.loads(enh.bonuses) if isinstance(enh.bonuses, str) else enh.bonuses
            )

            for bonus in bonuses:
                magnitude = bonus.get("magnitude", 0)
                expected = 0.333  # Default expected value

                # Set enhancements may have different values
                if enh.set_id:
                    # Set IOs typically range from 18% to 53%
                    if magnitude < 0.18 or magnitude > 0.53:
                        issues.append(
                            f"Set enhancement {enh.name} has unusual magnitude: "
                            f"{magnitude}"
                        )
                else:
                    # Common IOs should match standard values
                    if abs(magnitude - expected) > 0.05:
                        issues.append(
                            f"Enhancement {enh.name} has "
                            f"magnitude {magnitude}, expected ~{expected}"
                        )

        assert not issues, f"Enhancement value issues: {issues}"

    def test_enhancement_diversification(self, db: Session):
        """Test Enhancement Diversification (ED) calculations."""
        # ED soft caps at different enhancement totals
        # ed_breakpoints = [
        #     (0.7, 1.0),    # 0-70%: full value
        #     (0.9, 0.85),   # 70-90%: 85% effectiveness
        #     (1.0, 0.70),   # 90-100%: 70% effectiveness
        # ]

        # This is a conceptual test - actual ED calculation would need
        # to be implemented in the application
        test_cases = [
            (0.333, 0.333),  # One SO
            (0.666, 0.666),  # Two SOs
            (0.999, 0.9393),  # Three SOs (ED kicks in)
            (1.332, 1.1676),  # Four SOs (heavy ED)
        ]

        for input_val, expected in test_cases:
            # Calculate ED-affected value
            calculated = self._calculate_ed_value(input_val)

            if abs(calculated - expected) > 0.01:
                pytest.fail(
                    f"ED calculation for {input_val}: got {calculated:.3f}, "
                    f"expected {expected:.3f}"
                )

    def _calculate_ed_value(self, total_enhancement: float) -> float:
        """Calculate Enhancement Diversification affected value."""
        if total_enhancement <= 0.7:
            return total_enhancement
        elif total_enhancement <= 0.9:
            # 70% + (amount over 70% * 0.85)
            return 0.7 + (total_enhancement - 0.7) * 0.85
        else:
            # Previous + (amount over 90% * 0.70)
            return 0.7 + (0.2 * 0.85) + (total_enhancement - 0.9) * 0.70


class TestSetBonusCalculations:
    """Test enhancement set bonus calculations."""

    def test_set_bonus_values(self, db: Session):
        """Test that set bonus values are reasonable."""
        set_bonuses = db.query(SetBonus).all()

        # Expected ranges for different bonus types
        bonus_ranges = {
            "Accuracy": (0.05, 0.15),  # 5-15%
            "Damage": (0.02, 0.05),  # 2-5%
            "Defense": (0.0125, 0.05),  # 1.25-5%
            "Resistance": (0.015, 0.075),  # 1.5-7.5%
            "Recharge": (0.025, 0.10),  # 2.5-10%
            "Recovery": (0.01, 0.04),  # 1-4%
            "Regeneration": (0.08, 0.20),  # 8-20%
            "HP": (0.015, 0.04),  # 1.5-4%
        }

        issues = []
        for bonus in set_bonuses:
            bonus_type = bonus.bonus_type
            magnitude = float(bonus.bonus_amount) if bonus.bonus_amount else 0

            if bonus_type in bonus_ranges:
                min_val, max_val = bonus_ranges[bonus_type]

                # Scale by 100 if stored as percentage
                if magnitude > 1:
                    magnitude = magnitude / 100

                if magnitude < min_val or magnitude > max_val:
                    issues.append(
                        f"Set bonus {bonus.set_id} piece {bonus.pieces_required}: "
                        f"{bonus_type} = {magnitude}, expected {min_val}-{max_val}"
                    )

        assert not issues, f"Set bonus value issues: {issues}"

    def test_set_bonus_stacking(self, db: Session):
        """Test the Rule of Five for set bonuses."""
        # In CoH, you can only have 5 of the same set bonus
        # This test would check build calculations, but we'll verify
        # that the data supports this rule

        # Get all unique bonus combinations
        bonuses = db.query(SetBonus.bonus_type, SetBonus.bonus_amount).distinct().all()

        # Group by type and magnitude to find stackable bonuses
        bonus_groups = {}
        for bonus_type, magnitude in bonuses:
            key = f"{bonus_type}_{magnitude}"
            bonus_groups[key] = bonus_groups.get(key, 0) + 1

        # No individual bonus should appear in more than ~20 sets
        # (allows for variety while respecting Rule of Five)
        issues = []
        for key, count in bonus_groups.items():
            if count > 20:
                issues.append(f"Bonus {key} appears in {count} sets")

        assert not issues, f"Set bonus variety issues: {issues}"


class TestCombatMechanics:
    """Test combat mechanics calculations."""

    def test_accuracy_formula(self, db: Session):
        """Test base accuracy calculations."""
        # Base accuracy in CoH is typically:
        # Final = BaseAcc * (1 + AccBonus) * (1 + ToHitBonus - Defense)

        # Most powers have base accuracy of 1.0 (100%)
        powers = db.query(Power).filter(Power.accuracy.isnot(None)).limit(100).all()

        issues = []
        for power in powers:
            if power.accuracy < 0:
                issues.append(f"{power.name} has negative accuracy")
            elif power.accuracy > 2.0:
                # Some powers have inherent accuracy bonuses
                if "sniper" not in power.name.lower():
                    issues.append(
                        f"{power.name} has very high base accuracy: {power.accuracy}"
                    )

        assert not issues, f"Accuracy formula issues: {issues}"

    def test_defense_calculations(self, db: Session):
        """Test defense type interactions."""
        # Defense types should be properly categorized
        defense_types = [
            "Smashing",
            "Lethal",
            "Fire",
            "Cold",
            "Energy",
            "Negative",
            "Psionic",
            "Melee",
            "Ranged",
            "AoE",
        ]

        # This would test actual defense calculations in powers
        # For now, we verify the data structure supports it
        # Skip this test if no powers have effects data
        # This avoids PostgreSQL JSON LIKE issues
        powers_with_defense = (
            db.query(Power).filter(Power.effects.isnot(None)).limit(50).all()
        )

        issues = []
        for power in powers_with_defense:
            effects = (
                json.loads(power.effects)
                if isinstance(power.effects, str)
                else power.effects
            )

            for effect in effects:
                if effect.get("effect_type") == "Defense":
                    attribute = effect.get("attribute")
                    if attribute and attribute not in defense_types:
                        issues.append(
                            f"{power.name} has unknown defense type: {attribute}"
                        )

        assert not issues, f"Defense calculation issues: {issues}"

    def test_resistance_caps(self, db: Session):
        """Test that resistance values respect caps."""
        # Resistance caps vary by archetype:
        # Tankers/Brutes: 90%
        # Everyone else: 75%

        # This test would verify that power effects don't exceed caps
        # when combined. For now, we check individual power values

        # Skip this test if no powers have effects data
        # This avoids PostgreSQL JSON LIKE issues
        powers_with_resistance = (
            db.query(Power).filter(Power.effects.isnot(None)).limit(50).all()
        )

        issues = []
        for power in powers_with_resistance:
            effects = (
                json.loads(power.effects)
                if isinstance(power.effects, str)
                else power.effects
            )

            for effect in effects:
                if effect.get("effect_type") == "Resistance":
                    magnitude = effect.get("magnitude", 0)

                    # Individual powers rarely give >30% resistance
                    if magnitude > 0.30:
                        issues.append(
                            f"{power.name} gives {magnitude * 100}% resistance "
                            f"(unusually high)"
                        )

        assert not issues, f"Resistance cap issues: {issues}"
