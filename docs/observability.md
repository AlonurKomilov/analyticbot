# Observability and Monitoring Documentation

## Overview
Comprehensive observability stack for AnalyticBot providing monitoring, logging, metrics, and alerting across all system components.

## Architecture

### Observability Stack
- **Metrics Collection**: Prometheus + custom metrics
- **Logging**: Structured logging with JSON format
- **Tracing**: Request tracing for API calls
- **Health Checks**: Multi-layer health monitoring
- **Alerting**: Automated alerts for critical issues

### Data Flow
```
Application → Metrics → Prometheus → Grafana → Alerts
            ↓
         Logs → Structured JSON → Log Aggregation → Search
            ↓
        Traces → Request Context → Distributed Tracing
```

## Metrics Collection

### System Metrics
- **CPU Usage**: Per-service CPU utilization
- **Memory Usage**: RSS, heap, and swap usage
- **Disk I/O**: Read/write operations and throughput
- **Network I/O**: Inbound/outbound traffic per service

### Application Metrics
- **Request Metrics**: Request count, duration, status codes
- **Database Metrics**: Query count, duration, connection pool usage
- **Cache Metrics**: Hit/miss rates, eviction counts, memory usage
- **Task Metrics**: Task execution time, success/failure rates

### Business Metrics
- **User Activity**: Active users, session duration, feature usage
- **API Usage**: Endpoint usage patterns, rate limit violations
- **Share Links**: Creation/access rates, expiration patterns
- **Analytics Processing**: Data processing latency, error rates

### Custom Metrics Configuration
```python
# Example: Custom metric for trending analysis
from prometheus_client import Counter, Histogram, Gauge

trending_requests = Counter(
    'trending_analysis_requests_total',
    'Total trending analysis requests',
    ['method', 'status']
)

trending_duration = Histogram(
    'trending_analysis_duration_seconds',
    'Time spent on trending analysis',
    ['method']
)

cache_hit_ratio = Gauge(
    'analytics_cache_hit_ratio',
    'Cache hit ratio for analytics endpoints'
)
```

## Logging Strategy

### Log Levels
- **ERROR**: System errors requiring immediate attention
- **WARNING**: Issues that might need attention but don't stop operation
- **INFO**: Important system events and state changes
- **DEBUG**: Detailed information for troubleshooting

### Structured Logging Format
```json
{
  "timestamp": "2024-02-01T15:30:45.123Z",
  "level": "INFO",
  "service": "analytics-api",
  "component": "share_links",
  "message": "Share link created successfully",
  "context": {
    "share_token": "abc123...",
    "channel_id": "123456789",
    "format": "csv",
    "ttl_hours": 24,
    "client_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "request_id": "req-uuid-123",
    "duration_ms": 45
  },
  "metadata": {
    "hostname": "analytics-01",
    "process_id": 1234,
    "thread_id": 5678
  }
}
```

### Log Aggregation
- **Centralized Collection**: All logs sent to central logging service
- **Retention Policy**: Logs kept for 30 days (configurable)
- **Search and Filtering**: Full-text search across all log fields
- **Real-time Monitoring**: Stream processing for immediate alerts

### Key Logging Points
```python
# Example: Comprehensive logging for share link operations
logger.info(
    "Share link creation started",
    extra={
        "event": "share_creation_start",
        "channel_id": channel_id,
        "report_type": report_type,
        "client_ip": client_ip,
        "request_id": request_id
    }
)

logger.info(
    "Rate limit check passed",
    extra={
        "event": "rate_limit_check",
        "client_ip": client_ip,
        "bucket_tokens_remaining": bucket.tokens,
        "request_id": request_id
    }
)

logger.error(
    "Analytics service unavailable",
    extra={
        "event": "service_error",
        "service": "analytics",
        "error": str(e),
        "retry_count": retry_count,
        "request_id": request_id
    }
)
```

## Health Monitoring

### Health Check Levels

#### 1. Basic Health Check
**GET** `/health`
```json
{
  "status": "healthy",
  "timestamp": "2024-02-01T15:30:00Z",
  "version": "7.5.0",
  "uptime_seconds": 86400
}
```

#### 2. Detailed Health Check
**GET** `/health/detailed`
```json
{
  "status": "healthy",
  "timestamp": "2024-02-01T15:30:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "latency_ms": 5,
      "connections_active": 8,
      "connections_max": 20
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1,
      "memory_used_mb": 256,
      "memory_max_mb": 512
    },
    "analytics_service": {
      "status": "degraded",
      "latency_ms": 1200,
      "last_success": "2024-02-01T15:25:00Z",
      "error_rate": 0.05
    }
  },
  "feature_flags": {
    "share_links_enabled": true,
    "mtproto_enabled": true,
    "analytics_cache_enabled": true
  }
}
```

#### 3. Ready/Live Checks
**GET** `/ready` - Service ready to accept traffic
**GET** `/live` - Service is running (for Kubernetes)

