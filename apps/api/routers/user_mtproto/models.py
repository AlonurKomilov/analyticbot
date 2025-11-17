"""
User MTProto Models

Shared Pydantic models for user MTProto management endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field, validator


class MTProtoSetupRequest(BaseModel):
    """Initial MTProto setup with API credentials"""

    telegram_api_id: int = Field(..., description="Telegram API ID from my.telegram.org", gt=0)
    telegram_api_hash: str = Field(
        ..., description="Telegram API Hash from my.telegram.org", min_length=32
    )
    telegram_phone: str = Field(..., description="Phone number with country code")

    @validator("telegram_phone")
    def validate_phone(cls, v):
        # Basic validation
        if not v.startswith("+"):
            raise ValueError("Phone must start with +")
        if len(v) < 10:
            raise ValueError("Phone number too short")
        # Remove spaces and dashes for validation
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) < 10:
            raise ValueError("Phone must contain at least 10 digits")
        return v


class MTProtoVerifyRequest(BaseModel):
    """Verification code from Telegram"""

    verification_code: str = Field(
        ..., description="Code received via Telegram", min_length=5, max_length=6
    )
    phone_code_hash: str = Field(..., description="Hash from initial request")
    password: str | None = Field(None, description="2FA password if enabled")


class MTProtoStatusResponse(BaseModel):
    """Current MTProto configuration status"""

    configured: bool
    verified: bool
    phone: str | None = None  # Masked
    api_id: int | None = None
    connected: bool = False  # True if session ready (exists in DB)
    actively_connected: bool = False  # True if client in active pool
    last_used: datetime | None = None
    can_read_history: bool = False
    mtproto_enabled: bool = True  # New field for toggle state


class MTProtoSetupResponse(BaseModel):
    """Response after initiating setup"""

    success: bool
    phone_code_hash: str
    message: str


class MTProtoActionResponse(BaseModel):
    """Generic success response"""

    success: bool
    message: str


class MTProtoToggleRequest(BaseModel):
    """Toggle MTProto functionality"""

    enabled: bool = Field(..., description="Enable or disable MTProto functionality")


class ChannelMTProtoSettingResponse(BaseModel):
    """Per-channel MTProto setting"""

    channel_id: int
    mtproto_enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ChannelMTProtoSettingsListResponse(BaseModel):
    """List of all channel MTProto settings"""

    global_enabled: bool
    settings: list[ChannelMTProtoSettingResponse]


class ErrorResponse(BaseModel):
    """Error response"""

    detail: str
