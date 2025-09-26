"""Placeholder for MockAuthService - to be migrated"""

from ..base import BaseMockService  
from ..protocols import AuthServiceProtocol

class MockAuthService(BaseMockService, AuthServiceProtocol):
    def __init__(self):
        super().__init__("MockAuthService")
    
    def get_service_name(self) -> str:
        return self.service_name
    
    async def validate_token(self, token: str):
        return {"valid": True, "user_id": 123}