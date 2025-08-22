from enum import Enum

from pydantic import AnyHttpUrl, RedisDsn, SecretStr
from pydantic_settings import BaseSettings


class LogLevel(str, Enum):
    """Supported log levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Supported log formats"""

    TEXT = "text"
    JSON = "json"


class Settings(BaseSettings):
    """
    Bot settings with enhanced validation and monitoring configuration.
    Pydantic automatically reads them from environment variables or a .env file.
    It also validates the data types.
    """

    # Bot token is stored as a SecretStr to prevent accidental logging
    BOT_TOKEN: SecretStr

    # --- PostgreSQL Settings ---
    # These variables are used by docker-compose.yml,
    # but we define them here so Pydantic knows about them too.
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # Main connection URL for Python application (supports SQLite and PostgreSQL)
    DATABASE_URL: str

    # Redis connection URL
    REDIS_URL: RedisDsn

    # Telegram Web App (Frontend) URL
    TWA_HOST_URL: AnyHttpUrl

    # Sentry DSN for error tracking
    SENTRY_DSN: str | None = None

    # Plan limit enforcement
    ENFORCE_PLAN_LIMITS: bool = True

    # Storage channel ID for media files
    STORAGE_CHANNEL_ID: int

    # I18n (Localization) settings
    SUPPORTED_LOCALES: list[str] = ["en", "uz"]
    DEFAULT_LOCALE: str = "uz"


"""Configuration package bootstrap.

This stub remains for backward compatibility (legacy imports: `from bot.config import settings`).
Actual configuration objects now live in `bot/config/__init__.py` which defines
`Settings` and exposes a singleton `settings`. Performance tuning is unified under
`bot.database.performance.PerformanceConfig` to avoid duplicate class names.
"""

from bot.config import Settings, settings  # type: ignore  # re-export

__all__ = ["settings", "Settings"]
# NOTE: real implementation moved; this file stays minimal.
