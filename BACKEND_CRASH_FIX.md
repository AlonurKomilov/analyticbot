# Backend Crash Investigation & Fix Summary

## Problem Discovered

**Main Issue**: Backend API (uvicorn) was **crashing silently** causing all requests to timeout with 504 Gateway Timeout errors.

## Root Causes

### 1. Backend Crash - Telegram MTProto Rate Limiting
**Symptoms**:
- Nginx returning `504 Gateway Timeout` for all requests
- Backend process died but no obvious error
- Port 11400 not listening

**Root Cause**:
```
telethon.errors.common.InvalidBufferError: Invalid response buffer (HTTP code 429)
RpcError: Invalid msgs_ack query
```

**Analysis**:
- Telegram MTProto API is rate-limiting the application
- HTTP 429 (Too Many Requests) from Telegram
- Invalid buffer errors causing unhandled exceptions
- MTProto worker overwhelming Telegram's API limits

### 2. React Strict Mode - Duplicate API Calls (FIXED)
**Problem**: React Strict Mode in development causes components to mount twice
- Each page load = 2x API calls
- 2 simultaneous /channels requests × 30s timeout = frustrating UX

**Solution Applied**:
- Disabled `<React.StrictMode>` in development
- Kept it enabled in production for safety checks
- Location: `apps/frontend/src/main.tsx`

### 3. Invalid Refresh Token Handling (FIXED)
**Problem**: System tried to refresh tokens even when refresh_token was missing
- Missing refresh_token → 401 error → immediate logout

**Solution Applied**:
- Added check: Don't attempt refresh if no refresh_token exists
- Location: `apps/frontend/src/utils/tokenRefreshManager.ts`

## Solutions Implemented

### ✅ Immediate Fixes
1. **Restarted Backend API** - Port 11400 now listening and responding
2. **Disabled React Strict Mode in Dev** - No more duplicate requests
3. **Added Refresh Token Validation** - Won't try to refresh without token

### 🛠️ Monitoring Added
**Created API Watchdog Script**: `scripts/api-watchdog.sh`
- Checks every 30 seconds if backend is alive
- Auto-restarts if process dies
- Auto-restarts if port 11400 stops listening
- Logs all actions to `logs/watchdog.log`

**To start watchdog**:
```bash
nohup ./scripts/api-watchdog.sh > logs/watchdog.log 2>&1 &
```

### ⏳ Recommended Fixes (TODO)

#### 1. Rate Limit MTProto Requests
Add rate limiting to prevent Telegram API abuse:

```python
# In apps/mtproto/worker.py or equivalent
import asyncio
from datetime import datetime, timedelta

class TelegramRateLimiter:
    def __init__(self):
        self.requests = []
        self.max_requests_per_minute = 20  # Adjust based on Telegram limits

    async def wait_if_needed(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [req for req in self.requests if req > now - timedelta(minutes=1)]

        if len(self.requests) >= self.max_requests_per_minute:
            wait_time = (self.requests[0] + timedelta(minutes=1) - now).total_seconds()
            await asyncio.sleep(wait_time)

        self.requests.append(now)
```

#### 2. Add Exception Handling for MTProto
Wrap all Telegram client calls:

```python
try:
    result = await client.get_entity(channel_id)
except telethon.errors.common.InvalidBufferError as e:
    logger.warning(f"Telegram buffer error: {e}, retrying later...")
    # Don't crash - just skip and retry later
    return None
except telethon.errors.FloodWaitError as e:
    logger.warning(f"Rate limited by Telegram for {e.seconds}s")
    await asyncio.sleep(e.seconds)
    # Retry after wait
```

#### 3. Use Systemd for Production
Instead of manual processes, use systemd to auto-restart:

**File**: `/etc/systemd/system/analyticbot-api.service`
```ini
[Unit]
Description=AnalyticBot API Service
After=network.target postgresql.service

[Service]
Type=simple
User=abcdeveloper
WorkingDirectory=/home/abcdeveloper/projects/analyticbot
Environment="PATH=/home/abcdeveloper/projects/analyticbot/.venv/bin"
ExecStart=/home/abcdeveloper/projects/analyticbot/.venv/bin/uvicorn apps.api.main:app --host 0.0.0.0 --port 11400
Restart=always
RestartSec=10
StandardOutput=append:/home/abcdeveloper/projects/analyticbot/logs/api.log
StandardError=append:/home/abcdeveloper/projects/analyticbot/logs/api.error.log

[Install]
WantedBy=multi-user.target
```

Enable with:
```bash
sudo systemctl daemon-reload
sudo systemctl enable analyticbot-api
sudo systemctl start analyticbot-api
```

## Current Status

### ✅ Working
- Backend API responding on port 11400
- Nginx proxy forwarding requests correctly
- Frontend no longer makes duplicate requests
- Token refresh validation in place

### ⚠️ Known Issues
1. **MTProto Rate Limiting** - Will cause crashes again if not fixed
2. **No Auto-Restart** - Need to use watchdog or systemd
3. **Token Refresh Still Mentioned by User** - Need to verify actual behavior

## Testing Checklist

- [ ] Login and verify token stored correctly
- [ ] Refresh page - stay logged in
- [ ] Wait 8 hours - token should auto-refresh
- [ ] Try API request - should not see duplicate calls
- [ ] Monitor for 24 hours - backend should not crash

## Logs to Monitor

```bash
# Backend crashes
tail -f logs/dev_api.log | grep -E "Exception|Error|429"

# Frontend issues
tail -f logs/dev_frontend.log | grep -E "refresh|token|error"

# Watchdog activity
tail -f logs/watchdog.log

# Nginx errors
sudo tail -f /var/log/nginx/error.log
```

## Next Steps

1. **Start the watchdog** to prevent future crashes
2. **Implement MTProto rate limiting** to prevent Telegram bans
3. **Test token refresh** by waiting or manually triggering
4. **Consider systemd** for production deployment
5. **Monitor logs** for 24-48 hours to catch issues
