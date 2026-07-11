"""Application configuration.

Loads settings from environment variables and the .env file.
All configuration consumed by the application must be defined here.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings.

    Values are read from environment variables first, then from the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ─── Application ────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Construction Site Management System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ─── Database ───────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:password@localhost:5432/csms_db"
    )

    # ─── Security ───────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── CORS ───────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
