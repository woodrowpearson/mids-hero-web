"""Tests for parsing Enhancement records from MHD files."""

import io
import struct

import pytest

from app.mhd_parser.enhancement_parser import (
    parse_enhancement,
    parse_enhancement_set,
    parse_s_effect,
)


class TestSEffectParser:
    """Test cases for parsing sEffect substructures."""

    def test_parse_minimal_s_effect(self):
        """Test parsing a minimal sEffect without nested Effect."""
        data = io.BytesIO()

        # Write sEffect fields
        data.write(struct.pack("<i", 1))  # Mode (enum)
        data.write(struct.pack("<i", 0))  # BuffMode

        # Enhance sub-structure
        data.write(struct.pack("<i", 5))  # Enhance.ID
        data.write(struct.pack("<i", 2))  # Enhance.SubID

        # Schedule and Multiplier
        data.write(struct.pack("<i", 0))  # Schedule
        data.write(struct.pack("<f", 1.0))  # Multiplier

        # Boolean flag - False means no nested Effect FX
        data.write(struct.pack("<?", False))

        data.seek(0)

        s_effect = parse_s_effect(data)

        assert s_effect.mode == 1
        assert s_effect.buff_mode == 0
        assert s_effect.enhance_id == 5
        assert s_effect.enhance_sub_id == 2
        assert s_effect.schedule == 0
        assert pytest.approx(s_effect.multiplier, rel=1e-5) == 1.0
        assert s_effect.fx is None

    def test_parse_s_effect_with_nested_fx(self):
        """Test parsing sEffect with nested Effect FX."""
        data = io.BytesIO()

        # Basic sEffect fields
        data.write(struct.pack("<i", 2))  # Mode
        data.write(struct.pack("<i", 1))  # BuffMode
        data.write(struct.pack("<i", 10))  # Enhance.ID
        data.write(struct.pack("<i", 3))  # Enhance.SubID
        data.write(struct.pack("<i", 1))  # Schedule
        data.write(struct.pack("<f", 1.5))  # Multiplier

        # Boolean flag - True means nested Effect follows
        data.write(struct.pack("<?", True))

        # Nested Effect FX (simplified for test)
        # This would normally be a full Effect structure
        # For now we'll write minimal Effect data
        # (In real implementation, this would call parse_effect from power_parser)

        data.seek(0)

        # For now, we'll test just the flag parsing
        # Full Effect parsing will be integrated later
        with pytest.raises(NotImplementedError):
            parse_s_effect(data)


