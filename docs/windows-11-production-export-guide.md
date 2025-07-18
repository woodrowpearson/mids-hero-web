# Windows 11 Production-Ready Data Export Guide

## Overview

This is a streamlined, production-ready guide for exporting City of Heroes MHD data files using Windows 11 Pro and PowerShell. The guide uses .NET 8.0 LTS for stability and long-term support.

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

1. **Navigate to DataExporter**:
   ```powershell
   cd C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter
   ```

2. **Enable MidsReborn** (if you want full export):
   ```powershell
   # Open the project file in Notepad
   notepad DataExporter.csproj
   ```
   
   Remove the comment markers around the MidsReborn reference:
   ```xml
   <ItemGroup>
     <ProjectReference Include="..\external\MidsReborn\MidsReborn\MidsReborn.csproj" />
   </ItemGroup>
   ```
   
   Save and close Notepad.

3. **For simple export** (no MidsReborn):
   - Leave the file as-is (MidsReborn commented out)
   - This will use SimpleMhdExporter

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

# Or use the built executable directly
.\bin\Debug\net8.0\DataExporter.exe C:\Users\Public\Documents\MidsExport\MidsData\input C:\Users\Public\Documents\MidsExport\MidsData\output
```

Expected output:
```
Starting data export...
Input directory: C:\Users\Public\Documents\MidsExport\MidsData\input
Output directory: C:\Users\Public\Documents\MidsExport\MidsData\output

[With MidsReborn enabled]
Loading MidsReborn database...
Exporting archetypes... Done! (61 exported)
Exporting powersets... Done! (3665 exported)
Exporting powers... Done! (10942 exported)
...

[With SimpleMhdExporter]
Using simplified exporter (MidsReborn not available)
Creating placeholder JSON files...
...

Export complete!
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
   - If it fails, comment out the MidsReborn reference and use SimpleMhdExporter

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
4. Try SimpleMhdExporter if MidsReborn fails