"""
MTProto Dependencies - Dependency injection for MTProto services.

Provides FastAPI dependencies for MTProto-related services and repositories.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.di import get_db_session
from core.ports.mtproto_repository import (
    IChannelMTProtoSettingsRepository,
    IMTProtoAuditRepository,
    IMTProtoChannelRepository,
)
from infra.db.adapters.mtproto_repository_adapter import (
    MTProtoAuditRepositoryAdapter,
    MTProtoChannelRepositoryAdapter,
)
from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository


async def get_channel_mtproto_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IChannelMTProtoSettingsRepository:
    """Get Channel MTProto Settings Repository."""
    return ChannelMTProtoRepository(session)


async def get_mtproto_audit_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IMTProtoAuditRepository:
    """Get MTProto Audit Repository."""
    return MTProtoAuditRepositoryAdapter(session)


async def get_mtproto_channel_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IMTProtoChannelRepository:
    """Get MTProto Channel Repository (for future use)."""
    return MTProtoChannelRepositoryAdapter(session)
