"""CLI interface for RAG system."""

import asyncio
from pathlib import Path

import click

from .batch_processor import BatchProcessor
from .client import EmbeddingClient
from .config import rag_settings
from .database import ChromaDBManager
from .monitor import UsageMonitor
from .processor import DocumentProcessor


@click.group()
def cli():
    """RAG system CLI for City of Heroes build planner."""
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Force reset existing collections")
def setup(force: bool):
    """Set up RAG system collections."""

    async def _setup():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)

        try:
            collections = [
                rag_settings.codebase_collection,
                rag_settings.midsreborn_collection,
                rag_settings.game_data_collection,
            ]

            for collection in collections:
                if force:
                    try:
                        manager.delete_collection(collection)
                    except Exception:
                        pass

                try:
                    manager.create_collection(collection, {"type": collection})
                    click.echo(f"✓ Created collection: {collection}")
                except Exception as e:
                    if "already exists" in str(e):
                        click.echo(f"✓ Collection already exists: {collection}")
                    else:
                        raise

            click.echo("✓ Setup completed successfully")
        finally:
            await client.close()

    asyncio.run(_setup())


@cli.group()
def index():
    """Index data into RAG system."""
    pass


@index.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--pattern", "-p", multiple=True, help="File patterns to include")
def codebase(path: str, pattern: tuple):
    """Index codebase files."""

    async def _index():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)
        processor = DocumentProcessor()

        try:
            patterns = list(pattern) if pattern else ["**/*.py", "**/*.ts", "**/*.tsx"]
            chunks = await processor.process_directory(Path(path), patterns)

            if chunks:
                documents = [chunk["text"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]
                ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

                await manager.add_documents(
                    rag_settings.codebase_collection,
                    documents,
                    metadatas,
                    ids
                )

                click.echo(f"✓ Indexed {len(chunks)} documents from {path}")
            else:
                click.echo("No documents found to index")

        finally:
            await client.close()

    asyncio.run(_index())


@index.command()
@click.argument("path", type=click.Path(exists=True))
def midsreborn(path: str):
    """Index MidsReborn source files."""

    async def _index():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)
        processor = DocumentProcessor()

        try:
            chunks = await processor.process_directory(
                Path(path),
                patterns=["**/*.cs"]
            )

            if chunks:
                documents = [chunk["text"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]
                ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

                await manager.add_documents(
                    rag_settings.midsreborn_collection,
                    documents,
                    metadatas,
                    ids
                )

                click.echo(f"✓ Indexed {len(chunks)} MidsReborn files")

        finally:
            await client.close()

    asyncio.run(_index())


@index.command()
@click.argument("path", type=click.Path(exists=True))
def i12(path: str):
    """Index I12 game data files."""

    async def _index():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)
        processor = DocumentProcessor()

        try:
            chunks = await processor.process_directory(
                Path(path),
                patterns=["**/*.json", "**/*.txt"]
            )

            if chunks:
                documents = [chunk["text"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]
                ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

                await manager.add_documents(
                    rag_settings.game_data_collection,
                    documents,
                    metadatas,
                    ids
                )

                click.echo(f"✓ Indexed {len(chunks)} I12 data files")

        finally:
            await client.close()

    asyncio.run(_index())


@cli.command()
@click.argument("query")
@click.option("--collection", "-c", help="Collection to search")
@click.option("-n", "--limit", default=5, help="Number of results")
def search(query: str, collection: str, limit: int):
    """Search for content in RAG system."""

    async def _search():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)

        try:
            collection_name = collection or rag_settings.codebase_collection
            results = await manager.query(collection_name, [query], n_results=limit)

            if results["documents"][0]:
                click.echo(f"Results for '{query}':")
                for i, doc in enumerate(results["documents"][0], 1):
                    click.echo(f"\n{i}. {doc[:200]}...")
                    if results["metadatas"][0][i-1]:
                        metadata = results["metadatas"][0][i-1]
                        click.echo(f"   File: {metadata.get('file_name', 'Unknown')}")
            else:
                click.echo("No results found")

        finally:
            await client.close()

    asyncio.run(_search())


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed status")
def status(verbose: bool):
    """Show RAG system status."""

    async def _status():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)
        monitor = UsageMonitor()

        try:
            click.echo("RAG System Status")
            click.echo("=" * 50)

            collections = manager.list_collections()
            click.echo("\nCollections:")
            for coll in collections:
                click.echo(f"  - {coll['name']}")
                click.echo(f"    Document Count: {coll['count']}")

            if verbose:
                click.echo("\nConfiguration:")
                click.echo(f"  ChromaDB Path: {rag_settings.chromadb_path}")
                click.echo(f"  Cache Path: {rag_settings.embedding_cache_path}")
                click.echo(f"  Batch Size: {rag_settings.batch_size}")

                usage = monitor.get_current_usage()
                click.echo("\nUsage Statistics:")
                click.echo(f"  Tokens Used: {usage['tokens']}")
                click.echo(f"  Daily Limit: {usage['limit']}")
                click.echo(f"  Percentage: {usage['percentage']:.1f}%")

        finally:
            await client.close()

    asyncio.run(_status())


