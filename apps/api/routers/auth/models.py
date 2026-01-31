"""
Authentication Models

Shared Pydantic models for authentication endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Login request model

    🆕 Phase 3.2: Added remember_me parameter
    """

    email: EmailStr
    password: str = Field(..., min_length=8)
    remember_me: bool = Field(default=False, description="Keep user logged in for 30 days")


class RegisterRequest(BaseModel):
    """User registration request model"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None  # Legacy field
    first_name: str | None = None
    last_name: str | None = None

    def get_full_name(self) -> str | None:
        """Get full name, combining first_name and last_name if full_name not provided"""
        if self.full_name:
            return self.full_name
        if self.first_name or self.last_name:
            parts = [p for p in [self.first_name, self.last_name] if p]
            return " ".join(parts) if parts else None
        return None


class AuthResponse(BaseModel):
    """Authentication response model"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict[str, Any]


class UserResponse(BaseModel):
    """User response model"""

    id: str
    email: str | None = None  # Optional for Telegram-only users
    username: str | None = None  # Optional
    full_name: str | None = None
    first_name: str | None = None  # Split name field
    last_name: str | None = None  # Split name field
    role: str
    status: str
    created_at: datetime
    last_login: datetime | None
    # Login method indicators
    has_password: bool = False  # True if user can login with email/password
    telegram_id: int | None = None  # Telegram user ID if linked
    telegram_username: str | None = None  # Telegram username if linked
    # Credit system
    credit_balance: float = 0.0  # User's current credit balance
    # Profile photo
    photo_url: str | None = None  # User's profile photo URL


class PasswordResetRequest(BaseModel):
    """Password reset request model"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model"""

    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChangeRequest(BaseModel):
    """Password change request model"""

    current_password: str
    new_password: str = Field(..., min_length=8)


class TelegramVerifyRequest(BaseModel):
    """Telegram verification request model"""

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
