"""
Bot Domain Models - Shared DTOs and Data Structures
Centralized location for shared types to prevent circular imports
"""

from dataclasses import dataclass

from pydantic import BaseModel, HttpUrl, field_validator


@dataclass
class SubscriptionStatus:
    """Subscription status and usage information"""
    plan_name: str
    max_channels: int
    current_channels: int
    max_posts_per_month: int
    current_posts_this_month: int


class InlineButton(BaseModel):
    """Telegram inline button configuration"""
    text: str
    url: HttpUrl | None = None
    callback_data: str | None = None

    @field_validator("callback_data")
    @classmethod
    def limit_callback(cls, v: str | None):
        if v and len(v) > 60:
            raise ValueError("callback_data too long (>60)")
        return v


class InlineButtonsPayload(BaseModel):
    """Collection of inline buttons for Telegram messages"""
    buttons: list[list[InlineButton]]

    @field_validator("buttons")
    @classmethod
    def non_empty(cls, v):
        if not v:
            raise ValueError("buttons cannot be empty")
        return v


# Analytics related models
@dataclass
class AnalyticsMetrics:
    """Analytics metrics for services"""
    total_posts: int
    total_views: int
    engagement_rate: float
    timestamp: str


@dataclass  
class ServiceHealth:
    """Health status for services"""
    service_name: str
    is_healthy: bool
    last_check: str
    error_message: str | None = None
