"""Gemini embedding client with offline fallback."""

import asyncio
import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import google.generativeai as genai
import numpy as np
from google.api_core import exceptions as google_exceptions

from .config import rag_settings
from .exceptions import EmbeddingError

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client for generating embeddings using Gemini API with offline fallback."""

    def __init__(self):
        """Initialize the embedding client."""
        self.api_key = rag_settings.gemini_api_key
        self.cache_dir = Path(rag_settings.embedding_cache_path)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.offline_mode = False
        self.model_name = rag_settings.embedding_model
        self.task_type = rag_settings.embedding_task_type

        # Thread pool for CPU-bound operations
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize Gemini if API key is available
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self._test_connection()
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}")
                if rag_settings.offline_mode_fallback:
                    self.offline_mode = True
                else:
                    raise EmbeddingError(f"Failed to initialize Gemini API: {e}")
        else:
            logger.info("No Gemini API key provided, running in offline mode")
            self.offline_mode = True

    def _test_connection(self) -> None:
        """Test the connection to Gemini API."""
        try:
            # Simple test embedding
            genai.embed_content(
                model=self.model_name, content="test", task_type=self.task_type
            )
            logger.info("Gemini API connection successful")
        except Exception as e:
            raise EmbeddingError(f"Gemini API connection test failed: {e}")

    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for the given text."""
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        return f"{self.model_name}_{self.task_type}_{text_hash}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the cache file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"

    def _load_from_cache(self, text: str) -> list[float] | None:
        """Load embedding from cache if available."""
        cache_key = self._get_cache_key(text)
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            try:
                with open(cache_path) as f:
                    data = json.load(f)
                    return data["embedding"]
            except Exception as e:
                logger.warning(f"Failed to load from cache: {e}")

        return None

    def _save_to_cache(self, text: str, embedding: list[float]) -> None:
        """Save embedding to cache."""
        cache_key = self._get_cache_key(text)
        cache_path = self._get_cache_path(cache_key)

        try:
            data = {
                "text": text,
                "embedding": embedding,
                "model": self.model_name,
                "task_type": self.task_type,
            }
            with open(cache_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Failed to save to cache: {e}")

    def _generate_offline_embedding(self, text: str) -> list[float]:
        """Generate a deterministic embedding for offline mode."""
        # Use a simple hash-based approach for offline embeddings
        # This maintains consistency across runs
        text_bytes = text.encode("utf-8")
        hash_digest = hashlib.sha512(text_bytes).digest()

        # Convert to normalized float array (768 dimensions like Gemini)
        embedding = []
        for i in range(0, len(hash_digest), 2):
            if i + 1 < len(hash_digest):
                value = (hash_digest[i] + hash_digest[i + 1]) / 510.0 - 0.5
                embedding.append(value)

        # Pad or truncate to 768 dimensions
        target_dim = 768
        if len(embedding) < target_dim:
            # Repeat pattern to fill
            while len(embedding) < target_dim:
                embedding.extend(
                    embedding[: min(len(embedding), target_dim - len(embedding))]
                )
        else:
            embedding = embedding[:target_dim]

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = (np.array(embedding) / norm).tolist()

        return embedding

    async def embed_text(self, text: str, use_cache: bool = True) -> list[float]:
        """Generate embedding for a single text."""
        # Check cache first
        if use_cache:
            cached = self._load_from_cache(text)
            if cached is not None:
                return cached

        # Generate embedding
        if self.offline_mode:
            embedding = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._generate_offline_embedding, text
            )
        else:
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    genai.embed_content,
                    self.model_name,
                    text,
                    self.task_type,
                )
                embedding = result["embedding"]
            except google_exceptions.ResourceExhausted:
                raise EmbeddingError("Gemini API quota exceeded")
            except Exception as e:
                if rag_settings.offline_mode_fallback:
                    logger.warning(f"Gemini API error, falling back to offline: {e}")
                    embedding = await asyncio.get_event_loop().run_in_executor(
                        self.executor, self._generate_offline_embedding, text
                    )
                else:
                    raise EmbeddingError(f"Failed to generate embedding: {e}")

        # Save to cache
        if use_cache:
            self._save_to_cache(text, embedding)

        return embedding

    async def embed_batch(
        self, texts: list[str], use_cache: bool = True, show_progress: bool = True
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []

        # Separate cached and uncached texts
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            if use_cache:
                cached = self._load_from_cache(text)
                if cached is not None:
                    embeddings.append(cached)
                    continue

            uncached_texts.append(text)
            uncached_indices.append(i)
            embeddings.append(None)  # Placeholder

        # Process uncached texts
        if uncached_texts:
            if self.offline_mode:
                # Generate offline embeddings in parallel
                tasks = [
                    asyncio.get_event_loop().run_in_executor(
                        self.executor, self._generate_offline_embedding, text
                    )
                    for text in uncached_texts
                ]
                new_embeddings = await asyncio.gather(*tasks)
            else:
                # Use Gemini batch API if available
                try:
                    # For now, process individually (batch API requires Vertex AI setup)
                    tasks = [
                        self.embed_text(text, use_cache=False)
                        for text in uncached_texts
                    ]
                    new_embeddings = await asyncio.gather(*tasks)
                except Exception as e:
                    if rag_settings.offline_mode_fallback:
                        logger.warning(f"Batch embedding failed, using offline: {e}")
                        tasks = [
                            asyncio.get_event_loop().run_in_executor(
                                self.executor, self._generate_offline_embedding, text
                            )
                            for text in uncached_texts
                        ]
                        new_embeddings = await asyncio.gather(*tasks)
                    else:
                        raise

            # Save to cache and update results
            for i, (text, embedding) in enumerate(
                zip(uncached_texts, new_embeddings, strict=False)
            ):
                if use_cache:
                    self._save_to_cache(text, embedding)
                embeddings[uncached_indices[i]] = embedding

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return 768  # Gemini embedding dimension

    def is_online(self) -> bool:
        """Check if the client is in online mode."""
        return not self.offline_mode

    async def close(self):
        """Clean up resources."""
        self.executor.shutdown(wait=True)
