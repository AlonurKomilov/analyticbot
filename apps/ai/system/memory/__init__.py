"""
Memory Module - AI State and Learning Persistence
=================================================

Handles:
- Decision history tracking
- Metrics time series storage
- Pattern storage and retrieval
- State persistence across restarts
- Alert generation and management
"""

from apps.ai.system.memory.store import MemoryStore, MemoryEntry, MemoryType, get_memory_store
from apps.ai.system.memory.metrics import MetricsStore, MetricDataPoint, get_metrics_store
from apps.ai.system.memory.patterns import (
    PatternDetector, DetectedPattern, PatternType, PatternSeverity, get_pattern_detector
)
from apps.ai.system.memory.alerting import AlertManager, AIAlert, AlertChannel, get_alert_manager

__all__ = [
    # Memory store
    "MemoryStore",
    "MemoryEntry",
    "MemoryType",
    "get_memory_store",
    # Metrics store
    "MetricsStore",
    "MetricDataPoint",
    "get_metrics_store",
    # Pattern detection
    "PatternDetector",
    "DetectedPattern",
    "PatternType",
    "PatternSeverity",
    "get_pattern_detector",
    # Alerting
    "AlertManager",
    "AIAlert",
    "AlertChannel",
    "get_alert_manager",
]
