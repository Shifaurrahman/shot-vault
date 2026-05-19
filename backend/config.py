from pydantic_settings import BaseSettings
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "ShotVault"
    app_version: str = "0.1.0"
    debug: bool = True

    # Embedding
    embedding_model: str = "Qwen/Qwen3-VL-Embedding-2B"
    embedding_device: str = "cpu"
    embedding_dim: int = 2048

    # Vector DB
    vector_db: Literal["chromadb", "qdrant", "pgvector"] = "chromadb"
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection: str = "shotvault"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "shotvault"

    # Storage
    storage_backend: Literal["local", "s3"] = "local"
    local_storage_dir: str = "./data/uploads"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_bucket_name: str = ""
    aws_region: str = "ap-southeast-1"

    # LLM — Claude (answer generation)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-haiku-20241022"
    anthropic_max_tokens: int = 512

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()