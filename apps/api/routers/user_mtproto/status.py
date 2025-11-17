"""
MTProto Status Endpoint

Handles GET /status endpoint for checking user's MTProto configuration status.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.middleware.auth import get_current_user_id
from apps.api.routers.user_mtproto.deps import get_user_bot_repository
from apps.api.routers.user_mtproto.models import ErrorResponse, MTProtoStatusResponse
from apps.mtproto.multi_tenant.user_mtproto_service import get_user_mtproto_service
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/status",
    response_model=MTProtoStatusResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_mtproto_status(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Get user's MTProto configuration status

    Returns information about whether MTProto is configured and working.
    """
    try:
        # Get credentials from database
        credentials = await repository.get_by_user_id(user_id)

        if not credentials:
            return MTProtoStatusResponse(
                configured=False,
                verified=False,
                can_read_history=False,
            )

        has_api_id = credentials.telegram_api_id is not None
        has_api_hash = credentials.telegram_api_hash is not None
        has_session = credentials.session_string is not None

        configured = has_api_id and has_api_hash
        verified = configured and has_session

        # Check if client is actively connected in the pool
        connected = False  # True if session ready (exists in DB)
        actively_connected = False  # True if client in active pool
        last_used = None

        if verified:
            # Session exists in DB - mark as "ready"
            connected = True

            try:
                mtproto_service = get_user_mtproto_service()
                # Check if client exists in pool and is actively connected
                actively_connected = mtproto_service.is_user_connected(user_id)
                if actively_connected:
                    # Get client to access last_used (this is acceptable internal access)
                    client = await mtproto_service.get_user_client(user_id)
                    if client:
                        last_used = client.last_used
                    logger.debug(
                        f"User {user_id} has active client in pool (connected={actively_connected})"
                    )
                else:
                    logger.debug(f"User {user_id} has verified session (not in active pool yet)")
            except Exception as e:
                logger.warning(f"Error checking MTProto connection for user {user_id}: {e}")

        # Mask phone number
        phone = credentials.telegram_phone
        if phone and len(phone) > 6:
            phone = phone[:4] + "****" + phone[-3:]

        # Check if MTProto is enabled - use credentials value directly (no default!)
        mtproto_enabled = credentials.mtproto_enabled

        return MTProtoStatusResponse(
            configured=configured,
            verified=verified,
            phone=phone,
            api_id=credentials.telegram_api_id if configured else None,
            connected=connected and mtproto_enabled,  # True if session ready
            actively_connected=actively_connected and mtproto_enabled,  # True if in active pool
            last_used=last_used,
            can_read_history=verified and actively_connected and mtproto_enabled,
            mtproto_enabled=mtproto_enabled,  # Return the actual toggle state
        )

    except Exception as e:
        logger.error(f"Error getting MTProto status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get MTProto status"
        )
