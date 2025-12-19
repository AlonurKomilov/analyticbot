"""
Clean Task Utilities

Framework-agnostic task utilities that don't directly import infrastructure.
Uses dependency injection to get the necessary components.
"""

import asyncio
import functools
import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


class TaskRetryConfig:
    """Configuration for task retry behavior"""

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: int = 60,
        exponential_backoff: bool = True,
        max_retry_delay: int = 3600,
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        self.max_retry_delay = max_retry_delay


def create_retry_decorator(config: TaskRetryConfig):
    """
    Create a retry decorator with the specified configuration.

    This is framework-agnostic and can be adapted to any task system.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_retries:
                        logger.error(
                            f"Task {func.__name__} failed after {config.max_retries} retries. "
                            f"Last error: {e}"
                        )
                        raise

                    # Calculate delay
                    delay = config.retry_delay
                    if config.exponential_backoff:
                        delay = min(config.retry_delay * (2**attempt), config.max_retry_delay)

                    logger.warning(
                        f"Task {func.__name__} failed on attempt {attempt + 1}. "
                        f"Retrying in {delay} seconds. Error: {e}"
                    )

                    # In a real implementation, this would integrate with the task system
                    # For now, we'll just log the retry intent
                    await asyncio.sleep(1)  # Minimal delay for immediate retry

            # This should never be reached
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Task failed without exception details")

        return wrapper

    return decorator


# Default retry configuration
default_retry_config = TaskRetryConfig(
    max_retries=3, retry_delay=60, exponential_backoff=True, max_retry_delay=3600
)

# Default retry decorator
enhanced_retry_task = create_retry_decorator(default_retry_config)


class TaskExecutor:
    """Clean task executor that uses dependency injection"""

    def __init__(self, container=None):
        self.container = container

    async def execute_with_dependencies(self, task_func: Callable, *args, **kwargs):
        """Execute a task with proper dependency injection"""
        if self.container:
            # Inject dependencies from container
            # This would be implemented based on your DI framework
            pass

        return await task_func(*args, **kwargs)

    def create_task_wrapper(self, task_func: Callable):
        """Create a wrapper that handles DI and error handling"""

        @functools.wraps(task_func)
        async def wrapper(*args, **kwargs):
            try:
                return await self.execute_with_dependencies(task_func, *args, **kwargs)
            except Exception as e:
                logger.error(f"Task {task_func.__name__} failed: {e}")
                raise

        return wrapper
