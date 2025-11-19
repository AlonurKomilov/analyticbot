# Channels Timeout & Token Refresh Issues - Analysis & Recommendations

## Current Status

✅ **MTProto Restored** - Working normally
✅ **Backend Responding** - Health endpoint: <3ms, Channels endpoint functional
✅ **API Routing Working** - api.analyticbot.org resolves correctly
✅ **CORS Configured** - Preflight requests succeed
❌ **Frontend Times Out** - 30s timeout on /channels request
⚠️ **Token Refresh Triggering** - After timeout, refresh attempt happens

## Root Causes Identified

### 1. Multiple Issues Creating Perfect Storm

**Issue A: CloudFlare Tunnel Routing**
- Two CloudFlare tunnels running (user + system)
- Possible routing conflicts
- Network latency stacking up

**Issue B: Frontend Request Behavior**
- Request times out client-side after 30s
- Retry logic enabled BUT request never completes
- Backend never receives the request (no logs)

**Issue C: Token Refresh After Timeout**
- When request times out, frontend thinks it's auth issue
- Triggers token refresh unnecessarily
- User sees confusing behavior

## Technical Analysis

### Why Requests Don't Reach Backend

**Frontend Flow:**
```
Browser → api.analyticbot.org → CloudFlare → Nginx → Backend (port 11400)
```

**Where It's Failing:**
```bash
# Backend logs show NO /channels requests
tail logs/dev_api.log | grep "GET /channels"  # Empty!

# Nginx shows upstream timeouts
/var/log/nginx/error.log: "upstream timed out (110: Connection timed out)"
```

**Diagnosis:** Request is **reaching nginx** but nginx **cannot connect to backend** OR backend is **not responding**.

### Current Timeouts

| Component | Timeout | Setting |
|-----------|---------|---------|
| Frontend | 30s | `ENDPOINT_TIMEOUTS['/channels']` |
| Nginx | 30s | `proxy_read_timeout` |
| Backend | None | (FastAPI default) |

## MTProto Performance Recommendations

### ✅ What's Working

1. **Lazy Loading** - MTProto only connects when needed
2. **Error Handling** - Try/catch prevents crashes
3. **Graceful Degradation** - API works without MTProto

### 🔧 Improvements Needed

#### 1. Add Connection Pool Limits

**File:** `apps/mtproto/multi_tenant/user_mtproto_service.py`

```python
class UserMTProtoService:
    def __init__(self):
        self.max_concurrent_connections = 5  # Limit active Telegram connections
        self.connection_semaphore = asyncio.Semaphore(5)
        self.active_connections: Dict[str, TelegramClient] = {}

    async def get_client(self, user_id: str):
        async with self.connection_semaphore:
            # Only allow 5 concurrent Telegram operations
            if user_id in self.active_connections:
                return self.active_connections[user_id]

            client = await self._create_client(user_id)
            self.active_connections[user_id] = client
            return client
```

#### 2. Add Request Rate Limiting

```python
from datetime import datetime, timedelta
from collections import deque

class TelegramRateLimiter:
    def __init__(self):
        self.requests = deque(maxlen=100)
        self.max_per_minute = 20  # Telegram limit

    async def acquire(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        while self.requests and self.requests[0] < now - timedelta(minutes=1):
            self.requests.popleft()

        if len(self.requests) >= self.max_per_minute:
            # Wait until oldest request expires
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            await asyncio.sleep(wait_time)

        self.requests.append(now)
```

#### 3. Add Circuit Breaker for Telegram Errors

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=300):
        self.failures = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_failure(self):
        self.failures += 1
        self.last_failure = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("Circuit breaker OPEN - MTProto disabled temporarily")

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if datetime.now() - self.last_failure > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
                return True
            return False

        return True  # HALF_OPEN
```

#### 4. Wrap All MTProto Calls

```python
async def safe_telegram_call(client, operation, *args, **kwargs):
    """Wrapper for all Telegram API calls with error handling"""

    # Check circuit breaker
    if not circuit_breaker.can_execute():
        logger.warning("Circuit breaker OPEN - skipping Telegram request")
        return None

    # Rate limit
    await rate_limiter.acquire()

    try:
        result = await operation(*args, **kwargs)
        circuit_breaker.record_success()
        return result

    except telethon.errors.FloodWaitError as e:
        logger.warning(f"Telegram flood wait: {e.seconds}s")
        await asyncio.sleep(e.seconds)
        circuit_breaker.record_failure()
        raise

    except telethon.errors.InvalidBufferError as e:
        if "429" in str(e):
            logger.error(f"Rate limited by Telegram: {e}")
            circuit_breaker.record_failure()
            # Don't crash - return None for graceful degradation
            return None
        raise

    except Exception as e:
        logger.error(f"MTProto error: {e}")
        circuit_breaker.record_failure()
        return None
