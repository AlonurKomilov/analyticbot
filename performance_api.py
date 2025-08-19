"""Legacy shim for performance monitoring API.

Implementation lives in `apis.performance_api`.
This module exists only for backward compatibility with legacy imports
(`performance_api:app`). Remove once all references are migrated.
"""

from apis.performance_api import *  # type: ignore F401,F403

__all__ = [name for name in globals().keys() if not name.startswith("_")]
