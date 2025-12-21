"""
System AI Tools Framework
=========================

Tools that the System AI can use for monitoring, scaling, and management.
Each tool follows a standard interface and can be invoked by the AI controller.
"""

from apps.ai.system.tools.base import (
    BaseTool, ToolResult, ToolRegistry, ToolDefinition,
    ToolCategory, ToolRiskLevel,
)
from apps.ai.system.tools.monitoring import (
    HealthCheckTool,
    MetricsCollectorTool,
    LogAnalyzerTool,
)
from apps.ai.system.tools.scaling import (
    ScaleWorkerTool,
    AdjustIntervalTool,
)
from apps.ai.system.tools.config import (
    GetConfigTool,
    UpdateConfigTool,
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
