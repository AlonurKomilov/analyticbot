"""
Shared Telegram Client Infrastructure
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import os


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
            session_name=os.getenv("TELEGRAM_SESSION", "analyticbot_session")
        )


class SharedTelegramClient:
    """Shared Telegram client for all modules"""
    
    def __init__(self, config: Optional[TelegramConfig] = None):
        self.config = config or TelegramConfig.from_env()
        self._client: Optional[TelegramClient] = None
        self._connected = False
    
    async def get_client(self) -> TelegramClient:
        """Get or create Telegram client instance"""
        if self._client is None:
            self._client = TelegramClient(
                f"data/{self.config.session_name}",
                self.config.api_id,
                self.config.api_hash
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
    
    async def check_auth_status(self) -> Dict[str, Any]:
        """Check authentication status"""
        try:
            client = await self.get_client()
            me = await client.get_me()
            
            return {
                "authenticated": True,
                "user_id": me.id,
                "username": me.username,
                "phone": me.phone
            }
        
        except Exception as e:
            return {
                "authenticated": False,
                "error": str(e)
            }


# Global telegram client instance
_telegram_client: Optional[SharedTelegramClient] = None

def get_telegram_client() -> SharedTelegramClient:
    """Get global telegram client instance"""
    global _telegram_client
    if _telegram_client is None:
        _telegram_client = SharedTelegramClient()
    return _telegram_client