class TestEnhancementParser:
    """Test cases for parsing Enhancement records."""

    def test_parse_minimal_enhancement(self):
        """Test parsing a minimal enhancement."""
        data = io.BytesIO()

        # Basic fields
        data.write(struct.pack("<i", 1001))  # StaticIndex
        data.write(b"\x0bAccuracy IO")  # Name (length 11)
        data.write(b"\x06Acc IO")  # ShortName (length 6)
        data.write(b"\x1dIncreases accuracy of attacks")  # Desc (length 29)

        # Type IDs
        data.write(struct.pack("<i", 1))  # TypeID
        data.write(struct.pack("<i", 0))  # SubTypeID

        # ClassID array (count+1 pattern)
        data.write(struct.pack("<i", 0))  # count
        data.write(struct.pack("<i", -1))  # extra entry

        # More fields
        data.write(b"\x0faccuracy_io.png")  # Image (length 15)
        data.write(struct.pack("<i", 0))  # nIDSet
        data.write(b"\x00")  # UIDSet empty
        data.write(struct.pack("<f", 100.0))  # EffectChance
        data.write(struct.pack("<i", 10))  # LevelMin
        data.write(struct.pack("<i", 50))  # LevelMax
        data.write(struct.pack("<?", False))  # Unique
        data.write(struct.pack("<i", 0))  # MutExID
        data.write(struct.pack("<i", 0))  # BuffMode

        # Effect array (sEffect structures)
        data.write(struct.pack("<i", 1))  # count
        # Single sEffect
        data.write(struct.pack("<i", 1))  # Mode
        data.write(struct.pack("<i", 0))  # BuffMode
        data.write(struct.pack("<i", 1))  # Enhance.ID (Accuracy)
        data.write(struct.pack("<i", 0))  # Enhance.SubID
        data.write(struct.pack("<i", 0))  # Schedule
        data.write(struct.pack("<f", 0.3333))  # Multiplier (33.33%)
        data.write(struct.pack("<?", False))  # No FX

        # Final fields
        data.write(b"\x0fEnhancement.Acc")  # UID (length 15)
        data.write(b"\x00")  # RecipeName empty
        data.write(struct.pack("<?", False))  # Superior
        data.write(struct.pack("<?", False))  # IsProc
        data.write(struct.pack("<?", True))  # IsScalable

        data.seek(0)

        enhancement = parse_enhancement(data)

        assert enhancement.static_index == 1001
        assert enhancement.name == "Accuracy IO"
        assert enhancement.short_name == "Acc IO"
        assert enhancement.description == "Increases accuracy of attacks"
        assert enhancement.type_id == 1
        assert enhancement.sub_type_id == 0
        assert enhancement.class_ids == []  # Empty after removing -1
        assert enhancement.image == "accuracy_io.png"
        assert enhancement.n_id_set == 0
        assert enhancement.uid_set == ""
        assert pytest.approx(enhancement.effect_chance, rel=1e-5) == 100.0
        assert enhancement.level_min == 10
        assert enhancement.level_max == 50
        assert not enhancement.unique
        assert enhancement.mut_ex_id == 0
        assert enhancement.buff_mode == 0
        assert len(enhancement.effects) == 1
        assert enhancement.effects[0].enhance_id == 1
        assert pytest.approx(enhancement.effects[0].multiplier, rel=1e-5) == 0.3333
        assert enhancement.uid == "Enhancement.Acc"
        assert enhancement.recipe_name == ""
        assert not enhancement.superior
        assert not enhancement.is_proc
        assert enhancement.is_scalable

    def test_parse_enhancement_with_class_restrictions(self):
        """Test parsing enhancement with class restrictions."""
        data = io.BytesIO()

        # Basic fields
        data.write(struct.pack("<i", 2001))  # StaticIndex
        data.write(b"\x0eDamage Hamidon")  # Name (length 14)
        data.write(b"\x08Dam Hami")  # ShortName (length 8)
        data.write(b"\x15Hamidon Origin damage")  # Desc (length 21)
        data.write(struct.pack("<i", 5))  # TypeID (HamiO)
        data.write(struct.pack("<i", 1))  # SubTypeID

        # ClassID array with restrictions (count+1)
        data.write(struct.pack("<i", 3))  # count
        data.write(struct.pack("<i", 0))  # Tanker
        data.write(struct.pack("<i", 1))  # Scrapper
        data.write(struct.pack("<i", 5))  # Brute
        data.write(struct.pack("<i", -1))  # terminator

        # Rest of fields
        data.write(b"\x0cdam_hami.png")  # Image (length 12)
        data.write(struct.pack("<i", 0))  # nIDSet
        data.write(b"\x00")  # UIDSet
        data.write(struct.pack("<f", 100.0))  # EffectChance
        data.write(struct.pack("<i", 45))  # LevelMin
        data.write(struct.pack("<i", 50))  # LevelMax
        data.write(struct.pack("<?", True))  # Unique
        data.write(struct.pack("<i", 0))  # MutExID
        data.write(struct.pack("<i", 0))  # BuffMode

        # Multiple effects
        data.write(struct.pack("<i", 2))  # count
        # Effect 1: Damage
        data.write(struct.pack("<i", 1))  # Mode
        data.write(struct.pack("<i", 0))  # BuffMode
        data.write(struct.pack("<i", 2))  # Enhance.ID (Damage)
        data.write(struct.pack("<i", 0))  # Enhance.SubID
        data.write(struct.pack("<i", 0))  # Schedule
        data.write(struct.pack("<f", 0.50))  # Multiplier (50%)
        data.write(struct.pack("<?", False))  # No FX
        # Effect 2: Accuracy
        data.write(struct.pack("<i", 1))  # Mode
        data.write(struct.pack("<i", 0))  # BuffMode
        data.write(struct.pack("<i", 1))  # Enhance.ID (Accuracy)
        data.write(struct.pack("<i", 0))  # Enhance.SubID
        data.write(struct.pack("<i", 0))  # Schedule
        data.write(struct.pack("<f", 0.33))  # Multiplier (33%)
        data.write(struct.pack("<?", False))  # No FX

        # Final fields
        data.write(b"\x0eHamidon.Damage")  # UID (length 14)
        data.write(b"\x00")  # RecipeName
        data.write(struct.pack("<?", False))  # Superior
        data.write(struct.pack("<?", False))  # IsProc
        data.write(struct.pack("<?", False))  # IsScalable

        data.seek(0)

        enhancement = parse_enhancement(data)

        assert enhancement.static_index == 2001
        assert enhancement.name == "Damage Hamidon"
        assert enhancement.type_id == 5  # HamiO
        assert enhancement.unique
        assert len(enhancement.class_ids) == 3
        assert enhancement.class_ids == [0, 1, 5]  # Tanker, Scrapper, Brute
        assert len(enhancement.effects) == 2
        assert enhancement.effects[0].enhance_id == 2  # Damage
        assert enhancement.effects[1].enhance_id == 1  # Accuracy
        assert not enhancement.is_scalable


