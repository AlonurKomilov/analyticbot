"""
User Bot Service API Router

REST API endpoints for managing user bot service features:
- Chat settings management
- Banned words management
- Welcome message configuration
- Invite statistics
- Service log
"""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user
from apps.di import get_container, get_db_connection
from core.models.user_bot_service_domain import (
    ChatSettings,
    ChatType,
    ModerationAction,
    MessageType,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/user-bot/service",
    tags=["User Bot Service"],
)


# ===========================================
# Pydantic Schemas
# ===========================================

class ChatSettingsUpdate(BaseModel):
    """Schema for updating chat settings."""
    chat_type: str | None = None
    chat_title: str | None = None
    
    # Feature toggles
    clean_join_messages: bool | None = None
    clean_leave_messages: bool | None = None
    banned_words_enabled: bool | None = None
    anti_spam_enabled: bool | None = None
    anti_link_enabled: bool | None = None
    anti_forward_enabled: bool | None = None
    welcome_enabled: bool | None = None
    invite_tracking_enabled: bool | None = None
    captcha_enabled: bool | None = None
    slow_mode_enabled: bool | None = None
    night_mode_enabled: bool | None = None
    
    # Anti-spam settings
    spam_action: str | None = None
    max_warnings: int | None = Field(None, ge=1, le=10)
    warning_action: str | None = None
    mute_duration_minutes: int | None = Field(None, ge=1, le=10080)
    
    # Anti-flood settings
    flood_limit: int | None = Field(None, ge=2, le=20)
    flood_interval_seconds: int | None = Field(None, ge=5, le=60)
    
    # Night mode
    night_mode_start_hour: int | None = Field(None, ge=0, le=23)
    night_mode_end_hour: int | None = Field(None, ge=0, le=23)
    night_mode_timezone: str | None = None
    
    # Permissions
    whitelisted_users: list[int] | None = None
    admin_users: list[int] | None = None


class AvailableChatResponse(BaseModel):
    """Response schema for available chat."""
    chat_id: int
    chat_title: str
    chat_type: str
    settings_configured: bool


class ChatSettingsResponse(BaseModel):
    """Response schema for chat settings."""
    id: int
    user_id: int
    chat_id: int
    chat_type: str
    chat_title: str | None
    
    clean_join_messages: bool
    clean_leave_messages: bool
    banned_words_enabled: bool
    anti_spam_enabled: bool
    anti_link_enabled: bool
    anti_forward_enabled: bool
    welcome_enabled: bool
    invite_tracking_enabled: bool
    captcha_enabled: bool
    slow_mode_enabled: bool
    night_mode_enabled: bool
    
    spam_action: str
    max_warnings: int
    warning_action: str
    mute_duration_minutes: int
    flood_limit: int
    flood_interval_seconds: int
    
    night_mode_start_hour: int | None
    night_mode_end_hour: int | None
    night_mode_timezone: str
    
    whitelisted_users: list[int]
    admin_users: list[int]
    
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class BannedWordCreate(BaseModel):
    """Schema for creating a banned word."""
    word: str = Field(..., min_length=1, max_length=100)
    chat_id: int | None = None  # None = global
    is_regex: bool = False
    action: str = "delete"  # delete, warn, mute, kick, ban


class BannedWordResponse(BaseModel):
    """Response schema for banned word."""
    id: int
    user_id: int
    chat_id: int | None
    word: str
    is_regex: bool
    action: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class WelcomeMessageCreate(BaseModel):
    """Schema for creating/updating welcome message."""
    message_text: str = Field(..., min_length=1, max_length=4096)
    message_type: str = "welcome"  # welcome, goodbye, rules
    parse_mode: str = "HTML"
    buttons: list[dict] | None = None
    media_type: str | None = None
    media_file_id: str | None = None
    delete_after_seconds: int | None = Field(None, ge=5, le=3600)


