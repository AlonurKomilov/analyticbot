"""
Media Router - TWA Media Upload and Management API

This router handles direct media uploads through Telegram Web App,
storage channel management, and file operations.
"""

import logging
import mimetypes
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from apps.bot.container import container
from apps.bot.database.repositories.channel_repository import ChannelRepository
from apps.bot.services.media_service import MediaService
from core.security_engine.auth import get_current_user
from core.security_engine.models import User

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/media", tags=["Media"], responses={404: {"description": "Not found"}}
)


class MediaUploadResponse(BaseModel):
    """Media upload response model"""
    file_id: str
    file_name: str
    file_size: int
    file_type: str
    storage_channel_id: int
    telegram_file_id: str
    upload_timestamp: datetime
    metadata: dict = Field(default_factory=dict)


class StorageFileInfo(BaseModel):
    """Storage file information model"""
    id: int
    file_name: str
    file_type: str
    file_size: int
    telegram_file_id: str
    storage_channel_id: int
    created_at: datetime
    metadata: dict = Field(default_factory=dict)


class MediaUploadRequest(BaseModel):
    """Media upload request parameters"""
    channel_id: int
    direct_to_channel: bool = False
    compress: bool = True
    tags: List[str] = Field(default_factory=list)


# Dependency injection
async def get_media_service() -> MediaService:
    """Get media service from container"""
    return container.resolve(MediaService)


async def get_channel_repository() -> ChannelRepository:
    """Get channel repository from container"""
    return container.resolve(ChannelRepository)


@router.post("/upload-direct", response_model=MediaUploadResponse)
async def upload_media_direct(
    file: UploadFile = File(...),
    channel_id: int = 0,
    direct_to_channel: bool = False,
    compress: bool = True,
    current_user: User = Depends(get_current_user),
    media_service: MediaService = Depends(get_media_service),
    channel_repo: ChannelRepository = Depends(get_channel_repository),
):
    """
    Direct media upload to storage channel with TWA integration
    
    Args:
        file: The uploaded file
        channel_id: Target channel ID (0 for storage channel)
        direct_to_channel: Upload directly to channel vs storage
        compress: Apply compression if applicable
        current_user: Authenticated user
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400, detail="File name is required"
            )
        
        # Check file size (50MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(
                status_code=413, detail="File too large (max 50MB)"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Get MIME type
        file_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        
        # Validate channel access
        if channel_id > 0:
            channel = await channel_repo.get_by_id(channel_id)
            if not channel:
                raise HTTPException(
                    status_code=404, detail="Channel not found"
                )
        
        # Upload to Telegram
        upload_result = await media_service.upload_media(
            file=file,
            channel_id=channel_id,
            direct_to_channel=direct_to_channel,
            compress=compress,
            user_id=current_user.id,
        )
        
        return MediaUploadResponse(
            file_id=upload_result["file_id"],
            file_name=file.filename,
            file_size=file_size,
            file_type=file_type,
            storage_channel_id=upload_result["storage_channel_id"],
            telegram_file_id=upload_result["telegram_file_id"],
            upload_timestamp=datetime.utcnow(),
            metadata=upload_result.get("metadata", {}),
        )
        
    except Exception as e:
        logger.error(f"Media upload failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Upload failed: {str(e)}"
        )


@router.get("/storage-files/{channel_id}", response_model=List[StorageFileInfo])
async def get_storage_files(
    channel_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    media_service: MediaService = Depends(get_media_service),
):
    """Get all files from storage channel for management"""
    try:
        files = await media_service.get_storage_files(
            channel_id=channel_id,
            limit=limit,
            offset=offset,
            user_id=current_user.id,
        )
        
        return [
            StorageFileInfo(
                id=file["id"],
                file_name=file["file_name"],
                file_type=file["file_type"],
                file_size=file["file_size"],
                telegram_file_id=file["telegram_file_id"],
                storage_channel_id=file["storage_channel_id"],
                created_at=file["created_at"],
                metadata=file.get("metadata", {}),
            )
            for file in files
        ]
        
    except Exception as e:
        logger.error(f"Failed to get storage files: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get files: {str(e)}"
        )


@router.delete("/storage-files/{file_id}")
async def delete_storage_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    media_service: MediaService = Depends(get_media_service),
):
    """Delete file from storage channel"""
    try:
        success = await media_service.delete_storage_file(
            file_id=file_id,
            user_id=current_user.id,
        )
        
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail="File not found"
            )
            
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Delete failed: {str(e)}"
        )


@router.get("/upload-progress/{upload_id}")
async def get_upload_progress(
    upload_id: str,
    current_user: User = Depends(get_current_user),
    media_service: MediaService = Depends(get_media_service),
):
    """Get upload progress for long-running uploads"""
    try:
        progress = await media_service.get_upload_progress(
            upload_id=upload_id,
            user_id=current_user.id,
        )
        
        return {
            "upload_id": upload_id,
            "progress": progress["progress"],
            "status": progress["status"],
            "bytes_uploaded": progress["bytes_uploaded"],
            "total_bytes": progress["total_bytes"],
            "estimated_time_remaining": progress.get("estimated_time_remaining"),
        }
        
    except Exception as e:
        logger.error(f"Failed to get upload progress: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Progress check failed: {str(e)}"
        )


@router.post("/compress")
async def compress_media(
    file: UploadFile = File(...),
    quality: int = 80,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    media_service: MediaService = Depends(get_media_service),
):
    """Compress media file before upload"""
    try:
        if quality < 1 or quality > 100:
            raise HTTPException(
                status_code=400, detail="Quality must be between 1 and 100"
            )
        
        compressed_file = await media_service.compress_media(
            file=file,
            quality=quality,
            max_width=max_width,
            max_height=max_height,
        )
        
        return {
            "original_size": compressed_file["original_size"],
            "compressed_size": compressed_file["compressed_size"],
            "compression_ratio": compressed_file["compression_ratio"],
            "file_data": compressed_file["file_data"],
            "mime_type": compressed_file["mime_type"],
        }
        
    except Exception as e:
        logger.error(f"Media compression failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Compression failed: {str(e)}"
        )
