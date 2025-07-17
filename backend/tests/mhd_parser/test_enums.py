"""Tests for MHD enums."""

import pytest

from app.mhd_parser.enums import (
    ClassType,
    PowerType,
    SetType,
    EnhancementType,
    BuffDebuff,
)


class TestEnums:
    """Test MHD enum definitions."""
    
    def test_class_type_values(self):
        """Test ClassType enum values."""
        assert ClassType.NONE.value == 0
        assert ClassType.BLASTER.value == 1
        assert ClassType.CONTROLLER.value == 2
        assert ClassType.DEFENDER.value == 3
        assert ClassType.SCRAPPER.value == 4
        assert ClassType.TANKER.value == 5
    
    def test_power_type_values(self):
        """Test PowerType enum values."""
        assert PowerType.CLICK.value == 0
        assert PowerType.AUTO.value == 1
        assert PowerType.TOGGLE.value == 2
        assert PowerType.BOOST.value == 3
        assert PowerType.INSPIRATION.value == 4
    
    def test_set_type_values(self):
        """Test SetType enum values."""
        assert SetType.NONE.value == 0
        assert SetType.MELEE_DAMAGE.value == 1
        assert SetType.RANGED_DAMAGE.value == 2
        assert SetType.TARGETED_AOE_DAMAGE.value == 3
    
    def test_enhancement_type_values(self):
        """Test EnhancementType enum values."""
        assert EnhancementType.NONE.value == 0
        assert EnhancementType.NORMAL.value == 1
        assert EnhancementType.INVENTION.value == 2
        assert EnhancementType.SPECIAL_ORIGIN.value == 3
        assert EnhancementType.SET_IO.value == 4
    
    def test_buff_debuff_values(self):
        """Test BuffDebuff enum values."""
        assert BuffDebuff.BUFF.value == 0
        assert BuffDebuff.DEBUFF.value == 1
        assert BuffDebuff.ANY.value == 2
    
    def test_enum_from_value(self):
        """Test creating enums from integer values."""
        assert ClassType(1) == ClassType.BLASTER
        assert PowerType(2) == PowerType.TOGGLE
        assert SetType(3) == SetType.TARGETED_AOE_DAMAGE
    
    def test_invalid_enum_value(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError):
            ClassType(999)
        
        with pytest.raises(ValueError):
            PowerType(-1)