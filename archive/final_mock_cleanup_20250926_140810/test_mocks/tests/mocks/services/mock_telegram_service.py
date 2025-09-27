"""Placeholder for MockTelegramService - to be migrated"""

from ..base import BaseMockService
from ..protocols import TelegramAPIServiceProtocol


class MockTelegramService(BaseMockService, TelegramAPIServiceProtocol):
    def __init__(self):
        super().__init__("MockTelegramService")

    def get_service_name(self) -> str:
        return self.service_name

    async def get_channel_info(self, channel_id: str):
        return {"channel_id": channel_id, "name": "Mock Channel"}
