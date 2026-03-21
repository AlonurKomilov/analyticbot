"""Analyticbot v2 — Configuration"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_DEFAULT_SECRET = "change-this-to-a-random-secret"


class Settings:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")  # auto-detected at startup if empty

    # Telethon
    API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    PHONE: str = os.getenv("TELEGRAM_PHONE", "")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:changeme@localhost:5432/analyticbot_v2",
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_SECRET)
    API_KEY: str = os.getenv("API_KEY", "")  # required for web API access
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

    # Bot admin (receives startup/shutdown notifications)
    ADMIN_ID: int = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

    # Analysis
    MAX_POSTS: int = int(os.getenv("MAX_POSTS_PER_ANALYSIS", "500"))
    CACHE_TTL_HOURS: int = int(os.getenv("ANALYSIS_CACHE_TTL_HOURS", "24"))
    ANALYSIS_TIMEOUT: int = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "120"))

    def validate(self) -> None:
        """Validate critical settings on startup."""
        if self.SECRET_KEY == _DEFAULT_SECRET:
            logger.warning(
                "SECRET_KEY is using the default value! Set a strong random value in .env"
            )
        if not self.API_KEY:
            logger.warning("API_KEY is not set — web API endpoints are unprotected")


settings = Settings()
settings.validate()
