"""
Dependencies for Storage API

Shared dependencies for all storage endpoints.
"""

from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncSession:
    """Get database session from DI container."""
    from apps.di import get_container

    container = get_container()
    session_factory = await container.database.async_session_maker()
    async with session_factory() as session:
        yield session
