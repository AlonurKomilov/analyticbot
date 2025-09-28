"""
🔒 Core Authentication Manager - JWT, Sessions & Security

High-performance authentication system with comprehensive security features:
- JWT token management with refresh tokens
- Session management with Redis caching
- Account lockout protection
- Security event logging
- Device tracking
"""

import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any

import redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import get_security_config
from .models import User, UserRole, UserSession
from .rbac import RBACManager

# Configure logging
logger = logging.getLogger(__name__)


class SecurityManager:
    """
    🔐 Core Security Manager

    Handles all authentication operations with enterprise-grade security:
    - JWT token generation and validation
    - Session management with Redis
    - Multi-factor authentication
    - Account security policies
    - Audit logging
    """

    def __init__(self):
        self.config = get_security_config()
        self.redis_client = redis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            db=self.config.REDIS_DB,
            decode_responses=True,
        )
        self.security = HTTPBearer()
        self.rbac_manager = RBACManager()

    def create_access_token(
        self,
        user: User,
        expires_delta: timedelta | None = None,
        session_id: str | None = None,
    ) -> str:
        """
        Create JWT access token with user claims

        Args:
            user: User object
            expires_delta: Token expiration time
            session_id: Associated session ID

        Returns:
            JWT access token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Token payload with comprehensive claims
        to_encode = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "status": user.status.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),  # JWT ID for token tracking
            "session_id": session_id,
            "mfa_verified": user.is_mfa_enabled and session_id,
            "auth_provider": user.auth_provider.value,
        }

        encoded_jwt = jwt.encode(to_encode, self.config.SECRET_KEY, algorithm=self.config.ALGORITHM)

        # Cache token in Redis for fast validation
        self._cache_token(encoded_jwt, to_encode, expire)

        logger.info(f"Access token created for user {user.username} (ID: {user.id})")
        return encoded_jwt

    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """
        Create refresh token for token renewal

        Args:
            user_id: User ID
            session_id: Session ID

        Returns:
            Refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }

        refresh_token = jwt.encode(
            to_encode, self.config.REFRESH_SECRET_KEY, algorithm=self.config.ALGORITHM
        )

        # Store refresh token in Redis
        self.redis_client.setex(
            f"refresh_token:{refresh_token}",
            int(timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
            json.dumps({"user_id": user_id, "session_id": session_id}),
        )

        return refresh_token

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Check Redis cache first for performance
            cached_payload = self.redis_client.get(f"token:{token}")
            if cached_payload and isinstance(cached_payload, str):
                payload = json.loads(cached_payload)

                # Verify expiration
                if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                    self._revoke_token(token)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
                    )

                return payload

            # Decode JWT token
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])

            # Additional security validations
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )

            # Check if token is revoked
            if self.redis_client.exists(f"revoked_token:{token}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
                )

            return payload

        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    def create_user_session(
        self, user: User, request: Request, device_info: dict[str, Any] | None = None
    ) -> UserSession:
        """
        Create new user session with security tracking

        Args:
            user: User object
            request: FastAPI request object
            device_info: Device information dictionary

        Returns:
            UserSession object
        """
        # Create session
        session = UserSession(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info=device_info,
        )

        # Store session in Redis
        session_data = session.dict()
        self.redis_client.setex(
            f"session:{session.id}",
            int(timedelta(hours=24).total_seconds()),
            json.dumps(session_data, default=str),
        )

        # Track active sessions for user
        self.redis_client.sadd(f"user_sessions:{user.id}", session.id)

        logger.info(f"Session created for user {user.username} from IP {session.ip_address}")
        return session

    def get_session(self, session_id: str) -> UserSession | None:
        """
        Retrieve user session from Redis

        Args:
            session_id: Session ID

        Returns:
            UserSession object or None
        """
        session_data = self.redis_client.get(f"session:{session_id}")
        if not session_data or not isinstance(session_data, str):
            return None

        try:
            data = json.loads(session_data)
            session = UserSession(**data)

            # Check if session is expired
            if session.is_expired():
                self.terminate_session(session_id)
                return None

            return session
        except (json.JSONDecodeError, ValueError):
            return None

    def extend_session(self, session_id: str, hours: int = 24) -> bool:
        """
        Extend session expiration time

        Args:
            session_id: Session ID
            hours: Hours to extend

        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.extend_session(hours)

        # Update in Redis
        self.redis_client.setex(
            f"session:{session_id}",
            int(timedelta(hours=hours).total_seconds()),
            json.dumps(session.dict(), default=str),
        )

        return True

    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate user session

        Args:
            session_id: Session ID

        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Mark session as terminated
        session.terminate_session()

        # Remove from Redis
        self.redis_client.delete(f"session:{session_id}")

        # Remove from user's active sessions
        self.redis_client.srem(f"user_sessions:{session.user_id}", session_id)

        logger.info(f"Session {session_id} terminated for user {session.user_id}")
        return True

    def terminate_all_user_sessions(self, user_id: str) -> int:
        """
        Terminate all sessions for a user

        Args:
            user_id: User ID

        Returns:
            Number of sessions terminated
        """
        session_ids = self.redis_client.smembers(f"user_sessions:{user_id}")
        if not session_ids:
            return 0

        terminated_count = 0
        # Type hint: session_ids should be a set of strings due to decode_responses=True
        session_ids = session_ids if isinstance(session_ids, set) else set()

        for session_id in session_ids:
            if self.terminate_session(session_id):
                terminated_count += 1

        logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
        return terminated_count

    def revoke_token(self, token: str) -> bool:
        """
        Revoke JWT token

        Args:
            token: JWT token to revoke

        Returns:
            Success status
        """
        try:
            # Decode to get expiration
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
                options={"verify_exp": False},
            )

            # Add to revoked tokens with expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                expire_time = datetime.fromtimestamp(exp_timestamp)
                seconds_until_exp = int((expire_time - datetime.utcnow()).total_seconds())

                if seconds_until_exp > 0:
                    self.redis_client.setex(f"revoked_token:{token}", seconds_until_exp, "revoked")

            # Remove from token cache
            self._remove_cached_token(token)

            return True

        except JWTError:
            return False

    def generate_password_reset_token(self, user_email: str) -> str:
        """
        Generate password reset token

        Args:
            user_email: User email for password reset

        Returns:
            Password reset token
        """
        # Generate secure token
        reset_token = secrets.token_urlsafe(32)

        # Store in Redis with expiration (15 minutes)
        reset_data = {
            "email": user_email,
            "created_at": datetime.utcnow().isoformat(),
            "used": False,
        }

        self.redis_client.setex(
            f"password_reset:{reset_token}",
            900,
            json.dumps(reset_data),  # 15 minutes
        )

        logger.info(f"Password reset token generated for {user_email}")
        return reset_token

    def verify_password_reset_token(self, reset_token: str) -> dict[str, Any] | None:
        """
        Verify password reset token

        Args:
            reset_token: Password reset token to verify

        Returns:
            Token data if valid, None otherwise
        """
        try:
            reset_data_str = self.redis_client.get(f"password_reset:{reset_token}")
            if not reset_data_str or not isinstance(reset_data_str, str):
                return None

            reset_data = json.loads(reset_data_str)

            # Check if token was already used
            if reset_data.get("used", False):
                return None

            return reset_data

        except (json.JSONDecodeError, redis.RedisError) as e:
            logger.error(f"Error verifying reset token: {e}")
            return None

    def consume_password_reset_token(self, reset_token: str) -> bool:
        """
        Mark password reset token as used

        Args:
            reset_token: Token to consume

        Returns:
            Success status
        """
        try:
            reset_data_str = self.redis_client.get(f"password_reset:{reset_token}")
            if not reset_data_str or not isinstance(reset_data_str, str):
                return False

            reset_data = json.loads(reset_data_str)
            reset_data["used"] = True

            # Update with shorter expiration (1 hour for audit trail)
            self.redis_client.setex(f"password_reset:{reset_token}", 3600, json.dumps(reset_data))

            return True

        except (json.JSONDecodeError, redis.RedisError) as e:
            logger.error(f"Error consuming reset token: {e}")
            return False

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh access token using valid refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token

        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        try:
            # Validate refresh token
            refresh_data_str = self.redis_client.get(f"refresh_token:{refresh_token}")
            if not refresh_data_str or not isinstance(refresh_data_str, str):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            refresh_data = json.loads(refresh_data_str)
            user_id = refresh_data.get("user_id")
            session_id = refresh_data.get("session_id")

            if not user_id or not session_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token data",
                )

            # Verify session still exists
            session = self.get_session(session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
                )

            # Create new access token with minimal user data
            # In a real implementation, you'd fetch full user data from database
            from core.security_engine.models import (
                AuthProvider,
                User,
                UserRole,
                UserStatus,
            )

            # Mock user object for token creation - replace with actual user lookup
            user = User(
                id=user_id,
                email=f"user_{user_id}@example.com",  # This should come from database
                username=f"user_{user_id}",  # This should come from database
                role=UserRole.USER,  # This should come from database
                status=UserStatus.ACTIVE,  # This should come from database
                auth_provider=AuthProvider.LOCAL,  # This should come from database
            )

            # Create new access token
            new_access_token = self.create_access_token(
                user,
                expires_delta=timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
                session_id=session_id,
            )

            logger.info(f"Access token refreshed for user {user_id}")
            return new_access_token

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing refresh token data: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token refresh failed",
            )

    def revoke_user_sessions(self, user_id: str) -> int:
        """
        Revoke all active sessions for a user

        Args:
            user_id: User ID to revoke sessions for

        Returns:
            Number of sessions revoked
        """
        return self.terminate_all_user_sessions(user_id)

    def _cache_token(self, token: str, payload: dict[str, Any], expire: datetime) -> None:
        """Cache token in Redis for fast validation"""
        seconds_until_exp = int((expire - datetime.utcnow()).total_seconds())
        if seconds_until_exp > 0:
            self.redis_client.setex(
                f"token:{token}", seconds_until_exp, json.dumps(payload, default=str)
            )

    def _remove_cached_token(self, token: str) -> None:
        """Remove token from Redis cache"""
        self.redis_client.delete(f"token:{token}")

    def _revoke_token(self, token: str) -> None:
        """Internal method to revoke expired token"""
        self.redis_client.delete(f"token:{token}")
        self.redis_client.setex(f"revoked_token:{token}", 3600, "expired")


# Global security manager instance - lazy initialization
_security_manager = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# FastAPI dependency functions
# DEPRECATED: This function is deprecated.
# Use apps.api.middleware.auth.get_current_user instead for full user object
# or core.security_engine.auth_utils.AuthUtils for token operations
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> dict[str, Any]:
    """
    DEPRECATED: FastAPI dependency to get current authenticated user

    This function only returns token payload, not full user from database.
    Use apps.api.middleware.auth.get_current_user for complete user object.

    Returns:
        User payload from JWT token (deprecated - use middleware version)
    """
    token = credentials.credentials
    return get_security_manager().verify_token(token)


def require_role(required_role: UserRole):
    """
    FastAPI dependency to require specific user role

    Args:
        required_role: Required user role

    Returns:
        Dependency function
    """

    def role_checker(current_user: dict[str, Any] = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role"))

        # Role hierarchy check
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.READONLY: 1,
            UserRole.USER: 2,
            UserRole.ANALYST: 3,
            UserRole.MODERATOR: 4,
            UserRole.ADMIN: 5,
        }

        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}",
            )

        return current_user

    return role_checker


# Export convenience functions
# Convenience functions - these will initialize SecurityManager when first called
# DEPRECATED: These wrapper functions are deprecated.
# Use core.security_engine.auth_utils.AuthUtils or get_security_manager() directly


def create_access_token(*args, **kwargs):
    """DEPRECATED: Use auth_utils.create_access_token() instead"""
    return get_security_manager().create_access_token(*args, **kwargs)


def verify_token(*args, **kwargs):
    """DEPRECATED: Use auth_utils.verify_jwt_token() instead"""
    return get_security_manager().verify_token(*args, **kwargs)
