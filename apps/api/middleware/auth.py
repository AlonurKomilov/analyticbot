"""
🔒 Authentication Middleware for API Routes

Provides JWT authentication and channel ownership validation
using the existing SecurityManager from core.security_engine.
"""

import logging
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from apps.shared.di import container
from core.repositories.interfaces import ChannelRepository, UserRepository
from core.security_engine import SecurityManager, get_security_manager
from core.security_engine.models import User, UserRole
from core.security_engine.rbac import Permission, RBACManager
from infra.db.repositories.channel_repository import AsyncpgChannelRepository
from infra.db.repositories.user_repository import AsyncpgUserRepository

logger = logging.getLogger(__name__)

# Security dependencies
security = HTTPBearer()
security_manager = SecurityManager()
rbac_manager = RBACManager()


def get_security_manager() -> SecurityManager:
    """Get SecurityManager instance"""
    return security_manager


def get_rbac_manager() -> RBACManager:
    """Get RBACManager instance"""
    return rbac_manager


async def get_user_repository() -> UserRepository:
    """Get user repository dependency"""
    try:
        pool = await container().asyncpg_pool()
        return AsyncpgUserRepository(pool)
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )


async def get_channel_repository() -> ChannelRepository:
    """Get channel repository dependency"""
    try:
        pool = await container().asyncpg_pool()
        return AsyncpgChannelRepository(pool)
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> dict[str, Any]:
    """
    Extract and validate current user from JWT token

    Args:
        credentials: HTTP Bearer token
        user_repo: User repository for database access

    Returns:
        User dictionary with user information

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Verify JWT token using SecurityManager
        payload = get_security_manager().verify_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            logger.warning("JWT token missing user ID")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = await user_repo.get_user_by_id(int(user_id))
        if not user:
            logger.warning(f"User not found for ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Authenticated user: {user.get('username', user_id)}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_channel_access(
    channel_id: int,
    current_user: dict[str, Any] = Depends(get_current_user),
    channel_repo: ChannelRepository = Depends(get_channel_repository),
) -> int:
    """
    Validate that the current user has access to the specified channel

    Args:
        channel_id: Channel ID to validate access for
        current_user: Current authenticated user
        channel_repo: Channel repository for database access

    Returns:
        channel_id if access is granted

    Raises:
        HTTPException: If user doesn't have access to the channel
    """
    try:
        user_id = current_user["id"]

        # Get all channels owned by the user
        user_channels = await channel_repo.get_user_channels(user_id)
        user_channel_ids = [ch["id"] for ch in user_channels]

        if channel_id not in user_channel_ids:
            logger.warning(
                f"User {user_id} attempted to access channel {channel_id} without permission"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to channel {channel_id}. You can only access your own channels.",
            )

        logger.info(f"User {user_id} granted access to channel {channel_id}")
        return channel_id

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel access validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating channel access",
        )


async def get_current_user_id(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> int:
    """
    Simple dependency to get just the user ID

    Args:
        current_user: Current authenticated user

    Returns:
        User ID as integer
    """
    return current_user["id"]


async def require_admin_user(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Require user to have admin role

    Args:
        current_user: Current authenticated user

    Returns:
        User dictionary if admin role

    Raises:
        HTTPException: If user is not admin
    """
    user_role = current_user.get("role", "user")
    if user_role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def require_permission(permission: Permission):
    """
    Create a dependency that requires a specific permission

    Args:
        permission: Required permission

    Returns:
        Dependency function that checks user permission
    """

    async def permission_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
        rbac_manager: RBACManager = Depends(get_rbac_manager),
    ) -> dict[str, Any]:
        # Convert dict to User object for RBAC check
        user = User(
            id=str(current_user["id"]),
            email=current_user["email"],
            username=current_user["username"],
            role=UserRole(current_user.get("role", "user")),
        )

        # Check permission
        if not rbac_manager.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )

        return current_user

    return permission_checker


def require_role(required_role: UserRole):
    """
    Create a dependency that requires a specific role or higher

    Args:
        required_role: Required user role

    Returns:
        Dependency function that checks user role
    """

    async def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
        rbac_manager: RBACManager = Depends(get_rbac_manager),
    ) -> dict[str, Any]:
        # Convert dict to User object for RBAC check
        user = User(
            id=str(current_user["id"]),
            email=current_user["email"],
            username=current_user["username"],
            role=UserRole(current_user.get("role", "user")),
        )

        # Check if user has required role or higher
        if not rbac_manager.has_role(user, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role.value}' or higher required",
            )

        return current_user

    return role_checker


def require_resource_access(permission: Permission, resource_param: str = "resource_id"):
    """
    Create a dependency that requires permission for a specific resource

    Args:
        permission: Required permission
        resource_param: Name of the path parameter containing resource ID

    Returns:
        Dependency function that checks resource-level permission
    """

    async def resource_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
        rbac_manager: RBACManager = Depends(get_rbac_manager),
    ) -> dict[str, Any]:
        # Convert dict to User object for RBAC check
        user = User(
            id=str(current_user["id"]),
            email=current_user["email"],
            username=current_user["username"],
            role=UserRole(current_user.get("role", "user")),
        )

        # For now, check general permission (resource-specific checks can be added later)
        if not rbac_manager.has_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required for this resource",
            )

        return current_user

    return resource_checker


# Common permission dependencies for easy reuse
require_analytics_read = require_permission(Permission.ANALYTICS_READ)
require_analytics_create = require_permission(Permission.ANALYTICS_CREATE)
require_analytics_update = require_permission(Permission.ANALYTICS_UPDATE)
require_analytics_delete = require_permission(Permission.ANALYTICS_DELETE)
require_analytics_export = require_permission(Permission.ANALYTICS_EXPORT)

require_report_read = require_permission(Permission.REPORT_READ)
require_report_create = require_permission(Permission.REPORT_CREATE)
require_report_update = require_permission(Permission.REPORT_UPDATE)
require_report_delete = require_permission(Permission.REPORT_DELETE)

require_user_read = require_permission(Permission.USER_READ)
require_user_create = require_permission(Permission.USER_CREATE)
require_user_update = require_permission(Permission.USER_UPDATE)
require_user_delete = require_permission(Permission.USER_DELETE)

require_settings_read = require_permission(Permission.SETTINGS_READ)
require_settings_update = require_permission(Permission.SETTINGS_UPDATE)

# Role-based dependencies
require_analyst_role = require_role(UserRole.ANALYST)
require_moderator_role = require_role(UserRole.MODERATOR)
require_admin_role = require_role(UserRole.ADMIN)
