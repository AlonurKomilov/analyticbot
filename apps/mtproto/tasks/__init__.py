"""MTProto task scheduling scripts with feature flag safety.

This package contains both scheduled tasks and standalone scripts:
- sync_history.py: Sync channel history with repository storage
- poll_updates.py: Poll real-time updates with graceful shutdown
- StatsLoaderTask: Scheduled statistics loading (legacy)
- TaskScheduler: General task scheduling framework (legacy)

All tasks respect MTProto feature flags and provide safe fallback behavior.
"""

from .scheduler import TaskScheduler
from .stats_loader import StatsLoaderTask

__all__ = ["StatsLoaderTask", "TaskScheduler"]
