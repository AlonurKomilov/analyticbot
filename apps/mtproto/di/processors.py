"""
MTProto Data Processors Container
Focused on data processing and transformation services

✅ Phase 4 Note (Oct 19, 2025): Parser utilities
The infra.tg.parsers import is acceptable because:
1. Parser functions are pure utility functions (normalize_message, normalize_update)
2. They're MTProto-specific data transformations
3. No state, no complex dependencies - just data transformation
4. Creating a protocol for stateless utility functions adds no value
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.metrics import MTProtoMetrics

# MTProto-specific utility functions (acceptable - stateless data transformation)
from infra.tg.parsers import normalize_message, normalize_update


class ProcessorsContainer(containers.DeclarativeContainer):
    """Container for data processing services"""

    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)

    # Metrics and monitoring - disabled by default (can be enabled via OBS_PROMETHEUS_ENABLED env var)
    metrics = providers.Singleton(MTProtoMetrics, enabled=False)

    # Message processing services
    message_normalizer = providers.Factory(
        lambda: normalize_message  # Function wrapper
    )

    update_normalizer = providers.Factory(
        lambda: normalize_update  # Function wrapper
    )

    # Processing services would go here
    # message_processor = providers.Factory(MessageProcessor, ...)
    # stats_processor = providers.Factory(StatsProcessor, ...)
    # analytics_processor = providers.Factory(AnalyticsProcessor, ...)
