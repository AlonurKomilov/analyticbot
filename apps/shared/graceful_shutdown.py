#!/usr/bin/env python3
"""
Graceful Shutdown Handler for MTProto Worker

Adds signal handlers to ensure clean process termination and prevent orphaned workers.
"""

import atexit
import logging
import multiprocessing
import signal
import sys
import time

logger = logging.getLogger(__name__)


class GracefulShutdownHandler:
    """
    Handles graceful shutdown of multiprocessing workers.

    Ensures:
    - All child processes are terminated
    - Database connections are closed
    - Telethon sessions are saved
    - Resources are cleaned up
    """

    def __init__(self):
        self.shutdown_in_progress = False
        self.child_processes: list = []
        self.cleanup_callbacks: list = []

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)

        # Register atexit handler
        atexit.register(self._cleanup_on_exit)

    def register_child_process(self, process: multiprocessing.Process):
        """Register a child process for cleanup"""
        self.child_processes.append(process)

    def register_cleanup_callback(self, callback):
        """Register a cleanup function to call on shutdown"""
        self.cleanup_callbacks.append(callback)

    def _handle_shutdown_signal(self, signum, frame):
        """Handle SIGTERM/SIGINT signals"""
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        logger.info(f"🛑 Received {signal_name}, initiating graceful shutdown...")

        if self.shutdown_in_progress:
            logger.warning("⚠️  Shutdown already in progress, ignoring signal")
            return

        self.shutdown_in_progress = True
        self._perform_cleanup()

        logger.info("✅ Graceful shutdown complete")
        sys.exit(0)

    def _cleanup_on_exit(self):
        """Cleanup function called by atexit"""
        if not self.shutdown_in_progress:
            logger.info("🧹 Performing exit cleanup...")
            self._perform_cleanup()

    def _perform_cleanup(self):
        """Execute all cleanup operations"""
        # 1. Execute custom cleanup callbacks
        logger.info(f"Running {len(self.cleanup_callbacks)} cleanup callbacks...")
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Cleanup callback failed: {e}")

        # 2. Terminate child processes
        if self.child_processes:
            logger.info(f"Terminating {len(self.child_processes)} child processes...")
            for process in self.child_processes:
                if process.is_alive():
                    logger.info(f"  Terminating PID {process.pid}")
                    process.terminate()

            # Wait for processes to terminate (max 5 seconds)
            timeout = 5
            start_time = time.time()
            while time.time() - start_time < timeout:
                alive = [p for p in self.child_processes if p.is_alive()]
                if not alive:
                    break
                time.sleep(0.1)

            # Force kill any remaining processes
            for process in self.child_processes:
                if process.is_alive():
                    logger.warning(f"  Force killing PID {process.pid}")
                    process.kill()

        logger.info("✅ Cleanup complete")


# Global shutdown handler instance
_shutdown_handler: GracefulShutdownHandler | None = None


def get_shutdown_handler() -> GracefulShutdownHandler:
    """Get or create the global shutdown handler"""
    global _shutdown_handler
    if _shutdown_handler is None:
        _shutdown_handler = GracefulShutdownHandler()
    return _shutdown_handler


def register_process_for_cleanup(process: multiprocessing.Process):
    """Register a child process for automatic cleanup on shutdown"""
    handler = get_shutdown_handler()
    handler.register_child_process(process)


def register_cleanup_callback(callback):
    """Register a cleanup function to be called on shutdown"""
    handler = get_shutdown_handler()
    handler.register_cleanup_callback(callback)


# Example usage in MTProto worker:
"""
from apps.shared.graceful_shutdown import get_shutdown_handler, register_cleanup_callback

# Initialize shutdown handler
shutdown_handler = get_shutdown_handler()

# Register cleanup callbacks
def cleanup_telethon_session():
    logger.info("Closing Telethon session...")
    # session.close()

def cleanup_database_connections():
    logger.info("Closing database connections...")
    # await pool.close()

register_cleanup_callback(cleanup_telethon_session)
register_cleanup_callback(cleanup_database_connections)

# When creating multiprocessing workers:
from multiprocessing import Process
worker = Process(target=my_task)
register_process_for_cleanup(worker)
worker.start()
"""
