"""Real-time updates collector for Telegram."""

import logging
import asyncio
from typing import Optional, Callable, Any

from apps.mtproto.di import get_tg_client, get_settings
from core.ports.tg_client import TGClient, UpdateData


class UpdatesCollector:
    """Collects real-time updates from Telegram.
    
    This is a stub implementation that will be extended in future phases
    with actual update handling and processing capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tg_client: Optional[TGClient] = None
        self._running = False
        self._update_handler: Optional[Callable[[UpdateData], None]] = None
    
    async def initialize(self) -> None:
        """Initialize the updates collector."""
        settings = get_settings()
        
        if not settings.MTPROTO_ENABLED:
            self.logger.info("UpdatesCollector disabled (MTPROTO_ENABLED=False)")
            return
        
        self._tg_client = get_tg_client()
        await self._tg_client.start()
        self.logger.info("UpdatesCollector initialized")
    
    def set_update_handler(self, handler: Callable[[UpdateData], None]) -> None:
        """Set handler for processing updates.
        
        Args:
            handler: Function to handle incoming updates
        """
        self._update_handler = handler
        self.logger.info("Update handler registered")
    
    async def start_collecting(self) -> None:
        """Start collecting real-time updates."""
        if not self._tg_client:
            self.logger.warning("TGClient not initialized")
            return
        
        if self._running:
            self.logger.warning("UpdatesCollector already running")
            return
        
        self._running = True
        self.logger.info("Starting updates collection...")
        
        try:
            async for update in self._tg_client.iter_updates():
                if not self._running:
                    break
                
                self.logger.debug(f"Received update: {update.type}")
                
                if self._update_handler:
                    try:
                        self._update_handler(update)
                    except Exception as e:
                        self.logger.error(f"Error in update handler: {e}")
                
        except Exception as e:
            self.logger.error(f"Error in updates collection: {e}")
        finally:
            self._running = False
            self.logger.info("Updates collection stopped")
    
    async def stop_collecting(self) -> None:
        """Stop collecting updates."""
        if self._running:
            self._running = False
            self.logger.info("Stopping updates collection...")
            
            # Give some time for the collection loop to stop
            await asyncio.sleep(1)
    
    def is_collecting(self) -> bool:
        """Check if collector is currently running."""
        return self._running
    
    async def shutdown(self) -> None:
        """Shutdown the updates collector."""
        await self.stop_collecting()
        
        if self._tg_client:
            await self._tg_client.stop()
            self.logger.info("UpdatesCollector shutdown complete")
