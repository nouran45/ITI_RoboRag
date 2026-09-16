from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Application
    app_name: str = "RoboRAG API"
    app_version: str = "1.0.0"

    # RAG
    top_k: int = 4
    ollama_model: str = "llama3.2:latest"
    max_retrieval_distance: float = 0.65

    # Persisted knowledge base
    vector_store_path: Path = BASE_DIR / "data" / "vector_store"
    rag_config_path: Path = BASE_DIR / "data" / "rag_config.json"
    max_retrieval_distance: float = 0.65
    # Frontend / CORS
    cors_origins: str = "http://localhost:8501"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()