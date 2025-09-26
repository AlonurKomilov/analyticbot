"""Placeholder for MockAdminService - to be migrated"""

from ..base import BaseMockService
from ..protocols import AdminServiceProtocol

class MockAdminService(BaseMockService, AdminServiceProtocol):
    def __init__(self):
        super().__init__("MockAdminService")
    
    def get_service_name(self) -> str:
        return self.service_name