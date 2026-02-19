"""
MTProto Repository Port - Interface for MTProto data access.

This port defines the contract for accessing MTProto channel and user bot data
following the Ports & Adapters (Hexagonal Architecture) pattern.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class IChannelMTProtoSettingsRepository(ABC):
    """Interface for per-channel MTProto settings repository."""

    @abstractmethod
    async def get_setting(self, user_id: int, channel_id: int) -> Any | None:
        """Get MTProto setting for a specific user+channel combination."""

    @abstractmethod
    async def get_user_settings(self, user_id: int) -> list[Any]:
        """Get all channel MTProto settings for a user."""

    @abstractmethod
    async def create_or_update(self, user_id: int, channel_id: int, mtproto_enabled: bool) -> Any:
        """Create or update MTProto setting for a channel."""

    @abstractmethod
    async def delete_setting(self, user_id: int, channel_id: int) -> bool:
        """Delete MTProto setting for a specific channel."""

    @abstractmethod
    async def delete_user_settings(self, user_id: int) -> int:
        """Delete all MTProto settings for a user."""

    @abstractmethod
    async def is_channel_enabled(self, user_id: int, channel_id: int, global_enabled: bool) -> bool:
        """Check if MTProto is enabled for a specific channel."""


class IMTProtoChannelRepository(ABC):
    """Interface for MTProto channel data repository."""

    @abstractmethod
    async def get_by_id(self, channel_id: int) -> dict[str, Any] | None:
        """Get MTProto channel by ID."""

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[dict[str, Any]]:
        """Get all MTProto channels for a user."""

    @abstractmethod
    async def create(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Create new MTProto channel."""

    @abstractmethod
    async def update(self, channel_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update MTProto channel."""

    @abstractmethod
    async def delete(self, channel_id: int) -> bool:
        """Delete MTProto channel."""

    @abstractmethod
    async def list_with_pagination(
        self, user_id: int, offset: int = 0, limit: int = 50
    ) -> tuple[list[dict[str, Any]], int]:
        """List channels with pagination. Returns (channels, total_count)."""


class IMTProtoAuditRepository(ABC):
    """Interface for MTProto audit log repository."""

    @abstractmethod
    async def log_action(
        self,
        user_id: int,
        action: str,
        channel_id: int | None = None,
        details: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Log an MTProto action."""

    @abstractmethod
    async def get_user_actions(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get user's action history."""

    @abstractmethod
    async def get_channel_actions(
        self, channel_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get channel's action history."""
