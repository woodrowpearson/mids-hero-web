"""CLI interface for RAG operations."""

import asyncio
from pathlib import Path

import click

from .client import EmbeddingClient
from .database import ChromaDBManager
from .monitor import UsageMonitor
from .processor import DocumentProcessor


@click.group()
def cli():
    """RAG system CLI for Mids Hero Web."""
    pass


@cli.command()
@click.option("--text", "-t", required=True, help="Text to generate embedding for")
@click.option("--offline", is_flag=True, help="Force offline mode")
def embed(text: str, offline: bool):
    """Generate embedding for text."""

    async def _embed():
        client = EmbeddingClient()
        if offline:
            client.offline_mode = True

        try:
            embedding = await client.embed_text(text)
            click.echo(f"Embedding dimension: {len(embedding)}")
            click.echo(f"First 10 values: {embedding[:10]}")
            click.echo(f"Mode: {'Offline' if client.offline_mode else 'Online'}")
        finally:
            await client.close()

    asyncio.run(_embed())


@cli.command()
@click.option(
    "--path", "-p", type=click.Path(exists=True), required=True, help="Path to index"
)
@click.option(
    "--collection", "-c", default="mids_hero_codebase", help="Collection name"
)
@click.option("--pattern", "-g", multiple=True, help="File patterns to include")
def index(path: str, collection: str, pattern: tuple):
    """Index files or directories into ChromaDB."""

    async def _index():
        path_obj = Path(path)

        # Initialize components
        client = EmbeddingClient()
        db = ChromaDBManager(client)
        processor = DocumentProcessor()
        monitor = UsageMonitor()

        try:
            if path_obj.is_file():
                # Process single file
                click.echo(f"Processing file: {path_obj}")
                chunks = await processor.process_file(path_obj)
            else:
                # Process directory
                patterns = list(pattern) if pattern else None
                click.echo(f"Processing directory: {path_obj}")
                chunks = await processor.process_directory(path_obj, patterns=patterns)

            click.echo(f"Generated {len(chunks)} chunks")

            # Prepare for indexing
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]

            # Index in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_meta = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                await db.add_documents(collection, batch_docs, batch_meta, batch_ids)

                # Track usage
                total_tokens = (
                    sum(len(doc.split()) for doc in batch_docs) * 2
                )  # Rough estimate
                monitor.track_usage(total_tokens, "indexing")

                click.echo(
                    f"Indexed batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}"
                )

            click.echo(
                f"Successfully indexed {len(documents)} chunks to collection '{collection}'"
            )

            # Show usage
            usage = monitor.get_current_usage()
            click.echo(
                f"\nUsage: {usage['tokens']} / {usage['limit']} tokens ({usage['percentage']:.1f}%)"
            )
            click.echo(f"Cost: ${usage['cost']:.4f}")

        finally:
            await client.close()

    asyncio.run(_index())


@cli.command()
@click.option("--query", "-q", required=True, help="Search query")
@click.option(
    "--collection", "-c", default="mids_hero_codebase", help="Collection to search"
)
@click.option("--limit", "-n", default=5, help="Number of results")
def search(query: str, collection: str, limit: int):
    """Search for similar documents."""

    async def _search():
        client = EmbeddingClient()
        db = ChromaDBManager(client)
        monitor = UsageMonitor()

        try:
            # Perform search
            results = await db.query(collection, [query], n_results=limit)

            # Track usage
            monitor.track_usage(len(query.split()) * 2, "search")

            # Display results
            if results["documents"] and results["documents"][0]:
                click.echo(f"\nFound {len(results['documents'][0])} results:\n")

                for i, (doc, metadata, distance) in enumerate(
                    zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0],
                        strict=False,
                    )
                ):
                    click.echo(f"--- Result {i+1} (distance: {distance:.4f}) ---")
                    click.echo(f"File: {metadata.get('file_path', 'Unknown')}")
                    click.echo(f"Type: {metadata.get('type', 'Unknown')}")

                    # Truncate document for display
                    doc_preview = doc[:300] + "..." if len(doc) > 300 else doc
                    click.echo(f"Content: {doc_preview}\n")
            else:
                click.echo("No results found.")

        finally:
            await client.close()

    asyncio.run(_search())


