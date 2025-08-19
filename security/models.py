"""
🔒 Security Models - User Management & Authentication

Production-ready models for user authentication, roles, and sessions
with comprehensive security features and validation.
"""

import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, Enum):
    """User role hierarchy with permissions"""

    ADMIN = "admin"
    MODERATOR = "moderator"
    ANALYST = "analyst"
    USER = "user"
    READONLY = "readonly"
    GUEST = "guest"


class UserStatus(str, Enum):
    """User account status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    BLOCKED = "blocked"


class AuthProvider(str, Enum):
    """Authentication providers"""

    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    TELEGRAM = "telegram"


class User(BaseModel):
    """Complete user model with security features"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str | None = None

    # Authentication
    hashed_password: str | None = None
    auth_provider: AuthProvider = AuthProvider.LOCAL
    provider_id: str | None = None

    # Security
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    is_mfa_enabled: bool = False
    mfa_secret: str | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = None
    last_password_change: datetime | None = None
    email_verified_at: datetime | None = None

    # Security tracking
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    password_reset_token: str | None = None
    email_verification_token: str | None = None

    # Profile
    avatar_url: str | None = None
    timezone: str = "UTC"
    language: str = "en"

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not v.isalnum() and "_" not in v and "-" not in v:
            raise ValueError(
                "Username can only contain letters, numbers, underscores, and hyphens"
            )
        return v.lower()

    def set_password(self, password: str) -> None:
        """Hash and set user password"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self.hashed_password = pwd_context.hash(password)
        self.last_password_change = datetime.utcnow()

    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)

    def is_account_locked(self) -> bool:
        """Check if account is locked due to failed attempts"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def lock_account(self, minutes: int = 30) -> None:
        """Lock account for specified minutes"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.failed_login_attempts += 1

    def unlock_account(self) -> None:
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0

    def generate_verification_token(self) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        return token

    def generate_password_reset_token(self) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        return token


class UserSession(BaseModel):
    """User session model with security tracking"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    refresh_token: str | None = None

    # Session info
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)

    # Security tracking
    ip_address: str | None = None
    user_agent: str | None = None
    device_info: dict[str, Any] | None = None
    location: str | None = None

    # Session flags
    is_active: bool = True
    is_mfa_verified: bool = False
    logout_at: datetime | None = None

    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at

    def extend_session(self, hours: int = 24) -> None:
        """Extend session expiration"""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity = datetime.utcnow()

    def terminate_session(self) -> None:
        """Terminate session"""
        self.is_active = False
        self.logout_at = datetime.utcnow()


class LoginRequest(BaseModel):
    """Login request model"""

    email: EmailStr
    password: str
    remember_me: bool = False
    mfa_code: str | None = None


class RegisterRequest(BaseModel):
    """User registration request"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class TokenResponse(BaseModel):
    """JWT token response"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int
    user: User


class MFASetupResponse(BaseModel):
    """MFA setup response with QR code"""

    secret: str
    qr_code: str
    backup_codes: list[str]


class PermissionMatrix(BaseModel):
    """Role-based permission matrix"""

    role: UserRole
    permissions: dict[str, list[str]] = {
        "analytics": [],
        "users": [],
        "settings": [],
        "reports": [],
        "api": [],
    }

    class Config:
        class Config:
            json_schema_extra = {
                "example": {
                    "role": "analyst",
                    "permissions": {
                        "analytics": ["read", "create", "update"],
                        "users": ["read"],
                        "settings": ["read"],
                        "reports": ["read", "create", "update"],
                        "api": ["read", "write"],
                    },
                }
            }
