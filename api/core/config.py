"""
Configuration for JSON-native API
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """API configuration using Pydantic Settings"""
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Mids Hero Web"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Data Path
    game_data_path: Path = Path(__file__).parent.parent.parent / "external/city_of_data/raw_data_homecoming-20250617_6916"
    
    # Caching
    cache_ttl: int = 3600  # 1 hour
    max_cache_size: int = 128  # Maximum cached items
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()