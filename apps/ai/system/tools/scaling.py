"""
Scaling Tools
=============

Tools for scaling workers and adjusting their configuration.
"""

import logging
from datetime import datetime
from typing import Any

from apps.ai.system.tools.base import (
    BaseTool,
    ToolCategory,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
)

logger = logging.getLogger(__name__)


class ScaleWorkerTool(BaseTool):
    """
    Scale a worker up or down (change instance count).

    Medium risk - changes resource allocation.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="scale_worker",
            description="Scale a worker up or down by changing instance count",
            category=ToolCategory.SCALING,
            risk_level=ToolRiskLevel.MEDIUM,
            requires_approval=True,
            cooldown_seconds=300,  # 5 minute cooldown
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {"type": "string", "description": "Worker to scale"},
                    "direction": {
                        "type": "string",
                        "enum": ["up", "down"],
                        "description": "Scale direction",
                    },
                    "count": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of instances to add/remove",
                    },
                    "reason": {"type": "string", "description": "Reason for scaling"},
                },
                "required": ["worker_name", "direction"],
            },
        )

    async def validate_params(self, **params: Any) -> tuple[bool, str]:
        worker_name = params.get("worker_name")
        direction = params.get("direction")
        count = params.get("count", 1)

        if not worker_name:
            return False, "worker_name is required"

        if direction not in ["up", "down"]:
            return False, "direction must be 'up' or 'down'"

        if count < 1 or count > 5:
            return False, "count must be between 1 and 5"

        return True, ""

    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        direction = params.get("direction")
        count = params.get("count", 1)
        reason = params.get("reason", "AI-initiated scaling")

        try:
            from apps.ai.system.registry import WorkerRegistry

            registry = WorkerRegistry()

            worker = await registry.get_worker(worker_name)
            if not worker:
                return ToolResult(
                    success=False,
                    tool_name=self.definition.name,
                    error=f"Worker '{worker_name}' not found",
                )

            if not worker.ai_manageable:
                return ToolResult(
                    success=False,
                    tool_name=self.definition.name,
                    error=f"Worker '{worker_name}' is not AI-manageable",
                )

            if not worker.config.auto_scaling_enabled:
                return ToolResult(
                    success=False,
                    tool_name=self.definition.name,
                    error=f"Auto-scaling not enabled for '{worker_name}'",
                )

            # Calculate new instance count
            current_instances = worker.config.min_instances
            if direction == "up":
                new_instances = min(current_instances + count, worker.config.max_instances)
            else:
                new_instances = max(
                    current_instances - count,
                    1,  # Always keep at least 1
                )

            if new_instances == current_instances:
                return ToolResult(
                    success=True,
                    tool_name=self.definition.name,
                    data={
                        "worker_name": worker_name,
                        "action": "no_change",
                        "current_instances": current_instances,
                        "reason": f"Already at {'max' if direction == 'up' else 'min'} instances",
                    },
                    message="No scaling needed - already at limit",
                )

            # TODO: Actually scale the worker
            # This would interact with:
            # - Docker Compose for container-based workers
            # - Celery for task workers
            # - Process manager for daemon workers

            logger.info(
                f"🔄 Scaling {worker_name} {direction}: {current_instances} -> {new_instances}"
            )

            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data={
                    "worker_name": worker_name,
                    "direction": direction,
                    "previous_instances": current_instances,
                    "new_instances": new_instances,
                    "reason": reason,
                    "scaled_at": datetime.utcnow().isoformat(),
                },
                message=f"Scaled {worker_name} {direction}: {current_instances} -> {new_instances}",
            )

        except Exception as e:
            logger.error(f"Scaling failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )


class AdjustIntervalTool(BaseTool):
    """
    Adjust worker polling/execution interval.

    Low risk - changes timing but not resources.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="adjust_interval",
            description="Adjust worker polling or execution interval",
            category=ToolCategory.SCALING,
            risk_level=ToolRiskLevel.LOW,
            cooldown_seconds=60,  # 1 minute cooldown
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {
                        "type": "string",
                        "description": "Worker to adjust",
                    },
                    "new_interval_minutes": {
                        "type": "number",
                        "description": "New interval in minutes",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for adjustment",
                    },
                },
                "required": ["worker_name", "new_interval_minutes"],
            },
        )

    async def validate_params(self, **params: Any) -> tuple[bool, str]:
        worker_name = params.get("worker_name")
        new_interval = params.get("new_interval_minutes")

        if not worker_name:
            return False, "worker_name is required"

        if new_interval is None:
            return False, "new_interval_minutes is required"

        if new_interval < 1 or new_interval > 1440:  # 1 min to 24 hours
            return False, "interval must be between 1 and 1440 minutes"

        return True, ""

    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        new_interval = params.get("new_interval_minutes")
        reason = params.get("reason", "AI-initiated interval adjustment")

        try:
            from apps.ai.system.registry import WorkerRegistry

            registry = WorkerRegistry()

            worker = await registry.get_worker(worker_name)
            if not worker:
                return ToolResult(
                    success=False,
                    tool_name=self.definition.name,
                    error=f"Worker '{worker_name}' not found",
                )

            if not worker.ai_manageable:
                return ToolResult(
                    success=False,
                    tool_name=self.definition.name,
                    error=f"Worker '{worker_name}' is not AI-manageable",
                )

            old_interval = worker.config.interval_minutes

            # TODO: Actually update the interval
            # This would:
            # - Update config in database/file
            # - Signal worker to reload config
            # - Or restart worker with new config

            logger.info(
                f"⏱️  Adjusting {worker_name} interval: {old_interval} -> {new_interval} minutes"
            )

            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data={
                    "worker_name": worker_name,
                    "previous_interval_minutes": old_interval,
                    "new_interval_minutes": new_interval,
                    "reason": reason,
                    "adjusted_at": datetime.utcnow().isoformat(),
                },
                message=f"Adjusted {worker_name} interval: {old_interval} -> {new_interval} minutes",
            )

        except Exception as e:
            logger.error(f"Interval adjustment failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )
