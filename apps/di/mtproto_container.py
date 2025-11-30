"""
MTProto Services DI Container

Single Responsibility: MTProto-specific services and client management
Includes user MTProto service, session management, and channel settings

This container manages all MTProto-related dependencies separately from the API container,
following the same pattern as BotContainer for bot services.
"""

from dependency_injector import containers, providers


async def create_user_mtproto_service(database):
    """
    Create UserMTProtoService instance with repository factory.

    Args:
        database: Database container with session factory

    Returns:
        UserMTProtoService configured with repository factory
    """
    from apps.mtproto.multi_tenant.user_mtproto_service import UserMTProtoService
    from infra.db.repositories.user_bot_repository_factory import (
        UserBotRepositoryFactory,
    )

    # Get async session factory from database container
    session_factory = await database.async_session_maker()

    # Create repository factory (handles session lifecycle internally)
    repository_factory = UserBotRepositoryFactory(session_factory)

    # Create service with factory pattern
    return UserMTProtoService(user_bot_repo_factory=repository_factory)


class MTProtoContainer(containers.DeclarativeContainer):
    """
    MTProto Services Container

    Single Responsibility: User MTProto client management and services
    Provides MTProto service for multi-tenant channel history access
    """

    config = providers.Configuration()

    # Dependencies from other containers
    database = providers.DependenciesContainer()

    # ============================================================================
    # MTPROTO SERVICES
    # ============================================================================

    user_mtproto_service = providers.Singleton(
        create_user_mtproto_service,
        database=database,
    )
