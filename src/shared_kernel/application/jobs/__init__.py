"""
Background Jobs Package
======================
Background job processing functionality migrated from apps/jobs.

This package contains:
- Job definitions
- Task scheduling
- Background processing utilities
"""

# Import main job functionality
try:
    from .job_scheduler import *
except ImportError:
    pass

try:
    from .task_processor import *
except ImportError:
    pass

__version__ = "1.0.0"
