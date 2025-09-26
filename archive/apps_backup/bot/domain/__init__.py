"""
Bot Domain Module
Shared types, models, and constants for bot services
"""

from .constants import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_CACHE_TTL,
    DEFAULT_FREE_CHANNELS,
    DEFAULT_FREE_POSTS_PER_MONTH,
    DEFAULT_PREMIUM_CHANNELS,
    DEFAULT_PREMIUM_POSTS_PER_MONTH,
    MAX_RETRY_ATTEMPTS,
    TELEGRAM_API_RATE_LIMIT,
    TELEGRAM_BULK_RATE_LIMIT,
    AnalyticsEventType,
    PlanType,
    ServiceStatus,
)
from .models import (
    AnalyticsMetrics,
    InlineButton,
    InlineButtonsPayload,
    ServiceHealth,
    SubscriptionStatus,
)

__all__ = [
    # Models
    "SubscriptionStatus",
    "InlineButton",
    "InlineButtonsPayload",
    "AnalyticsMetrics",
    "ServiceHealth",
    # Constants
    "PlanType",
    "ServiceStatus",
    "AnalyticsEventType",
    "DEFAULT_FREE_CHANNELS",
    "DEFAULT_FREE_POSTS_PER_MONTH",
    "DEFAULT_PREMIUM_CHANNELS",
    "DEFAULT_PREMIUM_POSTS_PER_MONTH",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_CACHE_TTL",
    "MAX_RETRY_ATTEMPTS",
    "TELEGRAM_API_RATE_LIMIT",
    "TELEGRAM_BULK_RATE_LIMIT",
]
