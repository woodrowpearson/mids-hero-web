"""Tests for parsing Archetype records from MHD files."""

import io
import struct

import pytest

from app.mhd_parser.archetype_parser import parse_archetype


class TestArchetypeParser:
    """Test cases for parsing Archetype records."""

    def test_parse_minimal_archetype(self):
        """Test parsing a minimal archetype with required fields only."""
        # Create test data using the binary format
        data = io.BytesIO()

        # Write fields in order
        # 1. DisplayName
        data.write(b"\x06Tanker")  # string length 6 + "Tanker"

        # 2. Hitpoints (Int32)
        data.write(struct.pack("<i", 1000))

        # 3. HPCap (float)
        data.write(struct.pack("<f", 1500.0))

        # 4. DescLong (string)
        data.write(b"\x0aTank class")  # length 10

        # 5. ResCap (float)
        data.write(struct.pack("<f", 90.0))

        # 6. numOrigins (Int32) + Origin array
        data.write(struct.pack("<i", 3))  # 3 origins
        data.write(b"\x07Natural")  # Origin[0]
        data.write(b"\x06Mutant")  # Origin[1]
        data.write(b"\x04Tech")  # Origin[2]
        data.write(b"\x00")  # Origin[3] - extra empty string

        # 7. ClassName (string)
        data.write(b"\x0cClass_Tanker")

        # 8. ClassType (Int32)
        data.write(struct.pack("<i", 1))  # Hero

        # 9. Column (Int32)
        data.write(struct.pack("<i", 0))

        # 10. DescShort (string)
        data.write(b"\x04Tank")

        # 11. PrimaryGroup (string)
        data.write(b"\x07Defense")

        # 12. SecondaryGroup (string)
        data.write(b"\x05Melee")

        # 13. Playable (Boolean)
        data.write(b"\x01")  # True

        # 14. Various caps (7 floats)
        for cap_value in [100.0, 200.0, 300.0, 400.0, 500.0, 95.0, 10.0]:
            data.write(struct.pack("<f", cap_value))

        # 15. Base stats (3 floats)
        for base_value in [1.67, 0.1, 4.0]:
            data.write(struct.pack("<f", base_value))

        # 16. PerceptionCap (float)
        data.write(struct.pack("<f", 1000.0))

        data.seek(0)

        # Parse the archetype
        archetype = parse_archetype(data)

        # Verify all fields
        assert archetype.display_name == "Tanker"
        assert archetype.hitpoints == 1000
        assert archetype.hp_cap == 1500.0
        assert archetype.desc_long == "Tank class"
        assert archetype.res_cap == 90.0
        assert archetype.origins == ["Natural", "Mutant", "Tech"]
        assert archetype.class_name == "Class_Tanker"
        assert archetype.class_type == 1
        assert archetype.column == 0
        assert archetype.desc_short == "Tank"
        assert archetype.primary_group == "Defense"
        assert archetype.secondary_group == "Melee"
        assert archetype.playable
        assert archetype.recharge_cap == 100.0
        assert archetype.damage_cap == 200.0
        assert archetype.recovery_cap == 300.0
        assert archetype.regen_cap == 400.0
        assert archetype.threat_cap == 500.0
        assert archetype.resist_cap == 95.0
        assert archetype.damage_resist_cap == 10.0
        assert pytest.approx(archetype.base_recovery, rel=1e-5) == 1.67
        assert pytest.approx(archetype.base_regen, rel=1e-5) == 0.1
        assert pytest.approx(archetype.base_threat, rel=1e-5) == 4.0
        assert archetype.perception_cap == 1000.0

    def test_parse_archetype_with_special_origins(self):
        """Test parsing archetype with edge cases in origin array."""
        data = io.BytesIO()

        # Minimal data up to origins
        data.write(b"\x05Brute")  # DisplayName
        data.write(struct.pack("<i", 1200))  # Hitpoints
        data.write(struct.pack("<f", 1800.0))  # HPCap
        data.write(b"\x00")  # Empty DescLong
        data.write(struct.pack("<f", 85.0))  # ResCap

        # Special case: 0 origins (should still read one empty string)
        data.write(struct.pack("<i", 0))  # numOrigins = 0
        data.write(b"\x00")  # Origin[0] - still need one string

        # Rest of required fields with minimal data
        data.write(b"\x0bClass_Brute")  # ClassName
        data.write(struct.pack("<i", 2))  # ClassType = Villain
        data.write(struct.pack("<i", 1))  # Column
        data.write(b"\x05Brute")  # DescShort
        data.write(b"\x05Melee")  # PrimaryGroup
        data.write(b"\x07Defense")  # SecondaryGroup
        data.write(b"\x01")  # Playable

        # Caps and base stats
        for _ in range(7):
            data.write(struct.pack("<f", 100.0))
        for _ in range(3):
            data.write(struct.pack("<f", 1.0))
        data.write(struct.pack("<f", 800.0))  # PerceptionCap

        data.seek(0)

        archetype = parse_archetype(data)

        assert archetype.display_name == "Brute"
        assert archetype.origins == []  # Empty list when numOrigins = 0
        assert archetype.class_type == 2  # Villain

    def test_parse_archetype_with_unicode(self):
        """Test parsing archetype with Unicode characters."""
        data = io.BytesIO()

        # Unicode display name
        unicode_name = "Héros™"
        name_bytes = unicode_name.encode("utf-8")
        data.write(bytes([len(name_bytes)]))
        data.write(name_bytes)

        # Continue with other fields...
        data.write(struct.pack("<i", 1000))  # Hitpoints
        data.write(struct.pack("<f", 1500.0))  # HPCap

        # Unicode description
        unicode_desc = "Défenseur avec résistance élevée"
        desc_bytes = unicode_desc.encode("utf-8")
        data.write(bytes([len(desc_bytes)]))
        data.write(desc_bytes)

        # Rest of minimal required fields
        data.write(struct.pack("<f", 90.0))  # ResCap
        data.write(struct.pack("<i", 1))  # numOrigins
        data.write(b"\x07Natural")  # Origin[0]
        data.write(b"\x00")  # Origin[1]
        data.write(b"\x0cClass_Tanker")  # ClassName
        data.write(struct.pack("<i", 1))  # ClassType
        data.write(struct.pack("<i", 0))  # Column
        data.write(b"\x04Tank")  # DescShort
        data.write(b"\x07Defense")  # PrimaryGroup
        data.write(b"\x05Melee")  # SecondaryGroup
        data.write(b"\x01")  # Playable

        # Caps and base stats
        for _ in range(7):
            data.write(struct.pack("<f", 100.0))
        for _ in range(3):
            data.write(struct.pack("<f", 1.0))
        data.write(struct.pack("<f", 1000.0))

        data.seek(0)

        archetype = parse_archetype(data)

        assert archetype.display_name == "Héros™"
        assert archetype.desc_long == "Défenseur avec résistance élevée"

    def test_parse_archetype_eof_handling(self):
        """Test handling of EOF while parsing archetype."""
        # Create incomplete data
        data = io.BytesIO()
        data.write(b"\x06Tanker")  # DisplayName
        data.write(struct.pack("<i", 1000))  # Hitpoints
        # Missing rest of fields

        data.seek(0)

        with pytest.raises(EOFError):
            parse_archetype(data)

    def test_parse_non_playable_archetype(self):
        """Test parsing non-playable archetype (NPC class)."""
        data = io.BytesIO()

        # Build data step by step with verification
        # DisplayName
        data.write(b"\x08")  # length
        data.write(b"NPC_Boss")

        # Numeric fields
        data.write(struct.pack("<i", 5000))  # Hitpoints
        data.write(struct.pack("<f", 10000.0))  # HPCap

        # DescLong
        data.write(b"\x12")  # length 18
        data.write(b"Non-playable enemy")

        data.write(struct.pack("<f", 95.0))  # ResCap
        data.write(struct.pack("<i", 0))  # numOrigins
        data.write(b"\x00")  # Origin[0] - empty string

        # ClassName
        data.write(b"\x0e")  # length 14
        data.write(b"Class_NPC_Boss")

        data.write(struct.pack("<i", 3))  # ClassType
        data.write(struct.pack("<i", -1))  # Column

        # Short strings
        data.write(b"\x03NPC")  # DescShort
        data.write(b"\x00")  # Empty PrimaryGroup
        data.write(b"\x00")  # Empty SecondaryGroup
        data.write(b"\x00")  # Playable = False

        # All caps as individual writes
        data.write(struct.pack("<f", 1000.0))  # RechargeCap
        data.write(struct.pack("<f", 2000.0))  # DamageCap
        data.write(struct.pack("<f", 3000.0))  # RecoveryCap
        data.write(struct.pack("<f", 4000.0))  # RegenCap
        data.write(struct.pack("<f", 5000.0))  # ThreatCap
        data.write(struct.pack("<f", 100.0))  # ResistCap
        data.write(struct.pack("<f", 90.0))  # DamageResistCap

        # Base stats
        data.write(struct.pack("<f", 10.0))  # BaseRecovery
        data.write(struct.pack("<f", 5.0))  # BaseRegen
        data.write(struct.pack("<f", 20.0))  # BaseThreat

        # Final cap
        data.write(struct.pack("<f", 2000.0))  # PerceptionCap

        data.seek(0)

        archetype = parse_archetype(data)

        assert archetype.display_name == "NPC_Boss"
        assert archetype.hitpoints == 5000
        assert not archetype.playable
        assert archetype.class_type == 3
        assert archetype.column == -1
        assert archetype.primary_group == ""
        assert archetype.secondary_group == ""

    @pytest.mark.parametrize(
        "num_origins,expected_count",
        [
            (0, 0),  # 0 origins = empty list
            (1, 1),  # 1 origin
            (5, 5),  # Standard 5 origins
            (10, 10),  # More than usual
        ],
    )
    def test_origin_array_handling(self, num_origins, expected_count):
        """Test that origin array is handled correctly with count+1 pattern."""
        data = io.BytesIO()

        # Write minimal archetype data up to origins
        data.write(b"\x04Test")  # DisplayName
        data.write(struct.pack("<i", 1000))  # Hitpoints
        data.write(struct.pack("<f", 1500.0))  # HPCap
        data.write(b"\x00")  # Empty DescLong
        data.write(struct.pack("<f", 90.0))  # ResCap

        # Write origins
        data.write(struct.pack("<i", num_origins))
        for i in range(num_origins):
            origin = f"Origin{i}"
            data.write(bytes([len(origin)]))
            data.write(origin.encode())
        data.write(b"\x00")  # Extra empty string (count+1)

        # Write remaining required fields
        data.write(b"\x05Class")  # ClassName
        data.write(struct.pack("<i", 1))  # ClassType
        data.write(struct.pack("<i", 0))  # Column
        data.write(b"\x04Test")  # DescShort
        data.write(b"\x04Test")  # PrimaryGroup
        data.write(b"\x04Test")  # SecondaryGroup
        data.write(b"\x01")  # Playable

        # Caps and base stats
        for _ in range(7 + 3):
            data.write(struct.pack("<f", 100.0))
        data.write(struct.pack("<f", 1000.0))

        data.seek(0)

        archetype = parse_archetype(data)

        assert len(archetype.origins) == expected_count
        if expected_count > 0:
            assert archetype.origins[0] == "Origin0"
            assert archetype.origins[-1] == f"Origin{expected_count-1}"
