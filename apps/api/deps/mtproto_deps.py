"""
MTProto Dependencies - Dependency injection for MTProto services.

Provides FastAPI dependencies for MTProto-related services and repositories.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.di import get_container
from core.ports.mtproto_repository import IMTProtoAuditRepository, IMTProtoChannelRepository
from infra.db.adapters.mtproto_repository_adapter import (
    MTProtoAuditRepositoryAdapter,
    MTProtoChannelRepositoryAdapter,
)
from infra.db.repositories.channel_mtproto_repository import ChannelMTProtoRepository


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session from DI container."""
    container = get_container()
    session_factory = await container.database.async_session_maker()
    async with session_factory() as session:
        yield session


async def get_channel_mtproto_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChannelMTProtoRepository:
    """Get Channel MTProto Repository."""
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
