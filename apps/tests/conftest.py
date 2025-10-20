"""
Pytest Configuration and Shared Fixtures
========================================

This module provides shared test fixtures and configuration for all apps tests.
"""

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Set test environment
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://localhost/analyticbot_test"
)


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, no I/O)")
    config.addinivalue_line("markers", "integration: Integration tests (with DB/API)")
    config.addinivalue_line("markers", "slow: Slow tests (may take >5s)")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "bot: Bot handler tests")
    config.addinivalue_line("markers", "di: Dependency injection tests")


# ============================================================================
# Event Loop Fixture
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    from config.settings import settings

    # Use test database URL with proper null handling
    default_url = (
        settings.DATABASE_URL.replace("/analyticbot", "/analyticbot_test")
        if settings.DATABASE_URL
        else "postgresql+asyncpg://localhost/analyticbot_test"
    )
    test_db_url = os.getenv("TEST_DATABASE_URL", default_url)

    engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    This fixture provides a clean database session that is rolled back
    after each test to ensure test isolation.
    """
    # Create session factory
    async_session_factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_factory() as session:
        # Start a transaction
        async with session.begin():
            yield session
            # Rollback after test
            await session.rollback()


# ============================================================================
# DI Container Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def test_container():
    """
    Provide a test DI container with all dependencies.

    This fixture initializes the application's DI container
    with test configuration.
    """
    from apps.di import get_container, initialize_container

    # Initialize with test config
    await initialize_container()
    container = get_container()

    yield container

    # Cleanup
    from apps.di import cleanup_container

    await cleanup_container()


@pytest_asyncio.fixture(scope="function")
async def test_db_pool(test_container):
    """Provide a test database pool."""
    pool = await test_container.database.asyncpg_pool()
    yield pool


# ============================================================================
# API Client Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def api_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for API testing.

    This client can be used to make requests to the FastAPI application
    without starting the actual server.
    """
    from apps.api.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(
    api_client: AsyncClient, test_container
) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an authenticated HTTP client.

    This client includes valid JWT authentication headers.
    """
    # Create a test user and get auth token
    from core.security_engine import create_access_token  # Fixed Oct 19, 2025: Updated import path

    test_user_id = 123456789  # Test user ID
    token = create_access_token({"user_id": test_user_id})

    # Add auth header
    api_client.headers["Authorization"] = f"Bearer {token}"

    yield api_client


# ============================================================================
# Repository Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def user_repo(test_container):
    """Provide a user repository for testing."""
    return await test_container.database.user_repo()


@pytest_asyncio.fixture(scope="function")
async def channel_repo(test_container):
    """Provide a channel repository for testing."""
    return await test_container.database.channel_repo()


@pytest_asyncio.fixture(scope="function")
async def analytics_repo(test_container):
    """Provide an analytics repository for testing."""
    return await test_container.database.analytics_repo()


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def test_user_data():
    """Provide sample user data for testing."""
    return {
        "telegram_id": 123456789,
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "is_premium": False,
    }


@pytest.fixture
def test_channel_data():
    """Provide sample channel data for testing."""
    return {
        "telegram_id": -1001234567890,
        "title": "Test Channel",
        "username": "test_channel",
        "is_active": True,
    }


@pytest.fixture
def test_admin_data():
    """Provide sample admin user data for testing."""
    return {
        "telegram_id": 987654321,
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "is_superadmin": True,
    }


# ============================================================================
# Bot Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def bot_client(test_container):
    """Provide a bot client for testing."""
    return await test_container.bot.bot_client()


@pytest.fixture
def mock_update():
    """Provide a mock Telegram update object."""
    from unittest.mock import MagicMock

    update = MagicMock()
    update.message.chat.id = 123456789
    update.message.from_user.id = 123456789
    update.message.from_user.username = "testuser"
    update.message.text = "/start"

    return update


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def cleanup_test_data():
    """
    Fixture to track and cleanup test data.

    Usage:
        def test_something(cleanup_test_data):
            user_id = create_test_user()
            cleanup_test_data.add("user", user_id)
            # Test runs...
            # Cleanup happens automatically
    """
    data_to_cleanup = {"users": [], "channels": [], "analytics": []}

    class CleanupHelper:
        def add(self, entity_type: str, entity_id: int):
            if entity_type in data_to_cleanup:
                data_to_cleanup[entity_type].append(entity_id)

    yield CleanupHelper()

    # Cleanup logic would go here
    # For now, we rely on transaction rollback


# ============================================================================
# Markers and Skip Conditions
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """Modify test items based on markers and conditions."""
    # Skip integration tests if TEST_SKIP_INTEGRATION is set
    skip_integration = os.getenv("TEST_SKIP_INTEGRATION", "false").lower() == "true"

    if skip_integration:
        skip_marker = pytest.mark.skip(reason="Skipping integration tests")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_marker)
