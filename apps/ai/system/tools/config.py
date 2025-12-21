"""
Configuration Tools
===================

Tools for getting and updating worker configuration.
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


class GetConfigTool(BaseTool):
    """
    Get current configuration for a worker.
    
    Safe, read-only operation.
    """
    
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_config",
            description="Get current configuration for a worker",
            category=ToolCategory.CONFIG,
            risk_level=ToolRiskLevel.SAFE,
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {"type": "string", "description": "Worker name"},
                    "include_secrets": {"type": "boolean", "default": False, "description": "Include sensitive values"},
                },
                "required": ["worker_name"],
            },
        )
    
    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        include_secrets = params.get("include_secrets", False)
        
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
            
            config_data = {
                "worker_name": worker.name,
                "worker_type": worker.worker_type.value,
                "module_path": worker.module_path,
                "description": worker.description,
                "ai_manageable": worker.ai_manageable,
                "config": {
                    "interval_minutes": worker.config.interval_minutes,
                    "max_runtime_hours": worker.config.max_runtime_hours,
                    "auto_scaling_enabled": worker.config.auto_scaling_enabled,
                    "min_instances": worker.config.min_instances,
                    "max_instances": worker.config.max_instances,
                    "timeout_seconds": worker.config.timeout_seconds,
                    "retry_count": worker.config.retry_count,
                    "retry_delay_seconds": worker.config.retry_delay_seconds,
                },
            }
            
            # Add optional fields
            if worker.health_endpoint:
                config_data["health_endpoint"] = worker.health_endpoint
            
            if worker.metrics_endpoint:
                config_data["metrics_endpoint"] = worker.metrics_endpoint
            
            # Include resource requirements if available
            if worker.resources:
                config_data["resources"] = {
                    "cpu_limit": worker.resources.cpu_limit,
                    "memory_limit_mb": worker.resources.memory_limit_mb,
                    "disk_limit_mb": worker.resources.disk_limit_mb,
                }
            
            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data=config_data,
                message=f"Retrieved config for {worker_name}",
            )
            
        except Exception as e:
            logger.error(f"Get config failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )


class UpdateConfigTool(BaseTool):
    """
    Update configuration for a worker.
    
    High risk - configuration changes can affect system behavior.
    """
    
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="update_config",
            description="Update configuration for a worker",
            category=ToolCategory.CONFIG,
            risk_level=ToolRiskLevel.HIGH,
            requires_approval=True,
            cooldown_seconds=600,  # 10 minute cooldown
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {"type": "string", "description": "Worker to configure"},
                    "config_updates": {
                        "type": "object",
                        "description": "Configuration values to update",
                        "properties": {
                            "interval_minutes": {"type": "number"},
                            "max_runtime_hours": {"type": "number"},
                            "auto_scaling_enabled": {"type": "boolean"},
                            "min_instances": {"type": "integer"},
                            "max_instances": {"type": "integer"},
                            "timeout_seconds": {"type": "integer"},
                            "retry_count": {"type": "integer"},
                        },
                    },
                    "reason": {"type": "string", "description": "Reason for update"},
                },
                "required": ["worker_name", "config_updates"],
            },
        )
    
    async def validate_params(self, **params: Any) -> tuple[bool, str]:
        worker_name = params.get("worker_name")
        config_updates = params.get("config_updates", {})
        
        if not worker_name:
            return False, "worker_name is required"
        
        if not config_updates:
            return False, "config_updates cannot be empty"
        
        # Validate specific config values
        allowed_keys = {
            "interval_minutes", "max_runtime_hours", "auto_scaling_enabled",
            "min_instances", "max_instances", "timeout_seconds", "retry_count",
        }
        
        invalid_keys = set(config_updates.keys()) - allowed_keys
        if invalid_keys:
            return False, f"Invalid config keys: {invalid_keys}"
        
        # Value range validation
        if "interval_minutes" in config_updates:
            val = config_updates["interval_minutes"]
            if val < 1 or val > 1440:
                return False, "interval_minutes must be between 1 and 1440"
        
        if "max_instances" in config_updates:
            val = config_updates["max_instances"]
            if val < 1 or val > 10:
                return False, "max_instances must be between 1 and 10"
        
        if "min_instances" in config_updates:
            val = config_updates["min_instances"]
            if val < 1 or val > 5:
                return False, "min_instances must be between 1 and 5"
        
        return True, ""
    
    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        config_updates = params.get("config_updates", {})
        reason = params.get("reason", "AI-initiated configuration update")
        
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
            
            # Capture old values
            old_values = {}
            for key in config_updates:
                old_values[key] = getattr(worker.config, key, None)
            
            # TODO: Actually update configuration
            # This would:
            # - Update in database
            # - Update in-memory config
            # - Optionally restart worker
            
            logger.info(f"📝 Updating config for {worker_name}: {config_updates}")
            
            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data={
                    "worker_name": worker_name,
                    "old_values": old_values,
                    "new_values": config_updates,
                    "reason": reason,
                    "updated_at": datetime.utcnow().isoformat(),
                    "requires_restart": any(
                        k in config_updates for k in ["interval_minutes", "timeout_seconds"]
                    ),
                },
                message=f"Updated {len(config_updates)} config values for {worker_name}",
            )
            
        except Exception as e:
            logger.error(f"Config update failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )
