"""
MTProto Domain Models - Data transfer objects for MTProto functionality.

These models represent domain concepts without depending on ORM or infrastructure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AuditActionType(str, Enum):
    """Types of audit actions."""

    SETUP_MTPROTO = "setup_mtproto"
    UPDATE_MTPROTO = "update_mtproto"
    DELETE_MTPROTO = "delete_mtproto"
    VERIFY_PHONE = "verify_phone"
    CREATE_CHANNEL = "create_channel"
    UPDATE_CHANNEL = "update_channel"
    DELETE_CHANNEL = "delete_channel"
    SYNC_CHANNEL = "sync_channel"
    EXPORT_DATA = "export_data"


@dataclass
class MTProtoAuditLogDTO:
    """MTProto audit log entry."""

    id: int | None = None
    user_id: int = 0
    action: str = ""
    channel_id: int | None = None
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ip_address: str | None = None
    user_agent: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MTProtoAuditLogDTO":
        """Create DTO from dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", 0),
            action=data.get("action", ""),
            channel_id=data.get("channel_id"),
            details=data.get("details", {}),
            timestamp=data.get("timestamp", datetime.utcnow()),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "channel_id": self.channel_id,
            "details": self.details,
            "timestamp": self.timestamp,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }


@dataclass
class TelegramMediaDTO:
    """Telegram media metadata."""

    id: int | None = None
    channel_id: int = 0
    message_id: int = 0
    media_type: str = ""  # photo, video, document, etc.
    file_id: str = ""
    file_unique_id: str = ""
    file_size: int | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None
    thumbnail_path: str | None = None
    file_path: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TelegramMediaDTO":
        """Create DTO from dictionary."""
        return cls(
            id=data.get("id"),
            channel_id=data.get("channel_id", 0),
            message_id=data.get("message_id", 0),
            media_type=data.get("media_type", ""),
            file_id=data.get("file_id", ""),
            file_unique_id=data.get("file_unique_id", ""),
            file_size=data.get("file_size"),
            mime_type=data.get("mime_type"),
            width=data.get("width"),
            height=data.get("height"),
            duration=data.get("duration"),
            thumbnail_path=data.get("thumbnail_path"),
            file_path=data.get("file_path"),
            created_at=data.get("created_at", datetime.utcnow()),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "media_type": self.media_type,
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "thumbnail_path": self.thumbnail_path,
            "file_path": self.file_path,
            "created_at": self.created_at,
        }


@dataclass
class UserStorageChannelDTO:
    """User storage channel configuration."""

    id: int | None = None
    user_id: int = 0
    channel_id: int = 0
    channel_username: str | None = None
    channel_title: str = ""
    is_active: bool = True
    storage_quota_mb: int = 1000  # Default 1GB
    used_storage_mb: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserStorageChannelDTO":
        """Create DTO from dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", 0),
            channel_id=data.get("channel_id", 0),
            channel_username=data.get("channel_username"),
            channel_title=data.get("channel_title", ""),
            is_active=data.get("is_active", True),
            storage_quota_mb=data.get("storage_quota_mb", 1000),
            used_storage_mb=data.get("used_storage_mb", 0.0),
            created_at=data.get("created_at", datetime.utcnow()),
            updated_at=data.get("updated_at", datetime.utcnow()),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert DTO to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel_id": self.channel_id,
            "channel_username": self.channel_username,
            "channel_title": self.channel_title,
            "is_active": self.is_active,
            "storage_quota_mb": self.storage_quota_mb,
            "used_storage_mb": self.used_storage_mb,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
