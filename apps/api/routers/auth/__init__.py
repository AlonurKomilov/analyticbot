"""
Authentication package - modular auth endpoints.

This package provides authentication, registration, password management,
and user profile functionality split into separate domain modules.
"""

from .router import router
from .models import (
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    TelegramVerifyRequest,
)

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
