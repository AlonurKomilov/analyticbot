"""Task script for polling real-time updates with feature flag safety."""

import asyncio
import logging
import sys
import signal
from typing import Optional
from datetime import datetime

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.di import get_repositories, create_tg_client
from apps.mtproto.collectors.updates import UpdatesCollector


class UpdatesPoller:
    """Manages the updates polling process with graceful shutdown."""
    
    def __init__(self):
        self.collector: Optional[UpdatesCollector] = None
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def start_polling(self, restart_on_error: bool = True) -> dict:
        """Start polling for real-time updates.
        
        Args:
            restart_on_error: Whether to restart on errors
        
        Returns:
            Dictionary with polling results
        """
        settings = MTProtoSettings()
        
        # Safety check - feature must be enabled
        if not settings.MTPROTO_ENABLED or not settings.MTPROTO_UPDATES_ENABLED:
            logging.warning("Updates polling disabled by feature flags")
            return {
                "success": False,
                "reason": "disabled_by_flags",
                "uptime_seconds": 0,
                "updates_processed": 0
            }
        
        logging.info("Starting updates polling...")
        
        repos = await get_repositories()
        tg_client = create_tg_client(settings)
        
        try:
            # Initialize TG client
            await tg_client.start()
            
            # Create collector
            self.collector = UpdatesCollector(tg_client, repos, settings)
            self.running = True
            
            start_time = datetime.utcnow()
            
            while self.running and not self.shutdown_event.is_set():
                try:
                    logging.info("Starting updates collection...")
                    await self.collector.start_collecting()
                    
                    # If we reach here, collection ended normally
                    if self.running:
                        logging.warning("Updates collection ended unexpectedly")
                        if not restart_on_error:
                            break
                        
                        logging.info("Restarting updates collection in 5 seconds...")
                        try:
                            await asyncio.wait_for(
                                self.shutdown_event.wait(), timeout=5.0
                            )
                            # If we didn't timeout, shutdown was requested
                            break
                        except asyncio.TimeoutError:
                            # Timeout is expected, continue with restart
                            continue
                
                except Exception as e:
                    logging.error(f"Error in updates collection: {e}")
                    
                    if not restart_on_error or not self.running:
                        break
                    
                    logging.info("Restarting after error in 10 seconds...")
                    try:
                        await asyncio.wait_for(
                            self.shutdown_event.wait(), timeout=10.0
                        )
                        # If we didn't timeout, shutdown was requested
                        break
                    except asyncio.TimeoutError:
                        # Timeout is expected, continue with restart
                        continue
            
            # Get final stats
            uptime = (datetime.utcnow() - start_time).total_seconds()
            stats = self.collector.get_stats() if self.collector else {}
            
            logging.info(f"Updates polling stopped. Uptime: {uptime:.1f}s, Stats: {stats}")
            
            return {
                "success": True,
                "uptime_seconds": uptime,
                "updates_processed": stats.get("updates_processed", 0),
                "updates_skipped": stats.get("updates_skipped", 0),
                "updates_errors": stats.get("updates_errors", 0),
                "end_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Fatal error in updates polling: {e}")
            return {
                "success": False,
                "reason": f"fatal_error: {e}",
                "uptime_seconds": 0,
                "updates_processed": 0
            }
        
        finally:
            self.running = False
            try:
                if self.collector:
                    await self.collector.stop_collecting()
                await tg_client.stop()
            except Exception as e:
                logging.warning(f"Error during cleanup: {e}")
    
    async def stop_polling(self) -> None:
        """Stop polling gracefully."""
        if self.running:
            logging.info("Initiating graceful shutdown of updates poller...")
            self.running = False
            self.shutdown_event.set()
            
            if self.collector:
                await self.collector.stop_collecting()


async def poll_updates(restart_on_error: bool = True) -> dict:
    """Standalone function to poll updates.
    
    Args:
        restart_on_error: Whether to restart collection on errors
    
    Returns:
        Dictionary with polling results
    """
    poller = UpdatesPoller()
    
    def signal_handler():
        """Handle shutdown signals."""
        logging.info("Received shutdown signal")
        asyncio.create_task(poller.stop_polling())
    
    # Set up signal handlers
    loop = asyncio.get_running_loop()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        return await poller.start_polling(restart_on_error)
    finally:
        # Clean up signal handlers
        for sig in [signal.SIGTERM, signal.SIGINT]:
            try:
                loop.remove_signal_handler(sig)
            except (ValueError, RuntimeError):
                pass  # Signal handler not registered or event loop closed


async def main():
    """Main entry point for the poll updates task."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    restart_on_error = True
    
    if len(sys.argv) > 1:
        restart_arg = sys.argv[1].lower()
        if restart_arg in ['false', '0', 'no', 'off']:
            restart_on_error = False
        elif restart_arg in ['true', '1', 'yes', 'on']:
            restart_on_error = True
        else:
            logging.error("Invalid restart_on_error argument. Use: true/false, 1/0, yes/no, on/off")
            sys.exit(1)
    
    logging.info(f"Starting updates polling with restart_on_error={restart_on_error}")
    
    # Run the polling
    try:
        result = await poll_updates(restart_on_error=restart_on_error)
        
        if result['success']:
            logging.info(f"Updates polling completed: {result}")
            sys.exit(0)
        else:
            logging.error(f"Updates polling failed: {result}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logging.info("Updates polling interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
