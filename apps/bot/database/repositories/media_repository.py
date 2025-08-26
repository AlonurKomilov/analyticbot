"""
Media Repository - Database operations for media files

Handles CRUD operations for media files stored in the database.
Uses SQLAlchemy Core (not ORM) to match the project's architecture.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.bot.database.models import media_files
from core.models import MediaFile

logger = logging.getLogger(__name__)


class MediaRepository:
    """Repository for media file operations"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, media_data: Dict[str, Any]) -> MediaFile:
        """Create new media file record"""
        try:
            stmt = insert(media_files).values(
                file_id=media_data["file_id"],
                file_name=media_data["file_name"],
                file_size=media_data["file_size"],
                file_type=media_data["file_type"],
                telegram_file_id=media_data["telegram_file_id"],
                storage_channel_id=media_data["storage_channel_id"],
                user_id=media_data["user_id"],
                metadata=media_data.get("metadata", {}),
                created_at=datetime.utcnow(),
                is_active=True,
            )
            
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            
            # Get the created record
            media_file = await self.get_by_file_id(media_data["file_id"])
            
            logger.info(f"Created media file record: {media_data['file_id']}")
            return media_file
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to create media file: {str(e)}")
            raise
    
    async def get_by_file_id(self, file_id: str) -> Optional[MediaFile]:
        """Get media file by file ID"""
        try:
            stmt = select(media_files).where(
                and_(
                    media_files.c.file_id == file_id,
                    media_files.c.is_active == True
                )
            )
            result = await self.db_session.execute(stmt)
            row = result.first()
            
            if row:
                return MediaFile(
                    id=row.id,
                    file_id=row.file_id,
                    file_name=row.file_name,
                    file_size=row.file_size,
                    file_type=row.file_type,
                    telegram_file_id=row.telegram_file_id,
                    storage_channel_id=row.storage_channel_id,
                    user_id=row.user_id,
                    metadata=row.metadata or {},
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    is_active=row.is_active,
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to get media file by ID {file_id}: {str(e)}")
            return None
    
    async def get_by_channel(
        self,
        channel_id: int,
        user_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MediaFile]:
        """Get media files by channel"""
        try:
            conditions = [
                media_files.c.storage_channel_id == channel_id,
                media_files.c.is_active == True,
            ]
            
            if user_id:
                conditions.append(media_files.c.user_id == user_id)
            
            stmt = (
                select(media_files)
                .where(and_(*conditions))
                .order_by(desc(media_files.c.created_at))
                .offset(offset)
                .limit(limit)
            )
            
            result = await self.db_session.execute(stmt)
            rows = result.fetchall()
            
            return [
                MediaFile(
                    id=row.id,
                    file_id=row.file_id,
                    file_name=row.file_name,
                    file_size=row.file_size,
                    file_type=row.file_type,
                    telegram_file_id=row.telegram_file_id,
                    storage_channel_id=row.storage_channel_id,
                    user_id=row.user_id,
                    metadata=row.metadata or {},
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    is_active=row.is_active,
                )
                for row in rows
            ]
            
        except Exception as e:
            logger.error(f"Failed to get media files for channel {channel_id}: {str(e)}")
            return []
    
    async def delete(self, media_file_id: int) -> bool:
        """Soft delete media file"""
        try:
            stmt = (
                update(media_files)
                .where(media_files.c.id == media_file_id)
                .values(is_active=False, updated_at=datetime.utcnow())
            )
            
            result = await self.db_session.execute(stmt)
            await self.db_session.commit()
            
            if result.rowcount > 0:
                logger.info(f"Deleted media file: {media_file_id}")
                return True
            return False
            
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Failed to delete media file {media_file_id}: {str(e)}")
            return False
