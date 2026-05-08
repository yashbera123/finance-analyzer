"""
Application Configuration
=========================
Centralized, validated settings loaded from environment variables.
Uses pydantic-settings so misconfigurations fail fast at startup.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — populated from .env / environment."""

    # ── App ───────────────────────────────────────────────────────────────
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS origins from a comma-separated environment value."""
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    # ── Database (SQLite default for local dev; set postgresql+asyncpg://... for prod)
    DATABASE_URL: str = "sqlite+aiosqlite:///./finance_analyzer.db"

    # ── AI Providers ──────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # ── Redis (optional) ──────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
