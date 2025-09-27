"""
Shared Telegram Client Infrastructure
"""

import os
from dataclasses import dataclass
from typing import Any

from telethon import TelegramClient


@dataclass
class TelegramConfig:
    """Telegram API configuration"""

    api_id: int
    api_hash: str
    phone_number: str
    session_name: str = "analyticbot_session"

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        """Load config from environment variables"""
        return cls(
            api_id=int(os.getenv("TELEGRAM_API_ID", "0")),
            api_hash=os.getenv("TELEGRAM_API_HASH", ""),
            phone_number=os.getenv("TELEGRAM_PHONE", ""),
            session_name=os.getenv("TELEGRAM_SESSION", "analyticbot_session"),
        )


class SharedTelegramClient:
    """Shared Telegram client for all modules"""

    def __init__(self, config: TelegramConfig | None = None):
        self.config = config or TelegramConfig.from_env()
        self._client: TelegramClient | None = None
        self._connected = False

    async def get_client(self) -> TelegramClient:
        """Get or create Telegram client instance"""
        if self._client is None:
            self._client = TelegramClient(
                f"data/{self.config.session_name}",
                self.config.api_id,
                self.config.api_hash,
            )

        if not self._connected:
            await self._client.start(phone=self.config.phone_number)
            self._connected = True

        return self._client

    async def disconnect(self):
        """Disconnect from Telegram"""
        if self._client and self._connected:
            await self._client.disconnect()
            self._connected = False

    async def check_auth_status(self) -> dict[str, Any]:
        """Check authentication status"""
        try:
            client = await self.get_client()
            me = await client.get_me()

            return {
                "authenticated": True,
                "user_id": me.id,
                "username": me.username,
                "phone": me.phone,
            }

        except Exception as e:
            return {"authenticated": False, "error": str(e)}


# Global telegram client instance
_telegram_client: SharedTelegramClient | None = None


def get_telegram_client() -> SharedTelegramClient:
    """Get global telegram client instance"""
    global _telegram_client
    if _telegram_client is None:
        _telegram_client = SharedTelegramClient()
    return _telegram_client
