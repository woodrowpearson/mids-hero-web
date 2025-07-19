"""
Test game logic and rule validation.
"""
from sqlalchemy.orm import Session

from app.models import (
    Archetype,
    Enhancement,
    Power,
    PowerEnhancementCompatibility,
    PowerPrerequisite,
    Powerset,
)


class TestGameRules:
    """Test City of Heroes game rules and mechanics."""

    def test_power_level_progression(self, db: Session):
        """Test that power levels follow valid progression rules."""
        # Powers should be available at specific levels based on tier
        issues = []

        # Primary/Secondary power level rules
        primary_secondary_levels = [1, 1, 2, 6, 8, 12, 18, 26, 32]

        powersets = db.query(Powerset).filter(
            Powerset.set_type.in_(['Primary', 'Secondary'])
        ).all()

        for powerset in powersets:
            powers = db.query(Power).filter(
                Power.powerset_id == powerset.id
            ).order_by(Power.level_available).all()

            if len(powers) > 9:
                issues.append(f"{powerset.name} has more than 9 powers: {len(powers)}")

            # Check level progression
            for i, power in enumerate(powers[:9]):
                expected_level = primary_secondary_levels[i]
                if power.level_available != expected_level:
                    # Some powers can be taken earlier with prerequisites
                    prereqs = db.query(PowerPrerequisite).filter(
                        PowerPrerequisite.power_id == power.id
                    ).count()

                    if prereqs == 0 and power.level_available < expected_level:
                        issues.append(
                            f"{powerset.name}.{power.name} available at {power.level_available}, "
                            f"expected {expected_level}"
                        )

        assert not issues, f"Power level progression issues: {issues}"

    def test_power_prerequisites(self, db: Session):
        """Test that power prerequisites are valid."""
        issues = []

        prerequisites = db.query(PowerPrerequisite).all()

        for prereq in prerequisites:
            power = db.query(Power).filter(Power.id == prereq.power_id).first()
            required = db.query(Power).filter(Power.id == prereq.required_power_id).first()

            if not power or not required:
                continue

            # Required power must be in same powerset or a pool power
            if power.powerset_id != required.powerset_id:
                required_ps = db.query(Powerset).filter(
                    Powerset.id == required.powerset_id
                ).first()

                if required_ps and required_ps.set_type != 'Pool':
                    issues.append(
                        f"{power.name} requires {required.name} from different powerset"
                    )

            # Required power must be available at lower level
            if required.level_available >= power.level_available:
                issues.append(
                    f"{power.name} (level {power.level_available}) requires "
                    f"{required.name} (level {required.level_available})"
                )

        assert not issues, f"Prerequisite issues: {issues}"

    def test_max_slot_limits(self, db: Session):
        """Test that powers respect slot limits."""
        # Most powers can have 6 slots max
        over_slotted = db.query(Power).filter(Power.max_slots > 6).all()

        issues = []
        for power in over_slotted:
            # Some special powers might have different limits
            if 'inherent' not in power.name.lower():
                issues.append(f"{power.name} has max_slots={power.max_slots}")

        assert not issues, f"Powers exceeding 6 slot limit: {issues}"

    def test_archetype_modifiers(self, db: Session):
        """Test that archetype modifiers are within valid ranges."""
        archetypes = db.query(Archetype).all()

        issues = []
        for arch in archetypes:
            # Check scalar values are reasonable (0.5 to 2.0 range)
            scalars = ['damage_scalar', 'defense_scalar', 'hit_points_scalar']

            for scalar in scalars:
                value = getattr(arch, scalar, None)
                if value is not None:
                    if value < 0.5 or value > 2.0:
                        issues.append(
                            f"{arch.name}.{scalar}={value} outside normal range"
                        )

            # Check hit points progression
            if arch.hit_points_max <= arch.hit_points_base:
                issues.append(
                    f"{arch.name} HP max ({arch.hit_points_max}) <= "
                    f"base ({arch.hit_points_base})"
                )

        assert not issues, f"Archetype modifier issues: {issues}"

    def test_enhancement_restrictions(self, db: Session):
        """Test enhancement restrictions and allowed types."""
        # Check that powers only allow appropriate enhancement types
        power_enhancements = db.query(PowerEnhancementCompatibility).all()

        valid_enhancement_types = [
            'Accuracy', 'Damage', 'Defense', 'Resistance',
            'Endurance', 'Recharge', 'Heal', 'Hold',
            'Immobilize', 'Stun', 'Sleep', 'Fear',
            'Confuse', 'Taunt', 'ToHit', 'Range',
            'Fly', 'Jump', 'Run', 'Knockback'
        ]

        issues = []
        for pe in power_enhancements:
            if pe.enhancement_type not in valid_enhancement_types:
                power = db.query(Power).filter(Power.id == pe.power_id).first()
                issues.append(
                    f"{power.name if power else pe.power_id} allows "
                    f"invalid enhancement type: {pe.enhancement_type}"
                )

        assert not issues, f"Invalid enhancement types: {issues}"

    def test_pool_power_restrictions(self, db: Session):
        """Test pool power availability and restrictions."""
        pool_powersets = db.query(Powerset).filter(
            Powerset.set_type == 'Pool'
        ).all()

        issues = []
        for pool in pool_powersets:
            powers = db.query(Power).filter(
                Power.powerset_id == pool.id
            ).order_by(Power.level_available).all()

            # Pool powers typically have 5 powers max
            if len(powers) > 5:
                issues.append(f"Pool {pool.name} has {len(powers)} powers (max 5)")

            # First two powers should be available early (level 4)
            for _i, power in enumerate(powers[:2]):
                if power.level_available > 4:
                    issues.append(
                        f"Pool power {pool.name}.{power.name} not available "
                        f"until level {power.level_available}"
                    )

        assert not issues, f"Pool power issues: {issues}"

    def test_epic_power_restrictions(self, db: Session):
        """Test epic/ancillary power restrictions."""
        epic_powersets = db.query(Powerset).filter(
            Powerset.set_type == 'Epic'
        ).all()

        issues = []
        for epic in epic_powersets:
            powers = db.query(Power).filter(
                Power.powerset_id == epic.id
            ).all()

            # Epic powers should not be available before level 35
            for power in powers:
                if power.level_available < 35:
                    issues.append(
                        f"Epic power {epic.name}.{power.name} available "
                        f"at level {power.level_available} (min 35)"
                    )

        assert not issues, f"Epic power issues: {issues}"

    def test_inherent_power_configuration(self, db: Session):
        """Test inherent powers are properly configured."""
        inherent_powersets = db.query(Powerset).filter(
            Powerset.set_type == 'Inherent'
        ).all()

        issues = []
        for inherent in inherent_powersets:
            powers = db.query(Power).filter(
                Power.powerset_id == inherent.id
            ).all()

            for power in powers:
                # Inherent powers typically can't be slotted
                if power.max_slots > 1 and power.name not in ['Health', 'Stamina']:
                    issues.append(
                        f"Inherent power {power.name} has {power.max_slots} slots"
                    )

                # Should be available at specific levels
                if power.name == 'Rest' and power.level_available != 1:
                    issues.append("Rest should be available at level 1")
                elif power.name == 'Sprint' and power.level_available != 1:
                    issues.append("Sprint should be available at level 1")

        assert not issues, f"Inherent power issues: {issues}"

    def test_powerset_archetype_compatibility(self, db: Session):
        """Test that powersets are assigned to appropriate archetypes."""
        # Example: Blaster should have ranged primary, support secondary
        archetype_rules = {
            'Blaster': {'primary': 'Ranged', 'secondary': 'Support'},
            'Scrapper': {'primary': 'Melee', 'secondary': 'Defense'},
            'Defender': {'primary': 'Support', 'secondary': 'Ranged'},
            'Controller': {'primary': 'Control', 'secondary': 'Support'},
            'Tanker': {'primary': 'Defense', 'secondary': 'Melee'},
        }

        issues = []
        for arch_name, _rules in archetype_rules.items():
            archetype = db.query(Archetype).filter(
                Archetype.name == arch_name
            ).first()

            if not archetype:
                continue

            # Check primary powersets
            primaries = db.query(Powerset).filter(
                Powerset.archetype_id == archetype.id,
                Powerset.set_type == 'Primary'
            ).all()

            # This is a simplified check - would need category metadata
            # for full validation
            if not primaries:
                issues.append(f"{arch_name} has no primary powersets")

        # Basic check that each archetype has both primary and secondary
        for archetype in db.query(Archetype).all():
            primary_count = db.query(Powerset).filter(
                Powerset.archetype_id == archetype.id,
                Powerset.set_type == 'Primary'
            ).count()

            secondary_count = db.query(Powerset).filter(
                Powerset.archetype_id == archetype.id,
                Powerset.set_type == 'Secondary'
            ).count()

            if primary_count == 0:
                issues.append(f"{archetype.name} has no primary powersets")
            if secondary_count == 0:
                issues.append(f"{archetype.name} has no secondary powersets")

        assert not issues, f"Powerset compatibility issues: {issues}"


