"""
Telegram Storage Service

This service manages file storage using users' own Telegram channels as cloud storage.
Users connect their private Telegram channels, and files are uploaded there instead of server storage.

Benefits:
- Zero server storage costs
- Unlimited storage capacity (Telegram's infrastructure)
- Built-in CDN and media optimization
- Automatic file deduplication via telegram_unique_file_id
"""

import logging
from datetime import datetime
from typing import Any, BinaryIO

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient
from telethon.errors import (
    ChannelPrivateError,
    ChatWriteForbiddenError,
    FilePartsInvalidError,
    FloodWaitError,
)
from telethon.tl.types import DocumentAttributeFilename, Message

from config.settings import settings
from infra.db.models.telegram_storage import TelegramMedia, UserStorageChannel

logger = logging.getLogger(__name__)


class TelegramStorageError(Exception):
    """Base exception for Telegram storage operations"""

    pass


class ChannelNotFoundError(TelegramStorageError):
    """Raised when storage channel is not found or not accessible"""

    pass


class UploadFailedError(TelegramStorageError):
    """Raised when file upload to Telegram fails"""

    pass


class TelegramStorageService:
    """
    Service for managing file storage in user-owned Telegram channels.

    Each user can connect their own private Telegram channel(s) where files are uploaded.
    The service handles:
    - Channel validation and connection
    - File uploads to Telegram
    - File downloads from Telegram
    - File forwarding between channels
    - Storage quota tracking
    """

    def __init__(self, db_session: AsyncSession, telegram_client: TelegramClient):
        self.db = db_session
        self.client = telegram_client

    @classmethod
    async def create_for_user(
        cls,
        user_id: int,
        db_session: AsyncSession,
    ) -> "TelegramStorageService":
        """
        Factory method to create TelegramStorageService with user's MTProto client.

        This method:
        1. Fetches user credentials from database
        2. Decrypts API hash and session string
        3. Creates Telethon client
        4. Validates user authorization
        5. Returns initialized service

        Args:
            user_id: User ID to create service for
            db_session: Database session for queries

        Returns:
            TelegramStorageService instance with user's client

        Raises:
            HTTPException 400: User credentials not found or session expired
            HTTPException 503: Telethon library not available
        """
        from fastapi import HTTPException, status
        from sqlalchemy import select

        from core.services.encryption_service import get_encryption_service
        from infra.db.models.user_bot_orm import UserBotCredentialsORM

        # Get user credentials
        stmt = select(UserBotCredentialsORM).where(UserBotCredentialsORM.user_id == user_id)
        result = await db_session.execute(stmt)
        credentials = result.scalar_one_or_none()

        if (
            not credentials
            or not credentials.mtproto_api_id
            or not credentials.telegram_api_hash
            or not credentials.session_string
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User MTProto credentials not found. Please connect MTProto in Settings. "
                "This is required to validate and use storage channels.",
            )

        # Decrypt credentials
        encryption = get_encryption_service()
        api_hash = encryption.decrypt(credentials.telegram_api_hash)
        session_string = encryption.decrypt(credentials.session_string)

        # Create Telethon client with user's MTProto credentials
        # Import only when MTProto is actually being used (guard pattern)
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession
        except ImportError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"MTProto library (telethon) not available: {e}",
            ) from e

        user_client = TelegramClient(
            StringSession(session_string),
            api_id=credentials.mtproto_api_id,
            api_hash=api_hash,
        )

        try:
            # Connect the client
            await user_client.connect()

            if not await user_client.is_user_authorized():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MTProto session expired. Please reconnect MTProto in Settings.",
                )

            # Return initialized service
            return cls(db_session, user_client)

        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            # Cleanup client on error
            try:
                await user_client.disconnect()
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize Telegram client: {str(e)}",
            ) from e

    async def validate_storage_channel(
        self, user_id: int, channel_id: int, channel_username: str | None = None
    ) -> dict[str, Any]:
        """
        Validate that a channel can be used for storage.

        Checks:
        - Channel exists and is accessible
        - Bot has admin rights (post messages, delete messages)
        - User has permission to use this channel

        Args:
            user_id: User ID attempting to connect the channel
            channel_id: Telegram channel ID (e.g., -1001234567890)
            channel_username: Optional channel username for validation

        Returns:
            Dict with channel info: {id, title, username, member_count, is_valid}

        Raises:
            ChannelNotFoundError: Channel not accessible or doesn't exist
            TelegramStorageError: Bot doesn't have required permissions
        """
        try:
            # Clean and validate channel_username (remove spaces, @, etc.)
            clean_username = None
            if channel_username:
                # Remove @ prefix, spaces, and validate
                clean_username = channel_username.strip().lstrip("@").strip()
                # Check if username contains invalid characters (spaces, etc.)
                if " " in clean_username or not clean_username:
                    logger.warning(f"Invalid username format: '{channel_username}' - ignoring")
                    clean_username = None

            # Get channel entity - prefer username for first-time lookups
            # Telethon needs username or access_hash to resolve channels not in cache
            channel = None
            last_error = None

            # Try username first if provided and valid
            if clean_username:
                try:
                    username_query = f"@{clean_username}"
                    logger.info(f"Attempting to fetch channel by username: {username_query}")
                    channel = await self.client.get_entity(username_query)
                except Exception as e:
                    logger.warning(f"Failed to fetch by username '{username_query}': {e}")

            # Try channel_id with multiple formats as fallback
            if not channel:
                errors = []
                
                # Method 1: Try with provided ID directly
                try:
                    logger.info(f"Attempting to fetch channel by ID: {channel_id}")
                    channel = await self.client.get_entity(channel_id)
                except Exception as e1:
                    errors.append(f"direct({channel_id}): {e1}")
                    
                    # Method 2: Try with negative format
                    try:
                        negative_id = -abs(channel_id)
                        channel = await self.client.get_entity(negative_id)
                        logger.info(f"Fetched channel using negative ID: {negative_id}")
                    except Exception as e2:
                        errors.append(f"negative: {e2}")
                        
                        # Method 3: If ID has 100 prefix, try without it
                        id_str = str(abs(channel_id))
                        if len(id_str) > 10 and id_str.startswith("100"):
                            try:
                                raw_id = int(id_str[3:])  # Remove 100 prefix
                                channel = await self.client.get_entity(raw_id)
                                logger.info(f"Fetched channel using raw ID: {raw_id}")
                            except Exception as e3:
                                errors.append(f"raw({raw_id}): {e3}")
                
                if not channel:
                    error_details = "; ".join(errors) if errors else "Unknown error"
                    logger.error(f"All methods failed for channel_id {channel_id}: {error_details}")

                    # Provide helpful error message
                    error_msg = (
                        f"Cannot access channel (ID: {channel_id}"
                        + (f", Username: @{clean_username}" if clean_username else "")
                        + "). Common reasons:\n\n"
                        "1. **You are not a member of the channel**: Join/create the channel first\n"
                        "2. **Channel username is wrong**: Check spelling (no spaces, e.g., 'my_channel')\n"
                        "3. **Wrong channel ID**: Get the correct ID using @userinfobot\n"
                        "4. **MTProto session issue**: Your Telegram session may have expired\n\n"
                        "💡 Setup: Create channel → You join it → Add your bot as admin → Get ID → Validate"
                    )
                    raise TelegramStorageError(error_msg)

            # Check if bot has admin rights
            permissions = await self.client.get_permissions(channel, "me")

            if not permissions.is_admin:
                raise TelegramStorageError("Bot must be admin in the channel to use it for storage")

            if not permissions.post_messages:
                raise TelegramStorageError("Bot needs 'Post Messages' permission in the channel")

            # Get channel info
            member_count = getattr(channel, "participants_count", None)
            channel_info = {
                "id": channel.id,
                "title": channel.title,
                "username": getattr(channel, "username", None),
                "member_count": member_count if member_count is not None else 0,
                "is_valid": True,
                "bot_is_admin": True,
            }

            logger.info(
                f"Channel validation successful: {channel_info['title']} "
                f"(ID: {channel_id}) for user {user_id}"
            )

            return channel_info

        except ChannelPrivateError:
            raise ChannelNotFoundError("Channel is private or bot doesn't have access")
        except ChatWriteForbiddenError:
            raise TelegramStorageError("Bot doesn't have permission to write in this channel")
        except Exception as e:
            logger.error(f"Channel validation failed: {e}", exc_info=True)
            raise TelegramStorageError(f"Failed to validate channel: {str(e)}")

    async def connect_storage_channel(
        self,
        user_id: int,
        channel_id: int,
        channel_title: str,
        channel_username: str | None = None,
        is_bot_admin: bool = True,
    ) -> UserStorageChannel:
        """
        Connect a user's channel for storage use.

        Creates or updates the storage channel record in the database.

        Args:
            user_id: User ID
            channel_id: Telegram channel ID
            channel_title: Channel display name
            channel_username: Optional channel username
            is_bot_admin: Whether bot has admin access

        Returns:
            UserStorageChannel model instance
        """
        # Check if channel already connected
        result = await self.db.execute(
            select(UserStorageChannel).where(
                and_(
                    UserStorageChannel.user_id == user_id,
                    UserStorageChannel.channel_id == channel_id,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing record
            existing.channel_title = channel_title
            existing.channel_username = channel_username
            existing.is_active = True
            existing.is_bot_admin = is_bot_admin
            existing.last_validated_at = datetime.utcnow()
            existing.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(existing)

            logger.info(f"Updated storage channel {channel_id} for user {user_id}")
            return existing

        # Create new record
        storage_channel = UserStorageChannel(
            user_id=user_id,
            channel_id=channel_id,
            channel_title=channel_title,
            channel_username=channel_username,
            is_active=True,
            is_bot_admin=is_bot_admin,
            last_validated_at=datetime.utcnow(),
        )

        self.db.add(storage_channel)
        await self.db.commit()
        await self.db.refresh(storage_channel)

        logger.info(f"Connected storage channel {channel_id} for user {user_id}")
        return storage_channel

    async def get_user_storage_channels(
        self, user_id: int, only_active: bool = True
    ) -> list[UserStorageChannel]:
        """
        Get all storage channels for a user.

        Args:
            user_id: User ID
            only_active: Only return active channels

        Returns:
            List of UserStorageChannel instances
        """
        query = select(UserStorageChannel).where(UserStorageChannel.user_id == user_id)

        if only_active:
            query = query.where(UserStorageChannel.is_active)

        query = query.order_by(UserStorageChannel.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_default_storage_channel(self, user_id: int) -> UserStorageChannel | None:
        """
        Get the user's default (first active) storage channel.

        Args:
            user_id: User ID

        Returns:
            UserStorageChannel or None if no channels connected
        """
        channels = await self.get_user_storage_channels(user_id, only_active=True)
        return channels[0] if channels else None

    async def upload_file(
        self,
        user_id: int,
        file: BinaryIO,
        file_name: str,
        file_type: str,
        mime_type: str,
        file_size: int,
        caption: str | None = None,
        storage_channel_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TelegramMedia:
        """
        Upload a file to user's Telegram storage channel.

        Args:
            user_id: User ID
            file: File-like object to upload
            file_name: Original file name
            file_type: File type (photo, video, document)
            mime_type: MIME type
            file_size: File size in bytes
            caption: Optional caption for the file
            storage_channel_id: Specific channel ID (uses default if None)
            metadata: Additional metadata to store

        Returns:
            TelegramMedia model instance with Telegram file IDs

        Raises:
            ChannelNotFoundError: No storage channel found for user
            UploadFailedError: Upload to Telegram failed
        """
        # Get storage channel
        if storage_channel_id:
            result = await self.db.execute(
                select(UserStorageChannel).where(
                    and_(
                        UserStorageChannel.id == storage_channel_id,
                        UserStorageChannel.user_id == user_id,
                        UserStorageChannel.is_active,
                    )
                )
            )
            storage_channel = result.scalar_one_or_none()
        else:
            storage_channel = await self.get_default_storage_channel(user_id)

        if not storage_channel:
            raise ChannelNotFoundError(
                "No active storage channel found. Please connect a channel first."
            )

        try:
            # Upload file to Telegram
            message: Message = await self.client.send_file(
                entity=storage_channel.channel_id,
                file=file,
                caption=caption or f"📁 {file_name}",
                attributes=[DocumentAttributeFilename(file_name=file_name)],
                force_document=(file_type == "document"),
            )

            # Extract file information from uploaded message
            media = message.media
            document = getattr(media, "document", None) or getattr(media, "photo", None)

            if not document:
                raise UploadFailedError("Failed to get file info from uploaded message")

            # Get file dimensions if available
            width = height = duration = None
            if hasattr(document, "attributes"):
                for attr in document.attributes:
                    if hasattr(attr, "w") and hasattr(attr, "h"):
                        width, height = attr.w, attr.h
                    if hasattr(attr, "duration"):
                        duration = attr.duration

            # Create database record
            telegram_media = TelegramMedia(
                user_id=user_id,
                storage_channel_id=storage_channel.id,
                telegram_file_id=str(document.id),
                telegram_unique_file_id=getattr(document, "file_reference", b"").hex(),
                telegram_message_id=message.id,
                file_type=file_type,
                file_name=file_name,
                file_size=file_size,
                mime_type=mime_type,
                width=width,
                height=height,
                duration=duration,
                caption=caption,
                metadata=metadata or {},
                is_deleted=False,
            )

            self.db.add(telegram_media)
            await self.db.commit()
            await self.db.refresh(telegram_media)

            logger.info(
                f"Uploaded file {file_name} to channel {storage_channel.channel_id} "
                f"(message_id: {message.id}) for user {user_id}"
            )

            return telegram_media

        except FloodWaitError as e:
            logger.warning(f"Flood wait error: need to wait {e.seconds} seconds")
            raise UploadFailedError(f"Rate limited. Please try again in {e.seconds} seconds")
        except FilePartsInvalidError:
            raise UploadFailedError("File is corrupted or invalid")
        except Exception as e:
            logger.error(f"File upload failed: {e}", exc_info=True)
            raise UploadFailedError(f"Failed to upload file: {str(e)}")

    async def get_file_url(self, media_id: int, user_id: int) -> str:
        """
        Get a public URL for a file stored in Telegram.

        Args:
            media_id: TelegramMedia ID
            user_id: User ID (for authorization check)

        Returns:
            Public URL to access the file

        Raises:
            TelegramStorageError: File not found or access denied
        """
        # Get media record
        result = await self.db.execute(
            select(TelegramMedia).where(
                and_(
                    TelegramMedia.id == media_id,
                    TelegramMedia.user_id == user_id,
                    not TelegramMedia.is_deleted,
                )
            )
        )
        media = result.scalar_one_or_none()

        if not media:
            raise TelegramStorageError("File not found or access denied")

        # For now, return an API endpoint URL
        # In production, this could generate a signed URL or use Telegram's CDN
        return f"{settings.API_HOST_URL}/api/v1/storage/files/{media_id}/download"

    async def list_user_files(
        self, user_id: int, file_type: str | None = None, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """
        List files stored in user's Telegram channels.

        Args:
            user_id: User ID
            file_type: Filter by file type (photo, video, document)
            limit: Max number of files to return
            offset: Pagination offset

        Returns:
            Dict with 'files' list and 'total' count
        """
        # Build query
        query = select(TelegramMedia).where(
            and_(TelegramMedia.user_id == user_id, not TelegramMedia.is_deleted)
        )

        if file_type:
            query = query.where(TelegramMedia.file_type == file_type)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get files
        query = query.order_by(TelegramMedia.uploaded_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        files = list(result.scalars().all())

        return {"files": files, "total": total, "limit": limit, "offset": offset}

    async def delete_file(
        self, media_id: int, user_id: int, delete_from_telegram: bool = True
    ) -> bool:
        """
        Delete a file from storage.

        Args:
            media_id: TelegramMedia ID
            user_id: User ID (for authorization check)
            delete_from_telegram: Whether to delete from Telegram channel

        Returns:
            True if deleted successfully

        Raises:
            TelegramStorageError: File not found or deletion failed
        """
        # Get media record with channel info
        result = await self.db.execute(
            select(TelegramMedia, UserStorageChannel)
            .join(UserStorageChannel, TelegramMedia.storage_channel_id == UserStorageChannel.id)
            .where(
                and_(
                    TelegramMedia.id == media_id,
                    TelegramMedia.user_id == user_id,
                    not TelegramMedia.is_deleted,
                )
            )
        )
        row = result.first()

        if not row:
            raise TelegramStorageError("File not found or already deleted")

        media, channel = row

        # Delete from Telegram if requested
        if delete_from_telegram:
            try:
                await self.client.delete_messages(
                    entity=channel.channel_id, message_ids=[media.telegram_message_id]
                )
                logger.info(
                    f"Deleted message {media.telegram_message_id} from "
                    f"channel {channel.channel_id}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to delete message from Telegram: {e}. "
                    f"Marking as deleted in database only."
                )

        # Mark as deleted in database
        media.is_deleted = True
        await self.db.commit()

        logger.info(f"Marked file {media_id} as deleted for user {user_id}")
        return True

    async def forward_file(self, media_id: int, user_id: int, target_channel_id: int) -> int:
        """
        Forward a file from storage to another channel.

        Useful for posting media to user's public channels without re-uploading.

        Args:
            media_id: TelegramMedia ID
            user_id: User ID (for authorization check)
            target_channel_id: Target Telegram channel ID

        Returns:
            Message ID in target channel

        Raises:
            TelegramStorageError: File not found or forward failed
        """
        # Get media record with source channel
        result = await self.db.execute(
            select(TelegramMedia, UserStorageChannel)
            .join(UserStorageChannel, TelegramMedia.storage_channel_id == UserStorageChannel.id)
            .where(
                and_(
                    TelegramMedia.id == media_id,
                    TelegramMedia.user_id == user_id,
                    not TelegramMedia.is_deleted,
                )
            )
        )
        row = result.first()

        if not row:
            raise TelegramStorageError("File not found")

        media, source_channel = row

        try:
            # Forward message to target channel
            forwarded = await self.client.forward_messages(
                entity=target_channel_id,
                messages=[media.telegram_message_id],
                from_peer=source_channel.channel_id,
            )

            if not forwarded or len(forwarded) == 0:
                raise TelegramStorageError("Forward returned no messages")

            forwarded_msg = forwarded[0]

            logger.info(
                f"Forwarded file {media_id} from storage to channel {target_channel_id} "
                f"(new message_id: {forwarded_msg.id})"
            )

            return forwarded_msg.id

        except Exception as e:
            logger.error(f"Failed to forward file: {e}", exc_info=True)
            raise TelegramStorageError(f"Failed to forward file: {str(e)}")
