"""
BotService Interface - Public API for bot_service module
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class BotService(Protocol):
    """BotService public interface"""

    async def send_message(self, chat_id: int, message: str) -> dict:
        """send_message operation"""
        ...

    async def process_command(self, command: str, user_id: int) -> dict:
        """process_command operation"""
        ...

    async def handle_callback(self, callback_data: dict) -> dict:
        """handle_callback operation"""
        ...

    async def get_bot_status(self) -> dict:
        """get_bot_status operation"""
        ...
