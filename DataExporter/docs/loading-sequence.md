# MidsReborn Database Loading Sequence

## Overview

This document describes the proper loading sequence for MHD files when using the MidsReborn parser. The sequence is critical as some data depends on others being loaded first.

## Loading Order

The `MidsRebornExporter.LoadAllData()` method implements the following sequence:

1. **Server Data** (Optional)
   - File: `SData.json` or `SData.mhd`
   - Non-critical - wrapped in try-catch

2. **Attribute Modifiers**
   - File: `AttribMod.mhd` or `AttribMod.json`
   - Creates new Modifiers instance

3. **Type Grades**
   - File: `TypeGrades.json`
   - Required for power calculations

4. **Level Tables**
   - Files: `NLevels.mhd`, `RLevels.mhd`
   - Required for level-based calculations

5. **Main Database**
   - File: `I12.mhd`
   - Contains all powers, powersets, and archetypes

6. **Math Tables**
   - File: `Maths.mhd`
   - Required for damage calculations

7. **Effect IDs**
   - File: `GlobalMods.mhd`
   - Maps effect names to IDs

8. **Enhancement Classes**
   - File: `EClasses.mhd`
   - Defines enhancement categories

9. **Enhancement Database**
   - File: `EnhDB.mhd`
   - All enhancement definitions

10. **Origins**
    - File: `Origins.mhd`
    - Character origin data

11. **Salvage**
    - File: `Salvage.mhd`
    - Crafting salvage items

12. **Recipes**
    - File: `Recipe.mhd`
    - Enhancement recipes

## Post-Loading Setup

After all files are loaded, these methods must be called:

1. `DatabaseAPI.FillGroupArray()` - Populates group arrays
2. `DatabaseAPI.AssignSetBonusIndexes()` - Links set bonuses
3. `DatabaseAPI.AssignRecipeIDs()` - Maps recipes to enhancements

## Error Handling

- **Server Data**: Optional, errors are caught and logged
- **All Other Files**: Required, errors stop the loading process
- **Progress Reporting**: Each step reports success/failure
- **Summary**: Final summary shows counts of loaded items

## Dependencies

Some data files depend on others:
- Enhancements require Enhancement Classes
- Recipes require Enhancements and Salvage
- Powers require Level Tables and Math Tables

## Implementation

See `DataExporter/MidsRebornExporter.cs` method `LoadAllData()` for the complete implementation.