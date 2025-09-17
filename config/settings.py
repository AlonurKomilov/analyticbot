"""
Enhanced configuration settings for AnalyticBot
Centralized settings with proper security handling
"""

from enum import Enum
from typing import Union

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
    BOT_TOKEN: SecretStr = SecretStr("dummy_token_for_development")
    STORAGE_CHANNEL_ID: int = 0
    ADMIN_IDS_STR: str | None = None  # Will be parsed to ADMIN_IDS
    SUPPORTED_LOCALES: list[str] = ["en", "uz"]
    DEFAULT_LOCALE: str = "en"
    ENFORCE_PLAN_LIMITS: bool = True

    # Computed field
    _admin_ids: list[int] | None = None

    # Database Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = SecretStr("password")
    POSTGRES_DB: str = "analyticbot"
    DATABASE_URL: str | None = None
    REDIS_URL: str = "redis://localhost:6379/0"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # API & Web Application
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_HOST_URL: str = "http://localhost:8000"
    TWA_HOST_URL: str = "http://localhost:3000/"
    CORS_ORIGINS: Union[str, list[str]] = "*"

    # Security & Authentication
    JWT_SECRET_KEY: SecretStr = SecretStr("dev_secret_key_change_in_production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_ROUNDS: int = 12
    RATE_LIMIT_PER_MINUTE: int = 60

    # Payment Gateways (Optional)
    STRIPE_SECRET_KEY: SecretStr | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: SecretStr | None = None
    STRIPE_TEST_MODE: bool = True
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
    ANTHROPIC_API_KEY: SecretStr | None = None  # For Smart Auto-Fixer

    # Phase 4.5: Bot UI & Alerts Integration Feature Flags
    BOT_ANALYTICS_UI_ENABLED: bool = True
    ALERTS_ENABLED: bool = False
    EXPORT_ENABLED: bool = True
    SHARE_LINKS_ENABLED: bool = True

    # Week 5-6: Content Protection Feature Flags
    CONTENT_PROTECTION_ENABLED: bool = True
    WATERMARK_ENABLED: bool = True
    THEFT_DETECTION_ENABLED: bool = True
    PREMIUM_FEATURES_ENABLED: bool = True

    # Analytics V2 Bot Client Settings
    ANALYTICS_V2_BASE_URL: str = "http://173.212.236.167:8000"
    ANALYTICS_V2_TOKEN: SecretStr | None = None
    EXPORT_MAX_ROWS: int = 10000
    PNG_MAX_POINTS: int = 2000
    
    # Export Settings
    MAX_EXPORT_SIZE_MB: int = 50
    RATE_LIMIT_PER_HOUR: int = 100
    RATE_LIMIT_PER_MINUTE: int = 10

    # Alert Settings
    ALERT_CHECK_INTERVAL_MINUTES: int = 5
    ALERT_DEDUPE_TTL_HOURS: int = 24

    # Share Links Settings
    SHARE_LINK_DEFAULT_TTL_SECONDS: int = 3600
    SHARE_LINK_MAX_TTL_SECONDS: int = 86400  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, env_parse_none_str="None", extra="ignore"
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
                # Handle JSON format like ["123", "456"] or comma-separated like "123,456"
                import json

                try:
                    # Try to parse as JSON first
                    if admin_str.startswith("[") and admin_str.endswith("]"):
                        parsed_ids = json.loads(admin_str)
                        self._admin_ids = [
                            int(str(id_val).strip()) for id_val in parsed_ids if str(id_val).strip()
                        ]
                    else:
                        # Parse as comma-separated
                        self._admin_ids = [
                            int(id_str.strip()) for id_str in admin_str.split(",") if id_str.strip()
                        ]
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Warning: Could not parse ADMIN_IDS '{admin_str}': {e}")
                    self._admin_ids = []
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

        # Always extract secret value if it's a SecretStr
        if password and hasattr(password, "get_secret_value"):
            password = password.get_secret_value()

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins string to list"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            # Remove quotes if present
            v = v.strip('"\'')
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["*"]

    @field_validator("SUPPORTED_LOCALES", mode="before")
    @classmethod
    def parse_supported_locales(cls, v):
        """Parse comma-separated supported locales"""
        if isinstance(v, str):
            return [locale.strip() for locale in v.split(",") if locale.strip()]
        return v or ["en", "uz"]

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
try:
    settings = Settings()
except Exception as e:
    # For testing or when environment variables are not set
    import os
    # Set minimal required environment variables if not set
    required_vars = {
        'BOT_TOKEN': 'dummy_bot_token',
        'STORAGE_CHANNEL_ID': '123456789',
        'POSTGRES_USER': 'postgres',
        'POSTGRES_PASSWORD': 'password',
        'POSTGRES_DB': 'analyticbot',
        'JWT_SECRET_KEY': 'dummy_jwt_secret'
    }
    
    for var, default_value in required_vars.items():
        if not os.getenv(var):
            os.environ[var] = default_value
    
    settings = Settings()
