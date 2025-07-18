# Windows VM Data Export Guide - Key Corrections Summary

## Important Updates Made to the Guide

### 1. **.NET Version**
- **Changed from**: .NET 8.0
- **Changed to**: .NET 9.0
- **Reason**: DataExporter.csproj targets net9.0

### 2. **Windows Version Recommendation**
- **Added**: Windows 10 is recommended over Windows 11
- **Reason**: Windows 11 requires TPM 2.0 and has stricter requirements that cause VM issues

### 3. **MidsReborn Reference**
- **Added**: Step to uncomment the MidsReborn reference in DataExporter.csproj
- **Reason**: The reference is commented out by default due to Windows dependencies

### 4. **MHD Files to Copy**
- **Changed from**: Specific list of 9 files
- **Changed to**: Copy entire Homecoming_2025-7-1111 folder contents
- **Added**: Note about JSON files (AttribMod.json, TypeGrades.json) being required
- **Reason**: MidsReborn expects the full data folder structure with all dependencies

### 5. **Build Output Path**
- **Changed from**: `bin\Debug\net8.0`
- **Changed to**: `bin\Debug\net9.0` (with note to check net8.0 if needed)
- **Reason**: Build may create output in different folder than expected

### 6. **Troubleshooting Section**
- **Added**: Windows VM specific issues
- **Added**: Note about MidsReborn Windows dependencies
- **Added**: Full data folder structure requirement
- **Updated**: All .NET references from 8.0 to 9.0

## Key Files Verified

1. **DataExporter exists**: ✅ At `/DataExporter/`
2. **MidsReborn exists**: ✅ At `/external/MidsReborn/`
3. **MHD files exist**: ✅ All required files in `/data/Homecoming_2025-7-1111/`
4. **DataExporter.csproj**: Targets .NET 9.0 with commented MidsReborn reference

## Windows VM Requirements Summary

- **Recommended OS**: Windows 10 x64 (not Windows 11)
- **RAM**: 4GB minimum for VM
- **Disk**: 40GB
- **.NET SDK**: Version 9.0
- **No TPM required** for Windows 10

The guide is now accurate and ready for use.