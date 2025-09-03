from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from core.ports.mtproto_config import MTProtoConfigProtocol

# Try to import Telethon - graceful fallback if not installed
try:
    from telethon import TelegramClient, events
    from telethon.errors import (
        AuthKeyNotFound,
        FloodWaitError,
        SessionPasswordNeededError,
    )
    from telethon.tl.types import Channel, Chat, User

    TELETHON_AVAILABLE = True
except ImportError:
    TelegramClient = None
    events = None
    FloodWaitError = Exception
    AuthKeyNotFound = Exception
    SessionPasswordNeededError = Exception
    Channel = Chat = User = None
    TELETHON_AVAILABLE = False


class TelethonTGClient:
    """Real Telethon-based Telegram client implementation with feature flag support.

    This implementation provides actual Telegram connectivity when MTPROTO_ENABLED
    is True and Telethon is installed. Falls back gracefully when disabled or
    Telethon is not available.
    """

    def __init__(self, settings: MTProtoConfigProtocol):
        """Initialize the Telethon Telegram client.

        Args:
            settings: MTProto configuration settings
        """
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._client = None  # Type will be inferred, TelegramClient | None
        self._started = False

        # Validate configuration when features are enabled
        if self.settings.MTPROTO_ENABLED:
            if not TELETHON_AVAILABLE:
                raise ImportError(
                    "Telethon is required when MTPROTO_ENABLED=True. "
                    "Install with: pip install telethon"
                )

            if not self.settings.TELEGRAM_API_ID or not self.settings.TELEGRAM_API_HASH:
                raise ValueError(
                    "TELEGRAM_API_ID and TELEGRAM_API_HASH are required when MTPROTO_ENABLED=True"
                )

    async def start(self) -> None:
        """Start the client connection."""
        if not self.settings.MTPROTO_ENABLED:
            self.logger.info("MTProto disabled, using stub client")
            self._started = True
            return

        if not TELETHON_AVAILABLE:
            raise RuntimeError("Telethon not available but MTPROTO_ENABLED=True")

        try:
            # Initialize Telethon client
            self._client = TelegramClient(
                self.settings.TELEGRAM_SESSION_NAME,
                self.settings.TELEGRAM_API_ID,
                self.settings.TELEGRAM_API_HASH,
                proxy=self._parse_proxy(self.settings.TELEGRAM_PROXY),
            )

            # Set raw mode for minimal parsing overhead
            self._client.parse_mode = None

            # Start the client
            await self._client.start()
            self._started = True
            self.logger.info("Telethon client started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start Telethon client: {e}")
            raise

    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self._client and self._client.is_connected():
            await self._client.disconnect()
            self.logger.info("Telethon client stopped")
        self._started = False

    async def is_connected(self) -> bool:
        """Check if client is connected."""
        if not self.settings.MTPROTO_ENABLED or not self._client:
            return False
        return self._client.is_connected()

    async def iter_history(
        self, peer: Any, *, offset_id: int = 0, limit: int = 200
    ) -> AsyncIterator[Any]:
        """Iterate through message history with rate limiting and error handling.

        Args:
            peer: The target peer
            offset_id: Start from this message ID
            limit: Maximum messages per request

        Yields:
            Message objects
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            self.logger.info("MTProto disabled, no history available")
            return

        try:
            async for message in self._client.iter_messages(peer, offset_id=offset_id, limit=limit):
                yield message

                # Rate limiting
                await asyncio.sleep(self.settings.MTPROTO_SLEEP_THRESHOLD / 10)

        except FloodWaitError as e:
            wait_time = e.seconds
            self.logger.warning(f"Rate limited, waiting {wait_time} seconds")
            await asyncio.sleep(wait_time * self.settings.MTPROTO_RETRY_BACKOFF)

        except Exception as e:
            self.logger.error(f"Error in iter_history: {e}")
            raise

    async def iter_updates(self) -> AsyncIterator[Any]:
        """Iterate through real-time updates with error handling.

        Yields:
            Update objects from Telegram
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            self.logger.info("MTProto disabled, no updates available")
            return

        if not self.settings.MTPROTO_UPDATES_ENABLED:
            self.logger.info("Updates collection disabled")
            return

        try:
            # Set up update handler for new messages
            @self._client.on(events.NewMessage)
            async def handler(event):
                yield event

            @self._client.on(events.MessageEdited)
            async def edit_handler(event):
                yield event

            # Keep connection alive and yield updates
            await self._client.run_until_disconnected()

        except FloodWaitError as e:
            wait_time = e.seconds
            self.logger.warning(f"Updates rate limited, waiting {wait_time} seconds")
            await asyncio.sleep(wait_time * self.settings.MTPROTO_RETRY_BACKOFF)

        except Exception as e:
            self.logger.error(f"Error in iter_updates: {e}")
            raise

    async def get_broadcast_stats(self, channel: Any) -> Any:
        """Get broadcast channel statistics."""
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            return {"_": "stats.BroadcastStats(disabled)"}

        # This would be implemented in Phase 4.3
        return {"_": "stats.BroadcastStats(placeholder)"}

    async def get_megagroup_stats(self, chat: Any) -> Any:
        """Get megagroup statistics."""
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            return {"_": "stats.MegagroupStats(disabled)"}

        # This would be implemented in Phase 4.3
        return {"_": "stats.MegagroupStats(placeholder)"}

    async def load_async_graph(self, token: str) -> Any:
        """Load async graph data."""
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            return {"json": "{}", "token": token}

        # This would be implemented in Phase 4.3
        return {"json": "{}", "token": token}

    async def get_full_channel(self, peer: Any) -> Any:
        """Get full channel information."""
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            return {"full": False, "peer": str(peer)}

        try:
            entity = await self._client.get_entity(peer)
            return await self._client.get_full_channel(entity)

        except Exception as e:
            self.logger.error(f"Error getting full channel: {e}")
            return {"full": False, "peer": str(peer), "error": str(e)}

    async def get_me(self) -> Any:
        """Get current user information."""
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")

        if not self.settings.MTPROTO_ENABLED or not self._client:
            return {"id": 123456789, "username": "stub_user", "is_bot": False}

        try:
            return await self._client.get_me()
        except Exception as e:
            self.logger.error(f"Error getting user info: {e}")
            return {"id": 0, "username": "error", "is_bot": False, "error": str(e)}

    async def disconnect(self) -> None:
        """Disconnect the client."""
        await self.stop()

    def _parse_proxy(self, proxy_url: str | None) -> dict | None:
        """Parse proxy URL into Telethon proxy format."""
        if not proxy_url:
            return None

        try:
            # Simple proxy parsing for socks5://user:pass@host:port
            if proxy_url.startswith("socks5://"):
                # This would need proper URL parsing in production
                return None  # Simplified for now
        except Exception:
            self.logger.warning(f"Failed to parse proxy URL: {proxy_url}")

        return None
