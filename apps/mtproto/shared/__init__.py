"""
Shared MTProto Resources - Common utilities for both system and user MTProto.

Contains:
- metrics.py: Prometheus metrics collection
- audit.py: Audit logging for MTProto events
"""

from apps.mtproto.shared.metrics import MTProtoMetrics, get_metrics
from apps.mtproto.shared.audit import log_mtproto_event

__all__ = [
    "MTProtoMetrics",
    "get_metrics",
    "log_mtproto_event",
]
