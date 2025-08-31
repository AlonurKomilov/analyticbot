from __future__ import annotations
from typing import Protocol, AsyncIterator, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class MessageData:
    """Data class representing a Telegram message."""
    
    message_id: int
    text: str
    date: datetime
    sender_id: int
    peer_id: int
    views: int = 0
    forwards: int = 0
    replies: int = 0


@dataclass
class UpdateData:
    """Data class representing a Telegram update/event."""
    
    update_id: int
    type: str
    data: dict
    timestamp: datetime


@dataclass
class BroadcastStats:
    """Data class representing channel broadcast statistics."""
    
    channel_id: int
    subscriber_count: int
    view_count_avg: float
    share_count_avg: float
    reaction_count_avg: float
    growth_rate: float
    engagement_rate: float


class TGClient(Protocol):
    """Protocol defining the interface for Telegram client implementations.
    
    This protocol abstracts away the specific MTProto client implementation
    (Telethon, Pyrogram, etc.) and provides a clean interface for core business logic.
    """
    
    async def start(self) -> None:
        """Initialize and start the Telegram client connection."""
        ...
    
    async def stop(self) -> None:
        """Stop and cleanup the Telegram client connection."""
        ...
    
    async def is_connected(self) -> bool:
        """Check if client is connected to Telegram.
        
        Returns:
            True if connected, False otherwise
        """
        ...
    
    async def iter_history(self, peer: Any, *, offset_id: int = 0, limit: int = 200) -> AsyncIterator[Any]:
        """Iterate through message history for a given peer (channel, chat, user).
        
        Args:
            peer: The target peer (channel, chat, or user)
            offset_id: Start from this message ID (0 = most recent)
            limit: Maximum number of messages to retrieve per request
            
        Yields:
            Message objects from the peer's history
        """
        ...
    
    async def get_broadcast_stats(self, channel: Any) -> Any:
        """Retrieve broadcast statistics for a channel.
        
        Args:
            channel: The target channel
            
        Returns:
            Statistics object containing channel analytics data
        """
        ...
    
    async def get_megagroup_stats(self, chat: Any) -> Any:
        """Retrieve megagroup statistics for a chat.
        
        Args:
            chat: The target megagroup/supergroup
            
        Returns:
            Statistics object containing chat analytics data
        """
        ...
    
    async def load_async_graph(self, token: str) -> Any:
        """Load asynchronous statistics graph data using a token.
        
        Args:
            token: Graph data token from previous statistics request
            
        Returns:
            Graph data object with chart information
        """
        ...
    
    async def get_full_channel(self, peer: Any) -> Any:
        """Get full channel information including metadata.
        
        Args:
            peer: The target channel
            
        Returns:
            Full channel object with detailed information
        """
        ...
    
    async def iter_updates(self) -> AsyncIterator[UpdateData]:
        """Iterate through real-time updates from Telegram.
        
        Yields:
            UpdateData objects representing Telegram updates
        """
        ...
    
    async def get_me(self) -> Any:
        """Get information about the current user/bot.
        
        Returns:
            User information object
        """
        ...
    
    async def disconnect(self) -> None:
        """Disconnect the Telegram client (cleanup method)."""
        ...
