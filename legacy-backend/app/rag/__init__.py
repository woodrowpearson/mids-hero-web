"""RAG (Retrieval-Augmented Generation) module for Claude Code integration.

This module provides:
- Gemini embeddings with offline fallback
- ChromaDB vector storage
- Multi-format document processing
- Cost-optimized batch processing
- Usage monitoring and alerts
"""

from .batch_processor import BatchProcessor
from .client import EmbeddingClient
from .config import rag_settings
from .database import ChromaDBManager
from .exceptions import (
    ChromaDBError,
    DocumentProcessingError,
    EmbeddingError,
    OfflineModeError,
    RAGError,
    UsageLimitError,
)
from .monitor import UsageMonitor
from .processor import DocumentProcessor

__all__ = [
    "EmbeddingClient",
    "ChromaDBManager",
    "DocumentProcessor",
    "UsageMonitor",
    "BatchProcessor",
    "rag_settings",
    "RAGError",
    "EmbeddingError",
    "OfflineModeError",
    "ChromaDBError",
    "DocumentProcessingError",
    "UsageLimitError",
]
