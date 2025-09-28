"""
Channel Daily Repository Implementation
Repository for storing and managing daily channel metrics
"""

from datetime import date, datetime, timedelta
from typing import Any

import asyncpg


class AsyncpgChannelDailyRepository:
    """Channel daily metrics repository implementation using asyncpg"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def series_value(self, channel_id: int, metric: str, target_date: datetime) -> int | None:
        """Get metric value for a specific date"""
        target_day = target_date.date() if isinstance(target_date, datetime) else target_date

        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT value FROM channel_daily WHERE channel_id = $1 AND metric = $2 AND day = $3",
                channel_id,
                metric,
                target_day,
            )
            return result

    async def series_data(
        self, channel_id: int, metric: str, from_dt: datetime, to_dt: datetime
    ) -> list[dict[str, Any]]:
        """Get time series data for a metric"""
        from_day = from_dt.date() if isinstance(from_dt, datetime) else from_dt
        to_day = to_dt.date() if isinstance(to_dt, datetime) else to_dt

        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT day, value 
                FROM channel_daily 
                WHERE channel_id = $1 AND metric = $2 AND day BETWEEN $3 AND $4
                ORDER BY day ASC
                """,
                channel_id,
                metric,
                from_day,
                to_day,
            )
            return [{"day": record["day"], "value": record["value"]} for record in records]

    async def upsert_metric(
        self, channel_id: int, target_date: datetime, metric: str, value: int
    ) -> None:
        """Insert or update a daily metric"""
        target_day = target_date.date() if isinstance(target_date, datetime) else target_date

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO channel_daily (channel_id, day, metric, value)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (channel_id, day, metric) DO UPDATE SET
                    value = EXCLUDED.value
                """,
                channel_id,
                target_day,
                metric,
                value,
            )

    async def get_latest_metric(self, channel_id: int, metric: str) -> dict[str, Any] | None:
        """Get the latest value for a specific metric"""
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT day, value 
                FROM channel_daily 
                WHERE channel_id = $1 AND metric = $2
                ORDER BY day DESC
                LIMIT 1
                """,
                channel_id,
                metric,
            )
            return {"day": record["day"], "value": record["value"]} if record else None

    async def get_metrics_for_day(
        self, channel_id: int, target_date: datetime
    ) -> list[dict[str, Any]]:
        """Get all metrics for a specific day"""
        target_day = target_date.date() if isinstance(target_date, datetime) else target_date

        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT metric, value 
                FROM channel_daily 
                WHERE channel_id = $1 AND day = $2
                """,
                channel_id,
                target_day,
            )
            return [{"metric": record["metric"], "value": record["value"]} for record in records]

    async def delete_old_metrics(self, days_to_keep: int = 365) -> int:
        """Delete old metrics to manage storage"""
        cutoff_date = date.today() - timedelta(days=days_to_keep)

        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM channel_daily WHERE day < $1", cutoff_date)

            # Extract number from result string like "DELETE 42"
            deleted_count = 0
            if result and result.startswith("DELETE "):
                try:
                    deleted_count = int(result.split(" ")[1])
                except (IndexError, ValueError):
                    pass

            return deleted_count


# Alias for backwards compatibility and cleaner imports
ChannelDailyRepository = AsyncpgChannelDailyRepository
