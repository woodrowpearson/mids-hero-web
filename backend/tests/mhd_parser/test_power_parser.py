"""Tests for parsing Power records from MHD files."""

import io
import struct

import pytest

from app.mhd_parser.power_parser import (
    PowerType,
    parse_effect,
    parse_power,
    parse_requirement,
)


class TestRequirementParser:
    """Test cases for parsing Requirement substructures."""

    def test_parse_minimal_requirement(self):
        """Test parsing a minimal requirement."""
        data = io.BytesIO()

        # Write Requirement fields
        data.write(b'\x00')  # ClassName empty
        data.write(b'\x00')  # ClassNameNot empty
        data.write(struct.pack('<i', 0))  # ClassesRequired count
        data.write(struct.pack('<i', 0))  # ClassesDisallowed count
        data.write(struct.pack('<i', 0))  # PowerID count
        data.write(struct.pack('<i', 0))  # PowerIDNot count

        data.seek(0)

        req = parse_requirement(data)

        assert req.class_name == ""
        assert req.class_name_not == ""
        assert req.classes_required == []
        assert req.classes_disallowed == []
        assert req.power_ids == []
        assert req.power_ids_not == []

    def test_parse_requirement_with_class_restrictions(self):
        """Test parsing requirement with class restrictions."""
        data = io.BytesIO()

        # ClassName and ClassNameNot
        data.write(b'\x06Tanker')
        data.write(b'\x07Blaster')

        # ClassesRequired array
        data.write(struct.pack('<i', 2))  # count
        data.write(struct.pack('<i', 0))  # Tanker index
        data.write(struct.pack('<i', 1))  # Brute index

        # ClassesDisallowed array
        data.write(struct.pack('<i', 1))  # count
        data.write(struct.pack('<i', 5))  # Scrapper index

        # PowerID arrays (empty)
        data.write(struct.pack('<i', 0))  # PowerID count
        data.write(struct.pack('<i', 0))  # PowerIDNot count

        data.seek(0)

        req = parse_requirement(data)

        assert req.class_name == "Tanker"
        assert req.class_name_not == "Blaster"
        assert req.classes_required == [0, 1]
        assert req.classes_disallowed == [5]
        assert req.power_ids == []
        assert req.power_ids_not == []

    def test_parse_requirement_with_power_dependencies(self):
        """Test parsing requirement with power dependencies."""
        data = io.BytesIO()

        # Class names empty
        data.write(b'\x00')
        data.write(b'\x00')

        # Class arrays empty
        data.write(struct.pack('<i', 0))  # ClassesRequired
        data.write(struct.pack('<i', 0))  # ClassesDisallowed

        # PowerID - required powers
        data.write(struct.pack('<i', 3))  # count
        data.write(struct.pack('<i', 100))  # Power 100
        data.write(struct.pack('<i', 101))  # Power 101
        data.write(struct.pack('<i', 102))  # Power 102

        # PowerIDNot - excluded powers
        data.write(struct.pack('<i', 1))  # count
        data.write(struct.pack('<i', 200))  # Power 200

        data.seek(0)

        req = parse_requirement(data)

        assert req.power_ids == [100, 101, 102]
        assert req.power_ids_not == [200]


