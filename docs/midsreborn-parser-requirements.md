# MidsReborn Parser Requirements

## Current Situation

- The decision has been made to use the MidsReborn C# parser (not the archived Python parser)
- MidsReborn requires Windows (.NET 8.0 Windows-specific, Windows Forms dependencies)
- Current development environment is macOS, which cannot build MidsReborn

## Options to Proceed

### Option 1: Windows Development Environment
- Use a Windows machine or VM to build and run DataExporter
- Export all MHD files to JSON
- Transfer JSON files back to macOS for import

### Option 2: Docker with Windows Containers
- Create a Windows Docker container with .NET 8.0 SDK
- Build and run DataExporter in the container
- Note: Requires Windows host or specialized setup

### Option 3: Pre-built DataExporter
- Get a pre-built DataExporter.exe from a Windows developer
- Run it on a Windows machine with the MHD files
- Share the exported JSON files

### Option 4: GitHub Actions Windows Runner
- Set up a GitHub Actions workflow with Windows runner
- Build DataExporter and run export as part of CI/CD
- Commit exported JSON files to repository

## Recommended Approach

Given the constraints, **Option 4 (GitHub Actions)** is recommended:
1. Automated and repeatable
2. No local Windows requirement
3. Can be triggered on demand
4. Results are tracked in git

## Next Steps

1. Create GitHub Actions workflow for Windows build
2. Add DataExporter build and execution steps
3. Upload exported JSON as artifacts
4. Download and import JSON files locally