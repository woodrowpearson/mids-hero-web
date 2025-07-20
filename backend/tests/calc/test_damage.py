"""Tests for damage calculation module."""

import pytest

from app.calc.damage import (
    calc_critical_damage,
    calc_damage_scale_to_damage,
    calc_damage_with_resistance,
    calc_final_damage,
)
from app.core.enums import DamageType


class TestDamageCalculations:
    """Test damage calculation functions."""

    def test_final_damage_basic(self):
        """Test basic damage calculation without buffs."""
        base = 100.0
        enhancement = 0.0
        global_buff = 0.0
        
        result = calc_final_damage(base, enhancement, global_buff, "Blaster")
        assert result == 100.0

    def test_final_damage_with_enhancement(self):
        """Test damage with enhancement (3 SOs)."""
        base = 100.0
        enhancement = 0.9999  # ~100% enhancement (3 SOs)
        global_buff = 0.0
        
        result = calc_final_damage(base, enhancement, global_buff, "Blaster")
        # After ED, should be ~99.5% bonus
        assert result == pytest.approx(199.4, rel=0.01)

    def test_final_damage_with_cap(self):
        """Test damage cap enforcement."""
        base = 100.0
        enhancement = 2.0  # 200% enhancement
        global_buff = 3.0  # 300% global buff
        
        # Blaster cap is 400% (4.0x)
        result = calc_final_damage(base, enhancement, global_buff, "Blaster")
        assert result == 400.0  # Capped at 4x base

    def test_final_damage_pvp(self):
        """Test PvP damage reduction."""
        base = 100.0
        enhancement = 0.95
        global_buff = 0.0
        
        result = calc_final_damage(
            base, enhancement, global_buff, "Blaster", is_pvp=True
        )
        # Should be halved in PvP
        assert result == pytest.approx(97.5, rel=0.01)  # (100 * 1.95) * 0.5

    def test_damage_with_resistance(self):
        """Test damage after resistance."""
        damage = 100.0
        
        # 50% resistance
        result = calc_damage_with_resistance(damage, 50.0, DamageType.FIRE)
        assert result == 50.0
        
        # 90% resistance
        result = calc_damage_with_resistance(damage, 90.0, DamageType.SMASHING)
        assert result == 10.0
        
        # 95% resistance (capped)
        result = calc_damage_with_resistance(damage, 95.0, DamageType.LETHAL)
        assert result == 5.0
        
        # Over 95% still capped at 95%
        result = calc_damage_with_resistance(damage, 99.0, DamageType.ENERGY)
        assert result == 5.0

    def test_damage_with_negative_resistance(self):
        """Test damage with negative resistance (vulnerability)."""
        damage = 100.0
        
        # -50% resistance (50% more damage)
        result = calc_damage_with_resistance(damage, -50.0, DamageType.COLD)
        assert result == 150.0
        
        # -200% resistance (capped at 300% damage)
        result = calc_damage_with_resistance(damage, -200.0, DamageType.PSIONIC)
        assert result == 300.0

    def test_critical_damage_basic(self):
        """Test critical hit calculations."""
        base = 100.0
        crit_chance = 0.1  # 10% chance
        
        result = calc_critical_damage(base, crit_chance)
        
        # Critical should be 2x base
        assert result["critical"] == 200.0
        # Average should account for crit chance
        assert result["average"] == 110.0  # 90% * 100 + 10% * 200

    def test_critical_damage_scrapper(self):
        """Test Scrapper inherent critical chance."""
        base = 100.0
        crit_chance = 0.0  # No additional crit
        
        result = calc_critical_damage(base, crit_chance, archetype="Scrapper")
        
        # Scrappers have base 5% crit
        assert result["chance"] >= 0.05
        assert result["average"] >= 105.0

    def test_damage_scale_conversion(self):
        """Test damage scale to damage conversion."""
        scale = 1.0
        
        # Blaster ranged at level 50
        result = calc_damage_scale_to_damage(scale, "Blaster", 50, "ranged")
        assert result == pytest.approx(62.56, rel=0.01)
        
        # Tanker melee at level 50
        result = calc_damage_scale_to_damage(scale, "Tanker", 50, "melee")
        assert result == pytest.approx(44.49, rel=0.01)
        
        # Level scaling
        result = calc_damage_scale_to_damage(scale, "Blaster", 25, "ranged")
        assert result == pytest.approx(31.28, rel=0.01)  # Half of level 50