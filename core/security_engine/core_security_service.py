"""
🔒 Core Security Service - Framework Independent Implementation

Pure domain implementation of security operations without framework dependencies.
Uses dependency injection for external concerns like caching and token generation.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from core.ports.security_ports import (
    AuthRequest,
    CachePort,
    SecurityConfigPort,
    SecurityEventsPort,
    SecurityService,
    SessionInfo,
    TokenClaims,
    TokenGeneratorPort,
    UserRepositoryPort,
)

from .models import User

logger = logging.getLogger(__name__)


class CoreSecurityService(SecurityService):
    """
    🔐 Framework-Independent Core Security Service

    Pure domain implementation that uses ports for external dependencies.
    No direct coupling to FastAPI, Redis, or any specific framework.
    """

    def __init__(
        self,
        cache: CachePort,
        token_generator: TokenGeneratorPort,
        config: SecurityConfigPort,
        user_repository: UserRepositoryPort,
        security_events: SecurityEventsPort,
    ):
        self.cache = cache
        self.token_generator = token_generator
        self.config = config
        self.user_repository = user_repository
        self.security_events = security_events

    def create_access_token(
        self,
        user: User,
        expires_delta: timedelta | None = None,
        session_id: str | None = None,
    ) -> str:
        """Create JWT access token with user claims"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.config.get_access_token_expire_minutes()
            )

        claims = TokenClaims(
            user_id=user.id,
            email=user.email,
            username=user.username,
            role=user.role.value,
            status=user.status.value,
            session_id=session_id,
            mfa_verified=user.is_mfa_enabled and session_id is not None,
            auth_provider=user.auth_provider.value,
            issued_at=datetime.utcnow(),
            expires_at=expire,
            token_id=self.token_generator.generate_secure_token(16),
        )

        token = self.token_generator.generate_jwt_token(claims, expires_delta)

        # Cache token for fast validation
        self._cache_token(token, claims, expire)

        logger.info(f"Access token created for user {user.username} (ID: {user.id})")
        return token

    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """Create refresh token for token renewal"""
        expire = datetime.utcnow() + timedelta(days=self.config.get_refresh_token_expire_days())

        claims = TokenClaims(
            user_id=user_id,
            email="",  # Refresh tokens don't need full claims
            username="",
            role="",
            status="",
            session_id=session_id,
            issued_at=datetime.utcnow(),
            expires_at=expire,
            token_id=self.token_generator.generate_secure_token(16),
        )

        refresh_token = self.token_generator.generate_jwt_token(
            claims, timedelta(days=self.config.get_refresh_token_expire_days())
        )

        # Store refresh token data
        refresh_data: dict[str, Any] = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "type": "refresh",
        }

        expire_seconds = int(
            timedelta(days=self.config.get_refresh_token_expire_days()).total_seconds()
        )

        self.cache.set(f"refresh_token:{refresh_token}", json.dumps(refresh_data), expire_seconds)

        return refresh_token

    def verify_token(self, token: str) -> TokenClaims:
        """Verify and decode JWT token"""
        # Check cache first for performance
        cached_payload = self.cache.get(f"token:{token}")
        if cached_payload:
            try:
                payload_dict = json.loads(cached_payload)
                claims = self._dict_to_token_claims(payload_dict)

                # Verify expiration
                if datetime.utcnow() > claims.expires_at:
                    self._revoke_token(token)
                    raise ValueError("Token expired")

                return claims
            except (json.JSONDecodeError, KeyError, ValueError):
                # Fall through to JWT verification
                pass

        # Check if token is revoked
        if self.cache.exists(f"revoked_token:{token}"):
            raise ValueError("Token revoked")

        # Decode JWT token using port
        try:
            claims = self.token_generator.verify_jwt_token(token)
            return claims
        except Exception as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise ValueError("Invalid token")

    def create_session(self, user: User, auth_request: AuthRequest) -> SessionInfo:
        """Create new user session with security tracking"""
        session_token = self.token_generator.generate_secure_token(32)
        expires_at = datetime.utcnow() + timedelta(hours=self.config.get_session_expire_hours())

        session = SessionInfo(
            id=self.token_generator.generate_secure_token(16),
            user_id=user.id,
            token=session_token,
            expires_at=expires_at,
            ip_address=auth_request.client_ip,
            user_agent=auth_request.user_agent,
            device_info=auth_request.device_info,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            is_active=True,
        )

        # Store session data
        session_data: dict[str, Any] = {
            "id": session.id,
            "user_id": session.user_id,
            "token": session.token,
            "expires_at": session.expires_at.isoformat(),
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_info": session.device_info,
            "created_at": (session.created_at.isoformat() if session.created_at else None),
            "last_activity": (session.last_activity.isoformat() if session.last_activity else None),
            "is_active": session.is_active,
        }

        expire_seconds = int(
            timedelta(hours=self.config.get_session_expire_hours()).total_seconds()
        )

        self.cache.set(f"session:{session.id}", json.dumps(session_data), expire_seconds)

        # Track active sessions for user
        self.cache.add_to_set(f"user_sessions:{user.id}", session.id)

        # Log security event
        self.security_events.log_session_created(user.id, session.id, auth_request)

        logger.info(f"Session created for user {user.username} from IP {session.ip_address}")
        return session

    def get_session(self, session_id: str) -> SessionInfo | None:
        """Retrieve user session"""
        session_data_str = self.cache.get(f"session:{session_id}")
        if not session_data_str:
            return None

        try:
            session_data = json.loads(session_data_str)

            # Convert back to SessionInfo
            session = SessionInfo(
                id=session_data["id"],
                user_id=session_data["user_id"],
                token=session_data["token"],
                expires_at=datetime.fromisoformat(session_data["expires_at"]),
                ip_address=session_data.get("ip_address"),
                user_agent=session_data.get("user_agent"),
                device_info=session_data.get("device_info"),
                created_at=(
                    datetime.fromisoformat(session_data["created_at"])
                    if session_data.get("created_at")
                    else None
                ),
                last_activity=(
                    datetime.fromisoformat(session_data["last_activity"])
                    if session_data.get("last_activity")
                    else None
                ),
                is_active=session_data.get("is_active", True),
            )

            # Check if session is expired
            if datetime.utcnow() > session.expires_at:
                self.terminate_session(session_id)
                return None

            return session

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Error parsing session data for {session_id}: {e}")
            return None

    def terminate_session(self, session_id: str) -> bool:
        """Terminate user session"""
        session = self.get_session(session_id)
        if not session:
            return False

        # Remove from cache
        self.cache.delete(f"session:{session_id}")

        # Remove from user's active sessions
        self.cache.remove_from_set(f"user_sessions:{session.user_id}", session_id)

        # Log security event
        self.security_events.log_session_terminated(
            session.user_id, session_id, "manual_termination"
        )

        logger.info(f"Session {session_id} terminated for user {session.user_id}")
        return True

    def terminate_all_user_sessions(self, user_id: str) -> int:
        """Terminate all sessions for a user"""
        session_ids = self.cache.get_set_members(f"user_sessions:{user_id}")
        if not session_ids:
            return 0

        terminated_count = 0
        for session_id in session_ids:
            if self.terminate_session(session_id):
                terminated_count += 1

        logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
        return terminated_count

    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        try:
            # Verify token to get expiration
            claims = self.token_generator.verify_jwt_token(token)

            # Add to revoked tokens with expiration
            if claims.expires_at:
                seconds_until_exp = int((claims.expires_at - datetime.utcnow()).total_seconds())

                if seconds_until_exp > 0:
                    self.cache.set(f"revoked_token:{token}", "revoked", seconds_until_exp)

            # Remove from token cache
            self._remove_cached_token(token)

            # Log security event
            if claims.token_id:
                self.security_events.log_token_revoked(
                    claims.user_id, claims.token_id, "manual_revocation"
                )

            return True

        except Exception as e:
            logger.warning(f"Error revoking token: {e}")
            return False

    def generate_password_reset_token(self, user_email: str) -> str:
        """Generate password reset token"""
        reset_token = self.token_generator.generate_secure_token(32)

        reset_data: dict[str, Any] = {
            "email": user_email,
            "created_at": datetime.utcnow().isoformat(),
            "used": False,
        }

        expire_seconds = self.config.get_password_reset_expire_minutes() * 60

        self.cache.set(f"password_reset:{reset_token}", json.dumps(reset_data), expire_seconds)

        # Log security event
        auth_request = AuthRequest()  # Empty request for password reset
        self.security_events.log_password_reset_requested(user_email, auth_request)

        logger.info(f"Password reset token generated for {user_email}")
        return reset_token

    def verify_password_reset_token(self, token: str) -> dict[str, Any] | None:
        """Verify password reset token"""
        try:
            reset_data_str = self.cache.get(f"password_reset:{token}")
            if not reset_data_str:
                return None

            reset_data = json.loads(reset_data_str)

            # Check if token was already used
            if reset_data.get("used", False):
                return None

            return reset_data

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error verifying reset token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using valid refresh token"""
        # Validate refresh token
        refresh_data_str = self.cache.get(f"refresh_token:{refresh_token}")
        if not refresh_data_str:
            raise ValueError("Invalid refresh token")

        try:
            refresh_data = json.loads(refresh_data_str)
            user_id = refresh_data.get("user_id")
            session_id = refresh_data.get("session_id")

            if not user_id or not session_id:
                raise ValueError("Invalid refresh token data")

            # Verify session still exists
            session = self.get_session(session_id)
            if not session:
                raise ValueError("Session expired")

            # Get user from repository
            user = self.user_repository.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Create new access token
            new_access_token = self.create_access_token(
                user,
                expires_delta=timedelta(minutes=self.config.get_access_token_expire_minutes()),
                session_id=session_id,
            )

            logger.info(f"Access token refreshed for user {user_id}")
            return new_access_token

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error refreshing access token: {e}")
            raise ValueError("Token refresh failed")

    def _cache_token(self, token: str, claims: TokenClaims, expire: datetime) -> None:
        """Cache token for fast validation"""
        seconds_until_exp = int((expire - datetime.utcnow()).total_seconds())
        if seconds_until_exp > 0:
            claims_dict = self._token_claims_to_dict(claims)
            self.cache.set(f"token:{token}", json.dumps(claims_dict), seconds_until_exp)

    def _remove_cached_token(self, token: str) -> None:
        """Remove token from cache"""
        self.cache.delete(f"token:{token}")

    def _revoke_token(self, token: str) -> None:
        """Internal method to revoke expired token"""
        self.cache.delete(f"token:{token}")
        self.cache.set(f"revoked_token:{token}", "expired", 3600)

    def _token_claims_to_dict(self, claims: TokenClaims) -> dict[str, Any]:
        """Convert TokenClaims to dictionary for JSON serialization"""
        return {
            "user_id": claims.user_id,
            "email": claims.email,
            "username": claims.username,
            "role": claims.role,
            "status": claims.status,
            "session_id": claims.session_id,
            "mfa_verified": claims.mfa_verified,
            "auth_provider": claims.auth_provider,
            "issued_at": claims.issued_at.isoformat() if claims.issued_at else None,
            "expires_at": claims.expires_at.isoformat() if claims.expires_at else None,
            "token_id": claims.token_id,
        }

    def _dict_to_token_claims(self, data: dict[str, Any]) -> TokenClaims:
        """Convert dictionary to TokenClaims"""
        return TokenClaims(
            user_id=data["user_id"],
            email=data["email"],
            username=data["username"],
            role=data["role"],
            status=data["status"],
            session_id=data.get("session_id"),
            mfa_verified=data.get("mfa_verified", False),
            auth_provider=data.get("auth_provider", "local"),
            issued_at=(
                datetime.fromisoformat(data["issued_at"]) if data.get("issued_at") else None
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
            ),
            token_id=data.get("token_id"),
        )
