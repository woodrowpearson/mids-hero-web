# MidsReborn Code Repository Embedding Guide

This guide explains how to embed the MidsReborn code repository into the RAG system for semantic search and code understanding capabilities.

## Prerequisites

1. **Gemini API Key** (optional but recommended for better embeddings)
   - Add to your `backend/.env` file:
     ```
     GEMINI_API_KEY="your-api-key-here"
     ```
   - The system will automatically load this from the `.env` file
   
2. **MidsReborn Repository**
   - Clone the MidsReborn repository to your local machine
   - Ensure you have access to the C# source files

3. **RAG System Setup**
   ```bash
   # Ensure RAG system is set up
   just rag-setup
   
   # Initialize ChromaDB collections
   just rag-init-db
   ```

## Step 1: Prepare the Repository

Ensure the MidsReborn repository is accessible:

```bash
# Example path - adjust to your actual location
export MIDSREBORN_PATH="/path/to/MidsReborn"

# Verify the path contains C# files
ls "$MIDSREBORN_PATH"/**/*.cs | head -10
```

## Step 2: Index the MidsReborn Codebase

Use the just command to index all C# files from the MidsReborn repository:

```bash
# Index MidsReborn C# files
just rag-index-midsreborn
```

This command will:
- Process all `*.cs` files in the repository
- Extract classes, methods, and properties using regex patterns
- Generate embeddings for each code chunk
- Store them in the `midsreborn_docs` ChromaDB collection

### Monitoring Progress

The indexing process will show:
- Number of files being processed
- Chunks created from each file
- Total documents indexed

Example output:
```
✓ Indexed 245 MidsReborn files
```

## Step 3: Verify the Indexing

Check the status of the indexed collection:

```bash
# Show RAG system status
just rag-status
```

Expected output:
```
RAG System Status
==================================================

Collections:
  - midsreborn_docs
    Document Count: 245
```

## Step 4: Search the Embedded Code

Test searching through the MidsReborn codebase:

```bash
# Search for power calculation logic
just rag-search "calculate damage power" midsreborn_docs 5

# Search for enhancement-related code
just rag-search "enhancement bonus calculation" midsreborn_docs

# Search for specific classes
just rag-search "class Power" midsreborn_docs
```

## Step 5: Advanced Indexing Options

### Index Specific Directories

If you only want to index certain parts of the codebase:

```bash
# Index only the Base directory
just rag-index "$MIDSREBORN_PATH/Base" midsreborn_docs

# Index only the PowerCalc namespace
just rag-index "$MIDSREBORN_PATH/PowerCalc" midsreborn_docs
```

### Force Re-indexing

To re-index the codebase (useful after updates):

```bash
# Reset the collection first
just rag-reset-collection midsreborn_docs

# Then re-index
just rag-index-midsreborn
```

## Step 6: Usage Monitoring

Monitor your embedding usage to stay within limits:

```bash
# Show usage report for last 7 days
just rag-usage 7

# Check current system status
just rag-status
```

## Step 7: Backup the Embedded Data

The indexed data is stored in ChromaDB's persistent storage. To backup:

```bash
# The ChromaDB data is stored in:
# backend/.claude/rag/chroma_db/

# Create a backup using standard tools:
cp -r backend/.claude/rag/chroma_db/ /path/to/backup/midsreborn_rag_backup
```

## Integration with Development Workflow

### Using the Embedded Code in Your Application

```python
from app.rag import ChromaDBManager, EmbeddingClient

async def search_midsreborn_code(query: str):
    """Search through MidsReborn codebase."""
    client = EmbeddingClient()
    manager = ChromaDBManager(client)
    
    try:
        results = await manager.query(
            "midsreborn_docs",
            [query],
            n_results=10,
            where={"file_type": ".cs"}  # Only C# files
        )
        
        for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
            print(f"File: {metadata['file_name']}")
            print(f"Type: {metadata.get('type', 'code')}")
            print(f"Content: {doc[:200]}...")
            print("---")
            
    finally:
        await client.close()
```

### Metadata Filtering

The system stores useful metadata for each chunk:

- `file_name`: Name of the source file
- `file_path`: Full path to the file
- `file_type`: Always `.cs` for C# files
- `type`: Can be `csharp_class`, `csharp_method`, `csharp_property`, or `csharp_file`
- `chunk_index`: Position of this chunk in the file
- `class_name`: For class chunks
- `method_name`: For method chunks

Example filtered search:
```python
# Search only in class definitions
results = await manager.query(
    "midsreborn_docs",
    ["power calculation"],
    where={"type": "csharp_class"}
)

# Search in specific files
results = await manager.query(
    "midsreborn_docs",
    ["enhancement"],
    where={"file_name": "Power.cs"}
)
```

## Performance Considerations

### Offline Mode

If you don't have a Gemini API key, the system will use offline embeddings:
- Less accurate for semantic similarity
- Consistent and deterministic
- No API costs
- Suitable for exact match searches

### Batch Processing

For large repositories, consider enabling batch processing:

```python
# In your .env or environment
BATCH_PROCESSING_ENABLED=true
RAG_BATCH_SIZE=1000
```

This provides:
- 50% cost savings on embeddings
- Better throughput for large codebases
- Automatic retry on failures

### Caching

The system automatically caches embeddings:
- Located in `.claude/rag/cache/`
- Reuses embeddings for identical text
- Reduces API calls and costs

## Troubleshooting

### Common Issues

1. **"Collection already exists" error**
   ```bash
   # Reset and recreate the collection
   just rag-reset-collection midsreborn_docs
   ```

2. **Out of memory during indexing**
   - Process smaller directories at a time
   - Reduce chunk size in configuration

3. **API quota exceeded**
   - System will automatically fall back to offline mode
   - Check usage with `just rag-usage`
   - Consider batch processing for cost savings

4. **No results found**
   - Verify files were indexed: `just rag-status`
   - Try broader search terms
   - Check if offline mode is limiting semantic search

### Debug Mode

For detailed logging:
```bash
# Set logging level in your .env file
LOG_LEVEL=DEBUG

# Run indexing with debug output
just rag-index-midsreborn
```

## Best Practices

1. **Regular Updates**: Re-index after significant code changes
2. **Selective Indexing**: Index only relevant directories to save resources
3. **Backup Strategy**: Regular backups before re-indexing
4. **Monitor Usage**: Keep track of token usage and costs
5. **Test Searches**: Verify search quality with known code patterns

## Next Steps

- Integrate RAG search into your development tools
- Create custom search interfaces for specific use cases
- Build code analysis tools using the embedded knowledge
- Implement automated documentation generation

For more information, see the [RAG System Documentation](./rag-system-overview.md).