"""
Dependencies for Channels API

Shared dependencies for all channel management endpoints.
"""

import logging

from apps.api.services.telegram_validation_service import TelegramValidationService
from apps.di.analytics_container import (
    get_channel_management_service,
)
from apps.di.analytics_container import (
    get_telegram_validation_service as di_get_telegram_validation_service,
)

logger = logging.getLogger(__name__)


async def get_telegram_validation_service() -> TelegramValidationService | None:
    """
    Dependency to get telegram validation service.

    Returns None if Telegram validation is not available (MTProto not configured,
    client failed to start, etc.). This allows endpoints to handle gracefully
    when validation is unavailable.
    """
    try:
        return await di_get_telegram_validation_service()
    except Exception as e:
        logger.warning(f"Telegram validation service not available: {e}")
        logger.info("Channel operations will work without Telegram validation")
        return None


# Re-export for convenience
__all__ = ["get_channel_management_service", "get_telegram_validation_service"]
