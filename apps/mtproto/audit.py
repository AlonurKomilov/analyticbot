"""MTProto audit logging utilities for tracking collection events."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


async def log_mtproto_event(
    user_id: int,
    action: str,
    channel_id: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log MTProto collection event to audit table.

    Args:
        user_id: User ID performing the action
        action: Action type (e.g., 'collection_progress_detail', 'collection_start', etc.)
        channel_id: Optional channel ID
        metadata: Optional metadata dictionary
    """
    try:
        from apps.di import get_container

        container = get_container()
        pool = await container.database.asyncpg_pool()

        # Convert metadata dict to JSON string for JSONB column
        metadata_json = json.dumps(metadata) if metadata else None

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO mtproto_audit_log (user_id, channel_id, action, metadata, timestamp)
                VALUES ($1, $2, $3, $4::jsonb, $5)
                """,
                user_id,
                channel_id,
                action,
                metadata_json,
                datetime.now(UTC),
            )

    except Exception as e:
        logger.warning(f"Failed to log MTProto event: {e}")
