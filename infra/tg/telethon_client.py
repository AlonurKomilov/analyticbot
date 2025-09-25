from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from core.ports.mtproto_config import MTProtoConfigProtocol

# Type-only imports for Telethon
if TYPE_CHECKING:
    from telethon import TelegramClient, events
    from telethon.errors import FloodWaitError
    from telethon.tl.types import Channel, Chat, User

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
            proxy = self._parse_proxy(self.settings.TELEGRAM_PROXY)
            client_kwargs = {
                "session": self.settings.TELEGRAM_SESSION_NAME,
                "api_id": self.settings.TELEGRAM_API_ID,
                "api_hash": self.settings.TELEGRAM_API_HASH,
            }
            if proxy is not None:
                client_kwargs["proxy"] = proxy

            if not TELETHON_AVAILABLE or TelegramClient is None:
                raise RuntimeError("Telethon is not available")

            self._client = TelegramClient(**client_kwargs)

            if self._client is None:
                raise RuntimeError("Failed to create TelegramClient instance")

            # Set raw mode for minimal parsing overhead
            if hasattr(self._client, "parse_mode"):
                self._client.parse_mode = None  # Use setattr for dynamic assignment

            # Start the client
            if hasattr(self._client, "start") and callable(self._client.start):
                await self._client.start()  # type: ignore[misc]
            self._started = True
            self.logger.info("Telethon client started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start Telethon client: {e}")
            raise

    async def stop(self) -> None:
        """Stop the Telegram client."""
        if (
            self._client
            and hasattr(self._client, "is_connected")
            and callable(getattr(self._client, "is_connected", None))
            and self._client.is_connected()
            and hasattr(self._client, "disconnect")
        ):
            await self._client.disconnect()  # type: ignore[misc]
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
            return  # Exit early for async generator

        try:
            async for message in self._client.iter_messages(peer, offset_id=offset_id, limit=limit):
                yield message

                # Rate limiting
                await asyncio.sleep(self.settings.MTPROTO_SLEEP_THRESHOLD / 10)

        except Exception as e:
            # Handle FloodWaitError if it's available
            if TELETHON_AVAILABLE and hasattr(e, "seconds"):
                wait_time = getattr(e, "seconds", 60)  # Use getattr for safe access
                self.logger.warning(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time * self.settings.MTPROTO_RETRY_BACKOFF)
            else:
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
            return  # Exit early for async generator

        if not self.settings.MTPROTO_UPDATES_ENABLED:
            self.logger.info("Updates collection disabled")
            return  # Exit early for async generator

        try:
            # Simple update iteration if available
            if TELETHON_AVAILABLE and hasattr(self._client, "iter_updates"):
                iter_updates_method = getattr(self._client, "iter_updates", None)
                if iter_updates_method and callable(iter_updates_method):
                    async for update in iter_updates_method():  # type: ignore[misc]
                        yield update
                else:
                    self.logger.warning("Updates iteration method not callable")
                    return
            else:
                self.logger.warning("Updates iteration not available")
                return

        except Exception as e:
            # Handle FloodWaitError if it's available
            if TELETHON_AVAILABLE and hasattr(e, "seconds"):
                wait_time = getattr(e, "seconds", 60)  # Use getattr for safe access
                self.logger.warning(f"Updates rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time * self.settings.MTPROTO_RETRY_BACKOFF)
            else:
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
            entity = await self._client.get_entity(peer)  # type: ignore[misc]
            if hasattr(self._client, "get_full_channel"):
                get_full_channel_method = getattr(self._client, "get_full_channel", None)
                if get_full_channel_method and callable(get_full_channel_method):
                    return await get_full_channel_method(entity)  # type: ignore[misc]

            # Fallback - just return the entity
            return entity

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

    async def connect(self) -> bool:
        """Connect the client (alias for start)."""
        try:
            await self.start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

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
