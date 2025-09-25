"""
Authentication API Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response schema"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    status: str
    created_at: datetime
    last_login: Optional[datetime]


class RegisterResponse(BaseModel):
    """Registration response schema"""
    message: str
    user_id: int
    email: str
    requires_verification: bool = True


class VerifyEmailRequest(BaseModel):
    """Email verification request schema"""
    token: str


class VerifyEmailResponse(BaseModel):
    """Email verification response schema"""
    message: str
    user_id: int
    verified: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None