class WelcomeMessageResponse(BaseModel):
    """Response schema for welcome message."""
    id: int
    user_id: int
    chat_id: int
    message_type: str
    message_text: str
    parse_mode: str
    buttons: list[dict] | None
    media_type: str | None
    media_file_id: str | None
    delete_after_seconds: int | None
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class InviteStatsResponse(BaseModel):
    """Response schema for invite statistics."""
    inviter_tg_id: int
    inviter_username: str | None
    inviter_name: str | None
    total_invited: int
    still_members: int
    left_count: int
    retention_rate: float


class ModerationLogResponse(BaseModel):
    """Response schema for moderation log entry."""
    id: int
    chat_id: int
    action: str
    target_tg_id: int | None
    target_username: str | None
    performed_by: str
    performed_by_tg_id: int | None
    reason: str | None
    details: dict | None
    message_id: int | None
    created_at: str


# ===========================================
# Dependencies
# ===========================================

async def get_service():
    """Get moderation service from DI container."""
    container = get_container()
    return await container.bot.moderation_service()


async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> int:
    """Get current user ID from auth context."""
    return current_user["id"]


async def get_db_pool_connection():
    """Get a database connection from the asyncpg pool."""
    pool = await get_db_connection()
    async with pool.acquire() as conn:
        yield conn


# ===========================================
# Chat Settings Endpoints
# ===========================================

