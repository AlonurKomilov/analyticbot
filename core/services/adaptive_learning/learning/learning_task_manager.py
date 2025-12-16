"""
Learning Task Manager
====================

Clean coordinator for learning task lifecycle management.
Refactored from 815-line god object into focused coordination layer.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.services.adaptive_learning.protocols.learning_protocols import (
    LearningProgress,
    LearningStrategy,
)

from .progress_tracker import ProgressConfig, ProgressTracker
from .task_creator import TaskCreationConfig, TaskCreator
from .task_scheduler import SchedulingConfig, TaskPriority, TaskScheduler

logger = logging.getLogger(__name__)


@dataclass
class LearningTaskManagerConfig:
    """Configuration for learning task manager"""

    max_concurrent_tasks: int = 3
    task_timeout_minutes: int = 60
    enable_auto_cleanup: bool = True
    cleanup_interval_hours: int = 24


class LearningTaskManager:
    """
    Clean coordinator for learning task lifecycle management.

    Orchestrates specialized components rather than handling everything directly:
    - TaskCreator: Handles task creation and validation
    - TaskScheduler: Manages scheduling and worker assignment
    - ProgressTracker: Monitors progress and execution context
    """

    def __init__(
        self,
        config: LearningTaskManagerConfig | None = None,
        task_creator_config: TaskCreationConfig | None = None,
        scheduler_config: SchedulingConfig | None = None,
        progress_config: ProgressConfig | None = None,
    ):
        self.config = config or LearningTaskManagerConfig()

        # Initialize specialized components
        self.task_creator = TaskCreator(task_creator_config)
        self.task_scheduler = TaskScheduler(scheduler_config)
        self.progress_tracker = ProgressTracker(progress_config)

        # Manager state
        self.is_running = False
        self.manager_stats = {
            "started_at": None,
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
        }

        logger.info("🎯 Learning Task Manager initialized with specialized components")

    async def start_manager(self) -> bool:
        """Start the task manager and all components"""
        try:
            if self.is_running:
                logger.warning("⚠️ Learning Task Manager already running")
                return True

            # Start all components
            creator_started = await self.task_creator.start_creation_service()
            scheduler_started = await self.task_scheduler.start_scheduler()
            tracker_started = await self.progress_tracker.start_tracking()

            if not all([creator_started, scheduler_started, tracker_started]):
                logger.error("❌ Failed to start one or more components")
                return False

            self.is_running = True
            self.manager_stats["started_at"] = datetime.utcnow().isoformat()

            logger.info("✅ Learning Task Manager started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Learning Task Manager: {e}")
            return False

    async def stop_manager(self) -> bool:
        """Stop the task manager and all components"""
        try:
            if not self.is_running:
                logger.warning("⚠️ Learning Task Manager already stopped")
                return True

            # Stop all components
            await self.task_creator.stop_creation_service()
            await self.task_scheduler.stop_scheduler()
            await self.progress_tracker.stop_tracking()

            self.is_running = False

            logger.info("⏹️ Learning Task Manager stopped successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop Learning Task Manager: {e}")
            return False

    async def create_learning_task(
        self,
        model_id: str,
        strategy: LearningStrategy,
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]] | None = None,
        task_parameters: dict[str, Any] | None = None,
        priority: str = "normal",
    ) -> str | None:
        """Create a new learning task using TaskCreator"""
        try:
            self.manager_stats["total_operations"] += 1

            # Delegate to TaskCreator
            task_config = {
                "training_data": training_data,
                "validation_data": validation_data,
            }
            if task_parameters:
                task_config.update(task_parameters)

            task = await self.task_creator.create_task(
                model_id=model_id,
                learning_strategy=strategy,
                task_config=task_config,
                priority=str(priority),
            )

            if task:
                # Schedule the task
                task_priority = (
                    priority if isinstance(priority, TaskPriority) else TaskPriority.NORMAL
                )
                scheduled = await self.task_scheduler.schedule_task(
                    task=task, priority=task_priority
                )

                if scheduled:
                    # Start tracking
                    await self.progress_tracker.start_task_tracking(task.task_id)
                    self.manager_stats["successful_operations"] += 1
                    logger.info(f"✅ Created and scheduled learning task {task.task_id}")
                    return task.task_id
                else:
                    logger.error(f"❌ Failed to schedule task {task.task_id}")
                    self.manager_stats["failed_operations"] += 1
                    return None
            else:
                logger.error("❌ Failed to create task")
                self.manager_stats["failed_operations"] += 1
                return None

        except Exception as e:
            logger.error(f"❌ Failed to create learning task: {e}")
            self.manager_stats["failed_operations"] += 1
            return None

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get comprehensive task status from all components"""
        try:
            # Get task info from creator
            task_info = await self.task_creator.get_task_info(task_id)

            # Get scheduling info from scheduler
            schedule_info = await self.task_scheduler.get_task_status(task_id)

            # Get progress info from tracker
            progress_info = await self.progress_tracker.get_task_progress(task_id)

            if not task_info:
                return None

            # Combine all information
            status = {
                "task_id": task_id,
                "task_info": task_info,
                "schedule_info": schedule_info or {},
                "progress_info": progress_info or {},
                "manager_timestamp": datetime.utcnow().isoformat(),
            }

            return status

        except Exception as e:
            logger.error(f"❌ Failed to get task status: {e}")
            return None

    async def update_task_progress(
        self,
        task_id: str,
        progress_percent: float,
        current_phase: str = "",
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Update task progress via ProgressTracker"""
        try:
            return await self.progress_tracker.update_progress(
                task_id=task_id,
                progress_percent=progress_percent,
                current_phase=current_phase,
                details=details,
            )

        except Exception as e:
            logger.error(f"❌ Failed to update task progress: {e}")
            return False

    async def cancel_task(self, task_id: str, reason: str = "") -> bool:
        """Cancel a task across all components"""
        try:
            self.manager_stats["total_operations"] += 1

            # Cancel in scheduler
            scheduler_cancelled = await self.task_scheduler.cancel_task(task_id)

            # Mark as failed in progress tracker
            tracker_updated = await self.progress_tracker.fail_task_tracking(
                task_id=task_id, error_details={"cancellation_reason": reason}
            )

            if scheduler_cancelled or tracker_updated:
                self.manager_stats["successful_operations"] += 1
                logger.info(f"✅ Cancelled task {task_id}: {reason}")
                return True
            else:
                self.manager_stats["failed_operations"] += 1
                logger.error(f"❌ Failed to cancel task {task_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to cancel task: {e}")
            self.manager_stats["failed_operations"] += 1
            return False

    async def complete_task(
        self, task_id: str, final_results: dict[str, Any] | None = None
    ) -> bool:
        """Complete a task across all components"""
        try:
            self.manager_stats["total_operations"] += 1

            # Complete in scheduler
            scheduler_completed = await self.task_scheduler.complete_task(task_id)

            # Complete in progress tracker
            tracker_completed = await self.progress_tracker.complete_task_tracking(
                task_id=task_id, final_results=final_results
            )

            if scheduler_completed and tracker_completed:
                self.manager_stats["successful_operations"] += 1
                logger.info(f"✅ Completed task {task_id}")
                return True
            else:
                self.manager_stats["failed_operations"] += 1
                logger.error(f"❌ Failed to complete task {task_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to complete task: {e}")
            self.manager_stats["failed_operations"] += 1
            return False

    async def get_active_tasks(self) -> list[dict[str, Any]]:
        """Get all active tasks from all components"""
        try:
            # Get active tasks from progress tracker
            progress_tasks = await self.progress_tracker.get_active_tasks()

            # Get scheduling info for each task
            active_tasks = []
            for progress_info in progress_tasks:
                task_id = progress_info.get("task_id")
                if task_id:
                    # Get additional info from other components
                    task_info = await self.task_creator.get_task_info(task_id)
                    schedule_info = await self.task_scheduler.get_task_status(task_id)

                    combined_info = {
                        "task_id": task_id,
                        "progress": progress_info,
                        "task_info": task_info or {},
                        "schedule_info": schedule_info or {},
                    }
                    active_tasks.append(combined_info)

            return active_tasks

        except Exception as e:
            logger.error(f"❌ Failed to get active tasks: {e}")
            return []

    async def get_manager_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics from all components"""
        try:
            # Get statistics from all components
            creator_stats = await self.task_creator.get_creation_statistics()
            scheduler_stats = await self.task_scheduler.get_scheduler_statistics()
            tracker_stats = await self.progress_tracker.get_tracking_statistics()

            # Combine with manager stats
            combined_stats = {
                "manager": {
                    "service": "learning_task_manager",
                    "is_running": self.is_running,
                    "statistics": self.manager_stats,
                    "config": {
                        "max_concurrent_tasks": self.config.max_concurrent_tasks,
                        "task_timeout_minutes": self.config.task_timeout_minutes,
                        "enable_auto_cleanup": self.config.enable_auto_cleanup,
                        "cleanup_interval_hours": self.config.cleanup_interval_hours,
                    },
                },
                "components": {
                    "task_creator": creator_stats,
                    "task_scheduler": scheduler_stats,
                    "progress_tracker": tracker_stats,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            return combined_stats

        except Exception as e:
            logger.error(f"❌ Failed to get manager statistics: {e}")
            return {"error": str(e)}

    async def register_worker(self, worker_id: str, capabilities: dict[str, Any]) -> bool:
        """Register a worker for task execution"""
        try:
            # Default resource capacity if not provided
            resource_capacity = capabilities.get(
                "resource_capacity", {"cpu_cores": 1, "memory_gb": 2, "gpu_count": 0}
            )
            return await self.task_scheduler.register_worker(
                worker_id, capabilities, resource_capacity
            )

        except Exception as e:
            logger.error(f"❌ Failed to register worker: {e}")
            return False

    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker"""
        try:
            return await self.task_scheduler.unregister_worker(worker_id)

        except Exception as e:
            logger.error(f"❌ Failed to unregister worker: {e}")
            return False

    async def worker_heartbeat(self, worker_id: str, status: dict[str, Any]) -> bool:
        """Update worker heartbeat"""
        try:
            return await self.task_scheduler.worker_heartbeat(worker_id)

        except Exception as e:
            logger.error(f"❌ Failed to update worker heartbeat: {e}")
            return False

    async def get_learning_progress_history(
        self, task_id: str, limit: int = 50
    ) -> list[LearningProgress]:
        """Get learning progress history for a task"""
        try:
            return await self.progress_tracker.get_learning_progress_history(task_id, limit)

        except Exception as e:
            logger.error(f"❌ Failed to get learning progress history: {e}")
            return []

    async def health_check(self) -> dict[str, Any]:
        """Comprehensive health check across all components"""
        try:
            # Check component health
            creator_healthy = await self.task_creator.health_check()
            scheduler_healthy = await self.task_scheduler.health_check()
            tracker_healthy = await self.progress_tracker.get_tracking_statistics()

            # Overall health
            all_healthy = creator_healthy and scheduler_healthy and "error" not in tracker_healthy

            health_status = {
                "service": "learning_task_manager",
                "status": "healthy" if all_healthy else "degraded",
                "is_running": self.is_running,
                "components": {
                    "task_creator": creator_healthy,
                    "task_scheduler": scheduler_healthy,
                    "progress_tracker": {
                        "status": ("healthy" if "error" not in tracker_healthy else "unhealthy")
                    },
                },
                "manager_stats": self.manager_stats,
                "timestamp": datetime.utcnow().isoformat(),
            }

            return health_status

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "service": "learning_task_manager",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def create_task(
        self,
        model_id: str,
        strategy: LearningStrategy,
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]] | None = None,
        priority: Any | None = None,
        dependencies: list[str] | None = None,
        task_parameters: dict[str, Any] | None = None,
    ) -> str | None:
        """Create a learning task"""
        try:
            # Generate task ID
            task_id = f"task_{model_id}_{int(datetime.utcnow().timestamp())}"

            # Store task info for later retrieval
            task_info = {
                "task_id": task_id,
                "model_id": model_id,
                "strategy": strategy,
                "training_data": training_data,
                "validation_data": validation_data,
                "priority": priority,
                "dependencies": dependencies,
                "parameters": task_parameters or {},
                "created_at": datetime.utcnow(),
                "status": "pending",
            }

            # In a real implementation, this would be stored properly
            logger.info(f"Created learning task {task_id} for model {model_id}")
            return task_id

        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            return None

    async def get_pending_tasks(self, model_id: str | None = None) -> list[dict[str, Any]]:
        """Get pending learning tasks"""
        try:
            # Get pending tasks from scheduler
            pending_tasks = []

            # This would typically query a task database
            # For now, return empty list as a placeholder
            logger.info(f"Getting pending tasks for model: {model_id or 'all'}")

            return pending_tasks

        except Exception as e:
            logger.error(f"❌ Failed to get pending tasks: {e}")
            return []

    async def get_task_statistics(self, model_id: str | None = None) -> dict[str, Any]:
        """Get task statistics"""
        try:
            # Get statistics from components
            manager_stats = await self.get_manager_statistics()

            # Filter by model_id if specified
            if model_id:
                # In a real implementation, this would filter by model
                logger.info(f"Getting task statistics for model: {model_id}")

            return {
                "total_tasks": manager_stats.get("manager", {})
                .get("statistics", {})
                .get("total_operations", 0),
                "successful_tasks": manager_stats.get("manager", {})
                .get("statistics", {})
                .get("successful_operations", 0),
                "failed_tasks": manager_stats.get("manager", {})
                .get("statistics", {})
                .get("failed_operations", 0),
                "model_id": model_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get task statistics: {e}")
            return {}

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status synchronously"""
        try:
            return {
                "service": "learning_task_manager",
                "status": "healthy" if self.is_running else "stopped",
                "is_running": self.is_running,
                "manager_stats": self.manager_stats,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get service health: {e}")
            return {
                "service": "learning_task_manager",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
