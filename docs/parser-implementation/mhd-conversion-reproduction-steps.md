# Steps to Reproduce MHD Conversion

## Current Process (What Was Done)

### Prerequisites
- .NET SDK installed
- DataExporter project built

### Step 1: Build DataExporter
```bash
cd DataExporter
dotnet build
```

### Step 2: Extract Text from MHD Files
```bash
# Use --mac flag for Mac compatibility
dotnet run -- /path/to/mhd/files /path/to/output --mac
```

This creates `*_extracted.txt` files for each MHD file.

### Step 3: Parse Text to JSON
The DataExporter automatically runs TextToJsonParser, creating:
- `I12_structured.json`
- `enhancements.json`
- `salvage.json`
- `recipes.json`

### Step 4: Specialized I12 Power Parsing
```bash
cd backend
python scripts/parse_i12_text.py ../data/exported-json-latest/I12_extracted.txt ../data/exported-json-latest/I12_powers.json
```

This creates the detailed `I12_powers.json` with proper power structure.

### Step 5: Import to Database
```bash
# Using the just commands (expects JSON files)
just i12-import data/exported-json-latest/I12_powers.json
```

## Quick Reproduction for New MHD File

For the `I12-dev-071925.mhd` file:

1. **Option A: Use Existing Text Extractor**
   ```bash
   # Already done - we created extract_mhd_text.py
   python scripts/extract_mhd_text.py external/dev/I12-dev-071925.mhd data/dev/I12-dev-071925_extracted.txt
   ```

2. **Option B: Build and Use DataExporter**
   ```bash
   cd DataExporter
   dotnet build
   dotnet run -- ../external/dev ../data/dev --mac
   ```

3. **Parse to JSON**
   ```bash
   cd backend
   python scripts/parse_i12_text.py ../data/dev/I12-dev-071925_extracted.txt ../data/dev/I12-dev-071925_powers.json
   ```

4. **Import**
   ```bash
   just i12-import data/dev/I12-dev-071925_powers.json
   ```

## Notes
- The text extraction step loses binary structure but preserves readable content
- The JSON parsing relies on pattern matching in the text
- For production, implement direct MHD → JSON conversion as outlined in the main report