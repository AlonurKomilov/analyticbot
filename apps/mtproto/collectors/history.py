"""History data collector for Telegram channels/chats."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from apps.mtproto.di import get_tg_client, get_settings
from core.ports.tg_client import TGClient, MessageData


class HistoryCollector:
    """Collects message history from Telegram channels/chats.
    
    This is a stub implementation that will be extended in future phases
    with actual data collection and processing capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tg_client: Optional[TGClient] = None
    
    async def initialize(self) -> None:
        """Initialize the history collector."""
        settings = get_settings()
        
        if not settings.MTPROTO_ENABLED:
            self.logger.info("HistoryCollector disabled (MTPROTO_ENABLED=False)")
            return
        
        self._tg_client = get_tg_client()
        await self._tg_client.start()
        self.logger.info("HistoryCollector initialized")
    
    async def collect_channel_history(
        self,
        channel_username: str,
        limit: int = 100,
        offset_date: Optional[datetime] = None
    ) -> List[MessageData]:
        """Collect message history from a Telegram channel.
        
        Args:
            channel_username: Username or ID of the channel
            limit: Maximum number of messages to collect
            offset_date: Start collecting from this date
            
        Returns:
            List of message data
        """
        if not self._tg_client:
            self.logger.warning("TGClient not initialized")
            return []
        
        self.logger.info(
            f"Collecting history from channel {channel_username} "
            f"(limit: {limit}, offset_date: {offset_date})"
        )
        
        try:
            messages = []
            async for message in self._tg_client.iter_history(
                channel_username, 
                limit=limit, 
                offset_date=offset_date
            ):
                messages.append(message)
            
            self.logger.info(f"Collected {len(messages)} messages from {channel_username}")
            return messages
            
        except Exception as e:
            self.logger.error(f"Failed to collect history from {channel_username}: {e}")
            return []
    
    async def collect_batch_history(
        self,
        channels: List[str],
        limit_per_channel: int = 100
    ) -> Dict[str, List[MessageData]]:
        """Collect history from multiple channels in batch.
        
        Args:
            channels: List of channel usernames/IDs
            limit_per_channel: Message limit per channel
            
        Returns:
            Dictionary mapping channel names to their message lists
        """
        results = {}
        
        for channel in channels:
            try:
                messages = await self.collect_channel_history(
                    channel, 
                    limit=limit_per_channel
                )
                results[channel] = messages
            except Exception as e:
                self.logger.error(f"Failed to collect from {channel}: {e}")
                results[channel] = []
        
        return results
    
    async def shutdown(self) -> None:
        """Shutdown the history collector."""
        if self._tg_client:
            await self._tg_client.stop()
            self.logger.info("HistoryCollector shutdown complete")
