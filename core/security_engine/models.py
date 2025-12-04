"""
🔒 Security Models - User Management & Authentication

Production-ready models for user authentication, roles, and sessions
with comprehensive security features and validation.

Updated for 4-Role Hierarchical System with backwards compatibility.
"""

import secrets
import uuid
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, Enum):
    """
    DEPRECATED: Legacy user role hierarchy - use ApplicationRole/AdministrativeRole instead.

    Migration mapping:
    - GUEST → ApplicationRole.VIEWER
    - USER → ApplicationRole.USER
    - READONLY → ApplicationRole.VIEWER + readonly_access permission
    - ANALYST → ApplicationRole.USER + view_analytics permission
    - MODERATOR → AdministrativeRole.MODERATOR
    - ADMIN → AdministrativeRole.ADMIN or OWNER
    """

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
    """Complete user model with security features - Updated for 4-Role System"""

    username: str
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str | None = None

    # Authentication
    hashed_password: str | None = None
    auth_provider: AuthProvider = AuthProvider.LOCAL
    provider_id: str | None = None

    # Role System - New hierarchical approach
    role: str = "user"  # Default to ApplicationRole.USER.value
    legacy_role: UserRole | None = None  # For backwards compatibility
    additional_permissions: list[str] = field(default_factory=list)  # Extra permissions
    migration_profile: str | None = None  # Migration profile for special cases

    # Security
    # Default to ACTIVE since we don't have email verification system yet
    # Telegram users are always active (verified by Telegram)
    # Local users are active when they have a password
    status: UserStatus = UserStatus.ACTIVE
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
        self._migrate_legacy_role()

    def _migrate_legacy_role(self) -> None:
        """Migrate legacy role to new system if needed"""
        if self.legacy_role and not self._is_new_role_system():
            # Import here to avoid circular imports
            from .roles import migrate_user_role

            new_role, additional_perms = migrate_user_role(self.legacy_role.value)
            self.role = new_role
            self.additional_permissions.extend(additional_perms)

            # Set migration profile for special cases
            if self.legacy_role == UserRole.READONLY:
                self.migration_profile = "readonly_user"
            elif self.legacy_role == UserRole.ANALYST:
                self.migration_profile = "analyst_user"

    def _is_new_role_system(self) -> bool:
        """Check if using new 5-role system values"""
        # Import here to avoid circular imports
        from .roles import AdministrativeRole, ApplicationRole

        new_role_values = [
            ApplicationRole.VIEWER.value,
            ApplicationRole.USER.value,
            AdministrativeRole.MODERATOR.value,
            AdministrativeRole.ADMIN.value,
            AdministrativeRole.OWNER.value,
        ]
        return self.role in new_role_values

    def get_permissions(self):
        """Get all permissions for this user"""
        # Import here to avoid circular imports
        from .role_hierarchy import role_hierarchy_service

        user_info = role_hierarchy_service.get_user_role_info(
            role=self.role,
            additional_permissions=self.additional_permissions,
            migration_profile=self.migration_profile,
        )
        return user_info.permissions

    def has_permission(self, permission) -> bool:
        """Check if user has a specific permission"""
        # Import here to avoid circular imports
        from .permissions import Permission

        if isinstance(permission, str):
            try:
                permission = Permission(permission)
            except ValueError:
                return False

        return permission in self.get_permissions()

    def is_administrative(self) -> bool:
        """Check if user has administrative role"""
        from .roles import is_administrative_role

        return is_administrative_role(self.role)

    def can_access_admin_panel(self) -> bool:
        """Check if user can access admin panel"""
        from .permissions import can_access_admin_features

        return can_access_admin_features(self.get_permissions())

    def validate_username(self) -> None:
        """Validate username format in __post_init__"""
        # Allow alphanumeric, underscores, hyphens, dots, and @ symbols (for email-style usernames)
        import re

        if not re.match(r"^[a-zA-Z0-9._@-]+$", self.username):
            raise ValueError(
                "Username can only contain letters, numbers, underscores, hyphens, dots, and @ symbols"
            )
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
        if not any(c.isupper() for c in self.password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in self.password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in self.password):
            raise ValueError("Password must contain at least one digit")


@dataclass
class TokenResponse:
    """JWT token response"""

    access_token: str
    expires_in: int
    user: "User"
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
    """
    DEPRECATED: Role-based permission matrix - use Permission system instead.

    Use the new Permission enum and role_hierarchy_service for permission checking.
    """

    role: str  # Changed from UserRole to string for new system compatibility
    permissions: dict[str, list[str]] = field(
        default_factory=lambda: {
            "analytics": [],
            "users": [],
            "settings": [],
            "reports": [],
            "api": [],
        }
    )

    def __post_init__(self):
        warnings.warn(
            "PermissionMatrix is deprecated. Use Permission enum and role_hierarchy_service instead.",
            DeprecationWarning,
            stacklevel=2,
        )
