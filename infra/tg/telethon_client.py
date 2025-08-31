from __future__ import annotations
from typing import AsyncIterator, Any, Optional


class TelethonTGClient:
    """Stub implementation of Telegram client to keep runtime lean.
    
    This is a placeholder implementation that provides the correct interface
    without importing heavy dependencies like Telethon. The actual Telethon
    integration will be added in later phases when MTProto is enabled.
    
    Note: This implementation should NOT import telethon to avoid runtime
    and installation dependencies when MTProto is disabled.
    """
    
    def __init__(
        self, 
        api_id: Optional[int] = None, 
        api_hash: Optional[str] = None, 
        session_name: str = "stub_session",
        proxy_url: Optional[str] = None
    ):
        """Initialize the stub Telegram client.
        
        Args:
            api_id: Telegram API ID (from my.telegram.org)
            api_hash: Telegram API Hash (from my.telegram.org) 
            session_name: Name for the session file
            proxy_url: Optional proxy URL (e.g., socks5://user:pass@host:port)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.proxy_url = proxy_url
        self._started = False

    async def start(self) -> None:
        """Start the client connection (stub implementation)."""
        self._started = True

    async def stop(self) -> None:
        """Stop the Telegram client."""
        self._running = False
        self.logger.info("Stub TGClient stopped")
    
    async def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._running
    
    async def iter_history(
        self, 
        peer: Any, 
        *, 
        offset_id: int = 0, 
        limit: int = 200
    ) -> AsyncIterator[Any]:
        """Iterate through message history (stub implementation).
        
        Args:
            peer: The target peer
            offset_id: Start from this message ID
            limit: Maximum messages per request
            
        Yields:
            Message objects (currently none in stub)
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        # Keep generator shape but yield nothing in stub
        if False:  # This ensures the function is a generator
            yield None

    async def get_broadcast_stats(self, channel: Any) -> Any:
        """Get broadcast channel statistics (stub implementation).
        
        Args:
            channel: The target channel
            
        Returns:
            Placeholder statistics object
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        return {"_": "stats.BroadcastStats(placeholder)"}

    async def get_megagroup_stats(self, chat: Any) -> Any:
        """Get megagroup statistics (stub implementation).
        
        Args:
            chat: The target megagroup
            
        Returns:
            Placeholder statistics object
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        return {"_": "stats.MegagroupStats(placeholder)"}

    async def load_async_graph(self, token: str) -> Any:
        """Load async graph data (stub implementation).
        
        Args:
            token: Graph data token
            
        Returns:
            Placeholder graph data
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        return {"json": "{}", "token": token}

    async def get_full_channel(self, peer: Any) -> Any:
        """Get full channel information (stub implementation).
        
        Args:
            peer: The target channel
            
        Returns:
            Placeholder channel information
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        return {"full": True, "peer": str(peer)}

    async def iter_updates(self) -> AsyncIterator[Any]:
        """Iterate through real-time updates (stub implementation).
        
        Yields:
            Update objects (currently none in stub)
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        # Keep generator shape but yield nothing in stub
        if False:  # This ensures the function is a generator
            yield None

    async def get_me(self) -> Any:
        """Get current user information (stub implementation).
        
        Returns:
            Placeholder user information
        """
        if not self._started:
            raise RuntimeError("TelethonTGClient not started")
        
        return {"id": 123456789, "username": "stub_user", "is_bot": False}
    
    async def disconnect(self) -> None:
        """Disconnect the client (stub implementation)."""
        await self.stop()
