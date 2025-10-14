"""
Scheduling Domain Models

Clean Architecture: Domain models represent core business concepts
These are framework-agnostic and contain only business data
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScheduledPost:
    """
    Domain model for a scheduled post

    Represents a post that will be sent to a channel at a specific time
    Immutable data structure following Domain-Driven Design principles
    """

    id: int
    user_id: int
    channel_id: int
    post_text: str | None
    schedule_time: datetime
    media_id: str | None = None
    media_type: str | None = None
    inline_buttons: dict | None = None
    status: str = "pending"

    def has_media(self) -> bool:
        """Check if post includes media"""
        return self.media_id is not None

    def has_text(self) -> bool:
        """Check if post includes text"""
        return self.post_text is not None and len(self.post_text.strip()) > 0

    def has_buttons(self) -> bool:
        """Check if post includes inline buttons"""
        return self.inline_buttons is not None

    def is_valid(self) -> bool:
        """Validate that post has required content"""
        return self.has_text() or self.has_media()


@dataclass
class DeliveryResult:
    """
    Result of a post delivery operation

    Encapsulates all information about the delivery attempt
    Used for tracking and analytics
    """

    success: bool
    message_id: int | None = None
    error: str | None = None
    post_id: int | None = None
    duplicate: bool = False
    rate_limited: bool = False
    idempotency_key: str | None = None

    def __post_init__(self):
        """Validate delivery result consistency"""
        if self.success and self.message_id is None:
            raise ValueError("Successful delivery must have message_id")
        if not self.success and self.error is None:
            raise ValueError("Failed delivery must have error message")


@dataclass
class DeliveryStats:
    """
    Statistics for delivery operations

    Used for monitoring and reporting
    """

    total_attempted: int = 0
    total_succeeded: int = 0
    total_failed: int = 0
    total_duplicates: int = 0
    total_rate_limited: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_attempted == 0:
            return 0.0
        return (self.total_succeeded / self.total_attempted) * 100.0

    def record_success(self, duplicate: bool = False, rate_limited: bool = False) -> None:
        """Record a successful delivery"""
        self.total_attempted += 1
        self.total_succeeded += 1
        if duplicate:
            self.total_duplicates += 1
        if rate_limited:
            self.total_rate_limited += 1

    def record_failure(self) -> None:
        """Record a failed delivery"""
        self.total_attempted += 1
        self.total_failed += 1
