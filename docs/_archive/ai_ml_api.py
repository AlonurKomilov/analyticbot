"""Legacy shim module.

This file remains only to keep backward compatibility for imports expecting
`ai_ml_api:app` or symbols previously defined here. The implementation moved to
`apis.ai_ml_api`. All public names are re-exported.
"""

__all__ = [name for name in globals().keys() if not name.startswith("_")]
