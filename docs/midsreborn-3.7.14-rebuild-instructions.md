# MidsReborn 3.7.14 Rebuild Instructions

After replacing MidsReborn 3.7.11 with 3.7.14 in the external/ directory, follow these steps:

## Step 1: Clean Everything

```powershell
# Clean all previous builds
cd C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter
dotnet clean

cd C:\Users\Public\Documents\MidsExport\mids-hero-web\external\MidsReborn
dotnet clean
```

## Step 2: Build MidsReborn 3.7.14

```powershell
cd C:\Users\Public\Documents\MidsExport\mids-hero-web\external\MidsReborn

# Option A: Build individual C# projects (if full solution has issues)
dotnet build MRBLogging\MRBLogging.csproj
dotnet build MRBResourceLib\MRBResourceLib.csproj
dotnet build MidsReborn\MidsReborn.csproj

# Option B: Build full solution (if you have Visual Studio C++ tools)
dotnet build MidsReborn.sln
```

## Step 3: Build DataExporter

```powershell
cd C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter
dotnet build
```

## Step 4: Run the Export

```powershell
# Standard export
dotnet run -- C:\Users\Public\Documents\MidsExport\MidsData\input C:\Users\Public\Documents\MidsExport\MidsData\output

# If that fails, try direct mode (bypasses configuration)
dotnet run -- C:\Users\Public\Documents\MidsExport\MidsData\input C:\Users\Public\Documents\MidsExport\MidsData\output --direct
```

## Potential Issues and Solutions

### Issue 1: MidsReborn API Changes
If there are API changes in 3.7.14, you may see compile errors. Common fixes:

- `ConfigData.Current` might need to be `ConfigData.Instance`
- `EnhancementSets.Length` might need to be `EnhancementSets.Count`
- `SaveJsonDatabase` return type might have changed

### Issue 2: Missing Dependencies
If you get runtime errors about missing assemblies:

```powershell
# Copy all MidsReborn output to DataExporter
$source = "C:\Users\Public\Documents\MidsExport\mids-hero-web\external\MidsReborn\MidsReborn\bin\Debug\net8.0-windows10.0.19041"
$target = "C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter\bin\Debug\net8.0-windows10.0.19041"

Copy-Item "$source\*.dll" -Destination $target -Force
Copy-Item "$source\*.exe" -Destination $target -Force -ErrorAction SilentlyContinue
```

### Issue 3: Configuration Files
MidsReborn 3.7.14 might expect configuration files. If so:

1. Check if there's a default config in MidsReborn source
2. Copy any .json or .config files to the DataExporter output directory

## Verification

After successful build:
```powershell
# Check version in assembly
$dll = "C:\Users\Public\Documents\MidsExport\mids-hero-web\DataExporter\bin\Debug\net8.0-windows10.0.19041\MidsReborn.dll"
[System.Reflection.AssemblyName]::GetAssemblyName($dll) | Select-Object Name, Version
```

Should show: `MidsReborn, Version=3.7.14.0`

## Expected Output

With MidsReborn 3.7.14 and matching MHD files, you should see:

```
=== MidsReborn MHD to JSON Export ===
Loading MHD data files...
Loading main database (I12.mhd)... OK - Loaded 10942 powers
Loading enhancements... OK - Loaded 631 enhancements
...
Exporting to JSON...
=== Export Complete! ===
```

## If All Else Fails

Use the MidsReborn 3.7.14 GUI directly:
1. Run MidsReborn.exe from the 3.7.14 release
2. Tools → Export → Database to JSON
3. Select your output directory