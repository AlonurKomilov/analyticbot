"""
🔒 Security Engine Ports - Framework-Independent Security Abstractions

These ports define the contracts for security operations without coupling
to specific frameworks like FastAPI, Redis, or HTTP libraries.
"""

import builtins
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class AuthRequest:
    """Framework-independent authentication request"""

    client_ip: str | None = None
    user_agent: str | None = None
    device_info: dict[str, Any] | None = None
    headers: dict[str, str] | None = None


@dataclass
class TokenClaims:
    """JWT token claims data structure"""

    user_id: str
    email: str
    username: str
    role: str
    status: str
    session_id: str | None = None
    mfa_verified: bool = False
    auth_provider: str = "local"
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    token_id: str | None = None


@dataclass
class SessionInfo:
    """User session information"""

    id: str
    user_id: str
    token: str
    expires_at: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    device_info: dict[str, Any] | None = None
    created_at: datetime | None = None
    last_activity: datetime | None = None
    is_active: bool = True


class CachePort(ABC):
    """Port for caching operations (Redis abstraction)"""

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Get value by key"""

    @abstractmethod
    def set(self, key: str, value: str, expire_seconds: int | None = None) -> bool:
        """Set key-value with optional expiration"""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key"""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""

    @abstractmethod
    def add_to_set(self, key: str, value: str) -> bool:
        """Add value to set"""

    @abstractmethod
    def remove_from_set(self, key: str, value: str) -> bool:
        """Remove value from set"""

    @abstractmethod
    def get_set_members(self, key: str) -> builtins.set[str]:
        """Get all members of a set"""


class TokenGeneratorPort(ABC):
    """Port for token generation and validation"""

    @abstractmethod
    def generate_jwt_token(
        self, claims: TokenClaims, expires_delta: timedelta | None = None
    ) -> str:
        """Generate JWT token with claims"""

    @abstractmethod
    def verify_jwt_token(self, token: str) -> TokenClaims:
        """Verify and decode JWT token"""

    @abstractmethod
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""


class SecurityConfigPort(ABC):
    """Port for security configuration access"""

    @abstractmethod
    def get_secret_key(self) -> str:
        """Get JWT secret key"""

    @abstractmethod
    def get_algorithm(self) -> str:
        """Get JWT algorithm"""

    @abstractmethod
    def get_access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes"""

    @abstractmethod
    def get_refresh_token_expire_days(self) -> int:
        """Get refresh token expiration in days"""

    @abstractmethod
    def get_session_expire_hours(self) -> int:
        """Get session expiration in hours"""

    @abstractmethod
    def get_password_reset_expire_minutes(self) -> int:
        """Get password reset token expiration"""


class UserRepositoryPort(ABC):
    """Port for user data access"""

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Any | None:
        """Get user by ID"""

    @abstractmethod
    def get_user_by_email(self, email: str) -> Any | None:
        """Get user by email"""

    @abstractmethod
    def get_user_by_username(self, username: str) -> Any | None:
        """Get user by username"""


class HttpClientPort(ABC):
    """Port for HTTP client operations"""

    @abstractmethod
    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Make HTTP GET request"""

    @abstractmethod
    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        """Make HTTP POST request"""


class SecurityEventsPort(ABC):
    """Port for security event logging"""

    @abstractmethod
    def log_login_attempt(self, user_id: str, success: bool, request: AuthRequest) -> None:
        """Log login attempt"""

    @abstractmethod
    def log_session_created(self, user_id: str, session_id: str, request: AuthRequest) -> None:
        """Log session creation"""

    @abstractmethod
    def log_session_terminated(self, user_id: str, session_id: str, reason: str) -> None:
        """Log session termination"""

    @abstractmethod
    def log_token_revoked(self, user_id: str, token_id: str, reason: str) -> None:
        """Log token revocation"""

    @abstractmethod
    def log_password_reset_requested(self, email: str, request: AuthRequest) -> None:
        """Log password reset request"""

    @abstractmethod
    def log_security_event(
        self, user_id: str | None, event_type: str, details: dict[str, Any]
    ) -> None:
        """Log generic security event"""


class SecurityService(ABC):
    """Core Security Service - Framework Independent"""

    @abstractmethod
    def create_access_token(
        self,
        user: Any,
        expires_delta: timedelta | None = None,
        session_id: str | None = None,
    ) -> str:
        """Create JWT access token"""

    @abstractmethod
    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """Create refresh token"""

    @abstractmethod
    def verify_token(self, token: str) -> TokenClaims:
        """Verify and decode token"""

    @abstractmethod
    def create_session(self, user: Any, auth_request: AuthRequest) -> SessionInfo:
        """Create user session"""

    @abstractmethod
    def get_session(self, session_id: str) -> SessionInfo | None:
        """Get session by ID"""

    @abstractmethod
    def terminate_session(self, session_id: str) -> bool:
        """Terminate session"""

    @abstractmethod
    def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all user sessions"""

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""

    @abstractmethod
    def generate_password_reset_token(self, user_email: str) -> str:
        """Generate password reset token"""

    @abstractmethod
    def verify_password_reset_token(self, token: str) -> dict[str, Any] | None:
        """Verify password reset token"""

    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token"""


__all__ = [
    "AuthRequest",
    "TokenClaims",
    "SessionInfo",
    "CachePort",
    "TokenGeneratorPort",
    "SecurityConfigPort",
    "UserRepositoryPort",
    "HttpClientPort",
    "SecurityEventsPort",
    "SecurityService",
]
