"""Placeholder for MockDemoDataService - to be migrated"""

from ..base import BaseMockService
from ..protocols import DemoDataServiceProtocol

class MockDemoDataService(BaseMockService, DemoDataServiceProtocol):
    def __init__(self):
        super().__init__("MockDemoDataService")
    
    def get_service_name(self) -> str:
        return self.service_name