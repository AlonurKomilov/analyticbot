"""
🔧 Infrastructure Adapters for Security Operations

Framework-specific implementations of security ports that handle
Redis caching, JWT operations, and other external dependencies.
"""

import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Set

import redis
from jose import JWTError, jwt

from core.ports.security_ports import (
    AuthRequest,
    CachePort,
    SecurityConfigPort,
    SecurityEventsPort,
    TokenClaims,
    TokenGeneratorPort,
    UserRepositoryPort,
)

logger = logging.getLogger(__name__)


class RedisCache(CachePort):
    """Redis implementation of cache port"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            result = self.redis_client.get(key)
            return result if isinstance(result, str) else None
        except redis.RedisError as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set key-value with optional expiration"""
        try:
            if expire_seconds:
                return bool(self.redis_client.setex(key, expire_seconds, value))
            else:
                return bool(self.redis_client.set(key, value))
        except redis.RedisError as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    def add_to_set(self, key: str, value: str) -> bool:
        """Add value to set"""
        try:
            return bool(self.redis_client.sadd(key, value))
        except redis.RedisError as e:
            logger.error(f"Redis sadd error for key {key}: {e}")
            return False
    
    def remove_from_set(self, key: str, value: str) -> bool:
        """Remove value from set"""
        try:
            return bool(self.redis_client.srem(key, value))
        except redis.RedisError as e:
            logger.error(f"Redis srem error for key {key}: {e}")
            return False
    
    def get_set_members(self, key: str) -> Set[str]:
        """Get all members of a set"""
        try:
            result = self.redis_client.smembers(key)
            return result if isinstance(result, set) else set()
        except redis.RedisError as e:
            logger.error(f"Redis smembers error for key {key}: {e}")
            return set()


class JWTTokenGenerator(TokenGeneratorPort):
    """JWT implementation of token generator port"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_jwt_token(
        self, 
        claims: TokenClaims, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Generate JWT token with claims"""
        # Convert TokenClaims to JWT payload
        payload = {
            "sub": claims.user_id,
            "email": claims.email,
            "username": claims.username,
            "role": claims.role,
            "status": claims.status,
            "session_id": claims.session_id,
            "mfa_verified": claims.mfa_verified,
            "auth_provider": claims.auth_provider,
            "jti": claims.token_id or self.generate_secure_token(16),
            "iat": claims.issued_at or datetime.utcnow(),
            "exp": claims.expires_at or (
                datetime.utcnow() + (expires_delta or timedelta(minutes=15))
            )
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_jwt_token(self, token: str) -> TokenClaims:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            return TokenClaims(
                user_id=payload.get("sub", ""),
                email=payload.get("email", ""),
                username=payload.get("username", ""),
                role=payload.get("role", ""),
                status=payload.get("status", ""),
                session_id=payload.get("session_id"),
                mfa_verified=payload.get("mfa_verified", False),
                auth_provider=payload.get("auth_provider", "local"),
                issued_at=datetime.fromtimestamp(payload.get("iat")) 
                    if payload.get("iat") else None,
                expires_at=datetime.fromtimestamp(payload.get("exp")) 
                    if payload.get("exp") else None,
                token_id=payload.get("jti")
            )
            
        except JWTError as e:
            raise ValueError(f"JWT verification failed: {str(e)}")
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure random token"""
        return secrets.token_urlsafe(length)


class ConfigSecurityConfig(SecurityConfigPort):
    """Configuration-based security config implementation"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict
    
    def get_secret_key(self) -> str:
        """Get JWT secret key"""
        return self._config.get("SECRET_KEY", "default-secret-key")
    
    def get_algorithm(self) -> str:
        """Get JWT algorithm"""
        return self._config.get("ALGORITHM", "HS256")
    
    def get_access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes"""
        return self._config.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15)
    
    def get_refresh_token_expire_days(self) -> int:
        """Get refresh token expiration in days"""
        return self._config.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)
    
    def get_session_expire_hours(self) -> int:
        """Get session expiration in hours"""
        return self._config.get("SESSION_EXPIRE_HOURS", 24)
    
    def get_password_reset_expire_minutes(self) -> int:
        """Get password reset token expiration"""
        return self._config.get("PASSWORD_RESET_EXPIRE_MINUTES", 15)


class NoOpSecurityEvents(SecurityEventsPort):
    """No-op implementation of security events port (can be replaced with real logging)"""
    
    def log_login_attempt(self, user_id: str, success: bool, request: AuthRequest) -> None:
        """Log login attempt"""
        logger.info(f"Login attempt - User: {user_id}, Success: {success}, IP: {request.client_ip}")
    
    def log_session_created(self, user_id: str, session_id: str, request: AuthRequest) -> None:
        """Log session creation"""
        logger.info(f"Session created - User: {user_id}, Session: {session_id}, IP: {request.client_ip}")
    
    def log_session_terminated(self, user_id: str, session_id: str, reason: str) -> None:
        """Log session termination"""
        logger.info(f"Session terminated - User: {user_id}, Session: {session_id}, Reason: {reason}")
    
    def log_token_revoked(self, user_id: str, token_id: str, reason: str) -> None:
        """Log token revocation"""
        logger.info(f"Token revoked - User: {user_id}, Token: {token_id}, Reason: {reason}")
    
    def log_password_reset_requested(self, email: str, request: AuthRequest) -> None:
        """Log password reset request"""
        logger.info(f"Password reset requested - Email: {email}, IP: {request.client_ip}")


class MockUserRepository(UserRepositoryPort):
    """Mock implementation for user repository (replace with real database implementation)"""
    
    def get_user_by_id(self, user_id: str) -> Optional[Any]:
        """Get user by ID - mock implementation"""
        # This should be replaced with actual database lookup
        from core.security_engine.models import User, UserRole, UserStatus, AuthProvider
        
        return User(
            id=user_id,
            email=f"user_{user_id}@example.com",
            username=f"user_{user_id}",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            auth_provider=AuthProvider.LOCAL
        )
    
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Get user by email - mock implementation"""
        # Extract user ID from email for mock
        if "@" in email:
            username = email.split("@")[0]
            if username.startswith("user_"):
                user_id = username[5:]  # Remove "user_" prefix
                return self.get_user_by_id(user_id)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Any]:
        """Get user by username - mock implementation"""
        if username.startswith("user_"):
            user_id = username[5:]  # Remove "user_" prefix
            return self.get_user_by_id(user_id)
        return None