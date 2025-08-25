from datetime import datetime
from typing import Any

from asyncpg import Pool


class SchedulerRepository:
    def __init__(self, pool: Pool):
        self._pool = pool

    async def get_scheduler_by_id(self, post_id: int) -> dict[str, Any] | None:
        """Return a scheduled post row by id or None."""
        query = "SELECT * FROM scheduled_posts WHERE id = $1;"
        rec = await self._pool.fetchrow(query, post_id)
        return dict(rec) if rec else None

    async def create_scheduled_post(
        self,
        user_id: int,
        channel_id: int,
        post_text: str,
        schedule_time: datetime,
        media_id: str | None = None,
        media_type: str | None = None,
        inline_buttons: Any | None = None,
    ) -> int:
        """Ma'lumotlar bazasiga yangi rejalashtirilgan post yaratadi."""
        query = """
            INSERT INTO scheduled_posts (user_id, channel_id, post_text, schedule_time, media_id, media_type, inline_buttons, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
            RETURNING id;
        """
        post_id = await self._pool.fetchval(
            query,
            user_id,
            channel_id,
            post_text,
            schedule_time,
            media_id,
            media_type,
            inline_buttons,
        )
        return post_id

    async def get_scheduled_posts_by_user(self, user_id: int) -> list[dict[str, Any]]:
        """Foydalanuvchining barcha 'pending' statusidagi postlarini oladi."""
        query = "SELECT * FROM scheduled_posts WHERE user_id = $1 AND status = 'pending' ORDER BY schedule_time ASC;"
        records = await self._pool.fetch(query, user_id)
        return [dict(record) for record in records]

    async def delete_scheduled_post(self, post_id: int, user_id: int) -> bool:
        """Rejalashtirilgan postni o'chiradi."""
        query = "DELETE FROM scheduled_posts WHERE id = $1 AND user_id = $2;"
        result = await self._pool.execute(query, post_id, user_id)
        return result != "DELETE 0"

    async def update_post_status(self, post_id: int, status: str):
        """Postning statusini yangilaydi ('pending', 'sent', 'error')."""
        query = "UPDATE scheduled_posts SET status = $1 WHERE id = $2;"
        await self._pool.execute(query, status, post_id)

    async def get_pending_posts_to_send(self) -> list[dict[str, Any]]:
        """Yuborish vaqti kelgan barcha postlarni oladi."""
        query = "SELECT * FROM scheduled_posts WHERE schedule_time <= NOW() AND status = 'pending';"
        records = await self._pool.fetch(query)
        return [dict(record) for record in records]

    async def claim_due_posts(self, limit: int = 20) -> list[dict[str, Any]]:
        """Atomically 'claim' pending due posts by switching status to 'sending'.

        This reduces race condition risk when multiple workers poll.
        Returns claimed rows.
        """
        # Use CTE with UPDATE ... RETURNING for atomic claim
        query = """
        WITH cte AS (
            SELECT id FROM scheduled_posts
            WHERE schedule_time <= NOW() AND status='pending'
            ORDER BY schedule_time ASC
            LIMIT $1
            FOR UPDATE SKIP LOCKED
        )
        UPDATE scheduled_posts sp
        SET status='sending'
        FROM cte
        WHERE sp.id = cte.id
        RETURNING sp.*;
        """
        rows = await self._pool.fetch(query, limit)
        return [dict(r) for r in rows]

    async def remove_expired(self, now: datetime) -> int:
        """Remove pending posts whose schedule_time is in the past beyond now (simple clean-up).

        Returns number of deleted rows. (Could be extended with retention window.)
        """
        query = "DELETE FROM scheduled_posts WHERE status='pending' AND schedule_time < $1 RETURNING id;"
        rows = await self._pool.fetch(query, now)
        return len(rows)

    async def count_user_posts_this_month(self, user_id: int) -> int:
        """Foydalanuvchining joriy oyda yaratgan postlari sonini hisoblaydi."""
        query = """
            SELECT COUNT(*) FROM scheduled_posts
            WHERE user_id = $1 AND
                  created_at >= date_trunc('month', CURRENT_TIMESTAMP);
        """
        count = await self._pool.fetchval(query, user_id)
        return count or 0

    async def requeue_stuck_sending_posts(self, max_age_minutes: int = 15) -> int:
        """Reset 'sending' posts older than max_age_minutes back to 'pending'.

        Returns count of requeued posts.
        """
        query = """
        UPDATE scheduled_posts 
        SET status = 'pending'
        WHERE status = 'sending' 
          AND schedule_time <= NOW() - INTERVAL '%s minutes'
        RETURNING id;
        """
        rows = await self._pool.fetch(query % max_age_minutes)
        return len(rows)

    async def cleanup_old_posts(self, days_old: int = 30) -> int:
        """Archive or delete old completed posts.

        Returns count of cleaned posts.
        """
        query = """
        DELETE FROM scheduled_posts
        WHERE status IN ('sent', 'error') 
          AND created_at < NOW() - INTERVAL '%s days'
        RETURNING id;
        """
        rows = await self._pool.fetch(query % days_old)
        return len(rows)

    async def get_scheduled_count(self) -> int:
        """Get total number of scheduled posts (pending)."""
        query = "SELECT COUNT(*) FROM scheduled_posts WHERE status = 'pending'"
        return await self._pool.fetchval(query)
