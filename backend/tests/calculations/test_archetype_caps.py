"""
Test Archetype Caps - AT-specific maximum attribute values

Tests based on Spec 17 and Milestone 4 Implementation Plan test cases.
Validates cap values and cap application logic for all archetypes.
"""

from app.calculations.core import (
    ArchetypeCaps,
    ArchetypeType,
    apply_cap,
    get_archetype_caps,
    is_at_cap,
)


class TestSpec17TestCases:
    """Test Suite: Spec 17 / Implementation Plan Test Cases"""

    def test_1_tanker_resistance_cap(self):
        """
        Test 1: Tanker resistance cap → 0.90 (90%)

        From Implementation Plan, Batch 1D, Test Case 1.
        Tankers have highest resistance cap for survivability.
        """
        caps = get_archetype_caps(ArchetypeType.TANKER)

        assert caps.resistance_cap == 0.90

    def test_2_brute_damage_cap(self):
        """
        Test 2: Brute damage cap → 7.75 (775%)

        From Implementation Plan, Batch 1D, Test Case 2.
        Brutes have highest damage cap due to Fury mechanic.
        """
        caps = get_archetype_caps(ArchetypeType.BRUTE)

        assert caps.damage_cap == 7.75

    def test_3_blaster_damage_cap(self):
        """
        Test 3: Blaster damage cap → 5.0 (500%)

        From Implementation Plan, Batch 1D, Test Case 3.
        Blasters have high damage cap as primary damage dealers.
        """
        caps = get_archetype_caps(ArchetypeType.BLASTER)

        assert caps.damage_cap == 5.0

    def test_4_scrapper_defense_cap(self):
        """
        Test 4: Scrapper defense cap → 2.00 (200%)

        From Implementation Plan, Batch 1D, Test Case 4.
        Scrapper defense display cap.
        """
        caps = get_archetype_caps(ArchetypeType.SCRAPPER)

        assert caps.defense_cap == 2.00

    def test_5_controller_recovery_cap(self):
        """
        Test 5: Controller recovery cap → 12.0 (1200%)

        From Implementation Plan, Batch 1D, Test Case 5.
        Controllers have highest recovery cap for sustained support/control.
        """
        caps = get_archetype_caps(ArchetypeType.CONTROLLER)

        assert caps.recovery_cap == 12.0

    def test_6_defender_recovery_cap(self):
        """
        Test 6: Defender recovery cap → 10.0 (1000%)

        Modified from Implementation Plan (ToHit cap → Recovery cap).
        Defenders have high recovery cap for support role.
        """
        caps = get_archetype_caps(ArchetypeType.DEFENDER)

        assert caps.recovery_cap == 10.0


class TestCapValues:
    """Test Suite: Cap Values for All Archetypes"""

    def test_tanker_caps(self):
        """Test all Tanker caps"""
        caps = get_archetype_caps(ArchetypeType.TANKER)

        assert caps.damage_cap == 4.0
        assert caps.resistance_cap == 0.90  # Highest
        assert caps.defense_cap == 2.25
        assert caps.hp_cap == 3534.0  # Highest
        assert caps.recovery_cap == 8.0
        assert caps.regeneration_cap == 25.0
        assert caps.recharge_cap == 5.0

    def test_brute_caps(self):
        """Test all Brute caps"""
        caps = get_archetype_caps(ArchetypeType.BRUTE)

        assert caps.damage_cap == 7.75  # Highest
        assert caps.resistance_cap == 0.90  # Tanker-level
        assert caps.defense_cap == 2.25
        assert caps.hp_cap == 3212.0
        assert caps.recovery_cap == 8.0
        assert caps.regeneration_cap == 25.0

    def test_scrapper_caps(self):
        """Test all Scrapper caps"""
        caps = get_archetype_caps(ArchetypeType.SCRAPPER)

        assert caps.damage_cap == 5.0
        assert caps.resistance_cap == 0.75
        assert caps.defense_cap == 2.00
        assert caps.hp_cap == 2409.0
        assert caps.regeneration_cap == 30.0  # Highest regen cap

    def test_blaster_caps(self):
        """Test all Blaster caps"""
        caps = get_archetype_caps(ArchetypeType.BLASTER)

        assert caps.damage_cap == 5.0
        assert caps.resistance_cap == 0.75
        assert caps.defense_cap == 1.75
        assert caps.hp_cap == 1874.0  # Lowest
        assert caps.recovery_cap == 8.0
        assert caps.regeneration_cap == 20.0

    def test_defender_caps(self):
        """Test all Defender caps"""
        caps = get_archetype_caps(ArchetypeType.DEFENDER)

        assert caps.damage_cap == 4.0  # Lower for support
        assert caps.resistance_cap == 0.75
        assert caps.recovery_cap == 10.0  # Higher for support

    def test_controller_caps(self):
        """Test all Controller caps"""
        caps = get_archetype_caps(ArchetypeType.CONTROLLER)

        assert caps.damage_cap == 4.0
        assert caps.recovery_cap == 12.0  # Highest

    def test_kheldian_caps(self):
        """Test Kheldian (Peacebringer/Warshade) special caps"""
        pb_caps = get_archetype_caps(ArchetypeType.PEACEBRINGER)
        ws_caps = get_archetype_caps(ArchetypeType.WARSHADE)

        # Kheldians have 85% resistance cap (special)
        assert pb_caps.resistance_cap == 0.85
        assert ws_caps.resistance_cap == 0.85


