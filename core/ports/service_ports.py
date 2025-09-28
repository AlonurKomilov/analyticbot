# core/ports/service_ports.py
"""
Service interfaces (ports) for clean architecture.
These define contracts that external services must implement.
"""

from typing import Protocol, runtime_checkable
from datetime import datetime
from uuid import UUID

from core.models import ScheduledPost, Delivery


@runtime_checkable
class NotificationService(Protocol):
    """Port for notification services (email, push, etc.)"""

    async def send_notification(self, user_id: str, message: str, type: str = "info") -> bool:
        """Send notification to user"""
        ...

    async def send_system_alert(self, message: str, severity: str = "info") -> bool:
        """Send system-wide alert"""
        ...


@runtime_checkable
class CacheService(Protocol):
    """Port for caching services"""

    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        ...

    async def set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set value in cache with optional TTL"""
        ...

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        ...

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        ...


@runtime_checkable
class MessageQueueService(Protocol):
    """Port for message queue services"""

    async def publish(self, topic: str, message: dict, delay: int | None = None) -> bool:
        """Publish message to topic with optional delay"""
        ...

    async def subscribe(self, topic: str, callback: callable) -> bool:
        """Subscribe to topic with callback"""
        ...


@runtime_checkable
class FileStorageService(Protocol):
    """Port for file storage services"""

    async def upload(self, file_path: str, content: bytes) -> str:
        """Upload file and return URL"""
        ...

    async def download(self, file_url: str) -> bytes:
        """Download file content"""
        ...

    async def delete(self, file_url: str) -> bool:
        """Delete file"""
        ...


@runtime_checkable
class TelegramService(Protocol):
    """Port for Telegram API services"""

    async def send_message(self, chat_id: str, text: str, **kwargs) -> dict:
        """Send text message"""
        ...

    async def send_media(self, chat_id: str, media_url: str, caption: str = "", **kwargs) -> dict:
        """Send media message"""
        ...

    async def get_chat_info(self, chat_id: str) -> dict:
        """Get chat information"""
        ...

    async def get_chat_members_count(self, chat_id: str) -> int:
        """Get chat members count"""
        ...


@runtime_checkable
class AnalyticsService(Protocol):
    """Port for analytics services"""

    async def track_event(self, event: str, properties: dict) -> bool:
        """Track analytics event"""
        ...

    async def track_delivery(self, delivery: Delivery) -> bool:
        """Track post delivery event"""
        ...

    async def get_channel_stats(self, channel_id: str, from_date: datetime, to_date: datetime) -> dict:
        """Get channel analytics statistics"""
        ...


@runtime_checkable
class SchedulingService(Protocol):
    """Port for scheduling services"""

    async def schedule_post(self, post: ScheduledPost) -> bool:
        """Schedule a post for future delivery"""
        ...

    async def cancel_scheduled_post(self, post_id: UUID) -> bool:
        """Cancel a scheduled post"""
        ...

    async def reschedule_post(self, post_id: UUID, new_time: datetime) -> bool:
        """Reschedule a post to new time"""
        ...