"""Placeholder for MockDatabaseService - to be migrated"""

from ..base import BaseMockService
from ..protocols import DatabaseServiceProtocol

class MockDatabaseService(BaseMockService, DatabaseServiceProtocol):
    def __init__(self):
        super().__init__("MockDatabaseService")
    
    async def get_connection(self):
        return "mock_connection"