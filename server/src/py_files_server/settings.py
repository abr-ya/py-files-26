"""Environment-backed configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (optional `.env`)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(default="sqlite:///./var/py_files.db")
    storage_root: Path = Field(default=Path("./var/storage"))
    jwt_secret: str = Field(default="change-me-dev-only-unsecure")  # noqa: S105
    allow_self_registration: bool = Field(default=True)
    retention_days: int = Field(default=30)
    max_upload_bytes: int = Field(default=1_000_000_000)
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 24)
    ttl_purge_interval_seconds: int = Field(default=3600)


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
