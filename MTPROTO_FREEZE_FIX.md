# MTProto Backend Freeze - Emergency Fix

## Critical Issue Discovered

**Backend API was completely frozen** due to Telegram MTProto rate limiting causing unhandled exceptions that locked the asyncio event loop.

## Symptoms

1. ✅ Login works fine - tokens received
2. ❌ `/channels` endpoint times out after 30 seconds
3. ❌ ALL endpoints timeout (health, login OPTIONS, etc.)
4. ❌ Backend process running but not responding
5. ❌ Nginx logs: `upstream timed out (110: Connection timed out)`

## Root Cause

```python
[ERROR] asyncio: Future exception was never retrieved
future: <Future finished exception=InvalidBufferError('Invalid response buffer (HTTP code 429)')>
telethon.errors.common.InvalidBufferError: Invalid response buffer (HTTP code 429)
```

**Analysis:**
- Telegram API rate limiting (HTTP 429 - Too Many Requests)
- MTProto worker makes too many requests
- Unhandled `InvalidBufferError` exception
- Asyncio event loop gets stuck waiting for failed futures
- **Entire backend freezes** - no requests processed

## Emergency Fix Applied

### ✅ Temporarily Disabled MTProto Service

**File**: `apps/api/main.py` (line 81-103)

**What Changed:**
- Commented out MTProto initialization
- Added warning log: `⚠️ MTProto service disabled temporarily`
- Backend now starts without Telegram client

**Impact:**
- ✅ Backend responds immediately
- ✅ All endpoints working (login, channels, health)
- ❌ Cannot fetch full channel history from Telegram (using database only)
- ❌ Cannot add new channels via MTProto

### ✅ Restarted Backend

```bash
pkill -9 -f uvicorn
nohup .venv/bin/uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --reload > logs/dev_api.log 2>&1 &
```

## Current Status

### ✅ Working Now
- Backend responding in <3ms
- Login endpoint working
- Channels endpoint working (returns database data)
- No timeouts
- No freezes

### ❌ Limitations
- Cannot fetch data from Telegram directly
- Channel discovery disabled
- Historical data collection paused

## Permanent Fix Required

### 1. Add Rate Limiting to MTProto Worker

**Create**: `apps/mtproto/rate_limiter.py`

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List

class TelegramRateLimiter:
    """
    Rate limiter for Telegram API to prevent 429 errors

    Telegram limits:
    - ~20 requests per second per session
    - ~300 requests per minute
    - Stricter limits for channels API
    """

    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}
        self.max_requests_per_second = 10  # Conservative limit
        self.max_requests_per_minute = 200

    async def acquire(self, session_id: str = "default"):
        """Wait if needed before making request"""
        now = datetime.now()

        if session_id not in self.requests:
            self.requests[session_id] = []

        # Clean old requests
        self.requests[session_id] = [
            req for req in self.requests[session_id]
            if req > now - timedelta(minutes=1)
        ]

        # Check per-second limit
        recent_requests = [
            req for req in self.requests[session_id]
            if req > now - timedelta(seconds=1)
        ]

        if len(recent_requests) >= self.max_requests_per_second:
            wait_time = 1.0 - (now - recent_requests[0]).total_seconds()
            await asyncio.sleep(wait_time)

        # Check per-minute limit
        if len(self.requests[session_id]) >= self.max_requests_per_minute:
            wait_time = (
                self.requests[session_id][0] + timedelta(minutes=1) - now
            ).total_seconds()
            await asyncio.sleep(wait_time)

        # Record request
        self.requests[session_id].append(datetime.now())

# Global instance
_rate_limiter = TelegramRateLimiter()

async def wait_for_rate_limit(session_id: str = "default"):
    """Convenience function"""
    await _rate_limiter.acquire(session_id)
