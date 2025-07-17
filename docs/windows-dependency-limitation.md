# Windows Dependency Limitation for MidsReborn Parser

## Issue

The MidsReborn C# parser cannot be built on macOS/Linux due to Windows-specific dependencies:

1. **Target Framework**: `net8.0-windows10.0.19041.0`
2. **Windows Forms**: Uses `System.Windows.Forms` throughout the codebase
3. **DatabaseAPI.cs**: Core parsing logic is tightly coupled with Windows Forms

## Impact

- Cannot build DataExporter on non-Windows platforms
- Cannot use the community-maintained MidsReborn parser directly
- Must use alternative parsing solutions

## Resolution

Given this limitation, we're proceeding with the Python MHD parser implementation that:
- Works cross-platform
- Can parse the required data formats
- Is already partially implemented and tested

## Future Options

1. **Extract Core Logic**: Create a separate .NET Standard library with just the parsing logic (significant effort)
2. **Docker Windows Container**: Run the C# parser in a Windows container (complex setup)
3. **Complete Python Parser**: Finish implementing the Python parser for all data types (current approach)

## Current Status

- Python parser successfully imports archetypes and powersets
- Enhancement parser needs flag handling fix
- Power parser needs completion
- Recipe and salvage parsers need implementation

This is a pragmatic decision to keep development moving forward while maintaining cross-platform compatibility.