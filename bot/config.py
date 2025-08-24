"""
DEPRECATED: Legacy config module - Use config.settings instead

This stub remains for backward compatibility (legacy imports: `from bot.config import settings`).
For new code, import directly from the centralized config module:
    from config import settings

This file will be removed in a future version.
"""

import os

# Re-export from centralized config for backward compatibility
from config.settings import Settings as _Settings

# Create a legacy-compatible settings instance
settings = _Settings()

# Ensure backward compatibility for class access
Settings = type(settings)

__all__ = ["settings", "Settings"]

