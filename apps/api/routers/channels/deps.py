"""
Dependencies for Channels API

Shared dependencies for all channel management endpoints.
"""

from apps.api.services.telegram_validation_service import TelegramValidationService
from apps.di.analytics_container import (
    get_channel_management_service,
)
from apps.di.analytics_container import (
    get_telegram_validation_service as di_get_telegram_validation_service,
)


async def get_telegram_validation_service() -> TelegramValidationService:
    """Dependency to get telegram validation service"""
    return await di_get_telegram_validation_service()


# Re-export for convenience
__all__ = ["get_channel_management_service", "get_telegram_validation_service"]
