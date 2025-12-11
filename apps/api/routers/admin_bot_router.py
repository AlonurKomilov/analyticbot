"""
Admin Bot API Router - FastAPI endpoints for admin bot management.

Provides endpoints for admins to manage all user bots: list, access,
suspend, activate, and update rate limits.
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from apps.api.middleware.auth import require_admin_user  # Use existing auth system
from apps.api.services.bot_service_factory import create_admin_bot_service
from apps.di import get_container
from core.models.user_bot_domain import BotStatus
from core.ports.user_bot_repository import IUserBotRepository
from core.schemas.user_bot_schemas import (
    AdminAccessResponse,
    BotListResponse,
    BotStatusResponse,
    ErrorResponse,
    RateLimitUpdateResponse,
    SuspendBotRequest,
    UpdateRateLimitRequest,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/admin/bots",
    tags=["Admin Bot Management"],
)


# ==================== Dependency Injection ====================


async def get_user_bot_repository() -> IUserBotRepository:
    """Get user bot repository from DI container."""
    container = get_container()
    return await container.database.user_bot_repo()


async def get_admin_user_id(
    admin_user: Annotated[dict[str, Any], Depends(require_admin_user)],
) -> int:
    """Extract admin user ID from authenticated admin user."""
    return admin_user["id"]


# ==================== Admin Bot Endpoints ====================


@router.get(
    "/list",
    response_model=BotListResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Admin access required"},
    },
)
async def list_all_bots(
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status_filter: BotStatus | None = Query(None, description="Filter by status"),
):
    """
    List all user bots (admin only).

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (1-100, default: 50)
    - **status_filter**: Filter by bot status (optional)
    """
    try:
        service = await create_admin_bot_service(repository)

        bots, total = await service.list_all_user_bots(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
        )

        # Convert to response models (filter out bots with None IDs)
        bot_responses = [
            BotStatusResponse(
                id=bot.id,  # type: ignore[arg-type]
                user_id=bot.user_id,
                bot_username=bot.bot_username,
                bot_id=bot.bot_id,
                status=bot.status,
                is_verified=bot.is_verified,
                max_requests_per_second=int(bot.rate_limit_rps),
                max_concurrent_requests=bot.max_concurrent_requests,
                total_requests=bot.total_requests,
                last_used_at=bot.last_used_at,
                created_at=bot.created_at,
                updated_at=bot.updated_at,
                suspension_reason=bot.suspension_reason,
            )
            for bot in bots
            if bot.id is not None
        ]

        return BotListResponse(
            total=total,
            page=page,
            page_size=page_size,
            bots=bot_responses,
        )

    except Exception as e:
        logger.error(f"Error listing bots for admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list bots",
        )


@router.post(
    "/{user_id}/access",
    response_model=AdminAccessResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def access_user_bot(
    user_id: int,
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Admin access to a user's bot.

    This endpoint allows admins to:
    - Access a user's bot instance
    - View bot information
    - Action is logged for audit trail

    - **user_id**: Target user ID whose bot to access
    """
    try:
        service = await create_admin_bot_service(repository)

        bot_info = await service.access_user_bot(
            admin_user_id=admin_id,
            target_user_id=user_id,
            action="admin_access_bot",
        )

        if not bot_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No bot found for user {user_id}",
            )

        return AdminAccessResponse(
            success=True,
            message=f"Successfully accessed bot for user {user_id}",
            bot_info=bot_info,
            access_logged=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin access for user {user_id} by admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to access user bot",
        )


@router.patch(
    "/{user_id}/suspend",
    response_model=BotStatusResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def suspend_bot(
    user_id: int,
    request: SuspendBotRequest,
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Suspend a user's bot (admin only).

    This will:
    - Set bot status to SUSPENDED
    - Shutdown active bot instance
    - Log admin action with reason

    - **user_id**: Target user ID whose bot to suspend
    - **reason**: Reason for suspension (required, min 5 characters)
    """
    try:
        service = await create_admin_bot_service(repository)

        credentials = await service.suspend_user_bot(
            admin_user_id=admin_id,
            target_user_id=user_id,
            reason=request.reason,
        )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No bot found for user {user_id}",
            )

        if credentials.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot credentials ID is None",
            )

        return BotStatusResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            bot_username=credentials.bot_username,
            bot_id=credentials.bot_id,
            status=credentials.status,
            is_verified=credentials.is_verified,
            max_requests_per_second=int(credentials.rate_limit_rps),
            max_concurrent_requests=credentials.max_concurrent_requests,
            total_requests=credentials.total_requests,
            last_used_at=credentials.last_used_at,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at,
            suspension_reason=credentials.suspension_reason,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending bot for user {user_id} by admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suspend bot",
        )


@router.patch(
    "/{user_id}/activate",
    response_model=BotStatusResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def activate_bot(
    user_id: int,
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Activate a suspended bot (admin only).

    This will:
    - Set bot status to ACTIVE
    - Clear suspension reason
    - Log admin action

    - **user_id**: Target user ID whose bot to activate
    """
    try:
        service = await create_admin_bot_service(repository)

        credentials = await service.activate_user_bot(
            admin_user_id=admin_id,
            target_user_id=user_id,
        )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No bot found for user {user_id}",
            )

        if credentials.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot credentials ID is None",
            )

        return BotStatusResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            bot_username=credentials.bot_username,
            bot_id=credentials.bot_id,
            status=credentials.status,
            is_verified=credentials.is_verified,
            max_requests_per_second=int(credentials.rate_limit_rps),
            max_concurrent_requests=credentials.max_concurrent_requests,
            total_requests=credentials.total_requests,
            last_used_at=credentials.last_used_at,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at,
            suspension_reason=credentials.suspension_reason,
        )

    except HTTPException:
        raise
    except ValueError as e:
        # Handle incomplete bot validation error
        logger.warning(f"Cannot activate bot for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error activating bot for user {user_id} by admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate bot",
        )


