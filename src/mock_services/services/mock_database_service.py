"""
Mock Database Service for centralized mock services
"""

from typing import Any

from .base_service import BaseMockService


class MockDatabaseService(BaseMockService):
    """Mock Database Service for testing and development"""

    def __init__(self):
        super().__init__()
        self._data = {}
        self._connection_count = 0

    def get_service_name(self) -> str:
        return "MockDatabaseService"

    def connect(self):
        """Mock database connection"""
        self._connection_count += 1
        return MockConnection()

    def disconnect(self):
        """Mock database disconnection"""
        self._connection_count = max(0, self._connection_count - 1)

    def get_connection_count(self):
        """Get current connection count"""
        return self._connection_count

    def execute_query(self, query: str, params: dict | None = None):
        """Execute mock database query"""
        return MockResult(
            [
                {"id": 1, "name": "Mock Record 1", "value": "test1"},
                {"id": 2, "name": "Mock Record 2", "value": "test2"},
            ]
        )

    def get_table_info(self, table_name: str) -> dict[str, Any]:
        """Get mock table information"""
        return {
            "table_name": table_name,
            "columns": ["id", "name", "value", "created_at"],
            "row_count": 100,
            "size_mb": 5.2,
        }

    def reset(self):
        """Reset mock database state"""
        self._data.clear()
        self._connection_count = 0


class MockConnection:
    """Mock database connection"""

    def __init__(self):
        self._is_connected = True

    def execute(self, query: str, params: dict | None = None):
        """Mock query execution"""
        return MockResult()

    def close(self):
        """Close mock connection"""
        self._is_connected = False

    def is_connected(self) -> bool:
        return self._is_connected


class MockResult:
    """Mock query result"""

    def __init__(self, data: list[dict] = None):
        self._data = data or []

    def fetchall(self) -> list[dict]:
        return self._data

    def fetchone(self) -> dict | None:
        return self._data[0] if self._data else None

    def rowcount(self) -> int:
        return len(self._data)
