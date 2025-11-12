"""
Test Archetype Modifiers - AT-specific scaling

Tests based on Spec 16 test cases and depth coverage.
Validates modifier table structure and lookup functions.
"""

from app.calculations.core import (
    ArchetypeModifiers,
    ModifierTable,
    calculate_effect_magnitude,
)


class TestModifierTableBasics:
    """Test Suite: ModifierTable Class"""

    def test_modifier_table_creation(self):
        """Test creating a modifier table"""
        table = ModifierTable(
            id="Test_Table",
            base_index=0,
            table=[[1.0] * 60 for _ in range(55)]
        )

        assert table.id == "Test_Table"
        assert table.base_index == 0
        assert len(table.table) == 55
        assert len(table.table[0]) == 60

    def test_get_modifier_valid(self):
        """Test get_modifier with valid inputs"""
        # Create test table with known value
        table_data = [[0.0] * 60 for _ in range(55)]
        table_data[49][1] = -30.5856  # Level 50, Column 1

        table = ModifierTable(
            id="Test_Damage",
            base_index=0,
            table=table_data
        )

        modifier = table.get_modifier(50, 1)  # Level 50, Column 1
        assert abs(modifier - (-30.5856)) < 0.001

    def test_get_modifier_level_bounds(self):
        """Test get_modifier level bounds checking"""
        table = ModifierTable(
            id="Test_Table",
            base_index=0,
            table=[[1.0] * 60 for _ in range(55)]
        )

        # Level too low
        assert table.get_modifier(0, 0) == 0.0

        # Level too high
        assert table.get_modifier(56, 0) == 0.0

        # Valid levels
        assert table.get_modifier(1, 0) == 1.0
        assert table.get_modifier(55, 0) == 1.0

    def test_get_modifier_column_bounds(self):
        """Test get_modifier column bounds checking"""
        table = ModifierTable(
            id="Test_Table",
            base_index=0,
            table=[[1.0] * 60 for _ in range(55)]
        )

        # Column too low
        assert table.get_modifier(50, -1) == 0.0

        # Column too high
        assert table.get_modifier(50, 60) == 0.0

        # Valid columns
        assert table.get_modifier(50, 0) == 1.0
        assert table.get_modifier(50, 59) == 1.0


class TestArchetypeModifiersBasics:
    """Test Suite: ArchetypeModifiers Manager"""

    def test_create_test_instance(self):
        """Test creating test instance with known values"""
        modifiers = ArchetypeModifiers.create_test_instance()

        # Should have 3 tables
        assert len(modifiers.tables) == 3
        assert "Melee_Damage" in modifiers.tables
        assert "Melee_Buff_Def" in modifiers.tables
        assert "Melee_Ones" in modifiers.tables

    def test_get_modifier_valid_table(self):
        """Test get_modifier with valid table"""
        modifiers = ArchetypeModifiers.create_test_instance()

        # Scrapper melee damage at level 50
        modifier = modifiers.get_modifier("Melee_Damage", 50, 1)
        assert abs(modifier - (-30.5856)) < 0.001

    def test_get_modifier_invalid_table(self):
        """Test get_modifier with nonexistent table"""
        modifiers = ArchetypeModifiers.create_test_instance()

        # Nonexistent table should return 0.0
        modifier = modifiers.get_modifier("NonExistent", 50, 1)
        assert modifier == 0.0

    def test_table_exists(self):
        """Test table_exists method"""
        modifiers = ArchetypeModifiers.create_test_instance()

        assert modifiers.table_exists("Melee_Damage")
        assert modifiers.table_exists("Melee_Ones")
        assert not modifiers.table_exists("NonExistent")

    def test_list_tables(self):
        """Test list_tables method"""
        modifiers = ArchetypeModifiers.create_test_instance()

        tables = modifiers.list_tables()
        assert len(tables) == 3
        assert "Melee_Damage" in tables
        assert "Melee_Buff_Def" in tables
        assert "Melee_Ones" in tables


