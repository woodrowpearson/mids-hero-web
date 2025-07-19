"""Integration tests for MHD parser with real file samples."""

import io
import json
import struct
from typing import Any

from app.mhd_parser.enhancement_database_parser import (
    parse_enhancement_database,
)
from app.mhd_parser.main_database_parser import MainDatabase, parse_main_database
from app.mhd_parser.text_mhd_parser import (
    FileFormat,
    detect_file_format,
    parse_text_mhd,
)


class TestMhdParserIntegration:
    """Integration tests for complete MHD parsing workflow."""

    def test_parse_small_main_database(self):
        """Test parsing a small but complete main database."""
        data = io.BytesIO()

        # Create a small but complete database
        self._write_main_database_sample(data)
        data.seek(0)

        # Parse the database
        db = parse_main_database(data)

        # Validate structure
        assert db.header == "Mids Reborn Powers Database"
        assert db.version == "2.9.0.0"
        assert db.issue == 27

        # Validate counts
        assert len(db.archetypes) == 2
        assert len(db.powersets) == 4  # 2 primary + 2 secondary
        assert len(db.powers) == 8  # 4 powers per set
        assert len(db.summons) == 1

        # Validate specific content
        assert db.archetypes[0].display_name == "Blaster"
        assert db.archetypes[1].display_name == "Tanker"

        # Check powerset relationships
        blaster_primary = [
            ps for ps in db.powersets if ps.archetype_index == 0 and ps.set_type == 0
        ]
        assert len(blaster_primary) == 1
        assert blaster_primary[0].display_name == "Fire Blast"

        # Check power relationships
        fire_powers = [p for p in db.powers if p.set_name == "Fire_Blast"]
        assert len(fire_powers) == 4
        power_names = [p.display_name for p in fire_powers]
        assert "Fire Bolt" in power_names
        assert "Fire Ball" in power_names

    def test_parse_enhancement_database_integration(self):
        """Test parsing enhancement database with sets."""
        data = io.BytesIO()

        # Create enhancement database sample
        self._write_enhancement_database_sample(data)
        data.seek(0)

        # Parse the database
        db = parse_enhancement_database(data)

        # Validate structure
        assert len(db.enhancements) == 6  # 6 enhancements
        assert len(db.enhancement_sets) == 1  # 1 set

        # Validate enhancement set references
        enh_set = db.enhancement_sets[0]
        assert enh_set.display_name == "Thunderstrike"
        assert len(enh_set.enhancement_indices) == 6

        # Validate that enhancement indices match actual enhancements
        for i, idx in enumerate(enh_set.enhancement_indices):
            assert 0 <= idx < len(db.enhancements)
            # In our sample, indices are 0-5
            assert idx == i

    def test_cross_reference_validation(self):
        """Test validation of cross-references between entities."""
        # Create main database with archetype/powerset references
        main_data = io.BytesIO()
        self._write_main_database_sample(main_data)
        main_data.seek(0)
        main_db = parse_main_database(main_data)

        # Validate powerset archetype references
        for powerset in main_db.powersets:
            # Check archetype index is valid (or -1 for pool powers)
            if powerset.archetype_index >= 0:
                assert powerset.archetype_index < len(main_db.archetypes)

        # Validate power requirement references
        for power in main_db.powers:
            # Check power ID references in requirements
            for power_id in power.requirement.power_ids:
                # Power IDs should be valid indices
                assert 0 <= power_id < len(main_db.powers)

    def test_json_export_functionality(self):
        """Test exporting parsed data to JSON for comparison."""
        # Parse a sample database
        data = io.BytesIO()
        self._write_main_database_sample(data)
        data.seek(0)
        db = parse_main_database(data)

        # Convert to JSON-serializable format
        json_data = self._database_to_json(db)

        # Validate JSON structure
        assert "header" in json_data
        assert "version" in json_data
        assert "archetypes" in json_data
        assert "powersets" in json_data
        assert "powers" in json_data
        assert "summons" in json_data

        # Validate JSON serialization works
        json_str = json.dumps(json_data, indent=2)
        assert len(json_str) > 0

        # Validate round-trip
        parsed_json = json.loads(json_str)
        assert parsed_json["header"] == db.header
        assert len(parsed_json["archetypes"]) == len(db.archetypes)

    def test_text_file_integration(self):
        """Test parsing text-based MHD files."""
        # Test Origins.mhd format
        origins_data = io.BytesIO(
            b"""Version 1.5.0
Science
Technology
Mutation
Magic
Natural"""
        )

        # Detect format
        format_type = detect_file_format(origins_data)
        assert format_type == FileFormat.TEXT_WITH_VERSION

        # Parse file
        origins = parse_text_mhd(origins_data)
        assert origins.version == "1.5.0"
        assert len(origins.data) == 5
        assert origins.data[0] == ["Science"]
        assert origins.data[4] == ["Natural"]

        # Test NLevels.mhd format (TSV)
        levels_data = io.BytesIO(
            b"""Level\tExperience\tInfluence
1\t0\t0
2\t106\t50
3\t337\t150"""
        )

        format_type = detect_file_format(levels_data)
        assert format_type == FileFormat.TEXT_TSV

        levels = parse_text_mhd(levels_data)
        assert levels.headers == ["Level", "Experience", "Influence"]
        assert len(levels.data) == 3
        assert levels.data[1] == ["2", "106", "50"]

    def test_performance_benchmark(self):
        """Test that parsing completes within performance targets."""
        import time

        # Create a larger database for performance testing
        data = io.BytesIO()
        self._write_large_database_sample(data)
        data.seek(0)

        # Measure parsing time
        start_time = time.time()
        db = parse_main_database(data)
        end_time = time.time()

        parse_time = end_time - start_time

        # Validate it completes in reasonable time (< 1 second for test data)
        assert parse_time < 1.0

        # Validate correct parsing
        assert len(db.archetypes) == 10
        assert len(db.powersets) == 40  # 4 per archetype
        assert len(db.powers) == 200  # 5 per powerset

    # Helper methods

    def _write_main_database_sample(self, stream: io.BytesIO):
        """Write a small but complete main database sample."""
        # Header
        header = "Mids Reborn Powers Database"
        stream.write(bytes([len(header)]))
        stream.write(header.encode())

        # Version
        version = "2.9.0.0"
        stream.write(bytes([len(version)]))
        stream.write(version.encode())

        # Date, issue info
        stream.write(struct.pack("<i", 20231215))
        stream.write(struct.pack("<i", 27))
        stream.write(struct.pack("<i", 7))
        stream.write(b"\x06Page 7")

        # ARCHETYPES section
        marker = "BEGIN:ARCHETYPES"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 2))  # 2 archetypes

        # Archetype 1: Blaster
        self._write_archetype(stream, "Blaster", 0, "Ranged_Damage")

        # Archetype 2: Tanker
        self._write_archetype(stream, "Tanker", 1, "Melee_Tanker")

        # POWERSETS section
        marker = "BEGIN:POWERSETS"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 4))  # 4 powersets

        # Blaster powersets
        self._write_powerset(stream, "Fire Blast", 0, 0, "Fire_Blast")
        self._write_powerset(stream, "Fire Manipulation", 0, 1, "Fire_Manipulation")

        # Tanker powersets
        self._write_powerset(stream, "Invulnerability", 1, 0, "Invulnerability")
        self._write_powerset(stream, "Super Strength", 1, 1, "Super_Strength")

        # POWERS section
        marker = "BEGIN:POWERS"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 8))  # 8 powers

        # Fire Blast powers
        self._write_power(stream, "Fire Bolt", "Fire_Blast", 1)
        self._write_power(stream, "Fire Ball", "Fire_Blast", 2)
        self._write_power(stream, "Fire Breath", "Fire_Blast", 8)
        self._write_power(stream, "Inferno", "Fire_Blast", 32)

        # Fire Manipulation powers
        self._write_power(stream, "Ring of Fire", "Fire_Manipulation", 1)
        self._write_power(stream, "Fire Sword", "Fire_Manipulation", 2)
        self._write_power(stream, "Combustion", "Fire_Manipulation", 6)
        self._write_power(stream, "Burn", "Fire_Manipulation", 28)

        # SUMMONS section
        marker = "BEGIN:SUMMONS"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 1))  # 1 summon

        # Fire Imp summon
        stream.write(b"\x0bPet.FireImp")
        stream.write(b"\x08Fire Imp")
        stream.write(struct.pack("<i", 1))  # Pet type
        stream.write(b"\x0bPet_FireImp")
        stream.write(struct.pack("<i", 0))  # No powersets
        stream.write(struct.pack("<i", 0))  # No upgrades

    def _write_archetype(
        self, stream: io.BytesIO, name: str, index: int, class_name: str
    ):
        """Write a minimal archetype record."""
        stream.write(bytes([len(name)]))
        stream.write(name.encode())
        stream.write(struct.pack("<i", 1000 + index * 100))  # HP
        stream.write(struct.pack("<f", 1500.0 + index * 100))  # HPCap
        stream.write(b"\x00")  # DescLong empty
        stream.write(struct.pack("<f", 90.0))  # ResCap
        stream.write(struct.pack("<i", 5))  # 5 origins
        # Write origin strings
        origins = ["Science", "Technology", "Magic", "Mutation", "Natural"]
        for i in range(6):  # count+1
            if i < 5:
                origin = origins[i]
                stream.write(bytes([len(origin)]))
                stream.write(origin.encode())
            else:
                stream.write(b"\x00")  # Empty string
        stream.write(bytes([len(class_name)]))
        stream.write(class_name.encode())
        stream.write(struct.pack("<i", index))  # ClassType
        stream.write(struct.pack("<i", index))  # Column
        stream.write(b"\x04Name")  # DescShort
        stream.write(b"\x05Group")  # PrimaryGroup
        stream.write(b"\x05Group")  # SecondaryGroup
        stream.write(b"\x01")  # Playable
        for _ in range(7):  # Caps
            stream.write(struct.pack("<f", 100.0))
        for _ in range(3):  # Base stats
            stream.write(struct.pack("<f", 1.0))
        stream.write(struct.pack("<f", 1000.0))  # PerceptionCap

    def _write_powerset(
        self, stream: io.BytesIO, name: str, arch_idx: int, set_type: int, set_name: str
    ):
        """Write a minimal powerset record."""
        stream.write(bytes([len(name)]))
        stream.write(name.encode())
        stream.write(struct.pack("<i", arch_idx))
        stream.write(struct.pack("<i", set_type))
        stream.write(b"\x08icon.png")
        stream.write(b"\x00")  # FullName empty (will trigger fallback)
        stream.write(bytes([len(set_name)]))
        stream.write(set_name.encode())
        stream.write(b"\x0bDescription")
        stream.write(b"\x00")  # SubName
        stream.write(b"\x05Class")  # ATClass
        stream.write(b"\x03UID")  # UIDTrunkSet
        stream.write(b"\x00")  # UIDLinkSecondary
        stream.write(struct.pack("<i", 0))  # No mutex
        stream.write(b"\x00")  # Extra string
        stream.write(struct.pack("<i", 0))  # Extra int

    def _write_power(self, stream: io.BytesIO, name: str, set_name: str, level: int):
        """Write a minimal power record."""
        # Basic info
        full_name = f"{set_name}.{name.replace(' ', '_')}"
        stream.write(bytes([len(full_name)]))
        stream.write(full_name.encode())
        stream.write(b"\x05Group")  # GroupName
        stream.write(bytes([len(set_name)]))
        stream.write(set_name.encode())
        stream.write(bytes([len(name)]))
        stream.write(name.encode())
        stream.write(bytes([len(name)]))
        stream.write(name.encode())  # DisplayName
        stream.write(struct.pack("<i", level))  # Available level

        # Minimal requirement
        stream.write(b"\x00")  # ClassName
        stream.write(b"\x00")  # ClassNameNot
        stream.write(struct.pack("<i", 0))  # ClassesRequired
        stream.write(struct.pack("<i", 0))  # ClassesDisallowed
        stream.write(struct.pack("<i", 0))  # PowerID
        stream.write(struct.pack("<i", 0))  # PowerIDNot

        # Power type and basic stats
        stream.write(struct.pack("<i", 1))  # Click
        stream.write(struct.pack("<f", 1.0))  # Accuracy
        stream.write(struct.pack("<i", 0))  # AttackTypes
        stream.write(struct.pack("<i", 0))  # GroupMembership count
        stream.write(struct.pack("<i", 1))  # EntitiesAffected (Foe)
        stream.write(struct.pack("<i", 0))  # EntitiesAutoHit
        stream.write(struct.pack("<i", 1))  # Target
        stream.write(struct.pack("<?", False))  # TargetLineSpecialRange
        stream.write(struct.pack("<f", 80.0))  # Range
        stream.write(struct.pack("<f", 0.0))  # RangeSecondary

        # Costs and timing
        stream.write(struct.pack("<f", 5.2))  # EndCost
        stream.write(struct.pack("<f", 0.0))  # InterruptTime
        stream.write(struct.pack("<f", 1.0))  # CastTime
        stream.write(struct.pack("<f", 4.0))  # RechargeTime
        stream.write(struct.pack("<f", 4.0))  # BaseRechargeTime
        stream.write(struct.pack("<f", 0.0))  # ActivatePeriod

        # Area effect
        stream.write(struct.pack("<i", 0))  # EffectArea
        stream.write(struct.pack("<f", 0.0))  # Radius
        stream.write(struct.pack("<i", 0))  # Arc
        stream.write(struct.pack("<i", 1))  # MaxTargets

        # Rest of minimal fields
        stream.write(b"\x00")  # MaxBoosts
        stream.write(struct.pack("<i", 0))  # CastFlags
        stream.write(struct.pack("<i", 0))  # AIReport
        stream.write(struct.pack("<i", 0))  # NumEffects
        stream.write(struct.pack("<i", 0))  # BoostsAllowed count

        # More numeric fields
        for _ in range(7):
            stream.write(struct.pack("<f", 0.0))

        # Strings and arrays
        stream.write(b"\x00")  # DescShort
        stream.write(b"\x00")  # DescLong
        stream.write(struct.pack("<i", 0))  # SetTypes
        stream.write(struct.pack("<i", 0))  # ClickBuff
        stream.write(struct.pack("<?", False))  # AlwaysToggle
        stream.write(struct.pack("<i", 0))  # Level
        stream.write(struct.pack("<?", False))  # AllowFrontLoading
        stream.write(struct.pack("<?", False))  # IgnoreEnh
        stream.write(struct.pack("<?", False))  # IgnoreSetBonus
        stream.write(struct.pack("<?", False))  # BoostBoostable
        stream.write(struct.pack("<?", False))  # BoostAlways
        stream.write(struct.pack("<i", 0))  # UIDSubPower
        stream.write(struct.pack("<i", 0))  # IgnoreStrength
        stream.write(struct.pack("<i", 0))  # IgnoreBuff
        stream.write(struct.pack("<?", False))  # SkipMax
        stream.write(struct.pack("<i", 0))  # DisplayLocation
        stream.write(struct.pack("<?", False))  # MutexAuto
        stream.write(struct.pack("<?", False))  # MutexIgnore
        stream.write(struct.pack("<?", False))  # AbsorbSummonEffects
        stream.write(struct.pack("<?", False))  # AbsorbSummonAttributes
        stream.write(struct.pack("<?", False))  # ShowSummonAnyway
        stream.write(struct.pack("<?", False))  # NeverAutoUpdate
        stream.write(struct.pack("<?", False))  # NeverAutoUpdateRequirements
        stream.write(struct.pack("<?", False))  # IncludeFlag
        stream.write(b"\x00")  # ForcedClass
        stream.write(struct.pack("<i", 0))  # SortOverride
        stream.write(struct.pack("<?", False))  # BoostBoostSpecialAllowed
        stream.write(struct.pack("<i", 0))  # Effects count
        stream.write(struct.pack("<?", False))  # HiddenPower

    def _write_enhancement_database_sample(self, stream: io.BytesIO):
        """Write a small enhancement database sample."""
        # Header
        header = "Mids Reborn Enhancement Database"
        stream.write(bytes([len(header)]))
        stream.write(header.encode())

        # Version
        version = "1.0.0.0"
        stream.write(bytes([len(version)]))
        stream.write(version.encode())

        # Date
        stream.write(struct.pack("<i", 20231215))

        # Enhancements
        stream.write(struct.pack("<i", 6))  # 6 enhancements

        # Write 6 enhancements for a set
        for i in range(6):
            stream.write(struct.pack("<i", 1000 + i))  # StaticIndex
            name = f"Thunderstrike: {['Acc/Dmg', 'Dmg/End', 'Dmg/Rech', 'Acc/End/Rech', 'Acc/Dmg/End/Rech', 'Dmg/End/Rech'][i]}"
            stream.write(bytes([len(name)]))
            stream.write(name.encode())
            short = f"TS:{i + 1}"
            stream.write(bytes([len(short)]))
            stream.write(short.encode())
            stream.write(b"\x04Desc")
            stream.write(struct.pack("<i", 3))  # TypeID (Set IO)
            stream.write(struct.pack("<i", i))  # SubTypeID
            stream.write(struct.pack("<i", 0))  # ClassID count
            stream.write(struct.pack("<i", -1))  # Terminator
            stream.write(b"\x08icon.png")
            stream.write(struct.pack("<i", 0))  # nIDSet
            stream.write(b"\x0dThunderstrike")  # UIDSet
            stream.write(struct.pack("<f", 100.0))
            stream.write(struct.pack("<i", 10))
            stream.write(struct.pack("<i", 50))
            stream.write(struct.pack("<?", False))
            stream.write(struct.pack("<i", 0))
            stream.write(struct.pack("<i", 0))
            stream.write(struct.pack("<i", 0))  # No effects
            stream.write(bytes([len(f"Set.Thunderstrike.{i}")]))
            stream.write(f"Set.Thunderstrike.{i}".encode())
            stream.write(b"\x00")  # RecipeName
            stream.write(struct.pack("<?", False))
            stream.write(struct.pack("<?", False))
            stream.write(struct.pack("<?", True))

        # Enhancement sets
        stream.write(struct.pack("<i", 1))  # 1 set

        # Thunderstrike set
        stream.write(struct.pack("<i", 100))  # DisplayIndex
        stream.write(b"\x0dThunderstrike")  # DisplayName
        stream.write(b"\x02TS")  # ShortName
        stream.write(b"\x0cMelee damage")  # Desc
        stream.write(struct.pack("<i", 1))  # SetType
        stream.write(struct.pack("<i", 6))  # 6 pieces
        for i in range(6):
            stream.write(struct.pack("<i", i))  # Enhancement indices
        # Bonuses
        stream.write(struct.pack("<i", 5))  # 5 bonuses
        for i in range(5):
            stream.write(struct.pack("<i", 5000 + i))
        # BonusMin
        stream.write(struct.pack("<i", 5))
        for i in range(5):
            stream.write(struct.pack("<i", i + 2))  # 2-6 pieces
        # BonusMax
        stream.write(struct.pack("<i", 0))
        # SpecialBonus
        stream.write(struct.pack("<i", 0))
        # Final
        stream.write(b"\x11Set.Thunderstrike")
        stream.write(struct.pack("<i", 10))
        stream.write(struct.pack("<i", 50))

    def _write_large_database_sample(self, stream: io.BytesIO):
        """Write a larger database for performance testing."""
        # Header
        header = "Mids Reborn Powers Database"
        stream.write(bytes([len(header)]))
        stream.write(header.encode())
        version = "2.9.0.0"
        stream.write(bytes([len(version)]))
        stream.write(version.encode())
        stream.write(struct.pack("<i", 20231215))
        stream.write(struct.pack("<i", 27))
        stream.write(struct.pack("<i", 7))
        stream.write(b"\x06Page 7")

        # 10 archetypes
        marker = "BEGIN:ARCHETYPES"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 10))

        for i in range(10):
            self._write_archetype(stream, f"Archetype{i}", i, f"Class_{i}")

        # 40 powersets (4 per archetype)
        marker = "BEGIN:POWERSETS"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 40))

        for arch in range(10):
            for set_idx in range(4):
                set_type = set_idx % 2  # Alternate primary/secondary
                self._write_powerset(
                    stream,
                    f"Set_{arch}_{set_idx}",
                    arch,
                    set_type,
                    f"Set_{arch}_{set_idx}",
                )

        # 200 powers (5 per powerset)
        marker = "BEGIN:POWERS"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 200))

        for ps in range(40):
            for p in range(5):
                self._write_power(
                    stream, f"Power_{ps}_{p}", f"Set_{ps // 4}_{ps % 4}", p + 1
                )

        # Empty summons
        marker = "BEGIN:SUMMONS"
        stream.write(bytes([len(marker)]))
        stream.write(marker.encode())
        stream.write(struct.pack("<i", 0))

    def _database_to_json(self, db: MainDatabase) -> dict[str, Any]:
        """Convert a database object to JSON-serializable format."""
        return {
            "header": db.header,
            "version": db.version,
            "date": db.date if isinstance(db.date, int) else db.date.isoformat(),
            "issue": db.issue,
            "page_vol": db.page_vol,
            "page_vol_text": db.page_vol_text,
            "archetypes": [
                {
                    "display_name": a.display_name,
                    "hitpoints": a.hitpoints,
                    "class_name": a.class_name,
                    "playable": a.playable,
                }
                for a in db.archetypes
            ],
            "powersets": [
                {
                    "display_name": ps.display_name,
                    "archetype_index": ps.archetype_index,
                    "set_type": ps.set_type,
                    "set_name": ps.set_name,
                    "full_name": ps.full_name,
                }
                for ps in db.powersets
            ],
            "powers": [
                {
                    "full_name": p.full_name,
                    "display_name": p.display_name,
                    "set_name": p.set_name,
                    "available": p.available,
                    "power_type": p.power_type.value,
                }
                for p in db.powers
            ],
            "summons": [
                {
                    "uid": s.uid,
                    "display_name": s.display_name,
                    "entity_type": s.entity_type,
                }
                for s in db.summons
            ],
        }
