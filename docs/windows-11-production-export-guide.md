# Windows 11 Production-Ready Data Export Guide

## Overview

This is a streamlined, production-ready guide for exporting City of Heroes MHD data files using Windows 11 Pro and PowerShell. The guide uses .NET 8.0 LTS for stability and long-term support.

The project includes MidsReborn (located at `external\MidsReborn\`), which is the community-maintained parser for City of Heroes game data files. MidsReborn can read the binary MHD format and extract game data like archetypes, powers, enhancements, etc.

## Prerequisites

- Windows 11 Pro VM or physical machine
- 4GB RAM minimum
- 20GB free disk space
- Internet connection for downloading tools

## Step 1: Install .NET 8.0 LTS SDK

1. **Download .NET 8.0 SDK**:
   - Open browser and go to: https://dotnet.microsoft.com/download/dotnet/8.0
   - Download "SDK 8.0.xxx" for Windows x64
   - Run the installer with default options

2. **Verify installation** (open NEW PowerShell after install):
   ```powershell
   dotnet --version
   ```
   Should show: `8.0.xxx`

3. **If `dotnet` is not recognized**:
   ```powershell
   # Option A: Use full path
   & "C:\Program Files\dotnet\dotnet.exe" --version
   
   # Option B: Restart PowerShell as Administrator and add to PATH
   [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\dotnet", [EnvironmentVariableTarget]::Machine)
   # Then close and reopen PowerShell
   ```

## Step 2: Download Project Files

1. **Create working directory**:
   ```powershell
   cd C:\Users\Public\Documents
   mkdir MidsExport
   cd MidsExport
   ```

2. **Download the repository**:
   ```powershell
   # Option A: Using Git (if installed)
   git clone https://github.com/woodrowpearson/mids-hero-web.git
   
   # Option B: Download as ZIP
   # Go to: https://github.com/woodrowpearson/mids-hero-web
   # Click "Code" → "Download ZIP"
   # Extract to C:\Users\Public\Documents\MidsExport\
   ```

3. **Verify MidsReborn is included**:
   ```powershell
   # Check that MidsReborn parser is present
   dir mids-hero-web\external\MidsReborn\
   
   # You should see:
   # MidsReborn.sln
   # MidsReborn\ (project folder)
   # MRBResourceLib\ 
   # etc.
   ```

## Expected File Structure

After completing Step 2, your directory structure should look like this:

```
C:\Users\Public\Documents\MidsExport\
├── mids-hero-web\
│   ├── DataExporter\
│   │   ├── DataExporter.csproj
│   │   ├── Program.cs
│   │   └── MidsRebornExporter.cs
│   ├── external\
│   │   └── MidsReborn\
│   │       ├── MidsReborn.sln
│   │       ├── MidsReborn\
│   │       │   └── MidsReborn.csproj
│   │       ├── MRBResourceLib\
│   │       │   └── MRBResourceLib.csproj
│   │       └── MRBLogging\
│   │           └── MRBLogging.csproj
│   ├── data\
│   │   ├── Homecoming_2025-7-1111\
│   │   │   ├── I12.mhd          (30MB - Main database)
│   │   │   ├── EnhDB.mhd        (453KB - Enhancements)
│   │   │   ├── Recipe.mhd       (3.5MB - Recipes)
│   │   │   ├── Salvage.mhd      (5.4KB - Salvage)
│   │   │   ├── AttribMod.json   (Required)
│   │   │   ├── TypeGrades.json  (Required)
│   │   │   └── ... (other MHD files)
│   │   └── exported-json\       (Export destination)
│   └── docs\
│       └── windows-11-production-export-guide.md
└── MidsData\                    (You will create this)
    ├── input\                   (Copy MHD files here)
    └── output\                  (Exported JSON files)
```

## Step 3: Prepare MHD Data Files

1. **Create data directories**:
   ```powershell
   cd C:\Users\Public\Documents\MidsExport
   mkdir MidsData
   mkdir MidsData\input
   mkdir MidsData\output
   ```

2. **Copy MHD files**:
   - Copy ALL files from `mids-hero-web\data\Homecoming_2025-7-1111\` to `MidsData\input\`
   - This includes: `I12.mhd`, `EnhDB.mhd`, `Recipe.mhd`, `Salvage.mhd`, and all other files

## Step 4: Configure DataExporter

**Note**: The MidsReborn parser is already included in the repository at `mids-hero-web\external\MidsReborn\`. This is a complete City of Heroes data parser that can read MHD binary files.

1. **Navigate to DataExporter**:
   ```powershell
   cd C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter
   ```

2. **Verify MidsReborn is enabled** (automatic in Windows with MidsReborn present):
   ```powershell
   # Check the project file to confirm MidsReborn is detected
   type DataExporter.csproj | findstr MIDSREBORN
   ```
   
   You should see:
   ```xml
   <!-- Enable MidsReborn integration (only when MidsReborn is available) -->
   <DefineConstants Condition="Exists('..\external\MidsReborn\MidsReborn\MidsReborn.csproj')">MIDSREBORN</DefineConstants>
   ```
   
   **Note**: MidsReborn is automatically enabled when the external\MidsReborn folder exists. No manual editing required!

3. **For simple export** (if MidsReborn is not available):
   - The project automatically detects if MidsReborn is missing
   - Will only copy existing JSON files (AttribMod.json, TypeGrades.json)
   - **Note**: Without MidsReborn, MHD binary files cannot be parsed

## Step 5: Build DataExporter

```powershell
# Ensure you're in the DataExporter directory
cd C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter

# Restore packages
dotnet restore

# Build the project
dotnet build

# If successful, you'll see:
# Build succeeded.
#     0 Warning(s)
#     0 Error(s)
```

## Step 6: Run the Export

```powershell
# Run the exporter
dotnet run -- C:\Users\Public\Documents\MidsExport\MidsData\input C:\Users\Public\Documents\MidsExport\MidsData\output

# Or use the built executable directly (path may vary based on Windows version)
.\bin\Debug\net8.0-windows10.0.19041\DataExporter.exe C:\Users\Public\Documents\MidsExport\MidsData\input C:\Users\Public\Documents\MidsExport\MidsData\output
```

Expected output:

```text
[With MidsReborn enabled - Automatic when MidsReborn folder exists]
=== MidsReborn MHD to JSON Export ===
Input path: C:\Users\Public\Documents\MidsExport\MidsData\input
Output path: C:\Users\Public\Documents\MidsExport\MidsData\output

Initializing MidsReborn configuration...
Configuration initialized with data path: C:\Users\Public\Documents\MidsExport\MidsData\input

Loading MHD data files...
Loading server data... Skipped (not critical): Could not find file 'C:\Users\Public\Documents\MidsExport\MidsData\input\SData.mhd'.
Loading attribute modifiers... OK
Loading type grades... OK
Loading level tables... OK
Loading main database (I12.mhd)... OK - Loaded 10942 powers
Loading math tables... OK
Loading effect IDs... OK
Loading enhancement classes... OK
Loading enhancement database... OK - Loaded 631 enhancements
Loading origins... OK
Loading salvage... OK - Loaded 154 salvage items
Loading recipes... OK - Loaded 10244 recipes
Performing post-load setup... OK

=== Data Loading Summary ===
Archetypes: 61
Powersets: 3665
Powers: 10942
Enhancements: 631
Enhancement Sets: 98
Recipes: 10244
Salvage: 154

Exporting to JSON...
Attempting to use MidsReborn's built-in JSON export...
Built-in export successful!

=== Export Complete! ===

[Without MidsReborn - If MidsReborn folder is missing]
MidsReborn is not enabled. To enable:
1. Uncomment the MidsReborn reference in DataExporter.csproj
2. Add <DefineConstants>MIDSREBORN</DefineConstants> to the PropertyGroup
3. Rebuild the project
```

## Step 7: Verify Output

```powershell
# Check exported files
dir C:\Users\Public\Documents\MidsExport\MidsData\output\*.json

# View a sample file
type C:\Users\Public\Documents\MidsExport\MidsData\output\archetypes.json | more
```

You should see JSON files for:
- `archetypes.json`
- `powersets.json`
- `powers.json`
- `enhancements.json`
- `enhancement_sets.json`
- `recipes.json`
- `salvage.json`

After successful export, your MidsData\output\ directory should look like:

```
C:\Users\Public\Documents\MidsExport\MidsData\output\
├── archetypes.json         (61 records - Character classes)
├── powersets.json          (3,665 records - Power groups)
├── powers.json             (10,942 records - Individual powers)
├── enhancements.json       (631 records - Enhancement items)
├── enhancement_sets.json   (98 records - Set definitions)
├── recipes.json            (10,244 records - Crafting recipes)
├── salvage.json            (154 records - Salvage items)
├── AttribMod.json          (Copied from input)
└── TypeGrades.json         (Copied from input)
```

## Step 8: Transfer Files Back

### Option A: Network Share
1. Share the output folder or copy to a network location
2. Access from your main development machine

### Option B: Cloud Storage
1. Upload to OneDrive/Google Drive/Dropbox
2. Download on your development machine

### Option C: Git (if repository access)
```powershell
cd C:\Users\Public\Documents\MidsExport\mids-hero-web
git add data/exported-json/*
git commit -m "Add exported MidsReborn data"
git push
```

## Troubleshooting

### Common Issues and Solutions

1. **"dotnet is not recognized"**:
   - Close ALL PowerShell windows
   - Open fresh PowerShell as Administrator
   - Or use full path: `& "C:\Program Files\dotnet\dotnet.exe"`

2. **"Could not find project"**:
   - Ensure you're in the correct directory
   - Use `dir` to list files and verify DataExporter.csproj exists

3. **Build errors with MidsReborn**:
   - MidsReborn requires Windows-specific components
   - The project automatically adjusts target framework based on MidsReborn availability
   - If MidsReborn is present: targets net8.0-windows10.0.19041
   - If MidsReborn is missing: targets net8.0 (cross-platform)

4. **"Access denied" errors**:
   - Run PowerShell as Administrator
   - Check file permissions on MHD files

5. **Missing MHD files**:
   - Ensure ALL files from Homecoming folder are copied
   - Some files depend on others (e.g., JSON files are required)

## Quick Command Reference

```powershell
# Full process (copy and paste these commands)
cd C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter
dotnet restore
dotnet build
dotnet run -- C:\Users\Public\Documents\MidsExport\MidsData\input C:\Users\Public\Documents\MidsExport\MidsData\output
```

## Success Criteria

- Build completes without errors
- JSON files are created in output directory
- Files contain valid JSON data (not empty)
- No error messages during export

## Next Steps

After successful export:
1. Copy JSON files to your development machine
2. Place in `mids-hero-web/data/exported-json/`
3. Run database import script
4. Verify data in PostgreSQL

## Support

If you encounter issues:
1. Check the exact error message
2. Verify all prerequisites are installed
3. Ensure paths are correct (no typos)
4. Try running without MidsReborn if parsing fails