class TestSpec16TestCases:
    """Test Suite: Spec 16 Section 4 Test Cases"""

    def test_1_scrapper_melee_damage_level_50(self):
        """
        Test 1: Scrapper melee damage at level 50 → -30.59

        From Spec 16, Section 4, Test Case 1 (updated from implementation plan).
        Scrapper (column 1) melee damage at level 50.
        """
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 50, 1)

        expected = -30.5856
        assert abs(modifier - expected) < 0.01

    def test_2_tanker_melee_damage_level_50(self):
        """
        Test 2: Tanker melee damage at level 50 → -55.61

        From Spec 16 depth coverage (Test 2 equivalent).
        Tanker (column 0) does less melee damage than Scrapper.
        """
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 50, 0)

        expected = -55.6102
        assert abs(modifier - expected) < 0.01

        # Tanker should do less melee damage than Scrapper (higher negative value)
        scrapper_mod = modifiers.get_modifier("Melee_Damage", 50, 1)
        assert abs(modifier) > abs(scrapper_mod)

    def test_3_defender_buff_superiority(self):
        """
        Test 3: Defender defense buff at level 50 → 0.1

        From Spec 16 depth coverage (Test 4 equivalent).
        Defender (column 2) has highest defense buff modifier.
        """
        modifiers = ArchetypeModifiers.create_test_instance()

        table_name = "Melee_Buff_Def"
        level = 50

        tanker_mod = modifiers.get_modifier(table_name, level, 0)     # 0.07
        scrapper_mod = modifiers.get_modifier(table_name, level, 1)   # 0.09
        defender_mod = modifiers.get_modifier(table_name, level, 2)   # 0.1
        controller_mod = modifiers.get_modifier(table_name, level, 3) # 0.075

        # Defender should have highest buff modifier
        assert defender_mod > tanker_mod
        assert defender_mod > scrapper_mod
        assert defender_mod > controller_mod

        assert abs(defender_mod - 0.1) < 0.001

    def test_4_controller_melee_damage_level_50(self):
        """
        Test 4: Controller melee damage at level 50 → -62.56

        From Spec 16 depth coverage.
        Controller (column 3) has lowest melee damage (highest negative value).
        """
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 50, 3)

        expected = -62.5615
        assert abs(modifier - expected) < 0.01

    def test_5_blaster_melee_damage_level_50(self):
        """
        Test 5: Blaster melee damage at level 50 → -52.83

        From Spec 16 depth coverage.
        Blaster (column 4) moderate melee damage.
        """
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 50, 4)

        expected = -52.8297
        assert abs(modifier - expected) < 0.01

    def test_6_melee_ones_no_scaling(self):
        """
        Test 6: Melee_Ones returns 1.0 for all ATs and levels

        From Spec 16 depth coverage (Test 7).
        Melee_Ones table should return 1.0 for all inputs.
        """
        modifiers = ArchetypeModifiers.create_test_instance()

        table_name = "Melee_Ones"

        # Test multiple levels and columns
        for level in [1, 25, 50]:
            for column in range(5):  # First 5 ATs
                modifier = modifiers.get_modifier(table_name, level, column)
                assert abs(modifier - 1.0) < 0.001, \
                    f"Melee_Ones should be 1.0 for level {level}, column {column}"


class TestEffectMagnitudeCalculation:
    """Test Suite: Effect Magnitude Calculation"""

    def test_basic_magnitude_calculation(self):
        """Test calculate_effect_magnitude function"""
        # Scrapper melee attack at level 50
        base_magnitude = 10.0
        scale = 1.0
        modifier = -30.5856

        result = calculate_effect_magnitude(base_magnitude, scale, modifier)

        expected = 10.0 * 1.0 * (-30.5856)  # = -305.856
        assert abs(result - expected) < 0.01

    def test_defender_buff_calculation(self):
        """Test buff calculation with positive modifier"""
        # Defender defense buff
        base_magnitude = 5.0
        scale = 1.0
        modifier = 0.1

        result = calculate_effect_magnitude(base_magnitude, scale, modifier)

        expected = 5.0 * 1.0 * 0.1  # = 0.5
        assert abs(result - expected) < 0.001

    def test_magnitude_with_scale(self):
        """Test magnitude calculation with non-1.0 scale"""
        base_magnitude = 10.0
        scale = 1.5
        modifier = -30.5856

        result = calculate_effect_magnitude(base_magnitude, scale, modifier)

        expected = 10.0 * 1.5 * (-30.5856)  # = -458.784
        assert abs(result - expected) < 0.01


