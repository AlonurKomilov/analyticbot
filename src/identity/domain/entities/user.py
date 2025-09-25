"""
User Entity - Core identity domain entity
"""

import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from passlib.context import CryptContext

from src.shared_kernel.domain.base_entity import AggregateRoot
from src.shared_kernel.domain.value_objects import UserId, EmailAddress, Username
from src.shared_kernel.domain.exceptions import ValidationError, BusinessRuleViolationError
from .events import UserRegistered, UserLoggedIn, UserPasswordChanged, UserStatusChanged

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(str, Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User account status"""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"


class AuthProvider(str, Enum):
    """Authentication providers"""
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"
    TELEGRAM = "telegram"


class User(AggregateRoot):
    """
    User aggregate root - Core identity entity
    
    This represents a user in the system with all authentication,
    authorization, and profile management capabilities.
    """
    
    def __init__(
        self,
        id: UserId,
        email: EmailAddress,
        username: Username,
        full_name: Optional[str] = None,
        hashed_password: Optional[str] = None,
        auth_provider: AuthProvider = AuthProvider.LOCAL,
        provider_id: Optional[str] = None,
        role: UserRole = UserRole.USER,
        status: UserStatus = UserStatus.PENDING_VERIFICATION,
        is_mfa_enabled: bool = False,
        mfa_secret: Optional[str] = None,
        failed_login_attempts: int = 0,
        locked_until: Optional[datetime] = None,
        last_login: Optional[datetime] = None,
        last_password_change: Optional[datetime] = None,
        email_verified_at: Optional[datetime] = None,
        password_reset_token: Optional[str] = None,
        email_verification_token: Optional[str] = None,
        avatar_url: Optional[str] = None,
        timezone: str = "UTC",
        language: str = "en"
    ):
        # Call parent constructor with entity ID
        super().__init__(id)
        
        # Core identity
        self.email = email
        self.username = username
        self.full_name = full_name
        
        # Authentication
        self.hashed_password = hashed_password
        self.auth_provider = auth_provider
        self.provider_id = provider_id
        
        # Security
        self.role = role
        self.status = status
        self.is_mfa_enabled = is_mfa_enabled
        self.mfa_secret = mfa_secret
        
        # Security tracking
        self.failed_login_attempts = failed_login_attempts
        self.locked_until = locked_until
        self.last_login = last_login
        
        # Password management
        self.last_password_change = last_password_change
        self.email_verified_at = email_verified_at
        
        # Tokens
        self.password_reset_token = password_reset_token
        self.email_verification_token = email_verification_token
        
        # Profile
        self.avatar_url = avatar_url
        self.timezone = timezone
        self.language = language
        
        # Validate after initialization
        self._validate_user_data()
    
    def _validate_user_data(self):
        """Validate user data consistency"""
        if self.auth_provider == AuthProvider.LOCAL and not self.hashed_password:
            raise ValidationError("Local auth users must have a password")
        
        if self.auth_provider != AuthProvider.LOCAL and self.hashed_password:
            raise ValidationError("External auth users should not have passwords")
    
    @classmethod
    def create_new_user(
        cls,
        user_id: UserId,
        email: EmailAddress,
        username: Username,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        auth_provider: AuthProvider = AuthProvider.LOCAL
    ) -> "User":
        """Factory method to create a new user"""
        
        hashed_password = None
        if password and auth_provider == AuthProvider.LOCAL:
            hashed_password = pwd_context.hash(password)
        
        user = cls(
            id=user_id,
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            auth_provider=auth_provider,
            last_password_change=datetime.utcnow() if hashed_password else None
        )
        
        # Add domain event
        user.add_domain_event(UserRegistered(
            user_id=str(user_id.value),
            email=str(email),
            username=str(username),
            registration_time=datetime.utcnow(),
            auth_provider=auth_provider.value
        ))
        
        return user
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash"""
        if not self.hashed_password:
            return False
        return pwd_context.verify(password, self.hashed_password)
    
    def change_password(self, old_password: str, new_password: str) -> None:
        """Change user password"""
        if not self.verify_password(old_password):
            raise BusinessRuleViolationError("Current password is incorrect")
        
        self.hashed_password = pwd_context.hash(new_password)
        self.last_password_change = datetime.utcnow()
        self.failed_login_attempts = 0  # Reset failed attempts
        self.locked_until = None  # Unlock account if locked
        
        self.add_domain_event(UserPasswordChanged(
            user_id=str(self.id.value),
            email=str(self.email),
            change_time=datetime.utcnow()
        ))
    
    def reset_password(self, new_password: str) -> None:
        """Reset password (admin or token-based)"""
        self.hashed_password = pwd_context.hash(new_password)
        self.last_password_change = datetime.utcnow()
        self.password_reset_token = None
        self.failed_login_attempts = 0
        self.locked_until = None
        
        self.add_domain_event(UserPasswordChanged(
            user_id=str(self.id.value),
            email=str(self.email),
            change_time=datetime.utcnow()
        ))
    
    def login(self, ip_address: Optional[str] = None) -> None:
        """Record successful login"""
        self.last_login = datetime.utcnow()
        self.failed_login_attempts = 0
        self.locked_until = None
        
        self.add_domain_event(UserLoggedIn(
            user_id=str(self.id.value),
            email=str(self.email),
            login_time=datetime.utcnow(),
            ip_address=ip_address
        ))
    
    def record_failed_login(self) -> None:
        """Record failed login attempt"""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def is_account_locked(self) -> bool:
        """Check if account is locked"""
        if not self.locked_until:
            return False
        return datetime.utcnow() < self.locked_until
    
    def unlock_account(self) -> None:
        """Unlock account"""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def activate_account(self) -> None:
        """Activate account (typically after email verification)"""
        old_status = self.status
        self.status = UserStatus.ACTIVE
        self.email_verified_at = datetime.utcnow()
        self.email_verification_token = None
        
        self.add_domain_event(UserStatusChanged(
            user_id=str(self.id.value),
            email=str(self.email),
            old_status=old_status.value,
            new_status=self.status.value,
            change_time=datetime.utcnow()
        ))
    
    def suspend_account(self, reason: str) -> None:
        """Suspend account"""
        old_status = self.status
        self.status = UserStatus.SUSPENDED
        
        self.add_domain_event(UserStatusChanged(
            user_id=str(self.id.value),
            email=str(self.email),
            old_status=old_status.value,
            new_status=self.status.value,
            change_time=datetime.utcnow(),
            reason=reason
        ))
    
    def generate_verification_token(self) -> str:
        """Generate email verification token"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        return token
    
    def verify_email_token(self, token: str) -> bool:
        """Verify email verification token"""
        return self.email_verification_token == token
    
    def generate_password_reset_token(self) -> str:
        """Generate password reset token"""
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        return token
    
    def verify_password_reset_token(self, token: str) -> bool:
        """Verify password reset token"""
        return self.password_reset_token == token
    
    def can_be_processed(self) -> bool:
        """Check if user can be processed for business operations"""
        return self.status in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION]
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def is_moderator(self) -> bool:
        """Check if user is moderator or admin"""
        return self.role in [UserRole.ADMIN, UserRole.MODERATOR]
    
    def __str__(self) -> str:
        return f"User({self.username}@{self.email})"
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email}, status={self.status})"