"""
AI System Module
================

Infrastructure-level AI for:
- Worker management (MTProto, Bot, API, Celery)
- Auto-scaling and resource optimization
- Health monitoring and auto-healing
- Pattern detection and alerting
- Configured via environment variables
- Admin-only access

Usage:
    from apps.ai.system import SystemAIController, get_system_ai_config

    config = get_system_ai_config()
    controller = SystemAIController(config)
    await controller.start()

Phase 2 Components:
    from apps.ai.system.tools import HealthCheckTool, ToolRegistry
    from apps.ai.system.memory import MetricsStore, PatternDetector, AlertManager
"""

from apps.ai.system.config import (
    AIApprovalMode,
    SystemAIConfig,
    get_system_ai_config,
    reload_system_ai_config,
)
from apps.ai.system.controller import SystemAIController

# Phase 2: Memory & Monitoring
from apps.ai.system.memory import (
    AIAlert,
    AlertManager,
    DetectedPattern,
    MemoryEntry,
    MemoryStore,
    MetricDataPoint,
    MetricsStore,
    PatternDetector,
    get_alert_manager,
    get_memory_store,
    get_metrics_store,
    get_pattern_detector,
)

# Phase 2: Tools
from apps.ai.system.tools import (
    AdjustIntervalTool,
    BaseTool,
    GetConfigTool,
    HealthCheckTool,
    LogAnalyzerTool,
    MetricsCollectorTool,
    ScaleWorkerTool,
    ToolRegistry,
    ToolResult,
    UpdateConfigTool,
)

__all__ = [
    # Core
    "SystemAIController",
    "SystemAIConfig",
    "AIApprovalMode",
    "get_system_ai_config",
    "reload_system_ai_config",
    # Tools
    "BaseTool",
    "ToolResult",
    "ToolRegistry",
    "HealthCheckTool",
    "MetricsCollectorTool",
    "LogAnalyzerTool",
    "ScaleWorkerTool",
    "AdjustIntervalTool",
    "GetConfigTool",
    "UpdateConfigTool",
    # Memory
    "MemoryStore",
    "MemoryEntry",
    "get_memory_store",
    # Metrics
    "MetricsStore",
    "MetricDataPoint",
    "get_metrics_store",
    # Patterns
    "PatternDetector",
    "DetectedPattern",
    "get_pattern_detector",
    # Alerts
    "AlertManager",
    "AIAlert",
    "get_alert_manager",
]
