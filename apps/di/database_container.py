"""
Database & Repository DI Container

Single Responsibility: Database connectivity and repository factory
Clean Architecture compliant - uses repository factory pattern
"""

import logging
import os
from typing import Any

import asyncpg
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from apps.shared.factory import get_repository_factory
from infra.db.connection_manager import DatabaseManager, db_manager

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


async def _create_database_manager() -> DatabaseManager:
    """Create or get optimized database manager"""
    if not db_manager._pool:
        await db_manager.initialize()
    return db_manager


async def _create_asyncpg_pool(database_url: str, pool_size: int = 10) -> asyncpg.Pool:
    """Create asyncpg connection pool"""
    # Convert SQLAlchemy URL to asyncpg format if needed
    db_url = database_url
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    pool = await asyncpg.create_pool(db_url, min_size=1, max_size=pool_size)
    if pool is None:
        raise RuntimeError("Failed to create asyncpg pool")
    return pool


async def _create_sqlalchemy_engine(
    database_url: str, pool_size: int = 10, max_overflow: int = 20
) -> AsyncEngine:
    """Create SQLAlchemy async engine"""
    return create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )


async def _create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create SQLAlchemy session factory"""
    return async_sessionmaker(engine, expire_on_commit=False)


async def _create_repository(factory, repo_type: str) -> Any:
    """Create repository using factory pattern - no direct infra imports"""
    try:
        if repo_type == "user":
            return await factory.get_user_repository()
        elif repo_type == "channel":
            return await factory.get_channel_repository()
        elif repo_type == "analytics":
            return await factory.get_analytics_repository()
        elif repo_type == "admin":
            return await factory.get_admin_repository()
        elif repo_type == "plan":
            return await factory.get_plan_repository()
        elif repo_type == "schedule":
            return await factory.get_schedule_repository()
        elif repo_type == "payment":
            return await factory.get_payment_repository()
        elif repo_type == "post":
            return await factory.get_post_repository()
        elif repo_type == "metrics":
            return await factory.get_metrics_repository()
        elif repo_type == "channel_daily":
            return await factory.get_channel_daily_repository()
        elif repo_type == "edges":
            return await factory.get_edges_repository()
        elif repo_type == "stats_raw":
            return await factory.get_stats_raw_repository()
        else:
            logger.warning(f"Unknown repository type: {repo_type}")
            return None
    except Exception as e:
        logger.warning(f"Failed to create {repo_type} repository: {e}")
        return None


# ============================================================================
# DATABASE CONTAINER
# ============================================================================


class DatabaseContainer(containers.DeclarativeContainer):
    """
    Database & Repository Container

    Single Responsibility: Manages database connections and repository access
    Follows Clean Architecture - uses factory pattern for repositories
    """

    # Configuration
    config = providers.Configuration()

    # Database URL from environment or configuration
    database_url = providers.Callable(
        lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://analytic:change_me@localhost:5432/analytic_bot"
        )
    )

    # ============================================================================
    # DATABASE CONNECTIONS
    # ============================================================================

    database_manager = providers.Resource(_create_database_manager)

    asyncpg_pool = providers.Resource(
        _create_asyncpg_pool,
        database_url=database_url,
        pool_size=10
    )

    sqlalchemy_engine = providers.Resource(
        _create_sqlalchemy_engine,
        database_url=database_url,
        pool_size=10,
        max_overflow=20
    )

    session_factory = providers.Resource(
        _create_session_factory,
        engine=sqlalchemy_engine
    )

    # ============================================================================
    # REPOSITORY FACTORY (Clean Architecture Pattern)
    # ============================================================================

    repository_factory = providers.Singleton(get_repository_factory)

    # ============================================================================
    # REPOSITORIES (via factory pattern - no direct infra imports)
    # ============================================================================

    user_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="user"
    )

    channel_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="channel"
    )

    analytics_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="analytics"
    )

    admin_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="admin"
    )

    plan_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="plan"
    )

    schedule_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="schedule"
    )

    payment_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="payment"
    )

    post_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="post"
    )

    metrics_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="metrics"
    )

    channel_daily_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="channel_daily"
    )

    edges_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="edges"
    )

    stats_raw_repo = providers.Factory(
        _create_repository,
        factory=repository_factory,
        repo_type="stats_raw"
    )


# ============================================================================
# CLEANUP
# ============================================================================


async def cleanup_database_pool():
    """Cleanup database connections"""
    logger.info("Cleaning up database connections")
    # Cleanup will be handled by container lifecycle