### Health Check Implementation
```python
class HealthChecker:
    def __init__(self):
        self.checks = {
            "database": self._check_database,
            "redis": self._check_redis,
            "analytics_service": self._check_analytics_service
        }

    async def check_health(self, detailed=False):
        results = {}
        overall_status = "healthy"

        for name, check_func in self.checks.items():
            try:
                result = await asyncio.wait_for(check_func(), timeout=5.0)
                results[name] = result

                if result["status"] not in ["healthy", "degraded"]:
                    overall_status = "unhealthy"
                elif result["status"] == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"

            except asyncio.TimeoutError:
                results[name] = {"status": "timeout", "error": "Health check timeout"}
                overall_status = "unhealthy"
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
                overall_status = "unhealthy"

        return {
            "status": overall_status,
            "services": results if detailed else None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
```

## Performance Monitoring

### Response Time Monitoring
- **API Endpoints**: P50, P95, P99 latencies per endpoint
- **Database Queries**: Slow query detection (>100ms)
- **Cache Operations**: Redis operation latencies
- **External Services**: Third-party service response times

### Throughput Monitoring
- **Request Rate**: Requests per second per endpoint
- **Error Rate**: Error percentage by endpoint and type
- **Concurrency**: Active connections and requests
- **Queue Depth**: Background task queue sizes

### Resource Utilization
```python
# Example: Resource monitoring middleware
async def monitor_resources(request, call_next):
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss

    response = await call_next(request)

    duration = time.time() - start_time
    memory_delta = psutil.Process().memory_info().rss - start_memory

    # Record metrics
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).observe(duration)

    memory_usage.labels(
        endpoint=request.url.path
    ).observe(memory_delta)

    return response
```

## Error Tracking

### Error Classification
- **Critical**: System failures affecting all users
- **High**: Feature failures affecting multiple users
- **Medium**: Individual request failures
- **Low**: Expected errors (validation, rate limits)

### Error Context Collection
```python
def capture_error_context(error, request=None):
    context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc(),
        "timestamp": datetime.utcnow().isoformat(),
        "service": "analytics-api",
        "version": app_version
    }

    if request:
        context.update({
            "request_id": getattr(request.state, 'request_id', None),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": get_client_ip(request)
        })

    return context
```

### Error Rate Monitoring
- **Overall Error Rate**: Percentage of failed requests
- **Error Rate by Endpoint**: Per-endpoint error tracking
- **Error Rate by Client**: Identify problematic clients
- **Error Trends**: Error rate changes over time

## Rate Limiting Observability

### Rate Limit Metrics
```python
# Rate limiting metrics
rate_limit_exceeded = Counter(
    'rate_limit_exceeded_total',
    'Rate limit exceeded events',
    ['client_type', 'endpoint']
)

rate_limit_bucket_utilization = Histogram(
    'rate_limit_bucket_utilization',
    'Token bucket utilization percentage',
    ['client_ip', 'bucket_type']
)

rate_limit_retry_after = Histogram(
    'rate_limit_retry_after_seconds',
    'Retry-after time provided to clients',
    ['bucket_type']
)
```

### Rate Limit Dashboard
- **Current Bucket States**: Active buckets and token levels
- **Rate Limit Events**: 429 responses over time
- **Client Patterns**: Most rate-limited IPs and patterns
- **Bucket Cleanup**: Automatic cleanup effectiveness

## Caching Observability

### Cache Performance Metrics
```python
cache_operations = Counter(
    'cache_operations_total',
    'Cache operations count',
    ['operation', 'cache_type', 'status']
)

cache_latency = Histogram(
    'cache_operation_duration_seconds',
    'Cache operation duration',
    ['operation', 'cache_type']
)

cache_hit_ratio = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio',
    ['cache_type', 'endpoint']
)
```

### ETag Cache Monitoring
- **ETag Generation Time**: Time to compute SHA1 ETags
- **304 Response Rate**: Percentage of 304 Not Modified responses
- **ETag Cache Effectiveness**: Bandwidth saved through 304s
- **Client Cache Behavior**: ETag usage patterns

## Alerting Strategy

### Alert Severity Levels
- **P0 (Critical)**: System down, immediate response required
- **P1 (High)**: Significant degradation, response within 1 hour
- **P2 (Medium)**: Moderate issues, response within 4 hours
- **P3 (Low)**: Minor issues, response within 24 hours

### Critical Alerts
```yaml
# Example Prometheus alerting rules
groups:
  - name: analyticbot.critical
    rules:
      - alert: ServiceDown
        expr: up{service="analytics-api"} == 0
        for: 30s
        labels:
          severity: P0
        annotations:
          summary: "Analytics API service is down"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: P1
        annotations:
          summary: "High error rate detected: {{ $value }}%"

      - alert: DatabaseConnections
        expr: db_connections_active / db_connections_max > 0.9
        for: 1m
        labels:
          severity: P1
        annotations:
          summary: "Database connection pool near capacity"
```

