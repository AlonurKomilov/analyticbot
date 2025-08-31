# Analytics Fusion API v2 Documentation

## Overview
The Analytics Fusion API v2 provides a unified interface combining data from multiple sources:
- **MTProto Data**: Real-time Telegram data collection
- **Existing Analytics**: Historical metrics and processed insights
- **Performance-Optimized**: Redis caching and materialized views for sub-200ms responses

This API follows Clean Architecture principles with graceful degradation when data sources are unavailable.

## Authentication
All endpoints require valid JWT authentication via Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Base URL
```
/api/v2/analytics
```

## Endpoints

### 1. Overview Endpoint
**GET** `/overview?channel_id=<id>&days=<num>`

Provides comprehensive overview metrics combining multiple data sources.

**Parameters:**
- `channel_id` (required): Target channel ID
- `days` (optional): Time period, default 30 days

**Response Example:**
```json
{
  "channel_id": "@techchannel",
  "period": 30,
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-01-31T00:00:00Z",
  "overview": {
    "subscribers": 15432,
    "subscriber_growth": 234,
    "total_posts": 87,
    "total_views": 542301,
    "average_views_per_post": 6232,
    "engagement_rate": 4.2
  },
  "data_sources": ["mtproto", "existing_analytics"],
  "cache_hit": true,
  "last_updated": "2024-01-31T15:30:00Z"
}
```

### 2. Growth Metrics Endpoint
**GET** `/growth?channel_id=<id>&days=<num>`

Detailed growth analytics with time-series data.

**Parameters:**
- `channel_id` (required): Target channel ID
- `days` (optional): Time period, default 30 days

**Response Example:**
```json
{
  "channel_id": "@techchannel",
  "period": 30,
  "growth": {
    "subscriber_growth": 234,
    "growth_rate": 1.54,
    "daily_growth": [
      {"date": "2024-01-01", "subscribers": 15198, "change": 12},
      {"date": "2024-01-02", "subscribers": 15210, "change": 12}
    ]
  },
  "data_sources": ["mtproto"],
  "cache_hit": false,
  "last_updated": "2024-01-31T15:30:00Z"
}
```

### 3. Reach Analysis Endpoint
**GET** `/reach?channel_id=<id>&days=<num>`

Comprehensive reach metrics across different time periods.

**Parameters:**
- `channel_id` (required): Target channel ID
- `days` (optional): Time period, default 30 days

**Response Example:**
```json
{
  "channel_id": "@techchannel",
  "period": 30,
  "reach": {
    "total_views": 542301,
    "unique_viewers": 32145,
    "view_reach_ratio": 16.87,
    "peak_concurrent": 1234,
    "hourly_distribution": {
      "0": 45, "1": 23, "2": 18, ..., "23": 78
    }
  },
  "data_sources": ["mtproto", "existing_analytics"],
  "last_updated": "2024-01-31T15:30:00Z"
}
```

### 4. Top Posts Endpoint
**GET** `/top-posts?channel_id=<id>&days=<num>&limit=<num>`

Most engaging posts ranked by views and interactions.

**Parameters:**
- `channel_id` (required): Target channel ID
- `days` (optional): Time period, default 30 days
- `limit` (optional): Number of posts to return, default 10

**Response Example:**
```json
{
  "channel_id": "@techchannel",
  "period": 30,
  "top_posts": [
    {
      "post_id": 1234,
      "message": "Breaking: New tech announcement...",
      "views": 25431,
      "forwards": 234,
      "reactions": 1203,
      "engagement_score": 8.7,
      "published_at": "2024-01-15T10:30:00Z"
    }
  ],
  "data_sources": ["mtproto", "existing_analytics"],
  "last_updated": "2024-01-31T15:30:00Z"
}
```

### 5. Traffic Sources Endpoint
**GET** `/sources?channel_id=<id>&days=<num>`

Analysis of traffic sources and referral patterns.

**Parameters:**
- `channel_id` (required): Target channel ID
- `days` (optional): Time period, default 30 days

**Response Example:**
```json
{
  "channel_id": "@techchannel",
  "period": 30,
  "sources": {
    "direct": {"views": 234567, "percentage": 43.2},
    "forwards": {"views": 156789, "percentage": 28.9},
    "links": {"views": 89234, "percentage": 16.4},
    "search": {"views": 61711, "percentage": 11.4}
  },
  "referral_channels": [
    {"channel": "@referrer1", "views": 5432, "conversion_rate": 2.3}
  ],
  "data_sources": ["mtproto"],
  "last_updated": "2024-01-31T15:30:00Z"
}
```

