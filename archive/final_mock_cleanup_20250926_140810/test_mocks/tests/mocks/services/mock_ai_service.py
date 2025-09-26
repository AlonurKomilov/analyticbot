"""Placeholder for MockAIService - to be migrated"""

from ..base import BaseMockService
from ..protocols import AIServiceProtocol

class MockAIService(BaseMockService, AIServiceProtocol):
    def __init__(self):
        super().__init__("MockAIService")
    
    def get_service_name(self) -> str:
        return self.service_name
    
    async def generate_content(self, prompt: str) -> str:
        return f"AI generated content for: {prompt[:50]}"