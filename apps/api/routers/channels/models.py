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


class ChannelCreateRequest(BaseModel):
    """Request model for creating a channel"""

    name: str
    username: str | None = None
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
