"""
Analytics Repository Implementation
Concrete implementation for analytics data operations
"""

from typing import Any

import asyncpg


class AsyncpgAnalyticsRepository:
    """Analytics repository implementation using asyncpg"""

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def log_sent_post(self, scheduled_post_id: int, channel_id: int, message_id: int):
        """
        Kanalga yuborilgan post haqidagi ma'lumotni 'sent_posts' jadvaliga yozadi.
        """
        query = """
            INSERT INTO sent_posts (scheduled_post_id, channel_id, message_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (channel_id, message_id) DO NOTHING;
        """
        await self._pool.execute(query, scheduled_post_id, channel_id, message_id)

    async def get_all_trackable_posts(self, interval_days: int = 7) -> list[dict[str, Any]]:
        """
        Ko'rishlar sonini tekshirish kerak bo'lgan barcha postlarni oladi.
        Masalan, oxirgi 7 kun ichida yuborilganlar.
        """
        query = """
            SELECT
                sp.id AS scheduled_post_id,
                sp.views,
                snt.channel_id,
                snt.message_id
            FROM scheduled_posts sp
            JOIN sent_posts snt ON sp.id = snt.scheduled_post_id
            WHERE snt.sent_at >= NOW() - ($1 || ' days')::INTERVAL;
        """
        records = await self._pool.fetch(query, interval_days)
        return [dict(record) for record in records]

    async def update_post_views(self, scheduled_post_id: int, views: int):
        """
        Postning ko'rishlar sonini 'scheduled_posts' jadvalida yangilaydi.
        """
        query = "UPDATE scheduled_posts SET views = $1 WHERE id = $2;"
        await self._pool.execute(query, views, scheduled_post_id)

    async def get_all_posts_to_track_views(self) -> list[dict[str, Any]]:
        """
        Optimized version - Uses composite index and reduces data transfer.
        Optimized query that uses covering index to avoid table lookups.
        """
        query = """
            SELECT sp.id, sp.views, sp.channel_id, snt.message_id
            FROM scheduled_posts sp
            INNER JOIN sent_posts snt ON sp.id = snt.scheduled_post_id
            WHERE sp.status = 'sent'
            AND sp.views IS NOT NULL
            ORDER BY sp.id
        """
        rows = await self._pool.fetch(query)
        return [dict(row) for row in rows]

    async def get_posts_ordered_by_views(self, channel_id: int) -> list[dict[str, Any]]:
        """Return posts for a channel ordered by view count."""
        query = """
            SELECT id, views, message_id
            FROM scheduled_posts
            WHERE channel_id = $1 AND status = 'sent'
            ORDER BY views DESC NULLS LAST
        """
        rows = await self._pool.fetch(query, channel_id)
        return [dict(row) for row in rows]

    async def get_total_users_count(self) -> int:
        """
        Optimized version - Uses index-only scan on plan_id.
        Uses covering index for count operations without full table scan.
        """
        query = """
            SELECT COUNT(*)
            FROM users
            WHERE plan_id IS NOT NULL
        """
        count = await self._pool.fetchval(query)
        return count or 0

    async def get_total_channels_count(self) -> int:
        """
        Retrieves the total count of channels from the database.
        """
        query = "SELECT COUNT(id) FROM channels;"
        count = await self._pool.fetchval(query)
        return count or 0

    async def get_total_posts_count(self) -> int:
        """
        Retrieves the total count of scheduled posts from the database.
        """
        query = "SELECT COUNT(id) FROM scheduled_posts;"
        count = await self._pool.fetchval(query)
        return count or 0

    async def get_post_views(self, scheduled_post_id: int) -> int | None:
        """Return the current stored views for a scheduled post or None if missing."""
        query = "SELECT views FROM scheduled_posts WHERE id = $1;"
        val = await self._pool.fetchval(query, scheduled_post_id)
        return int(val) if val is not None else None

    # 🚀 NEW GENERATOR-BASED MEMORY OPTIMIZATIONS

    async def iter_posts_to_track_views(self, batch_size: int = 1000):
        """
        🧠 MEMORY-OPTIMIZED: Generator-based iteration for large datasets
        Yields posts in batches to minimize memory usage for large-scale operations
        """
        offset = 0
        while True:
            query = """
                SELECT sp.id, sp.views, sp.channel_id, snt.message_id
                FROM scheduled_posts sp
                INNER JOIN sent_posts snt ON sp.id = snt.scheduled_post_id
                WHERE sp.status = 'sent'
                AND sp.views IS NOT NULL
                ORDER BY sp.id
                LIMIT $1 OFFSET $2
            """

            rows = await self._pool.fetch(query, batch_size, offset)
            if not rows:
                break

            # Yield batch of dictionaries
            yield [dict(row) for row in rows]

            # If we got fewer rows than batch_size, we're done
            if len(rows) < batch_size:
                break

            offset += batch_size

    async def iter_posts_ordered_by_views(self, channel_id: int, batch_size: int = 1000):
        """
        🧠 MEMORY-OPTIMIZED: Generator for posts ordered by views
        Useful for processing large channels without loading all posts into memory
        """
        offset = 0
        while True:
            query = """
                SELECT id, views, message_id
                FROM scheduled_posts
                WHERE channel_id = $1 AND status = 'sent'
                ORDER BY views DESC NULLS LAST
                LIMIT $2 OFFSET $3
            """

            rows = await self._pool.fetch(query, channel_id, batch_size, offset)
            if not rows:
                break

            yield [dict(row) for row in rows]

            if len(rows) < batch_size:
                break

            offset += batch_size

    async def stream_all_posts_to_track_views(self):
        """
        🧠 ADVANCED MEMORY OPTIMIZATION: Async generator for streaming large datasets
        Yields individual posts to minimize memory footprint for very large datasets
        """
        query = """
            SELECT sp.id, sp.views, sp.channel_id, snt.message_id
            FROM scheduled_posts sp
            INNER JOIN sent_posts snt ON sp.id = snt.scheduled_post_id
            WHERE sp.status = 'sent'
            AND sp.views IS NOT NULL
            ORDER BY sp.id
        """

        # Use cursor for memory-efficient streaming
        async with self._pool.acquire() as conn:
            async with conn.transaction():
                async for record in conn.cursor(query):
                    yield dict(record)

    async def get_channel_posts_stream(self, channel_id: int):
        """
        🧠 MEMORY-OPTIMIZED: Stream posts for a specific channel
        Useful for processing individual channels without memory overhead
        """
        query = """
            SELECT sp.id, sp.views, sp.channel_id, snt.message_id, sp.created_at
            FROM scheduled_posts sp
            INNER JOIN sent_posts snt ON sp.id = snt.scheduled_post_id
            WHERE sp.channel_id = $1 AND sp.status = 'sent'
            ORDER BY sp.created_at DESC
        """

        async with self._pool.acquire() as conn:
            async for record in conn.cursor(query, channel_id):
                yield dict(record)
