"""Legacy shim for standalone AI API.

Canonical implementation lives in `apis.standalone_ai_api`.
Kept only for backward compatibility with imports expecting `standalone_ai_api:app`.
Safe to remove after external references are updated.
"""

from apis.standalone_ai_api import *  # type: ignore F401,F403

__all__ = [name for name in globals().keys() if not name.startswith("_")]
