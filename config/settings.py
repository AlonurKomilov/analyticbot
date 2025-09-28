"""
Enhanced configuration settings for AnalyticBot
Centralized settings without framework dependencies
"""

import os
from enum import Enum
from typing import Union
from dataclasses import dataclass, field


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


@dataclass
class SecretStr:
    """Simple wrapper for secret strings"""
    value: str
    
    def get_secret_value(self) -> str:
        return self.value
    
    def __str__(self) -> str:
        return "**********"
    
    def __repr__(self) -> str:
        return "SecretStr('**********')"


@dataclass 
class Settings:
    """
    Main application settings combining all configuration sections
    """

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Telegram Bot Configuration
    BOT_TOKEN: SecretStr = field(default_factory=lambda: SecretStr("dummy_token_for_development"))
    STORAGE_CHANNEL_ID: int = 0
    ADMIN_IDS_STR: str | None = None  # Will be parsed to ADMIN_IDS
    SUPPORTED_LOCALES: Union[str, list[str]] = field(default_factory=lambda: ["en", "uz"])
    DEFAULT_LOCALE: str = "en"
    ENFORCE_PLAN_LIMITS: bool = True

    # Computed field
    _admin_ids: list[int] | None = None

    # Database Configuration - Environment Configurable
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 10100
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: SecretStr = field(default_factory=lambda: SecretStr("password"))
    POSTGRES_DB: str = "analyticbot"
    DATABASE_URL: str | None = None
    REDIS_URL: str = "redis://localhost:10200/0"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Celery & Background Jobs - Environment Configurable
    CELERY_BROKER_URL: str = "redis://localhost:10200/1"  # Use different Redis DB
    CELERY_RESULT_BACKEND: str = "redis://localhost:10200/1"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = field(default_factory=lambda: ["json"])
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    # API & Web Application - Environment Configurable
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 10400
    API_HOST_URL: str = "http://localhost:10400"
    TWA_HOST_URL: str = "http://localhost:10300/"
    CORS_ORIGINS: Union[str, list[str]] = "*"

    # Security & Authentication
    JWT_SECRET_KEY: SecretStr = field(default_factory=lambda: SecretStr("dev_secret_key_change_in_production"))
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
    PROMETHEUS_PORT: int = 10500

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
    ANALYTICS_V2_BASE_URL: str = "http://localhost:11300"
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

    # ============================================================================
    # DEMO MODE CONFIGURATION
    # ============================================================================
    # For now, let's disable demo mode configuration to fix imports
    # demo_mode: 'DemoModeConfig' = field(default_factory=lambda: DemoModeConfig())

    def __post_init__(self):
        """Initialize computed fields"""
        # Parse admin IDs from environment
        admin_str = os.getenv('ADMIN_IDS_STR')
        if admin_str:
            try:
                self._admin_ids = [int(x.strip()) for x in admin_str.split(',') if x.strip()]
            except ValueError:
                self._admin_ids = []
        else:
            self._admin_ids = []

    @property
    def ADMIN_IDS(self) -> list[int]:
        """Parse admin IDs from string"""
        if self._admin_ids is None:
            self.__post_init__()  # Ensure initialization
        return self._admin_ids or []

    def get_database_url(self) -> str:
        """Build DATABASE_URL from components if not provided"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Build from components
        password = self.POSTGRES_PASSWORD.get_secret_value() if hasattr(self.POSTGRES_PASSWORD, 'get_secret_value') else self.POSTGRES_PASSWORD
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        password = self.POSTGRES_PASSWORD.get_secret_value() if hasattr(self.POSTGRES_PASSWORD, 'get_secret_value') else self.POSTGRES_PASSWORD
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

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