### 6. Trending Analysis Endpoint
**GET** `/trending?channel_id=<id>&days=<num>`

Statistical trending analysis using Z-score and EWMA algorithms.

**Parameters:**
- `channel_id` (required): Target channel ID
- `days` (optional): Time period, default 30 days

**Response Example:**
```json
{
  "channel_id": "@techchannel",
  "period": 30,
  "trending": {
    "is_trending": true,
    "trend_score": 2.34,
    "trend_direction": "up",
    "z_score": 1.87,
    "ewma_score": 2.12,
    "confidence": "high",
    "analysis": "Channel showing strong upward trend with 2.3x above average engagement"
  },
  "data_sources": ["mtproto", "existing_analytics"],
  "last_updated": "2024-01-31T15:30:00Z"
}
```

## Data Provenance

### Data Sources
- **MTProto**: Real-time data from Telegram API
- **Existing Analytics**: Historical processed metrics
- **Cache Layer**: Redis for performance optimization

### Data Freshness
- **Real-time**: MTProto data updated every 5-15 minutes
- **Historical**: Daily aggregations updated overnight
- **Cache TTL**: 30-180 seconds based on endpoint complexity

### Graceful Degradation
When data sources are unavailable:
1. **MTProto Unavailable**: Falls back to existing analytics with note in `data_sources`
2. **Cache Miss**: Serves fresh data with `cache_hit: false`
3. **Partial Data**: Clearly indicates missing sources and impacts

## Performance Characteristics

### Response Times
- **Cached Responses**: < 50ms
- **Fresh Data**: < 200ms (with materialized views)
- **Complex Aggregations**: < 500ms

### Caching Strategy
- **Cache Keys**: Include channel_id, endpoint, parameters, and user permissions
- **Cache Invalidation**: Time-based TTL with manual invalidation for critical updates
- **Cache Headers**: ETag and Last-Modified for client-side caching

### Rate Limiting
- **Authenticated Users**: 100 requests/minute
- **Premium Users**: 300 requests/minute
- **Burst Allowance**: 2x rate for short periods

## Error Responses

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid channel_id format",
  "details": {"field": "channel_id", "issue": "must start with @ or be numeric"}
}
```

### 401 Unauthorized
```json
{
  "error": "authentication_required",
  "message": "Valid JWT token required"
}
```

### 403 Forbidden
```json
{
  "error": "insufficient_permissions",
  "message": "Access to this channel requires premium subscription"
}
```

### 404 Not Found
```json
{
  "error": "channel_not_found",
  "message": "Channel @nonexistent not found in our database"
}
```

### 503 Service Unavailable
```json
{
  "error": "data_source_unavailable",
  "message": "MTProto service temporarily unavailable, serving cached data",
  "fallback_active": true,
  "retry_after": 300
}
```

## Migration from v1

### Breaking Changes
- **Response Format**: All responses now include `data_sources` and `last_updated`
- **Authentication**: JWT required for all endpoints (v1 allowed some anonymous access)
- **Parameter Names**: Standardized to snake_case (e.g., `channelId` → `channel_id`)

### Compatibility Layer
V1 endpoints remain available with deprecation notices until 2024-12-31.

### Migration Guide
1. **Update Authentication**: Ensure all requests include valid JWT tokens
2. **Update Parameter Names**: Convert camelCase to snake_case
3. **Handle New Response Fields**: Process `data_sources` and caching metadata
4. **Error Handling**: Update to handle new structured error responses

## SDK Usage

### Python Example
```python
import requests

headers = {"Authorization": "Bearer your-jwt-token"}
response = requests.get(
    "http://api.yourhost.com/api/v2/analytics/overview",
    params={"channel_id": "@techchannel", "days": 30},
    headers=headers
)
data = response.json()
print(f"Views: {data['overview']['total_views']}")
```

### JavaScript Example
```javascript
const response = await fetch('/api/v2/analytics/overview?channel_id=@techchannel&days=30', {
  headers: { 'Authorization': 'Bearer your-jwt-token' }
});
const data = await response.json();
console.log(`Subscribers: ${data.overview.subscribers}`);
```

## Monitoring and Observability

### Metrics Available
- **Request Volume**: Requests per endpoint per minute
- **Response Times**: P50, P95, P99 latencies
- **Cache Hit Rates**: Per endpoint and overall
- **Data Source Availability**: MTProto and analytics service uptime
- **Error Rates**: By endpoint and error type

### Health Check
**GET** `/health` returns service status and data source availability.

## Support
For API support and feature requests:
- Documentation Issues: Create GitHub issue
- Integration Support: Contact development team
- Performance Issues: Check status page and monitoring dashboards
