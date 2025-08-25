# RAG (Retrieval-Augmented Generation) Module

This module implements a cost-optimized RAG system for the Mids Hero Web project using Google's Gemini embeddings and ChromaDB for vector storage.

## Features

- **Gemini Embeddings**: Uses Google's state-of-the-art `gemini-embedding-001` model
- **Offline Fallback**: Deterministic embeddings when API is unavailable
- **Cost Optimization**: Batch processing for 50% cost savings
- **Multi-Format Support**: Processes Python, TypeScript, Markdown, JSON, SQL, C# files
- **Usage Monitoring**: Track tokens, costs, and set alerts
- **Caching**: Local embedding cache to reduce API calls
- **ChromaDB Integration**: Persistent vector storage with metadata filtering

## Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -e .
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

3. **Initialize Collections**:
   ```python
   from app.rag import ChromaDBManager, EmbeddingClient
   
   client = EmbeddingClient()
   db = ChromaDBManager(client)
   # Collections are auto-initialized
   ```

## Usage

### CLI Commands

```bash
# Generate embedding for text
python -m app.rag.cli embed -t "Your text here"

# Index a directory
python -m app.rag.cli index -p /path/to/code -c mids_hero_codebase

# Search for similar documents
python -m app.rag.cli search -q "power calculation formula" -n 10

# Check system status
python -m app.rag.cli status

# View usage report
python -m app.rag.cli usage-report -d 7
```

### Python API

```python
import asyncio
from app.rag import EmbeddingClient, ChromaDBManager, DocumentProcessor

async def main():
    # Initialize components
    client = EmbeddingClient()
    db = ChromaDBManager(client)
    processor = DocumentProcessor()
    
    # Process and index documents
    chunks = await processor.process_file(Path("example.py"))
    
    documents = [chunk['text'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    ids = [chunk['metadata']['chunk_id'] for chunk in chunks]
    
    await db.add_documents("mids_hero_codebase", documents, metadatas, ids)
    
    # Search
    results = await db.query("mids_hero_codebase", ["damage calculation"], n_results=5)
    
    # Cleanup
    await client.close()

asyncio.run(main())
```

### Batch Processing

```python
from app.rag import BatchProcessor

# For cost optimization with large datasets
processor = BatchProcessor(client)

# Add items to batch
tracking_ids = []
for text in large_text_list:
    tracking_id = processor.add_to_batch(text)
    tracking_ids.append(tracking_id)

# Process batch (50% cost savings)
result = await processor.process_batch()

# Get results
for tracking_id in tracking_ids:
    result = processor.get_result(tracking_id)
    embedding = result['embedding']
```

## Collections

Default collections created:
- `mids_hero_codebase`: Project source code and documentation
- `midsreborn_docs`: MidsReborn documentation and code
- `game_data`: City of Heroes game mechanics and data

## Cost Management

- **Free Tier**: Gemini API includes free monthly quota
- **Batch Processing**: 50% discount for batch operations
- **Caching**: Reduces redundant API calls
- **Monitoring**: Daily limits and alerts prevent overages

## Offline Mode

When API is unavailable or no key is configured:
- Uses deterministic hash-based embeddings
- Maintains consistent results across runs
- Suitable for development and testing
- Automatically falls back when API errors occur

## File Processing

Supported formats with specialized handling:
- **Python** (.py): AST parsing for functions/classes
- **TypeScript/TSX** (.ts, .tsx): Regex-based component extraction
- **JavaScript/JSX** (.js, .jsx): Similar to TypeScript
- **Markdown** (.md): Section-aware chunking
- **JSON** (.json): Key-based splitting for large files
- **SQL** (.sql): Statement-based chunking
- **C#** (.cs): Class/method extraction for MidsReborn

## Usage Monitoring

Track and control costs:
```python
from app.rag import UsageMonitor

monitor = UsageMonitor()

# Register alert callback
def alert_handler(message):
    print(f"ALERT: {message}")

monitor.register_alert_callback(alert_handler)

# Check current usage
usage = monitor.get_current_usage()
print(f"Used {usage['percentage']:.1f}% of daily limit")

# Get detailed report
report = monitor.get_usage_report(days=30)
```

## Testing

Run tests:
```bash
pytest tests/rag/
```

## Architecture

```
app/rag/
├── __init__.py          # Module exports
├── client.py           # Gemini embedding client
├── database.py         # ChromaDB manager
├── processor.py        # Document processor
├── batch_processor.py  # Batch optimization
├── monitor.py          # Usage tracking
├── config.py           # Settings
├── exceptions.py       # Custom exceptions
└── cli.py              # Command-line interface
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | None |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | None |
| `CHROMADB_PATH` | ChromaDB storage path | `.claude/rag/db` |
| `EMBEDDING_CACHE_PATH` | Cache directory | `.claude/rag/cache` |
| `BATCH_PROCESSING_ENABLED` | Enable batch mode | `true` |
| `OFFLINE_MODE_FALLBACK` | Allow offline mode | `true` |
| `RAG_DAILY_TOKEN_LIMIT` | Daily token limit | `1000000` |
| `RAG_ALERT_THRESHOLD` | Alert at % of limit | `0.8` |

## Best Practices

1. **Always use batch processing** for large datasets
2. **Monitor usage** regularly to avoid surprises
3. **Cache embeddings** for frequently accessed content
4. **Use metadata filters** in queries for better results
5. **Chunk appropriately** based on content type
6. **Test offline mode** for development