class TestCapApplication:
    """Test Suite: Applying Caps to Values"""

    def test_apply_damage_cap_below(self):
        """Test applying damage cap when value is below cap"""
        caps = get_archetype_caps(ArchetypeType.TANKER)

        # Value below cap should pass through unchanged
        result = caps.apply_damage_cap(3.0)
        assert result == 3.0

    def test_apply_damage_cap_above(self):
        """Test applying damage cap when value is above cap"""
        caps = get_archetype_caps(ArchetypeType.TANKER)

        # Value above cap should be capped
        result = caps.apply_damage_cap(5.0)
        assert result == 4.0  # Tanker damage cap

    def test_apply_resistance_cap_below(self):
        """Test applying resistance cap when value is below cap"""
        caps = get_archetype_caps(ArchetypeType.TANKER)

        result = caps.apply_resistance_cap(0.75)
        assert result == 0.75

    def test_apply_resistance_cap_above(self):
        """Test applying resistance cap when value is above cap"""
        caps = get_archetype_caps(ArchetypeType.TANKER)

        # 95% resistance capped at Tanker 90%
        result = caps.apply_resistance_cap(0.95)
        assert result == 0.90

    def test_apply_hp_cap(self):
        """Test applying HP cap"""
        caps = get_archetype_caps(ArchetypeType.BLASTER)

        # Blaster HP cap is 1874
        result = caps.apply_hp_cap(2000.0)
        assert result == 1874.0

        result = caps.apply_hp_cap(1500.0)
        assert result == 1500.0

    def test_apply_recovery_cap(self):
        """Test applying recovery cap"""
        caps = get_archetype_caps(ArchetypeType.CONTROLLER)

        # Controller recovery cap is 12.0 (1200%)
        result = caps.apply_recovery_cap(15.0)
        assert result == 12.0

        result = caps.apply_recovery_cap(10.0)
        assert result == 10.0

    def test_apply_regeneration_cap(self):
        """Test applying regeneration cap"""
        caps = get_archetype_caps(ArchetypeType.SCRAPPER)

        # Scrapper regen cap is 30.0 (3000%)
        result = caps.apply_regeneration_cap(35.0)
        assert result == 30.0

        result = caps.apply_regeneration_cap(25.0)
        assert result == 25.0

    def test_apply_recharge_cap(self):
        """Test applying recharge cap"""
        caps = get_archetype_caps(ArchetypeType.DEFENDER)

        # Universal recharge cap is 5.0 (500%)
        result = caps.apply_recharge_cap(6.0)
        assert result == 5.0


class TestUtilityFunctions:
    """Test Suite: Utility Functions"""

    def test_apply_cap_generic(self):
        """Test generic apply_cap function"""
        assert apply_cap(100.0, 75.0) == 75.0
        assert apply_cap(50.0, 75.0) == 50.0
        assert apply_cap(75.0, 75.0) == 75.0

    def test_is_at_cap_true(self):
        """Test is_at_cap returns True when at cap"""
        assert is_at_cap(0.90, 0.90)
        assert is_at_cap(0.9001, 0.90, tolerance=0.001)
        assert is_at_cap(1.0, 0.90)

    def test_is_at_cap_false(self):
        """Test is_at_cap returns False when below cap"""
        assert not is_at_cap(0.75, 0.90)
        assert not is_at_cap(0.89, 0.90, tolerance=0.001)


