"""
MTProto Repository Adapter - Implements MTProto ports using SQLAlchemy ORM.

This adapter translates between domain DTOs and ORM models,
following the Ports & Adapters (Hexagonal Architecture) pattern.
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ports.mtproto_repository import (
    IMTProtoAuditRepository,
    IMTProtoChannelRepository,
)
from infra.db.models.user_bot_orm import MTProtoAuditLog

logger = logging.getLogger(__name__)


class MTProtoChannelRepositoryAdapter(IMTProtoChannelRepository):
    """Adapter for MTProto channel repository using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def get_by_id(self, channel_id: int) -> dict[str, Any] | None:
        """Get MTProto channel by ID."""
        # Implementation depends on your channel ORM model
        # For now, returning None as placeholder
        logger.warning("MTProtoChannelRepositoryAdapter.get_by_id not fully implemented")
        return None

    async def get_by_user_id(self, user_id: int) -> list[dict[str, Any]]:
        """Get all MTProto channels for a user."""
        logger.warning("MTProtoChannelRepositoryAdapter.get_by_user_id not fully implemented")
        return []

    async def create(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Create new MTProto channel."""
        logger.warning("MTProtoChannelRepositoryAdapter.create not fully implemented")
        return channel_data

    async def update(self, channel_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
        """Update MTProto channel."""
        logger.warning("MTProtoChannelRepositoryAdapter.update not fully implemented")
        return None

    async def delete(self, channel_id: int) -> bool:
        """Delete MTProto channel."""
        logger.warning("MTProtoChannelRepositoryAdapter.delete not fully implemented")
        return False

    async def list_with_pagination(
        self, user_id: int, offset: int = 0, limit: int = 50
    ) -> tuple[list[dict[str, Any]], int]:
        """List channels with pagination."""
        logger.warning("MTProtoChannelRepositoryAdapter.list_with_pagination not fully implemented")
        return [], 0


class MTProtoAuditRepositoryAdapter(IMTProtoAuditRepository):
    """Adapter for MTProto audit repository using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    def _orm_to_dto(self, orm: MTProtoAuditLog) -> dict[str, Any]:
        """Convert ORM model to DTO dictionary."""
        return {
            "id": orm.id,
            "user_id": orm.user_id,
            "action": orm.action,
            "channel_id": orm.channel_id,
            "details": orm.event_metadata or {},
            "timestamp": orm.timestamp,
            "ip_address": orm.ip_address,
            "user_agent": orm.user_agent,
        }

    def _dto_to_orm(self, dto_dict: dict[str, Any]) -> MTProtoAuditLog:
        """Convert DTO dictionary to ORM model."""
        return MTProtoAuditLog(
            user_id=dto_dict.get("user_id", 0),
            action=dto_dict.get("action", ""),
            channel_id=dto_dict.get("channel_id"),
            event_metadata=dto_dict.get("details"),
            timestamp=dto_dict.get("timestamp", datetime.utcnow()),
            ip_address=dto_dict.get("ip_address"),
            user_agent=dto_dict.get("user_agent"),
            previous_state=dto_dict.get("previous_state"),
            new_state=dto_dict.get("new_state"),
        )

    async def log_action(
        self,
        user_id: int,
        action: str,
        channel_id: int | None = None,
        details: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Log an MTProto action."""
        dto_dict = {
            "user_id": user_id,
            "action": action,
            "channel_id": channel_id,
            "details": details or {},
            "timestamp": timestamp or datetime.utcnow(),
        }

        orm = self._dto_to_orm(dto_dict)
        self.session.add(orm)
        await self.session.flush()  # Get ID without committing

        logger.info(f"Logged MTProto action: {action} for user {user_id}")
        return self._orm_to_dto(orm)

    async def get_user_actions(
        self, user_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get user's action history."""
        query = (
            select(MTProtoAuditLog)
            .where(MTProtoAuditLog.user_id == user_id)
            .order_by(MTProtoAuditLog.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        orms = result.scalars().all()

        return [self._orm_to_dto(orm) for orm in orms]

    async def get_channel_actions(
        self, channel_id: int, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get channel's action history."""
        query = (
            select(MTProtoAuditLog)
            .where(MTProtoAuditLog.channel_id == channel_id)
            .order_by(MTProtoAuditLog.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        orms = result.scalars().all()

        return [self._orm_to_dto(orm) for orm in orms]
