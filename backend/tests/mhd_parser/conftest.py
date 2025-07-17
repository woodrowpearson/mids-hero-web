"""Pytest configuration and fixtures for MHD parser tests."""

import io
import struct
from pathlib import Path
from typing import BinaryIO

import pytest


@pytest.fixture
def binary_stream(request) -> BinaryIO:
    """Create a binary stream from bytes data.
    
    Usage:
        @pytest.mark.parametrize('binary_stream', [b'\\x05\\x00\\x00\\x00hello'], indirect=True)
        def test_something(binary_stream):
            # binary_stream is now a BytesIO object with the data
    """
    data = request.param if hasattr(request, 'param') else b''
    return io.BytesIO(data)


@pytest.fixture
def sample_data_dir() -> Path:
    """Path to directory containing sample MHD files for testing."""
    return Path(__file__).parent / "sample_data"


@pytest.fixture
def dotnet_string(text: str) -> bytes:
    """Encode a string in .NET BinaryWriter format.
    
    .NET uses a 7-bit encoded integer for the length prefix,
    followed by UTF-8 encoded bytes.
    """
    def encode_7bit_int(value: int) -> bytes:
        """Encode an integer using .NET's 7-bit encoding."""
        result = bytearray()
        while value >= 0x80:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    if not text:
        return b'\x00'
    
    utf8_bytes = text.encode('utf-8')
    length_prefix = encode_7bit_int(len(utf8_bytes))
    return length_prefix + utf8_bytes


@pytest.fixture
def create_binary_data():
    """Factory fixture for creating test binary data."""
    def _create(**kwargs) -> bytes:
        """Create binary data with various types.
        
        Supported kwargs:
            int32: 32-bit signed integer
            uint32: 32-bit unsigned integer
            int64: 64-bit signed integer
            float32: 32-bit float
            bool: boolean (1 byte)
            string: .NET formatted string
        """
        data = bytearray()
        
        for key, value in kwargs.items():
            if key == 'int32':
                data.extend(struct.pack('<i', value))
            elif key == 'uint32':
                data.extend(struct.pack('<I', value))
            elif key == 'int64':
                data.extend(struct.pack('<q', value))
            elif key == 'float32':
                data.extend(struct.pack('<f', value))
            elif key == 'bool':
                data.extend(struct.pack('<?', value))
            elif key == 'string':
                # Use the dotnet_string logic inline
                if not value:
                    data.append(0)
                else:
                    utf8_bytes = value.encode('utf-8')
                    length = len(utf8_bytes)
                    # 7-bit encode the length
                    while length >= 0x80:
                        data.append((length & 0x7F) | 0x80)
                        length >>= 7
                    data.append(length & 0x7F)
                    data.extend(utf8_bytes)
        
        return bytes(data)
    
    return _create