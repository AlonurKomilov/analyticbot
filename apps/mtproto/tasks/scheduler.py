"""Task scheduler for MTProto operations."""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass

from apps.mtproto.di import get_settings


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
    name: str
    func: Callable[..., Awaitable[Any]]
    interval_seconds: int
    next_run: datetime
    args: tuple = ()
    kwargs: dict = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


class TaskScheduler:
    """Simple task scheduler for MTProto operations.
    
    This is a stub implementation that will be extended in future phases
    with more sophisticated scheduling capabilities and integration with
    external schedulers like Celery or APScheduler.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def initialize(self) -> None:
        """Initialize the task scheduler."""
        settings = get_settings()
        
        if not settings.MTPROTO_ENABLED:
            self.logger.info("TaskScheduler disabled (MTPROTO_ENABLED=False)")
            return
        
        self.logger.info("TaskScheduler initialized")
    
    def schedule_task(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        interval_seconds: int,
        *args,
        **kwargs
    ) -> None:
        """Schedule a task to run at regular intervals.
        
        Args:
            name: Unique name for the task
            func: Async function to execute
            interval_seconds: Interval between executions in seconds
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        if name in self._tasks:
            self.logger.warning(f"Task {name} already scheduled, replacing...")
        
        next_run = datetime.now() + timedelta(seconds=interval_seconds)
        
        task = ScheduledTask(
            name=name,
            func=func,
            interval_seconds=interval_seconds,
            next_run=next_run,
            args=args,
            kwargs=kwargs
        )
        
        self._tasks[name] = task
        self.logger.info(f"Scheduled task {name} to run every {interval_seconds} seconds")
    
    def unschedule_task(self, name: str) -> bool:
        """Remove a scheduled task.
        
        Args:
            name: Name of the task to remove
            
        Returns:
            True if task was removed, False if not found
        """
        if name in self._tasks:
            del self._tasks[name]
            self.logger.info(f"Unscheduled task {name}")
            return True
        else:
            self.logger.warning(f"Task {name} not found")
            return False
    
    async def start(self) -> None:
        """Start the task scheduler."""
        if self._running:
            self.logger.warning("TaskScheduler already running")
            return
        
        self._running = True
        self.logger.info("Starting task scheduler...")
        
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
    
    async def stop(self) -> None:
        """Stop the task scheduler."""
        if not self._running:
            return
        
        self._running = False
        self.logger.info("Stopping task scheduler...")
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Task scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self._running:
            try:
                now = datetime.now()
                
                # Check which tasks need to run
                for task_name, task in self._tasks.items():
                    if now >= task.next_run:
                        self.logger.debug(f"Executing scheduled task: {task_name}")
                        
                        try:
                            # Execute the task
                            await task.func(*task.args, **task.kwargs)
                            
                            # Schedule next run
                            task.next_run = now + timedelta(seconds=task.interval_seconds)
                            
                        except Exception as e:
                            self.logger.error(f"Error executing task {task_name}: {e}")
                            # Still schedule next run despite error
                            task.next_run = now + timedelta(seconds=task.interval_seconds)
                
                # Sleep for a short interval before checking again
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5)  # Longer sleep on error
    
    def get_scheduled_tasks(self) -> Dict[str, dict]:
        """Get information about all scheduled tasks.
        
        Returns:
            Dictionary with task information
        """
        result = {}
        for name, task in self._tasks.items():
            result[name] = {
                "name": task.name,
                "interval_seconds": task.interval_seconds,
                "next_run": task.next_run.isoformat(),
                "function": task.func.__name__
            }
        return result
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running
