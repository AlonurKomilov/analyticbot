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

from core.adapters.jwt_adapter import JoseJWTAdapter
from core.ports.security_ports import (
    AuthRequest,
    CachePort,
    SecurityConfigPort,
    SecurityEventsPort,
    TokenClaims,
    TokenGeneratorPort,
    UserRepositoryPort,
)

from .config import get_security_config

# Import new role system with backwards compatibility
from .models import User, UserSession
from .rbac import RBACManager


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors"""

    def __init__(self, message: str, status_code: int = 401, error_code: str | None = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


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

    def __init__(
        self,
        cache: CachePort | None = None,
        security_events: SecurityEventsPort | None = None,
        token_generator: TokenGeneratorPort | None = None,
        security_config: SecurityConfigPort | None = None,
        user_repository: UserRepositoryPort | None = None,
    ):
        """
        Initialize Security Manager with dependency injection support

        Args:
            cache: Cache port for session/token storage (optional, falls back to Redis)
            security_events: Security events port for audit logging (optional)
            token_generator: Token generator port for JWT operations (optional)
            security_config: Security config port for settings (optional)
            user_repository: User repository port for user data (optional)
        """
        self.cache = cache
        self.security_events = security_events
        self.token_generator: TokenGeneratorPort  # Will be initialized below
        self.security_config_port = security_config
        self.user_repository = user_repository

        # Legacy fallbacks
        self.config = get_security_config()
        if not self.cache:
            self._setup_memory_cache()

        # Initialize JWT adapter if no token generator provided
        if token_generator is None:
            self.token_generator = JoseJWTAdapter(
                secret_key=self.config.SECRET_KEY, algorithm=self.config.ALGORITHM
            )
        else:
            self.token_generator = token_generator

        # Initialize RBAC manager with same DI pattern
        self.rbac_manager = RBACManager(cache=self.cache, security_events=self.security_events)

    def _setup_memory_cache(self) -> None:
        """Setup memory cache fallback when no cache port is provided"""
        logger.info("No cache port provided, using memory cache fallback")
        self._redis_available = False
        self.redis_client = None
        self._memory_cache: dict[str, Any] = {}

    def _cache_get(self, key: str) -> str | None:
        """Get value from cache (abstracted)"""
        if self.cache:
            return self.cache.get(key)
        elif self._redis_available and self.redis_client:
            result = self.redis_client.get(key)
            return result if isinstance(result, str) else None
        else:
            return self._memory_cache.get(key)

    def _cache_set(self, key: str, value: str, expire: int | None = None) -> None:
        """Set value in cache (abstracted)"""
        logger.debug(
            f"_cache_set called: self.cache={self.cache}, self._redis_available={getattr(self, '_redis_available', None)}"
        )
        if self.cache:
            logger.info(f"🔑 Storing in cache: {key[:50]}... (expire={expire}s)")
            result = self.cache.set(key, value, expire)
            logger.info(f"✅ Cache set result: {result}")
        elif self._redis_available and self.redis_client:
            logger.info(f"🔑 Storing in legacy redis: {key[:50]}... (expire={expire}s)")
            if expire:
                self.redis_client.setex(key, expire, value)
            else:
                self.redis_client.set(key, value)
        else:
            logger.warning(
                f"⚠️ Using memory cache for: {key[:50]}... (cache={self.cache}, redis_available={getattr(self, '_redis_available', None)})"
            )
            self._memory_cache[key] = value

    def _cache_delete(self, key: str) -> None:
        """Delete value from cache (abstracted)"""
        if self.cache:
            self.cache.delete(key)
        elif self._redis_available and self.redis_client:
            self.redis_client.delete(key)
        else:
            self._memory_cache.pop(key, None)

    def _cache_exists(self, key: str) -> bool:
        """Check if key exists in cache (abstracted)"""
        if self.cache:
            return self.cache.exists(key)
        elif self._redis_available and self.redis_client:
            result = self.redis_client.exists(key)
            return bool(result)
        else:
            return key in self._memory_cache

    def _cache_add_to_set(self, key: str, value: str) -> None:
        """Add value to set (abstracted)"""
        if self.cache:
            self.cache.add_to_set(key, value)
        elif self._redis_available and self.redis_client:
            self.redis_client.sadd(key, value)
        else:
            if key not in self._memory_cache:
                self._memory_cache[key] = set()
            if isinstance(self._memory_cache[key], set):
                self._memory_cache[key].add(value)

    def _cache_remove_from_set(self, key: str, value: str) -> None:
        """Remove value from set (abstracted)"""
        if self.cache:
            self.cache.remove_from_set(key, value)
        elif self._redis_available and self.redis_client:
            self.redis_client.srem(key, value)
        else:
            if key in self._memory_cache and isinstance(self._memory_cache[key], set):
                self._memory_cache[key].discard(value)

    def _cache_get_set_members(self, key: str) -> set[str]:
        """Get all members of a set (abstracted)"""
        if self.cache:
            return self.cache.get_set_members(key)
        elif self._redis_available and self.redis_client:
            members = self.redis_client.smembers(key)
            return members if isinstance(members, set) else set()
        else:
            cache_value = self._memory_cache.get(key, set())
            return cache_value if isinstance(cache_value, set) else set()

    def _log_security_event(
        self, event_type: str, user_id: str | None = None, details: dict | None = None
    ) -> None:
        """Log security event (abstracted)"""
        if self.security_events:
            self.security_events.log_security_event(user_id, event_type, details or {})
        else:
            logger.info(f"Security event: {event_type} - User: {user_id} - Details: {details}")

    def create_access_token(
        self, user: User, expires_delta: timedelta | None = None, session_id: str | None = None
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
        # Handle both enum and string values for role/status

        # Type-safe extraction of values
        role_val = getattr(user.role, "value", str(user.role)) if user.role is not None else "user"
        status_val = (
            getattr(user.status, "value", str(user.status)) if user.status is not None else "active"
        )
        auth_provider_val = (
            getattr(user.auth_provider, "value", str(user.auth_provider))
            if user.auth_provider is not None
            else "local"
        )

        # Create TokenClaims with correct parameters (matching CoreSecurityService)
        claims = TokenClaims(
            user_id=user.id,
            email=user.email,
            username=user.username,
            role=role_val,
            status=status_val,
            session_id=session_id,
            mfa_verified=user.is_mfa_enabled and session_id is not None,
            auth_provider=auth_provider_val,
            issued_at=datetime.utcnow(),
            expires_at=expire,
            token_id=secrets.token_urlsafe(16),
        )

        # Generate JWT token using adapter
        encoded_jwt = self.token_generator.generate_jwt_token(claims, expires_delta)

        # Cache token in Redis for fast validation (convert claims to dict)
        # Convert datetime to Unix timestamp for JWT standard compliance
        token_dict = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "role": role_val,
            "status": status_val,
            "exp": int(expire.timestamp()),  # Must be Unix timestamp (int)
            "iat": int(datetime.utcnow().timestamp()),  # Must be Unix timestamp (int)
            "jti": claims.token_id,
            "session_id": session_id,
            "mfa_verified": user.is_mfa_enabled and session_id is not None,
            "auth_provider": auth_provider_val,
        }
        self._cache_token(encoded_jwt, token_dict, expire)

        logger.info(f"Access token created for user {user.username} (ID: {user.id})")
        return encoded_jwt

    def create_refresh_token(self, user_id: str, session_id: str, remember_me: bool = False) -> str:
        """
        Create refresh token for token renewal

        🆕 Phase 3.2: Added remember_me parameter for extended sessions

        Args:
            user_id: User ID
            session_id: Session ID
            remember_me: If True, create long-lived token (30 days vs 7 days)

        Returns:
            Refresh token string
        """
        # Determine token expiry based on remember_me flag
        if remember_me:
            # Import settings dynamically to avoid circular imports
            try:
                from config.settings import settings

                expire_days = settings.AUTH_REMEMBER_ME_DAYS
                logger.info(
                    f"🔒 Creating long-lived refresh token ({expire_days} days) for user {user_id}"
                )
            except Exception:
                expire_days = 30  # Fallback to 30 days
        else:
            expire_days = self.config.REFRESH_TOKEN_EXPIRE_DAYS

        expire = datetime.utcnow() + timedelta(days=expire_days)

        # Build JWT payload directly to include custom fields like remember_me
        payload = {
            "sub": user_id,
            "session_id": session_id,
            "exp": int(expire.timestamp()),  # Unix timestamp for JWT standard
            "iat": int(datetime.utcnow().timestamp()),
            "type": "refresh",
            "remember_me": remember_me,  # Store remember_me flag in token
            "jti": f"refresh_{secrets.token_urlsafe(8)}",
        }

        # Encode directly using jose to preserve all custom fields
        from jose import jwt as jose_jwt

        refresh_token = jose_jwt.encode(
            payload, self.config.REFRESH_SECRET_KEY, algorithm=self.config.ALGORITHM
        )

        # Store refresh token in Redis with appropriate TTL
        self._cache_set(
            f"refresh_token:{refresh_token}",
            json.dumps({"user_id": user_id, "session_id": session_id, "remember_me": remember_me}),
            int(timedelta(days=expire_days).total_seconds()),
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
            AuthenticationError: If token is invalid or expired
        """
        try:
            # Check Redis cache first for performance
            cached_payload = self._cache_get(f"token:{token}")
            if cached_payload and isinstance(cached_payload, str):
                payload = json.loads(cached_payload)

                # Verify expiration - convert exp to int if it's a string
                exp_timestamp = (
                    int(payload["exp"]) if isinstance(payload["exp"], str) else payload["exp"]
                )
                if datetime.utcnow() > datetime.fromtimestamp(exp_timestamp):
                    self._revoke_token(token)
                    raise AuthenticationError("Token expired", 401)

                return payload

            # Decode JWT token using adapter
            try:
                claims = self.token_generator.verify_jwt_token(token)

                # Convert claims back to payload format for compatibility
                payload = {
                    "sub": claims.user_id,
                    "email": claims.email,
                    "username": claims.username,
                    "role": claims.role,
                    "status": claims.status,
                    "session_id": claims.session_id,
                    "mfa_verified": claims.mfa_verified,
                    "auth_provider": claims.auth_provider,
                    "jti": claims.token_id,
                }
            except ValueError as e:
                raise AuthenticationError(f"Invalid token: {str(e)}", 401) from e

            # Additional security validations
            user_id = payload.get("sub")
            if not user_id:
                raise AuthenticationError("Invalid token", 401)

            # Check if token is revoked
            if self._cache_exists(f"revoked_token:{token}"):
                raise AuthenticationError("Token revoked", 401)

            return payload

        except ValueError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise AuthenticationError("Could not validate credentials", 401) from e

    def create_user_session(
        self, user: User, auth_request: AuthRequest, device_info: dict[str, Any] | None = None
    ) -> UserSession:
        """
        Create new user session with security tracking

        Args:
            user: User object
            auth_request: Framework-independent request information
            device_info: Device information dictionary

        Returns:
            UserSession object
        """
        # Create session
        session = UserSession(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            ip_address=auth_request.client_ip,
            user_agent=auth_request.user_agent,
            device_info=device_info or auth_request.device_info,
        )

        # Store session in Redis
        from dataclasses import asdict

        session_data = asdict(session)
        self._cache_set(
            f"session:{session.id}",
            json.dumps(session_data, default=str),
            int(timedelta(hours=24).total_seconds()),
        )
        # Also store a lookup by session token to support systems that reference
        # sessions by token (legacy behavior). This writes the same session data
        # under a token-based key so refresh flows that pass session.token work.
        try:
            self._cache_set(
                f"session_token:{session.token}",
                json.dumps(session_data, default=str),
                int(timedelta(hours=24).total_seconds()),
            )
        except Exception:
            # Best-effort: do not fail session creation if token mapping cannot be stored
            logger.debug("Could not store session token mapping in cache (non-fatal)")

        # Track active sessions for user
        self._cache_add_to_set(f"user_sessions:{user.id}", session.id)

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
        session_data = self._cache_get(f"session:{session_id}")
        # If session is not found by ID, try legacy token-based lookup
        if not session_data or not isinstance(session_data, str):
            token_lookup = self._cache_get(f"session_token:{session_id}")
            if token_lookup and isinstance(token_lookup, str):
                session_data = token_lookup
            else:
                return None

        try:
            data = json.loads(session_data)
            # Normalize datetime fields if they were serialized to strings
            for dt_field in ("expires_at", "created_at", "last_activity", "logout_at"):
                if dt_field in data and isinstance(data[dt_field], str):
                    try:
                        from datetime import datetime as _dt

                        data[dt_field] = _dt.fromisoformat(data[dt_field])
                    except Exception:
                        # Fallback: leave as-is; UserSession will handle types or raise
                        pass

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
        from dataclasses import asdict

        self._cache_set(
            f"session:{session_id}",
            json.dumps(asdict(session), default=str),
            int(timedelta(hours=hours).total_seconds()),
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
        self._cache_delete(f"session:{session_id}")

        # Remove from user's active sessions
        self._cache_remove_from_set(f"user_sessions:{session.user_id}", session_id)

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
        session_ids = self._cache_get_set_members(f"user_sessions:{user_id}")
        if not session_ids:
            return 0

        terminated_count = 0

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
            # Use adapter to decode token (ignore expiration for revocation)
            try:
                # Verify token is valid (we'll get exp from it)
                _ = self.token_generator.verify_jwt_token(token)
                # For revocation, we need the expiration time, so we'll use a fallback
                # Since we can't easily get exp from claims, we'll revoke for a default period
                seconds_until_exp = 3600  # 1 hour default
            except ValueError:
                # If token is invalid, still revoke it for safety
                seconds_until_exp = 3600

            if seconds_until_exp > 0:
                self._cache_set(f"revoked_token:{token}", "revoked", seconds_until_exp)

            # Remove from token cache
            self._remove_cached_token(token)

            return True

        except ValueError:
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

        self._cache_set(
            f"password_reset:{reset_token}",
            json.dumps(reset_data),
            900,  # 15 minutes
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
            reset_data_str = self._cache_get(f"password_reset:{reset_token}")
            if not reset_data_str or not isinstance(reset_data_str, str):
                return None

            reset_data = json.loads(reset_data_str)

            # Check if token was already used
            if reset_data.get("used", False):
                return None

            return reset_data

        except (json.JSONDecodeError, Exception) as e:
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
            reset_data_str = self._cache_get(f"password_reset:{reset_token}")
            if not reset_data_str or not isinstance(reset_data_str, str):
                return False

            reset_data = json.loads(reset_data_str)
            reset_data["used"] = True

            # Update with shorter expiration (1 hour for audit trail)
            self._cache_set(f"password_reset:{reset_token}", json.dumps(reset_data), 3600)

            return True

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error consuming reset token: {e}")
            return False

    def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        """
        Refresh access token using valid refresh token with rotation

        🔄 NEW: Implements refresh token rotation for enhanced security
        - Validates old refresh token
        - Issues new access token
        - Issues new refresh token (rotation)
        - Invalidates old refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dictionary with new access_token and refresh_token

        Raises:
            AuthenticationError: If refresh token is invalid or expired
        """
        try:
            # Validate refresh token
            refresh_data_str = self._cache_get(f"refresh_token:{refresh_token}")
            if not refresh_data_str or not isinstance(refresh_data_str, str):
                raise AuthenticationError(
                    "Invalid refresh token", status_code=401, error_code="INVALID_REFRESH_TOKEN"
                )

            refresh_data = json.loads(refresh_data_str)
            user_id = refresh_data.get("user_id")
            session_id = refresh_data.get("session_id")

            if not user_id or not session_id:
                raise AuthenticationError(
                    "Invalid refresh token data", status_code=401, error_code="INVALID_TOKEN_DATA"
                )

            # Verify session still exists
            session = self.get_session(session_id)
            if not session:
                raise AuthenticationError(
                    "Session expired", status_code=401, error_code="SESSION_EXPIRED"
                )

            # 🔄 STEP 1: Invalidate old refresh token (rotation)
            self._cache_delete(f"refresh_token:{refresh_token}")
            logger.info(f"🔄 Rotated refresh token for user {user_id}")

            # Create new access token with minimal user data
            # In a real implementation, you'd fetch full user data from database
            from core.security_engine.models import AuthProvider, User, UserRole, UserStatus

            # Mock user object for token creation - replace with actual user lookup
            user = User(
                id=user_id,
                email=f"user_{user_id}@example.com",  # This should come from database
                username=f"user_{user_id}",  # This should come from database
                role=UserRole.USER,  # This should come from database
                status=UserStatus.ACTIVE,  # This should come from database
                auth_provider=AuthProvider.LOCAL,  # This should come from database
            )

            # 🔄 STEP 2: Create new access token
            new_access_token = self.create_access_token(
                user,
                expires_delta=timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
                session_id=session_id,
            )

            # 🔄 STEP 3: Create new refresh token (rotation)
            new_refresh_token = self.create_refresh_token(user_id, session_id)

            # Log security event
            self._log_security_event(
                "token_rotation",
                user_id=str(user_id),
                details={"session_id": session_id, "timestamp": datetime.utcnow().isoformat()},
            )

            logger.info(f"✅ Access token refreshed with rotation for user {user_id}")

            # 🔄 STEP 4: Return both tokens
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing refresh token data: {e}")
            raise AuthenticationError(
                "Invalid refresh token", status_code=401, error_code="INVALID_TOKEN_FORMAT"
            ) from e
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise AuthenticationError(
                "Token refresh failed", status_code=500, error_code="TOKEN_REFRESH_ERROR"
            ) from e

    def extend_session_on_activity(self, session_id: str, extension_minutes: int = 15) -> bool:
        """
        🆕 Phase 3.1: Extend session expiry time on user activity (sliding sessions)

        Implements sliding window sessions that extend on each user request,
        preventing timeout during active usage.

        Args:
            session_id: Active session ID to extend
            extension_minutes: Minutes to extend session by (default: 15)

        Returns:
            True if session was extended, False if session doesn't exist

        Example:
            # In API middleware/dependency:
            if settings.AUTH_SLIDING_SESSION_ENABLED:
                security_manager.extend_session_on_activity(
                    session_id=current_user.session_id,
                    extension_minutes=settings.AUTH_SESSION_EXTENSION_MINUTES
                )
        """
        try:
            # Get current session data
            session_key = f"session:{session_id}"
            session_data_str = self._cache_get(session_key)

            if not session_data_str or not isinstance(session_data_str, str):
                logger.debug(f"Session {session_id} not found for extension")
                return False

            # Parse session data
            session_data = json.loads(session_data_str)

            # Update last_activity timestamp
            session_data["last_activity"] = datetime.utcnow().isoformat()

            # Extend session TTL in cache
            ttl_seconds = int(extension_minutes * 60)

            # Update session in cache with new TTL
            self._cache_set(
                session_key,
                json.dumps(session_data),
                ttl_seconds,  # Use TTL in seconds, not datetime
            )

            logger.debug(
                f"🕐 Extended session {session_id} by {extension_minutes} minutes "
                f"(TTL: {ttl_seconds}s)"
            )

            return True

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing session data for extension: {e}")
            return False
        except Exception as e:
            logger.error(f"Error extending session {session_id}: {e}")
            return False

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
            self._cache_set(f"token:{token}", json.dumps(payload, default=str), seconds_until_exp)

    def _remove_cached_token(self, token: str) -> None:
        """Remove token from Redis cache"""
        self._cache_delete(f"token:{token}")

    def _revoke_token(self, token: str) -> None:
        """Internal method to revoke expired token"""
        self._cache_delete(f"token:{token}")
        self._cache_set(f"revoked_token:{token}", "expired", 3600)


# Global security manager instance - lazy initialization
_security_manager = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Note: FastAPI dependency functions have been moved to apps.api layer
# Core domain should not contain framework-specific dependencies
# Use apps.api.deps or apps.api.middleware for authentication dependencies


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
