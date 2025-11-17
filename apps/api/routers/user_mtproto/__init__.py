"""
User MTProto Package

Modular user MTProto management endpoints for Telegram API configuration.

This package provides endpoints for users to configure their personal MTProto
credentials for reading channel history and analyzing posts.
"""

from .models import (
    ChannelMTProtoSettingResponse,
    ChannelMTProtoSettingsListResponse,
    ErrorResponse,
    MTProtoActionResponse,
    MTProtoSetupRequest,
    MTProtoSetupResponse,
    MTProtoStatusResponse,
    MTProtoToggleRequest,
    MTProtoVerifyRequest,
)
from .router import router

__all__ = [
    "router",
    "MTProtoSetupRequest",
    "MTProtoVerifyRequest",
    "MTProtoStatusResponse",
    "MTProtoSetupResponse",
    "MTProtoActionResponse",
    "MTProtoToggleRequest",
    "ChannelMTProtoSettingResponse",
    "ChannelMTProtoSettingsListResponse",
    "ErrorResponse",
]
