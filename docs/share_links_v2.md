# Share Links API v2 Documentation

## Overview
The Share Links API v2 enables secure, time-limited sharing of analytics reports with rate limiting and access control. Share links provide a way to distribute analytics data to external stakeholders without requiring authentication.

## Features
- **Secure Token Generation**: Cryptographically secure 32-byte tokens
- **Time-Limited Access**: Configurable TTL (1 hour to 1 week)
- **Rate Limiting**: Token bucket algorithm with 429 responses
- **Multiple Formats**: CSV and PNG export support
- **Access Tracking**: Monitor link usage and access patterns
- **Graceful Expiration**: Automatic cleanup of expired links

## Base URL
```
/api/v2/share
```

## Rate Limits
- **Share Creation**: 5 per minute (burst of 10)
- **Share Access**: 60 per minute (burst of 120)
- **Rate Limiting**: Per client IP address with token bucket algorithm
- **429 Responses**: Include Retry-After header

## Endpoints

### 1. Create Share Link
**POST** `/create/{report_type}/{channel_id}`

Create a new shareable link for analytics data.

**Path Parameters:**
- `report_type` (required): Type of report - `overview`, `growth`, `reach`, `top_posts`, `sources`, `trending`
- `channel_id` (required): Target channel ID

**Query Parameters:**
- `period` (optional): Time period in days, 1-365, default 30
- `format` (optional): Export format - `csv` or `png`, default `csv`
- `ttl_hours` (optional): Time to live in hours, 1-168 (1 week), default 24

**Request Example:**
```
POST /api/v2/share/create/overview/123456789?period=30&format=csv&ttl_hours=48
```

**Response Example:**
```json
{
  "share_token": "h8k2n9p4q7s1t6v3x8z2a5c9f4g7j1m6n8p2r5u9w3y7",
  "share_url": "https://api.yourhost.com/api/v2/share/report/h8k2n9p4q7s1t6v3x8z2a5c9f4g7j1m6n8p2r5u9w3y7",
  "expires_at": "2024-02-02T15:30:00Z",
  "access_count": 0
}
```

### 2. Access Shared Report
**GET** `/report/{share_token}`

Access a shared report using the share token.

**Path Parameters:**
- `share_token` (required): The share token from create response

**Response:**
- **CSV Format**: Downloads CSV file with appropriate filename
- **PNG Format**: Downloads PNG image file

**Headers:**
- `Content-Disposition`: attachment with filename
- `Content-Type`: text/csv or image/png

**Error Responses:**
- `404`: Share link not found
- `410`: Share link has expired
- `429`: Rate limit exceeded

### 3. Get Share Information
**GET** `/info/{share_token}`

Get metadata about a share link without accessing the report.

**Path Parameters:**
- `share_token` (required): The share token

**Response Example:**
```json
{
  "report_type": "overview",
  "channel_id": "123456789", 
  "period": 30,
  "created_at": "2024-02-01T15:30:00Z",
  "expires_at": "2024-02-02T15:30:00Z",
  "access_count": 5,
  "format": "csv"
}
```

### 4. Revoke Share Link
**DELETE** `/revoke/{share_token}`

Revoke (delete) a share link before expiration.

**Path Parameters:**
- `share_token` (required): The share token to revoke

**Response Example:**
```json
{
  "message": "Share link revoked successfully"
}
```

### 5. Cleanup Expired Shares
**GET** `/cleanup`

Administrative endpoint to clean up expired share links.

**Response Example:**
```json
{
  "deleted_count": 23
}
```

## Rate Limiting Details

### Token Bucket Algorithm
- **Creation Bucket**: 10 token capacity, refills at 5 tokens/minute
- **Access Bucket**: 120 token capacity, refills at 60 tokens/minute
- **Per-IP Tracking**: Separate buckets for each client IP
- **IP Detection**: Supports X-Forwarded-For and X-Real-IP headers