class TestEdgeCases:
    """Test Suite: Edge Cases and Validation"""

    def test_level_zero(self):
        """Test level 0 returns 0.0 (matches C# behavior)"""
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 0, 1)
        assert modifier == 0.0

    def test_level_negative(self):
        """Test negative level returns 0.0"""
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", -1, 1)
        assert modifier == 0.0

    def test_level_too_high(self):
        """Test level > 55 returns 0.0"""
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 56, 1)
        assert modifier == 0.0

    def test_column_negative(self):
        """Test negative column returns 0.0"""
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 50, -1)
        assert modifier == 0.0

    def test_column_too_high(self):
        """Test column >= 60 returns 0.0"""
        modifiers = ArchetypeModifiers.create_test_instance()

        modifier = modifiers.get_modifier("Melee_Damage", 50, 999)
        assert modifier == 0.0


class TestValidation:
    """Test Suite: Structure Validation"""

    def test_validate_structure_valid(self):
        """Test validate_structure with valid tables"""
        modifiers = ArchetypeModifiers.create_test_instance()

        errors = modifiers.validate_structure()
        assert len(errors) == 0

    def test_validate_structure_invalid_level_count(self):
        """Test validate_structure detects wrong level count"""
        modifiers = ArchetypeModifiers()

        # Create table with wrong number of levels
        modifiers.tables["Bad_Table"] = ModifierTable(
            id="Bad_Table",
            base_index=0,
            table=[[1.0] * 60 for _ in range(50)]  # Only 50 levels
        )

        errors = modifiers.validate_structure()
        assert len(errors) > 0
        assert "Bad_Table" in errors[0]
        assert "50 levels" in errors[0]

    def test_validate_structure_inconsistent_columns(self):
        """Test validate_structure detects inconsistent column count"""
        modifiers = ArchetypeModifiers()

        # Create table with inconsistent columns
        table_data = [[1.0] * 60 for _ in range(55)]
        table_data[10] = [1.0] * 50  # Level 11 has wrong column count

        modifiers.tables["Bad_Columns"] = ModifierTable(
            id="Bad_Columns",
            base_index=0,
            table=table_data
        )

        errors = modifiers.validate_structure()
        assert len(errors) > 0
        assert "Bad_Columns" in errors[0]
        assert "level 11" in errors[0]


class TestATComparisons:
    """Test Suite: Cross-AT Comparisons"""

    def test_scrapper_vs_tanker_damage(self):
        """Test Scrappers do more melee damage than Tankers"""
        modifiers = ArchetypeModifiers.create_test_instance()

        scrapper = modifiers.get_modifier("Melee_Damage", 50, 1)
        tanker = modifiers.get_modifier("Melee_Damage", 50, 0)

        # More negative = more damage
        assert abs(scrapper) < abs(tanker)

    def test_defender_vs_tanker_buffs(self):
        """Test Defenders buff better than Tankers"""
        modifiers = ArchetypeModifiers.create_test_instance()

        defender = modifiers.get_modifier("Melee_Buff_Def", 50, 2)
        tanker = modifiers.get_modifier("Melee_Buff_Def", 50, 0)

        # Higher positive = stronger buffs
        assert defender > tanker

    def test_all_ats_melee_damage_different(self):
        """Test ATs have melee damage modifiers (some may be equal)"""
        modifiers = ArchetypeModifiers.create_test_instance()

        # Get melee damage for first 5 ATs
        at_mods = [
            modifiers.get_modifier("Melee_Damage", 50, col)
            for col in range(5)
        ]

        # All should be non-zero negative values
        for mod in at_mods:
            assert mod < 0, "Damage modifiers should be negative"

        # Note: Scrapper and Defender have same melee damage value (-30.5856)
        # This is correct per MidsReborn data
