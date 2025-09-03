"""
Global pytest configuration and fixtures for AnalyticBot testing
Provides shared test infrastructure for all test modules
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import asyncpg
import pytest
from aiogram import Bot
from faker import Faker
from sqlalchemy.orm import sessionmaker

# Test database configuration
# Test database configuration - use SQLite for tests (faster, no external dependencies)
TEST_DATABASE_URL = "sqlite:///./test_analyticbot.db"

# Faker instance for generating test data
fake = Faker()


# Configure asyncio event loop for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
async def mock_db_pool() -> AsyncMock:
    """Mock asyncpg connection pool for testing"""
    pool = AsyncMock(spec=asyncpg.Pool)

    # Common database mock responses
    pool.fetchrow.return_value = None
    pool.fetchval.return_value = None
    pool.fetch.return_value = []
    pool.execute.return_value = None

    return pool


@pytest.fixture
async def mock_db_connection() -> AsyncMock:
    """Mock database connection for testing"""
    connection = AsyncMock(spec=asyncpg.Connection)

    # Common connection mock responses
    connection.fetchrow.return_value = None
    connection.fetchval.return_value = None
    connection.fetch.return_value = []
    connection.execute.return_value = None

    return connection


@pytest.fixture
def mock_bot() -> MagicMock:
    """Mock Telegram Bot for testing"""
    bot = MagicMock(spec=Bot)

    # Common bot mock responses
    bot.send_message.return_value = AsyncMock(message_id=12345)
    bot.edit_message_text.return_value = AsyncMock()
    bot.delete_message.return_value = AsyncMock()

    return bot


@pytest.fixture
def test_user_data() -> dict:
    """Generate realistic test user data"""
    return {
        "id": fake.random_int(min=100000, max=999999999),
        "username": fake.user_name(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "plan_id": 1,
        "created_at": fake.date_time_this_year(),
    }


@pytest.fixture
def test_channel_data() -> dict:
    """Generate realistic test channel data"""
    return {
        "id": fake.random_int(min=-1000000000000, max=-1),
        "title": fake.company(),
        "username": fake.user_name(),
        "type": "channel",
        "member_count": fake.random_int(min=100, max=100000),
        "user_id": fake.random_int(min=100000, max=999999999),
    }


@pytest.fixture
def test_post_data() -> dict:
    """Generate realistic test post data"""
    return {
        "id": fake.uuid4(),
        "channel_id": fake.random_int(min=-1000000000000, max=-1),
        "text": fake.text(max_nb_chars=200),
        "scheduled_time": fake.date_time_this_month(),
        "status": "pending",
        "views": fake.random_int(min=0, max=10000),
    }


@pytest.fixture
def test_payment_data() -> dict:
    """Generate realistic test payment data"""
    return {
        "id": fake.uuid4(),
        "user_id": fake.random_int(min=100000, max=999999999),
        "amount": fake.random_int(min=1000, max=50000),  # cents
        "currency": fake.random_element(elements=["USD", "UZS"]),
        "provider": fake.random_element(elements=["stripe", "payme", "click"]),
        "status": fake.random_element(elements=["pending", "completed", "failed"]),
        "created_at": fake.date_time_this_year(),
    }


class TestDatabase:
    """Test database helper for integration tests using SQLite"""

    def __init__(self, db_url: str = TEST_DATABASE_URL):
        self.db_url = db_url
        self.engine = None
        self.session_factory = None

    async def setup(self):
        """Setup test database connection"""
        try:
            # Convert SQLite URL to async format if needed
            if self.db_url.startswith("sqlite://"):
                # For SQLite, we need to use aiosqlite
                from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

                self.engine = create_async_engine(
                    self.db_url.replace("sqlite://", "sqlite+aiosqlite://"),
                    echo=False,
                    connect_args={"check_same_thread": False},
                )
            else:
                # For PostgreSQL, use asyncpg
                self.engine = create_async_engine(self.db_url, echo=False)

            self.session_factory = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Create tables if they don't exist
            from core.models import Base

            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        except Exception as e:
            pytest.skip(f"Test database not available: {e}")

    async def cleanup(self):
        """Clean up test database"""
        if self.engine:
            await self.engine.dispose()

    async def reset_tables(self):
        """Reset all tables for clean test state"""
        if not self.engine:
            return

        from core.models import Base

        async with self.engine.begin() as conn:
            # Drop all tables and recreate them
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def test_database() -> AsyncGenerator[TestDatabase, None]:
    """Test database fixture for integration tests"""
    db = TestDatabase()
    await db.setup()
    yield db
    await db.cleanup()


@pytest.fixture(autouse=True)
async def reset_test_data(request):
    """Automatically reset test data before each test - but only for integration tests that need real DB"""
    # Skip database setup for unit tests - be more specific to avoid over-skipping
    if hasattr(request, "keywords") and (
        "unit" in request.keywords
        or "mock" in request.keywords
        or request.node.get_closest_marker("unit")
    ):
        yield
        return

    # Skip database setup for tests that don't need real database
    if (
        "test_domain_simple" in str(request.node.nodeid)
        or "test_imports" in str(request.node.nodeid)
        or "test_health" in str(request.node.nodeid)
    ):
        yield
        return

    # Skip database setup for mock-based integration tests (our new external service tests)
    if (
        "test_telegram_integration" in request.node.nodeid
        or "test_payment_integration" in request.node.nodeid
        or "test_redis_integration" in request.node.nodeid
        or "test_api_basic" in request.node.nodeid
    ):
        yield
        return

    # Only run database reset for integration tests that explicitly need it
    if hasattr(request, "param") and request.param == "no_db":
        yield
        return

    # Try to setup database for integration tests that actually need real DB
    try:
        test_db = TestDatabase()
        await test_db.setup()
        await test_db.reset_tables()
        yield test_db
        await test_db.cleanup()
    except Exception as e:
        # Skip if database not available for integration tests
        pytest.skip(f"Database not available for integration test: {e}")


# Test environment variables
@pytest.fixture(autouse=True)
def test_env_vars():
    """Set test environment variables"""
    test_vars = {
        "BOT_TOKEN": "123456789:TEST_BOT_TOKEN_FOR_TESTING",
        "DATABASE_URL": TEST_DATABASE_URL,
        "REDIS_URL": "redis://localhost:6379/15",  # Use test DB 15
        "ENVIRONMENT": "test",
        "DEBUG": "true",
    }

    # Store original values
    original_values = {}
    for key, value in test_vars.items():
        original_values[key] = os.environ.get(key)
        os.environ[key] = value

    yield

    # Restore original values
    for key, original_value in original_values.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


# Performance testing helpers
@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.perf_counter()

        def stop(self):
            self.end_time = time.perf_counter()
            return self.end_time - self.start_time

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()


# Test markers configuration
pytest_plugins = ["pytest_asyncio", "pytest_mock", "pytest_cov"]


# Custom test markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "external: Tests requiring external services")
