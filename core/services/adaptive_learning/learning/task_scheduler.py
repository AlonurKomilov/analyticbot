"""
Task Scheduler
=============

Handles learning task scheduling, prioritization, and worker assignment.
Extracted from LearningTaskManager god object to focus on scheduling concerns.
"""

import asyncio
import heapq
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from core.services.adaptive_learning.protocols.learning_protocols import (
    LearningTask,
    UpdateStatus,
)

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TaskScheduleInfo:
    """Task scheduling information"""

    task_id: str
    priority: TaskPriority
    scheduled_at: datetime
    estimated_duration: timedelta
    resource_requirements: dict[str, Any]
    dependencies: list[str]

    def __lt__(self, other):
        """For priority queue ordering"""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3,
        }
        return priority_order[self.priority] < priority_order[other.priority]


@dataclass
class WorkerInfo:
    """Worker information for task assignment"""

    worker_id: str
    is_available: bool
    current_task_id: str | None
    capabilities: dict[str, Any]
    resource_capacity: dict[str, Any]
    last_heartbeat: datetime


@dataclass
class SchedulingConfig:
    """Configuration for task scheduling"""

    max_concurrent_tasks: int = 3
    worker_timeout_minutes: int = 30
    priority_boost_hours: int = 24
    load_balancing_enabled: bool = True
    resource_aware_scheduling: bool = True


