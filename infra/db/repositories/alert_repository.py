"""
Alert repository implementations using AsyncPG
Infrastructure layer implementations for alert management
"""

import logging
from datetime import datetime, timedelta

import asyncpg

from core.repositories.alert_repository import AlertSent, AlertSubscription

logger = logging.getLogger(__name__)


class AsyncpgAlertSubscriptionRepository:
    """AsyncPG implementation of AlertSubscriptionRepository"""

    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def create_subscription(self, subscription: AlertSubscription) -> AlertSubscription:
        """Create new alert subscription"""
        query = """
            INSERT INTO alert_subscriptions 
            (chat_id, channel_id, kind, threshold, window_hours, enabled)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, created_at, updated_at
        """

        try:
            row = await self.connection.fetchrow(
                query,
                subscription.chat_id,
                subscription.channel_id,
                subscription.kind,
                subscription.threshold,
                subscription.window_hours,
                subscription.enabled,
            )

            if row:
                subscription.id = row["id"]
                subscription.created_at = row["created_at"]
                subscription.updated_at = row["updated_at"]

            return subscription

        except Exception as e:
            logger.error(f"Failed to create alert subscription: {e}")
            raise

    async def get_subscription(self, subscription_id: int) -> AlertSubscription | None:
        """Get subscription by ID"""
        query = """
            SELECT id, chat_id, channel_id, kind, threshold, window_hours, enabled, created_at, updated_at
            FROM alert_subscriptions
            WHERE id = $1
        """

        try:
            row = await self.connection.fetchrow(query, subscription_id)
            if row:
                return AlertSubscription(
                    id=row["id"],
                    chat_id=row["chat_id"],
                    channel_id=row["channel_id"],
                    kind=row["kind"],
                    threshold=float(row["threshold"]) if row["threshold"] else None,
                    window_hours=row["window_hours"],
                    enabled=row["enabled"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

        except Exception as e:
            logger.error(f"Failed to get alert subscription {subscription_id}: {e}")
            raise

    async def get_user_subscriptions(self, chat_id: int) -> list[AlertSubscription]:
        """Get all subscriptions for a user"""
        query = """
            SELECT id, chat_id, channel_id, kind, threshold, window_hours, enabled, created_at, updated_at
            FROM alert_subscriptions
            WHERE chat_id = $1
            ORDER BY created_at DESC
        """

        try:
            rows = await self.connection.fetch(query, chat_id)
            return [
                AlertSubscription(
                    id=row["id"],
                    chat_id=row["chat_id"],
                    channel_id=row["channel_id"],
                    kind=row["kind"],
                    threshold=float(row["threshold"]) if row["threshold"] else None,
                    window_hours=row["window_hours"],
                    enabled=row["enabled"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get user subscriptions for chat {chat_id}: {e}")
            raise

    async def get_channel_subscriptions(self, channel_id: int) -> list[AlertSubscription]:
        """Get all subscriptions for a channel"""
        query = """
            SELECT id, chat_id, channel_id, kind, threshold, window_hours, enabled, created_at, updated_at
            FROM alert_subscriptions
            WHERE channel_id = $1 AND enabled = TRUE
            ORDER BY created_at DESC
        """

        try:
            rows = await self.connection.fetch(query, channel_id)
            return [
                AlertSubscription(
                    id=row["id"],
                    chat_id=row["chat_id"],
                    channel_id=row["channel_id"],
                    kind=row["kind"],
                    threshold=float(row["threshold"]) if row["threshold"] else None,
                    window_hours=row["window_hours"],
                    enabled=row["enabled"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get channel subscriptions for channel {channel_id}: {e}")
            raise

    async def get_active_subscriptions(self) -> list[AlertSubscription]:
        """Get all active subscriptions"""
        query = """
            SELECT id, chat_id, channel_id, kind, threshold, window_hours, enabled, created_at, updated_at
            FROM alert_subscriptions
            WHERE enabled = TRUE
            ORDER BY created_at ASC
        """

        try:
            rows = await self.connection.fetch(query)
            return [
                AlertSubscription(
                    id=row["id"],
                    chat_id=row["chat_id"],
                    channel_id=row["channel_id"],
                    kind=row["kind"],
                    threshold=float(row["threshold"]) if row["threshold"] else None,
                    window_hours=row["window_hours"],
                    enabled=row["enabled"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in rows
            ]

        except Exception as e:
            logger.error(f"Failed to get active subscriptions: {e}")
            raise

    async def update_subscription(self, subscription: AlertSubscription) -> AlertSubscription:
        """Update existing subscription"""
        query = """
            UPDATE alert_subscriptions
            SET threshold = $1, window_hours = $2, enabled = $3, updated_at = now()
            WHERE id = $4
            RETURNING updated_at
        """

        try:
            row = await self.connection.fetchrow(
                query,
                subscription.threshold,
                subscription.window_hours,
                subscription.enabled,
                subscription.id,
            )

            if row:
                subscription.updated_at = row["updated_at"]

            return subscription

        except Exception as e:
            logger.error(f"Failed to update alert subscription {subscription.id}: {e}")
            raise

    async def delete_subscription(self, subscription_id: int) -> bool:
        """Delete subscription by ID"""
        query = "DELETE FROM alert_subscriptions WHERE id = $1"

        try:
            result = await self.connection.execute(query, subscription_id)
            return result == "DELETE 1"

        except Exception as e:
            logger.error(f"Failed to delete alert subscription {subscription_id}: {e}")
            raise

    async def toggle_subscription(self, subscription_id: int) -> bool:
        """Toggle subscription enabled/disabled status"""
        query = """
            UPDATE alert_subscriptions
            SET enabled = NOT enabled, updated_at = now()
            WHERE id = $1
            RETURNING enabled
        """

        try:
            row = await self.connection.fetchrow(query, subscription_id)
            return row["enabled"] if row else False

        except Exception as e:
            logger.error(f"Failed to toggle alert subscription {subscription_id}: {e}")
            raise


class AsyncpgAlertSentRepository:
    """AsyncPG implementation of AlertSentRepository"""

    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection

    async def mark_alert_sent(self, alert_sent: AlertSent) -> bool:
        """Mark alert as sent for deduplication"""
        query = """
            INSERT INTO alerts_sent (chat_id, channel_id, kind, key, sent_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (chat_id, channel_id, kind, key) DO NOTHING
        """

        try:
            sent_at = alert_sent.sent_at or datetime.utcnow()
            result = await self.connection.execute(
                query,
                alert_sent.chat_id,
                alert_sent.channel_id,
                alert_sent.kind,
                alert_sent.key,
                sent_at,
            )

            # Return True if insert happened (not a duplicate)
            return result == "INSERT 0 1"

        except Exception as e:
            logger.error(f"Failed to mark alert as sent: {e}")
            raise

    async def is_alert_sent(self, chat_id: int, channel_id: int, kind: str, key: str) -> bool:
        """Check if alert was already sent"""
        query = """
            SELECT 1 FROM alerts_sent
            WHERE chat_id = $1 AND channel_id = $2 AND kind = $3 AND key = $4
        """

        try:
            row = await self.connection.fetchrow(query, chat_id, channel_id, kind, key)
            return row is not None

        except Exception as e:
            logger.error(f"Failed to check if alert was sent: {e}")
            raise

    async def cleanup_old_alerts(self, hours_old: int = 24) -> int:
        """Clean up old alert sent records"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
        query = "DELETE FROM alerts_sent WHERE sent_at < $1"

        try:
            result = await self.connection.execute(query, cutoff_time)
            # Extract number of deleted rows from result
            deleted_count = int(result.split()[-1]) if result.startswith("DELETE") else 0

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old alert records")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")
            raise
