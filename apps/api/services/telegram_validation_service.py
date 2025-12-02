"""
Telegram Channel Validation Service
Validates Telegram channels and fetches metadata using Telethon client

✅ Phase 5 Fix (Oct 19, 2025): Uses protocol for type safety
Now uses TelegramClientProtocol instead of concrete TelethonTGClient
Enables dependency injection and testing with mocks
"""

import logging
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

# Use protocol for Clean Architecture compliance

# Type checking only - for IDE support
if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


class ChannelValidationResult(BaseModel):
    """Result of channel validation"""

    is_valid: bool
    telegram_id: int | None = None
    username: str | None = None
    title: str | None = None
    subscriber_count: int | None = None
    description: str | None = None
    telegram_created_at: str | None = None  # Actual Telegram channel creation date
    is_verified: bool = False
    is_scam: bool = False
    is_admin: bool | None = None  # Bot/MTProto session's admin status in the channel
    error_message: str | None = None


class TelegramValidationService:
    """Service for validating Telegram channels and fetching metadata"""

    def __init__(self, telethon_client: Any):
        """
        Initialize validation service

        Args:
            telethon_client: Telegram client for API access

        Note: Uses Any type since TelegramClientProtocol doesn't have all methods yet.
        Future: Expand TelegramClientProtocol with get_full_channel(), _started, _client
        The important part is dependency injection - type can be refined later.
        """
        self.client = telethon_client
        self.logger = logging.getLogger(self.__class__.__name__)

    async def validate_channel_by_username(self, username: str) -> ChannelValidationResult:
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
            
            # Get channel creation date from entity
            telegram_created_at = None
            entity_date = getattr(entity, "date", None)
            if entity_date:
                try:
                    telegram_created_at = entity_date.isoformat()
                except Exception:
                    pass

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
                telegram_created_at=telegram_created_at,
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

            # Try multiple ID formats for robustness
            entity = None
            errors = []
            
            # Method 1: Try with provided ID directly
            try:
                entity = await self.client._client.get_entity(telegram_id)  # type: ignore
            except Exception as e1:
                errors.append(f"direct({telegram_id}): {e1}")
                
                # Method 2: Try with negative format
                try:
                    negative_id = -abs(telegram_id)
                    entity = await self.client._client.get_entity(negative_id)  # type: ignore
                except Exception as e2:
                    errors.append(f"negative({negative_id}): {e2}")
                    
                    # Method 3: If ID has 100 prefix, try without it
                    id_str = str(abs(telegram_id))
                    if len(id_str) > 10 and id_str.startswith("100"):
                        try:
                            raw_id = int(id_str[3:])  # Remove 100 prefix
                            entity = await self.client._client.get_entity(raw_id)  # type: ignore
                        except Exception as e3:
                            errors.append(f"raw({raw_id}): {e3}")
            
            if not entity:
                error_details = "; ".join(errors)
                return {"error": f"Could not resolve channel: {error_details}"}
            
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

    async def check_bot_admin_access(self, username: str) -> tuple[bool, str]:
        """
        Check if the connected bot/MTProto session is an admin in the channel

        This verifies actual ownership by checking if the Telegram client
        (bot or MTProto session) that's making the request has admin rights.

        Args:
            username: Channel username (with or without @)

        Returns:
            Tuple of (has_access, error_message)
        """
        try:
            # Ensure client is started
            if not self.client._started:
                await self.client.start()

            # Clean username
            clean_username = username.strip().lstrip("@")

            if not clean_username:
                return False, "Username cannot be empty"

            # Get channel entity
            try:
                if self.client._client is None:
                    return False, "Telegram client not initialized"

                entity = await self.client._client.get_entity(clean_username)
            except Exception as e:
                self.logger.warning(f"Failed to get entity for @{clean_username}: {e}")
                return False, f"Channel not found: {str(e)}"

            # Check if it's a channel
            entity_type = type(entity).__name__
            if entity_type not in ["Channel"]:
                return False, f"Entity is not a channel (type: {entity_type})"

            # Try to get admin permissions using the current client
            # If the bot/MTProto session is admin, this will succeed
            try:
                from telethon.tl.functions.channels import GetParticipantRequest

                # Get "me" - the user/bot that this client represents
                me = await self.client._client.get_me()
                if not me:
                    return False, "Could not identify current Telegram session"

                # Check if "me" is a participant with admin rights
                try:
                    participant = await self.client._client(
                        GetParticipantRequest(channel=entity, participant=me)
                    )

                    # Check if participant has admin or creator rights
                    participant_type = type(participant.participant).__name__
                    is_admin = participant_type in [
                        "ChannelParticipantAdmin",
                        "ChannelParticipantCreator",
                    ]

                    if not is_admin:
                        self.logger.warning(
                            f"Connected bot/session is not an admin of @{clean_username} "
                            f"(participant type: {participant_type})"
                        )
                        return (
                            False,
                            "Your bot or MTProto session must be added as an admin to this channel. "
                            "Please add your bot/account as an admin with necessary permissions.",
                        )

                    self.logger.info(
                        f"✅ Connected bot/session verified as admin of @{clean_username}"
                    )
                    return True, ""

                except Exception as e:
                    # If we can't get participant info, user is likely not in the channel at all
                    self.logger.warning(f"Not a participant of @{clean_username}: {e}")
                    return (
                        False,
                        "Your bot or MTProto session is not a member of this channel. "
                        "Please add your bot/account as an admin with necessary permissions.",
                    )

            except Exception as e:
                self.logger.error(f"Failed to check admin permissions: {e}")
                return False, f"Could not verify admin access: {str(e)}"

        except Exception as e:
            self.logger.error(f"Error checking admin access: {e}")
            return False, str(e)
