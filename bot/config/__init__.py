from enum import Enum
from typing import List, Optional

from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn
    TWA_HOST_URL: AnyHttpUrl
    SENTRY_DSN: str | None = None
    ENFORCE_PLAN_LIMITS: bool = True
    STORAGE_CHANNEL_ID: int
    SUPPORTED_LOCALES: list[str] = ["en", "uz"]
    DEFAULT_LOCALE: str = "uz"

    @field_validator("DEFAULT_LOCALE")
    @classmethod
    def validate_default_locale(cls, v: str, info) -> str:
        supported = info.data.get("SUPPORTED_LOCALES", ["en", "uz"])
        if v not in supported:
            raise ValueError(f"DEFAULT_LOCALE '{v}' must be one of {supported}")
        return v

    WEBAPP_AUTH_MAX_AGE: int = 3600
    LOG_FORMAT: LogFormat = LogFormat.TEXT
    LOG_LEVEL: LogLevel = LogLevel.INFO
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20
    DB_POOL_TIMEOUT: int = 30
    TELEGRAM_API_DELAY: float = 0.5
    TELEGRAM_BATCH_SIZE: int = 50
    ANALYTICS_UPDATE_INTERVAL: int = 300
    ANALYTICS_BATCH_SIZE: int = 50
    HEALTH_CHECK_INTERVAL: int = 300
    HEALTH_CHECK_TIMEOUT: int = 10
    TASK_MAX_RETRIES: int = 3
    TASK_RETRY_DELAY: int = 60
    MAX_MEDIA_SIZE_MB: int = 20
    ALLOWED_MEDIA_TYPES: list[str] = [
        "image/jpeg",
        "image/png",
        "video/mp4",
        "image/gif",
    ]
    API_RATE_LIMIT_REQUESTS: int = 100
    API_RATE_LIMIT_WINDOW: int = 60
    CSRF_PROTECTION_ENABLED: bool = True
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]

    @field_validator("CORS_ALLOWED_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: list[str]) -> list[str]:
        if "*" in v:
            import logging

            logging.getLogger(__name__).warning(
                "CORS is set to allow all origins (*). Not recommended for production."
            )
        return v

    DEBUG_MODE: bool = False
    ENABLE_PROFILING: bool = False
    ENABLE_HEALTH_MONITORING: bool = True
    ENABLE_PERFORMANCE_MONITORING: bool = True
    ALERT_ON_HIGH_ERROR_RATE: bool = True
    ERROR_RATE_THRESHOLD: float = 0.05

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    def get_database_config(self) -> dict:
        return {
            "min_size": self.DB_POOL_MIN_SIZE,
            "max_size": self.DB_POOL_MAX_SIZE,
            "command_timeout": self.DB_POOL_TIMEOUT,
            "server_settings": {
                "application_name": "analyticbot",
                "tcp_keepalives_idle": "600",
                "tcp_keepalives_interval": "30",
                "tcp_keepalives_count": "3",
            },
        }

    def get_logging_config(self) -> dict:
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "text": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "json": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(funcName)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": self.LOG_FORMAT.value,
                    "level": self.LOG_LEVEL.value,
                },
            },
            "root": {
                "level": self.LOG_LEVEL.value,
                "handlers": ["console"],
            },
        }


settings = Settings()

__all__ = ["settings", "Settings", "LogLevel", "LogFormat"]