class TestEnhancementSetParser:
    """Test cases for parsing EnhancementSet records."""

    def test_parse_minimal_enhancement_set(self):
        """Test parsing a minimal enhancement set."""
        data = io.BytesIO()

        # Write EnhancementSet fields
        data.write(struct.pack("<i", 101))  # DisplayIndex
        data.write(b"\x11Thundering Strike")  # DisplayName (length 17)
        data.write(b"\x0dThunderStrike")  # ShortName (length 13)
        data.write(b"\x1fMelee damage set with knockback")  # Desc (length 31)

        # Set type
        data.write(struct.pack("<i", 1))  # SetType (enum)

        # Enhancement indices array
        data.write(struct.pack("<i", 6))  # count (typical set has 6 pieces)
        for i in range(6):
            data.write(struct.pack("<i", 1100 + i))  # Enhancement indices

        # Bonus arrays (simplified for test)
        data.write(struct.pack("<i", 0))  # Bonus count
        data.write(struct.pack("<i", 0))  # BonusMin count
        data.write(struct.pack("<i", 0))  # BonusMax count

        # Special arrays
        data.write(struct.pack("<i", 0))  # SpecialBonus count

        # Final fields
        data.write(b"\x11Set.ThunderStrike")  # UIDSet (length 17)
        data.write(struct.pack("<i", 10))  # LevelMin
        data.write(struct.pack("<i", 50))  # LevelMax

        data.seek(0)

        enh_set = parse_enhancement_set(data)

        assert enh_set.display_index == 101
        assert enh_set.display_name == "Thundering Strike"
        assert enh_set.short_name == "ThunderStrike"
        assert enh_set.description == "Melee damage set with knockback"
        assert enh_set.set_type == 1
        assert len(enh_set.enhancement_indices) == 6
        assert enh_set.enhancement_indices[0] == 1100
        assert enh_set.enhancement_indices[5] == 1105
        assert enh_set.uid_set == "Set.ThunderStrike"
        assert enh_set.level_min == 10
        assert enh_set.level_max == 50

    def test_parse_enhancement_set_with_bonuses(self):
        """Test parsing enhancement set with set bonuses."""
        data = io.BytesIO()

        # Basic fields
        data.write(struct.pack("<i", 201))  # DisplayIndex
        data.write(b"\x10Positron's Blast")  # DisplayName (length 16)
        data.write(b"\x08Positron")  # ShortName (length 8)
        data.write(b"\x15Ranged AoE damage set")  # Desc (length 21)
        data.write(struct.pack("<i", 2))  # SetType

        # Enhancement indices (5 pieces)
        data.write(struct.pack("<i", 5))  # count
        for i in range(5):
            data.write(struct.pack("<i", 2000 + i))

        # Bonus arrays (simplified - would be complex Power structures)
        data.write(struct.pack("<i", 4))  # Bonus count (2-5 piece bonuses)
        for i in range(4):
            data.write(struct.pack("<i", 3000 + i))  # Bonus power indices

        # BonusMin array - minimum pieces for each bonus
        data.write(struct.pack("<i", 4))  # count
        data.write(struct.pack("<i", 2))  # 2 pieces for first bonus
        data.write(struct.pack("<i", 3))  # 3 pieces
        data.write(struct.pack("<i", 4))  # 4 pieces
        data.write(struct.pack("<i", 5))  # 5 pieces

        # BonusMax array (empty in this case)
        data.write(struct.pack("<i", 0))  # count

        # SpecialBonus array (for PVP/exemplar bonuses)
        data.write(struct.pack("<i", 1))  # count
        data.write(struct.pack("<i", 4000))  # Special bonus index

        # Final fields
        data.write(b"\x0cSet.Positron")  # UIDSet (length 12)
        data.write(struct.pack("<i", 20))  # LevelMin
        data.write(struct.pack("<i", 50))  # LevelMax

        data.seek(0)

        enh_set = parse_enhancement_set(data)

        assert enh_set.display_index == 201
        assert enh_set.display_name == "Positron's Blast"
        assert len(enh_set.enhancement_indices) == 5
        assert len(enh_set.bonuses) == 4
        assert enh_set.bonuses[0] == 3000
        assert len(enh_set.bonus_min) == 4
        assert enh_set.bonus_min[0] == 2  # First bonus at 2 pieces
        assert enh_set.bonus_min[3] == 5  # Last bonus at 5 pieces
        assert len(enh_set.special_bonuses) == 1
        assert enh_set.special_bonuses[0] == 4000