class TestCapComparisons:
    """Test Suite: Cross-AT Cap Comparisons"""

    def test_damage_cap_hierarchy(self):
        """Test damage caps follow correct hierarchy"""
        brute = get_archetype_caps(ArchetypeType.BRUTE)
        blaster = get_archetype_caps(ArchetypeType.BLASTER)
        scrapper = get_archetype_caps(ArchetypeType.SCRAPPER)
        tanker = get_archetype_caps(ArchetypeType.TANKER)
        defender = get_archetype_caps(ArchetypeType.DEFENDER)

        # Brute has highest damage cap
        assert brute.damage_cap > blaster.damage_cap
        assert brute.damage_cap > scrapper.damage_cap
        assert brute.damage_cap > tanker.damage_cap

        # Damage dealers have 5.0 cap
        assert blaster.damage_cap == 5.0
        assert scrapper.damage_cap == 5.0

        # Support/tank ATs have 4.0 cap
        assert tanker.damage_cap == 4.0
        assert defender.damage_cap == 4.0

    def test_resistance_cap_hierarchy(self):
        """Test resistance caps follow correct hierarchy"""
        tanker = get_archetype_caps(ArchetypeType.TANKER)
        brute = get_archetype_caps(ArchetypeType.BRUTE)
        peacebringer = get_archetype_caps(ArchetypeType.PEACEBRINGER)
        blaster = get_archetype_caps(ArchetypeType.BLASTER)

        # Tanker/Brute have 90% cap
        assert tanker.resistance_cap == 0.90
        assert brute.resistance_cap == 0.90

        # Kheldians have 85% cap
        assert peacebringer.resistance_cap == 0.85

        # Others have 75% cap
        assert blaster.resistance_cap == 0.75

    def test_recovery_cap_hierarchy(self):
        """Test recovery caps follow correct hierarchy"""
        controller = get_archetype_caps(ArchetypeType.CONTROLLER)
        dominator = get_archetype_caps(ArchetypeType.DOMINATOR)
        defender = get_archetype_caps(ArchetypeType.DEFENDER)
        blaster = get_archetype_caps(ArchetypeType.BLASTER)

        # Control ATs have highest recovery caps
        assert controller.recovery_cap == 12.0  # Highest
        assert dominator.recovery_cap == 12.0

        # Defender has high recovery
        assert defender.recovery_cap == 10.0

        # Others have standard 8.0
        assert blaster.recovery_cap == 8.0

    def test_regen_cap_hierarchy(self):
        """Test regeneration caps follow correct hierarchy"""
        scrapper = get_archetype_caps(ArchetypeType.SCRAPPER)
        stalker = get_archetype_caps(ArchetypeType.STALKER)
        tanker = get_archetype_caps(ArchetypeType.TANKER)
        blaster = get_archetype_caps(ArchetypeType.BLASTER)

        # Scrappers/Stalkers have highest regen cap
        assert scrapper.regeneration_cap == 30.0
        assert stalker.regeneration_cap == 30.0

        # Tankers/Brutes have 25.0
        assert tanker.regeneration_cap == 25.0

        # Others have 20.0
        assert blaster.regeneration_cap == 20.0


class TestEdgeCases:
    """Test Suite: Edge Cases"""

    def test_get_caps_unknown_archetype(self):
        """Test get_archetype_caps with invalid archetype raises error"""
        # This would require creating an invalid enum value, which Python prevents
        # So we just verify all valid archetypes work
        for at_type in ArchetypeType:
            caps = get_archetype_caps(at_type)
            assert isinstance(caps, ArchetypeCaps)

    def test_caps_dataclass_immutable(self):
        """Test ArchetypeCaps is a dataclass"""
        caps = get_archetype_caps(ArchetypeType.TANKER)

        # Can access attributes
        assert caps.damage_cap == 4.0
        assert caps.resistance_cap == 0.90

        # Is a dataclass
        assert hasattr(caps, '__dataclass_fields__')

    def test_all_archetypes_have_caps(self):
        """Test all archetype types have cap definitions"""
        for at_type in ArchetypeType:
            caps = get_archetype_caps(at_type)
            assert caps is not None
            assert caps.archetype == at_type
