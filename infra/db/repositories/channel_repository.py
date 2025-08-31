"""
Channel Repository Implementation
Concrete implementation for channel data operations
"""

from typing import Any

import asyncpg


class AsyncpgChannelRepository:
    """Channel repository implementation using asyncpg"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_channel(
        self, channel_id: int, user_id: int, title: str, username: str | None = None
    ) -> None:
        """Adds a new channel to the database for a specific user.

        If the channel already exists, its title and username are refreshed.
        """

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO channels (id, user_id, title, username)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE
                    SET title = EXCLUDED.title,
                        username = EXCLUDED.username
                """,
                channel_id,
                user_id,
                title,
                username,
            )

    async def get_channel_by_id(self, channel_id: int) -> dict[str, Any] | None:
        """Retrieve a single channel by its ID."""

        async with self.pool.acquire() as conn:
            record = await conn.fetchrow("SELECT * FROM channels WHERE id = $1", channel_id)
            return dict(record) if record else None

    async def count_user_channels(self, user_id: int) -> int:
        """Count how many channels a user has registered."""

        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM channels WHERE user_id = $1", user_id)

    async def get_user_channels(self, user_id: int) -> list[dict[str, Any]]:
        """Retrieve all channels registered by a user."""

        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT id, title, username FROM channels WHERE user_id = $1",
                user_id,
            )
            return [dict(record) for record in records]

    async def delete_channel(self, channel_id: int) -> bool:
        """Delete a channel by its ID."""

        async with self.pool.acquire() as conn:
            result = await conn.execute("DELETE FROM channels WHERE id = $1", channel_id)
            return result != "DELETE 0"

    async def count(self) -> int:
        """Get total number of channels."""
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM channels")

    async def ensure_channel(
        self, 
        channel_id: int, 
        username: str | None = None,
        title: str | None = None,
        is_supergroup: bool = False
    ) -> dict[str, Any]:
        """Ensure channel exists with UPSERT behavior for MTProto ingestion.
        
        Args:
            channel_id: Telegram channel ID
            username: Channel username (without @)
            title: Channel title/name
            is_supergroup: Whether channel is a supergroup
            
        Returns:
            Dictionary with channel information
        """
        async with self.pool.acquire() as conn:
            # Use UPSERT to handle existing channels
            await conn.execute(
                """
                INSERT INTO channels (id, title, username, user_id)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET
                    title = COALESCE(EXCLUDED.title, channels.title),
                    username = COALESCE(EXCLUDED.username, channels.username),
                    updated_at = NOW()
                """,
                channel_id,
                title or username or f"Channel_{channel_id}",
                username,
                0  # Default user_id for MTProto channels
            )
            
            # Return the channel record
            record = await conn.fetchrow("SELECT * FROM channels WHERE id = $1", channel_id)
            return dict(record) if record else {}


# Alias for backwards compatibility and cleaner imports
ChannelRepository = AsyncpgChannelRepository
