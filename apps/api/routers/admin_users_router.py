"""
Admin Users Router - User Administration

Handles administrative user operations including user management, permissions, and monitoring.
Clean architecture: Single responsibility for user administration.

Domain: Admin user management operations
Path: /admin/users/*
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.api.middleware.auth import (
    get_current_user,
    require_admin_user,
)
from apps.api.services.channel_management_service import ChannelManagementService
from apps.di.analytics_container import get_channel_management_service, get_database_pool
from apps.shared.performance import performance_timer

logger = logging.getLogger(__name__)


# Dependency function for channel service
def get_channel_service():
    """Get channel management service instance - using mock for now"""

    # Create a simple mock implementation to avoid complex dependencies
    class MockChannelService:
        async def get_user_channels(self, user_id: int):
            return {
                "user_id": user_id,
                "username": f"user_{user_id}",
                "channels": [
                    {"id": 1, "name": "Sample Channel", "telegram_id": 12345},
                    {"id": 2, "name": "Demo Channel", "telegram_id": 67890},
                ],
                "last_activity": "2024-01-01T12:00:00Z",
            }

    return MockChannelService()


router = APIRouter(
    prefix="/admin/users",
    tags=["Admin - User Management"],
    responses={404: {"description": "Not found"}},
)

# === ADMIN USER MODELS ===


class UserChannelInfo(BaseModel):
    user_id: int
    username: str | None = None
    total_channels: int = 0
    active_channels: int = 0
    channels: list[dict[str, Any]] = Field(default_factory=list)
    last_activity: datetime | None = None


class AdminUserInfo(BaseModel):
    id: int
    email: str
    username: str | None = None
    role: str = "user"
    status: str = "active"
    created_at: datetime
    last_login: datetime | None = None
    channels_count: int = 0
    auth_provider: str = "local"


class AdminUserDetail(BaseModel):
    """Detailed user info for admin view"""

    id: int
    email: str
    username: str | None = None
    full_name: str | None = None
    role: str = "user"
    status: str = "active"
    created_at: datetime
    last_login: datetime | None = None
    channels_count: int = 0
    total_posts: int = 0
    total_views: int = 0
    subscription_tier: str | None = None
    auth_provider: str = "local"  # 'local' (email/password), 'telegram', 'google', etc.


class UserStatusUpdate(BaseModel):
    """Model for updating user status"""

    status: str  # 'active', 'suspended', 'pending_verification'
    reason: str | None = None


class SuspendUserRequest(BaseModel):
    """Request model for suspending a user"""

    reason: str = Field(..., min_length=5, max_length=500, description="Reason for suspension")


class SuspensionInfo(BaseModel):
    """Suspension details for a user"""

    status: str
    suspension_reason: str | None = None
    suspended_at: datetime | None = None
    suspended_by: int | None = None


class CreditAdjustRequest(BaseModel):
    """Request model for adjusting user credits"""

    amount: float = Field(..., description="Amount to add (positive) or subtract (negative)")
    reason: str = Field(..., min_length=5, max_length=500, description="Reason for adjustment")


class UserCreditInfo(BaseModel):
    """User credit information for admin"""

    user_id: int
    username: str | None
    email: str | None
    credit_balance: float
    lifetime_earned: float
    lifetime_spent: float


# === ADMIN USER ENDPOINTS ===


@router.get("", response_model=list[AdminUserInfo])
async def get_all_users(
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
):
    """
    ## 👥 Get All Users (Admin)

    Retrieve all users in the system with administrative details.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            users = await conn.fetch(
                """
                SELECT
                    u.id,
                    u.email,
                    u.username,
                    u.role,
                    u.status,
                    u.created_at,
                    u.last_login,
                    u.auth_provider,
                    COUNT(c.id) as channels_count
                FROM users u
                LEFT JOIN channels c ON u.id = c.user_id
                GROUP BY u.id, u.email, u.username, u.role, u.status, u.created_at, u.last_login, u.auth_provider
                ORDER BY u.created_at DESC
                LIMIT $1 OFFSET $2
            """,
                limit,
                offset,
            )

            return [
                AdminUserInfo(
                    id=user["id"],
                    email=user["email"] or "",
                    username=user["username"],
                    role=user["role"] or "user",
                    status=user["status"] or "active",
                    created_at=user["created_at"],
                    last_login=user["last_login"],
                    channels_count=user["channels_count"],
                    auth_provider=user["auth_provider"] or "local",
                )
                for user in users
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin users fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@router.get("/{user_id}", response_model=AdminUserDetail)
async def get_user_detail(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 👤 Get User Details (Admin)

    Retrieve detailed information about a specific user.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Get basic user info
            user = await conn.fetchrow(
                """
                SELECT
                    u.id,
                    u.email,
                    u.username,
                    u.full_name,
                    u.role,
                    u.status,
                    u.created_at,
                    u.last_login,
                    u.auth_provider,
                    COUNT(DISTINCT c.id) as channels_count
                FROM users u
                LEFT JOIN channels c ON u.id = c.user_id
                WHERE u.id = $1
                GROUP BY u.id
            """,
                user_id,
            )

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get posts count (excluding deleted) and views separately for accuracy
            stats = await conn.fetchrow(
                """
                SELECT
                    COUNT(DISTINCT p.msg_id) FILTER (WHERE p.is_deleted = false) as total_posts,
                    COALESCE((
                        SELECT SUM(latest_views.views)
                        FROM (
                            SELECT DISTINCT ON (pm.channel_id, pm.msg_id) pm.views
                            FROM post_metrics pm
                            INNER JOIN channels c ON pm.channel_id = c.id
                            WHERE c.user_id = $1
                            ORDER BY pm.channel_id, pm.msg_id, pm.snapshot_time DESC
                        ) latest_views
                    ), 0) as total_views
                FROM posts p
                INNER JOIN channels c ON p.channel_id = c.id
                WHERE c.user_id = $1
            """,
                user_id,
            )

            return AdminUserDetail(
                id=user["id"],
                email=user["email"] or "",
                username=user["username"],
                full_name=user["full_name"],
                role=user["role"] or "user",
                status=user["status"] or "active",
                created_at=user["created_at"],
                last_login=user["last_login"],
                channels_count=user["channels_count"],
                total_posts=stats["total_posts"] if stats else 0,
                total_views=int(stats["total_views"] or 0) if stats else 0,
                auth_provider=user["auth_provider"] or "local",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user detail fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user details")


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    request: SuspendUserRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⏸️ Suspend User (Admin)

    Suspend a user account, preventing them from logging in.
    Also stops their MTProto data collection workers to save system resources.

    **Admin Only**: Requires admin role

    **Request Body:**
    - reason: Explanation for why the user is being suspended (required)
    """
    try:
        await require_admin_user(current_user)

        # Prevent suspending yourself
        if int(current_user["id"]) == user_id:
            raise HTTPException(status_code=400, detail="Cannot suspend your own account")

        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow(
                "SELECT id, role, status, username FROM users WHERE id = $1", user_id
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Prevent suspending other admins
            if user["role"] == "admin" or user["role"] == "owner":
                raise HTTPException(status_code=403, detail="Cannot suspend admin users")

            # Already suspended check
            if user["status"] == "suspended":
                raise HTTPException(status_code=400, detail="User is already suspended")

            suspended_at = datetime.now()

            # Update user status with suspension details
            await conn.execute(
                """
                UPDATE users
                SET status = $1,
                    suspension_reason = $2,
                    suspended_at = $3,
                    suspended_by = $4
                WHERE id = $5
            """,
                "suspended",
                request.reason,
                suspended_at,
                int(current_user["id"]),
                user_id,
            )

            # Disable all user's channels to stop MTProto data collection
            disabled_channels = await conn.execute(
                """
                UPDATE channels
                SET is_active = false,
                    updated_at = NOW()
                WHERE user_id = $1 AND is_active = true
            """,
                user_id,
            )

            channels_disabled = int(disabled_channels.split()[-1]) if disabled_channels else 0

            logger.warning(
                f"ADMIN SUSPENSION: User {user_id} ({user['username']}) suspended by admin {current_user['id']}. "
                f"Reason: {request.reason}. Channels disabled: {channels_disabled}"
            )

            return {
                "message": "User suspended successfully",
                "user_id": user_id,
                "username": user["username"],
                "status": "suspended",
                "reason": request.reason,
                "suspended_by": current_user["id"],
                "suspended_at": suspended_at.isoformat(),
                "channels_disabled": channels_disabled,
                "mtproto_stopped": True,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User suspension failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to suspend user")


@router.post("/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ▶️ Unsuspend User (Admin)

    Reactivate a suspended user account.
    Also re-enables their MTProto data collection workers.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow(
                "SELECT id, status, username, suspension_reason, suspended_at FROM users WHERE id = $1",
                user_id,
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check if user is actually suspended
            if user["status"] != "suspended":
                raise HTTPException(status_code=400, detail="User is not suspended")

            # Update status and clear suspension fields
            await conn.execute(
                """
                UPDATE users
                SET status = $1,
                    suspension_reason = NULL,
                    suspended_at = NULL,
                    suspended_by = NULL
                WHERE id = $2
            """,
                "active",
                user_id,
            )

            # Re-enable all user's channels to resume MTProto data collection
            enabled_channels = await conn.execute(
                """
                UPDATE channels
                SET is_active = true,
                    updated_at = NOW()
                WHERE user_id = $1 AND is_active = false
            """,
                user_id,
            )

            channels_enabled = int(enabled_channels.split()[-1]) if enabled_channels else 0

            logger.info(
                f"ADMIN UNSUSPENSION: User {user_id} ({user['username']}) unsuspended by admin {current_user['id']}. "
                f"Channels re-enabled: {channels_enabled}"
            )

            return {
                "message": "User unsuspended successfully",
                "user_id": user_id,
                "username": user["username"],
                "status": "active",
                "previous_suspension_reason": user["suspension_reason"],
                "was_suspended_at": user["suspended_at"].isoformat()
                if user["suspended_at"]
                else None,
                "unsuspended_by": current_user["id"],
                "unsuspended_at": datetime.now().isoformat(),
                "channels_enabled": channels_enabled,
                "mtproto_resumed": True,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User unsuspension failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsuspend user")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🗑️ Delete User (Admin)

    Permanently delete a user and all their associated data.

    **Admin Only**: Requires admin role
    **⚠️ WARNING**: This action is permanent and cannot be undone.
    """
    try:
        await require_admin_user(current_user)

        # Prevent deleting yourself
        if int(current_user["id"]) == user_id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")

        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow(
                "SELECT id, role, username FROM users WHERE id = $1", user_id
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Prevent deleting other admins
            if user["role"] == "admin" or user["role"] == "owner":
                raise HTTPException(status_code=403, detail="Cannot delete admin users")

            # Delete user's channels first (cascade)
            await conn.execute("DELETE FROM channels WHERE user_id = $1", user_id)

            # Delete the user
            await conn.execute("DELETE FROM users WHERE id = $1", user_id)

            logger.warning(
                f"ADMIN DELETION: User {user_id} ({user['username']}) deleted by admin {current_user['id']}"
            )

            return {
                "message": "User permanently deleted",
                "user_id": user_id,
                "deleted_by": current_user["id"],
                "deleted_at": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")


@router.get("/{user_id}/channels", response_model=UserChannelInfo)
async def get_user_channels_admin(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(get_channel_management_service),
):
    """
    ## 👤 Get User Channels (Admin)

    Retrieve all channels owned by a specific user with administrative details.

    **Admin Only**: Requires admin role

    **Parameters:**
    - user_id: ID of the user to inspect

    **Returns:**
    - User channel information and statistics
    """
    try:
        await require_admin_user(current_user)

        with performance_timer("admin_user_channels_fetch"):
            user_channels = await channel_service.get_user_channels(user_id=user_id)

            if not user_channels:
                raise HTTPException(status_code=404, detail="User not found or has no channels")

            # Process the channels data
            channels_list = []
            active_count = 0

            for channel in user_channels:
                channel_info = {
                    "id": channel.id,
                    "name": channel.name,
                    "username": getattr(channel, "username", None),
                    "is_active": channel.is_active,
                    "subscriber_count": channel.subscriber_count,
                    "created_at": channel.created_at.isoformat()
                    if channel.created_at
                    else datetime.now().isoformat(),
                    "total_posts": getattr(channel, "total_posts", 0),
                    "total_views": getattr(channel, "total_views", 0),
                }
                channels_list.append(channel_info)

                if channel.is_active:
                    active_count += 1

            logger.info(
                f"Admin fetched user channels: user_id={user_id}, total={len(channels_list)}"
            )

            return UserChannelInfo(
                user_id=user_id,
                username=f"User_{user_id}",  # We don't have username in channel service
                total_channels=len(channels_list),
                active_channels=active_count,
                channels=channels_list,
                last_activity=None,  # We don't have this info in channel service
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user channels for admin")


# === CREDIT MANAGEMENT ENDPOINTS ===


@router.get("/{user_id}/credits", response_model=UserCreditInfo)
async def get_user_credits(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 💰 Get User Credit Info (Admin)

    Retrieve credit balance and statistics for a specific user.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Get user info with credit balance
            user = await conn.fetchrow(
                """
                SELECT
                    u.id, u.username, u.email,
                    COALESCE(u.credit_balance, 0) as credit_balance
                FROM users u
                WHERE u.id = $1
            """,
                user_id,
            )

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Get lifetime stats from user_credits table
            credits_info = await conn.fetchrow(
                """
                SELECT
                    COALESCE(lifetime_earned, 0) as lifetime_earned,
                    COALESCE(lifetime_spent, 0) as lifetime_spent
                FROM user_credits
                WHERE user_id = $1
            """,
                user_id,
            )

            return UserCreditInfo(
                user_id=user["id"],
                username=user["username"],
                email=user["email"],
                credit_balance=float(user["credit_balance"] or 0),
                lifetime_earned=float(credits_info["lifetime_earned"] if credits_info else 0),
                lifetime_spent=float(credits_info["lifetime_spent"] if credits_info else 0),
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin get user credits failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user credits")


@router.post("/{user_id}/credits/adjust")
async def adjust_user_credits(
    user_id: int,
    request: CreditAdjustRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Adjust User Credits (Admin)

    Add or subtract credits from a user's balance.
    Positive amount = add credits, negative amount = subtract credits.

    **Admin Only**: Requires admin role

    **Request Body:**
    - amount: Number of credits to add (positive) or subtract (negative)
    - reason: Explanation for the adjustment (required)
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow(
                "SELECT id, username, credit_balance FROM users WHERE id = $1", user_id
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            current_balance = float(user["credit_balance"] or 0)
            new_balance = current_balance + request.amount

            # Prevent negative balance
            if new_balance < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot reduce balance below 0. Current: {current_balance}, Requested: {request.amount}",
                )

            # Update user's credit balance
            await conn.execute(
                "UPDATE users SET credit_balance = $1 WHERE id = $2", new_balance, user_id
            )

            # Update user_credits table
            if request.amount > 0:
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, balance, lifetime_earned)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = $2,
                        lifetime_earned = user_credits.lifetime_earned + $3
                """,
                    user_id,
                    new_balance,
                    request.amount,
                )
            else:
                await conn.execute(
                    """
                    INSERT INTO user_credits (user_id, balance, lifetime_spent)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id) DO UPDATE SET
                        balance = $2,
                        lifetime_spent = user_credits.lifetime_spent + $3
                """,
                    user_id,
                    new_balance,
                    abs(request.amount),
                )

            # Record the transaction
            tx_type = "admin_add" if request.amount > 0 else "admin_subtract"
            description = f"Admin adjustment by {current_user.get('username', current_user['id'])}: {request.reason}"

            await conn.execute(
                """
                INSERT INTO credit_transactions (user_id, amount, transaction_type, description, balance_after)
                VALUES ($1, $2, $3, $4, $5)
            """,
                user_id,
                request.amount,
                tx_type,
                description,
                new_balance,
            )

            logger.info(
                f"ADMIN CREDIT ADJUSTMENT: User {user_id} ({user['username']}) credits adjusted by {request.amount} "
                f"by admin {current_user['id']}. New balance: {new_balance}. Reason: {request.reason}"
            )

            return {
                "message": "Credits adjusted successfully",
                "user_id": user_id,
                "username": user["username"],
                "previous_balance": current_balance,
                "adjustment": request.amount,
                "new_balance": new_balance,
                "reason": request.reason,
                "adjusted_by": current_user["id"],
                "adjusted_at": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin credit adjustment failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to adjust user credits")


@router.get("/credits/all", response_model=list[UserCreditInfo])
async def get_all_user_credits(
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
    offset: int = 0,
):
    """
    ## 💰 Get All User Credits (Admin)

    Retrieve credit balances for all users.

    **Admin Only**: Requires admin role
    """
    try:
        await require_admin_user(current_user)
        pool = await get_database_pool()

        async with pool.acquire() as conn:
            users = await conn.fetch(
                """
                SELECT
                    u.id, u.username, u.email,
                    COALESCE(u.credit_balance, 0) as credit_balance,
                    COALESCE(uc.lifetime_earned, 0) as lifetime_earned,
                    COALESCE(uc.lifetime_spent, 0) as lifetime_spent
                FROM users u
                LEFT JOIN user_credits uc ON u.id = uc.user_id
                ORDER BY u.credit_balance DESC NULLS LAST
                LIMIT $1 OFFSET $2
            """,
                limit,
                offset,
            )

            return [
                UserCreditInfo(
                    user_id=user["id"],
                    username=user["username"],
                    email=user["email"],
                    credit_balance=float(user["credit_balance"] or 0),
                    lifetime_earned=float(user["lifetime_earned"] or 0),
                    lifetime_spent=float(user["lifetime_spent"] or 0),
                )
                for user in users
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin get all user credits failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user credits")
