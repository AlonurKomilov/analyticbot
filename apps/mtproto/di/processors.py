"""
MTProto Data Processors Container
Focused on data processing and transformation services
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.metrics import MTProtoMetrics
from infra.tg.parsers import normalize_message, normalize_update


class ProcessorsContainer(containers.DeclarativeContainer):
    """Container for data processing services"""

    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)

    # Metrics and monitoring
    metrics = providers.Singleton(
        MTProtoMetrics, enabled=settings.provided.enable_metrics.as_(bool)
    )

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
