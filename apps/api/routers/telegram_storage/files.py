"""
File Management Endpoints

Handles file operations: upload, list, download, delete, forward.
"""

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.middleware.auth import get_current_user
from apps.api.services.telegram_storage_service import TelegramStorageService
from infra.db.models.telegram_storage import TelegramMedia, UserStorageChannel

from .deps import get_db_session
from .models import (
    FilesListResponse,
    FileUploadResponse,
    TelegramMediaResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file to Telegram storage",
)
async def upload_file_to_storage(
    file: UploadFile = File(..., description="File to upload"),
    caption: str | None = Form(None, description="Optional caption"),
    storage_channel_id: int | None = Form(None, description="Specific channel ID"),
    current_user: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    ## 📤 Upload to Telegram Storage

    Upload a file to your Telegram storage channel.

    **Benefits:**
    - Zero server storage costs
    - Unlimited capacity (Telegram infrastructure)
    - Global CDN delivery
    - Automatic thumbnails and optimization

    **Parameters:**
    - file: File to upload (up to 2GB)
    - caption: Optional caption for the file
    - storage_channel_id: Specific channel (uses default if not provided)

    **Supported:**
    - Images, videos, documents, audio
    - Any file type up to 2GB

    **Note:** Requires connected storage channel and MTProto integration.
    """
    user_id: int = current_user.get("id")  # type: ignore[assignment]
    logger.info(
        f"User {user_id} uploading file: {file.filename} "
        f"({file.content_type}, size: {file.size if hasattr(file, 'size') else 'unknown'})"
    )

    try:
        # Get user's bot credentials
        from apps.di import get_container

        container = get_container()
        user_bot_repo = await container.database.user_bot_repo()
        credentials = await user_bot_repo.get_by_user_id(user_id)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No bot configured. Please configure your bot in Settings first.",
            )

        if not all(
            [credentials.telegram_api_id, credentials.telegram_api_hash, credentials.session_string]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MTProto not configured. Please set up MTProto in Settings first.",
            )

        # Get user's storage channel
        query = select(UserStorageChannel).where(
            UserStorageChannel.user_id == user_id,
            UserStorageChannel.is_active.is_(True),
        )

        if storage_channel_id:
            query = query.where(UserStorageChannel.id == storage_channel_id)
        else:
            query = query.order_by(UserStorageChannel.created_at.asc()).limit(1)

        result = await db_session.execute(query)
        storage_channel = result.scalar_one_or_none()

        if not storage_channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No storage channel connected. Please connect a storage channel first.",
            )

        # Use TelegramStorageService factory (Clean Architecture)
        storage_service = await TelegramStorageService.create_for_user(
            user_id=user_id,
            db_session=db_session,
        )

        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)

            # Determine file type and upload settings
            file_type = "document"  # Default
            force_document = True
            attributes = []

            # Import Telethon attributes and BytesIO
            import io

            from telethon.tl.types import DocumentAttributeFilename

            # Create BytesIO object for file content
            file_bytes = io.BytesIO(file_content)
            file_bytes.name = file.filename or "file"

            if file.content_type:
                if file.content_type.startswith("image/"):
                    if file.content_type == "image/gif":
                        # GIFs as documents to preserve animation
                        file_type = "document"
                        force_document = True
                        if file.filename:
                            attributes.append(DocumentAttributeFilename(file.filename))
                    else:
                        # Regular images as PHOTOS
                        file_type = "photo"
                        force_document = False
                        attributes = []
                        logger.info(f"📸 Detected photo: {file.filename}, force_document=False")
                elif file.content_type.startswith("video/"):
                    # Videos as actual videos
                    file_type = "video"
                    force_document = False
                    attributes = []
                    logger.info(f"🎥 Detected video: {file.filename}, force_document=False")
                elif file.content_type.startswith("audio/"):
                    file_type = "audio"
                    force_document = False
                    if file.filename:
                        attributes.append(DocumentAttributeFilename(file.filename))
                else:
                    # Other files as documents with filename
                    if file.filename:
                        attributes.append(DocumentAttributeFilename(file.filename))

            logger.info(
                f"⚙️ Upload settings: type={file_type}, force_document={force_document}, "
                f"attributes_count={len(attributes)}, content_type={file.content_type}"
            )

            # Upload to Telegram channel - use BytesIO object instead of raw bytes
            message = await storage_service.client.send_file(
                storage_channel.channel_id,
                file_bytes,  # Use BytesIO object, not raw bytes
                caption=caption if caption else None,
                force_document=force_document,
                attributes=attributes if attributes else None,
            )

            logger.info(
                f"✅ Telegram response: has_photo={hasattr(message, 'photo') and message.photo is not None}, "
                f"has_video={hasattr(message, 'video') and message.video is not None}, "
                f"has_document={hasattr(message, 'document') and message.document is not None}"
            )

            # Extract file metadata from message and generate preview URL
            telegram_file_id = None
            width = None
            height = None
            duration = None
            preview_url = None

            # Generate API endpoint URL for thumbnail preview
            # This will be served by our /storage/files/{id}/thumbnail endpoint
            base_url = "https://api.analyticbot.org"  # TODO: Get from config

            if message.photo:
                telegram_file_id = str(message.photo.id)
                file_type = "photo"  # Ensure it's marked as photo
                if hasattr(message.photo, "sizes") and message.photo.sizes:
                    largest = message.photo.sizes[-1]
                    if hasattr(largest, "w"):
                        width = largest.w
                        height = largest.h

            elif message.video:
                telegram_file_id = str(message.video.id)
                file_type = "video"  # Ensure it's marked as video
                width = getattr(message.video, "w", None)
                height = getattr(message.video, "h", None)
                duration = getattr(message.video, "duration", None)

            elif message.document:
                telegram_file_id = str(message.document.id)
                # Check document mime type for better classification
                mime = message.document.mime_type
                if mime and (mime.startswith("image/") or mime.startswith("video/")):
                    # Document that's actually media
                    pass

                # Check if document has image/video attributes
                for attr in message.document.attributes:
                    if hasattr(attr, "w") and hasattr(attr, "h"):
                        width = attr.w
                        height = attr.h
                    if hasattr(attr, "duration"):
                        duration = attr.duration

            # Save metadata to database (without preview_url first)
            media_record = TelegramMedia(
                user_id=user_id,
                storage_channel_id=storage_channel.id,
                telegram_file_id=telegram_file_id or str(message.id),
                telegram_message_id=message.id,
                file_type=file_type,
                file_name=file.filename or "unnamed",
                file_size=file_size,
                mime_type=file.content_type,
                caption=caption,
                width=width,
                height=height,
                duration=duration,
                preview_url=None,  # Will be set after we have the ID
            )

            db_session.add(media_record)
            await db_session.commit()
            await db_session.refresh(media_record)

            # Now generate preview_url using the media_record.id
            # For photos and videos, point to our thumbnail endpoint
            if file_type in ["photo", "video"]:
                base_url = "https://api.analyticbot.org"  # TODO: Get from config/env
                preview_url = f"{base_url}/storage/files/{media_record.id}/thumbnail"
                media_record.preview_url = preview_url
                await db_session.commit()
                await db_session.refresh(media_record)

            logger.info(
                f"Successfully uploaded file {file.filename} for user {user_id} "
                f"to channel {storage_channel.channel_id} (message_id: {message.id})"
            )

            return FileUploadResponse(
                success=True,
                media=TelegramMediaResponse(
                    id=media_record.id,
                    user_id=media_record.user_id,
                    storage_channel_id=media_record.storage_channel_id,
                    telegram_file_id=media_record.telegram_file_id,
                    telegram_message_id=media_record.telegram_message_id,
                    file_type=media_record.file_type,
                    file_name=media_record.file_name,
                    file_size=media_record.file_size,
                    file_size_formatted=media_record.size_formatted,
                    mime_type=media_record.mime_type,
                    width=media_record.width,
                    height=media_record.height,
                    duration=media_record.duration,
                    caption=media_record.caption,
                    preview_url=media_record.preview_url,  # Include preview URL
                    uploaded_at=media_record.uploaded_at.isoformat(),
                ),
                message="File uploaded successfully to Telegram storage!",
            )
        finally:
            # Clean up Telethon client
            if storage_service.client.is_connected():
                await storage_service.client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload file for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )


@router.get("/files", response_model=FilesListResponse, summary="List files in Telegram storage")
async def list_storage_files(
    file_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    ## 📂 List Storage Files

    Browse files stored in your Telegram channels.

    **Parameters:**
    - file_type: Filter by type (photo, video, document, audio)
    - limit: Max files to return (default: 50, max: 100)
    - offset: Pagination offset

    **Returns:**
    - Paginated list of files with metadata

    **Metadata includes:**
    - File name, size, type
    - Upload date and caption
    - Telegram file IDs for direct access
    """
    user_id: int = current_user.get("id")  # type: ignore[assignment]
    logger.info(f"User {user_id} listing files (type={file_type}, limit={limit}, offset={offset})")

    try:
        # Build query to get files for this user
        query = select(TelegramMedia).where(
            TelegramMedia.user_id == user_id, TelegramMedia.is_deleted.is_(False)
        )

        # Filter by file type if specified
        if file_type:
            query = query.where(TelegramMedia.file_type == file_type)

        # Get total count for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db_session.execute(count_query)
        total = total_result.scalar() or 0

        # Order by upload date (newest first) and apply pagination
        query = query.order_by(TelegramMedia.uploaded_at.desc())
        query = query.limit(min(limit, 100)).offset(offset)

        # Execute query
        result = await db_session.execute(query)
        media_files = result.scalars().all()

        # Convert to response models
        files = [
            TelegramMediaResponse(
                id=file.id,
                user_id=file.user_id,
                storage_channel_id=file.storage_channel_id,
                telegram_file_id=file.telegram_file_id,
                telegram_message_id=file.telegram_message_id,
                file_type=file.file_type,
                file_name=file.file_name,
                file_size=file.file_size,
                file_size_formatted=file.size_formatted,
                mime_type=file.mime_type,
                width=file.width,
                height=file.height,
                duration=file.duration,
                caption=file.caption,
                preview_url=file.preview_url,
                uploaded_at=file.uploaded_at.isoformat(),
            )
            for file in media_files
        ]

        return FilesListResponse(files=files, total=total, limit=min(limit, 100), offset=offset)

    except Exception as e:
        logger.error(f"Failed to list storage files for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list storage files: {str(e)}",
        )


@router.get("/files/{media_id}", response_model=TelegramMediaResponse, summary="Get file metadata")
async def get_file_metadata(
    media_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📋 Get File Metadata

    Retrieve detailed information about a specific file.

    **Parameters:**
    - media_id: File ID from your storage

    **Returns:**
    - Complete file metadata including Telegram file IDs
    """
    logger.info(f"User {current_user.get('id')} requesting metadata for file: {media_id}")

    # TODO: Fetch file metadata from database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"File {media_id} not found or access denied"
    )


@router.get("/files/{media_id}/url", summary="Get file download URL")
async def get_file_url(
    media_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔗 Get File URL

    Get a URL to access/download a file from Telegram storage.

    **Parameters:**
    - media_id: File ID from your storage

    **Returns:**
    - Direct Telegram CDN URL or API proxy endpoint
    """
    logger.info(f"User {current_user.get('id')} requesting URL for file: {media_id}")

    # TODO: Generate file access URL
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"File {media_id} not found or access denied"
    )


@router.get("/files/{media_id}/thumbnail", summary="Get file thumbnail")
async def get_file_thumbnail(
    media_id: int,
    current_user: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    """
    ## 🖼️ Get File Thumbnail

    Get a thumbnail/preview image for photos and videos.

    **Parameters:**
    - media_id: File ID from your storage

    **Returns:**
    - Image data (JPEG/PNG) for display in UI

    **Note:** For photos and videos only. Documents return 404.
    """
    from fastapi.responses import Response
    from sqlalchemy import select

    user_id: int = current_user.get("id")  # type: ignore[assignment]

    logger.info(f"User {user_id} requesting thumbnail for file: {media_id}")

    try:
        # Get file metadata from database
        result = await db_session.execute(
            select(TelegramMedia).where(
                TelegramMedia.id == media_id,
                TelegramMedia.user_id == user_id,
                TelegramMedia.is_deleted.is_(False),
            )
        )
        media_file = result.scalar_one_or_none()

        if not media_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found or access denied"
            )

        # Only generate thumbnails for photos and videos
        if media_file.file_type not in ["photo", "video"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Thumbnails not available for {media_file.file_type} files",
            )

        # Get storage channel
        channel_result = await db_session.execute(
            select(UserStorageChannel).where(UserStorageChannel.id == media_file.storage_channel_id)
        )
        storage_channel = channel_result.scalar_one_or_none()

        if not storage_channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Storage channel not found"
            )

        # Create storage service to download thumbnail
        storage_service = await TelegramStorageService.create_for_user(
            user_id=user_id,
            db_session=db_session,
        )

        try:
            # Get the message
            from_channel = storage_channel.channel_username or int(storage_channel.channel_id)
            message = await storage_service.client.get_messages(
                entity=from_channel, ids=media_file.telegram_message_id
            )

            if not message or not message.media:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Media not found in Telegram"
                )

            # Download thumbnail/preview
            import io

            thumbnail_bytes = io.BytesIO()

            # Download with thumb parameter for smaller preview
            await storage_service.client.download_media(
                message.media,
                file=thumbnail_bytes,
                thumb=-1,  # Download smallest thumbnail
            )

            thumbnail_bytes.seek(0)
            content = thumbnail_bytes.read()

            # Determine content type
            content_type = "image/jpeg"
            if media_file.mime_type and media_file.mime_type.startswith("image/"):
                content_type = media_file.mime_type

            return Response(
                content=content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                    "Content-Disposition": f'inline; filename="thumb_{media_file.file_name}"',
                },
            )

        finally:
            if storage_service.client.is_connected():
                await storage_service.client.disconnect()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate thumbnail for file {media_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate thumbnail: {str(e)}",
        )


