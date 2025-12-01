"""
MTProto-related Celery tasks.

Tasks for syncing data between Telegram (via MTProto) and the database.
"""

import asyncio
import logging
from datetime import datetime

from apps.shared.utils.error_handler import ErrorContext, ErrorHandler
from apps.shared.utils.task_utils import enhanced_retry_task
from apps.di import get_container

logger = logging.getLogger(__name__)


async def cleanup_resources():
    """Clean up resources after task completion"""
    try:
        pass
    except Exception as e:
        logger.warning("Resource cleanup warning", exc_info=e)


@enhanced_retry_task
def sync_channel_metadata_task():
    """
    Periodic task to sync channel metadata (title, description, subscriber count) from Telegram.
    
    This ensures the database stays in sync with any changes made to channel settings
    in Telegram (e.g., description, title changes).
    
    Schedule: Every 6 hours via Celery Beat
    """

    async def _run() -> str:
        context = ErrorContext().add("task", "sync_channel_metadata")
        synced = 0
        errors = 0
        
        try:
            from apps.mtproto.config import MTProtoSettings
            
            settings = MTProtoSettings()
            if not settings.MTPROTO_ENABLED:
                logger.info("MTProto disabled, skipping channel metadata sync")
                return "mtproto-disabled"
            
            container = get_container()
            pool = await container.database.pool()
            
            # Get all active channels
            async with pool.acquire() as conn:
                channels = await conn.fetch(
                    "SELECT id, user_id, title FROM channels WHERE is_active = true"
                )
            
            if not channels:
                logger.info("No active channels to sync")
                return "no-channels"
            
            logger.info(f"🔄 Syncing metadata for {len(channels)} channels...")
            
            # Import MTProto service
            from apps.mtproto.services.user_mtproto_service import UserMTProtoService
            
            user_bot_repo = await container.database.user_bot_repo()
            mtproto_service = UserMTProtoService(user_bot_repo)
            
            # Group channels by user_id for efficient connection reuse
            channels_by_user: dict[int, list] = {}
            for ch in channels:
                user_id = ch["user_id"]
                if user_id not in channels_by_user:
                    channels_by_user[user_id] = []
                channels_by_user[user_id].append(ch)
            
            # Process each user's channels
            for user_id, user_channels in channels_by_user.items():
                try:
                    # Get or create MTProto client for this user
                    client = await mtproto_service.get_or_create_client(user_id)
                    if not client:
                        logger.warning(f"No MTProto client available for user {user_id}")
                        continue
                    
                    for channel in user_channels:
                        try:
                            channel_id = channel["id"]
                            
                            # Get full channel info from Telegram
                            from telethon.tl.functions.channels import GetFullChannelRequest
                            
                            full_response = await client(GetFullChannelRequest(channel_id))
                            
                            if full_response:
                                full_chat = getattr(full_response, "full_chat", None)
                                chats = getattr(full_response, "chats", [])
                                
                                if full_chat:
                                    subscriber_count = getattr(full_chat, "participants_count", 0)
                                    about = getattr(full_chat, "about", None)
                                    
                                    # Get channel entity for title/username
                                    channel_entity = None
                                    for chat in chats:
                                        if getattr(chat, "id", None) == abs(channel_id):
                                            channel_entity = chat
                                            break
                                    
                                    title = getattr(channel_entity, "title", None) if channel_entity else None
                                    username = getattr(channel_entity, "username", None) if channel_entity else None
                                    
                                    # Update database
                                    async with pool.acquire() as conn:
                                        await conn.execute(
                                            """
                                            UPDATE channels
                                            SET subscriber_count = $1,
                                                description = COALESCE($2, description),
                                                title = COALESCE($3, title),
                                                username = COALESCE($4, username),
                                                updated_at = NOW()
                                            WHERE id = $5
                                            """,
                                            subscriber_count,
                                            about,
                                            title,
                                            username,
                                            abs(channel_id),
                                        )
                                    
                                    synced += 1
                                    logger.debug(f"✅ Synced channel {channel_id}: {title}")
                                    
                        except Exception as e:
                            errors += 1
                            logger.warning(f"Failed to sync channel {channel['id']}: {e}")
                            
                except Exception as e:
                    logger.warning(f"Failed to process channels for user {user_id}: {e}")
            
            logger.info(f"✅ Channel metadata sync complete: {synced} synced, {errors} errors")
            return f"synced-{synced}-errors-{errors}"
            
        except Exception as e:
            ErrorHandler.log_error(e, context)
            logger.exception("sync_channel_metadata_task failed", exc_info=e)
            return "sync-failed"
        finally:
            await cleanup_resources()

    return asyncio.run(_run())
