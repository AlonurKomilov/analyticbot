"""
Profile and permissions management endpoints.

This module handles user profile retrieval, permissions checking,
MFA status, and administrative role information.
"""

import json
import logging
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.middleware.auth import get_current_user
from core.security_engine import get_security_manager
from core.security_engine.decorators import require_analytics_access, require_permission
from core.security_engine.mfa import MFAManager
from core.security_engine.permissions import Permission

from .models import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# MFA manager instance
mfa_manager = MFAManager()


def get_mfa_manager() -> MFAManager:
    """Get MFA manager instance"""
    return mfa_manager


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(request: Request):
    """
    Get current user's profile information.
    Uses JWT token to identify user, fetches additional data from database.

    NOTE: Caching REMOVED - was causing cross-user data leaks because
    cache key was not properly including user_id from JWT token.
    """
    start_time = time.time()
    logger.info("⏱️ /auth/me endpoint called")

    try:
        # Extract user info from JWT token
        from apps.api.middleware.auth import get_current_user_id_from_request
        from apps.di import get_container

        step1 = time.time()
        user_id = await get_current_user_id_from_request(request)
        logger.info(f"⏱️ get_current_user_id_from_request took {(time.time() - step1) * 1000:.2f}ms")

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            step2 = time.time()
            token = auth_header[7:]
            security_manager = get_security_manager()
            claims = security_manager.verify_token(token)
            logger.info(f"⏱️ Token verification took {(time.time() - step2) * 1000:.2f}ms")

            # Fetch additional user data from database (full_name, telegram info, password status)
            step3 = time.time()
            container = get_container()
            pool = await container.database.asyncpg_pool()

            full_name = claims.get("full_name")
            has_password = False
            telegram_id = None
            telegram_username = None
            credit_balance = 0.0

            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT
                        full_name,
                        hashed_password IS NOT NULL as has_password,
                        telegram_id,
                        COALESCE(credit_balance, 0) as credit_balance,
                        CASE
                            WHEN telegram_id IS NOT NULL THEN username
                            ELSE NULL
                        END as telegram_username
                    FROM users WHERE id = $1
                """,
                    int(user_id),
                )
                if row:
                    full_name = row["full_name"] or full_name
                    has_password = row["has_password"] or False
                    telegram_id = row["telegram_id"]
                    telegram_username = row["telegram_username"]
                    credit_balance = float(row["credit_balance"] or 0)

            logger.info(f"⏱️ Database lookup took {(time.time() - step3) * 1000:.2f}ms")

            # Extract user info from JWT claims + database
            response = UserResponse(
                id=str(claims.get("sub", user_id)),
                email=claims.get("email", f"user_{user_id}@example.com"),
                username=claims.get("username", f"user_{user_id}"),
                full_name=full_name,
                role=claims.get("role", "user"),
                status=claims.get("status", "active"),
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                has_password=has_password,
                telegram_id=telegram_id,
                telegram_username=telegram_username,
                credit_balance=credit_balance,
            )

            total_time = (time.time() - start_time) * 1000
            logger.info(f"⏱️ /auth/me TOTAL time: {total_time:.2f}ms")
            return response
        else:
            raise HTTPException(status_code=401, detail="Missing authentication token")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")


@router.get("/mfa/status")
async def get_mfa_status(
    current_user: dict[str, Any] = Depends(get_current_user),
    mfa_manager: MFAManager = Depends(get_mfa_manager),
):
    """
    Get MFA status for current user
    """
    try:
        # Check if MFA is enabled using MFAManager's cache access methods
        # Use _get_from_cache method instead of redis_client
        mfa_data_str = mfa_manager._get_from_cache(f"mfa_data:{current_user['id']}")

        if mfa_data_str and isinstance(mfa_data_str, str):
            mfa_data = json.loads(mfa_data_str)
            return {
                "enabled": True,
                "enabled_at": mfa_data.get("enabled_at"),
                "backup_codes_remaining": len(mfa_data.get("backup_codes", [])),
            }
        else:
            return {"enabled": False, "enabled_at": None, "backup_codes_remaining": 0}

    except Exception as e:
        logger.error(f"MFA status check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MFA status",
        )


@router.get("/profile/permissions", response_model=dict)
@require_permission(Permission.VIEW_CONTENT)
async def get_user_permissions(current_user: dict = Depends(get_current_user)):
    """
    Get current user's permissions - demonstrates new permission system.

    Requires: Permission.VIEW_CONTENT
    """
    try:
        from core.security_engine.role_hierarchy import role_hierarchy_service

        user_info = role_hierarchy_service.get_user_role_info(
            role=current_user.get("role", "user"),
            additional_permissions=current_user.get("additional_permissions", []),
            migration_profile=current_user.get("migration_profile"),
        )

        return {
            "user_id": current_user.get("id"),
            "username": current_user.get("username"),
            "role": user_info.role,
            "role_level": user_info.role_level,
            "is_administrative": user_info.is_administrative,
            "permissions": [perm.value for perm in user_info.permissions],
            "migration_profile": user_info.migration_profile,
            "total_permissions": len(user_info.permissions),
        }

    except Exception as e:
        logger.error(f"Permission check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user permissions",
        )


@router.get("/admin/user-roles", response_model=dict)
@require_analytics_access()
async def get_role_hierarchy(current_user: dict = Depends(get_current_user)):
    """
    Get role hierarchy information - demonstrates analytics permission.

    Requires: Permission.VIEW_ANALYTICS (via @require_analytics_access)
    """
    try:
        from core.security_engine.role_hierarchy import role_hierarchy_service

        hierarchy = role_hierarchy_service.get_role_hierarchy_display()
        # Removed include_deprecated=True - only show active roles
        available_roles = role_hierarchy_service.get_available_roles()

        return {
            "current_user": current_user.get("username"),
            "role_hierarchy": hierarchy,
            "available_roles": available_roles,
            "new_role_system": True,
            "permission_count": len(Permission),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Role hierarchy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get role hierarchy",
        )


@router.put("/profile")
async def update_profile(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Update user profile information.

    Supports updating: username, full_name, email, password
    """
    try:
        from apps.api.middleware.auth import get_user_repository
        from core.security_engine.models import pwd_context

        body = await request.json()
        user_id = int(current_user["id"])

        # Get repository
        user_repo = await get_user_repository()

        # Build updates dict
        updates = {}

        if "username" in body and body["username"]:
            updates["username"] = body["username"]

        if "full_name" in body and body["full_name"]:
            updates["full_name"] = body["full_name"]

        if "email" in body and body["email"]:
            # Validate email format
            import re

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, body["email"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format",
                )
            updates["email"] = body["email"]

        if "password" in body and body["password"]:
            # Hash the new password
            hashed_password = pwd_context.hash(body["password"])
            updates["hashed_password"] = hashed_password
            # When user sets a password, activate their account if pending
            # This allows Telegram users to complete setup
            if current_user.get("status") == "pending_verification":
                updates["status"] = "active"
                logger.info(
                    f"Activating user {user_id} - password set by pending_verification user"
                )

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update",
            )

        # Update user in database
        success = await user_repo.update_user(user_id, **updates)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile",
            )

        # Get updated user data
        updated_user = await user_repo.get_user_by_id(user_id)

        logger.info(f"Profile updated for user {user_id}: {list(updates.keys())}")

        return {"message": "Profile updated successfully", "user": updated_user}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}",
        )
