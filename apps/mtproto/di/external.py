"""
MTProto External Services Container
Focused on external integrations and monitoring

✅ Phase 4 Note (Oct 19, 2025): Cross-cutting concerns
The infra imports here are acceptable because they represent cross-cutting concerns:
1. Observability (tracing, metrics) - infra.obs.otel
2. Resilience patterns (rate limiting, fault injection) - infra.common
3. These are infrastructure-level concerns that span all layers
4. They don't represent business logic dependencies
5. Cross-cutting concerns are allowed to be used throughout the application

This is consistent with Clean Architecture - cross-cutting concerns like
logging, monitoring, and resilience are infrastructure that all layers can use.
"""

from dependency_injector import containers, providers

from apps.mtproto.config import MTProtoSettings
from apps.mtproto.health_http import HealthCheckServer

# Cross-cutting concerns (acceptable - observability & resilience patterns)
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
