"""Legacy shim for standalone performance API.

Canonical implementation lives in `apis.standalone_performance_api`.
Kept only for backward compatibility with imports expecting `standalone_performance_api:app`.
Safe to remove after external references are updated.
"""

from apps.api.standalone_performance_api import *

__all__ = [name for name in globals().keys() if not name.startswith("_")]