### Rate Limit Headers
When rate limited (429), responses include:
```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
Content-Type: application/json

{
  "error": "rate_limit_exceeded", 
  "message": "Rate limit exceeded for share link creation",
  "retry_after": 12
}
```

### Background Cleanup
- **Bucket Cleanup**: Inactive IP buckets removed after 1 hour
- **Share Cleanup**: Expired share links cleaned up automatically
- **Cleanup Interval**: Every 5 minutes for optimal performance

## Security Considerations

### Token Security
- **Token Generation**: Uses `secrets.token_urlsafe(32)` for cryptographic security
- **Token Length**: 43 characters (32 bytes base64url encoded)
- **Entropy**: 256 bits of entropy per token
- **No Predictable Patterns**: Each token is completely random

### Access Control
- **Time-Limited**: All shares have mandatory expiration
- **Single-Use Optional**: Can be configured for one-time access
- **IP Logging**: Access attempts logged for security monitoring
- **Automatic Cleanup**: Expired shares removed automatically

### Data Protection
- **Fresh Data**: Reports generated on-demand, not cached
- **No Persistent Storage**: Report content not stored on server
- **Access Logging**: All access attempts logged with timestamps and IPs

## Error Handling

### Common Error Codes
- **400 Bad Request**: Invalid report type or parameters
- **403 Forbidden**: Share functionality disabled
- **404 Not Found**: Share token not found
- **410 Gone**: Share link has expired
- **429 Too Many Requests**: Rate limit exceeded
- **502 Bad Gateway**: Analytics service unavailable
- **503 Service Unavailable**: PNG rendering not available

### Error Response Format
```json
{
  "error": "error_code",
  "message": "Human readable error description",
  "details": {
    "field": "specific_field",
    "issue": "validation_error_detail"
  }
}
```

## Export Formats

### CSV Export
- **Filename Pattern**: `{report_type}_{channel_id}_{period}d_shared.csv`
- **Content-Type**: `text/csv`
- **Encoding**: UTF-8 with BOM for Excel compatibility
- **Structure**: Headers in first row, data in subsequent rows

#### CSV Structure Examples

**Overview Report:**
```csv
Metric,Value,Period
Posts,87,30 days
Views,542301,30 days
Average Reach,6232.07,30 days
ERR,4.20,30 days
Followers,15432,30 days
```

**Top Posts Report:**
```csv
Message ID,Date,Title,Views,Forwards,Replies,Reactions
1234,2024-01-15T10:30:00Z,Breaking: New tech...,25431,234,45,"{""👍"": 800, ""❤️"": 403}"
```

### PNG Export
- **Filename Pattern**: `{report_type}_{channel_id}_{period}d_shared.png`
- **Content-Type**: `image/png`
- **Size**: 1200x800 pixels optimized for web and print
- **Supported Reports**: growth, reach, sources (overview and top_posts not supported in PNG)

#### Chart Features
- **High DPI**: 150 DPI for crisp display and printing
- **Color Scheme**: Professional color palette with accessibility considerations
- **Branding**: Subtle watermark with generation timestamp
- **Responsive**: Optimized for various screen sizes

## Integration Examples

### Python Integration
```python
import requests
import time

# Create share link
response = requests.post(
    'https://api.yourhost.com/api/v2/share/create/overview/123456789',
    params={'period': 30, 'format': 'csv', 'ttl_hours': 24},
    headers={'Authorization': 'Bearer your-jwt-token'}
)

if response.status_code == 429:
    retry_after = int(response.headers['Retry-After'])
    print(f"Rate limited. Retry after {retry_after} seconds")
    time.sleep(retry_after)
else:
    share_data = response.json()
    print(f"Share URL: {share_data['share_url']}")
```

### JavaScript Integration
```javascript
async function createShareLink(reportType, channelId) {
  try {
    const response = await fetch(
      `/api/v2/share/create/${reportType}/${channelId}?period=30&format=csv`,
      {
        method: 'POST',
        headers: { 'Authorization': 'Bearer your-jwt-token' }
      }
    );
    
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      throw new Error(`Rate limited. Retry after ${retryAfter} seconds`);
    }
    
    const shareData = await response.json();
    return shareData.share_url;
    
  } catch (error) {
    console.error('Share link creation failed:', error);
    throw error;
  }
}
```

