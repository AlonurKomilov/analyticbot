"""
Dependency Injection for Celery Tasks
====================================

Provides dependency injection for Celery background tasks following Clean Architecture.
Tasks should depend on protocols, not concrete implementations.
"""

import logging

from core.protocols import DeepLearningServiceProtocol
from core.services.deep_learning import DLOrchestratorService

logger = logging.getLogger(__name__)

# Global service instances (cached for performance)
_dl_service: DeepLearningServiceProtocol | None = None


async def get_deep_learning_service() -> DeepLearningServiceProtocol:
    """
    Get deep learning service for Celery tasks

    Uses singleton pattern for performance in background tasks.
    Services are started once and reused across tasks.
    """
    global _dl_service

    if _dl_service is None:
        logger.info("🚀 Initializing Deep Learning service for Celery tasks")

        # Create and start the orchestrator service
        orchestrator = DLOrchestratorService()

        # Start all underlying services
        await orchestrator.start_services()

        _dl_service = orchestrator
        logger.info("✅ Deep Learning service initialized for Celery")

    return _dl_service


def get_deep_learning_service_sync() -> DeepLearningServiceProtocol:
    """
    Synchronous wrapper for getting deep learning service

    For use in synchronous Celery tasks that can't use async/await.
    Uses asyncio.run() to execute the async initialization.
    """
    import asyncio

    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If in async context, can't use asyncio.run()
            # Return cached service or raise error
            if _dl_service is None:
                raise RuntimeError(
                    "Deep Learning service not initialized. Call get_deep_learning_service() first."
                )
            return _dl_service
        else:
            # Not in async context, safe to use asyncio.run()
            return asyncio.run(get_deep_learning_service())
    except RuntimeError:
        # No event loop, safe to use asyncio.run()
        return asyncio.run(get_deep_learning_service())


async def cleanup_celery_services():
    """
    Cleanup services when Celery worker shuts down
    """
    global _dl_service

    if _dl_service is not None:
        logger.info("🛑 Cleaning up Celery services")

        # Try to stop the orchestrator service if it has the method
        try:
            # Cast to concrete type for cleanup (implementation detail)
            from core.services.deep_learning import DLOrchestratorService

            if isinstance(_dl_service, DLOrchestratorService):
                await _dl_service.stop_services()
            else:
                logger.info("Service is not DLOrchestratorService, skipping stop_services")
        except Exception as e:
            logger.warning(f"Error stopping services: {e}")

        _dl_service = None
        logger.info("✅ Celery services cleaned up")


def cleanup_celery_services_sync():
    """
    Synchronous wrapper for cleanup
    """
    import asyncio

    try:
        asyncio.run(cleanup_celery_services())
    except Exception as e:
        logger.warning(f"Error during Celery service cleanup: {e}")


def run_async_in_sync(coro):
    """
    Helper to run async coroutines in synchronous Celery tasks

    Args:
        coro: Async coroutine to execute

    Returns:
        Result of the coroutine
    """
    import asyncio

    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # In async context - this shouldn't happen in Celery tasks
            # but handle gracefully
            raise RuntimeError(
                "Cannot run async coroutine in already running event loop. "
                "Celery tasks should be synchronous."
            )
        else:
            # Not in async context, safe to use asyncio.run()
            return asyncio.run(coro)
    except RuntimeError:
        # No event loop, safe to use asyncio.run()
        return asyncio.run(coro)
