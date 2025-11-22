"""
Database models for Telegram storage system.

These models track user-owned Telegram channels used for file storage
and metadata for files stored in those channels.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from infra.db.models.base import Base


class UserStorageChannel(Base):
    """
    User's Telegram channel used for file storage.

    Each user can connect one or more private Telegram channels
    where their files will be uploaded and stored.
    """

    __tablename__ = "user_storage_channels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Telegram channel info
    channel_id = Column(BigInteger, nullable=False)  # Telegram channel ID (e.g., -1001234567890)
    channel_title = Column(String(255), nullable=False)
    channel_username = Column(String(255), nullable=True)  # @username if public

    # Status flags
    is_active = Column(Boolean, default=True, nullable=False)
    is_bot_admin = Column(Boolean, default=True, nullable=False)  # Bot has admin rights

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_validated_at = Column(DateTime, nullable=True)  # Last time bot verified access

    # Relationships
    # TODO: Re-enable when User model is migrated to use common Base
    # user = relationship("User", back_populates="storage_channels")
    media_files = relationship(
        "TelegramMedia", back_populates="storage_channel", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_storage_channels_user_id", "user_id"),
        Index("idx_user_storage_channels_channel_id", "channel_id"),
        Index(
            "idx_user_storage_channels_user_channel",
            "user_id",
            "channel_id",
            unique=True,
        ),
    )

    def __repr__(self):
        return f"<UserStorageChannel(id={self.id}, user_id={self.user_id}, channel={self.channel_title})>"


class TelegramMedia(Base):
    """
    Metadata for files stored in Telegram channels.

    Instead of storing files on the server, files are uploaded to user's
    Telegram storage channel. This table stores the Telegram file IDs
    and metadata needed to retrieve the files.
    """

    __tablename__ = "telegram_media"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    storage_channel_id = Column(
        Integer,
        ForeignKey("user_storage_channels.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Telegram file identifiers
    telegram_file_id = Column(String(255), nullable=False)  # Telegram's file_id
    telegram_unique_file_id = Column(
        String(255), nullable=True
    )  # Unique identifier for deduplication
    telegram_message_id = Column(Integer, nullable=False)  # Message ID in the storage channel

    # File metadata
    file_type = Column(String(50), nullable=False)  # photo, video, document, audio
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=True)

    # Media-specific attributes
    thumbnail_file_id = Column(String(255), nullable=True)
    width = Column(Integer, nullable=True)  # For images/videos
    height = Column(Integer, nullable=True)  # For images/videos
    duration = Column(Integer, nullable=True)  # For videos/audio in seconds

    # Content
    caption = Column(Text, nullable=True)
    preview_url = Column(String(500), nullable=True)  # CDN URL if available

    # Status
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Additional metadata (flexible JSON field) - renamed to avoid SQLAlchemy reserved word conflict
    file_metadata = Column("metadata", JSON, nullable=True, default={})

    # Relationships
    # TODO: Re-enable when User model is migrated to use common Base
    # user = relationship("User", back_populates="telegram_media")
    storage_channel = relationship("UserStorageChannel", back_populates="media_files")

    # Indexes
    __table_args__ = (
        Index("idx_telegram_media_user_id", "user_id"),
        Index("idx_telegram_media_storage_channel_id", "storage_channel_id"),
        Index("idx_telegram_media_file_type", "file_type"),
        Index("idx_telegram_media_uploaded_at", "uploaded_at"),
        Index("idx_telegram_media_telegram_file_id", "telegram_file_id"),
        Index("idx_telegram_media_unique_file_id", "telegram_unique_file_id"),
    )

    def __repr__(self):
        return f"<TelegramMedia(id={self.id}, file_name={self.file_name}, type={self.file_type})>"

    @property
    def size_mb(self) -> float:
        """File size in megabytes"""
        return self.file_size / (1024 * 1024) if self.file_size else 0.0

    @property
    def size_formatted(self) -> str:
        """Human-readable file size"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
