"""Application configuration settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google API
    google_api_key: str = ""
    google_cloud_project: str = ""

    # Database
    database_url: str = "postgresql://root:112233@localhost:5433/doc-ai"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Processing
    chunk_size: int = 400
    chunk_overlap: int = 50
    top_k_candidates: int = 5
    similarity_threshold: float = 0.7

    # Models
    embedding_model: str = "gemini-embedding-001"
    llm_model: str = "gemini-2.5-flash-lite"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
