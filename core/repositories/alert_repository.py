"""
Alert repository interfaces for Clean Architecture
Core domain abstractions for alert management
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class AlertSubscription:
    """Alert subscription domain model"""

    chat_id: int
    channel_id: int
    kind: str  # 'spike', 'quiet', 'growth'
    window_hours: int
    enabled: bool
    threshold: float | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class AlertSent:
    """Alert sent tracking domain model"""

    chat_id: int
    channel_id: int
    kind: str
    key: str
    sent_at: datetime | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AlertSubscriptionRepository(Protocol):
    """Repository interface for alert subscriptions"""

    async def create_subscription(self, subscription: AlertSubscription) -> AlertSubscription:
        """Create new alert subscription"""
        ...

    async def get_subscription(self, subscription_id: int) -> AlertSubscription | None:
        """Get subscription by ID"""
        ...

    async def get_user_subscriptions(self, chat_id: int) -> list[AlertSubscription]:
        """Get all subscriptions for a user"""
        ...

    async def get_channel_subscriptions(self, channel_id: int) -> list[AlertSubscription]:
        """Get all subscriptions for a channel"""
        ...

    async def get_active_subscriptions(self) -> list[AlertSubscription]:
        """Get all active subscriptions"""
        ...

    async def update_subscription(self, subscription: AlertSubscription) -> AlertSubscription:
        """Update existing subscription"""
        ...

    async def delete_subscription(self, subscription_id: int) -> bool:
        """Delete subscription by ID"""
        ...

    async def toggle_subscription(self, subscription_id: int) -> bool:
        """Toggle subscription enabled/disabled status"""
        ...


class AlertSentRepository(Protocol):
    """Repository interface for alert sent tracking"""

    async def mark_alert_sent(self, alert_sent: AlertSent) -> bool:
        """Mark alert as sent for deduplication"""
        ...

    async def is_alert_sent(self, chat_id: int, channel_id: int, kind: str, key: str) -> bool:
        """Check if alert was already sent"""
        ...

    async def cleanup_old_alerts(self, hours_old: int = 24) -> int:
        """Clean up old alert sent records"""
        ...
