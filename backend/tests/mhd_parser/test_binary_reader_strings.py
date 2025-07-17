"""Tests for .NET BinaryReader string format parsing."""

import io

import pytest

from app.mhd_parser.binary_reader import read_string


class TestDotNetStringParsing:
    """Test cases for parsing .NET BinaryReader string format."""

    def test_read_empty_string(self):
        """Empty string should be encoded as single zero byte."""
        data = b'\x00'
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == ""
        assert stream.tell() == 1  # Should have read 1 byte

    def test_read_single_char_string(self):
        """Single character string with 1-byte length prefix."""
        # "A" = 1 byte UTF-8, length=1 encoded as 0x01
        data = b'\x01A'
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == "A"
        assert stream.tell() == 2

    def test_read_hello_world(self):
        """Standard ASCII string test."""
        # "Hello" = 5 bytes, length=5 encoded as 0x05
        data = b'\x05Hello'
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == "Hello"
        assert stream.tell() == 6

    def test_read_unicode_string(self):
        """UTF-8 encoded string with non-ASCII characters."""
        # "Ω" (omega) = 2 bytes in UTF-8 (0xCE 0xA9)
        data = b'\x02\xCE\xA9'
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == "Ω"
        assert stream.tell() == 3

    def test_read_string_with_7bit_encoded_length(self):
        """Test string with length requiring 7-bit encoding."""
        # Length 128 = 0x80, encoded as 0x80 0x01 in 7-bit encoding
        # Create a string of 128 'a' characters
        test_string = 'a' * 128
        length_bytes = b'\x80\x01'  # 128 in 7-bit encoding
        data = length_bytes + test_string.encode('utf-8')
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == test_string
        assert len(result) == 128
        assert stream.tell() == 130  # 2 bytes length + 128 bytes string

    def test_read_string_with_multibyte_7bit_length(self):
        """Test string with length requiring multiple bytes in 7-bit encoding."""
        # Length 300 = 0x12C
        # In 7-bit encoding: 0xAC 0x02 (low byte: 0x2C | 0x80 = 0xAC, high byte: 0x02)
        test_string = 'x' * 300
        length_bytes = b'\xAC\x02'  # 300 in 7-bit encoding
        data = length_bytes + test_string.encode('utf-8')
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == test_string
        assert len(result) == 300
        assert stream.tell() == 302  # 2 bytes length + 300 bytes string

    def test_read_string_at_eof_for_length(self):
        """Test EOF while reading length prefix."""
        data = b''  # Empty stream
        stream = io.BytesIO(data)

        with pytest.raises(EOFError, match="reading string length"):
            read_string(stream)

    def test_read_string_at_eof_for_data(self):
        """Test EOF while reading string data."""
        data = b'\x05Hi'  # Says 5 bytes but only 2 available
        stream = io.BytesIO(data)

        with pytest.raises(EOFError, match="String data truncated"):
            read_string(stream)

    def test_read_string_with_continuation_bit_eof(self):
        """Test EOF in middle of multi-byte length."""
        data = b'\x80'  # Continuation bit set but no next byte
        stream = io.BytesIO(data)

        with pytest.raises(EOFError, match="reading string length"):
            read_string(stream)

    def test_read_multiple_strings(self):
        """Test reading multiple strings in sequence."""
        data = (
            b'\x05Hello'      # "Hello"
            b'\x00'           # ""
            b'\x05World'      # "World"
            b'\x01!'          # "!"
        )
        stream = io.BytesIO(data)

        assert read_string(stream) == "Hello"
        assert read_string(stream) == ""
        assert read_string(stream) == "World"
        assert read_string(stream) == "!"
        assert stream.tell() == len(data)

    @pytest.mark.parametrize("test_string", [
        "Simple ASCII text",
        "Unicode: αβγδε ΑΒΓΔΕ",
        "Emoji: 🎮🏙️⚔️",
        "Mixed: Hello, 世界! 🌍",
        "Special chars: \n\t\r\\\"'",
        "Long " + "text " * 100,  # 500+ character string
    ])
    def test_string_roundtrip(self, test_string, create_binary_data):
        """Test that various strings can be encoded and decoded correctly."""
        # Use the fixture to create .NET encoded string data
        data = create_binary_data(string=test_string)
        stream = io.BytesIO(data)

        result = read_string(stream)

        assert result == test_string
        assert stream.tell() == len(data)