class TestEnhancementSetBonuses:
    """Test enhancement set bonus rules."""

    def test_set_bonus_thresholds(self, db: Session):
        """Test that set bonuses follow the 2-6 piece rule."""
        from app.models import SetBonus

        set_bonuses = db.query(SetBonus).all()

        issues = []
        for bonus in set_bonuses:
            if bonus.bonus_count < 2 or bonus.bonus_count > 6:
                issues.append(
                    f"Set {bonus.enhancement_set_id} has bonus at "
                    f"{bonus.bonus_count} pieces"
                )

        assert not issues, f"Invalid set bonus thresholds: {issues}"

    def test_set_bonus_progression(self, db: Session):
        """Test that set bonuses increase with more pieces."""
        from app.models import EnhancementSet, SetBonus

        enhancement_sets = db.query(EnhancementSet).all()

        issues = []
        for enh_set in enhancement_sets:
            bonuses = db.query(SetBonus).filter(
                SetBonus.enhancement_set_id == enh_set.id
            ).order_by(SetBonus.bonus_count).all()

            # Check that bonuses exist at expected counts
            bonus_counts = [b.bonus_count for b in bonuses]

            # Most sets have bonuses at 2, 3, 4, 5, 6 pieces
            # Some may skip certain counts
            if bonuses and max(bonus_counts) > 6:
                issues.append(f"{enh_set.name} has bonuses beyond 6 pieces")

            if bonuses and min(bonus_counts) < 2:
                issues.append(f"{enh_set.name} has bonuses before 2 pieces")

        assert not issues, f"Set bonus progression issues: {issues}"

    def test_unique_enhancements_per_set(self, db: Session):
        """Test that each enhancement set has unique enhancements."""
        from app.models import EnhancementSet

        enhancement_sets = db.query(EnhancementSet).all()

        issues = []
        for enh_set in enhancement_sets:
            enhancements = db.query(Enhancement).filter(
                Enhancement.enhancement_set_id == enh_set.id
            ).all()

            # Check for reasonable number of enhancements per set
            if len(enhancements) < 3:
                issues.append(f"{enh_set.name} has only {len(enhancements)} enhancements")
            elif len(enhancements) > 6:
                issues.append(f"{enh_set.name} has {len(enhancements)} enhancements (>6)")

            # Check for duplicate names within set
            names = [e.name for e in enhancements]
            if len(names) != len(set(names)):
                issues.append(f"{enh_set.name} has duplicate enhancement names")

        assert not issues, f"Enhancement set composition issues: {issues}"
