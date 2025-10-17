"""
Core Analytics Services - Business Logic Layer
Modular analytics architecture with clean separation of concerns
"""

# Core modules
from core.services.bot.analytics.analytics_batch_processor import AnalyticsBatchProcessor
from core.services.bot.analytics.analytics_coordinator import (
    AnalyticsCoordinator,
    AnalyticsService,  # Backward compatibility alias
    create_analytics_coordinator,
)
from core.services.bot.analytics.cache_manager import (
    AnalyticsCacheManager,
    create_cache_manager,
)
from core.services.bot.analytics.data_aggregator import (
    AnalyticsDataAggregator,
    create_data_aggregator,
)
from core.services.bot.analytics.post_tracker import (
    AnalyticsPostTracker,
    create_post_tracker,
)
from core.services.bot.analytics.stream_processor import (
    AnalyticsStreamProcessor,
    create_stream_processor,
)

__all__ = [
    # Main coordinator (recommended API)
    "AnalyticsCoordinator",
    "AnalyticsService",  # Backward compatibility
    "create_analytics_coordinator",
    # Sub-modules (for advanced usage)
    "AnalyticsBatchProcessor",
    "AnalyticsStreamProcessor",
    "AnalyticsCacheManager",
    "AnalyticsDataAggregator",
    "AnalyticsPostTracker",
    # Factory functions
    "create_cache_manager",
    "create_data_aggregator",
    "create_post_tracker",
    "create_stream_processor",
]
