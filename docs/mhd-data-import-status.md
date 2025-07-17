# MHD Data Import Status

## Current Situation

1. **MidsReborn Parser**: The C# parser exists in `external/MidsReborn` but:
   - Has Windows dependencies (Windows Forms, .NET Windows target)
   - Is not tracked in git (too large or external dependency)
   - Cannot be built on macOS/Linux

2. **DataExporter Tool**: Created in `DataExporter/` directory:
   - `MidsRebornExporter.cs` - Full implementation using MidsReborn
   - `SimpleMhdExporter.cs` - Placeholder implementation for CI/CD
   - Can switch between implementations based on environment

3. **GitHub Actions Workflow**: Set up but cannot use MidsReborn directly

## Options to Complete Data Import

### Option 1: Manual Windows Export (Recommended)
1. Clone the repository on a Windows machine
2. Ensure `external/MidsReborn` directory contains the MidsReborn source
3. Uncomment the ProjectReference in `DataExporter.csproj`
4. Update `Program.cs` to use `MidsRebornExporter`
5. Build and run: `dotnet run -- <mhd-path> <output-path>`
6. Commit the exported JSON files

### Option 2: Pre-built Binary
1. Get a pre-built DataExporter.exe from a Windows developer
2. Run on Windows with MHD files
3. Upload exported JSON

### Option 3: Python Parser (Already Partially Working)
1. Continue with the Python parser in `backend/app/mhd_parser/`
2. Already successfully imports archetypes and powersets
3. Fix enhancement parser and complete power parser
4. Simpler but may have accuracy issues

## Next Steps

Since the MidsReborn parser cannot be used in the current CI/CD setup:

1. **Short term**: Use the Python parser to get data imported
2. **Long term**: Set up proper MidsReborn integration with:
   - Git LFS for large files
   - Or submodule for MidsReborn
   - Or pre-built Windows binary in CI/CD

## Current Data Status

From Python parser attempts:
- ✅ 61 Archetypes successfully parsed
- ✅ 380 Powersets successfully parsed (partial)
- ❌ Powers not imported (parser incomplete)
- ❌ Enhancements failed (format issue)
- ❌ Recipes not attempted
- ❌ Salvage not attempted