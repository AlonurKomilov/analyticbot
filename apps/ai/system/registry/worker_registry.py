"""Worker Registry - Central registry for all manageable workers"""

import logging
from typing import Any

from apps.ai.shared.models.worker import (
    ResourceRequirements,
    WorkerConfig,
    WorkerDefinition,
    WorkerState,
    WorkerStatus,
    WorkerType,
)

logger = logging.getLogger(__name__)


class WorkerRegistry:
    """
    Central registry for all workers that can be managed by the AI system.

    Responsibilities:
    - Register new workers
    - Track worker definitions and state
    - Discover workers from codebase
    - Provide worker information to AI controller
    """

    def __init__(self):
        self.workers: dict[str, WorkerDefinition] = {}
        self.worker_states: dict[str, WorkerState] = {}

        logger.info("📋 Worker Registry initialized")

    async def register_worker(self, definition: WorkerDefinition) -> bool:
        """Register a new worker"""
        try:
            self.workers[definition.name] = definition

            # Initialize state if not exists
            if definition.name not in self.worker_states:
                self.worker_states[definition.name] = WorkerState(
                    worker_name=definition.name,
                    worker_type=definition.worker_type,
                    status=WorkerStatus.UNKNOWN,
                )

            logger.info(f"✅ Registered worker: {definition.name} ({definition.worker_type.value})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to register worker {definition.name}: {e}")
            return False

    async def unregister_worker(self, worker_name: str) -> bool:
        """Unregister a worker"""
        try:
            if worker_name in self.workers:
                del self.workers[worker_name]

            if worker_name in self.worker_states:
                del self.worker_states[worker_name]

            logger.info(f"✅ Unregistered worker: {worker_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to unregister worker {worker_name}: {e}")
            return False

    async def get_worker(self, worker_name: str) -> WorkerDefinition | None:
        """Get worker definition by name"""
        return self.workers.get(worker_name)

    async def get_worker_state(self, worker_name: str) -> WorkerState | None:
        """Get current state of a worker"""
        return self.worker_states.get(worker_name)

    async def update_worker_state(self, worker_name: str, state: WorkerState) -> bool:
        """Update worker state"""
        try:
            if worker_name not in self.workers:
                logger.warning(f"⚠️  Worker {worker_name} not registered")
                return False

            self.worker_states[worker_name] = state
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update worker state for {worker_name}: {e}")
            return False

    async def list_workers(
        self,
        worker_type: WorkerType | None = None,
        ai_manageable_only: bool = False,
        status: WorkerStatus | None = None,
    ) -> list[WorkerDefinition]:
        """List workers with optional filters"""
        workers = list(self.workers.values())

        if worker_type:
            workers = [w for w in workers if w.worker_type == worker_type]

        if ai_manageable_only:
            workers = [w for w in workers if w.ai_manageable]

        if status:
            workers = [
                w
                for w in workers
                if w.name in self.worker_states and self.worker_states[w.name].status == status
            ]

        return workers

    async def discover_workers(self) -> list[WorkerDefinition]:
        """
        Discover workers from the codebase automatically.

        This method scans for known worker patterns and registers them.
        """
        discovered = []

        # MTProto Worker
        mtproto_worker = WorkerDefinition(
            name="mtproto_worker",
            worker_type=WorkerType.MTPROTO,
            module_path="apps.mtproto.system.worker",
            description="MTProto data collection worker for Telegram channels",
            config=WorkerConfig(
                interval_minutes=10,
                batch_size=5000,
                max_runtime_hours=24.0,
                health_check_port=9091,
                memory_limit_mb=2048,
                cpu_limit_percent=80.0,
                auto_scaling_enabled=True,
                min_instances=1,
                max_instances=3,
            ),
            resource_requirements=ResourceRequirements(
                cpu_cores=1.0,
                memory_mb=512,
                max_cpu_percent=80.0,
                max_memory_mb=2048,
            ),
            health_endpoint="http://localhost:9091/health",
            metrics_endpoint="http://localhost:9091/metrics",
            log_file="logs/dev_mtproto_worker.log",
            ai_manageable=True,
            auto_restart_on_failure=True,
            requires_approval_for=["scale_up", "modify_db_config"],
            tags=["telegram", "data-collection", "real-time"],
            dependencies=["postgresql", "redis"],
        )
        await self.register_worker(mtproto_worker)
        discovered.append(mtproto_worker)

        # Bot Worker
        bot_worker = WorkerDefinition(
            name="bot_worker",
            worker_type=WorkerType.BOT,
            module_path="apps.bot.system.run_bot",
            description="Telegram bot worker for user interactions",
            config=WorkerConfig(
                max_runtime_hours=24.0,
                memory_limit_mb=1024,
                cpu_limit_percent=70.0,
                auto_scaling_enabled=False,  # Single instance
            ),
            resource_requirements=ResourceRequirements(
                cpu_cores=0.5, memory_mb=256, max_cpu_percent=70.0, max_memory_mb=1024
            ),
            log_file="logs/dev_bot.log",
            ai_manageable=True,
            auto_restart_on_failure=True,
            requires_approval_for=["stop_worker", "modify_token"],
            tags=["telegram", "bot", "user-interaction"],
            dependencies=["postgresql", "redis", "api"],
        )
        await self.register_worker(bot_worker)
        discovered.append(bot_worker)

        # API Workers
        api_worker = WorkerDefinition(
            name="api_worker",
            worker_type=WorkerType.API,
            module_path="apps.api.main",
            description="FastAPI backend application",
            config=WorkerConfig(
                auto_scaling_enabled=True,
                min_instances=2,
                max_instances=8,
                scale_up_threshold=70.0,
                scale_down_threshold=30.0,
            ),
            resource_requirements=ResourceRequirements(
                cpu_cores=1.0, memory_mb=512, max_cpu_percent=80.0, max_memory_mb=2048
            ),
            health_endpoint="http://localhost:11400/health",
            log_file="logs/dev_api.log",
            ai_manageable=True,
            auto_restart_on_failure=True,
            requires_approval_for=["scale_down_below_2"],
            tags=["api", "http", "backend"],
            dependencies=["postgresql", "redis"],
        )
        await self.register_worker(api_worker)
        discovered.append(api_worker)

        # Celery Workers
        celery_worker = WorkerDefinition(
            name="celery_worker",
            worker_type=WorkerType.CELERY,
            module_path="apps.workers.celery_app",
            description="Celery background task worker",
            config=WorkerConfig(
                auto_scaling_enabled=True,
                min_instances=1,
                max_instances=5,
                custom_settings={
                    "concurrency": 4,
                    "prefetch_multiplier": 4,
                    "max_tasks_per_child": 1000,
                },
            ),
            resource_requirements=ResourceRequirements(
                cpu_cores=1.0, memory_mb=512, max_cpu_percent=80.0, max_memory_mb=2048
            ),
            ai_manageable=True,
            auto_restart_on_failure=True,
            requires_approval_for=["scale_up_above_5"],
            tags=["celery", "background-tasks", "async"],
            dependencies=["postgresql", "redis"],
        )
        await self.register_worker(celery_worker)
        discovered.append(celery_worker)

        logger.info(f"🔍 Discovered {len(discovered)} workers")
        return discovered

    async def get_registry_stats(self) -> dict[str, Any]:
        """Get registry statistics"""
        status_counts = {}
        for state in self.worker_states.values():
            status_counts[state.status.value] = status_counts.get(state.status.value, 0) + 1

        type_counts = {}
        for worker in self.workers.values():
            type_counts[worker.worker_type.value] = type_counts.get(worker.worker_type.value, 0) + 1

        return {
            "total_workers": len(self.workers),
            "ai_manageable_workers": len([w for w in self.workers.values() if w.ai_manageable]),
            "status_counts": status_counts,
            "type_counts": type_counts,
            "auto_scaling_enabled": len(
                [w for w in self.workers.values() if w.config.auto_scaling_enabled]
            ),
        }
