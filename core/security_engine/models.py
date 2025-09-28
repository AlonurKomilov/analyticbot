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
from dataclasses import dataclass, field

from passlib.context import CryptContext

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


@dataclass
class User:
    """Complete user model with security features"""

    username: str
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
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
    created_at: datetime = field(default_factory=datetime.utcnow)
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

    def __post_init__(self):
        """Initialize and validate user data"""
        self.validate_username()

    def validate_username(self) -> None:
        """Validate username format in __post_init__"""
        if not self.username.isalnum() and "_" not in self.username and "-" not in self.username:
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
        self.username = self.username.lower()

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


@dataclass
class UserSession:
    """User session model with security tracking"""

    user_id: str
    token: str
    expires_at: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    refresh_token: str | None = None

    # Session info
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

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


@dataclass
class LoginRequest:
    """Login request model"""

    email: str
    password: str
    remember_me: bool = False
    mfa_code: str | None = None


@dataclass
class RegisterRequest:
    """User registration request"""

    email: str
    username: str
    password: str
    full_name: str | None = None

    def __post_init__(self):
        """Validate password strength"""
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


@dataclass
class TokenResponse:
    """JWT token response"""

    access_token: str
    expires_in: int
    user: 'User'
    refresh_token: str | None = None
    token_type: str = "bearer"


@dataclass
class MFASetupResponse:
    """MFA setup response with QR code"""

    secret: str
    qr_code: str
    backup_codes: list[str]


@dataclass  
class PermissionMatrix:
    """Role-based permission matrix"""

    role: UserRole
    permissions: dict[str, list[str]] = field(default_factory=lambda: {
        "analytics": [],
        "users": [],
        "settings": [],
        "reports": [],
        "api": [],
    })
