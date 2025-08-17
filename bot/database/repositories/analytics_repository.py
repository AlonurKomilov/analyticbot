from typing import Any, Dict, List

from asyncpg import Pool


class AnalyticsRepository:
    def __init__(self, pool: Pool):
        self._pool = pool

    async def log_sent_post(
        self, scheduled_post_id: int, channel_id: int, message_id: int
    ):
        """
        Kanalga yuborilgan post haqidagi ma'lumotni 'sent_posts' jadvaliga yozadi.
        """
        query = """
            INSERT INTO sent_posts (scheduled_post_id, channel_id, message_id)
            VALUES ($1, $2, $3);
        """
        await self._pool.execute(query, scheduled_post_id, channel_id, message_id)

    async def get_all_trackable_posts(
        self, interval_days: int = 7
    ) -> List[Dict[str, Any]]:
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

    # --- YANGI QO'SHILGAN FUNKSIYA ---
    async def get_all_posts_to_track_views(self) -> List[Dict[str, Any]]:
        """
        Yuborilgan (`sent`) statusidagi va ko'rishlarni kuzatish kerak bo'lgan
        barcha postlarni ma'lumotlar bazasidan oladi.
        """
        query = """
            SELECT sp.id, sp.views, sp.channel_id, snt.message_id
            FROM scheduled_posts sp
            JOIN sent_posts snt ON sp.id = snt.scheduled_post_id
            WHERE sp.status = 'sent'
        """
        rows = await self._pool.fetch(query)
        return [dict(row) for row in rows]

    async def get_posts_ordered_by_views(self, channel_id: int) -> List[Dict[str, Any]]:
        """Return posts for a channel ordered by view count."""
        query = """
            SELECT id, views, message_id
            FROM scheduled_posts
            WHERE channel_id = $1
            ORDER BY views DESC
        """
        rows = await self._pool.fetch(query, channel_id)
        return [dict(row) for row in rows]

    async def get_total_users_count(self) -> int:
        """
        Retrieves the total count of users from the database.
        This is a placeholder and assumes a 'users' table exists.
        """
        # This query is a placeholder and might need adjustment based on the actual schema.
        query = "SELECT COUNT(id) FROM users;"
        count = await self._pool.fetchval(query)
        return count or 0

    async def get_total_channels_count(self) -> int:
        """
        Retrieves the total count of channels from the database.
        This is a placeholder and assumes a 'channels' table exists.
        """
        # This query is a placeholder and might need adjustment based on the actual schema.
        query = "SELECT COUNT(id) FROM channels;"
        count = await self._pool.fetchval(query)
        return count or 0

    async def get_total_posts_count(self) -> int:
        """
        Retrieves the total count of scheduled posts from the database.
        This is a placeholder.
        """
        # This query is a placeholder and might need adjustment based on the actual schema.
        query = "SELECT COUNT(id) FROM scheduled_posts;"
        count = await self._pool.fetchval(query)
        return count or 0

    async def get_post_views(self, scheduled_post_id: int) -> int | None:
        """Return the current stored views for a scheduled post or None if missing."""
        query = "SELECT views FROM scheduled_posts WHERE id = $1;"
        val = await self._pool.fetchval(query, scheduled_post_id)
        return int(val) if val is not None else None
