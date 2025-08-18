from typing import Optional, List
from enum import Enum

from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Main connection URL for Python application
    DATABASE_URL: PostgresDsn

    # Redis connection URL
    REDIS_URL: RedisDsn

    # Telegram Web App (Frontend) URL
    TWA_HOST_URL: AnyHttpUrl

    # Sentry DSN for error tracking
    SENTRY_DSN: Optional[str] = None

    # Plan limit enforcement
    ENFORCE_PLAN_LIMITS: bool = True

    # Storage channel ID for media files
    STORAGE_CHANNEL_ID: int

    # I18n (Localization) settings
    SUPPORTED_LOCALES: List[str] = ["en", "uz"]
    DEFAULT_LOCALE: str = "uz"

    @field_validator("DEFAULT_LOCALE")
    @classmethod
    def validate_default_locale(cls, v: str, info) -> str:
        """Ensure default locale is in supported locales"""
        supported = info.data.get("SUPPORTED_LOCALES", ["en", "uz"])
        if v not in supported:
            raise ValueError(f"DEFAULT_LOCALE '{v}' must be one of {supported}")
        return v

    # Telegram WebApp auth initData maximum age (seconds)
    WEBAPP_AUTH_MAX_AGE: int = 3600

    # Logging configuration
    LOG_FORMAT: LogFormat = LogFormat.TEXT
    LOG_LEVEL: LogLevel = LogLevel.INFO

    # Performance and monitoring settings
    # Database connection pool settings
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Telegram API rate limiting
    TELEGRAM_API_DELAY: float = 0.5
    TELEGRAM_BATCH_SIZE: int = 50

    # Analytics settings
    ANALYTICS_UPDATE_INTERVAL: int = 300  # seconds
    ANALYTICS_BATCH_SIZE: int = 50

    # Health check settings
    HEALTH_CHECK_INTERVAL: int = 300  # seconds
    HEALTH_CHECK_TIMEOUT: int = 10

    # Task retry settings
    TASK_MAX_RETRIES: int = 3
    TASK_RETRY_DELAY: int = 60  # seconds

    # Media upload settings
    MAX_MEDIA_SIZE_MB: int = 20
    ALLOWED_MEDIA_TYPES: List[str] = ["image/jpeg", "image/png", "video/mp4", "image/gif"]

    # Rate limiting for API endpoints
    API_RATE_LIMIT_REQUESTS: int = 100
    API_RATE_LIMIT_WINDOW: int = 60  # seconds

    # Security settings
    CSRF_PROTECTION_ENABLED: bool = True
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ALLOWED_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Warn about wildcard CORS in production"""
        if "*" in v:
            import logging
            logging.getLogger(__name__).warning(
                "CORS is set to allow all origins (*). This is not recommended for production."
            )
        return v

    # Development and debugging
    DEBUG_MODE: bool = False
    ENABLE_PROFILING: bool = False

    # Monitoring and alerting
    ENABLE_HEALTH_MONITORING: bool = True
    ENABLE_PERFORMANCE_MONITORING: bool = True
    ALERT_ON_HIGH_ERROR_RATE: bool = True
    ERROR_RATE_THRESHOLD: float = 0.05  # 5% error rate threshold

    # Pydantic configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    def get_database_config(self) -> dict:
        """Get database configuration dict"""
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
        """Get logging configuration dict"""
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


# Global settings instance
# All other modules in the project should import this 'settings' object
settings = Settings()
