"""
Pydantic models for Channels API

Request/response models for channel management endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ChannelListResponse(BaseModel):
    """Channel list item response"""

    id: int
    name: str
    username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_updated: datetime | None = None  # Optional - not all channels have this field
    bot_is_admin: bool | None = None  # Bot admin status
    mtproto_is_admin: bool | None = None  # MTProto admin status
    admin_status_message: str | None = None  # Helpful message for users


class ChannelResponse(BaseModel):
    """Full channel details response"""

    id: int
    name: str
    username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_updated: datetime | None = None  # Optional - not all channels have this field
    settings: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class AddChannelRequest(BaseModel):
    """Request model for adding a channel to analytics"""

    name: str
    telegram_id: int | None = None
    username: str | None = None
    description: str = ""
    subscriber_count: int = 0
    is_active: bool = True
    settings: dict[str, Any] | None = None


class ChannelUpdateRequest(BaseModel):
    """Request model for updating channel"""

    name: str | None = None
    username: str | None = None
    is_active: bool | None = None
    settings: dict[str, Any] | None = None


class ValidateChannelRequest(BaseModel):
    """Request model for channel validation"""

    username: str


class ChannelLookupResponse(BaseModel):
    """Response model for channel lookup - auto-fetched from Telegram"""

    is_valid: bool
    telegram_id: int | None = None
    username: str | None = None
    title: str | None = None  # Channel name from Telegram
    subscriber_count: int | None = None
    description: str | None = None
    telegram_created_at: str | None = None
    is_verified: bool = False
    is_scam: bool = False
    is_admin: bool | None = None  # Whether bot has admin access
    error_message: str | None = None
