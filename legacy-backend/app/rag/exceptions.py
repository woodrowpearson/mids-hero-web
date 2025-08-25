"""RAG module exceptions."""


class RAGError(Exception):
    """Base exception for RAG module."""

    pass


class EmbeddingError(RAGError):
    """Error generating embeddings."""

    pass


class OfflineModeError(RAGError):
    """Error when operation requires online mode."""

    pass


class ChromaDBError(RAGError):
    """Error with ChromaDB operations."""

    pass


class DocumentProcessingError(RAGError):
    """Error processing documents."""

    pass


class UsageLimitError(RAGError):
    """Error when usage limits are exceeded."""

    pass
