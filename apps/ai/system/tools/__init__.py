"""
System AI Tools Framework
=========================

Tools that the System AI can use for monitoring, scaling, and management.
Each tool follows a standard interface and can be invoked by the AI controller.
"""

from apps.ai.system.tools.base import (
    BaseTool,
    ToolCategory,
    ToolDefinition,
    ToolRegistry,
    ToolResult,
    ToolRiskLevel,
)
from apps.ai.system.tools.config import (
    GetConfigTool,
    UpdateConfigTool,
)
from apps.ai.system.tools.monitoring import (
    HealthCheckTool,
    LogAnalyzerTool,
    MetricsCollectorTool,
)
from apps.ai.system.tools.scaling import (
    AdjustIntervalTool,
    ScaleWorkerTool,
)

__all__ = [
    # Base
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "ToolDefinition",
    "ToolCategory",
    "ToolRiskLevel",
    # Monitoring
    "HealthCheckTool",
    "MetricsCollectorTool",
    "LogAnalyzerTool",
    # Scaling
    "ScaleWorkerTool",
    "AdjustIntervalTool",
    # Config
    "GetConfigTool",
    "UpdateConfigTool",
]
