"""
Compatibility Wrapper for apps.api.di_container.analytics_container
Redirects all calls to the new unified DI container

This file maintains backward compatibility while the codebase transitions
to the unified container pattern.
"""

import logging

from apps.shared.unified_di import get_container

logger = logging.getLogger(__name__)


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================


async def get_analytics_fusion_service():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return await container.analytics_fusion_service()


async def get_cache():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return container.cache_adapter  # Resource provider, not async


async def get_repository_factory():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return container.repository_factory()


async def get_channel_daily_repository():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return await container.channel_daily_repo()


async def get_post_repository():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return await container.post_repo()


async def get_metrics_repository():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return await container.metrics_repo()


async def get_edges_repository():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return await container.edges_repo()


async def get_stats_raw_repository():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return await container.stats_raw_repo()


async def get_channel_management_service():
    """Backward compatibility wrapper - redirects to unified container"""
    container = get_container()
    return container.channel_management_service()  # Factory provider


# Cleanup function
async def cleanup_analytics():
    """Cleanup function for graceful shutdown"""
    from apps.shared.unified_di import cleanup_container

    await cleanup_container()
    logger.info("Analytics dependencies cleaned up via unified container")
