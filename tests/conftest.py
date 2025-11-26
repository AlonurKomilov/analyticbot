"""
Pytest configuration and fixtures for AnalyticBot tests

This file provides:
- Test database configuration
- FastAPI test clients (sync and async)
- Common fixtures for testing
- Event loop configuration for async tests
"""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest

# Mock heavy ML dependencies before importing app
# This allows tests to run without installing torch, prophet, etc.
mock = MagicMock()
sys.modules["torch"] = mock
sys.modules["torch.nn"] = mock
sys.modules["torch.nn.utils"] = mock
sys.modules["torch.nn.utils.rnn"] = mock
sys.modules["torch.optim"] = mock
sys.modules["torch.cuda"] = mock
sys.modules["torchvision"] = mock
sys.modules["lightgbm"] = mock
sys.modules["xgboost"] = mock
sys.modules["prophet"] = mock
sys.modules["prophet.plot"] = mock
sys.modules["pmdarima"] = mock
sys.modules["pmdarima.arima"] = mock

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Import the FastAPI app (after mocking heavy dependencies)
from apps.api.main import app

# Test database URL - use a separate test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://analytic:change_me@localhost:10100/analytic_bot_test"
)


# ============================================================================
# Event Loop Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the test session.
    Required for pytest-asyncio to work properly.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop

    # Cleanup
    try:
        loop.close()
    except Exception:
        pass


# ============================================================================
# Test Clients
# ============================================================================


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """
    Synchronous FastAPI test client.

    Use this for simple synchronous tests:
    ```python
    def test_health(test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
    ```
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Asynchronous FastAPI test client.

    Use this for async tests that need to test async endpoints:
    ```python
    @pytest.mark.asyncio
    async def test_async_endpoint(async_client):
        response = await async_client.get("/api/endpoint")
        assert response.status_code == 200
    ```
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="session")
async def test_db_engine():
    """
    Create a test database engine for the session.
    Uses NullPool to avoid connection issues in tests.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,  # Don't pool connections in tests
    )

    yield engine

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    Each test gets a fresh session that's rolled back after the test.

    Usage:
    ```python
    @pytest.mark.asyncio
    async def test_database_operation(test_db_session):
        result = await test_db_session.execute(select(User))
        users = result.scalars().all()
        assert len(users) >= 0
    ```
    """
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        # Start a transaction
        await session.begin()

        yield session

        # Rollback the transaction after the test
        await session.rollback()


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def mock_channel_id() -> str:
    """Mock channel ID for testing"""
    return "demo_channel"


@pytest.fixture
def mock_user_data() -> dict:
    """Mock user data for authentication tests"""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture
def mock_auth_token() -> str:
    """Mock JWT token for authenticated requests"""
    # This is a test token - not valid for production
    return "test_jwt_token_12345"


@pytest.fixture
def auth_headers(mock_auth_token) -> dict:
    """Headers with authentication token"""
    return {"Authorization": f"Bearer {mock_auth_token}"}


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    """
    config.addinivalue_line("markers", "unit: Unit tests - fast, isolated tests")
    config.addinivalue_line(
        "markers", "integration: Integration tests - tests that interact with external systems"
    )
    config.addinivalue_line("markers", "slow: Slow tests - tests that take more than 1 second")
    config.addinivalue_line("markers", "asyncio: Async tests - tests that use asyncio")


def pytest_collection_modifyitems(config, items):
    """
    Automatically mark tests based on their characteristics.
    """
    for item in items:
        # Mark async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

        # Mark integration tests (tests in integration/ folder)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark unit tests (tests in unit/ folder)
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


# ============================================================================
# Environment Setup
# ============================================================================


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """
    Automatically set up test environment for all tests.
    This fixture runs before each test.
    """
    # Set test environment
    monkeypatch.setenv("ENVIRONMENT", "testing")
    monkeypatch.setenv("DEBUG", "true")

    # Use test database
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)

    # Disable external services in tests
    monkeypatch.setenv("MTPROTO_ENABLED", "false")
    monkeypatch.setenv("WEBHOOK_ENABLED", "false")

    yield

    # Cleanup happens automatically with monkeypatch


# ============================================================================
# Cleanup
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """
    Cleanup after all tests are done.
    This runs once at the end of the test session.
    """
    yield

    # Add any cleanup logic here
    # For example: clear test database, remove temporary files, etc.
    pass
