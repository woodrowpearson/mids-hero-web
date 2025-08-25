"""ChromaDB vector database manager."""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .client import EmbeddingClient
from .config import rag_settings
from .exceptions import ChromaDBError

logger = logging.getLogger(__name__)


class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Custom embedding function using Gemini API."""

    def __init__(self, client: EmbeddingClient):
        self.client = client

    def __call__(self, input: list[str]) -> list[list[float]]:
        """Generate embeddings for input texts."""
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            embeddings = loop.run_until_complete(self.client.embed_batch(input))
            return embeddings
        finally:
            loop.close()


class ChromaDBManager:
    """Manager for ChromaDB vector database operations."""

    def __init__(self, embedding_client: EmbeddingClient | None = None):
        """Initialize ChromaDB manager."""
        self.db_path = Path(rag_settings.chromadb_path)
        self.db_path.mkdir(parents=True, exist_ok=True)

        # Initialize embedding client
        self.embedding_client = embedding_client or EmbeddingClient()
        self.embedding_function = GeminiEmbeddingFunction(self.embedding_client)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Collection references
        self.collections: dict[str, chromadb.Collection] = {}

        # Initialize default collections
        self._init_collections()

    def _init_collections(self) -> None:
        """Initialize default collections."""
        collection_configs = [
            (
                rag_settings.codebase_collection,
                {
                    "description": "Mids Hero Web codebase documentation",
                    "indexed_at": datetime.now().isoformat(),
                },
            ),
            (
                rag_settings.midsreborn_collection,
                {
                    "description": "MidsReborn documentation and code",
                    "indexed_at": datetime.now().isoformat(),
                },
            ),
            (
                rag_settings.game_data_collection,
                {
                    "description": "City of Heroes game mechanics and data",
                    "indexed_at": datetime.now().isoformat(),
                },
            ),
        ]

        for name, metadata in collection_configs:
            try:
                collection = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=self.embedding_function,
                    metadata=metadata,
                )
                self.collections[name] = collection
                logger.info(f"Initialized collection: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize collection {name}: {e}")

    def get_collection(self, name: str) -> chromadb.Collection:
        """Get a collection by name."""
        if name not in self.collections:
            raise ChromaDBError(f"Collection '{name}' not found")
        return self.collections[name]

    def create_collection(
        self, name: str, metadata: dict[str, Any] | None = None
    ) -> chromadb.Collection:
        """Create a new collection."""
        try:
            # Ensure metadata is not empty
            if not metadata:
                metadata = {"created_at": datetime.now().isoformat()}
            
            collection = self.client.create_collection(
                name=name,
                embedding_function=self.embedding_function,
                metadata=metadata,
            )
            self.collections[name] = collection
            logger.info(f"Created collection: {name}")
            return collection
        except Exception as e:
            raise ChromaDBError(f"Failed to create collection '{name}': {e}")

    def delete_collection(self, name: str) -> None:
        """Delete a collection."""
        try:
            self.client.delete_collection(name=name)
            if name in self.collections:
                del self.collections[name]
            logger.info(f"Deleted collection: {name}")
        except Exception as e:
            raise ChromaDBError(f"Failed to delete collection '{name}': {e}")

    def _sanitize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Sanitize metadata for ChromaDB compatibility."""
        sanitized = {}
        for key, value in metadata.items():
            if value is None or isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                # Convert lists to comma-separated strings
                sanitized[key] = ", ".join(str(v) for v in value)
            elif isinstance(value, dict):
                # Convert dicts to JSON strings
                sanitized[key] = json.dumps(value)
            else:
                # Convert other types to strings
                sanitized[key] = str(value)
        return sanitized

    async def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Add documents to a collection."""
        collection = self.get_collection(collection_name)

        try:
            # Generate embeddings
            embeddings = await self.embedding_client.embed_batch(documents)

            # Sanitize metadata for ChromaDB
            sanitized_metadatas = [self._sanitize_metadata(m) for m in metadatas]

            # Add to collection
            collection.add(
                documents=documents, embeddings=embeddings, metadatas=sanitized_metadatas, ids=ids
            )

            logger.info(f"Added {len(documents)} documents to '{collection_name}'")
        except Exception as e:
            raise ChromaDBError(f"Failed to add documents: {e}")

    async def update_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Update existing documents in a collection."""
        collection = self.get_collection(collection_name)

        try:
            # Generate embeddings
            embeddings = await self.embedding_client.embed_batch(documents)

            # Sanitize metadata for ChromaDB
            sanitized_metadatas = [self._sanitize_metadata(m) for m in metadatas]

            # Update in collection
            collection.update(
                documents=documents, embeddings=embeddings, metadatas=sanitized_metadatas, ids=ids
            )

            logger.info(f"Updated {len(documents)} documents in '{collection_name}'")
        except Exception as e:
            raise ChromaDBError(f"Failed to update documents: {e}")

    async def query(
        self,
        collection_name: str,
        query_texts: list[str],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
        where_document: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Query a collection for similar documents."""
        collection = self.get_collection(collection_name)

        try:
            # Generate query embeddings
            query_embeddings = await self.embedding_client.embed_batch(query_texts)

            # Query collection
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
            )

            return results
        except Exception as e:
            raise ChromaDBError(f"Failed to query collection: {e}")

    def delete_documents(
        self,
        collection_name: str,
        ids: list[str] | None = None,
        where: dict[str, Any] | None = None,
    ) -> None:
        """Delete documents from a collection."""
        collection = self.get_collection(collection_name)

        try:
            collection.delete(ids=ids, where=where)
            logger.info(f"Deleted documents from '{collection_name}'")
        except Exception as e:
            raise ChromaDBError(f"Failed to delete documents: {e}")

    def get_document_count(self, collection_name: str) -> int:
        """Get the number of documents in a collection."""
        collection = self.get_collection(collection_name)
        return collection.count()

    def list_collections(self) -> list[dict[str, Any]]:
        """List all collections."""
        collections_info = []
        for collection in self.client.list_collections():
            info = {
                "name": collection.name,
                "metadata": collection.metadata,
                "count": collection.count(),
            }
            collections_info.append(info)
        return collections_info

    def backup_database(self, backup_path: Path | None = None) -> Path:
        """Backup the entire database."""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.db_path.parent / f"chromadb_backup_{timestamp}"

        try:
            shutil.copytree(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            raise ChromaDBError(f"Failed to backup database: {e}")

    def restore_database(self, backup_path: Path) -> None:
        """Restore database from backup."""
        if not backup_path.exists():
            raise ChromaDBError(f"Backup path does not exist: {backup_path}")

        try:
            # Remove current database
            if self.db_path.exists():
                shutil.rmtree(self.db_path)

            # Restore from backup
            shutil.copytree(backup_path, self.db_path)

            # Reinitialize client and collections
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False, allow_reset=True),
            )
            self._init_collections()

            logger.info(f"Database restored from: {backup_path}")
        except Exception as e:
            raise ChromaDBError(f"Failed to restore database: {e}")

    def reset_collection(self, collection_name: str) -> None:
        """Reset a collection (delete all documents)."""
        try:
            self.delete_collection(collection_name)
            metadata = {
                "description": f"Reset collection: {collection_name}",
                "reset_at": datetime.now().isoformat(),
            }
            self.create_collection(collection_name, metadata)
            logger.info(f"Reset collection: {collection_name}")
        except Exception as e:
            raise ChromaDBError(f"Failed to reset collection: {e}")

    async def close(self) -> None:
        """Clean up resources."""
        await self.embedding_client.close()
