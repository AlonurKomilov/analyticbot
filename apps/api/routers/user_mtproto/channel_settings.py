"""
Channel MTProto Settings Endpoints

Handles per-channel MTProto configuration endpoints under /channels/*.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from apps.api.deps.mtproto_deps import get_channel_mtproto_repository
from apps.api.middleware.auth import get_current_user_id
from apps.api.routers.user_mtproto.deps import get_user_bot_repository
from apps.api.routers.user_mtproto.models import (
    ChannelMTProtoSettingResponse,
    ChannelMTProtoSettingsListResponse,
    ErrorResponse,
    MTProtoActionResponse,
    MTProtoToggleRequest,
)
from core.ports.mtproto_repository import IChannelMTProtoSettingsRepository
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/channels/settings",
    response_model=ChannelMTProtoSettingsListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_all_channel_settings(
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_bot_repo: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
    channel_repo: Annotated[
        IChannelMTProtoSettingsRepository, Depends(get_channel_mtproto_repository)
    ],
):
    """
    Get all per-channel MTProto settings for the user

    Returns the global MTProto enabled flag plus any per-channel overrides.
    If no per-channel setting exists, the channel inherits the global setting.
    """
    try:
        # Get global setting
        credentials = await user_bot_repo.get_by_user_id(user_id)
        global_enabled = credentials.mtproto_enabled if credentials else False

        # Get per-channel settings
        settings = await channel_repo.get_user_settings(user_id)

        settings_list = [
            ChannelMTProtoSettingResponse(
                channel_id=s.channel_id,
                mtproto_enabled=s.mtproto_enabled,
                created_at=s.created_at,
                updated_at=s.updated_at,
            )
            for s in settings
        ]

        return ChannelMTProtoSettingsListResponse(
            global_enabled=global_enabled,
            settings=settings_list,
        )

    except Exception as e:
        logger.error(f"Error fetching channel MTProto settings for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch channel settings",
        )


@router.get(
    "/channels/{channel_id}/settings",
    response_model=ChannelMTProtoSettingResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Setting not found (uses global default)",
        },
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_channel_setting(
    channel_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_bot_repo: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
    channel_repo: Annotated[
        IChannelMTProtoSettingsRepository, Depends(get_channel_mtproto_repository)
    ],
):
    """
    Get MTProto setting for a specific channel

    If no per-channel setting exists, returns 404 (channel uses global default).
    """
    try:
        setting = await channel_repo.get_setting(user_id, channel_id)

        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No per-channel setting for channel {channel_id} (uses global default)",
            )

        return ChannelMTProtoSettingResponse(
            channel_id=setting.channel_id,
            mtproto_enabled=setting.mtproto_enabled,
            created_at=setting.created_at,
            updated_at=setting.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching channel {channel_id} MTProto setting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch channel setting",
        )


@router.post(
    "/channels/{channel_id}/toggle",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def toggle_channel_mtproto(
    channel_id: int,
    payload: MTProtoToggleRequest,
    request: Request,
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_bot_repo: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
    channel_repo: Annotated[
        IChannelMTProtoSettingsRepository, Depends(get_channel_mtproto_repository)
    ],
):
    """
    Enable or disable MTProto for a specific channel

    Creates or updates a per-channel override. Even if global MTProto is enabled,
    you can disable it for specific channels, and vice versa (though global=disabled
    will still prevent access).
    """
    try:
        # Get credentials to ensure user has MTProto configured
        credentials = await user_bot_repo.get_by_user_id(user_id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No MTProto configuration found. Please configure MTProto first.",
            )

        # Get previous state for audit
        previous_setting = await channel_repo.get_setting(user_id, channel_id)
        previous_state = previous_setting.mtproto_enabled if previous_setting else None

        # Create or update per-channel setting
        await channel_repo.create_or_update(user_id, channel_id, payload.enabled)

        # Audit log the per-channel change
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
                    request=request,
                    channel_id=channel_id,
                    previous_state=previous_state,
                )
        except Exception as e:
            logger.warning(
                f"Failed to write MTProto audit log for user {user_id}, channel {channel_id}: {e}"
            )

        action = "enabled" if payload.enabled else "disabled"
        logger.info(f"MTProto {action} for user {user_id}, channel {channel_id}")

        channel_status = (
            "This channel can now read history (if global MTProto is also enabled)."
            if payload.enabled
            else "This channel cannot read history."
        )
        return MTProtoActionResponse(
            success=True,
            message=f"MTProto {action} for channel {channel_id}. {channel_status}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling channel {channel_id} MTProto for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle channel MTProto setting",
        )


@router.delete(
    "/channels/{channel_id}/settings",
    response_model=MTProtoActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse, "description": "Setting not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_channel_setting(
    channel_id: int,
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_bot_repo: Annotated[IUserBotRepository, Depends(get_user_bot_repository)],
    channel_repo: Annotated[
        IChannelMTProtoSettingsRepository, Depends(get_channel_mtproto_repository)
    ],
):
    """
    Delete per-channel MTProto setting (reverts to global default)

    After deletion, the channel will inherit the global MTProto enabled/disabled state.
    """
    try:
        deleted = await channel_repo.delete_setting(user_id, channel_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No per-channel setting found for channel {channel_id}",
            )

        logger.info(f"Deleted per-channel MTProto setting for user {user_id}, channel {channel_id}")

        return MTProtoActionResponse(
            success=True,
            message=(
                f"Per-channel setting deleted for channel {channel_id}. Now uses global default."
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting channel {channel_id} MTProto setting: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete channel setting",
        )
