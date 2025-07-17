"""Tests for MHD binary file reader."""

import io
import struct
from typing import BinaryIO

import pytest

from app.mhd_parser.binary_reader import MHDBinaryReader


class TestMHDBinaryReader:
    """Test MHD binary reader functionality."""

    def test_read_string(self):
        """Test reading .NET-style strings."""
        # .NET BinaryWriter writes strings with a 7-bit encoded length prefix
        buffer = io.BytesIO()
        
        # Write a test string "Hello" with length 5
        # In .NET's 7-bit encoding, small values (< 128) are written as single byte
        buffer.write(bytes([5]))  # Length
        buffer.write(b"Hello")    # String data
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert reader.read_string() == "Hello"
    
    def test_read_empty_string(self):
        """Test reading empty string."""
        buffer = io.BytesIO()
        buffer.write(bytes([0]))  # Length 0
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert reader.read_string() == ""
    
    def test_read_int32(self):
        """Test reading 32-bit integers."""
        buffer = io.BytesIO()
        buffer.write(struct.pack("<i", 42))  # Little-endian int32
        buffer.write(struct.pack("<i", -100))
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert reader.read_int32() == 42
        assert reader.read_int32() == -100
    
    def test_read_single(self):
        """Test reading single-precision floats."""
        buffer = io.BytesIO()
        buffer.write(struct.pack("<f", 3.14159))  # Little-endian float
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert abs(reader.read_single() - 3.14159) < 0.0001
    
    def test_read_boolean(self):
        """Test reading boolean values."""
        buffer = io.BytesIO()
        buffer.write(bytes([1]))  # True
        buffer.write(bytes([0]))  # False
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert reader.read_boolean() is True
        assert reader.read_boolean() is False
    
    def test_read_7bit_encoded_int(self):
        """Test reading .NET 7-bit encoded integers."""
        buffer = io.BytesIO()
        
        # Test small value (< 128)
        buffer.write(bytes([42]))
        
        # Test larger value (128-16383)
        # 300 = 0x12C = 0000001 00101100
        # Encoded as: 10101100 00000010
        buffer.write(bytes([0xAC, 0x02]))
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert reader.read_7bit_encoded_int() == 42
        assert reader.read_7bit_encoded_int() == 300
    
    def test_read_longer_string(self):
        """Test reading string with multi-byte length encoding."""
        buffer = io.BytesIO()
        
        # String of length 200
        test_string = "X" * 200
        # 200 = 0xC8 = 11001000
        # Encoded as: 11001000 00000001
        buffer.write(bytes([0xC8, 0x01]))
        buffer.write(test_string.encode("utf-8"))
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        assert reader.read_string() == test_string
    
    def test_read_array(self):
        """Test reading arrays with count prefix."""
        buffer = io.BytesIO()
        
        # Write array count
        buffer.write(struct.pack("<i", 3))
        # Write array elements
        buffer.write(struct.pack("<i", 10))
        buffer.write(struct.pack("<i", 20))
        buffer.write(struct.pack("<i", 30))
        
        buffer.seek(0)
        reader = MHDBinaryReader(buffer)
        
        count = reader.read_int32()
        array = [reader.read_int32() for _ in range(count)]
        
        assert array == [10, 20, 30]