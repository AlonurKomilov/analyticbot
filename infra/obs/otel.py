"""
OpenTelemetry integration for MTProto distributed tracing.
Provides optional OTEL tracing with graceful fallback when unavailable.
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

# Try to import OpenTelemetry components
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

    # Create stub classes for when OTEL is not available
    class MockTracer:
        def start_span(self, name: str, **kwargs):
            return MockSpan()

        def start_as_current_span(self, name: str, **kwargs):
            return MockSpanContext()

    class MockSpan:
        def set_attribute(self, key: str, value: Any):
            pass

        def set_status(self, status):
            pass

        def record_exception(self, exception):
            pass

        def end(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class MockSpanContext:
        def __enter__(self):
            return MockSpan()

        def __exit__(self, *args):
            pass


logger = logging.getLogger(__name__)


class MTProtoTracer:
    """MTProto-specific tracer with optional OTEL integration."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled and OTEL_AVAILABLE
        self.tracer: Any = None

        if not self.enabled:
            logger.info("OpenTelemetry tracing disabled (not available or disabled)")
            self.tracer = MockTracer()

    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Any:
        """Start a new span."""
        span = self.tracer.start_span(name)

        if attributes and self.enabled:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

        return span

    @contextmanager
    def trace_operation(self, operation: str, **attributes) -> Generator[Any, None, None]:
        """Context manager for tracing operations."""
        span = self.start_span(f"mtproto.{operation}", attributes)
        try:
            yield span
        except Exception as e:
            if self.enabled:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
        finally:
            span.end()

    @contextmanager
    def trace_request(self, method: str, account: str, dc: str) -> Generator[Any, None, None]:
        """Context manager for tracing MTProto requests."""
        attributes = {
            "mtproto.method": method,
            "mtproto.account": account,
            "mtproto.dc": dc,
        }

        with self.trace_operation(f"request.{method}", **attributes) as span:
            yield span

    @contextmanager
    def trace_db_operation(self, operation: str, table: str) -> Generator[Any, None, None]:
        """Context manager for tracing database operations."""
        attributes = {"db.operation": operation, "db.table": table}

        with self.trace_operation(f"db.{operation}", **attributes) as span:
            yield span

    @contextmanager
    def trace_collector(self, collector_type: str, channel: str) -> Generator[Any, None, None]:
        """Context manager for tracing collector operations."""
        attributes = {"collector.type": collector_type, "collector.channel": channel}

        with self.trace_operation(f"collector.{collector_type}", **attributes) as span:
            yield span


def setup_tracing(
    endpoint: str | None = None,
    sampling_ratio: float = 0.05,
    service_name: str = "mtproto",
    service_version: str = "1.0.0",
) -> MTProtoTracer | None:
    """
    Set up OpenTelemetry tracing.

    Args:
        endpoint: OTLP endpoint (e.g., http://jaeger:14268/api/traces)
        sampling_ratio: Trace sampling ratio (0.05 = 5%)
        service_name: Service name for traces
        service_version: Service version

    Returns:
        MTProtoTracer instance or None if setup failed
    """
    if not OTEL_AVAILABLE:
        logger.warning("OpenTelemetry not available, tracing disabled")
        return MTProtoTracer(enabled=False)

    if not endpoint:
        logger.info("No OTEL endpoint configured, tracing disabled")
        return MTProtoTracer(enabled=False)

    try:
        # Create resource with service information
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": service_version,
                "service.namespace": "analytics",
            }
        )

        # Create tracer provider with sampling
        provider = TracerProvider(resource=resource, sampler=TraceIdRatioBased(sampling_ratio))

        # Create OTLP exporter
        exporter = OTLPSpanExporter(endpoint=endpoint)

        # Create batch span processor
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Create MTProto tracer
        tracer_instance = MTProtoTracer(enabled=True)
        tracer_instance.tracer = trace.get_tracer(service_name, service_version)

        # Instrument HTTP requests and database queries
        try:
            RequestsInstrumentor().instrument()
            AsyncPGInstrumentor().instrument()
            logger.info("HTTP and database instrumentation enabled")
        except Exception as e:
            logger.warning(f"Failed to enable auto-instrumentation: {e}")

        logger.info(
            f"OpenTelemetry tracing initialized: endpoint={endpoint}, "
            f"sampling={sampling_ratio}, service={service_name}"
        )

        return tracer_instance

    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry tracing: {e}")
        return MTProtoTracer(enabled=False)


def get_tracer() -> MTProtoTracer:
    """Get a tracer instance (stub if OTEL not available)."""
    return MTProtoTracer(enabled=False)


# Convenience functions for common tracing patterns
def trace_mtproto_call(method: str, account: str, dc: str):
    """Decorator for tracing MTProto calls."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.trace_request(method, account, dc):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def trace_db_operation(operation: str, table: str):
    """Decorator for tracing database operations."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.trace_db_operation(operation, table):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def trace_collector_operation(collector_type: str, channel: str):
    """Decorator for tracing collector operations."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.trace_collector(collector_type, channel):
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global tracer instance
_global_tracer: MTProtoTracer | None = None


def initialize_global_tracer(
    endpoint: str | None = None,
    sampling_ratio: float = 0.05,
    service_name: str = "mtproto",
) -> MTProtoTracer:
    """Initialize global tracer instance."""
    global _global_tracer
    _global_tracer = setup_tracing(endpoint, sampling_ratio, service_name)
    return _global_tracer


def get_global_tracer() -> MTProtoTracer:
    """Get global tracer instance."""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = MTProtoTracer(enabled=False)
    return _global_tracer
