# MHD File Format Analysis

## Overview

MHD (Mids Hero Designer) files are binary format files used by MidsReborn to store City of Heroes game data. The format uses .NET BinaryReader/BinaryWriter for serialization.

## File Types

Based on the Files.cs constants:
- `I12.mhd` - Main powers database
- `NLevels.mhd` - Normal levels data
- `RLevels.mhd` - Revised levels data
- `Maths.mhd` - Mathematics tables
- `EClasses.mhd` - Enhancement classes
- `Origins.mhd` - Origin data
- `Salvage.mhd` - Salvage items
- `Recipe.mhd` - Recipes
- `EnhDB.mhd` - Enhancement database
- `BBCode.mhd` - BBCode updates
- `Compare.mhd` - Overrides
- `AttribMod.mhd` - Attribute modifiers
- `GlobalMods.mhd` - Effect IDs
- `I9.mhd` - Graphics data
- `SData.mhd` - Server data

## Binary Format Structure

Each file type has:
1. A header string for validation
2. Version information (sometimes)
3. Count of items
4. Binary serialized data for each item

### Headers
- Main DB: "Mids Reborn Powers Database"
- Enhancement DB: "Mids Reborn Enhancement Database"
- Salvage: "Mids Reborn Salvage Database"
- Recipe: "Mids Reborn Recipe Database"
- AttribMod: "Mids Reborn Attribute Modifier Tables"
- ServerData: "Mids Reborn Server Data"

## Key Classes for Parsing

### Core Data Classes
1. **Archetype** - Character archetypes (Tank, Scrapper, etc.)
2. **Power** - Individual powers
3. **Powerset** - Groups of powers
4. **Enhancement** - Enhancement items
5. **EnhancementSet** - Enhancement set bonuses
6. **Recipe** - Crafting recipes
7. **Salvage** - Salvage items
8. **Effect** - Power effects

### Reading Pattern

All classes follow this pattern:
```csharp
public ClassName(BinaryReader reader)
{
    // Read primitive types in order
    Property1 = reader.ReadString();
    Property2 = reader.ReadInt32();
    Property3 = reader.ReadSingle(); // float
    Property4 = reader.ReadBoolean();
    // Arrays are prefixed with count
    var count = reader.ReadInt32();
    ArrayProperty = new Type[count];
    for (int i = 0; i < count; i++)
        ArrayProperty[i] = reader.ReadType();
}
```

### Writing Pattern
```csharp
public void StoreTo(BinaryWriter writer)
{
    writer.Write(Property1);
    writer.Write(Property2);
    writer.Write(Property3);
    writer.Write(Property4);
    // Arrays write count first
    writer.Write(ArrayProperty.Length);
    foreach (var item in ArrayProperty)
        writer.Write(item);
}
```

## Dependencies to Remove

The MidsReborn code has several Windows-specific dependencies:
1. `System.Windows.Forms` - Used for MessageBox, dialogs
2. `System.Drawing` - Used for images/graphics
3. Windows-specific target framework
4. UI controls and forms

## Minimal Classes Needed

For cross-platform MHD parsing, we need:
1. Core data classes (without UI dependencies)
2. Binary serialization/deserialization methods
3. Enums definitions
4. Basic file I/O

## Next Steps

1. Create Python equivalents of the core data classes
2. Implement binary reading using Python's struct module
3. Test with actual MHD files
4. Create import utilities for PostgreSQL database