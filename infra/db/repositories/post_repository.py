"""
Post Repository Implementation
Repository for storing and managing Telegram posts/messages
"""

from datetime import datetime
from typing import Any

import asyncpg


class AsyncpgPostRepository:
    """Post repository implementation using asyncpg for MTProto message storage"""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def upsert_post(
        self,
        channel_id: int,
        msg_id: int,
        date: datetime,
        text: str = "",
        links_json: list | None = None,
    ) -> dict[str, Any]:
        """Insert or update a post with UPSERT behavior.

        Args:
            channel_id: Telegram channel ID
            msg_id: Message ID
            date: Message date
            text: Message text content
            links_json: List of extracted links (ignored for now, table doesn't have links column)

        Returns:
            Dictionary with upsert result information
        """
        async with self.pool.acquire() as conn:
            # Check if record exists
            existing = await conn.fetchval(
                "SELECT 1 FROM posts WHERE channel_id = $1 AND msg_id = $2",
                channel_id,
                msg_id,
            )

            if existing:
                # Update existing post
                await conn.execute(
                    """
                    UPDATE posts SET
                        text = $3,
                        updated_at = NOW()
                    WHERE channel_id = $1 AND msg_id = $2
                    """,
                    channel_id,
                    msg_id,
                    text,
                )
                return {"inserted": False, "updated": True}
            else:
                # Insert new post
                await conn.execute(
                    """
                    INSERT INTO posts (channel_id, msg_id, date, text, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, NOW(), NOW())
                    """,
                    channel_id,
                    msg_id,
                    date,
                    text,
                )
                return {"inserted": True, "updated": False}

    async def max_msg_id(self, channel_id: int) -> int | None:
        """Get the maximum message ID for a channel (for incremental sync).

        Args:
            channel_id: Channel ID to query

        Returns:
            Maximum message ID or None if no messages exist
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT MAX(msg_id) FROM posts WHERE channel_id = $1", channel_id
            )
            return result

    async def get_post(self, channel_id: int, msg_id: int) -> dict[str, Any] | None:
        """Get a specific post by channel and message ID.

        Args:
            channel_id: Channel ID
            msg_id: Message ID

        Returns:
            Post dictionary or None if not found
        """
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(
                "SELECT * FROM posts WHERE channel_id = $1 AND msg_id = $2",
                channel_id,
                msg_id,
            )
            return dict(record) if record else None

    async def get_channel_posts(
        self, channel_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get posts for a channel with pagination.

        Args:
            channel_id: Channel ID
            limit: Maximum number of posts to return
            offset: Number of posts to skip

        Returns:
            List of post dictionaries
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT * FROM posts
                WHERE channel_id = $1
                ORDER BY date DESC, msg_id DESC
                LIMIT $2 OFFSET $3
                """,
                channel_id,
                limit,
                offset,
            )
            return [dict(record) for record in records]

    async def count_posts(self, channel_id: int) -> int:
        """Count total posts for a channel.

        Args:
            channel_id: Channel ID

        Returns:
            Total number of posts
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE channel_id = $1", channel_id
            )

    async def delete_post(self, channel_id: int, msg_id: int) -> bool:
        """Delete a specific post.

        Args:
            channel_id: Channel ID
            msg_id: Message ID

        Returns:
            True if post was deleted, False if not found
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM posts WHERE channel_id = $1 AND msg_id = $2",
                channel_id,
                msg_id,
            )
            return result != "DELETE 0"

    async def get_recent_posts(self, hours: int = 24, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent posts across all channels.

        Args:
            hours: Number of hours to look back
            limit: Maximum posts to return

        Returns:
            List of recent post dictionaries
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT * FROM posts
                WHERE date > NOW() - INTERVAL '%s hours'
                ORDER BY date DESC, msg_id DESC
                LIMIT $1
                """,
                limit,
            )
            return [dict(record) for record in records]

    async def count(self, channel_id: int, from_dt: datetime, to_dt: datetime) -> int:
        """Count posts in date range for analytics fusion"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE channel_id = $1 AND date BETWEEN $2 AND $3",
                channel_id,
                from_dt,
                to_dt,
            )

    async def sum_views(self, channel_id: int, from_dt: datetime, to_dt: datetime) -> int:
        """Sum views for posts in date range (from latest metrics)"""
        async with self.pool.acquire() as conn:
            # Join with post_metrics to get latest view counts
            result = await conn.fetchval(
                """
                SELECT COALESCE(SUM(pm.views), 0)
                FROM posts p
                LEFT JOIN LATERAL (
                    SELECT views
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1 AND p.date BETWEEN $2 AND $3
                """,
                channel_id,
                from_dt,
                to_dt,
            )
            return result or 0

    async def top_by_views(
        self, channel_id: int, from_dt: datetime, to_dt: datetime, limit: int
    ) -> list[dict[str, Any]]:
        """Get top posts by views for analytics fusion"""
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                """
                SELECT
                    p.msg_id,
                    p.date,
                    p.text,
                    p.links,
                    COALESCE(pm.views, 0) as views,
                    COALESCE(pm.forwards, 0) as forwards,
                    COALESCE(pm.replies_count, 0) as replies,
                    pm.reactions
                FROM posts p
                LEFT JOIN LATERAL (
                    SELECT views, forwards, replies_count, reactions
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1 AND p.date BETWEEN $2 AND $3
                ORDER BY COALESCE(pm.views, 0) DESC
                LIMIT $4
                """,
                channel_id,
                from_dt,
                to_dt,
                limit,
            )

            results = []
            for record in records:
                post_dict = dict(record)
                # Parse reactions JSON if present
                if post_dict.get("reactions"):
                    import json

                    try:
                        post_dict["reactions"] = json.loads(post_dict["reactions"])
                    except (json.JSONDecodeError, TypeError):
                        post_dict["reactions"] = {}
                else:
                    post_dict["reactions"] = {}

                # Generate title and permalink
                text = post_dict.get("text", "")
                post_dict["title"] = (
                    text[:100] + "..." if len(text) > 100 else text or f"Post {post_dict['msg_id']}"
                )
                post_dict["permalink"] = f"https://t.me/c/{abs(channel_id)}/{post_dict['msg_id']}"

                results.append(post_dict)

            return results


# Alias for backwards compatibility and cleaner imports
PostRepository = AsyncpgPostRepository
