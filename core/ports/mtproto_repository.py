"""
MTProto Repository Port - Interface for MTProto data access.

This port defines the contract for accessing MTProto channel and user bot data
following the Ports & Adapters (Hexagonal Architecture) pattern.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class IMTProtoChannelRepository(ABC):
    """Interface for MTProto channel data repository."""

    @abstractmethod
    async def get_by_id(self, channel_id: int) -> dict[str, Any] | None:
        """Get MTProto channel by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[dict[str, Any]]:
        """Get all MTProto channels for a user."""
        pass

    @abstractmethod
    async def create(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Create new MTProto channel."""
        pass

    @abstractmethod
    async def update(self, channel_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update MTProto channel."""
        pass

    @abstractmethod
    async def delete(self, channel_id: int) -> bool:
        """Delete MTProto channel."""
        pass

    @abstractmethod
    async def list_with_pagination(
        self, user_id: int, offset: int = 0, limit: int = 50
    ) -> tuple[list[dict[str, Any]], int]:
        """List channels with pagination. Returns (channels, total_count)."""
        pass


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
        pass

    @abstractmethod
    async def get_user_actions(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get user's action history."""
        pass

    @abstractmethod
    async def get_channel_actions(
        self, channel_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get channel's action history."""
        pass