@router.delete(
    "/files/{media_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete file from storage"
)
async def delete_storage_file(
    media_id: int,
    delete_from_telegram: bool = True,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🗑️ Delete File

    Remove a file from storage.

    **Parameters:**
    - media_id: File ID to delete
    - delete_from_telegram: Also delete from Telegram channel (default: true)

    **Behavior:**
    - If true: File deleted from Telegram and marked deleted in database
    - If false: File remains in Telegram, only marked as deleted in database
    """
    logger.info(
        f"User {current_user.get('id')} deleting file {media_id} "
        f"(from_telegram={delete_from_telegram})"
    )

    # TODO: Delete file and update database
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"File {media_id} not found or access denied"
    )


@router.post("/files/{media_id}/forward", summary="Forward file to another channel")
async def forward_file_to_channel(
    media_id: int,
    target_channel_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⏩ Forward File

    Forward a file from storage to another Telegram channel.

    **Use case:**
    - Post media to your public channel without re-uploading
    - Share files between channels instantly

    **Parameters:**
    - media_id: File ID from your storage
    - target_channel_id: Destination Telegram channel ID

    **Returns:**
    - Message ID in the target channel

    **Note:** File is forwarded within Telegram's infrastructure (instant, no bandwidth used).
    """
    logger.info(
        f"User {current_user.get('id')} forwarding file {media_id} "
        f"to channel {target_channel_id}"
    )

    # TODO: Forward message using MTProto
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="File forwarding requires MTProto integration. Feature coming soon!",
    )
