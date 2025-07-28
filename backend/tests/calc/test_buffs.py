"""Tests for buff and debuff calculations."""


from app.calc.buffs import BuffCalculator


class TestBuffCalculator:
    """Test BuffCalculator functionality."""

    def test_aggregate_buffs_basic(self):
        """Test basic buff aggregation."""
        calc = BuffCalculator("Blaster")

        sources = [
            {"damage": 10.0},
            {"damage": 15.0},
            {"damage": 25.0},
        ]

        result = calc.aggregate_buffs(sources, "damage")
        assert result == 50.0

    def test_aggregate_buffs_with_debuffs(self):
        """Test buff aggregation with debuffs."""
        calc = BuffCalculator("Scrapper")

        sources = [
            {"tohit": 20.0},
            {"tohit": -10.0},  # Debuff
            {"tohit": 15.0},
        ]

        # Include debuffs
        result = calc.aggregate_buffs(sources, "tohit", include_debuffs=True)
        assert result == 25.0

        # Exclude debuffs
        result = calc.aggregate_buffs(sources, "tohit", include_debuffs=False)
        assert result == 35.0

    def test_apply_debuff_resistance(self):
        """Test debuff resistance application."""
        calc = BuffCalculator("Tanker")

        # 50% damage debuff with 40% resistance
        resistance_sources = [{"damage_resistance": 40.0}]
        result = calc.apply_debuff_resistance(-50.0, "damage", resistance_sources)
        assert result == -30.0  # -50% * (1 - 0.4) = -30%

        # Test resistance cap
        resistance_sources = [
            {"damage_resistance": 60.0},
            {"damage_resistance": 60.0},  # Total 120%, capped at 100%
        ]
        result = calc.apply_debuff_resistance(-50.0, "damage", resistance_sources)
        assert result == 0.0  # 100% resistance = no debuff

    def test_calculate_offensive_buffs_damage_cap(self):
        """Test offensive buff calculations with damage cap."""
        calc = BuffCalculator("Blaster")  # 400% damage cap

        buff_sources = [
            {"damage": 200.0},
            {"damage_melee": 150.0},
            {"damage": 100.0},  # Total 300% general + 150% melee
        ]

        result = calc.calculate_offensive_buffs(buff_sources)

        # General damage capped at 400%
        assert result["damage"] == 300.0  # Not capped yet
        assert result["damage_melee"] == 150.0

        # Test hitting cap
        buff_sources.append({"damage": 200.0})  # Now 500% total
        result = calc.calculate_offensive_buffs(buff_sources)
        assert result["damage"] == 400.0  # Capped

    def test_calculate_offensive_buffs_with_debuffs(self):
        """Test offensive buffs with debuffs and resistance."""
        calc = BuffCalculator("Scrapper")

        buff_sources = [
            {"damage": 100.0},
            {"damage": -30.0},  # Damage debuff
            {"tohit": 20.0},
            {"tohit": -15.0},   # ToHit debuff
            {"accuracy": 50.0},
        ]

        debuff_resistance = [
            {"damage_resistance": 50.0},  # 50% damage debuff resistance
            {"tohit_resistance": 40.0},   # 40% tohit debuff resistance
        ]

        result = calc.calculate_offensive_buffs(buff_sources, debuff_resistance)

        # Damage: 100% buff, -30% debuff with 50% resistance = -15%
        assert result["damage"] == 85.0  # 100 - 15

        # ToHit: 20% buff, -15% debuff with 40% resistance = -9%
        assert result["tohit"] == 11.0  # 20 - 9

        # Accuracy: No debuffs
        assert result["accuracy"] == 50.0

    def test_calculate_defensive_buffs(self):
        """Test defensive buff calculations."""
        calc = BuffCalculator("Tanker")

        buff_sources = [
            {"hp": 50.0},
            {"regeneration": 100.0},
            {"recovery": 75.0},
            {"defense_melee": 15.0},
            {"defense_ranged": 10.0},
            {"defense_smashing": 5.0},
        ]

        result = calc.calculate_defensive_buffs(buff_sources)

        assert result["hp"] == 50.0
        assert result["regeneration"] == 100.0
        assert result["recovery"] == 75.0
        assert result["defense_melee"] == 15.0
        assert result["defense_ranged"] == 10.0
        assert result["defense_smashing"] == 5.0

    def test_calculate_defensive_buffs_with_caps(self):
        """Test defensive buffs hitting caps."""
        calc = BuffCalculator("Brute")

        buff_sources = [
            {"hp": 150.0},
            {"hp": 100.0},  # Total 250%, cap at 200%
            {"regeneration": 1500.0},
            {"regeneration": 1000.0},  # Total 2500%, cap at 2000%
        ]

        result = calc.calculate_defensive_buffs(buff_sources)

        assert result["hp"] == 200.0  # Capped
        assert result["regeneration"] == 2000.0  # Capped

    def test_calculate_utility_buffs(self):
        """Test utility buff calculations."""
        calc = BuffCalculator("Controller")

        buff_sources = [
            {"recharge": 100.0},
            {"recharge": 50.0},
            {"run_speed": 50.0},
            {"fly_speed": 100.0},
            {"endurance_cost": 30.0},  # 30% reduction
        ]

        result = calc.calculate_utility_buffs(buff_sources)

        assert result["recharge"] == 150.0
        assert result["run_speed"] == 50.0
        assert result["fly_speed"] == 100.0
        assert result["endurance_cost"] == 30.0

    def test_calculate_utility_buffs_with_caps(self):
        """Test utility buffs hitting caps."""
        calc = BuffCalculator("Defender")

        buff_sources = [
            {"recharge": 300.0},
            {"recharge": 300.0},  # Total 600%, cap at 500%
            {"endurance_cost": 50.0},
            {"endurance_cost": 50.0},  # Total 100%, cap at 90%
        ]

        result = calc.calculate_utility_buffs(buff_sources)

        assert result["recharge"] == 500.0  # Capped
        assert result["endurance_cost"] == 90.0  # Capped

    def test_calculate_all_buffs_integration(self):
        """Test full buff calculation integration."""
        calc = BuffCalculator("Scrapper")

        global_buffs = {
            "damage": 25.0,
            "recharge": 70.0,
            "defense_melee": 10.0,
        }

        power_buffs = [
            {
                "defense_melee": 15.0,
                "defense_ranged": 10.0,
                "resistance_smashing": 20.0,
            },
            {
                "damage": 30.0,
                "tohit": 15.0,
            },
        ]

        set_bonuses = [
            {"damage": 2.5},
            {"recharge": 5.0},
            {"defense_melee": 2.5},
            {"hp": 3.0},
        ]

        result = calc.calculate_all_buffs(global_buffs, power_buffs, set_bonuses)

        # Check offensive
        assert result["offensive"]["damage"] == 57.5  # 25 + 30 + 2.5
        assert result["offensive"]["tohit"] == 15.0

        # Check defensive
        assert result["defensive"]["defense_melee"] == 27.5  # 10 + 15 + 2.5
        assert result["defensive"]["defense_ranged"] == 10.0
        assert result["defensive"]["hp"] == 3.0

        # Check utility
        assert result["utility"]["recharge"] == 75.0  # 70 + 5

    def test_archetype_specific_caps(self):
        """Test that archetype-specific caps are applied."""
        # Brute has 600% damage cap
        brute_calc = BuffCalculator("Brute")
        buff_sources = [{"damage": 700.0}]
        result = brute_calc.calculate_offensive_buffs(buff_sources)
        assert result["damage"] == 600.0  # Capped at 600%

        # Blaster has 400% damage cap
        blaster_calc = BuffCalculator("Blaster")
        buff_sources = [{"damage": 700.0}]
        result = blaster_calc.calculate_offensive_buffs(buff_sources)
        assert result["damage"] == 400.0  # Capped at 400%

    def test_complex_debuff_scenario(self):
        """Test complex scenario with multiple debuffs and resistances."""
        calc = BuffCalculator("Tanker")

        buff_sources = [
            {"defense_melee": 30.0},
            {"defense_melee": -20.0},  # Defense debuff
            {"defense_ranged": 25.0},
            {"defense_ranged": -15.0},  # Defense debuff
            {"recharge": 100.0},
            {"recharge": -50.0},  # Recharge debuff
        ]

        debuff_resistance = [
            {"defense_resistance": 60.0},
            {"recharge_resistance": 40.0},
        ]

        defensive = calc.calculate_defensive_buffs(buff_sources, debuff_resistance)
        utility = calc.calculate_utility_buffs(buff_sources, debuff_resistance)

        # Defense melee: 30% buff, -20% debuff with 60% resistance = -8%
        assert defensive["defense_melee"] == 22.0  # 30 - 8

        # Defense ranged: 25% buff, -15% debuff with 60% resistance = -6%
        assert defensive["defense_ranged"] == 19.0  # 25 - 6

        # Recharge: 100% buff, -50% debuff with 40% resistance = -30%
        assert utility["recharge"] == 70.0  # 100 - 30