```

### 2. Wrap All MTProto Calls

**Modify**: `apps/mtproto/multi_tenant/user_mtproto_service.py`

```python
from apps.mtproto.rate_limiter import wait_for_rate_limit
from telethon.errors import FloodWaitError, InvalidBufferError

async def safe_telegram_request(client, operation, *args, **kwargs):
    """
    Wrapper for all Telegram requests with error handling
    """
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Wait for rate limiter
            await wait_for_rate_limit(str(client.session.id))

            # Perform operation
            return await operation(*args, **kwargs)

        except FloodWaitError as e:
            logger.warning(f"Telegram flood wait: {e.seconds}s")
            await asyncio.sleep(e.seconds + 1)
            retry_count += 1

        except InvalidBufferError as e:
            logger.error(f"Telegram buffer error (likely rate limit): {e}")
            if "429" in str(e):
                # Exponential backoff
                wait_time = 60 * (2 ** retry_count)
                logger.warning(f"Rate limited, waiting {wait_time}s")
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                raise

        except Exception as e:
            logger.error(f"Telegram request failed: {e}")
            if retry_count < max_retries - 1:
                await asyncio.sleep(5)
                retry_count += 1
            else:
                raise

    raise Exception(f"Failed after {max_retries} retries")

# Usage example:
# result = await safe_telegram_request(client, client.get_entity, channel_id)
```

### 3. Add Circuit Breaker Pattern

```python
class MTProtoCircuitBreaker:
    """
    Circuit breaker to stop making requests if Telegram is rejecting them
    """

    def __init__(self, failure_threshold=5, timeout=300):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"🚨 Circuit breaker OPEN - too many Telegram failures")

    def can_make_request(self) -> bool:
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if timeout passed
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
                self.failure_count = 0
                return True
            return False

        return True  # HALF_OPEN - try again
```

### 4. Graceful Degradation

Ensure endpoints work even without MTProto:

```python
@router.get("/channels")
async def get_channels(user_id: str):
    channels = await db.get_channels(user_id)

    # Try MTProto only if circuit is closed
    if mtproto_available and circuit_breaker.can_make_request():
        try:
            fresh_data = await fetch_from_telegram(channels)
            return fresh_data
        except Exception as e:
            logger.warning(f"MTProto unavailable, using cached data: {e}")
            circuit_breaker.record_failure()

    # Return database data (graceful degradation)
    return channels
```

## How to Re-enable MTProto

### Step 1: Implement Rate Limiting
```bash
# Create the rate limiter
nano apps/mtproto/rate_limiter.py
# Paste the code above
```

### Step 2: Update MTProto Service
```bash
# Wrap all Telegram calls with safe_telegram_request
nano apps/mtproto/multi_tenant/user_mtproto_service.py
```

### Step 3: Test Carefully
```bash
# Start with rate limiter enabled
# Monitor logs: tail -f logs/dev_api.log | grep "rate\|429\|Flood"
```

### Step 4: Uncomment in main.py
Once tested, uncomment lines 81-103 in `apps/api/main.py`

## Monitoring

Watch for these signs:
```bash
# Check for rate limit errors
tail -f logs/dev_api.log | grep -E "429|FloodWaitError|InvalidBufferError"

# Check backend responsiveness
watch -n 5 'curl -s -w "Time: %{time_total}s\n" http://localhost:11400/health'

# Check if backend is frozen (should be < 0.01s)
time curl -s http://localhost:11400/health > /dev/null
```

## Prevention Checklist

- [ ] Implement TelegramRateLimiter class
- [ ] Wrap all MTProto calls with safe_telegram_request
- [ ] Add circuit breaker pattern
- [ ] Test with small user base first
- [ ] Monitor for 24 hours before enabling for all users
- [ ] Set up alerts for 429 errors
- [ ] Document Telegram API limits

## Notes

- MTProto is currently DISABLED - this is temporary
- All endpoints working normally without it
- Channel data comes from database cache
- Need proper rate limiting before re-enabling
- This is an emergency fix, not a permanent solution