class TaskScheduler:
    """
    Handles task scheduling, prioritization, and worker assignment.

    Focuses solely on:
    - Task queue management
    - Priority-based scheduling
    - Worker assignment and load balancing
    - Resource-aware scheduling
    """

    def __init__(self, config: SchedulingConfig | None = None):
        self.config = config or SchedulingConfig()

        # Task queue (priority queue)
        self.task_queue: list[TaskScheduleInfo] = []
        self.pending_tasks: dict[str, LearningTask] = {}
        self.scheduled_tasks: dict[str, TaskScheduleInfo] = {}

        # Worker management
        self.available_workers: set[str] = set()
        self.worker_info: dict[str, WorkerInfo] = {}
        self.worker_assignments: dict[str, str] = {}  # worker_id -> task_id

        # Scheduling state
        self.is_running = False
        self.scheduler_task: asyncio.Task | None = None

        # Statistics
        self.scheduling_stats = {
            "total_scheduled": 0,
            "total_assigned": 0,
            "avg_wait_time_minutes": 0.0,
            "worker_utilization": {},
        }

        logger.info("📅 Task Scheduler initialized")

    async def start_scheduler(self) -> bool:
        """Start the task scheduler"""
        try:
            if self.is_running:
                logger.warning("⚠️ Scheduler already running")
                return True

            # Start scheduling loop
            self.scheduler_task = asyncio.create_task(self._scheduling_loop())
            self.is_running = True

            logger.info("✅ Task scheduler started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            return False

    async def stop_scheduler(self) -> bool:
        """Stop the task scheduler"""
        try:
            self.is_running = False

            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass

            logger.info("⏹️ Task scheduler stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
            return False

    async def schedule_task(
        self,
        task: LearningTask,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: list[str] | None = None,
    ) -> bool:
        """Schedule a task for execution"""
        try:
            # Extract resource requirements and duration from task parameters
            resource_requirements = task.parameters.get("resource_requirements", {})
            estimated_duration_minutes = task.parameters.get("estimated_duration_minutes", 30)
            estimated_duration = timedelta(minutes=estimated_duration_minutes)

            # Create schedule info
            schedule_info = TaskScheduleInfo(
                task_id=task.task_id,
                priority=priority,
                scheduled_at=datetime.utcnow(),
                estimated_duration=estimated_duration,
                resource_requirements=resource_requirements,
                dependencies=dependencies or [],
            )

            # Add to pending tasks and scheduling queue
            self.pending_tasks[task.task_id] = task
            self.scheduled_tasks[task.task_id] = schedule_info

            # Add to priority queue
            heapq.heappush(self.task_queue, schedule_info)

            self.scheduling_stats["total_scheduled"] += 1

            logger.info(f"📅 Scheduled task {task.task_id} with priority {priority.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to schedule task: {e}")
            return False

    async def assign_task_to_worker(self, task_id: str, worker_id: str) -> bool:
        """Manually assign a task to a specific worker"""
        try:
            if task_id not in self.pending_tasks:
                logger.error(f"❌ Task {task_id} not found in pending tasks")
                return False

            if worker_id not in self.available_workers:
                logger.error(f"❌ Worker {worker_id} not available")
                return False

            # Update worker assignment
            self.worker_assignments[worker_id] = task_id
            self.available_workers.discard(worker_id)

            # Update worker info
            if worker_id in self.worker_info:
                self.worker_info[worker_id].is_available = False
                self.worker_info[worker_id].current_task_id = task_id

            # Update task status
            task = self.pending_tasks[task_id]
            task.status = UpdateStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()

            # Remove from queue and pending
            self._remove_from_queue(task_id)
            del self.pending_tasks[task_id]

            self.scheduling_stats["total_assigned"] += 1

            logger.info(f"📅 Assigned task {task_id} to worker {worker_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to assign task to worker: {e}")
            return False

    async def register_worker(
        self,
        worker_id: str,
        capabilities: dict[str, Any],
        resource_capacity: dict[str, Any],
    ) -> bool:
        """Register a new worker"""
        try:
            worker_info = WorkerInfo(
                worker_id=worker_id,
                is_available=True,
                current_task_id=None,
                capabilities=capabilities,
                resource_capacity=resource_capacity,
                last_heartbeat=datetime.utcnow(),
            )

            self.worker_info[worker_id] = worker_info
            self.available_workers.add(worker_id)
            self.scheduling_stats["worker_utilization"][worker_id] = 0.0

            logger.info(f"👷 Registered worker {worker_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to register worker: {e}")
            return False

    async def unregister_worker(self, worker_id: str) -> bool:
        """Unregister a worker"""
        try:
            # Check if worker has active task
            if worker_id in self.worker_assignments:
                task_id = self.worker_assignments[worker_id]
                logger.warning(f"⚠️ Unregistering worker {worker_id} with active task {task_id}")
                # TODO: Handle task reassignment

            # Remove worker
            self.available_workers.discard(worker_id)
            if worker_id in self.worker_info:
                del self.worker_info[worker_id]
            if worker_id in self.worker_assignments:
                del self.worker_assignments[worker_id]
            if worker_id in self.scheduling_stats["worker_utilization"]:
                del self.scheduling_stats["worker_utilization"][worker_id]

            logger.info(f"👷 Unregistered worker {worker_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to unregister worker: {e}")
            return False

    async def worker_heartbeat(self, worker_id: str) -> bool:
        """Update worker heartbeat"""
        try:
            if worker_id in self.worker_info:
                self.worker_info[worker_id].last_heartbeat = datetime.utcnow()
                return True
            else:
                logger.warning(f"⚠️ Heartbeat from unknown worker {worker_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to update worker heartbeat: {e}")
            return False

    async def task_completed(self, task_id: str, worker_id: str) -> bool:
        """Mark task as completed and free worker"""
        try:
            # Free worker
            if worker_id in self.worker_assignments:
                del self.worker_assignments[worker_id]

            if worker_id in self.worker_info:
                self.worker_info[worker_id].is_available = True
                self.worker_info[worker_id].current_task_id = None
                self.available_workers.add(worker_id)

            # Remove from scheduled tasks
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]

            logger.info(f"✅ Task {task_id} completed, worker {worker_id} freed")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to handle task completion: {e}")
            return False

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        try:
            # Remove from queue
            self._remove_from_queue(task_id)

            # Remove from pending and scheduled
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]

            logger.info(f"🚫 Cancelled task {task_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to cancel task: {e}")
            return False

    async def get_next_task(self) -> str | None:
        """Get the next task to execute (for manual scheduling)"""
        try:
            if not self.task_queue:
                return None

            # Check dependencies for top priority task
            while self.task_queue:
                schedule_info = self.task_queue[0]

                # Check if dependencies are satisfied
                if await self._are_dependencies_satisfied(schedule_info):
                    # Check if we have available workers
                    if self.available_workers:
                        return schedule_info.task_id
                    else:
                        break  # No available workers
                else:
                    # Dependencies not satisfied, check next task
                    heapq.heappop(self.task_queue)
                    # Re-add to queue with lower priority (temporary)
                    schedule_info.priority = TaskPriority.LOW
                    heapq.heappush(self.task_queue, schedule_info)
                    break

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get next task: {e}")
            return None

    async def get_queue_status(self) -> dict[str, Any]:
        """Get current queue status"""
        try:
            # Calculate wait times
            current_time = datetime.utcnow()
            wait_times = []

            for schedule_info in self.task_queue:
                wait_time = (current_time - schedule_info.scheduled_at).total_seconds() / 60
                wait_times.append(wait_time)

            avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0
            self.scheduling_stats["avg_wait_time_minutes"] = avg_wait_time

            return {
                "service": "task_scheduler",
                "queue_length": len(self.task_queue),
                "pending_tasks": len(self.pending_tasks),
                "available_workers": len(self.available_workers),
                "total_workers": len(self.worker_info),
                "active_assignments": len(self.worker_assignments),
                "statistics": self.scheduling_stats,
                "queue_summary": {
                    priority.value: len([s for s in self.task_queue if s.priority == priority])
                    for priority in TaskPriority
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get queue status: {e}")
            return {"error": str(e)}

    def _remove_from_queue(self, task_id: str) -> None:
        """Remove task from priority queue"""
        try:
            # Find and remove task from queue
            self.task_queue = [
                schedule_info
                for schedule_info in self.task_queue
                if schedule_info.task_id != task_id
            ]
            # Rebuild heap
            heapq.heapify(self.task_queue)

        except Exception as e:
            logger.error(f"❌ Failed to remove task from queue: {e}")

    async def _scheduling_loop(self) -> None:
        """Main scheduling loop"""
        while self.is_running:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds

                # Check for worker timeouts
                await self._check_worker_timeouts()

                # Auto-assign tasks if enabled
                if self.config.load_balancing_enabled:
                    await self._auto_assign_tasks()

                # Boost priority for old tasks
                await self._boost_old_task_priorities()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in scheduling loop: {e}")

    async def _check_worker_timeouts(self) -> None:
        """Check for worker timeouts and handle them"""
        try:
            current_time = datetime.utcnow()
            timeout_threshold = timedelta(minutes=self.config.worker_timeout_minutes)

            timed_out_workers = []
            for worker_id, worker_info in self.worker_info.items():
                if current_time - worker_info.last_heartbeat > timeout_threshold:
                    timed_out_workers.append(worker_id)

            for worker_id in timed_out_workers:
                logger.warning(f"⚠️ Worker {worker_id} timed out")
                await self.unregister_worker(worker_id)

        except Exception as e:
            logger.error(f"❌ Failed to check worker timeouts: {e}")

    async def _auto_assign_tasks(self) -> None:
        """Automatically assign tasks to available workers"""
        try:
            while self.available_workers and self.task_queue:
                # Get next task
                next_task_id = await self.get_next_task()
                if not next_task_id:
                    break

                # Find best worker for task
                best_worker = await self._find_best_worker(next_task_id)
                if best_worker:
                    await self.assign_task_to_worker(next_task_id, best_worker)
                else:
                    break  # No suitable worker found

        except Exception as e:
            logger.error(f"❌ Failed to auto-assign tasks: {e}")

    async def _find_best_worker(self, task_id: str) -> str | None:
        """Find the best available worker for a task"""
        try:
            if task_id not in self.scheduled_tasks:
                return None

            schedule_info = self.scheduled_tasks[task_id]
            resource_requirements = schedule_info.resource_requirements

            # If resource-aware scheduling is disabled, return any available worker
            if not self.config.resource_aware_scheduling:
                return next(iter(self.available_workers)) if self.available_workers else None

            # Find worker with best resource match
            best_worker = None
            best_score = -1

            for worker_id in self.available_workers:
                worker_info = self.worker_info.get(worker_id)
                if not worker_info:
                    continue

                score = self._calculate_worker_score(worker_info, resource_requirements)
                if score > best_score:
                    best_score = score
                    best_worker = worker_id

            return best_worker

        except Exception as e:
            logger.error(f"❌ Failed to find best worker: {e}")
            return None

    def _calculate_worker_score(
        self, worker_info: WorkerInfo, resource_requirements: dict[str, Any]
    ) -> float:
        """Calculate suitability score for worker-task assignment"""
        try:
            score = 0.0

            # Check memory requirements
            required_memory = resource_requirements.get("memory_mb", 0)
            available_memory = worker_info.resource_capacity.get("memory_mb", 0)
            if available_memory >= required_memory:
                score += 1.0
            else:
                return -1.0  # Cannot handle memory requirement

            # Check CPU requirements
            required_cpu = resource_requirements.get("cpu_cores", 1)
            available_cpu = worker_info.resource_capacity.get("cpu_cores", 1)
            if available_cpu >= required_cpu:
                score += 1.0

            # Check GPU requirements
            gpu_required = resource_requirements.get("gpu_required", False)
            gpu_available = worker_info.resource_capacity.get("gpu_available", False)
            if gpu_required and gpu_available:
                score += 2.0
            elif not gpu_required:
                score += 1.0
            elif gpu_required and not gpu_available:
                return -1.0  # Cannot handle GPU requirement

            return score

        except Exception as e:
            logger.error(f"❌ Failed to calculate worker score: {e}")
            return 0.0

    async def _are_dependencies_satisfied(self, schedule_info: TaskScheduleInfo) -> bool:
        """Check if task dependencies are satisfied"""
        try:
            # For now, assume all dependencies are satisfied
            # In a real implementation, this would check the status of dependent tasks
            return len(schedule_info.dependencies) == 0

        except Exception as e:
            logger.error(f"❌ Failed to check dependencies: {e}")
            return False

    async def _boost_old_task_priorities(self) -> None:
        """Boost priority for tasks that have been waiting too long"""
        try:
            current_time = datetime.utcnow()
            boost_threshold = timedelta(hours=self.config.priority_boost_hours)

            for schedule_info in self.task_queue:
                wait_time = current_time - schedule_info.scheduled_at
                if wait_time > boost_threshold and schedule_info.priority != TaskPriority.CRITICAL:
                    # Boost priority
                    if schedule_info.priority == TaskPriority.LOW:
                        schedule_info.priority = TaskPriority.NORMAL
                    elif schedule_info.priority == TaskPriority.NORMAL:
                        schedule_info.priority = TaskPriority.HIGH
                    elif schedule_info.priority == TaskPriority.HIGH:
                        schedule_info.priority = TaskPriority.CRITICAL

                    logger.info(f"⬆️ Boosted priority for task {schedule_info.task_id}")

            # Rebuild heap after priority changes
            heapq.heapify(self.task_queue)

        except Exception as e:
            logger.error(f"❌ Failed to boost old task priorities: {e}")

    async def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get the status of a specific task"""
        try:
            # Check if task is in queue
            for schedule_info in self.task_queue:
                if schedule_info.task_id == task_id:
                    return {
                        "task_id": task_id,
                        "status": "queued",
                        "priority": schedule_info.priority.value,
                        "scheduled_at": schedule_info.scheduled_at.isoformat(),
                    }

            # Check if task is assigned to worker
            for worker_id, assigned_task_id in self.worker_assignments.items():
                if assigned_task_id == task_id:
                    return {
                        "task_id": task_id,
                        "status": "assigned",
                        "worker_id": worker_id,
                    }

            # Task not found
            return None

        except Exception as e:
            logger.error(f"❌ Failed to get task status for {task_id}: {e}")
            return None

    async def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed"""
        try:
            # Find and remove task from worker assignments
            for worker_id, assigned_task_id in self.worker_assignments.items():
                if assigned_task_id == task_id:
                    del self.worker_assignments[worker_id]
                    # Mark worker as available
                    if worker_id in self.worker_info:
                        self.worker_info[worker_id].is_available = True
                        self.worker_info[worker_id].current_task_id = None
                        self.available_workers.add(worker_id)

                    logger.info(f"✅ Task {task_id} completed by worker {worker_id}")
                    return True

            logger.warning(f"⚠️ Task {task_id} not found in worker assignments")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to complete task {task_id}: {e}")
            return False

    async def get_scheduler_statistics(self) -> dict[str, Any]:
        """Get scheduler statistics"""
        try:
            return {
                "service": "task_scheduler",
                "queue_size": len(self.task_queue),
                "active_workers": len(self.worker_info),
                "available_workers": len(self.available_workers),
                "worker_assignments": len(self.worker_assignments),
                "total_assigned_tasks": len(self.worker_assignments),
                "is_running": self.is_running,
                "config": {
                    "max_concurrent_tasks": self.config.max_concurrent_tasks,
                    "worker_timeout_minutes": self.config.worker_timeout_minutes,
                    "priority_boost_hours": self.config.priority_boost_hours,
                },
                "stats": self.scheduling_stats,
            }
        except Exception as e:
            logger.error(f"❌ Failed to get scheduler statistics: {e}")
            return {"error": str(e)}

    async def health_check(self) -> bool:
        """Check the health of the task scheduler"""
        try:
            # Check if scheduler is running and workers are responsive
            if not self.is_running:
                return False

            # Check if we have any active workers
            current_time = datetime.utcnow()
            active_workers = 0
            for worker_id, worker_info in self.worker_info.items():
                time_since_heartbeat = current_time - worker_info.last_heartbeat
                if time_since_heartbeat.total_seconds() < self.config.worker_timeout_minutes * 60:
                    active_workers += 1

            # Health is good if we have at least one active worker or no tasks in queue
            return active_workers > 0 or len(self.task_queue) == 0

        except Exception as e:
            logger.error(f"❌ TaskScheduler health check failed: {e}")
            return False
