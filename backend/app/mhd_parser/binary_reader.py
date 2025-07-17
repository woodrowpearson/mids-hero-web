"""Binary reader for parsing .NET BinaryWriter format used in MHD files."""

import struct
from typing import BinaryIO


class BinaryReader:
    """Reads binary data in .NET BinaryWriter format."""
    
    def __init__(self, stream: BinaryIO):
        self.stream = stream
    
    def read_int32(self) -> int:
        """Read a 32-bit signed integer."""
        data = self.stream.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected end of stream")
        return struct.unpack('<i', data)[0]
    
    def read_uint32(self) -> int:
        """Read a 32-bit unsigned integer."""
        data = self.stream.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected end of stream")
        return struct.unpack('<I', data)[0]
    
    def read_int64(self) -> int:
        """Read a 64-bit signed integer."""
        data = self.stream.read(8)
        if len(data) < 8:
            raise EOFError("Unexpected end of stream")
        return struct.unpack('<q', data)[0]
    
    def read_float(self) -> float:
        """Read a 32-bit float."""
        data = self.stream.read(4)
        if len(data) < 4:
            raise EOFError("Unexpected end of stream")
        return struct.unpack('<f', data)[0]
    
    def read_boolean(self) -> bool:
        """Read a boolean value."""
        data = self.stream.read(1)
        if len(data) < 1:
            raise EOFError("Unexpected end of stream")
        return struct.unpack('?', data)[0]
    
    def read_string(self) -> str:
        """Read a .NET BinaryWriter encoded string with 7-bit length prefix."""
        length = self._read_7bit_encoded_int()
        if length == 0:
            return ""
        data = self.stream.read(length)
        if len(data) < length:
            raise EOFError("Unexpected end of stream")
        return data.decode('utf-8')
    
    def _read_7bit_encoded_int(self) -> int:
        """Read a 7-bit encoded integer as used by .NET BinaryWriter."""
        count = 0
        shift = 0
        while True:
            data = self.stream.read(1)
            if len(data) < 1:
                raise EOFError("Unexpected end of stream")
            byte = ord(data)
            count |= (byte & 0x7F) << shift
            shift += 7
            if (byte & 0x80) == 0:
                break
        return count