@router.patch(
    "/{user_id}/rate-limit",
    response_model=RateLimitUpdateResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def update_bot_rate_limit(
    user_id: int,
    request: UpdateRateLimitRequest,
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Update rate limits for a user's bot (admin only).

    This will:
    - Update rate limit settings
    - Reload bot instance with new limits
    - Log admin action

    - **user_id**: Target user ID whose bot to update
    - **max_requests_per_second**: New RPS limit (1-100, optional)
    - **max_concurrent_requests**: New concurrent limit (1-50, optional)
    """
    try:
        service = await create_admin_bot_service(repository)

        credentials = await service.update_user_bot_rate_limits(
            admin_user_id=admin_id,
            target_user_id=user_id,
            max_requests_per_second=request.max_requests_per_second,
            max_concurrent_requests=request.max_concurrent_requests,
        )

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No bot found for user {user_id}",
            )

        return RateLimitUpdateResponse(
            success=True,
            message=f"Rate limits updated for user {user_id}",
            new_limits={
                "max_requests_per_second": int(credentials.rate_limit_rps),
                "max_concurrent_requests": credentials.max_concurrent_requests,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rate limits for user {user_id} by admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rate limits",
        )


@router.get(
    "/{user_id}/status",
    response_model=BotStatusResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def get_user_bot_status(
    user_id: int,
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Get status of a specific user's bot (admin only).

    - **user_id**: Target user ID
    """
    try:
        service = await create_admin_bot_service(repository)
        credentials = await service.get_bot_by_id(user_id)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No bot found for user {user_id}",
            )

        if credentials.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot credentials ID is None",
            )

        return BotStatusResponse(
            id=credentials.id,
            user_id=credentials.user_id,
            bot_username=credentials.bot_username,
            bot_id=credentials.bot_id,
            status=credentials.status,
            is_verified=credentials.is_verified,
            max_requests_per_second=int(credentials.rate_limit_rps),
            max_concurrent_requests=credentials.max_concurrent_requests,
            total_requests=credentials.total_requests,
            last_used_at=credentials.last_used_at,
            created_at=credentials.created_at,
            updated_at=credentials.updated_at,
            suspension_reason=credentials.suspension_reason,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bot status for user {user_id} by admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get bot status",
        )


@router.delete(
    "/{user_id}/delete",
    responses={
        200: {"description": "Bot deleted successfully"},
        403: {"model": ErrorResponse, "description": "Admin access required"},
        404: {"model": ErrorResponse, "description": "Bot not found"},
    },
)
async def delete_user_bot(
    user_id: int,
    admin_id: Annotated[int, Depends(get_admin_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Delete a user's bot from the system (admin only).

    This will completely remove the bot credentials, allowing the user
    to set up a new bot from scratch.

    - **user_id**: Target user ID whose bot to delete
    """
    try:
        # First check if bot exists
        credentials = await repository.get_by_user_id(user_id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No bot found for user {user_id}",
            )

        # Delete the bot
        success = await repository.delete(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete bot from database",
            )

        # Log admin action
        from datetime import datetime
        from core.models.user_bot_domain import AdminBotAction
        await repository.log_admin_action(
            AdminBotAction(
                id=0,
                admin_user_id=admin_id,
                target_user_id=user_id,
                action="delete_bot",
                details={"bot_username": credentials.bot_username, "bot_id": credentials.bot_id},
                timestamp=datetime.utcnow(),
            )
        )

        logger.info(f"Admin {admin_id} deleted bot for user {user_id}")

        return {"message": f"Bot for user {user_id} deleted successfully", "deleted": True}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bot for user {user_id} by admin {admin_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete bot",
        )
