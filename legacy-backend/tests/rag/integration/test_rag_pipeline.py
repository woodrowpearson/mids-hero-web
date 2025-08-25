"""Integration tests for RAG pipeline."""

import pytest
import asyncio
from pathlib import Path
import shutil

from app.rag import (
    EmbeddingClient,
    ChromaDBManager,
    DocumentProcessor,
    UsageMonitor,
    BatchProcessor,
    rag_settings
)


@pytest.fixture
def test_env(tmp_path):
    """Set up test environment."""
    # Save original settings
    original_chromadb_path = rag_settings.chromadb_path
    original_cache_path = rag_settings.embedding_cache_path
    original_api_key = rag_settings.gemini_api_key
    
    # Set test paths
    rag_settings.chromadb_path = str(tmp_path / "chromadb")
    rag_settings.embedding_cache_path = str(tmp_path / "cache")
    rag_settings.gemini_api_key = None  # Force offline mode
    
    yield tmp_path
    
    # Restore settings
    rag_settings.chromadb_path = original_chromadb_path
    rag_settings.embedding_cache_path = original_cache_path
    rag_settings.gemini_api_key = original_api_key


@pytest.fixture
def test_codebase(tmp_path):
    """Create a test codebase structure."""
    codebase = tmp_path / "test_project"
    codebase.mkdir()
    
    # Create Python module
    (codebase / "app").mkdir()
    (codebase / "app" / "__init__.py").write_text("")
    (codebase / "app" / "models.py").write_text('''
"""Database models for the application."""

class Power:
    """Represents a City of Heroes power."""
    
    def __init__(self, name, damage, recharge):
        self.name = name
        self.damage = damage
        self.recharge = recharge
    
    def calculate_dps(self):
        """Calculate damage per second."""
        return self.damage / self.recharge
''')
    
    (codebase / "app" / "api.py").write_text('''
"""API endpoints for power management."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/powers")
async def get_powers():
    """Get all available powers."""
    return {"powers": []}

@router.post("/powers/{power_id}/enhance")
async def enhance_power(power_id: int, enhancement_type: str):
    """Apply enhancement to a power."""
    return {"success": True}
''')
    
    # Create tests
    (codebase / "tests").mkdir()
    (codebase / "tests" / "test_models.py").write_text('''
import pytest
from app.models import Power

def test_power_dps():
    power = Power("Fire Blast", damage=100, recharge=2.0)
    assert power.calculate_dps() == 50.0
''')
    
    # Create documentation
    (codebase / "README.md").write_text('''
# Test Project

This is a test project for RAG integration testing.

## Features

- Power management system
- DPS calculations
- Enhancement system

## Installation

```bash
uv pip install -r requirements.txt
```
''')
    
    # Create config
    (codebase / "config.json").write_text('''{
    "game": {
        "name": "City of Heroes",
        "server": "Homecoming"
    },
    "api": {
        "version": "1.0"
    }
}''')
    
    return codebase


