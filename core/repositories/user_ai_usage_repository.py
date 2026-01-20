"""
User AI Usage Repository
=========================

Repository for tracking AI usage (daily and hourly).
"""

import logging
from datetime import datetime, timedelta

import asyncpg

logger = logging.getLogger(__name__)


class UserAIUsageRepository:
    """Repository for AI usage tracking."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_today(self, user_id: int) -> dict | None:
        """Get today's usage for a user."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    id, user_id, usage_date, requests_count, tokens_used,
                    features_used, estimated_cost, created_at, updated_at
                FROM user_ai_usage
                WHERE user_id = $1 AND usage_date = CURRENT_DATE
                """,
                user_id,
            )
            return dict(row) if row else None

    async def increment_usage(
        self,
        user_id: int,
        tokens: int = 0,
        feature_used: str | None = None,
        cost: float = 0.0,
    ) -> dict:
        """Increment usage counters for today."""
        async with self.pool.acquire() as conn:
            # First try to update existing record
            row = await conn.fetchrow(
                """
                UPDATE user_ai_usage
                SET 
                    requests_count = requests_count + 1,
                    tokens_used = tokens_used + $2,
                    estimated_cost = estimated_cost + $3,
                    updated_at = NOW()
                WHERE user_id = $1 AND usage_date = CURRENT_DATE
                RETURNING 
                    id, user_id, usage_date, requests_count, tokens_used,
                    features_used, estimated_cost, created_at, updated_at
                """,
                user_id,
                tokens,
                cost,
            )

            if row:
                return dict(row)

            # If no record exists, create one
            row = await conn.fetchrow(
                """
                INSERT INTO user_ai_usage (
                    user_id, usage_date, requests_count, tokens_used, estimated_cost
                )
                VALUES ($1, CURRENT_DATE, 1, $2, $3)
                RETURNING 
                    id, user_id, usage_date, requests_count, tokens_used,
                    features_used, estimated_cost, created_at, updated_at
                """,
                user_id,
                tokens,
                cost,
            )
            return dict(row)

    async def get_current_hour(self, user_id: int) -> dict | None:
        """Get current hour's usage for rate limiting."""
        async with self.pool.acquire() as conn:
            current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            row = await conn.fetchrow(
                """
                SELECT 
                    id, user_id, hour_timestamp, requests_count,
                    created_at, updated_at
                FROM user_ai_hourly_usage
                WHERE user_id = $1 AND hour_timestamp = $2
                """,
                user_id,
                current_hour,
            )
            return dict(row) if row else None

    async def increment_hourly(self, user_id: int) -> dict:
        """Increment hourly usage counter."""
        async with self.pool.acquire() as conn:
            current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

            # Try to update existing record
            row = await conn.fetchrow(
                """
                UPDATE user_ai_hourly_usage
                SET 
                    requests_count = requests_count + 1,
                    updated_at = NOW()
                WHERE user_id = $1 AND hour_timestamp = $2
                RETURNING 
                    id, user_id, hour_timestamp, requests_count,
                    created_at, updated_at
                """,
                user_id,
                current_hour,
            )

            if row:
                return dict(row)

            # Create new record if doesn't exist
            row = await conn.fetchrow(
                """
                INSERT INTO user_ai_hourly_usage (
                    user_id, hour_timestamp, requests_count
                )
                VALUES ($1, $2, 1)
                RETURNING 
                    id, user_id, hour_timestamp, requests_count,
                    created_at, updated_at
                """,
                user_id,
                current_hour,
            )
            return dict(row)

    async def can_make_request(
        self, user_id: int, daily_limit: int, hourly_limit: int
    ) -> tuple[bool, str, dict]:
        """Check if user can make another request based on limits."""
        # Check daily limit
        today_usage = await self.get_today(user_id)
        if today_usage:
            if today_usage["requests_count"] >= daily_limit:
                return False, "Daily request limit reached", today_usage

        # Check hourly limit
        hour_usage = await self.get_current_hour(user_id)
        if hour_usage:
            if hour_usage["requests_count"] >= hourly_limit:
                return False, "Hourly request limit reached", today_usage or {}

        return True, "OK", today_usage or {}

    async def get_usage_history(self, user_id: int, days: int = 30) -> list[dict]:
        """Get usage history for the past N days."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    id, user_id, usage_date, requests_count, tokens_used,
                    features_used, estimated_cost, created_at, updated_at
                FROM user_ai_usage
                WHERE user_id = $1 
                AND usage_date >= CURRENT_DATE - $2::interval
                ORDER BY usage_date DESC
                """,
                user_id,
                f"{days} days",
            )
            return [dict(row) for row in rows]

    async def cleanup_old_hourly_records(self, hours_to_keep: int = 24) -> int:
        """Clean up hourly usage records older than specified hours."""
        async with self.pool.acquire() as conn:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_to_keep)
            result = await conn.execute(
                """
                DELETE FROM user_ai_hourly_usage
                WHERE hour_timestamp < $1
                """,
                cutoff_time,
            )
            deleted_count = int(result.split()[-1])
            if deleted_count > 0:
                logger.info(f"🧹 Cleaned up {deleted_count} old hourly usage records")
            return deleted_count
