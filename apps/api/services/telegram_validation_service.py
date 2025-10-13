"""
Telegram Channel Validation Service
Validates Telegram channels and fetches metadata using Telethon client
"""

import logging
from typing import Any

from pydantic import BaseModel

from infra.tg.telethon_client import TelethonTGClient


logger = logging.getLogger(__name__)


class ChannelValidationResult(BaseModel):
    """Result of channel validation"""

    is_valid: bool
    telegram_id: int | None = None
    username: str | None = None
    title: str | None = None
    subscriber_count: int | None = None
    description: str | None = None
    is_verified: bool = False
    is_scam: bool = False
    error_message: str | None = None


class TelegramValidationService:
    """Service for validating Telegram channels and fetching metadata"""

    def __init__(self, telethon_client: TelethonTGClient):
        """
        Initialize validation service

        Args:
            telethon_client: Telethon client for Telegram API access
        """
        self.client = telethon_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def validate_channel_by_username(
        self, username: str
    ) -> ChannelValidationResult:
        """
        Validate a Telegram channel by username and fetch metadata

        Args:
            username: Channel username (with or without @)

        Returns:
            ChannelValidationResult with validation status and metadata
        """
        try:
            # Ensure client is started
            if not self.client._started:
                await self.client.start()

            # Clean username
            clean_username = username.strip()
            if clean_username.startswith("@"):
                clean_username = clean_username[1:]

            if not clean_username:
                return ChannelValidationResult(
                    is_valid=False, error_message="Username cannot be empty"
                )

            # Get entity from Telegram
            try:
                if self.client._client is None:
                    return ChannelValidationResult(
                        is_valid=False,
                        username=clean_username,
                        error_message="Telegram client not initialized",
                    )

                entity = await self.client._client.get_entity(clean_username)  # type: ignore
            except Exception as e:
                self.logger.warning(f"Failed to get entity for @{clean_username}: {e}")
                return ChannelValidationResult(
                    is_valid=False,
                    username=clean_username,
                    error_message=f"Channel not found or not accessible: {str(e)}",
                )

            # Check if it's a channel
            entity_type = type(entity).__name__
            if entity_type not in ["Channel"]:
                return ChannelValidationResult(
                    is_valid=False,
                    username=clean_username,
                    error_message=f"Entity is not a channel (type: {entity_type})",
                )

            # Extract channel metadata with type checking
            telegram_id = getattr(entity, "id", None)
            title = getattr(entity, "title", None)
            username_from_entity = getattr(entity, "username", clean_username)
            is_verified = getattr(entity, "verified", False)
            is_scam = getattr(entity, "scam", False)

            # Get full channel info for subscriber count
            subscriber_count = None
            description = None
            try:
                full_channel = await self.client.get_full_channel(entity)
                if hasattr(full_channel, "full_chat"):
                    full_chat = full_channel.full_chat
                    if hasattr(full_chat, "participants_count"):
                        subscriber_count = full_chat.participants_count
                    if hasattr(full_chat, "about"):
                        description = full_chat.about
            except Exception as e:
                self.logger.warning(f"Could not fetch full channel info: {e}")

            return ChannelValidationResult(
                is_valid=True,
                telegram_id=telegram_id,
                username=username_from_entity,
                title=title,
                subscriber_count=subscriber_count,
                description=description,
                is_verified=is_verified,
                is_scam=is_scam,
            )

        except Exception as e:
            self.logger.error(f"Error validating channel @{username}: {e}")
            return ChannelValidationResult(
                is_valid=False,
                username=username,
                error_message=f"Validation error: {str(e)}",
            )

    async def get_channel_metadata(self, telegram_id: int) -> dict[str, Any]:
        """
        Get channel metadata by Telegram ID

        Args:
            telegram_id: Telegram channel ID

        Returns:
            Dictionary with channel metadata
        """
        try:
            # Ensure client is started
            if not self.client._started:
                await self.client.start()

            if self.client._client is None:
                return {"error": "Telegram client not initialized"}

            entity = await self.client._client.get_entity(telegram_id)  # type: ignore
            full_channel = await self.client.get_full_channel(entity)

            metadata = {
                "telegram_id": getattr(entity, "id", telegram_id),
                "title": getattr(entity, "title", None),
                "username": getattr(entity, "username", None),
                "is_verified": getattr(entity, "verified", False),
                "is_scam": getattr(entity, "scam", False),
            }

            # Extract full channel info
            if hasattr(full_channel, "full_chat"):
                full_chat = full_channel.full_chat
                if hasattr(full_chat, "participants_count"):
                    metadata["subscriber_count"] = full_chat.participants_count
                if hasattr(full_chat, "about"):
                    metadata["description"] = full_chat.about

            return metadata

        except Exception as e:
            self.logger.error(f"Error getting metadata for channel {telegram_id}: {e}")
            return {"error": str(e)}

    async def check_user_admin_access(
        self, username: str, user_id: int
    ) -> tuple[bool, str]:
        """
        Check if a user has admin access to a channel

        Args:
            username: Channel username
            user_id: Telegram user ID

        Returns:
            Tuple of (has_access, error_message)
        """
        try:
            # This would require checking the user's permissions in the channel
            # For now, we'll return True to allow channel creation
            # In production, you'd want to verify admin rights
            return True, ""

        except Exception as e:
            self.logger.error(f"Error checking admin access: {e}")
            return False, str(e)
