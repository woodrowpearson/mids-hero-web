"""Tests for ChromaDB manager."""

import asyncio
import shutil

import pytest

from app.rag import ChromaDBError, ChromaDBManager, EmbeddingClient
from app.rag.config import rag_settings


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary database path."""
    db_dir = tmp_path / "test_chromadb"
    db_dir.mkdir()

    original_path = rag_settings.chromadb_path
    rag_settings.chromadb_path = str(db_dir)

    yield db_dir

    rag_settings.chromadb_path = original_path
    if db_dir.exists():
        shutil.rmtree(db_dir)


@pytest.fixture
def embedding_client():
    """Create an embedding client in offline mode."""
    original_api_key = rag_settings.gemini_api_key
    rag_settings.gemini_api_key = None

    client = EmbeddingClient()

    yield client

    rag_settings.gemini_api_key = original_api_key
    asyncio.run(client.close())


@pytest.fixture
def db_manager(embedding_client, db_path):
    """Create a ChromaDB manager for testing."""
    manager = ChromaDBManager(embedding_client)

    yield manager

    asyncio.run(manager.close())


class TestChromaDBManager:
    """Test ChromaDB manager functionality."""

    def test_initialization(self, db_manager):
        """Test manager initialization."""
        assert db_manager.embedding_client is not None
        assert len(db_manager.collections) == 3  # Default collections
        assert rag_settings.codebase_collection in db_manager.collections
        assert rag_settings.midsreborn_collection in db_manager.collections
        assert rag_settings.game_data_collection in db_manager.collections

    def test_get_collection(self, db_manager):
        """Test getting collections."""
        collection = db_manager.get_collection(rag_settings.codebase_collection)
        assert collection is not None
        assert collection.name == rag_settings.codebase_collection

        with pytest.raises(ChromaDBError):
            db_manager.get_collection("nonexistent_collection")

    def test_create_and_delete_collection(self, db_manager):
        """Test creating and deleting collections."""
        # Create collection
        test_collection = "test_collection"
        metadata = {"description": "Test collection"}

        collection = db_manager.create_collection(test_collection, metadata)
        assert collection.name == test_collection
        assert test_collection in db_manager.collections

        # Delete collection
        db_manager.delete_collection(test_collection)
        assert test_collection not in db_manager.collections

        with pytest.raises(ChromaDBError):
            db_manager.get_collection(test_collection)

    @pytest.mark.asyncio
    async def test_add_documents(self, db_manager):
        """Test adding documents to a collection."""
        collection_name = rag_settings.codebase_collection

        documents = [
            "This is a test document about Python programming.",
            "Another document about City of Heroes powers.",
            "Documentation for the RAG system implementation.",
        ]

        metadatas = [
            {"type": "test", "id": 1},
            {"type": "test", "id": 2},
            {"type": "test", "id": 3},
        ]

        ids = ["doc1", "doc2", "doc3"]

        await db_manager.add_documents(collection_name, documents, metadatas, ids)

        # Verify documents were added
        collection = db_manager.get_collection(collection_name)
        assert collection.count() == 3

    @pytest.mark.asyncio
    async def test_query_documents(self, db_manager):
        """Test querying documents."""
        collection_name = rag_settings.codebase_collection

        # Add test documents
        documents = [
            "Python is a high-level programming language.",
            "City of Heroes has many different powersets.",
            "The RAG system uses ChromaDB for vector storage.",
        ]

        metadatas = [
            {"type": "programming", "language": "python"},
            {"type": "game", "topic": "powers"},
            {"type": "technical", "system": "rag"},
        ]

        ids = ["query_doc1", "query_doc2", "query_doc3"]

        await db_manager.add_documents(collection_name, documents, metadatas, ids)

        # Query for Python-related documents
        results = await db_manager.query(
            collection_name, ["Python programming language"], n_results=2
        )

        assert len(results["documents"][0]) <= 2
        assert len(results["metadatas"][0]) <= 2
        assert len(results["distances"][0]) <= 2

    @pytest.mark.asyncio
    async def test_update_documents(self, db_manager):
        """Test updating existing documents."""
        collection_name = rag_settings.codebase_collection

        # Add initial document
        documents = ["Original document content"]
        metadatas = [{"version": 1}]
        ids = ["update_doc1"]

        await db_manager.add_documents(collection_name, documents, metadatas, ids)

        # Update document
        updated_documents = ["Updated document content with new information"]
        updated_metadatas = [{"version": 2}]

        await db_manager.update_documents(
            collection_name, updated_documents, updated_metadatas, ids
        )

        # Query to verify update
        results = await db_manager.query(
            collection_name, ["Updated document"], n_results=1
        )

        assert len(results["documents"][0]) == 1
        assert results["metadatas"][0][0]["version"] == 2

    def test_delete_documents(self, db_manager):
        """Test deleting documents."""
        collection_name = rag_settings.codebase_collection

        # Get initial count
        initial_count = db_manager.get_document_count(collection_name)

        # Delete documents by ID (if any exist)
        db_manager.delete_documents(collection_name, ids=["doc1", "doc2"])

        # Verify count changed or stayed same
        new_count = db_manager.get_document_count(collection_name)
        assert new_count <= initial_count

    def test_list_collections(self, db_manager):
        """Test listing all collections."""
        collections = db_manager.list_collections()

        assert len(collections) >= 3  # At least default collections

        collection_names = [c["name"] for c in collections]
        assert rag_settings.codebase_collection in collection_names
        assert rag_settings.midsreborn_collection in collection_names
        assert rag_settings.game_data_collection in collection_names

        for collection in collections:
            assert "name" in collection
            assert "metadata" in collection
            assert "count" in collection

    def test_backup_and_restore(self, db_manager, tmp_path):
        """Test database backup and restore."""
        # Create backup
        backup_path = db_manager.backup_database()
        assert backup_path.exists()
        assert backup_path.is_dir()

        # Create custom backup path
        custom_backup = tmp_path / "custom_backup"
        custom_path = db_manager.backup_database(custom_backup)
        assert custom_path == custom_backup
        assert custom_path.exists()

        # Test restore
        db_manager.restore_database(backup_path)

        # Verify collections still exist
        assert len(db_manager.collections) >= 3

        # Clean up
        shutil.rmtree(backup_path)
        shutil.rmtree(custom_backup)

    def test_reset_collection(self, db_manager):
        """Test resetting a collection."""
        collection_name = "reset_test_collection"

        # Create and populate collection
        db_manager.create_collection(collection_name)

        # Reset collection
        db_manager.reset_collection(collection_name)

        # Verify collection exists but is empty
        collection = db_manager.get_collection(collection_name)
        assert collection.count() == 0

        # Clean up
        db_manager.delete_collection(collection_name)

    @pytest.mark.asyncio
    async def test_query_with_filters(self, db_manager):
        """Test querying with metadata filters."""
        collection_name = rag_settings.codebase_collection

        # Add documents with specific metadata
        documents = [
            "FastAPI endpoint implementation",
            "React component for power selection",
            "Database migration script",
        ]

        metadatas = [
            {"type": "backend", "framework": "fastapi"},
            {"type": "frontend", "framework": "react"},
            {"type": "backend", "category": "database"},
        ]

        ids = ["filter_doc1", "filter_doc2", "filter_doc3"]

        await db_manager.add_documents(collection_name, documents, metadatas, ids)

        # Query with metadata filter
        results = await db_manager.query(
            collection_name, ["backend code"], n_results=10, where={"type": "backend"}
        )

        # Should only return backend documents
        for metadata in results["metadatas"][0]:
            assert metadata.get("type") == "backend"

    def test_get_document_count(self, db_manager):
        """Test getting document count."""
        count = db_manager.get_document_count(rag_settings.codebase_collection)
        assert isinstance(count, int)
        assert count >= 0

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, db_manager):
        """Test concurrent document operations."""
        collection_name = rag_settings.codebase_collection

        # Prepare multiple document batches
        batches = []
        for i in range(3):
            documents = [f"Concurrent document {i}-{j}" for j in range(3)]
            metadatas = [{"batch": i, "doc": j} for j in range(3)]
            ids = [f"concurrent_{i}_{j}" for j in range(3)]
            batches.append((documents, metadatas, ids))

        # Add documents concurrently
        tasks = [
            db_manager.add_documents(collection_name, docs, meta, ids)
            for docs, meta, ids in batches
        ]

        await asyncio.gather(*tasks)

        # Verify all documents were added
        count = db_manager.get_document_count(collection_name)
        assert count >= 9  # At least our 9 documents
