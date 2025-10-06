"""
Task Client Port
================

Protocol interface for submitting background tasks to task queues (Celery, etc.).

This port enables the CORE layer to submit async tasks without depending on
specific implementations (APPS layer or infrastructure).
"""

from abc import abstractmethod
from typing import Any, Protocol


class TaskClientProtocol(Protocol):
    """
    Protocol for submitting and managing background tasks.

    Implementations should handle task queue integration (Celery, RQ, etc.)
    without the CORE layer needing to know the specific implementation.
    """

    @abstractmethod
    def submit_task(self, task_name: str, **task_kwargs: Any) -> str:
        """
        Submit a task to the background queue.

        Args:
            task_name: Name of the task to execute
            **task_kwargs: Keyword arguments to pass to the task

        Returns:
            Task ID for status checking

        Raises:
            TaskSubmissionError: If task submission fails
        """
        ...

    @abstractmethod
    async def submit_task_async(self, task_name: str, **task_kwargs: Any) -> str:
        """
        Submit a task asynchronously to the background queue.

        Args:
            task_name: Name of the task to execute
            **task_kwargs: Keyword arguments to pass to the task

        Returns:
            Task ID for status checking

        Raises:
            TaskSubmissionError: If task submission fails
        """
        ...

    @abstractmethod
    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """
        Get the status of a submitted task.

        Args:
            task_id: Task ID to check

        Returns:
            Dictionary with task status information:
            {
                "task_id": str,
                "status": str,  # "pending", "processing", "completed", "failed"
                "result": Optional[Any],
                "error": Optional[str]
            }
        """
        ...

    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.

        Args:
            task_id: Task ID to cancel

        Returns:
            True if cancelled successfully, False otherwise
        """
        ...


class TaskSubmissionError(Exception):
    """Raised when task submission fails"""

    pass
