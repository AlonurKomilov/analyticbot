"""
MTProto Toggle Endpoint

Handles POST /toggle endpoint for enabling/disabling MTProto globally.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.middleware.auth import get_current_user_id
from apps.api.routers.user_mtproto.deps import get_user_bot_repository
from apps.api.routers.user_mtproto.models import (
    ErrorResponse,
    MTProtoActionResponse,
    MTProtoToggleRequest,
)
from apps.mtproto.multi_tenant.user_mtproto_service import get_user_mtproto_service
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/toggle",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "No MTProto configuration found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def toggle_mtproto(
    payload: MTProtoToggleRequest,
    http_request: Request,
    user_id: Annotated[int, Depends(get_current_user_id)],
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
):
    """
    Enable or disable MTProto functionality

    When disabled:
    - MTProto client will be disconnected
    - Channel history reading will be unavailable
    - Only bot-based operations will work

    When enabled:
    - MTProto client can reconnect
    - Full channel history access restored
    """
    try:
        # Get credentials
        credentials = await repository.get_by_user_id(user_id)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No MTProto configuration found. Please configure MTProto first.",
            )

        # If disabling, disconnect client
        if not payload.enabled and credentials.mtproto_enabled:
            try:
                mtproto_service = get_user_mtproto_service()
                await mtproto_service.disconnect_user(user_id)
                logger.info(f"Disconnected MTProto client for user {user_id} (disabled)")
            except Exception as e:
                logger.warning(f"Error disconnecting MTProto service for user {user_id}: {e}")

        # Update flag
        previous_state = credentials.mtproto_enabled
        credentials.mtproto_enabled = payload.enabled
        await repository.update(credentials)

        # Audit log the change
        try:
            from apps.api.services.mtproto_audit_service import MTProtoAuditService
            from apps.di import get_container

            container = get_container()
            session_factory = await container.database.async_session_maker()
            async with session_factory() as audit_session:
                audit_service = MTProtoAuditService(audit_session)
                await audit_service.log_toggle_event(
                    user_id=user_id,
                    enabled=payload.enabled,
                    request=http_request,
                    channel_id=None,
                    previous_state=previous_state,
                )
        except Exception as e:
            logger.warning(f"Failed to write MTProto audit log for user {user_id}: {e}")

        action = "enabled" if payload.enabled else "disabled"
        logger.info(f"MTProto {action} for user {user_id}")

        status_message = (
            "Full history access is now available."
            if payload.enabled
            else "Only bot-based operations are available."
        )
        return MTProtoActionResponse(
            success=True,
            message=f"MTProto {action} successfully. {status_message}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle MTProto functionality",
        )
