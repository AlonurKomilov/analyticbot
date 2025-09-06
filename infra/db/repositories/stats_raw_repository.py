"""
Stats Raw Repository Implementation
Repository for storing and managing raw statistics data from MTProto
"""

import json
from datetime import datetime, timedelta
from typing import Any

import asyncpg


class AsyncpgStatsRawRepository:
    """Stats raw repository implementation using asyncpg for MTProto stats storage"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def store_raw_stats(
        self, channel_id: int, key: str, data: dict, fetched_at: datetime = None
    ) -> dict[str, Any]:
        """Store raw statistics data from MTProto.

        Args:
            channel_id: Telegram channel ID
            key: Statistics key (e.g., 'views', 'followers', etc.)
            data: Raw JSON data from MTProto
            fetched_at: When the data was fetched

        Returns:
            Dictionary with operation result
        """
        fetched_at = fetched_at or datetime.utcnow()

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO stats_raw (channel_id, key, json, fetched_at)
                VALUES ($1, $2, $3, $4)
                """,
                channel_id,
                key,
                json.dumps(data),
                fetched_at,
            )

            return {
                "stored": True,
                "channel_id": channel_id,
                "key": key,
                "fetched_at": fetched_at,
            }

    async def get_latest_stats(self, channel_id: int, key: str) -> dict[str, Any] | None:
        """Get the latest raw stats for a channel and key.

        Args:
            channel_id: Channel ID
            key: Statistics key

        Returns:
            Latest stats data or None if not found
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT json, fetched_at 
                FROM stats_raw 
                WHERE channel_id = $1 AND key = $2
                ORDER BY fetched_at DESC
                LIMIT 1
                """,
                channel_id,
                key,
            )

            if record:
                return {
                    "channel_id": channel_id,
                    "key": key,
                    "data": json.loads(record["json"]),
                    "fetched_at": record["fetched_at"],
                }
            return None

    async def get_stats_history(
        self,
        channel_id: int,
        key: str,
        from_dt: datetime = None,
        to_dt: datetime = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get statistics history for a channel and key.

        Args:
            channel_id: Channel ID
            key: Statistics key
            from_dt: Start date filter
            to_dt: End date filter
            limit: Maximum records to return

        Returns:
            List of historical stats records
        """
        async with self.pool.acquire() as conn:
            query = """
                SELECT json, fetched_at 
                FROM stats_raw 
                WHERE channel_id = $1 AND key = $2
            """
            params = [channel_id, key]

            if from_dt:
                query += " AND fetched_at >= $3"
                params.append(from_dt)
                if to_dt:
                    query += " AND fetched_at <= $4"
                    params.append(to_dt)
            elif to_dt:
                query += " AND fetched_at <= $3"
                params.append(to_dt)

            query += " ORDER BY fetched_at DESC"

            if limit:
                query += f" LIMIT ${len(params) + 1}"
                params.append(limit)

            records = await conn.fetch(query, *params)

            return [
                {
                    "channel_id": channel_id,
                    "key": key,
                    "data": json.loads(record["json"]),
                    "fetched_at": record["fetched_at"],
                }
                for record in records
            ]

    async def get_all_keys(self, channel_id: int) -> list[str]:
        """Get all available statistics keys for a channel.

        Args:
            channel_id: Channel ID

        Returns:
            List of available keys
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT DISTINCT key FROM stats_raw WHERE channel_id = $1", channel_id
            )
            return [record["key"] for record in records]

    async def cleanup_old_stats(self, days_to_keep: int = 90) -> int:
        """Clean up old statistics data to manage storage.

        Args:
            days_to_keep: Number of days to retain

        Returns:
            Number of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM stats_raw WHERE fetched_at < $1", cutoff_date)

            # Extract number from result string like "DELETE 42"
            deleted_count = 0
            if result and result.startswith("DELETE "):
                try:
                    deleted_count = int(result.split(" ")[1])
                except (IndexError, ValueError):
                    pass

            return deleted_count

    async def get_stats_summary(self, channel_id: int) -> dict[str, Any]:
        """Get a summary of available stats for a channel.

        Args:
            channel_id: Channel ID

        Returns:
            Summary of available stats
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT key) as unique_keys,
                    MIN(fetched_at) as earliest_fetch,
                    MAX(fetched_at) as latest_fetch
                FROM stats_raw 
                WHERE channel_id = $1
                """,
                channel_id,
            )

            return {
                "channel_id": channel_id,
                "total_records": record["total_records"] or 0,
                "unique_keys": record["unique_keys"] or 0,
                "earliest_fetch": record["earliest_fetch"],
                "latest_fetch": record["latest_fetch"],
            }

        return {}


# Alias for backwards compatibility and cleaner imports
StatsRawRepository = AsyncpgStatsRawRepository
