"""
Progress Tracker
===============

Handles learning task progress monitoring and execution context management.
Extracted from LearningTaskManager god object to focus on progress tracking concerns.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..protocols.learning_protocols import LearningProgress

logger = logging.getLogger(__name__)


@dataclass
class TaskExecutionContext:
    """Task execution context and state"""

    task_id: str
    worker_id: str | None
    started_at: datetime
    last_heartbeat: datetime
    progress_percent: float
    current_phase: str
    resource_usage: dict[str, Any]
    intermediate_results: dict[str, Any]
    status_updates: list[dict[str, Any]]

    def __post_init__(self):
        if not self.status_updates:
            self.status_updates = []


@dataclass
class ProgressConfig:
    """Configuration for progress tracking"""

    heartbeat_interval_seconds: int = 30
    stale_threshold_minutes: int = 10
    progress_report_interval: int = 5  # Every 5% progress
    max_status_updates: int = 100
    enable_resource_monitoring: bool = True


class ProgressTracker:
    """
    Handles task progress monitoring and execution context management.

    Focuses solely on:
    - Progress monitoring and reporting
    - Execution context management
    - Status updates and heartbeats
    - Resource usage tracking
    """

    def __init__(self, config: ProgressConfig | None = None):
        self.config = config or ProgressConfig()

        # Execution contexts
        self.active_contexts: dict[str, TaskExecutionContext] = {}
        self.completed_contexts: dict[str, TaskExecutionContext] = {}

        # Progress tracking
        self.progress_history: dict[str, list[LearningProgress]] = {}
        self.last_progress_report: dict[str, float] = {}

        # Monitoring
        self.is_monitoring = False
        self.monitor_task: asyncio.Task | None = None

        # Statistics
        self.tracking_stats = {
            "total_tracked": 0,
            "active_tasks": 0,
            "avg_progress_rate": 0.0,
            "stale_tasks": 0,
        }

        logger.info("📊 Progress Tracker initialized")

    async def start_tracking(self) -> bool:
        """Start progress tracking and monitoring"""
        try:
            if self.is_monitoring:
                logger.warning("⚠️ Progress tracking already running")
                return True

            # Start monitoring loop
            self.monitor_task = asyncio.create_task(self._monitoring_loop())
            self.is_monitoring = True

            logger.info("✅ Progress tracking started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start progress tracking: {e}")
            return False

    async def stop_tracking(self) -> bool:
        """Stop progress tracking and monitoring"""
        try:
            self.is_monitoring = False

            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass

            logger.info("⏹️ Progress tracking stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop progress tracking: {e}")
            return False

    async def start_task_tracking(self, task_id: str, worker_id: str | None = None) -> bool:
        """Start tracking a task's execution"""
        try:
            if task_id in self.active_contexts:
                logger.warning(f"⚠️ Task {task_id} already being tracked")
                return True

            # Create execution context
            context = TaskExecutionContext(
                task_id=task_id,
                worker_id=worker_id,
                started_at=datetime.utcnow(),
                last_heartbeat=datetime.utcnow(),
                progress_percent=0.0,
                current_phase="initializing",
                resource_usage={},
                intermediate_results={},
                status_updates=[],
            )

            self.active_contexts[task_id] = context
            self.progress_history[task_id] = []
            self.last_progress_report[task_id] = 0.0

            self.tracking_stats["total_tracked"] += 1
            self.tracking_stats["active_tasks"] = len(self.active_contexts)

            logger.info(f"📊 Started tracking task {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start task tracking: {e}")
            return False

    async def update_progress(
        self,
        task_id: str,
        progress_percent: float,
        current_phase: str = "",
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Update task progress"""
        try:
            if task_id not in self.active_contexts:
                logger.error(f"❌ Task {task_id} not being tracked")
                return False

            context = self.active_contexts[task_id]

            # Update progress
            context.progress_percent = min(100.0, max(0.0, progress_percent))
            context.last_heartbeat = datetime.utcnow()

            if current_phase:
                context.current_phase = current_phase

            # Add status update
            status_update = {
                "timestamp": datetime.utcnow().isoformat(),
                "progress_percent": progress_percent,
                "phase": context.current_phase,
                "details": details or {},
            }

            context.status_updates.append(status_update)

            # Limit status updates history
            if len(context.status_updates) > self.config.max_status_updates:
                context.status_updates = context.status_updates[-self.config.max_status_updates :]

            # Create learning progress record
            await self._record_learning_progress(task_id, context, details)

            # Report significant progress changes
            await self._check_progress_reporting(task_id, progress_percent)

            logger.debug(
                f"📊 Updated progress for task {task_id}: {progress_percent:.1f}% ({current_phase})"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update progress: {e}")
            return False

    async def update_resource_usage(self, task_id: str, resource_usage: dict[str, Any]) -> bool:
        """Update task resource usage"""
        try:
            if task_id not in self.active_contexts:
                logger.error(f"❌ Task {task_id} not being tracked")
                return False

            context = self.active_contexts[task_id]
            context.resource_usage = resource_usage
            context.last_heartbeat = datetime.utcnow()

            logger.debug(f"📊 Updated resource usage for task {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update resource usage: {e}")
            return False

    async def update_intermediate_results(self, task_id: str, results: dict[str, Any]) -> bool:
        """Update task intermediate results"""
        try:
            if task_id not in self.active_contexts:
                logger.error(f"❌ Task {task_id} not being tracked")
                return False

            context = self.active_contexts[task_id]
            context.intermediate_results.update(results)
            context.last_heartbeat = datetime.utcnow()

            logger.debug(f"📊 Updated intermediate results for task {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update intermediate results: {e}")
            return False

    async def heartbeat(self, task_id: str) -> bool:
        """Update task heartbeat"""
        try:
            if task_id not in self.active_contexts:
                logger.error(f"❌ Task {task_id} not being tracked")
                return False

            context = self.active_contexts[task_id]
            context.last_heartbeat = datetime.utcnow()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to update heartbeat: {e}")
            return False

    async def complete_task_tracking(
        self, task_id: str, final_results: dict[str, Any] | None = None
    ) -> bool:
        """Complete task tracking and archive context"""
        try:
            if task_id not in self.active_contexts:
                logger.error(f"❌ Task {task_id} not being tracked")
                return False

            context = self.active_contexts[task_id]

            # Set final progress
            context.progress_percent = 100.0
            context.current_phase = "completed"

            # Add final results
            if final_results:
                context.intermediate_results.update(final_results)

            # Add completion status update
            status_update = {
                "timestamp": datetime.utcnow().isoformat(),
                "progress_percent": 100.0,
                "phase": "completed",
                "details": final_results or {},
            }
            context.status_updates.append(status_update)

            # Move to completed contexts
            self.completed_contexts[task_id] = context
            del self.active_contexts[task_id]

            self.tracking_stats["active_tasks"] = len(self.active_contexts)

            logger.info(f"✅ Completed tracking for task {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to complete task tracking: {e}")
            return False

    async def fail_task_tracking(
        self, task_id: str, error_details: dict[str, Any] | None = None
    ) -> bool:
        """Mark task tracking as failed"""
        try:
            if task_id not in self.active_contexts:
                logger.error(f"❌ Task {task_id} not being tracked")
                return False

            context = self.active_contexts[task_id]

            # Set failure state
            context.current_phase = "failed"

            # Add failure status update
            status_update = {
                "timestamp": datetime.utcnow().isoformat(),
                "progress_percent": context.progress_percent,
                "phase": "failed",
                "details": error_details or {},
            }
            context.status_updates.append(status_update)

            # Move to completed contexts
            self.completed_contexts[task_id] = context
            del self.active_contexts[task_id]

            self.tracking_stats["active_tasks"] = len(self.active_contexts)

            logger.info(f"❌ Failed tracking for task {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to fail task tracking: {e}")
            return False

    async def get_task_progress(self, task_id: str) -> dict[str, Any] | None:
        """Get current progress for a task"""
        try:
            # Check active contexts first
            if task_id in self.active_contexts:
                context = self.active_contexts[task_id]
                return self._format_progress_response(context, is_active=True)

            # Check completed contexts
            if task_id in self.completed_contexts:
                context = self.completed_contexts[task_id]
                return self._format_progress_response(context, is_active=False)

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get task progress: {e}")
            return None

    async def get_active_tasks(self) -> list[dict[str, Any]]:
        """Get all active task progress"""
        try:
            active_tasks = []

            for task_id, context in self.active_contexts.items():
                progress_info = self._format_progress_response(context, is_active=True)
                active_tasks.append(progress_info)

            return active_tasks

        except Exception as e:
            logger.error(f"❌ Failed to get active tasks: {e}")
            return []

    async def get_learning_progress_history(
        self, task_id: str, limit: int = 50
    ) -> list[LearningProgress]:
        """Get learning progress history for a task"""
        try:
            if task_id not in self.progress_history:
                return []

            history = self.progress_history[task_id]
            return history[-limit:] if limit > 0 else history

        except Exception as e:
            logger.error(f"❌ Failed to get learning progress history: {e}")
            return []

    async def get_tracking_statistics(self) -> dict[str, Any]:
        """Get progress tracking statistics"""
        try:
            # Calculate average progress rate
            if self.active_contexts:
                total_progress = sum(ctx.progress_percent for ctx in self.active_contexts.values())
                self.tracking_stats["avg_progress_rate"] = total_progress / len(
                    self.active_contexts
                )

            # Count stale tasks
            stale_threshold = timedelta(minutes=self.config.stale_threshold_minutes)
            current_time = datetime.utcnow()
            stale_count = 0

            for context in self.active_contexts.values():
                if current_time - context.last_heartbeat > stale_threshold:
                    stale_count += 1

            self.tracking_stats["stale_tasks"] = stale_count

            return {
                "service": "progress_tracker",
                "statistics": self.tracking_stats,
                "active_tasks": len(self.active_contexts),
                "completed_tasks": len(self.completed_contexts),
                "total_progress_records": sum(
                    len(history) for history in self.progress_history.values()
                ),
                "config": {
                    "heartbeat_interval_seconds": self.config.heartbeat_interval_seconds,
                    "stale_threshold_minutes": self.config.stale_threshold_minutes,
                    "progress_report_interval": self.config.progress_report_interval,
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get tracking statistics: {e}")
            return {"error": str(e)}

    def _format_progress_response(
        self, context: TaskExecutionContext, is_active: bool
    ) -> dict[str, Any]:
        """Format progress response"""
        try:
            # Calculate runtime
            runtime = datetime.utcnow() - context.started_at

            return {
                "task_id": context.task_id,
                "worker_id": context.worker_id,
                "is_active": is_active,
                "progress_percent": context.progress_percent,
                "current_phase": context.current_phase,
                "started_at": context.started_at.isoformat(),
                "last_heartbeat": context.last_heartbeat.isoformat(),
                "runtime_minutes": runtime.total_seconds() / 60,
                "resource_usage": context.resource_usage,
                "intermediate_results": context.intermediate_results,
                "recent_updates": context.status_updates[-10:],  # Last 10 updates
                "total_updates": len(context.status_updates),
            }

        except Exception as e:
            logger.error(f"❌ Failed to format progress response: {e}")
            return {"error": str(e)}

    async def _record_learning_progress(
        self, task_id: str, context: TaskExecutionContext, details: dict[str, Any] | None
    ) -> None:
        """Record learning progress"""
        try:
            if task_id not in self.progress_history:
                return

            # Extract metrics from details if available
            training_loss = 0.0
            validation_metrics = {}

            if details:
                training_loss = details.get("training_loss", 0.0)
                validation_metrics = details.get("validation_metrics", {})

            # Create learning progress record
            progress_record = LearningProgress(
                task_id=task_id,
                model_id=details.get("model_id", "unknown") if details else "unknown",
                current_epoch=int(context.progress_percent),
                total_epochs=100,  # Assuming 100% = 100 epochs for simplicity
                training_loss=training_loss,
                validation_metrics=validation_metrics,
                timestamp=datetime.utcnow(),
                metadata={
                    "phase": context.current_phase,
                    "worker_id": context.worker_id,
                    "resource_usage": context.resource_usage,
                },
            )

            self.progress_history[task_id].append(progress_record)

            # Limit history size
            if len(self.progress_history[task_id]) > 1000:
                self.progress_history[task_id] = self.progress_history[task_id][-1000:]

        except Exception as e:
            logger.error(f"❌ Failed to record learning progress: {e}")

    async def _check_progress_reporting(self, task_id: str, progress_percent: float) -> None:
        """Check if progress should be reported"""
        try:
            last_reported = self.last_progress_report.get(task_id, 0.0)
            interval = self.config.progress_report_interval

            if progress_percent - last_reported >= interval:
                self.last_progress_report[task_id] = progress_percent
                logger.info(f"📈 Task {task_id} progress: {progress_percent:.1f}%")

        except Exception as e:
            logger.error(f"❌ Failed to check progress reporting: {e}")

    async def _monitoring_loop(self) -> None:
        """Monitor tasks for stale heartbeats and other issues"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(self.config.heartbeat_interval_seconds)

                # Check for stale tasks
                await self._check_stale_tasks()

                # Clean up old completed contexts
                await self._cleanup_old_contexts()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")

    async def _check_stale_tasks(self) -> None:
        """Check for tasks with stale heartbeats"""
        try:
            stale_threshold = timedelta(minutes=self.config.stale_threshold_minutes)
            current_time = datetime.utcnow()

            stale_tasks = []
            for task_id, context in self.active_contexts.items():
                if current_time - context.last_heartbeat > stale_threshold:
                    stale_tasks.append(task_id)

            for task_id in stale_tasks:
                logger.warning(
                    f"⚠️ Task {task_id} appears stale (no heartbeat for {self.config.stale_threshold_minutes} minutes)"
                )
                # Optionally mark as failed or take other action

        except Exception as e:
            logger.error(f"❌ Failed to check stale tasks: {e}")

    async def _cleanup_old_contexts(self) -> None:
        """Clean up old completed contexts"""
        try:
            # Keep only recent completed contexts (last 24 hours)
            cleanup_threshold = datetime.utcnow() - timedelta(hours=24)

            tasks_to_remove = []
            for task_id, context in self.completed_contexts.items():
                if context.started_at < cleanup_threshold:
                    tasks_to_remove.append(task_id)

            for task_id in tasks_to_remove:
                del self.completed_contexts[task_id]
                # Also clean up progress history
                if task_id in self.progress_history:
                    del self.progress_history[task_id]
                if task_id in self.last_progress_report:
                    del self.last_progress_report[task_id]

            if tasks_to_remove:
                logger.info(f"🧹 Cleaned up {len(tasks_to_remove)} old task contexts")

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old contexts: {e}")
