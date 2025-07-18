# JSON Export Documentation

## Overview

The DataExporter supports two methods of exporting MHD data to JSON format:

1. **Built-in Export** - Uses MidsReborn's `DatabaseAPI.SaveJsonDatabase()`
2. **Custom Export** - Direct serialization of database objects

## Built-in Export

The built-in export method leverages MidsReborn's native JSON serialization:

```csharp
var serializer = Serializer.GetSerializer();
DatabaseAPI.SaveJsonDatabase(serializer);
```

### Output Formats

The built-in export may create:
- A compressed ZIP archive containing JSON files
- A single JSON file with all data
- Multiple JSON files in the output directory

### Archive Extraction

If a compressed archive is created, the `JsonArchiveExtractor` will:
1. Detect the archive format (ZIP or embedded JSON)
2. Extract files to the output directory
3. Rename files to standard names (e.g., `archetypes.json`)

## Custom Export

The custom export method serializes each data type individually:

### Output Files

- `archetypes.json` - Character archetypes/classes
- `powersets.json` - Power sets for each archetype
- `powers.json` - Individual power definitions
- `enhancements.json` - Enhancement items
- `enhancement_sets.json` - Set bonus definitions
- `recipes.json` - Crafting recipes
- `salvage.json` - Salvage items

### Serialization Settings

```csharp
var jsonSettings = new JsonSerializerSettings
{
    Formatting = Formatting.Indented,
    ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
    TypeNameHandling = TypeNameHandling.Auto
};
```

- **Indented**: Human-readable formatting
- **Ignore circular references**: Prevents serialization errors
- **Auto type handling**: Preserves type information for polymorphic objects

## Error Handling

The export process includes multiple fallback mechanisms:

1. Try built-in export
2. If successful, look for archives to extract
3. If no archive, check for direct JSON files
4. If built-in fails, use custom export
5. If any step fails, log error and continue

## Usage

```bash
dotnet run -- <input_path> <output_path>
```

The exporter will automatically:
- Create the output directory if needed
- Attempt both export methods
- Extract any archives created
- Organize output files with standard names