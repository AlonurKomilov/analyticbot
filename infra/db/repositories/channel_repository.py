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
        self,
        channel_id: int,
        user_id: int,
        title: str,
        username: str | None = None,
        description: str | None = None,
    ) -> None:
        """Adds a new channel to the database for a specific user.

        If the channel already exists, its title, username, and description are refreshed.
        """

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO channels (id, user_id, title, username, description)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO UPDATE
                    SET title = EXCLUDED.title,
                        username = EXCLUDED.username,
                        description = EXCLUDED.description
                """,
                channel_id,
                user_id,
                title,
                username,
                description,
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
                "SELECT id, title, username, description, created_at FROM channels WHERE user_id = $1",
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
        is_supergroup: bool = False,
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
                0,  # Default user_id for MTProto channels
            )

            # Return the channel record
            record = await conn.fetchrow("SELECT * FROM channels WHERE id = $1", channel_id)
            return dict(record) if record else {}

    async def get_channels(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all channels with pagination - API compatibility method"""
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT * FROM channels ORDER BY id LIMIT $1 OFFSET $2", limit, skip
            )
            return [dict(record) for record in records]

    async def get_channel_by_telegram_id(self, telegram_id: int) -> dict[str, Any] | None:
        """Get channel by telegram ID - API compatibility method"""
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow("SELECT * FROM channels WHERE id = $1", telegram_id)
            return dict(record) if record else None

    async def get_channel(self, channel_id: int) -> dict[str, Any] | None:
        """Get channel by ID - alias for get_channel_by_id for API compatibility"""
        return await self.get_channel_by_id(channel_id)

    async def get_tracked_channels(self) -> list[dict[str, Any]]:
        """Get all tracked channels - channels that have data collection enabled"""
        async with self.pool.acquire() as conn:
            records = await conn.fetch("SELECT * FROM channels ORDER BY id")
            return [dict(record) for record in records]

    async def get_all_channels(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """Get all channels (admin method)"""
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT * FROM channels ORDER BY id OFFSET $1 LIMIT $2", skip, limit
            )
            return [dict(record) for record in records]

    async def update_channel_status(self, channel_id: int, is_active: bool) -> None:
        """Update channel active status"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE channels SET is_active = $1, updated_at = NOW() WHERE id = $2",
                is_active,
                channel_id,
            )

    async def update_channel(self, channel_id: int, **kwargs) -> dict[str, Any] | None:
        """Update channel with provided fields"""
        if not kwargs:
            # If no updates, just return the current channel
            return await self.get_channel_by_id(channel_id)

        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        param_num = 1

        for key, value in kwargs.items():
            if key in ["name", "description", "username", "is_active"]:
                set_clauses.append(f"{key} = ${param_num}")
                values.append(value)
                param_num += 1

        if not set_clauses:
            # No valid fields to update
            return await self.get_channel_by_id(channel_id)

        # Add updated_at
        set_clauses.append(f"updated_at = ${param_num}")
        values.append("NOW()")
        param_num += 1

        # Add channel_id for WHERE clause
        values.append(channel_id)

        query = f"UPDATE channels SET {', '.join(set_clauses)} WHERE id = ${param_num} RETURNING *"

        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(query, *values[:-1], values[-1])
            return dict(record) if record else None


# Alias for backwards compatibility and cleaner imports
ChannelRepository = AsyncpgChannelRepository