### Performance Alerts
```yaml
  - name: analyticbot.performance
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: P2
        annotations:
          summary: "95th percentile latency above 500ms"

      - alert: CacheHitRateDecline
        expr: cache_hit_ratio < 0.7
        for: 10m
        labels:
          severity: P2
        annotations:
          summary: "Cache hit rate below 70%"
```

## Dashboards

### System Overview Dashboard
- **Service Status**: Health check status for all services
- **Request Volume**: Total requests per minute across all endpoints
- **Error Rate**: Overall error percentage
- **Response Time**: P95 latency trends
- **Resource Usage**: CPU, memory, disk usage per service

### API Performance Dashboard
- **Endpoint Performance**: Latency and throughput per endpoint
- **Rate Limiting**: Rate limit events and client patterns
- **Caching**: Cache hit rates and ETag effectiveness
- **Share Links**: Creation/access patterns and usage metrics

### Business Metrics Dashboard
- **User Activity**: Active users and session patterns
- **Feature Usage**: Most used analytics endpoints
- **Share Link Analytics**: Popular report types and formats
- **Trending Analysis**: Z-score and EWMA algorithm performance

### Infrastructure Dashboard
- **Database Performance**: Query performance, connection usage
- **Redis Performance**: Cache performance, memory usage
- **Background Tasks**: Task queue depth, processing rates
- **Network**: Inbound/outbound traffic patterns

## Troubleshooting Guides

### Common Issues

#### High Response Times
1. **Check Database**: Query performance and connection pool
2. **Check Cache**: Hit rates and Redis performance
3. **Check External Services**: Analytics service latency
4. **Check Resource Usage**: CPU/memory constraints

#### Rate Limiting Issues
1. **Identify Patterns**: Most rate-limited IPs and endpoints
2. **Bucket Analysis**: Token bucket utilization patterns
3. **Client Behavior**: Legitimate vs. abusive traffic
4. **Configuration Review**: Rate limit settings appropriateness

#### Cache Performance Issues
1. **Hit Rate Analysis**: Cache effectiveness per endpoint
2. **ETag Generation**: SHA1 computation performance
3. **Client Behavior**: If-None-Match header usage
4. **Invalidation Patterns**: Cache invalidation effectiveness

### Debug Tools

#### Log Analysis Queries
```bash
# Find all errors in the last hour
grep '"level":"ERROR"' /var/log/app.log | grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')"

# Rate limiting events by IP
grep '"event":"rate_limit_exceeded"' /var/log/app.log | jq -r '.context.client_ip' | sort | uniq -c

# Slow requests (>1s)
grep '"duration_ms"' /var/log/app.log | jq 'select(.context.duration_ms > 1000)'
```

#### Metrics Queries
```promql
# 95th percentile response time by endpoint
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
) by (endpoint)

# Cache hit ratio trend
rate(cache_operations_total{status="hit"}[5m]) /
rate(cache_operations_total[5m])

# Rate limit events per minute
rate(rate_limit_exceeded_total[1m]) * 60
```

## Configuration

### Environment Variables
```bash
# Observability Configuration
LOG_LEVEL=INFO
LOG_FORMAT=structured
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# Error Tracking
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production
SENTRY_SAMPLE_RATE=0.1

# Alerting
ALERT_WEBHOOK_URL=https://your-alert-webhook
ALERT_CHANNELS=["#alerts", "#on-call"]
```

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'analyticbot'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

## Best Practices

### Monitoring Best Practices
- **Golden Signals**: Monitor latency, traffic, errors, saturation
- **Service Level Objectives**: Define and track SLOs for critical services
- **Alert Fatigue**: Avoid too many low-priority alerts
- **Dashboard Design**: Focus on actionable metrics

### Logging Best Practices
- **Structured Logging**: Always use structured JSON format
- **Context Enrichment**: Include request IDs and user context
- **Sensitive Data**: Never log passwords, tokens, or PII
- **Performance**: Async logging to avoid blocking requests

### Performance Monitoring
- **Baseline Establishment**: Know normal performance characteristics
- **Percentile Tracking**: Focus on P95/P99 rather than averages
- **Resource Correlation**: Correlate performance with resource usage
- **Continuous Improvement**: Regular performance review cycles

## Maintenance and Updates

### Regular Maintenance
- **Log Rotation**: Automatic log rotation and cleanup
- **Metric Retention**: Configure appropriate metric retention policies
- **Dashboard Updates**: Keep dashboards current with new features
- **Alert Tuning**: Regular review and tuning of alert thresholds

### Capacity Planning
- **Growth Projections**: Monitor growth trends for capacity planning
- **Resource Forecasting**: Predict resource needs based on usage patterns
- **Scaling Triggers**: Define automatic scaling thresholds
- **Performance Testing**: Regular load testing to validate capacity

This observability strategy provides comprehensive monitoring and alerting for all aspects of the AnalyticBot system, enabling proactive issue detection and resolution.