@router.get(
    "/chats",
    response_model=list[AvailableChatResponse],
    summary="Get available chats for moderation",
)
async def get_available_chats(
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
    conn = Depends(get_db_pool_connection),
):
    """
    Get list of user's channels/groups available for moderation configuration.
    
    Returns all chats (both channels and groups) from the database with:
    - Chat type detection (channel vs group based on Telegram ID format)
    - Moderation settings status
    - Proper ID formatting
    
    Telegram Chat Types:
    - Channels: IDs with -100 prefix (e.g., -1001234567890) - broadcast only
    - Groups: Negative IDs without -100 prefix (e.g., -123456789) - interactive chat
    """
    # Helper function to detect chat type from Telegram ID
    def detect_chat_type(telegram_id: int) -> str:
        """
        Detect if a Telegram chat is a channel or group based on ID format.
        
        Telegram ID patterns:
        - Channels: -100 prefix (supergroups with broadcast mode)
        - Groups: Negative without -100 prefix
        - Private: Positive (not used here)
        """
        id_str = str(abs(telegram_id))
        if id_str.startswith("100") and len(id_str) >= 12:
            return "channel"
        elif telegram_id < 0:
            return "group"
        else:
            return "channel"  # Default fallback
    
    # Fetch user's channels using raw SQL
    channels = await conn.fetch(
        """
        SELECT id, user_id, title, username, description, created_at
        FROM channels
        WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        user_id
    )
    
    # Get all configured settings
    configured_settings = await service.get_all_user_settings(user_id)
    configured_chat_ids = {s.chat_id for s in configured_settings}
    
    # Build response
    available_chats = []
    for channel in channels:
        channel_id = channel['id']
        chat_type = detect_chat_type(channel_id)
        
        # Use channel ID as-is (it's already in Telegram format from database)
        chat_id = channel_id
        
        available_chats.append(
            AvailableChatResponse(
                chat_id=chat_id,
                chat_title=channel['title'] or f"{'Channel' if chat_type == 'channel' else 'Group'} {abs(channel_id)}",
                chat_type=chat_type,
                settings_configured=chat_id in configured_chat_ids,
            )
        )
    
    return available_chats


@router.get(
    "/settings/{chat_id}",
    response_model=ChatSettingsResponse,
    summary="Get chat moderation settings",
)
async def get_chat_settings(
    chat_id: int,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Get moderation settings for a specific chat."""
    settings = await service.get_settings(user_id, chat_id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settings not found for this chat",
        )
    
    return _settings_to_response(settings)


@router.get(
    "/settings",
    response_model=list[ChatSettingsResponse],
    summary="Get all chat settings",
)
async def get_all_settings(
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Get all moderation settings for user's chats."""
    settings_list = await service.get_all_user_settings(user_id)
    return [_settings_to_response(s) for s in settings_list]


@router.post(
    "/settings/{chat_id}",
    response_model=ChatSettingsResponse,
    summary="Create or update chat settings",
)
async def upsert_chat_settings(
    chat_id: int,
    data: ChatSettingsUpdate,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Create or update moderation settings for a chat."""
    # Get existing or create new
    existing = await service.get_settings(user_id, chat_id)
    
    if existing:
        # Update existing settings
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                if field in ["chat_type"]:
                    setattr(existing, field, ChatType(value))
                elif field in ["spam_action", "warning_action"]:
                    setattr(existing, field, ModerationAction(value))
                else:
                    setattr(existing, field, value)
        
        settings = await service.update_settings(existing)
    else:
        # Create new settings
        chat_type = ChatType(data.chat_type) if data.chat_type else ChatType.GROUP
        settings = await service.get_or_create_settings(
            user_id=user_id,
            chat_id=chat_id,
            chat_type=chat_type,
            chat_title=data.chat_title,
        )
        
        # Apply provided settings
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None and hasattr(settings, field):
                if field in ["chat_type"]:
                    setattr(settings, field, ChatType(value))
                elif field in ["spam_action", "warning_action"]:
                    setattr(settings, field, ModerationAction(value))
                else:
                    setattr(settings, field, value)
        
        settings = await service.update_settings(settings)
    
    return _settings_to_response(settings)


@router.delete(
    "/settings/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete chat settings",
)
async def delete_chat_settings(
    chat_id: int,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Delete moderation settings for a chat."""
    # This would need to be implemented in the service
    # For now, raise not implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Settings deletion not yet implemented",
    )


# ===========================================
# Banned Words Endpoints
# ===========================================

@router.get(
    "/banned-words",
    response_model=list[BannedWordResponse],
    summary="Get banned words",
)
async def get_banned_words(
    chat_id: int | None = Query(None, description="Filter by chat ID"),
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Get all banned words for user, optionally filtered by chat."""
    words = await service.get_banned_words(user_id, chat_id)
    return [_banned_word_to_response(w) for w in words]


@router.post(
    "/banned-words",
    response_model=BannedWordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add banned word",
)
async def add_banned_word(
    data: BannedWordCreate,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Add a new banned word."""
    word = await service.add_banned_word(
        user_id=user_id,
        word=data.word,
        chat_id=data.chat_id,
        is_regex=data.is_regex,
        action=ModerationAction(data.action),
    )
    return _banned_word_to_response(word)


@router.delete(
    "/banned-words/{word_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove banned word",
)
async def remove_banned_word(
    word_id: int,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Remove a banned word."""
    success = await service.remove_banned_word(word_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banned word not found",
        )


# ===========================================
# Welcome Messages Endpoints
# ===========================================

@router.get(
    "/welcome/{chat_id}",
    response_model=WelcomeMessageResponse | None,
    summary="Get welcome message",
)
async def get_welcome_message(
    chat_id: int,
    message_type: str = Query("welcome", description="Message type: welcome, goodbye, rules"),
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Get welcome/goodbye message for a chat."""
    msg_type = MessageType(message_type)
    message = await service.get_welcome_message(user_id, chat_id, msg_type)
    
    if not message:
        return None
    
    return _welcome_to_response(message)


@router.post(
    "/welcome/{chat_id}",
    response_model=WelcomeMessageResponse,
    summary="Set welcome message",
)
async def set_welcome_message(
    chat_id: int,
    data: WelcomeMessageCreate,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Set welcome/goodbye message for a chat."""
    msg_type = MessageType(data.message_type)
    
    message = await service.set_welcome_message(
        user_id=user_id,
        chat_id=chat_id,
        message_text=data.message_text,
        message_type=msg_type,
        parse_mode=data.parse_mode,
        buttons=data.buttons,
        media_type=data.media_type,
        media_file_id=data.media_file_id,
        delete_after_seconds=data.delete_after_seconds,
    )
    
    return _welcome_to_response(message)


# ===========================================
# Invite Statistics Endpoints
# ===========================================

@router.get(
    "/invites/{chat_id}",
    response_model=list[InviteStatsResponse],
    summary="Get invite statistics",
)
async def get_invite_stats(
    chat_id: int,
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Get invite statistics for a chat."""
    stats = await service.get_invite_stats(user_id, chat_id)
    return [
        InviteStatsResponse(
            inviter_tg_id=s.inviter_tg_id,
            inviter_username=s.inviter_username,
            inviter_name=s.inviter_name,
            total_invited=s.total_invited,
            still_members=s.still_members,
            left_count=s.left_count,
            retention_rate=s.retention_rate,
        )
        for s in stats
    ]


# ===========================================
# Moderation Log Endpoints
# ===========================================

@router.get(
    "/log/{chat_id}",
    response_model=list[ModerationLogResponse],
    summary="Get moderation log",
)
async def get_moderation_log(
    chat_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_current_user_id),
    service = Depends(get_service),
):
    """Get moderation log for a chat."""
    logs = await service.get_moderation_log(user_id, chat_id, limit, offset)
    return [
        ModerationLogResponse(
            id=entry.id,
            chat_id=entry.chat_id,
            action=entry.action,
            target_tg_id=entry.target_tg_id,
            target_username=entry.target_username,
            performed_by=entry.performed_by.value,
            performed_by_tg_id=entry.performed_by_tg_id,
            reason=entry.reason,
            details=entry.details,
            message_id=entry.message_id,
            created_at=entry.created_at.isoformat(),
        )
        for entry in logs
    ]


# ===========================================
# Helper Functions
# ===========================================

def _settings_to_response(settings: ChatSettings) -> ChatSettingsResponse:
    """Convert domain model to response schema."""
    return ChatSettingsResponse(
        id=settings.id or 0,
        user_id=settings.user_id,
        chat_id=settings.chat_id,
        chat_type=settings.chat_type.value,
        chat_title=settings.chat_title,
        clean_join_messages=settings.clean_join_messages,
        clean_leave_messages=settings.clean_leave_messages,
        banned_words_enabled=settings.banned_words_enabled,
        anti_spam_enabled=settings.anti_spam_enabled,
        anti_link_enabled=settings.anti_link_enabled,
        anti_forward_enabled=settings.anti_forward_enabled,
        welcome_enabled=settings.welcome_enabled,
        invite_tracking_enabled=settings.invite_tracking_enabled,
        captcha_enabled=settings.captcha_enabled,
        slow_mode_enabled=settings.slow_mode_enabled,
        night_mode_enabled=settings.night_mode_enabled,
        spam_action=settings.spam_action.value,
        max_warnings=settings.max_warnings,
        warning_action=settings.warning_action.value,
        mute_duration_minutes=settings.mute_duration_minutes,
        flood_limit=settings.flood_limit,
        flood_interval_seconds=settings.flood_interval_seconds,
        night_mode_start_hour=settings.night_mode_start_hour,
        night_mode_end_hour=settings.night_mode_end_hour,
        night_mode_timezone=settings.night_mode_timezone,
        whitelisted_users=settings.whitelisted_users,
        admin_users=settings.admin_users,
        created_at=settings.created_at.isoformat(),
        updated_at=settings.updated_at.isoformat(),
    )


def _banned_word_to_response(word: Any) -> BannedWordResponse:
    """Convert domain model to response schema."""
    return BannedWordResponse(
        id=word.id or 0,
        user_id=word.user_id,
        chat_id=word.chat_id,
        word=word.word,
        is_regex=word.is_regex,
        action=word.action.value,
        is_active=word.is_active,
        created_at=word.created_at.isoformat(),
    )


def _welcome_to_response(message: Any) -> WelcomeMessageResponse:
    """Convert domain model to response schema."""
    return WelcomeMessageResponse(
        id=message.id or 0,
        user_id=message.user_id,
        chat_id=message.chat_id,
        message_type=message.message_type.value,
        message_text=message.message_text,
        parse_mode=message.parse_mode,
        buttons=message.buttons,
        media_type=message.media_type,
        media_file_id=message.media_file_id,
        delete_after_seconds=message.delete_after_seconds,
        is_active=message.is_active,
        created_at=message.created_at.isoformat(),
        updated_at=message.updated_at.isoformat(),
    )
