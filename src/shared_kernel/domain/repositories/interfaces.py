"""
Repository Interfaces (Ports) for Clean Architecture
Contains all abstract repository interfaces that define contracts
Concrete implementations are in infra/db/repositories/
"""

from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.shared_kernel.domain.entities import Delivery, DeliveryFilter, ScheduledPost, ScheduleFilter


class UserRepository(Protocol):
    """User repository interface using Protocol (structural typing)"""

    async def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID"""
        ...

    async def get_user_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get user by Telegram ID"""
        ...

    async def create_user(self, user_data: dict) -> dict:
        """Create new user"""
        ...

    async def update_user(self, user_id: int, **updates) -> bool:
        """Update user information"""
        ...

    async def get_user_subscription_tier(self, user_id: int) -> str:
        """Get user's subscription tier"""
        ...

    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists"""
        ...


class AdminRepository(Protocol):
    """Admin repository interface using Protocol"""

    async def get_admin_by_username(self, username: str) -> dict | None:
        """Get admin by username"""
        ...

    async def create_admin(self, admin_data: dict) -> dict:
        """Create new admin"""
        ...

    async def update_admin(self, admin_id: int, **updates) -> bool:
        """Update admin information"""
        ...


class ChannelRepository(Protocol):
    """Channel repository interface using Protocol"""

    async def create_channel(
        self, channel_id: int, user_id: int, title: str, username: str | None = None
    ) -> None:
        """Create a new channel"""
        ...

    async def get_channel_by_id(self, channel_id: int) -> dict | None:
        """Get channel by ID"""
        ...

    async def count_user_channels(self, user_id: int) -> int:
        """Count user's channels"""
        ...

    async def get_user_channels(self, user_id: int) -> list[dict]:
        """Get all channels for a user"""
        ...

    async def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel"""
        ...

    async def count(self) -> int:
        """Get total number of channels"""
        ...

    async def ensure_channel(
        self,
        channel_id: int,
        username: str | None = None,
        title: str | None = None,
        is_supergroup: bool = False,
    ) -> dict:
        """Ensure channel exists with UPSERT behavior"""
        ...

    async def get_channels(self, skip: int = 0, limit: int = 100) -> list[dict]:
        """Get all channels with pagination"""
        ...

    async def get_channel_by_telegram_id(self, telegram_id: int) -> dict | None:
        """Get channel by telegram ID"""
        ...

    async def get_channel(self, channel_id: int) -> dict | None:
        """Get channel by ID (alias)"""
        ...

    async def get_tracked_channels(self) -> list[dict]:
        """Get all tracked channels"""
        ...


class ScheduleRepository(Protocol):
    """
    Abstract interface for scheduled post persistence
    Defines contract for data access without implementation details
    """

    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """Create a new scheduled post"""
        ...

    async def get_by_id(self, post_id: UUID) -> ScheduledPost | None:
        """Get scheduled post by ID"""
        ...

    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """Update an existing scheduled post"""
        ...

    async def delete(self, post_id: UUID) -> bool:
        """Delete a scheduled post"""
        ...

    async def find(self, filter_criteria: ScheduleFilter) -> list[ScheduledPost]:
        """Find scheduled posts by filter criteria"""
        ...

    async def get_ready_for_delivery(self) -> list[ScheduledPost]:
        """Get all posts that are ready for delivery"""
        ...

    async def count(self, filter_criteria: ScheduleFilter) -> int:
        """Count scheduled posts matching filter criteria"""
        ...


class DeliveryRepository(Protocol):
    """
    Abstract interface for delivery tracking persistence
    Defines contract for delivery data access
    """

    async def create(self, delivery: Delivery) -> Delivery:
        """Create a new delivery record"""
        ...

    async def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        """Get delivery by ID"""
        ...

    async def get_by_post_id(self, post_id: UUID) -> list[Delivery]:
        """Get all deliveries for a specific post"""
        ...

    async def update(self, delivery: Delivery) -> Delivery:
        """Update an existing delivery"""
        ...

    async def find(self, filter_criteria: DeliveryFilter) -> list[Delivery]:
        """Find deliveries by filter criteria"""
        ...

    async def get_failed_retryable(self) -> list[Delivery]:
        """Get failed deliveries that can be retried"""
        ...

    async def count(self, filter_criteria: DeliveryFilter) -> int:
        """Count deliveries matching filter criteria"""
        ...


class ChannelDailyRepository(Protocol):
    """Repository interface for daily channel metrics"""

    async def series_value(self, channel_id: int, metric: str, date: datetime) -> int | None:
        """Get metric value for a specific date"""
        ...

    async def series_data(
        self, channel_id: int, metric: str, from_dt: datetime, to_dt: datetime
    ) -> list[dict]:
        """Get time series data for a metric"""
        ...

    async def upsert_metric(self, channel_id: int, date: datetime, metric: str, value: int) -> None:
        """Insert or update a daily metric"""
        ...


class PostRepository(Protocol):
    """Repository interface for posts/messages"""

    async def count(self, channel_id: int, from_dt: datetime, to_dt: datetime) -> int:
        """Count posts in date range"""
        ...

    async def sum_views(self, channel_id: int, from_dt: datetime, to_dt: datetime) -> int:
        """Sum views for posts in date range"""
        ...

    async def top_by_views(
        self, channel_id: int, from_dt: datetime, to_dt: datetime, limit: int
    ) -> list[dict]:
        """Get top posts by views"""
        ...


class PostMetricsRepository(Protocol):
    """Repository interface for post metrics snapshots"""

    async def get_latest_for_posts(
        self, channel_id: int, from_dt: datetime, to_dt: datetime
    ) -> list[dict]:
        """Get latest metrics for posts in date range"""
        ...


class EdgesRepository(Protocol):
    """Repository interface for mention/forward edges"""

    async def top_edges(
        self, channel_id: int, from_dt: datetime, to_dt: datetime, kind: str
    ) -> list[dict]:
        """Get top edges (mentions/forwards) for a channel"""
        ...
