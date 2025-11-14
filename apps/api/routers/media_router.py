"""
Media Router - File upload and management endpoints
Handles media uploads for posts (images, videos, documents)
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/media",
    tags=["Media"],
    responses={404: {"description": "Not found"}},
)


class MediaUploadResponse(BaseModel):
    """Response model for media upload"""
    id: str
    url: str
    type: str
    filename: str
    size: int
    uploaded_at: datetime
    upload_duration: Optional[float] = None
    upload_speed: Optional[float] = None
    upload_type: str = "storage"


# Configure upload directory
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Max file size: 50MB
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed file types
ALLOWED_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'video/mp4', 'video/webm', 'video/quicktime',
    'application/pdf', 'text/plain'
}


@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    channel_id: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📤 Upload Media File

    Upload an image, video, or document for use in posts.

    **Parameters:**
    - file: The media file to upload (max 50MB)
    - channel_id: Optional - if provided, upload directly to channel
    - caption: Optional - caption for the media

    **Supported formats:**
    - Images: JPEG, PNG, GIF, WebP
    - Videos: MP4, WebM, MOV
    - Documents: PDF, TXT

    **Returns:**
    - Upload confirmation with file URL and metadata
    """
    start_time = datetime.now()

    try:
        # Validate file type
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_TYPES)}"
            )

        # Read file content to check size
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is 50MB."
            )

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_id = current_user.get("id", "unknown")
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ")
        unique_filename = f"{user_id}_{timestamp}_{safe_filename}"

        # Determine file path
        if channel_id:
            # Direct to channel upload
            file_path = UPLOAD_DIR / "channels" / str(channel_id) / unique_filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            upload_type = "direct_channel"
        else:
            # Storage upload
            file_path = UPLOAD_DIR / "storage" / unique_filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            upload_type = "storage"

        # Save file
        with open(file_path, "wb") as f:
            f.write(content)

        # Calculate upload stats
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        speed = file_size / duration if duration > 0 else 0

        # Determine media type
        if file.content_type.startswith('image/'):
            media_type = 'image'
        elif file.content_type.startswith('video/'):
            media_type = 'video'
        else:
            media_type = 'document'

        # Generate file ID and URL
        file_id = f"{user_id}_{timestamp}"
        # Use relative path for URL
        relative_path = str(file_path.relative_to(UPLOAD_DIR.parent))
        file_url = f"/uploads/{file_path.name}"

        logger.info(
            f"✅ Media uploaded: {file.filename} ({file_size / 1024:.1f}KB) "
            f"by user {user_id} in {duration:.2f}s"
        )

        return MediaUploadResponse(
            id=file_id,
            url=file_url,
            type=media_type,
            filename=file.filename,
            size=file_size,
            uploaded_at=end_time,
            upload_duration=duration,
            upload_speed=speed,
            upload_type=upload_type
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Media upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload media: {str(e)}"
        )


@router.get("/storage", response_model=dict)
async def list_storage_files(
    offset: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📁 List Storage Files

    Get list of uploaded files in user's storage.

    **Parameters:**
    - offset: Pagination offset (default: 0)
    - limit: Number of files to return (default: 20, max: 100)

    **Returns:**
    - List of files with metadata
    """
    try:
        user_id = current_user.get("id")
        storage_path = UPLOAD_DIR / "storage"

        if not storage_path.exists():
            return {
                "files": [],
                "total": 0,
                "offset": offset,
                "limit": limit
            }

        # Get all user's files
        all_files = []
        for file_path in storage_path.glob(f"{user_id}_*"):
            if file_path.is_file():
                stat = file_path.stat()
                all_files.append({
                    "file_id": file_path.stem,
                    "filename": file_path.name.split("_", 2)[-1] if "_" in file_path.name else file_path.name,
                    "file_size": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "preview_url": f"/uploads/{file_path.name}",
                })

        # Sort by upload time (newest first)
        all_files.sort(key=lambda x: x["uploaded_at"], reverse=True)

        # Apply pagination
        paginated_files = all_files[offset:offset + limit]

        return {
            "files": paginated_files,
            "total": len(all_files),
            "offset": offset,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"❌ Failed to list storage files: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list storage files: {str(e)}"
        )


@router.delete("/{file_id}")
async def delete_media(
    file_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🗑️ Delete Media File

    Delete an uploaded media file.

    **Parameters:**
    - file_id: The ID of the file to delete

    **Returns:**
    - Deletion confirmation
    """
    try:
        user_id = current_user.get("id")

        # Security check: file_id must start with user_id
        if not file_id.startswith(str(user_id)):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to delete this file"
            )

        # Search for file in both storage and channel directories
        storage_path = UPLOAD_DIR / "storage"
        deleted = False

        for file_path in storage_path.rglob(f"{file_id}*"):
            if file_path.is_file():
                file_path.unlink()
                deleted = True
                logger.info(f"✅ Deleted file: {file_path.name}")
                break

        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")

        return {"success": True, "message": "File deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )
