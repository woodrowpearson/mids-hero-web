"""Binary reader utilities for parsing .NET BinaryReader format data."""

import io
import struct
from typing import BinaryIO, Union


def read_7bit_encoded_int(stream: BinaryIO) -> int:
    """Read a 7-bit encoded integer from the stream.
    
    .NET's BinaryWriter uses 7-bit encoding for string lengths where:
    - Each byte uses 7 bits for data and 1 bit as a continuation flag
    - If bit 7 (0x80) is set, there are more bytes to read
    - The value is assembled from low to high bytes
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The decoded integer value
        
    Raises:
        EOFError: If stream ends while reading
    """
    value = 0
    shift = 0
    
    while True:
        byte_data = stream.read(1)
        if not byte_data:
            raise EOFError("Unexpected EOF while reading 7-bit encoded int")
            
        byte = byte_data[0]
        value |= (byte & 0x7F) << shift
        
        if (byte & 0x80) == 0:
            break
            
        shift += 7
        
    return value


def read_string(stream: BinaryIO) -> str:
    """Read a .NET BinaryReader format string from the stream.
    
    Format:
    - Length prefix using 7-bit encoding (byte count, not char count)
    - UTF-8 encoded string data
    - Empty strings are encoded as single zero byte
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The decoded string
        
    Raises:
        EOFError: If stream ends while reading
    """
    try:
        # Read the length prefix
        length = read_7bit_encoded_int(stream)
    except EOFError:
        raise EOFError("Unexpected EOF while reading string length")
    
    # Handle empty string
    if length == 0:
        return ""
    
    # Read the string data
    string_data = stream.read(length)
    if len(string_data) < length:
        raise EOFError(f"String data truncated: expected {length} bytes, got {len(string_data)}")
    
    # Decode UTF-8
    return string_data.decode('utf-8')


def read_int32(stream: BinaryIO) -> int:
    """Read a 32-bit signed integer from the stream.
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The 32-bit signed integer value
        
    Raises:
        EOFError: If stream ends while reading
    """
    data = stream.read(4)
    if len(data) < 4:
        raise EOFError(f"Unexpected EOF while reading int32: expected 4 bytes, got {len(data)}")
    return struct.unpack('<i', data)[0]


def read_uint32(stream: BinaryIO) -> int:
    """Read a 32-bit unsigned integer from the stream.
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The 32-bit unsigned integer value
        
    Raises:
        EOFError: If stream ends while reading
    """
    data = stream.read(4)
    if len(data) < 4:
        raise EOFError(f"Unexpected EOF while reading uint32: expected 4 bytes, got {len(data)}")
    return struct.unpack('<I', data)[0]


def read_int64(stream: BinaryIO) -> int:
    """Read a 64-bit signed integer from the stream.
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The 64-bit signed integer value
        
    Raises:
        EOFError: If stream ends while reading
    """
    data = stream.read(8)
    if len(data) < 8:
        raise EOFError(f"Unexpected EOF while reading int64: expected 8 bytes, got {len(data)}")
    return struct.unpack('<q', data)[0]


def read_float32(stream: BinaryIO) -> float:
    """Read a 32-bit float from the stream.
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The 32-bit float value
        
    Raises:
        EOFError: If stream ends while reading
    """
    data = stream.read(4)
    if len(data) < 4:
        raise EOFError(f"Unexpected EOF while reading float32: expected 4 bytes, got {len(data)}")
    return struct.unpack('<f', data)[0]


def read_bool(stream: BinaryIO) -> bool:
    """Read a boolean value from the stream.
    
    In .NET, bool is stored as 1 byte where 0 = false, non-zero = true
    
    Args:
        stream: Binary stream to read from
        
    Returns:
        The boolean value
        
    Raises:
        EOFError: If stream ends while reading
    """
    data = stream.read(1)
    if len(data) < 1:
        raise EOFError("Unexpected EOF while reading bool")
    return data[0] != 0


class BinaryReader:
    """A reader for .NET BinaryWriter format data with position tracking."""
    
    def __init__(self, data: Union[bytes, BinaryIO]):
        """Initialize BinaryReader with data or stream.
        
        Args:
            data: Either raw bytes or a file-like object
        """
        if isinstance(data, bytes):
            self._stream = io.BytesIO(data)
        else:
            self._stream = data
        self._start_pos = self._stream.tell()
    
    def read(self, size: int) -> bytes:
        """Read raw bytes from the stream."""
        return self._stream.read(size)
    
    def seek(self, offset: int, whence: int = 0) -> int:
        """Seek to a position in the stream."""
        return self._stream.seek(offset, whence)
    
    def tell(self) -> int:
        """Get current position in the stream."""
        return self._stream.tell()
    
    def read_string(self) -> str:
        """Read a .NET formatted string."""
        pos = self.tell()
        try:
            return read_string(self._stream)
        except EOFError as e:
            raise EOFError(f"Error at position {pos}: {str(e)}")
    
    def read_int32(self) -> int:
        """Read a 32-bit signed integer."""
        pos = self.tell()
        try:
            return read_int32(self._stream)
        except EOFError as e:
            raise EOFError(f"Error at position {pos}: {str(e)}")
    
    def read_uint32(self) -> int:
        """Read a 32-bit unsigned integer."""
        pos = self.tell()
        try:
            return read_uint32(self._stream)
        except EOFError as e:
            raise EOFError(f"Error at position {pos}: {str(e)}")
    
    def read_int64(self) -> int:
        """Read a 64-bit signed integer."""
        pos = self.tell()
        try:
            return read_int64(self._stream)
        except EOFError as e:
            raise EOFError(f"Error at position {pos}: {str(e)}")
    
    def read_float32(self) -> float:
        """Read a 32-bit float."""
        pos = self.tell()
        try:
            return read_float32(self._stream)
        except EOFError as e:
            raise EOFError(f"Error at position {pos}: {str(e)}")
    
    def read_bool(self) -> bool:
        """Read a boolean value."""
        pos = self.tell()
        try:
            return read_bool(self._stream)
        except EOFError as e:
            raise EOFError(f"Error at position {pos}: {str(e)}")