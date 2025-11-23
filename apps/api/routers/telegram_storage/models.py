"""
Pydantic models for Telegram Storage API

Request/response models for storage channel and file management endpoints.
"""

from pydantic import BaseModel, Field

# ============================================================================
# Channel Models
# ============================================================================


class StorageChannelCreate(BaseModel):
    """Request to connect a new storage channel"""

    channel_id: int = Field(..., description="Telegram channel ID (e.g., -1001234567890)")
    channel_username: str | None = Field(None, description="Channel username if public")

    class Config:
        json_schema_extra = {
            "example": {"channel_id": -1001234567890, "channel_username": "my_storage_channel"}
        }


class StorageChannelResponse(BaseModel):
    """Storage channel information"""

    id: int
    user_id: int
    channel_id: int
    channel_title: str
    channel_username: str | None
    is_active: bool
    is_bot_admin: bool
    created_at: str
    last_validated_at: str | None

    class Config:
        from_attributes = True


class ChannelValidationResponse(BaseModel):
    """Channel validation result"""

    is_valid: bool
    channel_id: int
    channel_title: str
    channel_username: str | None
    member_count: int = 0  # Default to 0 if unavailable
    bot_is_admin: bool
    message: str


# ============================================================================
# File Models
# ============================================================================


class TelegramMediaResponse(BaseModel):
    """Telegram media file information"""

    id: int
    user_id: int
    storage_channel_id: int
    telegram_file_id: str
    telegram_message_id: int
    file_type: str
    file_name: str
    file_size: int
    file_size_formatted: str
    mime_type: str | None
    width: int | None
    height: int | None
    duration: int | None
    caption: str | None
    preview_url: str | None
    uploaded_at: str

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response for successful file upload"""

    success: bool
    media: TelegramMediaResponse
    message: str


class FilesListResponse(BaseModel):
    """Paginated list of files"""

    files: list[TelegramMediaResponse]
    total: int
    limit: int
    offset: int
