"""RAG configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class RAGSettings(BaseSettings):
    """Settings for RAG system."""

    # Gemini API
    gemini_api_key: str | None = Field(None, env="GEMINI_API_KEY")
    google_cloud_project: str | None = Field(None, env="GOOGLE_CLOUD_PROJECT")

    # ChromaDB
    chromadb_path: str = Field(".claude/rag/db", env="CHROMADB_PATH")

    # Caching
    embedding_cache_path: str = Field(".claude/rag/cache", env="EMBEDDING_CACHE_PATH")
    redis_url: str | None = Field(None, env="REDIS_URL")

    # Batch Processing
    batch_processing_enabled: bool = Field(True, env="BATCH_PROCESSING_ENABLED")
    batch_size: int = Field(1000, env="RAG_BATCH_SIZE")

    # Offline Mode
    offline_mode_fallback: bool = Field(True, env="OFFLINE_MODE_FALLBACK")

    # Usage Limits
    daily_token_limit: int = Field(1_000_000, env="RAG_DAILY_TOKEN_LIMIT")
    alert_threshold: float = Field(0.8, env="RAG_ALERT_THRESHOLD")

    # Model Configuration
    embedding_model: str = Field("models/embedding-001", env="EMBEDDING_MODEL")
    embedding_task_type: str = Field("RETRIEVAL_DOCUMENT", env="EMBEDDING_TASK_TYPE")

    # Collection Names
    codebase_collection: str = Field("mids_hero_codebase", env="CODEBASE_COLLECTION")
    midsreborn_collection: str = Field("midsreborn_docs", env="MIDSREBORN_COLLECTION")
    game_data_collection: str = Field("game_data", env="GAME_DATA_COLLECTION")

    class Config:
        env_file = ".env"
        case_sensitive = False


rag_settings = RAGSettings()
