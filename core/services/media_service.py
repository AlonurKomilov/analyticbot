"""
Media Service - TWA Media Management Service

Handles media upload, storage, compression, and file management
for Telegram Web App integration.
"""

import asyncio
import hashlib
import logging
import mimetypes
import tempfile
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import UploadFile
from PIL import Image, ImageOps
from pydantic import BaseModel

from apps.bot.container import container
from apps.bot.database.repositories.channel_repository import ChannelRepository
from apps.bot.database.repositories.media_repository import MediaRepository
from core.models import MediaFile

logger = logging.getLogger(__name__)


class MediaUploadResult(BaseModel):
    """Media upload result model"""
    file_id: str
    telegram_file_id: str
    storage_channel_id: int
    metadata: Dict[str, Any]


class MediaService:
    """Service for handling media operations"""
    
    def __init__(
        self,
        media_repository: MediaRepository,
        channel_repository: ChannelRepository,
    ):
        self.media_repository = media_repository
        self.channel_repository = channel_repository
        self.upload_progress = {}  # In-memory progress tracking
    
    async def upload_media(
        self,
        file: UploadFile,
        channel_id: int,
        user_id: UUID,
        direct_to_channel: bool = False,
        compress: bool = True,
    ) -> Dict[str, Any]:
        """
        Upload media file to Telegram with optional compression
        
        Args:
            file: The uploaded file
            channel_id: Target channel ID (0 for storage channel)
            direct_to_channel: Upload directly to channel vs storage
            compress: Apply compression if applicable
            user_id: User performing the upload
        """
        try:
            upload_id = str(uuid4())
            self.upload_progress[upload_id] = {
                "progress": 0,
                "status": "starting",
                "bytes_uploaded": 0,
                "total_bytes": 0,
            }
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Update progress
            self.upload_progress[upload_id].update({
                "total_bytes": file_size,
                "status": "processing",
                "progress": 10,
            })
            
            # Determine target channel
            target_channel_id = channel_id if direct_to_channel else await self._get_storage_channel_id()
            
            # Apply compression if needed
            processed_content = content
            compression_metadata = {}
            
            if compress and self._is_compressible(file.filename):
                self.upload_progress[upload_id]["status"] = "compressing"
                compressed_result = await self._compress_file(content, file.filename)
                processed_content = compressed_result["data"]
                compression_metadata = compressed_result["metadata"]
                self.upload_progress[upload_id]["progress"] = 30
            
            # Upload to Telegram
            self.upload_progress[upload_id]["status"] = "uploading"
            telegram_file_id = await self._upload_to_telegram(
                processed_content,
                file.filename,
                target_channel_id,
                upload_id,
            )
            
            # Generate file ID
            file_id = self._generate_file_id(file.filename, content)
            
            # Store metadata in database
            media_record = await self.media_repository.create({
                "file_id": file_id,
                "file_name": file.filename,
                "file_size": len(processed_content),
                "file_type": mimetypes.guess_type(file.filename)[0],
                "telegram_file_id": telegram_file_id,
                "storage_channel_id": target_channel_id,
                "user_id": user_id,
                "metadata": {
                    "original_size": file_size,
                    "compression": compression_metadata,
                    "upload_id": upload_id,
                },
            })
            
            # Update progress to complete
            self.upload_progress[upload_id].update({
                "progress": 100,
                "status": "completed",
                "bytes_uploaded": len(processed_content),
            })
            
            return {
                "file_id": file_id,
                "telegram_file_id": telegram_file_id,
                "storage_channel_id": target_channel_id,
                "metadata": {
                    "original_size": file_size,
                    "processed_size": len(processed_content),
                    "compression_applied": compress and compression_metadata,
                    "compression_ratio": compression_metadata.get("compression_ratio", 1.0),
                },
            }
            
        except Exception as e:
            if upload_id in self.upload_progress:
                self.upload_progress[upload_id].update({
                    "status": "error",
                    "error": str(e),
                })
            logger.error(f"Media upload failed: {str(e)}")
            raise
    
    async def get_storage_files(
        self,
        channel_id: int,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Get files from storage channel"""
        try:
            # Get from database
            files = await self.media_repository.get_by_channel(
                channel_id=channel_id,
                limit=limit,
                offset=offset,
                user_id=user_id,
            )
            
            return [
                {
                    "id": file.id,
                    "file_name": file.file_name,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "telegram_file_id": file.telegram_file_id,
                    "storage_channel_id": file.storage_channel_id,
                    "created_at": file.created_at,
                    "metadata": file.metadata,
                }
                for file in files
            ]
            
        except Exception as e:
            logger.error(f"Failed to get storage files: {str(e)}")
            raise
    
    async def delete_storage_file(
        self,
        file_id: str,
        user_id: UUID,
    ) -> bool:
        """Delete file from storage"""
        try:
            # Get file record
            file_record = await self.media_repository.get_by_file_id(file_id)
            if not file_record or file_record.user_id != user_id:
                return False
            
            # Delete from Telegram (optional - files can remain in channel)
            # await self.telegram_client.delete_message(
            #     channel_id=file_record.storage_channel_id,
            #     message_id=file_record.telegram_message_id,
            # )
            
            # Delete from database
            await self.media_repository.delete(file_record.id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete storage file: {str(e)}")
            return False
    
    async def get_upload_progress(
        self,
        upload_id: str,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """Get upload progress"""
        progress = self.upload_progress.get(upload_id, {
            "progress": 0,
            "status": "not_found",
            "bytes_uploaded": 0,
            "total_bytes": 0,
        })
        
        # Calculate ETA
        if progress.get("bytes_uploaded", 0) > 0 and progress.get("progress", 0) > 0:
            bytes_remaining = progress["total_bytes"] - progress["bytes_uploaded"]
            if bytes_remaining > 0:
                # Simple ETA calculation (this could be improved)
                progress["estimated_time_remaining"] = bytes_remaining / 1024  # seconds estimate
        
        return progress
    
    async def compress_media(
        self,
        file: UploadFile,
        quality: int = 80,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compress media file"""
        try:
            content = await file.read()
            original_size = len(content)
            
            if not self._is_compressible(file.filename):
                return {
                    "original_size": original_size,
                    "compressed_size": original_size,
                    "compression_ratio": 1.0,
                    "file_data": content,
                    "mime_type": mimetypes.guess_type(file.filename)[0],
                }
            
            # Compress image
            compressed_result = await self._compress_file(
                content,
                file.filename,
                quality=quality,
                max_width=max_width,
                max_height=max_height,
            )
            
            return {
                "original_size": original_size,
                "compressed_size": len(compressed_result["data"]),
                "compression_ratio": len(compressed_result["data"]) / original_size,
                "file_data": compressed_result["data"],
                "mime_type": compressed_result["mime_type"],
            }
            
        except Exception as e:
            logger.error(f"Media compression failed: {str(e)}")
            raise
    
    # Private helper methods
    
    def _generate_file_id(self, filename: str, content: bytes) -> str:
        """Generate unique file ID"""
        hash_input = f"{filename}_{len(content)}_{datetime.utcnow().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _is_compressible(self, filename: str) -> bool:
        """Check if file type supports compression"""
        mime_type = mimetypes.guess_type(filename)[0]
        compressible_types = [
            "image/jpeg", "image/jpg", "image/png", "image/webp",
            "image/bmp", "image/tiff"
        ]
        return mime_type in compressible_types
    
    async def _get_storage_channel_id(self) -> int:
        """Get default storage channel ID"""
        # This should be configured in settings or database
        # For now, return a default value
        return -1001234567890  # Replace with actual storage channel
    
    async def _compress_file(
        self,
        content: bytes,
        filename: str,
        quality: int = 80,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Compress image file"""
        try:
            with Image.open(BytesIO(content)) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                
                # Resize if dimensions specified
                if max_width or max_height:
                    img.thumbnail((max_width or img.width, max_height or img.height), Image.Resampling.LANCZOS)
                
                # Apply auto-orientation
                img = ImageOps.exif_transpose(img)
                
                # Save compressed
                output = BytesIO()
                img_format = "JPEG"  # Default to JPEG for compression
                img.save(output, format=img_format, quality=quality, optimize=True)
                compressed_data = output.getvalue()
                
                return {
                    "data": compressed_data,
                    "mime_type": "image/jpeg",
                    "metadata": {
                        "compression_ratio": len(compressed_data) / len(content),
                        "quality": quality,
                        "original_format": img.format,
                        "final_format": img_format,
                        "dimensions": img.size,
                    },
                }
                
        except Exception as e:
            logger.error(f"Image compression failed: {str(e)}")
            # Return original if compression fails
            return {
                "data": content,
                "mime_type": mimetypes.guess_type(filename)[0],
                "metadata": {"compression_failed": str(e)},
            }
    
    async def _upload_to_telegram(
        self,
        content: bytes,
        filename: str,
        channel_id: int,
        upload_id: str,
    ) -> str:
        """Upload file to Telegram channel"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Upload via Telegram client
            # This is a placeholder - implement actual Telegram upload
            telegram_file_id = f"telegram_file_{upload_id}"
            
            # Update progress during upload
            for progress in range(40, 95, 10):
                await asyncio.sleep(0.1)  # Simulate upload time
                if upload_id in self.upload_progress:
                    self.upload_progress[upload_id]["progress"] = progress
                    self.upload_progress[upload_id]["bytes_uploaded"] = int(
                        (progress / 100) * len(content)
                    )
            
            return telegram_file_id
            
        except Exception as e:
            logger.error(f"Telegram upload failed: {str(e)}")
            raise
