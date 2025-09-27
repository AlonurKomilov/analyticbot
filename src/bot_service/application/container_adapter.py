"""
Bot Container Compatibility Adapter
===================================
Maintains backward compatibility for existing apps.bot.container imports.
Redirects to unified container while preserving the existing interface.
"""

from ..migration_bridge.unified_container import get_container

# Import original container functionality if it exists
try:
    from .original_container import *  # Import existing functionality
except ImportError:
    # If original container doesn't exist, create minimal interface
    pass


def get_bot_container():
    """Get container with bot-specific services"""
    unified = get_container()
    return unified


def init_bot_services(unified_container):
    """Initialize bot-specific services in unified container"""
    # This would register bot-specific service implementations
    # For now, it's a placeholder


# Maintain backward compatibility
container = get_bot_container()

# Export commonly used functions
__all__ = ["container", "get_bot_container", "init_bot_services"]
