"""Environment-backed interface configuration."""

import json
from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "L1 Support Bot"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    qdrant_url: str = "http://localhost:6333"
    file_storage_path: str = "./data/documents"
    embedding_base_url: str = "http://localhost:11434/v1"
    embedding_model: str = "nomic-embed-text"
    embedding_model_version: str = "dev"
    embedding_dimensions: int = 768
    embedding_batch_size: int = 32
    embedding_timeout_seconds: int = 30
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "phi3.5"
    ollama_timeout_seconds: int = 120
    log_level: str = "INFO"
    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    max_request_body_bytes: int = 10 * 1024 * 1024
    max_document_size_bytes: int = 10 * 1024 * 1024
    session_ttl_minutes: int = 30
    session_history_window_turns: int = 10
    session_history_token_budget: int = 2_000

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def validate_runtime_limits(self) -> "Settings":
        if self.max_request_body_bytes < 1:
            raise ValueError("Maximum request body size must be positive")
        if self.max_document_size_bytes < 1:
            raise ValueError("Maximum document size must be positive")
        if self.session_ttl_minutes < 1:
            raise ValueError("Session TTL must be positive")
        if self.session_history_window_turns < 1 or self.session_history_token_budget < 1:
            raise ValueError("Session history limits must be positive")
        if self.embedding_dimensions < 1 or self.embedding_batch_size < 1:
            raise ValueError("Embedding dimensions and batch size must be positive")
        if self.embedding_timeout_seconds < 1:
            raise ValueError("Embedding timeout must be positive")
        if self.ollama_timeout_seconds < 1:
            raise ValueError("Ollama timeout must be positive")
        if not self.cors_allowed_origins:
            raise ValueError("At least one CORS origin is required")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()