"""
MTProto Connection Endpoints

Handles POST /connect, POST /disconnect, and DELETE /remove endpoints.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.middleware.auth import get_current_user_id
from apps.api.routers.user_mtproto.deps import get_user_bot_repository
from apps.api.routers.user_mtproto.models import ErrorResponse, MTProtoActionResponse
from apps.di import get_user_mtproto_service
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/connect",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "No MTProto configuration or not verified"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def connect_mtproto(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Manually connect MTProto client and add to active pool

    This creates an active Telegram connection and adds the client to the
    service pool. Use this when you want immediate "Active" status instead
    of lazy "Ready" status.
    """
    try:
        # Check credentials exist and are verified
        credentials = await repository.get_by_user_id(user_id)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No MTProto configuration found. Please configure MTProto first.",
            )

        if not credentials.is_verified or not credentials.session_string:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MTProto not verified. Please complete verification first.",
            )

        if not credentials.mtproto_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MTProto is disabled. Please enable it first.",
            )

        # Get MTProto service and connect client
        mtproto_service = await get_user_mtproto_service()

        # This will create client and add to pool if not exists, or reconnect if exists
        client = await mtproto_service.get_user_client(user_id)

        if not client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create MTProto client. Check your configuration.",
            )

        logger.info(f"MTProto client connected manually for user {user_id}")

        return MTProtoActionResponse(
            success=True,
            message="MTProto client connected successfully. You can now read channel history.",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect MTProto: {str(e)}",
        )


@router.post(
    "/disconnect",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def disconnect_mtproto(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Disconnect and remove MTProto configuration

    This will:
    1. Disconnect active client
    2. Remove session from database
    3. Keep API ID/Hash for easy reconnection
    """
    try:
        # Remove from MTProto service pool
        try:
            mtproto_service = await get_user_mtproto_service()
            await mtproto_service.disconnect_user(user_id)
        except Exception as e:
            logger.warning(f"Error disconnecting MTProto service for user {user_id}: {e}")

        # Clear session from database (keep API credentials)
        credentials = await repository.get_by_user_id(user_id)
        if credentials:
            credentials.session_string = None
            credentials.is_verified = False
            await repository.update(credentials)

        logger.info(f"MTProto disconnected for user {user_id}")

        return MTProtoActionResponse(success=True, message="MTProto disconnected successfully")

    except Exception as e:
        logger.error(f"Error disconnecting MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disconnect MTProto"
        )


@router.delete(
    "/remove",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def remove_mtproto(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Completely remove MTProto configuration

    This will remove all MTProto credentials including API ID/Hash.
    """
    try:
        # Disconnect first
        try:
            mtproto_service = get_user_mtproto_service()
            await mtproto_service.disconnect_user(user_id)
        except Exception as e:
            logger.warning(f"Error disconnecting MTProto service for user {user_id}: {e}")

        # Remove all MTProto data from database
        credentials = await repository.get_by_user_id(user_id)
        if credentials:
            credentials.mtproto_api_id = None
            credentials.telegram_api_hash = None
            credentials.mtproto_phone = None
            credentials.session_string = None
            credentials.is_verified = False
            await repository.update(credentials)

        logger.info(f"MTProto configuration removed for user {user_id}")

        return MTProtoActionResponse(
            success=True, message="MTProto configuration removed successfully"
        )

    except Exception as e:
        logger.error(f"Error removing MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove MTProto configuration",
        )