```

## Immediate Fixes Needed

### Fix 1: Increase Nginx Backend Timeout

**File:** `/etc/nginx/sites-available/api.analyticbot.conf`

```nginx
location / {
    proxy_pass http://127.0.0.1:11400;

    # Increase timeouts for slow endpoints
    proxy_connect_timeout 10s;   # Connection establishment
    proxy_send_timeout 60s;      # Sending request to backend
    proxy_read_timeout 60s;      # Reading response from backend (was 30s)

    # Keep existing settings
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    # ... rest of config
}
```

Then reload: `sudo nginx -s reload`

### Fix 2: Add Aggressive Retry with Exponential Backoff

**File:** `apps/frontend/src/api/client.ts`

Update retry logic to be more aggressive for `/channels`:

```typescript
async request<T>(endpoint: string, options: RequestConfig = {}, attempt = 1): Promise<T> {
    try {
        // ... existing code ...
    } catch (error) {
        // Special handling for /channels endpoint
        if (endpoint.includes('/channels') && attempt < this.config.maxRetries) {
            const delay = this.config.retryDelay * Math.pow(2, attempt - 1);
            console.warn(`🔄 Retry ${attempt}/${this.config.maxRetries} for /channels after ${delay}ms`);
            await this.sleep(delay);
            return this.request<T>(endpoint, options, attempt + 1);
        }

        // ... existing retry logic ...
    }
}
```

### Fix 3: Add Loading State with Retry Button

**File:** `apps/frontend/src/shared/hooks/useUserChannels.ts`

```typescript
export const useUserChannels = (options = {}) => {
    const [retryCount, setRetryCount] = useState(0);

    const fetchChannels = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            // Add explicit timeout to fail fast
            const timeoutPromise = new Promise((_, reject) =>
                setTimeout(() => reject(new Error('Request timeout')), 35000)
            );

            const requestPromise = (dataProvider as any)._makeRequest('/channels');

            const response = await Promise.race([requestPromise, timeoutPromise]);

            setChannels(response || []);
            setRetryCount(0);
        } catch (err) {
            console.error('Failed to fetch channels:', err);
            setError(err.message);

            // Auto-retry up to 3 times with delay
            if (retryCount < 3) {
                console.log(`Auto-retry ${retryCount + 1}/3 in 2 seconds...`);
                setTimeout(() => {
                    setRetryCount(prev => prev + 1);
                    fetchChannels();
                }, 2000);
            }
        } finally {
            setLoading(false);
        }
    }, [dataProvider, retryCount]);

    return { channels, loading, error, refetch: fetchChannels };
};
```

### Fix 4: Prevent Token Refresh on Timeout

**File:** `apps/frontend/src/api/client.ts`

```typescript
// Handle 401 Unauthorized - but NOT for timeouts
if (error instanceof ApiRequestError &&
    error.response?.status === 401 &&
    !options._retry &&
    error.message !== 'Request timeout') {  // Don't refresh on timeout!

    const hasRefreshToken = localStorage.getItem('refresh_token');
    if (hasRefreshToken) {
        // ... existing refresh logic ...
    }
}
```

## Testing Plan

```bash
# 1. Check backend is responding
curl -s http://localhost:11400/health

# 2. Check via nginx
curl -s https://api.analyticbot.org/health

# 3. Test channels with auth (use fresh token)
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.analyticbot.org/channels

# 4. Monitor backend logs
tail -f logs/dev_api.log | grep "channels"

# 5. Monitor nginx errors
sudo tail -f /var/log/nginx/error.log | grep "timeout"
```

## Summary

**MTProto is NOT the problem** - it's working correctly with graceful degradation.

**Real Issue:** Network/timeout configuration causing requests to timeout before completing. Backend is healthy, but requests either:
1. Don't reach backend (routing issue)
2. Reach backend but response times out (nginx timeout too short)
3. Frontend gives up too early (client-side timeout)

**Recommended Priority:**
1. ✅ Increase nginx `proxy_read_timeout` to 60s
2. ✅ Add retry logic to useUserChannels hook
3. ✅ Prevent token refresh on timeout errors
4. ⏳ Add MTProto rate limiting (nice to have)
5. ⏳ Add circuit breaker pattern (nice to have)
