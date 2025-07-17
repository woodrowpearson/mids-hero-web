"""Tests for parsing Powerset records from MHD files."""

import io
import struct
from dataclasses import dataclass
from typing import List, Tuple

import pytest

from app.mhd_parser.powerset_parser import parse_powerset, Powerset, PowersetType


class TestPowersetParser:
    """Test cases for parsing Powerset records."""
    
    def test_parse_minimal_powerset(self):
        """Test parsing a minimal powerset with required fields only."""
        data = io.BytesIO()
        
        # Write fields in order
        # 1. DisplayName
        data.write(b'\x0BSword Melee')  # length 11
        
        # 2. nArchetype (Int32) - archetype index
        data.write(struct.pack('<i', 0))  # Tanker
        
        # 3. SetType (Int32 as enum)
        data.write(struct.pack('<i', 0))  # Primary
        
        # 4. ImageName (string)
        data.write(b'\x0FSword_Melee.png')  # length 15
        
        # 5. FullName (string) - empty, should fallback
        data.write(b'\x00')
        
        # 6. SetName (string)
        data.write(b'\x0BSword_Melee')
        
        # 7. Description (string)
        data.write(b'\x1BSlashing attacks with sword')  # length 27
        
        # 8. SubName (string)
        data.write(b'\x00')  # empty
        
        # 9. ATClass (string)
        data.write(b'\x0CTanker_Melee')  # length 12
        
        # 10. UIDTrunkSet (string)
        data.write(b'\x09Melee_Set')  # length 9
        
        # 11. UIDLinkSecondary (string)
        data.write(b'\x00')  # empty
        
        # 12. numMutex (Int32) + mutex arrays
        data.write(struct.pack('<i', 0))  # no mutex
        data.write(b'\x00')  # empty string (count+1)
        data.write(struct.pack('<i', 0))  # empty int (count+1)
        
        data.seek(0)
        
        # Parse the powerset
        powerset = parse_powerset(data)
        
        # Verify all fields
        assert powerset.display_name == "Sword Melee"
        assert powerset.archetype_index == 0
        assert powerset.set_type == PowersetType.PRIMARY
        assert powerset.image_name == "Sword_Melee.png"
        assert powerset.full_name == "Orphan.Sword Melee"  # Fallback applied
        assert powerset.set_name == "Sword_Melee"
        assert powerset.description == "Slashing attacks with sword"
        assert powerset.sub_name == ""
        assert powerset.at_class == "Tanker_Melee"
        assert powerset.uid_trunk_set == "Melee_Set"
        assert powerset.uid_link_secondary == ""
        assert powerset.mutex_list == []
    
    def test_parse_powerset_with_mutex(self):
        """Test parsing powerset with mutex (mutually exclusive) powersets."""
        data = io.BytesIO()
        
        # Standard fields
        data.write(b'\x0EWeapon Mastery')  # DisplayName
        data.write(struct.pack('<i', 5))  # nArchetype - Scrapper
        data.write(struct.pack('<i', 3))  # SetType - Epic
        data.write(b'\x15Weapon_Mastery_01.png')  # ImageName
        data.write(b'\x17Scrapper.Weapon_Mastery')  # FullName (no fallback needed) - length 23
        data.write(b'\x0EWeapon_Mastery')  # SetName
        data.write(b'\x20Master various weapon techniques')  # Description - length 32
        data.write(b'\x04Epic')  # SubName
        data.write(b'\x0DScrapper_Epic')  # ATClass - length 13
        data.write(b'\x08Epic_Set')  # UIDTrunkSet
        data.write(b'\x00')  # UIDLinkSecondary empty
        
        # Mutex data - 2 mutually exclusive sets
        data.write(struct.pack('<i', 2))  # numMutex = 2
        data.write(b'\x0CBody_Mastery')  # mutex[0].name
        data.write(struct.pack('<i', 101))  # mutex[0].index
        data.write(b'\x0CSoul_Mastery')  # mutex[1].name  
        data.write(struct.pack('<i', 102))  # mutex[1].index
        data.write(b'\x00')  # extra string (count+1)
        data.write(struct.pack('<i', -1))  # extra int (count+1)
        
        data.seek(0)
        
        powerset = parse_powerset(data)
        
        assert powerset.display_name == "Weapon Mastery"
        assert powerset.archetype_index == 5
        assert powerset.set_type == PowersetType.EPIC
        assert powerset.full_name == "Scrapper.Weapon_Mastery"
        assert powerset.sub_name == "Epic"
        assert len(powerset.mutex_list) == 2
        assert powerset.mutex_list[0] == ("Body_Mastery", 101)
        assert powerset.mutex_list[1] == ("Soul_Mastery", 102)
    
    def test_parse_powerset_type_enum(self):
        """Test that SetType is properly converted to enum."""
        test_cases = [
            (0, PowersetType.PRIMARY),
            (1, PowersetType.SECONDARY),
            (2, PowersetType.POOL),
            (3, PowersetType.EPIC),
            (4, PowersetType.INHERENT),
            (5, PowersetType.INCARNATE),
        ]
        
        for set_type_int, expected_enum in test_cases:
            data = io.BytesIO()
            
            # Minimal data with focus on SetType
            data.write(b'\x04Test')  # DisplayName
            data.write(struct.pack('<i', 0))  # nArchetype
            data.write(struct.pack('<i', set_type_int))  # SetType to test
            data.write(b'\x08test.png')  # ImageName
            data.write(b'\x00')  # FullName empty
            data.write(b'\x04Test')  # SetName
            data.write(b'\x00')  # Description empty
            data.write(b'\x00')  # SubName empty
            data.write(b'\x05Class')  # ATClass
            data.write(b'\x04Uid1')  # UIDTrunkSet
            data.write(b'\x00')  # UIDLinkSecondary empty
            data.write(struct.pack('<i', 0))  # numMutex
            data.write(b'\x00')  # mutex string
            data.write(struct.pack('<i', 0))  # mutex int
            
            data.seek(0)
            
            powerset = parse_powerset(data)
            assert powerset.set_type == expected_enum
    
    def test_parse_powerset_fullname_fallback(self):
        """Test FullName fallback to Orphan.[DisplayName] when empty."""
        data = io.BytesIO()
        
        # Write powerset with empty FullName
        data.write(b'\x0FFlame Aura Test')  # DisplayName
        data.write(struct.pack('<i', 2))  # nArchetype
        data.write(struct.pack('<i', 0))  # SetType
        data.write(b'\x09flame.png')  # ImageName
        data.write(b'\x00')  # FullName empty - should trigger fallback
        data.write(b'\x0AFlame_Aura')  # SetName
        data.write(b'\x00')  # Description
        data.write(b'\x00')  # SubName
        data.write(b'\x05Class')  # ATClass
        data.write(b'\x03Uid')  # UIDTrunkSet
        data.write(b'\x00')  # UIDLinkSecondary
        data.write(struct.pack('<i', 0))  # numMutex
        data.write(b'\x00')  # mutex string
        data.write(struct.pack('<i', 0))  # mutex int
        
        data.seek(0)
        
        powerset = parse_powerset(data)
        
        # Should have Orphan prefix
        assert powerset.full_name == "Orphan.Flame Aura Test"
    
    def test_parse_powerset_with_unicode(self):
        """Test parsing powerset with Unicode characters."""
        data = io.BytesIO()
        
        # Unicode display name
        unicode_name = "Défense Élevée"
        name_bytes = unicode_name.encode('utf-8')
        data.write(bytes([len(name_bytes)]))
        data.write(name_bytes)
        
        # Standard fields
        data.write(struct.pack('<i', 0))  # nArchetype
        data.write(struct.pack('<i', 1))  # SetType
        data.write(b'\x08icon.png')  # ImageName
        
        # Unicode full name
        unicode_full = "Tanker.Défense"
        full_bytes = unicode_full.encode('utf-8')
        data.write(bytes([len(full_bytes)]))
        data.write(full_bytes)
        
        # Rest of fields
        data.write(b'\x07Defense')  # SetName
        
        # Unicode description
        unicode_desc = "Capacité défensive améliorée"
        desc_bytes = unicode_desc.encode('utf-8')
        data.write(bytes([len(desc_bytes)]))
        data.write(desc_bytes)
        
        data.write(b'\x00')  # SubName
        data.write(b'\x05Class')  # ATClass
        data.write(b'\x03Uid')  # UIDTrunkSet
        data.write(b'\x00')  # UIDLinkSecondary
        data.write(struct.pack('<i', 0))  # numMutex
        data.write(b'\x00')  # mutex string
        data.write(struct.pack('<i', 0))  # mutex int
        
        data.seek(0)
        
        powerset = parse_powerset(data)
        
        assert powerset.display_name == "Défense Élevée"
        assert powerset.full_name == "Tanker.Défense"
        assert powerset.description == "Capacité défensive améliorée"
    
    def test_parse_powerset_eof_handling(self):
        """Test handling of EOF while parsing powerset."""
        # Create incomplete data
        data = io.BytesIO()
        data.write(b'\x06Tanker')  # DisplayName
        data.write(struct.pack('<i', 0))  # nArchetype
        # Missing rest of fields
        
        data.seek(0)
        
        with pytest.raises(EOFError):
            parse_powerset(data)
    
    def test_parse_pool_powerset(self):
        """Test parsing a pool powerset (available to all archetypes)."""
        data = io.BytesIO()
        
        # Pool powerset data
        data.write(b'\x06Flight')  # DisplayName
        data.write(struct.pack('<i', -1))  # nArchetype = -1 for pools
        data.write(struct.pack('<i', 2))  # SetType = Pool
        data.write(b'\x0AFlight.png')  # ImageName
        data.write(b'\x0BPool.Flight')  # FullName - length 11
        data.write(b'\x06Flight')  # SetName
        data.write(b'\x1ETravel power for flying around')  # Description - length 30
        data.write(b'\x04Pool')  # SubName
        data.write(b'\x04Pool')  # ATClass
        data.write(b'\x08Pool_Set')  # UIDTrunkSet - length 8
        data.write(b'\x00')  # UIDLinkSecondary
        
        # Pools typically have mutex with other travel powers
        data.write(struct.pack('<i', 3))  # numMutex = 3
        data.write(b'\x05Speed')  # mutex[0]
        data.write(struct.pack('<i', 201))
        data.write(b'\x07Leaping')  # mutex[1]
        data.write(struct.pack('<i', 202))
        data.write(b'\x08Teleport')  # mutex[2]
        data.write(struct.pack('<i', 203))
        data.write(b'\x00')  # extra string
        data.write(struct.pack('<i', -1))  # extra int
        
        data.seek(0)
        
        powerset = parse_powerset(data)
        
        assert powerset.display_name == "Flight"
        assert powerset.archetype_index == -1  # Pool power marker
        assert powerset.set_type == PowersetType.POOL
        assert powerset.sub_name == "Pool"
        assert len(powerset.mutex_list) == 3
        assert powerset.mutex_list[0][0] == "Speed"
        assert powerset.mutex_list[1][0] == "Leaping"
        assert powerset.mutex_list[2][0] == "Teleport"
    
    @pytest.mark.parametrize("num_mutex,expected_count", [
        (0, 0),    # No mutex
        (1, 1),    # Single mutex
        (5, 5),    # Multiple mutex
        (10, 10),  # Many mutex
    ])
    def test_mutex_array_handling(self, num_mutex, expected_count):
        """Test that mutex array is handled correctly with count+1 pattern."""
        data = io.BytesIO()
        
        # Write minimal powerset data up to mutex
        data.write(b'\x04Test')  # DisplayName
        data.write(struct.pack('<i', 0))  # nArchetype
        data.write(struct.pack('<i', 0))  # SetType
        data.write(b'\x08test.png')  # ImageName
        data.write(b'\x00')  # FullName
        data.write(b'\x04Test')  # SetName
        data.write(b'\x00')  # Description
        data.write(b'\x00')  # SubName
        data.write(b'\x05Class')  # ATClass
        data.write(b'\x03Uid')  # UIDTrunkSet
        data.write(b'\x00')  # UIDLinkSecondary
        
        # Write mutex data
        data.write(struct.pack('<i', num_mutex))
        for i in range(num_mutex):
            mutex_name = f'Mutex{i}'
            data.write(bytes([len(mutex_name)]))
            data.write(mutex_name.encode())
            data.write(struct.pack('<i', 100 + i))
        
        # Extra entries (count+1)
        data.write(b'\x00')  # empty string
        data.write(struct.pack('<i', -1))  # -1 int
        
        data.seek(0)
        
        powerset = parse_powerset(data)
        
        assert len(powerset.mutex_list) == expected_count
        if expected_count > 0:
            assert powerset.mutex_list[0][0] == "Mutex0"
            assert powerset.mutex_list[0][1] == 100
            if expected_count > 1:
                assert powerset.mutex_list[-1][0] == f"Mutex{expected_count-1}"
                assert powerset.mutex_list[-1][1] == 100 + expected_count - 1