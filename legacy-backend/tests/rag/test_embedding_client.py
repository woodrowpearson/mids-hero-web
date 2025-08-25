"""Tests for the Gemini embedding client."""

import pytest
import asyncio
from pathlib import Path
import json
import os

from app.rag import EmbeddingClient, EmbeddingError
from app.rag.config import rag_settings


@pytest.fixture
def embedding_client(cache_dir):
    """Create an embedding client for testing."""
    # Force offline mode for testing
    original_api_key = rag_settings.gemini_api_key
    rag_settings.gemini_api_key = None
    
    client = EmbeddingClient()
    
    yield client
    
    # Restore original settings
    rag_settings.gemini_api_key = original_api_key
    asyncio.run(client.close())


@pytest.fixture
def cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_path = tmp_path / "embeddings"
    cache_path.mkdir()
    
    original_path = rag_settings.embedding_cache_path
    rag_settings.embedding_cache_path = str(cache_path)
    
    yield cache_path
    
    rag_settings.embedding_cache_path = original_path


class TestEmbeddingClient:
    """Test embedding client functionality."""
    
    @pytest.mark.asyncio
    async def test_offline_embedding_generation(self, embedding_client):
        """Test offline embedding generation."""
        text = "Test text for embedding"
        embedding = await embedding_client.embed_text(text, use_cache=False)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 768  # Gemini embedding dimension
        assert all(isinstance(x, float) for x in embedding)
        
        # Check normalization
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 0.01  # Should be normalized
    
    @pytest.mark.asyncio
    async def test_offline_embedding_consistency(self, embedding_client):
        """Test that offline embeddings are consistent."""
        text = "Consistent text"
        
        embedding1 = await embedding_client.embed_text(text, use_cache=False)
        embedding2 = await embedding_client.embed_text(text, use_cache=False)
        
        assert embedding1 == embedding2
    
    @pytest.mark.asyncio
    async def test_embedding_cache(self, embedding_client, cache_dir):
        """Test embedding caching."""
        text = "Cached text"
        
        # First call should generate and cache
        embedding1 = await embedding_client.embed_text(text)
        
        # Check cache file exists
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) == 1
        
        # Second call should load from cache
        embedding2 = await embedding_client.embed_text(text)
        
        assert embedding1 == embedding2
    
    @pytest.mark.asyncio
    async def test_batch_embedding(self, embedding_client):
        """Test batch embedding generation."""
        texts = [
            "First text",
            "Second text",
            "Third text"
        ]
        
        embeddings = await embedding_client.embed_batch(texts, use_cache=False)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 768 for emb in embeddings)
        
        # Check that different texts produce different embeddings
        assert embeddings[0] != embeddings[1]
        assert embeddings[1] != embeddings[2]
    
    @pytest.mark.asyncio
    async def test_batch_with_cache(self, embedding_client, cache_dir):
        """Test batch processing with caching."""
        texts = ["Text A", "Text B", "Text C"]
        
        # Pre-cache one text
        await embedding_client.embed_text("Text B")
        
        # Process batch
        embeddings = await embedding_client.embed_batch(texts)
        
        assert len(embeddings) == 3
        
        # Check cache files (should have all 3 now)
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) == 3
    
    def test_embedding_dimension(self, embedding_client):
        """Test getting embedding dimension."""
        assert embedding_client.get_embedding_dimension() == 768
    
    def test_offline_mode_check(self, embedding_client):
        """Test offline mode checking."""
        assert embedding_client.is_online() is False
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, embedding_client):
        """Test handling of empty text."""
        embedding = await embedding_client.embed_text("", use_cache=False)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 768