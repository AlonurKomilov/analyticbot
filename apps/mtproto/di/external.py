"""
MTProto External Services Container
Focused on external integrations and monitoring
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.health_http import HealthCheckServer
from infra.common.faults import get_global_injector
from infra.common.ratelimit import RateLimitManager
from infra.obs.otel import MTProtoTracer, initialize_global_tracer


class ExternalContainer(containers.DeclarativeContainer):
    """Container for external services and integrations"""

    # Configuration
    settings = providers.Dependency(instance_of=MTProtoSettings)

    # Health and monitoring
    health_server = providers.Singleton(HealthCheckServer, settings=settings)

    tracer = providers.Singleton(MTProtoTracer, enabled=settings.provided.enable_tracing.as_(bool))

    # Rate limiting and fault injection
    rate_limiter = providers.Singleton(RateLimitManager, settings=settings)

    fault_injector = providers.Singleton(lambda: get_global_injector())

    # Global tracer initialization
    global_tracer = providers.Resource(initialize_global_tracer, settings=settings)
