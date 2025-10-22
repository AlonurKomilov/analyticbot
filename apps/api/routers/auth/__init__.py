"""
Authentication package - modular auth endpoints.

This package provides authentication, registration, password management,
and user profile functionality split into separate domain modules.
"""

from .models import (
    AuthResponse,
    LoginRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TelegramVerifyRequest,
    UserResponse,
)
from .router import router

__all__ = [
    "router",
    "LoginRequest",
    "RegisterRequest",
    "AuthResponse",
    "UserResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "TelegramVerifyRequest",
]
