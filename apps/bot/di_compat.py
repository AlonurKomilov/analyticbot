"""
Compatibility Wrapper for apps.bot.di
Redirects all calls to the new unified DI container

This file maintains backward compatibility while the codebase transitions
to the unified container pattern.
"""

import logging

from apps.shared.unified_di import get_container as get_unified_container
from dependency_injector import containers

logger = logging.getLogger(__name__)


# ============================================================================
# BACKWARD COMPATIBILITY: BotContainer class
# ============================================================================


class BotContainer(containers.DeclarativeContainer):
    """
    Backward compatibility wrapper for BotContainer
    Redirects to unified container
    """

    pass  # Empty - all functionality in unified container


def configure_bot_container():
    """Configure and return the unified container (backward compatibility)"""
    logger.info("Using unified DI container (via bot compatibility wrapper)")
    return get_unified_container()


def get_container():
    """Get the configured container instance (backward compatibility)"""
    return get_unified_container()
