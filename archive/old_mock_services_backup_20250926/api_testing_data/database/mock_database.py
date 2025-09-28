"""
Database Mock Data Module
Extracted from di_analytics.py to maintain clean separation of mock data
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

from core.protocols import DatabaseServiceProtocol


class MockDatabase(DatabaseServiceProtocol):
    """Mock database service for testing and demo mode"""

    def __init__(self):
        self._data = create_mock_analytics_data()
        self._mock_pool = AsyncMock()

    async def get_connection(self):
        """Get mock database connection"""
        return AsyncMock()

    async def execute_query(self, query: str, *args):
        """Execute mock query"""
        return self._data

    async def fetch_all(self, query: str, *args):
        """Fetch all mock results"""
        return self._data

    async def fetch_one(self, query: str, *args):
        """Fetch one mock result"""
        return self._data[0] if self._data else None


def create_mock_analytics_data() -> list[dict]:
    """Create mock analytics data for database fallback"""
    return [
        {
            "date": "2025-09-07",
            "views": 1500,
            "joins": 25,
            "leaves": 5,
            "posts": 8,
            "engagement": 0.045,
        },
        {
            "date": "2025-09-08",
            "views": 1750,
            "joins": 32,
            "leaves": 3,
            "posts": 12,
            "engagement": 0.052,
        },
    ]


def create_mock_snapshot_data() -> dict:
    """Create mock snapshot data for database fallback"""
    return {
        "snapshot_time": datetime(2025, 9, 7, 12, 0, 0, tzinfo=UTC),
        "total_subscribers": 1250,
        "views_today": 3500,
        "active_users": 890,
    }


def get_mock_value_by_query(query: str) -> int:
    """Return mock values based on query type"""
    query_upper = query.upper()

    if "COUNT" in query_upper:
        return 42  # Mock count
    elif "subscriber" in query.lower():
        return 1250  # Mock subscriber count
    elif "SUM" in query_upper:
        return 15000  # Mock sum
    elif "views" in query.lower():
        return 3500  # Mock views
    elif "engagement" in query.lower():
        return 45  # Mock engagement (as percentage * 100)

    return 100  # Default mock value


class EnhancedMockPool:
    """Enhanced mock database pool that mimics asyncpg behavior"""

    async def fetchval(self, query: str, *args) -> int:
        """Mock fetchval method"""
        return get_mock_value_by_query(query)

    async def fetch(self, query: str, *args) -> list[dict]:
        """Mock fetch method"""
        return create_mock_analytics_data()

    async def fetchrow(self, query: str, *args) -> dict:
        """Mock fetchrow method"""
        return create_mock_snapshot_data()

    def acquire(self):
        """Mock acquire method"""
        return self

    async def __aenter__(self):
        """Mock async context manager entry"""
        return self

    async def __aexit__(self, *args):
        """Mock async context manager exit"""

    async def execute(self, query: str, *args) -> str:
        """Mock execute method"""
        return "INSERT 0 1"  # Mock successful insert


def create_enhanced_mock_pool() -> EnhancedMockPool:
    """Create enhanced mock pool for graceful database degradation"""
    return EnhancedMockPool()


# Legacy mock connection for backwards compatibility
class MockConnection:
    """Legacy mock connection class"""

    def __init__(self):
        self.execute = AsyncMock(return_value=None)
        self.fetchrow = AsyncMock(return_value=create_mock_snapshot_data())
        self.fetchval = AsyncMock(return_value=100)
        self.fetch = AsyncMock(return_value=create_mock_analytics_data())

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class MockPool:
    """Legacy mock pool class"""

    def __init__(self):
        self._connection = MockConnection()

    def acquire(self):
        return self._connection

    async def fetchval(self, query: str, *args):
        return get_mock_value_by_query(query)

    async def fetch(self, query: str, *args):
        return create_mock_analytics_data()

    async def fetchrow(self, query: str, *args):
        return create_mock_snapshot_data()

    async def execute(self, query: str, *args):
        return "INSERT 0 1"


def create_legacy_mock_pool() -> MockPool:
    """Create legacy mock pool for backwards compatibility"""
    return MockPool()
