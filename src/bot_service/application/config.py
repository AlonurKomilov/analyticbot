"""
Bot Configuration Module
Provides backward-compatible settings interface for bot components
"""

import logging

from config.settings import Settings as MainSettings

logger = logging.getLogger(__name__)

# Create main settings instance
_main_settings = MainSettings()


class BotSettings:
    """Bot-specific settings wrapper"""

    @property
    def BOT_TOKEN(self):
        return _main_settings.BOT_TOKEN

    @property
    def ADMIN_IDS(self) -> list[int]:
        try:
            admin_ids_str = _main_settings.ADMIN_IDS or ""
            if admin_ids_str:
                return [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
            return []
        except (ValueError, AttributeError):
            logger.warning("Invalid ADMIN_IDS format, returning empty list")
            return []


class MonitoringSettings:
    """Monitoring settings wrapper"""

    @property
    def LOG_LEVEL(self):
        return _main_settings.LOG_LEVEL

    @property
    def LOG_FORMAT(self):
        return _main_settings.LOG_FORMAT


class Settings:
    """
    Main settings class providing backward-compatible interface
    """

    def __init__(self):
        # Core settings
        self.DATABASE_URL = _main_settings.DATABASE_URL
        self.REDIS_URL = _main_settings.REDIS_URL

        # Database pool settings
        self.DB_POOL_SIZE = getattr(_main_settings, "DB_POOL_SIZE", 10)
        self.DB_MAX_OVERFLOW = getattr(_main_settings, "DB_MAX_OVERFLOW", 20)
        self.DB_POOL_TIMEOUT = getattr(_main_settings, "DB_POOL_TIMEOUT", 30)

        # Task settings
        self.TASK_RETRY_DELAY = getattr(_main_settings, "TASK_RETRY_DELAY", 30)
        self.TASK_MAX_RETRIES = getattr(_main_settings, "TASK_MAX_RETRIES", 5)

        # Monitoring settings
        self.ANALYTICS_UPDATE_INTERVAL = getattr(_main_settings, "ANALYTICS_UPDATE_INTERVAL", 300)
        self.HEALTH_CHECK_INTERVAL = getattr(_main_settings, "HEALTH_CHECK_INTERVAL", 300)

        # Localization
        self.DEFAULT_LOCALE = getattr(_main_settings, "DEFAULT_LOCALE", "en")
        self.SUPPORTED_LOCALES = getattr(_main_settings, "SUPPORTED_LOCALES", "en,uz")

        # Web Application settings
        self.TWA_HOST_URL = _main_settings.TWA_HOST_URL
        self.API_HOST_URL = _main_settings.API_HOST_URL

        # App settings for backward compatibility
        self.LOG_FORMAT = _main_settings.LOG_FORMAT

        # Nested settings for new interface
        self.bot = BotSettings()
        self.monitoring = MonitoringSettings()

    # Legacy properties for direct access
    @property
    def BOT_TOKEN(self):
        return _main_settings.BOT_TOKEN


# Create global settings instance
settings = Settings()

# Export for compatibility
__all__ = ["settings", "Settings"]
