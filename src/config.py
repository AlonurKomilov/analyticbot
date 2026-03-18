"""Analyticbot v2 — Configuration"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-to-a-random-secret")

    # Analysis
    MAX_POSTS: int = int(os.getenv("MAX_POSTS_PER_ANALYSIS", "500"))
    CACHE_TTL_HOURS: int = int(os.getenv("ANALYSIS_CACHE_TTL_HOURS", "24"))


settings = Settings()
