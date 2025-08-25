"""
Enhanced configuration settings for AnalyticBot
Centralized settings with proper security handling
"""

from enum import Enum

from pydantic import AnyHttpUrl, RedisDsn, SecretStr, field_validator
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
    Main application settings combining all configuration sections
    """

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Telegram Bot Configuration
    BOT_TOKEN: SecretStr
    STORAGE_CHANNEL_ID: int
    ADMIN_IDS_STR: str | None = None  # Will be parsed to ADMIN_IDS
    SUPPORTED_LOCALES: list[str] = ["en", "uz"]
    DEFAULT_LOCALE: str = "en"
    ENFORCE_PLAN_LIMITS: bool = True

    # Computed field
    _admin_ids: list[int] | None = None

    # Database Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    DATABASE_URL: str | None = None
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # API & Web Application
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_HOST_URL: AnyHttpUrl = "http://localhost:8000"
    TWA_HOST_URL: AnyHttpUrl
    CORS_ORIGINS: list[str] = ["*"]

    # Security & Authentication
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_ROUNDS: int = 12
    RATE_LIMIT_PER_MINUTE: int = 60

    # Payment Gateways (Optional)
    STRIPE_SECRET_KEY: SecretStr | None = None
    STRIPE_WEBHOOK_SECRET: SecretStr | None = None
    PAYME_SECRET_KEY: SecretStr | None = None
    CLICK_SECRET_KEY: SecretStr | None = None

    # Monitoring & Logging
    SENTRY_DSN: str | None = None
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: LogFormat = LogFormat.TEXT
    LOG_FILE: str | None = None
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    # External Services
    OPENAI_API_KEY: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        env_parse_none_str="None",
    )

    @field_validator("ADMIN_IDS_STR", mode="before")
    @classmethod
    def capture_admin_ids(cls, v):
        """Capture ADMIN_IDS env var as string"""
        return v

    @property
    def ADMIN_IDS(self) -> list[int]:
        """Parse admin IDs from string"""
        if self._admin_ids is None:
            admin_str = getattr(self, "ADMIN_IDS_STR", None)
            if not admin_str:
                # Try to get from environment directly
                import os

                admin_str = os.getenv("ADMIN_IDS") or os.getenv("ADMIN_IDS_STR", "")

            if admin_str:
                self._admin_ids = [
                    int(id_str.strip()) for id_str in admin_str.split(",") if id_str.strip()
                ]
            else:
                self._admin_ids = []

        return self._admin_ids

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def build_database_url(cls, v, info):
        """Build DATABASE_URL from components if not provided"""
        if v:
            return v

        values = info.data
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        host = values.get("POSTGRES_HOST", "localhost")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB")

        if password and hasattr(password, "get_secret_value"):
            password = password.get_secret_value()

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins"""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v or ["*"]

    # Convenience property accessors for backward compatibility
    @property
    def bot(self):
        """Bot-specific settings"""
        return self

    @property
    def api(self):
        """API-specific settings"""
        return self

    @property
    def database(self):
        """Database-specific settings"""
        return self

    @property
    def security(self):
        """Security-specific settings"""
        return self

    @property
    def monitoring(self):
        """Monitoring-specific settings"""
        return self


# Global settings instance
settings = Settings()
