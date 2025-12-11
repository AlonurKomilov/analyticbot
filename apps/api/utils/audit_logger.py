"""
Admin Audit Logger

Utility for logging administrative actions to the audit log.
Use this to track all admin operations for security and compliance.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import Request

logger = logging.getLogger(__name__)


async def log_admin_action(
    admin_user_id: int,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    request: Optional[Request] = None,
    success: bool = True,
    error_message: Optional[str] = None,
) -> bool:
    """
    Log an administrative action to the audit log.

    Args:
        admin_user_id: ID of the admin performing the action
        action: Type of action (e.g., 'user_suspend', 'channel_delete', 'settings_update')
        resource_type: Type of resource affected (e.g., 'user', 'channel', 'settings')
        resource_id: ID of the resource affected
        details: Additional details about the action (JSON)
        request: FastAPI request object for IP/user-agent extraction
        success: Whether the action was successful
        error_message: Error message if action failed

    Returns:
        True if logged successfully, False otherwise

    Example:
        await log_admin_action(
            admin_user_id=current_user["id"],
            action="user_suspend",
            resource_type="user",
            resource_id=str(user_id),
            details={"reason": "Violation of terms"},
            request=request,
        )
    """
    try:
        from apps.di.analytics_container import get_database_pool

        pool = await get_database_pool()

        # Extract IP and user agent from request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO admin_audit_log (
                    admin_user_id,
                    action,
                    resource_type,
                    resource_id,
                    details,
                    ip_address,
                    user_agent,
                    timestamp,
                    success,
                    error_message
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                admin_user_id,
                action,
                resource_type,
                str(resource_id) if resource_id else None,
                details,
                ip_address,
                user_agent,
                datetime.utcnow(),
                success,
                error_message,
            )

        logger.info(
            f"Audit log: admin={admin_user_id} action={action} "
            f"resource={resource_type}/{resource_id} success={success}"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
        return False


# Common action types for consistency
class AdminActions:
    """Constants for common admin action types"""

    # User actions
    USER_VIEW = "user_view"
    USER_SUSPEND = "user_suspend"
    USER_UNSUSPEND = "user_unsuspend"
    USER_DELETE = "user_delete"
    USER_CREDITS_ADJUST = "user_credits_adjust"
    USER_ROLE_CHANGE = "user_role_change"

    # Channel actions
    CHANNEL_VIEW = "channel_view"
    CHANNEL_SUSPEND = "channel_suspend"
    CHANNEL_UNSUSPEND = "channel_unsuspend"
    CHANNEL_DELETE = "channel_delete"
    CHANNEL_FORCE_SYNC = "channel_force_sync"

    # Bot actions
    BOT_VIEW = "bot_view"
    BOT_SUSPEND = "bot_suspend"
    BOT_ACTIVATE = "bot_activate"
    BOT_RATE_LIMIT_UPDATE = "bot_rate_limit_update"

    # System actions
    SETTINGS_VIEW = "settings_view"
    SETTINGS_UPDATE = "settings_update"
    SYSTEM_HEALTH_CHECK = "system_health_check"

    # Auth actions
    ADMIN_LOGIN = "admin_login"
    ADMIN_LOGOUT = "admin_logout"
    ADMIN_LOGIN_FAILED = "admin_login_failed"


# Resource types for consistency
class ResourceTypes:
    """Constants for resource types"""

    USER = "user"
    CHANNEL = "channel"
    BOT = "bot"
    SETTINGS = "settings"
    SYSTEM = "system"
