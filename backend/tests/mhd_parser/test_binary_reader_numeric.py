"""Tests for .NET BinaryReader numeric type parsing."""

import io
import struct

import pytest

from app.mhd_parser.binary_reader import (
    read_int32,
    read_uint32,
    read_int64,
    read_float32,
    read_bool,
    BinaryReader
)


class TestNumericTypeParsing:
    """Test cases for parsing numeric types in .NET BinaryReader format."""
    
    def test_read_int32(self):
        """Test reading 32-bit signed integers."""
        # Test positive, negative, zero, and edge cases
        test_values = [0, 1, -1, 2147483647, -2147483648, 42, -42]
        
        for value in test_values:
            data = struct.pack('<i', value)  # Little-endian signed int
            stream = io.BytesIO(data)
            
            result = read_int32(stream)
            
            assert result == value
            assert stream.tell() == 4
    
    def test_read_uint32(self):
        """Test reading 32-bit unsigned integers."""
        test_values = [0, 1, 4294967295, 42, 1000000]
        
        for value in test_values:
            data = struct.pack('<I', value)  # Little-endian unsigned int
            stream = io.BytesIO(data)
            
            result = read_uint32(stream)
            
            assert result == value
            assert stream.tell() == 4
    
    def test_read_int64(self):
        """Test reading 64-bit signed integers."""
        test_values = [
            0, 1, -1,
            9223372036854775807,  # Max int64
            -9223372036854775808,  # Min int64
            1234567890123456
        ]
        
        for value in test_values:
            data = struct.pack('<q', value)  # Little-endian signed long
            stream = io.BytesIO(data)
            
            result = read_int64(stream)
            
            assert result == value
            assert stream.tell() == 8
    
    def test_read_float32(self):
        """Test reading 32-bit floats."""
        test_values = [0.0, 1.0, -1.0, 3.14159, -273.15, 1e-10, 1e10]
        
        for value in test_values:
            data = struct.pack('<f', value)  # Little-endian float
            stream = io.BytesIO(data)
            
            result = read_float32(stream)
            
            # 32-bit floats have limited precision, use relative tolerance
            assert pytest.approx(result, rel=1e-5) == value
            assert stream.tell() == 4
    
    def test_read_bool(self):
        """Test reading boolean values."""
        # .NET bool is 1 byte: 0 = false, non-zero = true
        test_cases = [
            (b'\x00', False),
            (b'\x01', True),
            (b'\xFF', True),  # Any non-zero is true
            (b'\x42', True),
        ]
        
        for data, expected in test_cases:
            stream = io.BytesIO(data)
            
            result = read_bool(stream)
            
            assert result == expected
            assert stream.tell() == 1
    
    def test_numeric_eof_handling(self):
        """Test EOF handling for numeric types."""
        # Empty stream
        stream = io.BytesIO(b'')
        
        with pytest.raises(EOFError, match="reading int32"):
            read_int32(stream)
        
        # Partial data
        stream = io.BytesIO(b'\x01\x02\x03')  # Only 3 bytes for int32
        
        with pytest.raises(EOFError, match="reading int32"):
            read_int32(stream)
    
    def test_read_multiple_values(self):
        """Test reading multiple values in sequence."""
        # Pack multiple values
        data = io.BytesIO()
        data.write(struct.pack('<i', 42))      # int32
        data.write(struct.pack('<f', 3.14))    # float32
        data.write(struct.pack('<?', True))    # bool
        data.write(struct.pack('<q', 9999))    # int64
        data.seek(0)
        
        # Read them back
        assert read_int32(data) == 42
        assert pytest.approx(read_float32(data), rel=1e-5) == 3.14
        assert read_bool(data) == True
        assert read_int64(data) == 9999
        assert data.tell() == 17  # 4 + 4 + 1 + 8


class TestBinaryReaderClass:
    """Test cases for the BinaryReader class."""
    
    def test_binary_reader_initialization(self):
        """Test BinaryReader initialization with various inputs."""
        # From bytes
        reader = BinaryReader(b'Hello')
        assert reader.tell() == 0
        assert reader.read(5) == b'Hello'
        
        # From file-like object
        stream = io.BytesIO(b'World')
        reader = BinaryReader(stream)
        assert reader.tell() == 0
        assert reader.read(5) == b'World'
    
    def test_binary_reader_methods(self):
        """Test BinaryReader convenience methods."""
        data = io.BytesIO()
        # Write test data
        data.write(b'\x05Hello')              # String
        data.write(struct.pack('<i', -42))    # int32
        data.write(struct.pack('<I', 42))     # uint32
        data.write(struct.pack('<f', 2.718))  # float32
        data.write(struct.pack('<?', False))  # bool
        data.write(struct.pack('<q', 12345))  # int64
        data.seek(0)
        
        reader = BinaryReader(data)
        
        # Test all methods
        assert reader.read_string() == "Hello"
        assert reader.read_int32() == -42
        assert reader.read_uint32() == 42
        assert pytest.approx(reader.read_float32(), rel=1e-5) == 2.718
        assert reader.read_bool() == False
        assert reader.read_int64() == 12345
    
    def test_binary_reader_position_tracking(self):
        """Test that BinaryReader tracks position correctly."""
        reader = BinaryReader(b'\x00\x01\x02\x03\x04\x05\x06\x07')
        
        assert reader.tell() == 0
        reader.read_int32()
        assert reader.tell() == 4
        reader.read_int32()
        assert reader.tell() == 8
    
    def test_binary_reader_eof_handling(self):
        """Test BinaryReader EOF handling."""
        reader = BinaryReader(b'\x01\x02')  # Only 2 bytes
        
        # Should raise EOFError with position info
        with pytest.raises(EOFError) as exc_info:
            reader.read_int32()
        
        assert "position 0" in str(exc_info.value)
    
    def test_binary_reader_seek(self):
        """Test seeking in BinaryReader."""
        reader = BinaryReader(b'\x00\x01\x02\x03\x04\x05\x06\x07')
        
        # Seek to position
        reader.seek(4)
        assert reader.tell() == 4
        assert reader.read_int32() == struct.unpack('<i', b'\x04\x05\x06\x07')[0]
        
        # Seek back
        reader.seek(0)
        assert reader.tell() == 0
        assert reader.read_int32() == struct.unpack('<i', b'\x00\x01\x02\x03')[0]