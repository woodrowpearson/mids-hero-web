# Test Fixtures

This directory contains test fixtures for DataExporter integration tests.

## Sample MHD Files

Due to the proprietary nature of MHD files, actual game data files are not included in the repository. For full integration testing:

1. Place MHD files from City of Heroes in this directory
2. Required files:
   - `I12.mhd` - Main database
   - `EnhDB.mhd` - Enhancement database
   - `Recipe.mhd` - Recipe database
   - `Salvage.mhd` - Salvage database
   - `AttribMod.json` - Attribute modifiers
   - `TypeGrades.json` - Type grades

## Mock Data

For unit tests, the test suite creates mock files automatically. These mock files:
- Have the correct file names
- Contain minimal binary/JSON data
- Are sufficient for testing file operations and error handling
- Do not contain actual game data

## Creating Test Fixtures

To create a minimal test fixture:

```csharp
// Binary file
File.WriteAllBytes("test.mhd", new byte[] { 0x00 });

// JSON file  
File.WriteAllText("test.json", "{}");
```

## CI/CD Integration

The test suite is designed to work in CI/CD environments without real MHD files:
- All tests handle missing files gracefully
- Mock files are created as needed
- No proprietary data is required for tests to pass