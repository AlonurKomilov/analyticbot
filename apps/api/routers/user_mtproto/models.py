"""
User MTProto Models

Shared Pydantic models for user MTProto management endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field, validator


class MTProtoSetupRequest(BaseModel):
    """Initial MTProto setup with API credentials"""

    mtproto_api_id: int = Field(..., description="MTProto API ID from my.telegram.org", gt=0)
    telegram_api_hash: str = Field(
        ..., description="Telegram API Hash from my.telegram.org", min_length=32
    )
    mtproto_phone: str = Field(..., description="Phone number with country code")


class MTProtoSimpleSetupRequest(BaseModel):
    """Simplified MTProto setup - only requires phone number"""

    mtproto_phone: str = Field(..., description="Phone number with country code (e.g., +1234567890)")

    @validator("mtproto_phone")
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


class MTProtoQRLoginResponse(BaseModel):
    """Response containing QR code data for login"""

    success: bool
    qr_code_url: str = Field(..., description="URL to encode in QR code (tg://login?token=...)")
    qr_code_base64: str | None = Field(None, description="Base64 encoded QR code image")
    expires_in: int = Field(..., description="Seconds until QR code expires")
    message: str


class MTProtoQRStatusResponse(BaseModel):
    """Status of QR login attempt"""

    status: str = Field(..., description="pending, success, expired, 2fa_required, or error")
    success: bool = False
    message: str
    user_id: int | None = None  # Telegram user ID if successful
    needs_2fa: bool = False  # True if 2FA password is needed


class MTProtoQR2FARequest(BaseModel):
    """2FA password for QR login"""

    password: str = Field(..., description="2FA password")


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
