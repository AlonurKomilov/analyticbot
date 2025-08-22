"""
SQLite database engine for development
"""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from bot.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# SQLAlchemy Engine
engine: AsyncEngine = None
async_session: async_sessionmaker[AsyncSession] = None


async def init_db():
    """Initialize SQLite database"""
    global engine, async_session

    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,  # Set to True for SQL logging
            future=True,
        )

        # Create session factory
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info("✅ SQLite database initialized")
        return engine

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def get_session() -> AsyncSession:
    """Get database session"""
    if async_session is None:
        await init_db()
    return async_session()


async def close_db():
    """Close database connections"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("✅ Database connections closed")
