"""
🔒 FastAPI Authentication Utilities

Provides FastAPI-specific authentication utilities and dependencies.
Maps core domain authentication to FastAPI HTTP layer.
"""

from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.repositories.interfaces import UserRepository
from core.security_engine import (
    AuthenticationError,
    SecurityManager,
)
from core.security_engine import LegacyUserRole as UserRole

# Import new role system with backwards compatibility

# HTTP Bearer security scheme
security_scheme = HTTPBearer()


class AuthError(HTTPException):
    """FastAPI-specific authentication error"""

    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            status_code=status_code, detail=detail, headers={"WWW-Authenticate": "Bearer"}
        )


class FastAPIAuthUtils:
    """
    FastAPI-specific authentication utilities

    Bridges core domain authentication with FastAPI HTTP layer.
    Maps domain exceptions to HTTP exceptions.
    """

    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager

    def verify_jwt_token(self, token: str) -> dict[str, Any]:
        """
        Verify JWT token and return payload

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            AuthError: If token is invalid
        """
        try:
            return self.security_manager.verify_token(token)
        except AuthenticationError as e:
            raise AuthError(f"Invalid token: {str(e)}")

    def create_access_token(self, user: Any, expires_minutes: int | None = None) -> str:
        """
        Create access token for authenticated user

        Args:
            user: User object
            expires_minutes: Optional custom expiration time

        Returns:
            JWT access token string
        """
        from datetime import timedelta

        expires_delta = timedelta(minutes=expires_minutes) if expires_minutes else None
        return self.security_manager.create_access_token(user, expires_delta)

    def create_refresh_token(
        self, user_id: str | int, session_token: str, remember_me: bool = False
    ) -> str:
        """
        Create refresh token for user session

        🆕 Phase 3.2: Added remember_me parameter

        Args:
            user_id: User ID (string or int)
            session_token: Session token
            remember_me: If True, create long-lived token (30 days vs 7 days)

        Returns:
            JWT refresh token string
        """
        return self.security_manager.create_refresh_token(
            str(user_id), session_token, remember_me=remember_me
        )

    def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        """
        Create new access token from refresh token with rotation

        🔄 NEW: Returns both access_token and refresh_token (rotated)

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dictionary with access_token, refresh_token, and token_type

        Raises:
            AuthError: If refresh token is invalid
        """
        try:
            return self.security_manager.refresh_access_token(refresh_token)
        except AuthenticationError as e:
            raise AuthError(f"Token refresh failed: {str(e)}")

    def revoke_user_sessions(self, user_id: str) -> None:
        """
        Revoke all user sessions

        Args:
            user_id: User ID to revoke sessions for
        """
        self.security_manager.revoke_user_sessions(user_id)

    async def get_user_from_token(
        self, credentials: HTTPAuthorizationCredentials, user_repo: UserRepository
    ) -> dict[str, Any]:
        """
        Extract and validate user from JWT token with database lookup

        Args:
            credentials: HTTP Bearer credentials
            user_repo: User repository for database lookup

        Returns:
            User dictionary from database

        Raises:
            AuthError: If token is invalid or user not found
        """
        # Verify token
        payload = self.verify_jwt_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            raise AuthError("Invalid token: missing user ID")

        # Get user from database
        user = await user_repo.get_user_by_id(int(user_id))
        if not user:
            raise AuthError("User not found")

        return user

    @staticmethod
    def check_user_role(user: dict[str, Any], required_role: UserRole) -> bool:
        """
        Check if user has required role with hierarchy support

        Args:
            user: User dictionary
            required_role: Required role

        Returns:
            True if user has required role or higher
        """
        try:
            user_role = UserRole(user.get("role"))

            # Role hierarchy: OWNER > ADMIN > MODERATOR > USER > VIEWER
            # Updated for new 5-role system
            role_levels = {
                UserRole.VIEWER: 0,
                UserRole.USER: 1,
                UserRole.MODERATOR: 2,
                UserRole.ADMIN: 3,
                UserRole.OWNER: 5,
                # Legacy mappings for backwards compatibility
                UserRole.GUEST: 0,  # Maps to VIEWER
                UserRole.READONLY: 0,  # Maps to VIEWER
                UserRole.ANALYST: 1,  # Maps to USER
            }

            return role_levels.get(user_role, 0) >= role_levels.get(required_role, 0)
        except (ValueError, KeyError):
            return False


# FastAPI dependency functions
def get_auth_utils() -> FastAPIAuthUtils:
    """FastAPI dependency to get auth utils instance"""
    # This should be injected via DI container in production
    from core.security_engine import SecurityManager

    security_manager = SecurityManager()
    return FastAPIAuthUtils(security_manager)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    auth_utils: FastAPIAuthUtils = Depends(get_auth_utils),
    # user_repo should also be injected via DI
) -> dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    # This is a placeholder - should use proper DI container
    raise NotImplementedError("Use proper DI container integration")


# Create default auth_utils instance using container singleton (with Redis cache!)
from core.security_engine.container import get_security_manager

auth_utils = FastAPIAuthUtils(get_security_manager())
