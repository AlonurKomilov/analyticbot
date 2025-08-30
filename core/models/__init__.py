"""
Core domain models for AnalyticBot
Framework-agnostic business entities
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class PostStatus(str, Enum):
    """Post status enumeration"""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeliveryStatus(str, Enum):
    """Delivery status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class ScheduledPost:
    """
    Core domain model for scheduled posts
    Framework-agnostic representation of a post to be delivered
    """

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    channel_id: str = ""
    user_id: str = ""

    # Scheduling
    scheduled_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    # Status and metadata
    status: PostStatus = PostStatus.DRAFT
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Media attachments
    media_urls: list[str] = field(default_factory=list)
    media_types: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate post data after initialization"""
        if not self.content and not self.media_urls:
            raise ValueError("Post must have either content or media")

        if self.media_urls and len(self.media_urls) != len(self.media_types):
            raise ValueError("Media URLs and types must have same length")

    def is_ready_for_delivery(self) -> bool:
        """Check if post is ready to be delivered"""
        return (
            self.status == PostStatus.SCHEDULED
            and self.scheduled_at <= datetime.utcnow()
            and bool(self.content or self.media_urls)
            and bool(self.channel_id)
        )

    def mark_as_published(self) -> None:
        """Mark post as successfully published"""
        self.status = PostStatus.PUBLISHED
        self.updated_at = datetime.utcnow()

    def mark_as_failed(self) -> None:
        """Mark post as failed to publish"""
        self.status = PostStatus.FAILED
        self.updated_at = datetime.utcnow()


@dataclass
class Delivery:
    """
    Core domain model for post deliveries
    Tracks the actual delivery attempt of a scheduled post
    """

    id: UUID = field(default_factory=uuid4)
    post_id: UUID = field(default=None)

    # Delivery tracking
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempted_at: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Delivery details
    delivery_channel_id: str = ""
    message_id: str | None = None  # Telegram message ID after delivery

    # Error handling
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3

    # Delivery metadata
    delivery_metadata: dict[str, Any] = field(default_factory=dict)

    def can_retry(self) -> bool:
        """Check if delivery can be retried"""
        return (
            self.status in [DeliveryStatus.FAILED, DeliveryStatus.RETRYING]
            and self.retry_count < self.max_retries
        )

    def mark_as_delivered(self, message_id: str) -> None:
        """Mark delivery as successful"""
        self.status = DeliveryStatus.DELIVERED
        self.message_id = message_id
        self.delivered_at = datetime.utcnow()
        self.error_message = None

    def mark_as_failed(self, error: str) -> None:
        """Mark delivery as failed"""
        self.status = DeliveryStatus.FAILED
        self.error_message = error
        self.attempted_at = datetime.utcnow()

    def increment_retry(self) -> None:
        """Increment retry count and set status"""
        self.retry_count += 1
        self.status = DeliveryStatus.RETRYING
        self.attempted_at = datetime.utcnow()


@dataclass
class ScheduleFilter:
    """
    Filter criteria for querying scheduled posts
    """

    user_id: str | None = None
    channel_id: str | None = None
    status: PostStatus | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    tags: list[str] | None = None
    limit: int | None = None
    offset: int | None = None


@dataclass
class DeliveryFilter:
    """
    Filter criteria for querying deliveries
    """

    post_id: UUID | None = None
    status: DeliveryStatus | None = None
    channel_id: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    limit: int | None = None
    offset: int | None = None
