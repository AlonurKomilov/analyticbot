"""
DI Container Tests
==================

Test the dependency injection container initialization and wiring.
"""

import pytest


@pytest.mark.di
@pytest.mark.unit
class TestContainerInitialization:
    """Test DI container initialization."""

    @pytest.mark.asyncio
    async def test_container_can_be_initialized(self, test_container):
        """Test that the DI container can be initialized."""
        assert test_container is not None
        assert hasattr(test_container, "database")
        assert hasattr(test_container, "bot")
        assert hasattr(test_container, "core_services")

    @pytest.mark.asyncio
    async def test_container_provides_database_resources(self, test_container):
        """Test that database resources are available."""
        # Check database container exists
        assert test_container.database is not None

        # Check we can get a pool
        pool = await test_container.database.asyncpg_pool()
        assert pool is not None

    @pytest.mark.asyncio
    async def test_container_provides_repositories(self, test_container):
        """Test that repositories can be resolved."""
        # Test user repository
        user_repo = await test_container.database.user_repo()
        assert user_repo is not None

        # Test channel repository
        channel_repo = await test_container.database.channel_repo()
        assert channel_repo is not None

        # Test analytics repository
        analytics_repo = await test_container.database.analytics_repo()
        assert analytics_repo is not None


@pytest.mark.di
@pytest.mark.integration
class TestRepositoryFactory:
    """Test the repository factory pattern."""

    @pytest.mark.asyncio
    async def test_user_repo_can_be_created(self, user_repo):
        """Test that user repository can be created."""
        assert user_repo is not None
        # Check it has expected methods
        assert hasattr(user_repo, "get_user")
        assert hasattr(user_repo, "create_user")

    @pytest.mark.asyncio
    async def test_channel_repo_can_be_created(self, channel_repo):
        """Test that channel repository can be created."""
        assert channel_repo is not None
        assert hasattr(channel_repo, "get_channel")
        assert hasattr(channel_repo, "create_channel")

    @pytest.mark.asyncio
    async def test_analytics_repo_can_be_created(self, analytics_repo):
        """Test that analytics repository can be created."""
        assert analytics_repo is not None
        assert hasattr(analytics_repo, "get_analytics")


@pytest.mark.di
@pytest.mark.integration
class TestServiceResolution:
    """Test that services can be resolved from the container."""

    @pytest.mark.asyncio
    async def test_core_services_available(self, test_container):
        """Test that core services are available."""
        assert test_container.core_services is not None

        # Test analytics fusion service
        analytics_service = await test_container.core_services.analytics_fusion_service()
        assert analytics_service is not None

    @pytest.mark.asyncio
    async def test_bot_services_available(self, test_container):
        """Test that bot services are available."""
        assert test_container.bot is not None

        # Test bot client (may need mocking in test env)
        # bot_client = await test_container.bot.bot_client()
        # assert bot_client is not None


@pytest.mark.di
@pytest.mark.unit
class TestContainerCleanup:
    """Test container cleanup and resource management."""

    @pytest.mark.asyncio
    async def test_container_cleanup_succeeds(self):
        """Test that container cleanup doesn't raise errors."""
        from apps.di import cleanup_container, get_container, initialize_container

        # Initialize
        await initialize_container()
        container = get_container()
        assert container is not None

        # Cleanup
        await cleanup_container()
        # Should not raise any errors
