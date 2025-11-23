"""
Pydantic schemas for User Bot API endpoints.

This module defines request and response models for user bot management endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from core.models.user_bot_domain import BotStatus

# ==================== Request Models ====================


class CreateBotRequest(BaseModel):
    """Request model for creating a new user bot."""

    bot_token: str = Field(..., description="Telegram bot token from @BotFather")
    bot_username: str | None = Field(None, description="Bot username (optional, will be fetched)")
    api_id: int | None = Field(None, description="Telegram API ID (optional, for MTProto)")
    api_hash: str | None = Field(None, description="Telegram API Hash (optional, for MTProto)")
    max_requests_per_second: int = Field(30, ge=1, le=100, description="Max RPS for rate limiting")
    max_concurrent_requests: int = Field(10, ge=1, le=50, description="Max concurrent requests")

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate bot token format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Bot token cannot be empty")

        # Basic format check: should contain ':' and be alphanumeric
        if ":" not in v:
            raise ValueError("Invalid bot token format (missing ':')")

        parts = v.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid bot token format")

        return v.strip()

    @field_validator("bot_username")
    @classmethod
    def validate_bot_username(cls, v: str | None) -> str | None:
        """Validate bot username format."""
        if v is None:
            return v

        v = v.strip()
        if len(v) == 0:
            return None

        # Remove @ if present
        if v.startswith("@"):
            v = v[1:]

        # Must be alphanumeric with underscores
        if not v.replace("_", "").isalnum():
            raise ValueError("Bot username must be alphanumeric with underscores")

        return v


class VerifyBotRequest(BaseModel):
    """Request model for verifying bot credentials."""

    send_test_message: bool = Field(False, description="Send a test message to verify bot works")
    test_chat_id: int | None = Field(None, description="Chat ID to send test message to")
    test_message: str | None = Field(None, description="Custom test message to send")


class UpdateRateLimitRequest(BaseModel):
    """Request model for updating rate limits."""

    max_requests_per_second: int | None = Field(None, ge=1, le=100, description="Max RPS")
    max_concurrent_requests: int | None = Field(None, ge=1, le=50, description="Max concurrent")


class SuspendBotRequest(BaseModel):
    """Request model for suspending a bot."""

    reason: str = Field(..., description="Reason for suspension")

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Validate suspension reason."""
        if not v or len(v.strip()) < 5:
            raise ValueError("Suspension reason must be at least 5 characters")
        return v.strip()


# ==================== Response Models ====================


class BotStatusResponse(BaseModel):
    """Response model for bot status."""

    id: int
    user_id: int
    bot_username: str | None
    bot_id: int | None
    status: BotStatus
    is_verified: bool
    max_requests_per_second: int
    max_concurrent_requests: int
    total_requests: int
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime
    suspension_reason: str | None = None

    class Config:
        from_attributes = True


class BotCreatedResponse(BaseModel):
    """Response model for successful bot creation."""

    id: int
    message: str = "Bot created successfully"
    status: BotStatus
    bot_username: str | None
    requires_verification: bool = True
    webhook_enabled: bool = False
    webhook_url: str | None = None


class BotVerificationResponse(BaseModel):
    """Response model for bot verification."""

    success: bool
    message: str
    bot_info: dict[str, Any] | None = None
    is_verified: bool


class BotRemovedResponse(BaseModel):
    """Response model for bot removal."""

    success: bool = True
    message: str = "Bot removed successfully"


class BotListResponse(BaseModel):
    """Response model for listing bots (admin)."""

    total: int
    page: int
    page_size: int
    bots: list[BotStatusResponse]


class AdminAccessResponse(BaseModel):
    """Response model for admin accessing a user bot."""

    success: bool
    message: str
    bot_info: dict[str, Any] | None = None
    access_logged: bool = True


class RateLimitUpdateResponse(BaseModel):
    """Response model for rate limit updates."""

    success: bool = True
    message: str = "Rate limits updated successfully"
    new_limits: dict[str, int]


# ==================== Error Response ====================


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str
    detail: str | None = None
    code: str | None = None
