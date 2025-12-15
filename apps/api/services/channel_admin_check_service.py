"""
Channel Admin Check Service

Service for verifying channel admin rights via MTProto.
Extracted from channels_router.py to follow Clean Architecture principles.

This service:
- Encapsulates all MTProto admin checking logic
- Guards Telethon imports (graceful degradation)
- Handles multiple entity resolution strategies
- Returns structured results (not Telethon objects)
"""

import logging
from typing import Any

from core.services.mtproto_service import MTProtoService

logger = logging.getLogger(__name__)


class ChannelAdminCheckService:
    """
    Service for checking channel admin rights via MTProto.

    This service abstracts the complexity of MTProto admin verification,
    including entity resolution, participant checking, and error handling.
    """

    def __init__(self, mtproto_service: MTProtoService):
        """
        Initialize the service.

        Args:
            mtproto_service: Service for getting user's MTProto clients
        """
        self._mtproto_service = mtproto_service

    async def check_mtproto_admin_status(
        self,
        user_id: int,
        channel_id: int,
        channel_username: str | None = None,
        telegram_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Check if user has admin rights in a channel via MTProto.

        This method:
        1. Gets user's MTProto client
        2. Resolves channel entity (username, telegram_id, or fallback)
        3. Checks participant status
        4. Returns structured result

        Args:
            user_id: User ID from authentication
            channel_id: Internal channel ID (database)
            channel_username: Optional Telegram username (@channel)
            telegram_id: Optional Telegram channel ID

        Returns:
            {
                "is_admin": bool,
                "admin_rights": dict | None,
                "method_used": str,  # "username" | "telegram_id" | "failed"
                "error": str | None,
                "participant_type": str | None,  # "ChannelParticipantAdmin", etc.
            }
        """
        result: dict[str, Any] = {
            "is_admin": False,
            "admin_rights": None,
            "method_used": "failed",
            "error": None,
            "participant_type": None,
        }

        try:
            # Get user's MTProto client
            mtproto_client = await self._mtproto_service.get_user_client(  # type: ignore[attr-defined]
                user_id=user_id, channel_id=channel_id
            )

            if not mtproto_client:
                result["error"] = "MTProto client not available for user"
                logger.debug(f"No MTProto client for user {user_id}, channel {channel_id}")
                return result

            # Guard MTProto imports (graceful degradation)
            try:
                from telethon.tl.functions.channels import GetParticipantRequest
            except ImportError as e:
                result["error"] = f"MTProto library (telethon) not available: {e}"
                logger.warning("MTProto library (telethon) not available for admin check")
                return result

            # Attempt to resolve channel entity
            entity = None
            last_error = None

            # Method 1: Try with username first (most reliable)
            if channel_username:
                try:
                    entity = await mtproto_client.client.get_entity(channel_username)
                    result["method_used"] = "username"
                    logger.debug(f"✓ MTProto get_entity via username {channel_username} succeeded")
                except Exception as e:
                    last_error = str(e)
                    logger.debug(f"MTProto username method failed: {e}")

            # Method 2: Try with telegram_id (direct)
            if not entity and telegram_id:
                try:
                    entity = await mtproto_client.client.get_entity(telegram_id)
                    result["method_used"] = "telegram_id"
                    logger.debug(f"✓ MTProto get_entity via ID {telegram_id} succeeded")
                except Exception as e:
                    last_error = str(e)
                    logger.debug(f"MTProto ID method failed: {e}")

                    # Method 3: Try with negative format (-1002678877654)
                    if not entity:
                        try:
                            negative_id = -abs(telegram_id)
                            entity = await mtproto_client.client.get_entity(negative_id)
                            result["method_used"] = "telegram_id_negative"
                            logger.debug(
                                f"✓ MTProto get_entity via negative ID {negative_id} succeeded"
                            )
                        except Exception as e2:
                            logger.debug(f"MTProto negative ID method failed: {e2}")

                    # Method 4: If ID has 100 prefix, try without it
                    if not entity:
                        id_str = str(abs(telegram_id))
                        if len(id_str) > 10 and id_str.startswith("100"):
                            try:
                                raw_id = int(id_str[3:])  # Remove 100 prefix
                                entity = await mtproto_client.client.get_entity(raw_id)
                                result["method_used"] = "telegram_id_raw"
                                logger.debug(f"✓ MTProto get_entity via raw ID {raw_id} succeeded")
                            except Exception as e3:
                                logger.debug(f"MTProto raw ID method failed: {e3}")

            if not entity:
                result["error"] = f"Failed to resolve channel entity: {last_error}"
                logger.warning(
                    f"Failed to get channel entity for channel {channel_id}: {last_error}"
                )
                return result

            # Get current user (MTProto session user)
            me = await mtproto_client.client.get_me()

            # Check participant status
            participant = await mtproto_client.client(
                GetParticipantRequest(channel=entity, participant=me)
            )

            # Check if admin or creator
            participant_type = type(participant.participant).__name__
            result["participant_type"] = participant_type
            result["is_admin"] = participant_type in [
                "ChannelParticipantAdmin",
                "ChannelParticipantCreator",
            ]

            # Extract admin rights if available
            if result["is_admin"] and hasattr(participant.participant, "admin_rights"):
                admin_rights_obj = participant.participant.admin_rights
                result["admin_rights"] = {
                    "change_info": getattr(admin_rights_obj, "change_info", False),
                    "post_messages": getattr(admin_rights_obj, "post_messages", False),
                    "edit_messages": getattr(admin_rights_obj, "edit_messages", False),
                    "delete_messages": getattr(admin_rights_obj, "delete_messages", False),
                    "ban_users": getattr(admin_rights_obj, "ban_users", False),
                    "invite_users": getattr(admin_rights_obj, "invite_users", False),
                    "pin_messages": getattr(admin_rights_obj, "pin_messages", False),
                    "add_admins": getattr(admin_rights_obj, "add_admins", False),
                    "manage_call": getattr(admin_rights_obj, "manage_call", False),
                }

            if result["is_admin"]:
                logger.info(
                    f"✅ User {user_id} MTProto is admin of channel {channel_id} "
                    f"(type: {participant_type})"
                )
            else:
                logger.warning(
                    f"❌ User {user_id} MTProto is NOT admin of channel {channel_id} "
                    f"(type: {participant_type})"
                )

            return result

        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.error(
                f"Failed to check MTProto admin for user {user_id}, channel {channel_id}: {e}",
                exc_info=True,
            )
            return result


# Dependency injection helper
async def get_channel_admin_check_service() -> ChannelAdminCheckService:
    """
    Get ChannelAdminCheckService with dependencies injected from DI container.

    Returns:
        ChannelAdminCheckService instance
    """
    from apps.di import get_container

    container = get_container()
    return await container.bot.channel_admin_check_service()