class TestRAGPipeline:
    """Test full RAG pipeline integration."""
    
    @pytest.mark.asyncio
    async def test_full_indexing_workflow(self, test_env, test_codebase):
        """Test complete indexing workflow."""
        # Initialize components
        embedding_client = EmbeddingClient()
        db_manager = ChromaDBManager(embedding_client)
        processor = DocumentProcessor()
        monitor = UsageMonitor()
        
        try:
            # Process codebase
            chunks = await processor.process_directory(
                test_codebase,
                patterns=["**/*.py", "**/*.md", "**/*.json"]
            )
            
            assert len(chunks) > 0
            
            # Index chunks
            collection_name = rag_settings.codebase_collection
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
            
            await db_manager.add_documents(
                collection_name, documents, metadatas, ids
            )
            
            # Track usage
            total_tokens = sum(chunk["token_count"] for chunk in chunks)
            monitor.track_usage(total_tokens, "indexing")
            
            # Verify indexing
            doc_count = db_manager.get_document_count(collection_name)
            assert doc_count == len(chunks)
            
            # Check usage tracking
            usage = monitor.get_current_usage()
            assert usage["tokens"] == total_tokens
            
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_search_accuracy(self, test_env, test_codebase):
        """Test search functionality and accuracy."""
        # Initialize and index
        embedding_client = EmbeddingClient()
        
        # Skip if in offline mode since semantic search won't work
        if embedding_client.offline_mode:
            await embedding_client.close()
            pytest.skip("Semantic search accuracy test requires online mode")
        db_manager = ChromaDBManager(embedding_client)
        processor = DocumentProcessor()
        
        try:
            # Index test codebase
            chunks = await processor.process_directory(test_codebase)
            
            collection_name = rag_settings.codebase_collection
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
            
            await db_manager.add_documents(
                collection_name, documents, metadatas, ids
            )
            
            # Test searches
            test_queries = [
                ("calculate DPS for powers", ["calculate_dps", "damage", "recharge"]),
                ("enhance power API endpoint", ["enhance_power", "power_id", "enhancement_type"]),
                ("City of Heroes features", ["City of Heroes", "Power management", "Enhancement"]),
            ]
            
            for query, expected_terms in test_queries:
                results = await db_manager.query(
                    collection_name,
                    [query],
                    n_results=3
                )
                
                # Check we got results
                assert len(results["documents"][0]) > 0
                
                # Check relevance - at least one result should contain expected terms
                found_relevant = False
                for doc in results["documents"][0]:
                    if any(term in doc for term in expected_terms):
                        found_relevant = True
                        break
                
                assert found_relevant, f"No relevant results for query: {query}"
                
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_offline_mode_fallback(self, test_env):
        """Test that offline mode works correctly."""
        # Ensure offline mode
        rag_settings.gemini_api_key = None
        
        embedding_client = EmbeddingClient()
        assert embedding_client.offline_mode is True
        
        try:
            # Test embedding generation
            text = "Test document for offline mode"
            embedding = await embedding_client.embed_text(text)
            
            assert len(embedding) == 768
            assert all(isinstance(x, float) for x in embedding)
            
            # Test consistency
            embedding2 = await embedding_client.embed_text(text)
            assert embedding == embedding2
            
            # Test batch processing
            texts = ["Doc 1", "Doc 2", "Doc 3"]
            embeddings = await embedding_client.embed_batch(texts)
            
            assert len(embeddings) == 3
            assert all(len(emb) == 768 for emb in embeddings)
            
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, test_env):
        """Test that caching reduces redundant API calls."""
        embedding_client = EmbeddingClient()
        
        try:
            text = "Cached document test"
            
            # First call - should generate and cache
            embedding1 = await embedding_client.embed_text(text)
            
            # Check cache file exists
            cache_dir = Path(rag_settings.embedding_cache_path)
            cache_files = list(cache_dir.glob("*.json"))
            assert len(cache_files) > 0
            
            # Second call - should load from cache
            embedding2 = await embedding_client.embed_text(text)
            
            # Should be identical
            assert embedding1 == embedding2
            
            # Test batch with mixed cached/uncached
            texts = [
                text,  # cached
                "New document 1",  # not cached
                text,  # cached
                "New document 2"  # not cached
            ]
            
            embeddings = await embedding_client.embed_batch(texts)
            
            assert len(embeddings) == 4
            assert embeddings[0] == embedding1  # From cache
            assert embeddings[2] == embedding1  # From cache
            assert embeddings[1] != embeddings[3]  # Different new docs
            
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_metadata_filtering(self, test_env, test_codebase):
        """Test querying with metadata filters."""
        embedding_client = EmbeddingClient()
        db_manager = ChromaDBManager(embedding_client)
        processor = DocumentProcessor()
        
        try:
            # Index with metadata
            chunks = await processor.process_directory(test_codebase)
            
            collection_name = rag_settings.codebase_collection
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
            
            await db_manager.add_documents(
                collection_name, documents, metadatas, ids
            )
            
            # Query Python files only
            results = await db_manager.query(
                collection_name,
                ["class implementation"],
                n_results=10,
                where={"file_type": ".py"}
            )
            
            # All results should be Python files
            for metadata in results["metadatas"][0]:
                assert metadata["file_type"] == ".py"
            
            # Query specific file
            results = await db_manager.query(
                collection_name,
                ["any content"],
                n_results=10,
                where={"file_name": "models.py"}
            )
            
            # All results should be from models.py
            for metadata in results["metadatas"][0]:
                assert metadata["file_name"] == "models.py"
                
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_batch_processing_integration(self, test_env):
        """Test batch processing with full pipeline."""
        embedding_client = EmbeddingClient()
        batch_processor = BatchProcessor(embedding_client)
        monitor = UsageMonitor()
        
        try:
            # Add documents to batch
            docs = [
                ("Technical documentation about powers", {"type": "docs"}),
                ("API endpoint implementation", {"type": "code"}),
                ("Game mechanics explanation", {"type": "guide"}),
            ]
            
            tracking_ids = []
            for text, metadata in docs:
                tracking_id = batch_processor.add_to_batch(text, metadata)
                tracking_ids.append(tracking_id)
            
            # Process batch
            result = await batch_processor.process_batch()
            
            assert result["processed"] == 3
            assert result["cost_savings"] > 0
            
            # Get embeddings
            embeddings = []
            for tracking_id in tracking_ids:
                result_data = batch_processor.get_result(tracking_id)
                assert result_data is not None
                embeddings.append(result_data["embedding"])
            
            # Use embeddings with ChromaDB
            db_manager = ChromaDBManager(embedding_client)
            collection_name = rag_settings.codebase_collection
            
            await db_manager.add_documents(
                collection_name,
                [doc[0] for doc in docs],
                [doc[1] for doc in docs],
                [f"batch_doc_{i}" for i in range(len(docs))]
            )
            
            # Track usage
            total_tokens = sum(len(doc[0].split()) for doc in docs) * 2
            monitor.track_usage(total_tokens, "batch_indexing")
            
            # Verify
            count = db_manager.get_document_count(collection_name)
            assert count >= 3
            
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_indexing(self, test_env, test_codebase):
        """Test concurrent document indexing."""
        embedding_client = EmbeddingClient()
        db_manager = ChromaDBManager(embedding_client)
        processor = DocumentProcessor()
        
        try:
            # Process multiple file types concurrently
            tasks = []
            
            for pattern in ["**/*.py", "**/*.md", "**/*.json"]:
                task = processor.process_directory(
                    test_codebase,
                    patterns=[pattern]
                )
                tasks.append(task)
            
            # Process concurrently
            all_chunks = await asyncio.gather(*tasks)
            
            # Flatten chunks
            chunks = []
            for chunk_list in all_chunks:
                chunks.extend(chunk_list)
            
            # Index all chunks
            if chunks:
                collection_name = rag_settings.codebase_collection
                documents = [chunk["text"] for chunk in chunks]
                metadatas = [chunk["metadata"] for chunk in chunks]
                ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
                
                await db_manager.add_documents(
                    collection_name, documents, metadatas, ids
                )
                
                # Verify
                count = db_manager.get_document_count(collection_name)
                assert count == len(chunks)
                
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, test_env):
        """Test error recovery in pipeline."""
        embedding_client = EmbeddingClient()
        db_manager = ChromaDBManager(embedding_client)
        
        try:
            collection_name = "test_error_collection"
            db_manager.create_collection(collection_name)
            
            # Try to add documents with mismatched lengths (should fail)
            with pytest.raises(Exception):
                await db_manager.add_documents(
                    collection_name,
                    ["Doc 1", "Doc 2"],
                    [{"meta": 1}],  # Wrong length
                    ["id1", "id2"]
                )
            
            # Collection should still be usable
            await db_manager.add_documents(
                collection_name,
                ["Doc 1"],
                [{"meta": 1}],
                ["id1"]
            )
            
            assert db_manager.get_document_count(collection_name) == 1
            
            # Clean up
            db_manager.delete_collection(collection_name)
            
        finally:
            await embedding_client.close()
    
    @pytest.mark.asyncio
    async def test_usage_limits_integration(self, test_env):
        """Test usage limit enforcement in full pipeline."""
        embedding_client = EmbeddingClient()
        monitor = UsageMonitor()
        
        # Set very low limit
        monitor.daily_limit = 100
        
        try:
            # Generate embeddings until limit
            texts = ["Document " + str(i) for i in range(10)]
            
            with pytest.raises(Exception):  # Should hit limit
                for text in texts:
                    await embedding_client.embed_text(text)
                    monitor.track_usage(50, "embedding")  # 50 tokens each
                    
        finally:
            await embedding_client.close()