@cli.command()
def status():
    """Show RAG system status."""

    async def _status():
        client = EmbeddingClient()
        db = ChromaDBManager(client)
        monitor = UsageMonitor()

        try:
            # System status
            click.echo("=== RAG System Status ===\n")

            # Embedding client status
            click.echo(
                f"Embedding Client: {'Online' if client.is_online() else 'Offline'}"
            )
            click.echo(f"Embedding Model: {client.model_name}")
            click.echo(f"Cache Directory: {client.cache_dir}")

            # Collections
            click.echo("\nCollections:")
            for collection_info in db.list_collections():
                click.echo(
                    f"  - {collection_info['name']}: {collection_info['count']} documents"
                )

            # Usage
            usage = monitor.get_current_usage()
            click.echo("\nToday's Usage:")
            click.echo(
                f"  Tokens: {usage['tokens']} / {usage['limit']} ({usage['percentage']:.1f}%)"
            )
            click.echo(f"  Requests: {usage['requests']}")
            click.echo(f"  Cost: ${usage['cost']:.4f}")

            # Recent usage
            report = monitor.get_usage_report(days=7)
            click.echo("\nLast 7 Days:")
            click.echo(f"  Total Tokens: {report['summary']['total_tokens']}")
            click.echo(f"  Total Cost: ${report['summary']['total_cost']:.4f}")
            click.echo(
                f"  Avg per Day: {report['summary']['avg_tokens_per_day']:.0f} tokens"
            )

        finally:
            await client.close()

    asyncio.run(_status())


@cli.command()
@click.option("--collection", "-c", required=True, help="Collection to reset")
@click.option("--confirm", is_flag=True, help="Confirm reset")
def reset_collection(collection: str, confirm: bool):
    """Reset a collection (delete all documents)."""
    if not confirm:
        click.echo("Please add --confirm to reset the collection")
        return

    async def _reset():
        client = EmbeddingClient()
        db = ChromaDBManager(client)

        try:
            db.reset_collection(collection)
            click.echo(f"Collection '{collection}' has been reset")
        finally:
            await client.close()

    asyncio.run(_reset())


@cli.command()
@click.option("--days", "-d", default=7, help="Number of days to show")
def usage_report(days: int):
    """Show detailed usage report."""
    monitor = UsageMonitor()
    report = monitor.get_usage_report(days=days)

    click.echo(f"\n=== Usage Report ({days} days) ===\n")

    # Daily breakdown
    click.echo("Daily Usage:")
    for day_usage in report["daily_usage"]:
        if day_usage["tokens"] > 0:
            click.echo(
                f"  {day_usage['date']}: "
                f"{day_usage['tokens']} tokens, "
                f"{day_usage['requests']} requests, "
                f"${day_usage['cost']:.4f}"
            )

    # Summary
    summary = report["summary"]
    click.echo("\nSummary:")
    click.echo(f"  Total Tokens: {summary['total_tokens']}")
    click.echo(f"  Total Cost: ${summary['total_cost']:.4f}")
    click.echo(f"  Avg Tokens/Day: {summary['avg_tokens_per_day']:.0f}")
    click.echo(f"  Avg Cost/Day: ${summary['avg_cost_per_day']:.4f}")

    # Cost breakdown
    cost_breakdown = monitor.get_cost_breakdown()
    click.echo("\nCost Breakdown:")
    for operation, cost in cost_breakdown["breakdown"].items():
        click.echo(f"  {operation.capitalize()}: ${cost:.4f}")


if __name__ == "__main__":
    cli()