### cURL Examples
```bash
# Create share link
curl -X POST "https://api.yourhost.com/api/v2/share/create/overview/123456789?period=30&format=csv" \
  -H "Authorization: Bearer your-jwt-token"

# Access shared report
curl -o report.csv "https://api.yourhost.com/api/v2/share/report/h8k2n9p4q7s1t6v3x8z2a5c9f4g7j1m6n8p2r5u9w3y7"

# Get share info
curl "https://api.yourhost.com/api/v2/share/info/h8k2n9p4q7s1t6v3x8z2a5c9f4g7j1m6n8p2r5u9w3y7"
```

## Monitoring and Analytics

### Share Link Metrics
- **Creation Rate**: Share links created per hour/day
- **Access Patterns**: Most accessed report types and formats
- **Geographic Distribution**: Share access by region (IP-based)
- **Expiration Analysis**: Usage patterns before expiration
- **Error Rates**: Failed access attempts and reasons

### Performance Metrics
- **Response Times**: P50/P95/P99 latencies for creation and access
- **Rate Limit Efficiency**: Bucket utilization and overflow rates  
- **Cache Hit Rates**: Analytics data cache effectiveness
- **Export Generation**: Time to generate CSV/PNG exports

### Operational Metrics
- **Active Shares**: Currently valid share links
- **Storage Usage**: Database storage for share metadata
- **Cleanup Efficiency**: Expired share removal rates
- **Security Events**: Suspicious access patterns or abuse attempts

## Best Practices

### Share Link Creation
- **Appropriate TTL**: Set TTL based on actual sharing needs (shorter is more secure)
- **Minimal Data**: Share only necessary report types and time periods
- **Batch Operations**: Group related shares to avoid rate limits
- **Error Handling**: Always handle 429 responses with retry logic

### Security Best Practices
- **Token Handling**: Never log or expose share tokens in client-side code
- **Network Security**: Use HTTPS for all share link communications
- **Access Monitoring**: Monitor share link usage for unusual patterns
- **Regular Cleanup**: Implement regular cleanup of old shares (handled automatically)

### Performance Optimization
- **Format Selection**: Use CSV for data processing, PNG for presentations
- **Period Optimization**: Request appropriate time periods (avoid unnecessary large datasets)
- **Caching Awareness**: Understand that reports are generated fresh on each access
- **Rate Limit Management**: Implement exponential backoff for rate limit handling

## Migration and Updates

### Version Compatibility
- **API Version**: v2 is current stable version
- **Breaking Changes**: Any breaking changes will be announced 30 days in advance
- **Deprecation Policy**: Deprecated features supported for 6 months minimum

### Feature Roadmap
- **Additional Formats**: Excel (.xlsx) export support planned
- **Advanced Security**: Optional IP whitelisting for share access
- **Bulk Operations**: Bulk share creation and management APIs
- **Analytics Integration**: Embedded share widgets for third-party sites

## Support and Troubleshooting

### Common Issues
- **429 Rate Limits**: Implement proper retry logic with exponential backoff
- **Expired Shares**: Check expiration times and create new shares as needed
- **PNG Not Available**: Ensure matplotlib is installed for PNG rendering
- **Analytics Service Down**: Shares will fail if analytics service is unavailable

### Debugging Tools
- **Share Info Endpoint**: Use `/info/{token}` to check share status without consuming access
- **Rate Limit Headers**: Monitor rate limit consumption in response headers
- **Error Logs**: Check application logs for detailed error information
- **Health Checks**: Use `/health` endpoint to verify service status

### Contact and Support
- **API Issues**: Submit GitHub issues with share token (redacted) and error details
- **Performance Problems**: Include timing information and usage patterns
- **Security Concerns**: Report security issues privately to security team
- **Feature Requests**: Use GitHub discussions for new feature proposals
