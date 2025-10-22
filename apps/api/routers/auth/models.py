"""
Authentication Models

Shared Pydantic models for authentication endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request model"""

    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """User registration request model"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None


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
    email: str
    username: str
    full_name: str | None
    role: str
    status: str
    created_at: datetime
    last_login: datetime | None


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
