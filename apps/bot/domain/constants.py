"""
Bot Domain Constants - Shared constants and enums
Centralized constants to prevent circular imports
"""

from enum import Enum


class PlanType(str, Enum):
    """Available subscription plan types"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class ServiceStatus(str, Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AnalyticsEventType(str, Enum):
    """Analytics event types"""
    POST_PUBLISHED = "post_published"
    POST_VIEWED = "post_viewed"
    USER_SUBSCRIBED = "user_subscribed"
    USER_UNSUBSCRIBED = "user_unsubscribed"
    CHANNEL_ADDED = "channel_added"
    CHANNEL_REMOVED = "channel_removed"


# Default limits
DEFAULT_FREE_CHANNELS = 1
DEFAULT_FREE_POSTS_PER_MONTH = 30
DEFAULT_PREMIUM_CHANNELS = 10
DEFAULT_PREMIUM_POSTS_PER_MONTH = 500

# Performance constants
DEFAULT_BATCH_SIZE = 50
DEFAULT_CACHE_TTL = 300  # 5 minutes
MAX_RETRY_ATTEMPTS = 3

# API rate limits
TELEGRAM_API_RATE_LIMIT = 30  # requests per second
TELEGRAM_BULK_RATE_LIMIT = 20  # bulk operations per second
