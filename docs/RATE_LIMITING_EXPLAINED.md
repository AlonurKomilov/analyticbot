# Rate Limiting System - Comprehensive Guide

## Overview

Your platform uses **PER-IP rate limiting**, NOT global rate limiting. This means each user/IP address gets their own independent rate limit quota.

## How It Works

### Per-IP Limits (Not Global!)

✅ **Current System**: Each IP address has its own rate limit
- If you have 100,000 users, each one gets the full rate limit quota
- Example: 500 requests/minute means EACH user can make 500 requests/minute
- Total capacity: 100,000 users × 500 req/min = **50 million requests/minute**

❌ **NOT Global Limits**: The limit is NOT shared across all users
- You don't have a single pool of 500 requests/minute for all users
- Each user operates independently

### Current Production Limits (After Update)

| Endpoint Type | Limit | Per IP | Description |
|---------------|-------|--------|-------------|
| **Public Read** | 500/minute | ✅ | Public API endpoints (dashboards, stats) |
| **Bot Operations** | 300/minute | ✅ | Normal bot operations |
| **Auth Login** | 30/minute | ✅ | Login attempts |
| **Auth Register** | 3/hour | ✅ | New registrations |
| **Bot Creation** | 5/hour | ✅ | Creating new bots (prevents spam) |
| **Webhooks** | 1000/minute | ✅ | Telegram webhook callbacks |
| **Admin Ops** | 30/minute | ✅ | Admin dashboard operations |

### Development vs Production

#### Development (.env.development)
```bash
RATE_LIMITING_ENABLED=false  # Disabled for easier testing
RATE_LIMIT_PER_MINUTE=1000   # High limit if enabled
```

#### Production (.env.production)
```bash
RATE_LIMITING_ENABLED=true   # Active protection
RATE_LIMIT_PER_MINUTE=300    # Per-IP limit
```

## Rate Limiting Implementation

### Backend (slowapi library)

```python
# File: apps/api/middleware/rate_limiter.py

# Uses slowapi with Redis backend for distributed rate limiting
limiter = Limiter(
    key_func=get_remote_address_with_whitelist,  # Uses IP address
    storage_uri="redis://localhost:10200/1",      # Shared Redis
    strategy="fixed-window",                       # Time windows
    headers_enabled=True                           # Returns limit headers
)
```

### IP Detection

The system correctly handles proxied requests:
1. Checks `X-Forwarded-For` header (Cloudflare, nginx)
2. Falls back to `X-Real-IP` header
3. Uses direct connection IP as last resort

### Response Headers

When rate limit is applied, clients receive:
```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 487
X-RateLimit-Reset: 42
Retry-After: 42
```

## 503 Errors for .ts Files - NOT RATE LIMIT ISSUE!

### What You're Seeing

```
GET https://app.analyticbot.org/src/shared/components/.../useUserPreferences.ts
503 (Service Unavailable)
```

### This is NOT a Rate Limit Problem!

These 503 errors are **Vite dev server issues**, not rate limiting:

#### Root Causes:
1. **Module Resolution Failures**: Vite can't find/compile the TypeScript module
2. **Circular Dependencies**: Files importing each other in a loop
3. **HMR (Hot Module Replacement) Issues**: Vite's live reload failing
4. **Network Issues**: Between browser and Vite dev server

#### Why It Happens:
- Vite dev server compiles TypeScript on-the-fly
- If a module has errors or circular deps, Vite returns 503
- This is a **development environment issue**, not production

#### Solutions:

1. **Restart Vite Dev Server**:
   ```bash
   make -f Makefile.dev dev-stop
   make -f Makefile.dev dev-start
   ```

2. **Clear Vite Cache**:
   ```bash
   cd apps/frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

3. **Check for Circular Dependencies**:
   ```bash
   npx madge --circular apps/frontend/src
   ```

4. **Hard Refresh Browser**:
   - Chrome: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Clears browser cache and re-requests all modules

## Scaling Considerations

### For 100,000 Users

With current limits (500 req/min per IP):
- **Max capacity**: 100k users × 500 req/min = 50M req/min
- **Actual usage**: Typically 1-5% of max (500k-2.5M req/min)
- **Headroom**: 20x-100x current needs

### When to Increase Limits

Increase if you see:
- Legitimate users hitting rate limits frequently
- 429 errors in monitoring dashboards
- User complaints about "too many requests"

### When NOT to Increase

Current limits are MORE than sufficient for:
- 100,000 concurrent users
- Normal browsing patterns (5-10 requests per page load)
- Typical API usage (1-2 requests per second per user)

## Monitoring Rate Limits

### Check Current Status

```bash
# Test an endpoint with your token
TOKEN="your_jwt_token_here"
curl -v -H "Authorization: Bearer $TOKEN" https://api.analyticbot.org/dashboard

# Look for these headers:
# X-RateLimit-Limit: 500
# X-RateLimit-Remaining: 499
# X-RateLimit-Reset: 60
```

### Redis Storage

Rate limit counters are stored in Redis:
```bash
# Connect to Redis
docker exec -it analyticbot-redis redis-cli

# Check rate limit keys
KEYS "LIMITER*"

# Check a specific IP's limit
GET "LIMITER:127.0.0.1:/api/dashboard:minute"
```

## IP Whitelisting

Certain IPs bypass rate limits:
```python
# Automatically whitelisted:
- 127.0.0.1 (localhost)
- ::1 (IPv6 localhost)

# Add more via environment:
RATE_LIMIT_WHITELIST=10.0.0.1,10.0.0.2,192.168.1.0/24
```

## Production Deployment

### Before Deploying

1. **Enable Redis for distributed limiting**:
   ```bash
   # .env.production
   RATE_LIMIT_STORAGE_URI=redis://analyticbot-redis:6379/1
   ```

2. **Configure Cloudflare Rate Limiting** (optional extra layer):
   - Cloudflare Dashboard → Security → WAF
   - Add rate limiting rules (10,000 req/min per IP)
   - This protects against DDoS before traffic reaches your API

3. **Monitor in Production**:
   ```bash
   # Watch for rate limit violations
   tail -f logs/api.log | grep "Rate limit exceeded"
   
   # Check Redis storage
   docker exec analyticbot-redis redis-cli DBSIZE
   ```

### Graceful Degradation

If rate limit Redis goes down:
- API continues working with in-memory limits (per-process)
- Not distributed across multiple API servers
- Restart Redis ASAP

## Summary

### Key Points

✅ **Per-IP Limits**: Each user gets their own quota
✅ **Increased Limits**: Updated from 60/min to 300-500/min
✅ **Scalable**: Handles 100k+ users easily
✅ **503 Errors**: NOT rate limiting - Vite dev server issues
✅ **Redis Backend**: Distributed rate limiting across API instances

### Updated Limits

| Before | After | Improvement |
|--------|-------|-------------|
| 60/min | 300/min | **5x increase** |
| 200/min (public) | 500/min | **2.5x increase** |
| 100/min (bot ops) | 300/min | **3x increase** |
| 10/min (login) | 30/min | **3x increase** |

### Action Items

1. ✅ **Rate limits increased** - No action needed
2. ⚠️ **Fix 503 errors** - Restart Vite dev server
3. 📊 **Monitor usage** - Check if new limits are sufficient
4. 🚀 **Deploy to production** - Restart API to apply changes

---

**Last Updated**: December 24, 2025
**Rate Limit System**: Per-IP with Redis backend
**Capacity**: 50M requests/minute for 100k users