@cli.group()
def batch():
    """Batch processing commands."""
    pass


@batch.command(name="status")
def batch_status():
    """Show batch processing status."""

    async def _status():
        client = EmbeddingClient()
        processor = BatchProcessor(client)

        try:
            status = processor.get_batch_status()

            click.echo("Batch Processing Status")
            click.echo("=" * 50)
            click.echo(f"Pending items: {status['pending_items']}")
            click.echo(f"Processing: {status['processing']}")
            click.echo(f"Results available: {status['results_available']}")

        finally:
            await client.close()

    asyncio.run(_status())


@batch.command()
@click.argument("file", type=click.Path(exists=True))
def add(file: str):  # noqa: ARG001
    """Add file to batch queue."""
    click.echo("Batch add command not fully implemented")


@batch.command()
def process():
    """Process pending batch."""

    async def _process():
        client = EmbeddingClient()
        processor = BatchProcessor(client)

        try:
            # Check if batch processing is enabled
            if not rag_settings.batch_processing_enabled:
                click.echo("⚠️  Batch processing is disabled")
                return

            # Process the batch
            status = processor.get_batch_status()
            if status["pending_items"] == 0:
                click.echo("No pending items to process")
                return

            click.echo(f"Processing {status['pending_items']} pending items...")
            results = await processor.process_batch()

            if results:
                click.echo("✓ Processed batch successfully")
                click.echo(f"Total items: {results['total_items']}")
                click.echo(f"Successful: {results['successful_items']}")
                if results['failed_items'] > 0:
                    click.echo(f"Failed: {results['failed_items']}")
                click.echo(f"Cost savings: ${results['cost_savings']:.4f}")
            else:
                click.echo("✗ Batch processing failed")

        finally:
            await client.close()

    asyncio.run(_process())


@cli.command()
@click.option("--days", "-d", default=7, help="Number of days to report")
def usage(days: int):
    """Show usage report."""
    monitor = UsageMonitor()

    report = monitor.get_usage_report(days=days)

    click.echo(f"Usage Report ({days} days)")
    click.echo("=" * 50)
    click.echo(f"Total Tokens: {report['summary']['total_tokens']:,}")
    click.echo(f"Total Cost: ${report['summary']['total_cost']:.4f}")
    click.echo(f"Total Requests: {report['summary']['total_requests']:,}")


@cli.command()
@click.option("--collection", "-c", help="Collection to reset")
@click.option("--all", is_flag=True, help="Reset all collections")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def reset(collection: str, all: bool, yes: bool):  # noqa: ARG001
    """Reset collections."""

    async def _reset():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)

        try:
            if all:
                collections = [
                    rag_settings.codebase_collection,
                    rag_settings.midsreborn_collection,
                    rag_settings.game_data_collection,
                ]
                for coll in collections:
                    manager.reset_collection(coll)
                click.echo("✓ Reset all collections")
            elif collection:
                manager.reset_collection(collection)
                click.echo(f"✓ Reset collection: {collection}")
            else:
                click.echo("Please specify --collection or --all")

        finally:
            await client.close()

    asyncio.run(_reset())


@cli.command()
@click.option("--path", "-p", type=click.Path(), help="Backup path")
def backup(path: str):
    """Backup ChromaDB database."""

    async def _backup():
        client = EmbeddingClient()
        manager = ChromaDBManager(client)

        try:
            backup_path = Path(path) if path else None
            result_path = manager.backup_database(backup_path)
            click.echo(f"✓ Backup created at: {result_path}")

        finally:
            await client.close()

    asyncio.run(_backup())


@cli.command()
def config():
    """Show RAG configuration."""
    click.echo("RAG Configuration")
    click.echo("=" * 50)
    click.echo(f"chromadb_path: {rag_settings.chromadb_path}")
    click.echo(f"embedding_cache_path: {rag_settings.embedding_cache_path}")
    click.echo(f"batch_size: {rag_settings.batch_size}")
    click.echo(f"daily_token_limit: {rag_settings.daily_token_limit}")
    click.echo(f"embedding_model: {rag_settings.embedding_model}")


@cli.command()
@click.option("--text", "-t", required=True, help="Text to generate embedding for")
def embed(text: str):
    """Generate embedding for text."""

    async def _embed():
        client = EmbeddingClient()

        try:
            # Get embedding
            embedding = await client.get_embedding(text)

            # Show basic info
            click.echo(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
            click.echo(f"Embedding dimension: {len(embedding)}")
            click.echo(f"Mode: {'Offline' if client.offline_mode else 'Online (Gemini)'}")

            # Show first few values
            click.echo(f"First 10 values: {embedding[:10]}")

            # Calculate embedding norm
            import math
            norm = math.sqrt(sum(x*x for x in embedding))
            click.echo(f"Embedding norm: {norm:.4f}")

        finally:
            await client.close()

    asyncio.run(_embed())


if __name__ == "__main__":
    cli()