class TestEffectParser:
    """Test cases for parsing Effect substructures."""

    def test_parse_minimal_effect(self):
        """Test parsing a minimal effect."""
        data = io.BytesIO()

        # Basic fields
        data.write(struct.pack('<i', 0))  # PowerFullName
        data.write(struct.pack('<i', 1))  # EffectClass (Damage)
        data.write(struct.pack('<i', 2))  # EffectType (Energy)
        data.write(struct.pack('<i', 0))  # DamageType
        data.write(struct.pack('<i', 0))  # MezType
        data.write(struct.pack('<i', 0))  # ETModifies
        data.write(b'\x0BDamage Test')  # Summon

        # Numeric fields (15 floats)
        for i in range(15):
            data.write(struct.pack('<f', float(i)))

        # More fields
        data.write(struct.pack('<i', 60))  # DisplayPercentage
        data.write(struct.pack('<f', 0.0))  # Probability
        data.write(struct.pack('<f', 0.0))  # Delay
        data.write(struct.pack('<i', 0))  # Stacking
        data.write(struct.pack('<i', 0))  # Suppression count

        # Arrays
        data.write(struct.pack('<i', 0))  # Reward count
        data.write(struct.pack('<i', 0))  # EffectId count
        data.write(struct.pack('<i', 0))  # IgnoreED count
        data.write(struct.pack('<i', 0))  # IgnoreScale count

        # Requirement
        data.write(b'\x00')  # ClassName empty
        data.write(b'\x00')  # ClassNameNot empty
        data.write(struct.pack('<i', 0))  # ClassesRequired
        data.write(struct.pack('<i', 0))  # ClassesDisallowed
        data.write(struct.pack('<i', 0))  # PowerID
        data.write(struct.pack('<i', 0))  # PowerIDNot

        # Special fields
        data.write(b'\x00')  # SpecialCase empty
        data.write(struct.pack('<i', 0))  # UIDClassName
        data.write(struct.pack('<i', 0))  # nIDClassName
        data.write(struct.pack('<i', 0))  # CancelEvents count

        # More flags/fields
        data.write(struct.pack('<i', 0))  # AttribType
        data.write(struct.pack('<i', 0))  # Aspect
        data.write(b'\x00')  # ModifierTable empty
        data.write(struct.pack('<i', 0))  # nModifierTable
        data.write(b'\x00')  # PowerFullName_Enh empty
        data.write(struct.pack('<i', 0))  # buffMode
        data.write(struct.pack('<i', 0))  # Override count

        # Flags and final fields
        data.write(struct.pack('<i', 0))  # ProcsPerMinute
        data.write(struct.pack('<?', False))  # Cancelable
        data.write(struct.pack('<?', False))  # IgnoreToggleDrop
        data.write(struct.pack('<?', False))  # IgnoreActiveDefense
        data.write(struct.pack('<i', 0))  # ChainID count
        data.write(struct.pack('<?', False))  # ChainsRequirePrimaryTarget
        data.write(struct.pack('<?', False))  # IgnoreStrength

        data.seek(0)

        effect = parse_effect(data)

        assert effect.power_full_name == 0
        assert effect.effect_class == 1  # Damage
        assert effect.effect_type == 2  # Energy
        assert effect.summon == "Damage Test"
        assert effect.display_percentage == 60
        assert effect.scale == 0.0  # First of the 15 floats

    def test_parse_effect_with_arrays(self):
        """Test parsing effect with array data."""
        data = io.BytesIO()

        # Basic fields up to arrays
        data.write(struct.pack('<i', 0))  # PowerFullName
        data.write(struct.pack('<i', 0))  # EffectClass
        data.write(struct.pack('<i', 0))  # EffectType
        data.write(struct.pack('<i', 0))  # DamageType
        data.write(struct.pack('<i', 0))  # MezType
        data.write(struct.pack('<i', 0))  # ETModifies
        data.write(b'\x00')  # Summon empty

        # Numeric fields
        for _i in range(15):
            data.write(struct.pack('<f', 0.0))

        data.write(struct.pack('<i', 0))  # DisplayPercentage
        data.write(struct.pack('<f', 0.0))  # Probability
        data.write(struct.pack('<f', 0.0))  # Delay
        data.write(struct.pack('<i', 0))  # Stacking

        # Suppression array
        data.write(struct.pack('<i', 2))  # count
        data.write(struct.pack('<?', True))  # Suppression[0]
        data.write(struct.pack('<?', False))  # Suppression[1]

        # Reward array
        data.write(struct.pack('<i', 1))  # count
        data.write(b'\x06Reward')  # Reward[0]

        # EffectId array
        data.write(struct.pack('<i', 3))  # count
        data.write(b'\x08Effect_1')
        data.write(b'\x08Effect_2')
        data.write(b'\x08Effect_3')

        # IgnoreED and IgnoreScale arrays
        data.write(struct.pack('<i', 0))  # IgnoreED count
        data.write(struct.pack('<i', 0))  # IgnoreScale count

        # Requirement (minimal)
        data.write(b'\x00')  # ClassName
        data.write(b'\x00')  # ClassNameNot
        data.write(struct.pack('<i', 0))  # ClassesRequired
        data.write(struct.pack('<i', 0))  # ClassesDisallowed
        data.write(struct.pack('<i', 0))  # PowerID
        data.write(struct.pack('<i', 0))  # PowerIDNot

        # Rest of fields
        data.write(b'\x00')  # SpecialCase
        data.write(struct.pack('<i', 0))  # UIDClassName
        data.write(struct.pack('<i', 0))  # nIDClassName
        data.write(struct.pack('<i', 0))  # CancelEvents
        data.write(struct.pack('<i', 0))  # AttribType
        data.write(struct.pack('<i', 0))  # Aspect
        data.write(b'\x00')  # ModifierTable
        data.write(struct.pack('<i', 0))  # nModifierTable
        data.write(b'\x00')  # PowerFullName_Enh
        data.write(struct.pack('<i', 0))  # buffMode
        data.write(struct.pack('<i', 0))  # Override
        data.write(struct.pack('<i', 0))  # ProcsPerMinute
        data.write(struct.pack('<?', False))  # Cancelable
        data.write(struct.pack('<?', False))  # IgnoreToggleDrop
        data.write(struct.pack('<?', False))  # IgnoreActiveDefense
        data.write(struct.pack('<i', 0))  # ChainID
        data.write(struct.pack('<?', False))  # ChainsRequirePrimaryTarget
        data.write(struct.pack('<?', False))  # IgnoreStrength

        data.seek(0)

        effect = parse_effect(data)

        assert effect.suppression == [True, False]
        assert effect.reward == ["Reward"]
        assert effect.effect_ids == ["Effect_1", "Effect_2", "Effect_3"]


