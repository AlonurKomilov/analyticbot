"""
Prometheus metrics for MTProto scaling and observability.
Provides comprehensive metrics for monitoring MTProto performance and health.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

try:
    from prometheus_client import (
        start_http_server, Counter, Gauge, Histogram, 
        CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create stub classes for when prometheus is not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def time(self): return self
        def labels(self, *args, **kwargs): return self
        def __enter__(self): return self
        def __exit__(self, *args): pass

logger = logging.getLogger(__name__)


class MTProtoMetrics:
    """Metrics collector for MTProto operations."""
    
    def __init__(self, enabled: bool = False, registry: Optional[Any] = None):
        self.enabled = enabled and PROMETHEUS_AVAILABLE
        self.registry = registry
        self._server_task: Optional[asyncio.Task] = None
        
        if not self.enabled:
            logger.warning("Prometheus metrics disabled (prometheus_client not available or disabled)")
            return
        
        # MTProto request metrics
        self.requests_total = Counter(
            'mtproto_requests_total',
            'Total MTProto requests',
            ['method', 'account', 'dc', 'status'],
            registry=registry
        )
        
        self.request_duration = Histogram(
            'mtproto_request_duration_seconds',
            'MTProto request duration',
            ['method', 'account', 'dc'],
            registry=registry
        )
        
        self.flood_wait_seconds = Histogram(
            'mtproto_flood_wait_seconds',
            'Flood wait durations',
            ['account', 'method'],
            buckets=(1, 5, 10, 30, 60, 300, 1800, 3600, float('inf')),
            registry=registry
        )
        
        # Account pool metrics
        self.pool_accounts_total = Gauge(
            'mtproto_pool_accounts_total',
            'Total accounts in pool',
            registry=registry
        )
        
        self.pool_accounts_healthy = Gauge(
            'mtproto_pool_accounts_healthy',
            'Healthy accounts in pool',
            registry=registry
        )
        
        self.pool_accounts_inflight = Gauge(
            'mtproto_pool_accounts_inflight_requests',
            'Inflight requests per account',
            ['account'],
            registry=registry
        )
        
        # Proxy pool metrics
        self.proxy_pool_total = Gauge(
            'mtproto_proxy_pool_total',
            'Total proxies in pool',
            registry=registry
        )
        
        self.proxy_pool_healthy = Gauge(
            'mtproto_proxy_pool_healthy',
            'Healthy proxies in pool',
            registry=registry
        )
        
        self.proxy_rotation_total = Counter(
            'mtproto_proxy_rotations_total',
            'Total proxy rotations',
            ['reason'],
            registry=registry
        )
        
        # Queue and batch metrics
        self.queue_depth = Gauge(
            'mtproto_queue_depth',
            'Current queue depth',
            ['task_type'],
            registry=registry
        )
        
        self.batch_duration = Histogram(
            'mtproto_batch_duration_seconds',
            'Batch processing duration',
            ['task_type', 'status'],
            registry=registry
        )
        
        self.batch_size = Histogram(
            'mtproto_batch_size',
            'Batch size processed',
            ['task_type'],
            buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000, float('inf')),
            registry=registry
        )
        
        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            'mtproto_rate_limit_hits_total',
            'Rate limit hits',
            ['limiter_type', 'account'],
            registry=registry
        )
        
        self.rate_limit_tokens = Gauge(
            'mtproto_rate_limit_tokens',
            'Available tokens in rate limiter',
            ['limiter_type', 'account'],
            registry=registry
        )
        
        # Database operation metrics
        self.db_operations = Counter(
            'mtproto_db_operations_total',
            'Database operations',
            ['operation', 'table', 'status'],
            registry=registry
        )
        
        self.db_operation_duration = Histogram(
            'mtproto_db_operation_duration_seconds',
            'Database operation duration',
            ['operation', 'table'],
            registry=registry
        )
        
        # Collector-specific metrics
        self.messages_collected = Counter(
            'mtproto_messages_collected_total',
            'Messages collected from channels',
            ['channel', 'collector_type'],
            registry=registry
        )
        
        self.channel_sync_duration = Histogram(
            'mtproto_channel_sync_duration_seconds',
            'Channel synchronization duration',
            ['channel', 'sync_type'],
            registry=registry
        )
        
        # Health and error metrics
        self.component_health = Gauge(
            'mtproto_component_health',
            'Component health status (1=healthy, 0=unhealthy)',
            ['component'],
            registry=registry
        )
        
        self.errors_total = Counter(
            'mtproto_errors_total',
            'Total errors by type',
            ['error_type', 'component'],
            registry=registry
        )
        
        logger.info("MTProto metrics initialized successfully")
    
    async def start_server(self, port: int = 9108) -> None:
        """Start Prometheus metrics HTTP server."""
        if not self.enabled:
            logger.info("Prometheus metrics server not started (disabled)")
            return
        
        try:
            start_http_server(port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")
            raise
    
    def record_request(self, method: str, account: str, dc: str, status: str, 
                      duration: Optional[float] = None) -> None:
        """Record MTProto request metrics."""
        if not self.enabled:
            return
        
        self.requests_total.labels(method=method, account=account, dc=dc, status=status).inc()
        
        if duration is not None:
            self.request_duration.labels(method=method, account=account, dc=dc).observe(duration)
    
    def record_flood_wait(self, account: str, method: str, duration: float) -> None:
        """Record flood wait event."""
        if not self.enabled:
            return
        
        self.flood_wait_seconds.labels(account=account, method=method).observe(duration)
    
    def update_pool_metrics(self, stats: Dict[str, Any]) -> None:
        """Update account pool metrics."""
        if not self.enabled:
            return
        
        self.pool_accounts_total.set(stats.get('total_accounts', 0))
        
        status_counts = stats.get('status_counts', {})
        healthy_count = status_counts.get('healthy', 0)
        self.pool_accounts_healthy.set(healthy_count)
        
        # Update per-account inflight requests
        for account_info in stats.get('accounts', []):
            account_name = account_info.get('name', 'unknown')
            inflight = account_info.get('inflight', 0)
            self.pool_accounts_inflight.labels(account=account_name).set(inflight)
    
    def update_proxy_metrics(self, stats: Dict[str, Any]) -> None:
        """Update proxy pool metrics."""
        if not self.enabled:
            return
        
        self.proxy_pool_total.set(stats.get('total_proxies', 0))
        
        status_counts = stats.get('status_counts', {})
        healthy_count = status_counts.get('healthy', 0)
        self.proxy_pool_healthy.set(healthy_count)
    
    def record_proxy_rotation(self, reason: str = 'scheduled') -> None:
        """Record proxy rotation event."""
        if not self.enabled:
            return
        
        self.proxy_rotation_total.labels(reason=reason).inc()
    
    def update_queue_depth(self, task_type: str, depth: int) -> None:
        """Update queue depth metric."""
        if not self.enabled:
            return
        
        self.queue_depth.labels(task_type=task_type).set(depth)
    
    @asynccontextmanager
    async def time_batch(self, task_type: str, status: str = 'success'):
        """Context manager to time batch operations."""
        if not self.enabled:
            yield
            return
        
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.batch_duration.labels(task_type=task_type, status=status).observe(duration)
    
    def record_batch_size(self, task_type: str, size: int) -> None:
        """Record batch size."""
        if not self.enabled:
            return
        
        self.batch_size.labels(task_type=task_type).observe(size)
    
    def record_rate_limit_hit(self, limiter_type: str, account: str) -> None:
        """Record rate limit hit."""
        if not self.enabled:
            return
        
        self.rate_limit_hits.labels(limiter_type=limiter_type, account=account).inc()
    
    def update_rate_limit_tokens(self, limiter_type: str, account: str, tokens: float) -> None:
        """Update available rate limit tokens."""
        if not self.enabled:
            return
        
        self.rate_limit_tokens.labels(limiter_type=limiter_type, account=account).set(tokens)
    
    def record_db_operation(self, operation: str, table: str, status: str, 
                           duration: Optional[float] = None) -> None:
        """Record database operation."""
        if not self.enabled:
            return
        
        self.db_operations.labels(operation=operation, table=table, status=status).inc()
        
        if duration is not None:
            self.db_operation_duration.labels(operation=operation, table=table).observe(duration)
    
    def record_messages_collected(self, channel: str, collector_type: str, count: int) -> None:
        """Record messages collected."""
        if not self.enabled:
            return
        
        self.messages_collected.labels(channel=channel, collector_type=collector_type).inc(count)
    
    @asynccontextmanager
    async def time_channel_sync(self, channel: str, sync_type: str):
        """Context manager to time channel sync operations."""
        if not self.enabled:
            yield
            return
        
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.channel_sync_duration.labels(channel=channel, sync_type=sync_type).observe(duration)
    
    def set_component_health(self, component: str, healthy: bool) -> None:
        """Set component health status."""
        if not self.enabled:
            return
        
        self.component_health.labels(component=component).set(1.0 if healthy else 0.0)
    
    def record_error(self, error_type: str, component: str) -> None:
        """Record error by type."""
        if not self.enabled:
            return
        
        self.errors_total.labels(error_type=error_type, component=component).inc()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics (for debugging)."""
        if not self.enabled:
            return {"enabled": False, "message": "Prometheus metrics disabled"}
        
        # This would typically scrape current metric values
        # For now, return basic status
        return {
            "enabled": True,
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "registry": str(type(self.registry)) if self.registry else "default"
        }


# Global metrics instance
_metrics: Optional[MTProtoMetrics] = None


def get_metrics() -> MTProtoMetrics:
    """Get global metrics instance."""
    global _metrics
    if _metrics is None:
        _metrics = MTProtoMetrics(enabled=False)
    return _metrics


def initialize_metrics(enabled: bool = False, port: int = 9108, registry: Optional[Any] = None) -> MTProtoMetrics:
    """Initialize global metrics instance."""
    global _metrics
    _metrics = MTProtoMetrics(enabled=enabled, registry=registry)
    
    if enabled and PROMETHEUS_AVAILABLE:
        # Start metrics server in background
        asyncio.create_task(_metrics.start_server(port))
    
    return _metrics