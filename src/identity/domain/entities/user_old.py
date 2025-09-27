"""
User Entity - Core identity domain entity
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from passlib.context import CryptContext

from src.shared_kernel.domain.base_entity import AggregateRoot
from src.shared_kernel.domain.exceptions import (
    BusinessRuleViolationError,
    ValidationError,
)
from src.shared_kernel.domain.value_objects import EmailAddress, UserId, Username

from .events import UserLoggedIn, UserPasswordChanged, UserRegistered, UserStatusChanged

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
class User(AggregateRoot):
    """
    User aggregate root - Core identity entity

    This represents a user in the system with all authentication,
    authorization, and profile management capabilities.
    """

    # Identity (required first due to inheritance)
    id: UserId
    email: EmailAddress
    username: Username

    # Profile
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

    # Security tracking
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    last_login: datetime | None = None
    last_password_change: datetime | None = None
    email_verified_at: datetime | None = None

    # Tokens
    password_reset_token: str | None = None
    email_verification_token: str | None = None

    # Profile
    avatar_url: str | None = None
    timezone: str = "UTC"
    language: str = "en"

    def __post_init__(self):
        """Post-initialization validation"""
        super().__post_init__()
        self._validate_user_data()

    def _validate_user_data(self) -> None:
        """Validate user data consistency"""
        if self.auth_provider == AuthProvider.LOCAL and not self.hashed_password:
            raise ValidationError("Local auth users must have a password")

    @classmethod
    def create_new_user(
        cls,
        user_id: UserId,
        email: EmailAddress,
        username: Username,
        password: str | None = None,
        full_name: str | None = None,
        auth_provider: AuthProvider = AuthProvider.LOCAL,
    ) -> "User":
        """
        Factory method to create a new user
        """
        user = cls(
            id=user_id,
            email=email,
            username=username,
            full_name=full_name,
            auth_provider=auth_provider,
            status=(
                UserStatus.PENDING_VERIFICATION
                if auth_provider == AuthProvider.LOCAL
                else UserStatus.ACTIVE
            ),
        )

        if password and auth_provider == AuthProvider.LOCAL:
            user.set_password(password)

        # Emit domain event
        user.add_domain_event(
            UserRegistered(
                user_id=user_id.value,
                email=str(email),
                username=str(username),
                auth_provider=auth_provider.value,
            )
        )

        return user

    def set_password(self, password: str) -> None:
        """
        Set and hash user password with validation

        Business Rules:
        - Password must be at least 8 characters long
        - Must contain uppercase, lowercase, digit, and special character
        """
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        if not any(c.isupper() for c in password):
            raise ValidationError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            raise ValidationError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit")

        self.hashed_password = pwd_context.hash(password)
        self.last_password_change = datetime.utcnow()
        self.mark_as_updated()

        # Emit domain event
        self.add_domain_event(
            UserPasswordChanged(user_id=self.id.value, changed_at=self.last_password_change)
        )

    def verify_password(self, password: str) -> bool:
        """Verify user password"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)

    def login(self, ip_address: str | None = None) -> None:
        """
        Record successful login

        Business Rules:
        - Account must not be locked
        - Account must be active
        - Reset failed login attempts on successful login
        """
        if self.is_account_locked():
            raise BusinessRuleViolationError("Account is locked due to failed login attempts")

        if self.status not in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION]:
            raise BusinessRuleViolationError(f"Cannot login with status: {self.status}")

        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
        self.mark_as_updated()

        # Emit domain event
        self.add_domain_event(
            UserLoggedIn(user_id=self.id.value, login_time=self.last_login, ip_address=ip_address)
        )

    def record_failed_login(self, max_attempts: int = 5) -> None:
        """
        Record failed login attempt

        Business Rules:
        - Lock account after max failed attempts
        - Increase lockout duration with repeated failures
        """
        self.failed_login_attempts += 1

        if self.failed_login_attempts >= max_attempts:
            # Progressive lockout: 30 min, 1 hour, 2 hours, etc.
            lockout_minutes = min(30 * (2 ** (self.failed_login_attempts - max_attempts)), 1440)
            self.lock_account(lockout_minutes)

        self.mark_as_updated()

    def is_account_locked(self) -> bool:
        """Check if account is locked due to failed attempts"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def lock_account(self, minutes: int = 30) -> None:
        """Lock account for specified minutes"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        self.mark_as_updated()

    def unlock_account(self) -> None:
        """Unlock account and reset failed attempts"""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.mark_as_updated()

    def change_status(self, new_status: UserStatus) -> None:
        """
        Change user status

        Business Rules:
        - Certain status transitions are not allowed
        - Status changes should be tracked
        """
        if self.status == new_status:
            return

        old_status = self.status
        self.status = new_status
        self.mark_as_updated()

        # Emit domain event
        self.add_domain_event(
            UserStatusChanged(
                user_id=self.id.value,
                old_status=old_status.value,
                new_status=new_status.value,
            )
        )

    def activate_account(self) -> None:
        """Activate user account"""
        if self.status != UserStatus.PENDING_VERIFICATION:
            raise BusinessRuleViolationError("Can only activate accounts pending verification")

        self.change_status(UserStatus.ACTIVE)
        self.email_verified_at = datetime.utcnow()

    def suspend_account(self) -> None:
        """Suspend user account"""
        if self.status == UserStatus.BLOCKED:
            raise BusinessRuleViolationError("Cannot suspend a blocked account")

        self.change_status(UserStatus.SUSPENDED)

    def generate_verification_token(self) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.mark_as_updated()
        return token

    def generate_password_reset_token(self) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.mark_as_updated()
        return token

    def verify_email_token(self, token: str) -> bool:
        """Verify email verification token"""
        return self.email_verification_token == token if self.email_verification_token else False

    def verify_reset_token(self, token: str) -> bool:
        """Verify password reset token"""
        return self.password_reset_token == token if self.password_reset_token else False

    def consume_reset_token(self) -> None:
        """Consume password reset token (mark as used)"""
        self.password_reset_token = None
        self.mark_as_updated()

    def update_profile(
        self,
        full_name: str | None = None,
        timezone: str | None = None,
        language: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        """Update user profile information"""
        if full_name is not None:
            self.full_name = full_name
        if timezone is not None:
            self.timezone = timezone
        if language is not None:
            self.language = language
        if avatar_url is not None:
            self.avatar_url = avatar_url

        self.mark_as_updated()

    def change_role(self, new_role: UserRole) -> None:
        """Change user role (typically done by admin)"""
        if self.role != new_role:
            self.role = new_role
            self.mark_as_updated()

    def enable_mfa(self) -> str:
        """Enable multi-factor authentication and return secret"""
        if self.is_mfa_enabled:
            raise BusinessRuleViolationError("MFA is already enabled")

        self.mfa_secret = secrets.token_urlsafe(32)
        self.is_mfa_enabled = True
        self.mark_as_updated()
        return self.mfa_secret

    def disable_mfa(self) -> None:
        """Disable multi-factor authentication"""
        self.is_mfa_enabled = False
        self.mfa_secret = None
        self.mark_as_updated()

    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]

    def can_access_analytics(self) -> bool:
        """Check if user can access analytics features"""
        return self.role in [
            UserRole.ADMIN,
            UserRole.MODERATOR,
            UserRole.ANALYST,
            UserRole.USER,
        ]

    def has_active_status(self) -> bool:
        """Check if user has an active status"""
        return self.status == UserStatus.ACTIVE