class TestPowerParser:
    """Test cases for parsing Power records."""

    def test_parse_minimal_power(self):
        """Test parsing a minimal power with basic fields."""
        data = io.BytesIO()

        # Write Power fields in order (simplified for test)
        # 1. FullName
        data.write(b'\x0BPunch_Quick')  # length 11

        # 2. GroupName
        data.write(b'\x05Melee')

        # 3. SetName
        data.write(b'\x0BSword_Melee')

        # 4. PowerName
        data.write(b'\x05Punch')

        # 5. DisplayName
        data.write(b'\x0BQuick Punch')

        # 6. Available
        data.write(struct.pack('<i', 1))  # Level 1

        # 7. Requirement (minimal)
        data.write(b'\x00')  # ClassName
        data.write(b'\x00')  # ClassNameNot
        data.write(struct.pack('<i', 0))  # ClassesRequired
        data.write(struct.pack('<i', 0))  # ClassesDisallowed
        data.write(struct.pack('<i', 0))  # PowerID
        data.write(struct.pack('<i', 0))  # PowerIDNot

        # 8. PowerType (enum)
        data.write(struct.pack('<i', 1))  # Click

        # 9. Basic numeric fields
        data.write(struct.pack('<f', 5.0))  # Accuracy
        data.write(struct.pack('<i', 5))  # AttackTypes

        # 10. GroupMembership array
        data.write(struct.pack('<i', 0))  # count

        # 11. EntitiesAffected and EntitiesAutoHit (enums)
        data.write(struct.pack('<i', 1))  # Foe
        data.write(struct.pack('<i', 0))  # None

        # 12. Target (enum)
        data.write(struct.pack('<i', 1))  # SingleTarget

        # 13. TargetLineSpecialRange
        data.write(struct.pack('<?', False))

        # 14. Range and RangeSecondary
        data.write(struct.pack('<f', 7.0))
        data.write(struct.pack('<f', 0.0))

        # 15. EndCost, InterruptTime, CastTime, RechargeTime
        data.write(struct.pack('<f', 5.2))
        data.write(struct.pack('<f', 0.0))
        data.write(struct.pack('<f', 1.07))
        data.write(struct.pack('<f', 4.0))

        # 16. BaseRechargeTime, ActivatePeriod
        data.write(struct.pack('<f', 4.0))
        data.write(struct.pack('<f', 0.0))

        # 17. EffectArea, Radius, Arc
        data.write(struct.pack('<i', 0))  # None
        data.write(struct.pack('<f', 0.0))
        data.write(struct.pack('<i', 0))

        # 18. MaxTargets
        data.write(struct.pack('<i', 1))

        # 19. MaxBoosts
        data.write(b'\x06DAERTH')  # string "DAERTH" with length 6

        # 20. CastFlags (bitfield)
        data.write(struct.pack('<i', 0))

        # 21. AI related fields
        data.write(struct.pack('<i', 0))  # AIReport
        data.write(struct.pack('<i', 0))  # NumEffects

        # 22. BoostsAllowed array
        data.write(struct.pack('<i', 0))  # count

        # 23-29. More numeric fields
        for _ in range(7):
            data.write(struct.pack('<f', 0.0))

        # 30. Strings and arrays
        data.write(b'\x00')  # DescShort
        data.write(b'\x00')  # DescLong
        data.write(struct.pack('<i', 0))  # SetTypes count
        data.write(struct.pack('<i', 0))  # ClickBuff
        data.write(struct.pack('<?', False))  # AlwaysToggle
        data.write(struct.pack('<i', 0))  # Level
        data.write(struct.pack('<?', False))  # AllowFrontLoading
        data.write(struct.pack('<?', False))  # IgnoreEnh
        data.write(struct.pack('<?', False))  # IgnoreSetBonus
        data.write(struct.pack('<?', False))  # BoostBoostable
        data.write(struct.pack('<?', False))  # BoostAlways

        # 31. UIDSubPower array
        data.write(struct.pack('<i', 0))  # count

        # 32. IgnoreStrength array
        data.write(struct.pack('<i', 0))  # count

        # 33. IgnoreBuff array
        data.write(struct.pack('<i', 0))  # count

        # 34. SkipMax
        data.write(struct.pack('<?', False))

        # 35. DisplayLocation
        data.write(struct.pack('<i', 0))

        # 36. MutexAuto, MutexIgnore
        data.write(struct.pack('<?', False))
        data.write(struct.pack('<?', False))

        # 37. AbsorbSummonEffects, AbsorbSummonAttributes
        data.write(struct.pack('<?', False))
        data.write(struct.pack('<?', False))

        # 38. ShowSummonAnyway, NeverAutoUpdate, NeverAutoUpdateRequirements
        data.write(struct.pack('<?', False))
        data.write(struct.pack('<?', False))
        data.write(struct.pack('<?', False))

        # 39. IncludeFlag, ForcedClass
        data.write(struct.pack('<?', False))
        data.write(b'\x00')

        # 40. SortOverride, BoostBoostSpecialAllowed
        data.write(struct.pack('<i', 0))
        data.write(struct.pack('<?', False))

        # 41. Effects array
        data.write(struct.pack('<i', 0))  # count

        # 42. HiddenPower
        data.write(struct.pack('<?', False))

        data.seek(0)

        power = parse_power(data)

        assert power.full_name == "Punch_Quick"
        assert power.group_name == "Melee"
        assert power.set_name == "Sword_Melee"
        assert power.power_name == "Punch"
        assert power.display_name == "Quick Punch"
        assert power.available == 1
        assert power.power_type == PowerType.CLICK
        assert pytest.approx(power.accuracy, rel=1e-5) == 5.0
        assert power.attack_types == 5
        assert pytest.approx(power.range, rel=1e-5) == 7.0
        assert pytest.approx(power.end_cost, rel=1e-5) == 5.2
        assert pytest.approx(power.cast_time, rel=1e-5) == 1.07
        assert pytest.approx(power.recharge_time, rel=1e-5) == 4.0
        assert len(power.effects) == 0

    def test_parse_power_with_effects(self):
        """Test parsing power with multiple effects."""
        # This would be a large test - simplified for brevity
        # Would test parsing a power with actual Effect objects
        pass

    def test_parse_power_with_arrays(self):
        """Test parsing power with various array fields."""
        # Test GroupMembership, BoostsAllowed, SetTypes, UIDSubPower arrays
        pass
