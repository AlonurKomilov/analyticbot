"""
🔒 Security Engine Ports - Framework-Independent Security Abstractions

These ports define the contracts for security operations without coupling
to specific frameworks like FastAPI, Redis, or HTTP libraries.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Set


@dataclass
class AuthRequest:
    """Framework-independent authentication request"""
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None


@dataclass
class TokenClaims:
    """JWT token claims data structure"""
    user_id: str
    email: str
    username: str
    role: str
    status: str
    session_id: Optional[str] = None
    mfa_verified: bool = False
    auth_provider: str = "local"
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    token_id: Optional[str] = None


@dataclass
class SessionInfo:
    """User session information"""
    id: str
    user_id: str
    token: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    is_active: bool = True


class CachePort(ABC):
    """Port for caching operations (Redis abstraction)"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set key-value with optional expiration"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    def add_to_set(self, key: str, value: str) -> bool:
        """Add value to set"""
        pass
    
    @abstractmethod
    def remove_from_set(self, key: str, value: str) -> bool:
        """Remove value from set"""
        pass
    
    @abstractmethod
    def get_set_members(self, key: str) -> Set[str]:
        """Get all members of a set"""
        pass


class TokenGeneratorPort(ABC):
    """Port for token generation and validation"""
    
    @abstractmethod
    def generate_jwt_token(
        self, 
        claims: TokenClaims, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT token with claims"""
        pass
    
    @abstractmethod
    def verify_jwt_token(self, token: str) -> TokenClaims:
        """Verify and decode JWT token"""
        pass
    
    @abstractmethod
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        pass


class SecurityConfigPort(ABC):
    """Port for security configuration access"""
    
    @abstractmethod
    def get_secret_key(self) -> str:
        """Get JWT secret key"""
        pass
    
    @abstractmethod
    def get_algorithm(self) -> str:
        """Get JWT algorithm"""
        pass
    
    @abstractmethod
    def get_access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes"""
        pass
    
    @abstractmethod
    def get_refresh_token_expire_days(self) -> int:
        """Get refresh token expiration in days"""
        pass
    
    @abstractmethod
    def get_session_expire_hours(self) -> int:
        """Get session expiration in hours"""
        pass
    
    @abstractmethod
    def get_password_reset_expire_minutes(self) -> int:
        """Get password reset token expiration"""
        pass


class UserRepositoryPort(ABC):
    """Port for user data access"""
    
    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[Any]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Any]:
        """Get user by username"""
        pass


class SecurityEventsPort(ABC):
    """Port for security event logging"""
    
    @abstractmethod
    def log_login_attempt(self, user_id: str, success: bool, request: AuthRequest) -> None:
        """Log login attempt"""
        pass
    
    @abstractmethod
    def log_session_created(self, user_id: str, session_id: str, request: AuthRequest) -> None:
        """Log session creation"""
        pass
    
    @abstractmethod
    def log_session_terminated(self, user_id: str, session_id: str, reason: str) -> None:
        """Log session termination"""
        pass
    
    @abstractmethod
    def log_token_revoked(self, user_id: str, token_id: str, reason: str) -> None:
        """Log token revocation"""
        pass
    
    @abstractmethod
    def log_password_reset_requested(self, email: str, request: AuthRequest) -> None:
        """Log password reset request"""
        pass


class SecurityService(ABC):
    """Core Security Service - Framework Independent"""
    
    @abstractmethod
    def create_access_token(
        self,
        user: Any,
        expires_delta: Optional[timedelta] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Create JWT access token"""
        pass
    
    @abstractmethod
    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """Create refresh token"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> TokenClaims:
        """Verify and decode token"""
        pass
    
    @abstractmethod
    def create_session(
        self, 
        user: Any, 
        auth_request: AuthRequest
    ) -> SessionInfo:
        """Create user session"""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def terminate_session(self, session_id: str) -> bool:
        """Terminate session"""
        pass
    
    @abstractmethod
    def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all user sessions"""
        pass
    
    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        pass
    
    @abstractmethod
    def generate_password_reset_token(self, user_email: str) -> str:
        """Generate password reset token"""
        pass
    
    @abstractmethod
    def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify password reset token"""
        pass
    
    @abstractmethod
    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token"""
        pass


__all__ = [
    "AuthRequest",
    "TokenClaims", 
    "SessionInfo",
    "CachePort",
    "TokenGeneratorPort",
    "SecurityConfigPort",
    "UserRepositoryPort",
    "SecurityEventsPort",
    "SecurityService",
]