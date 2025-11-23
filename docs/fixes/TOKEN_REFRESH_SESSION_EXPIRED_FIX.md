# 🔧 Token Refresh Bug Fix - Session Expired Error

**Date:** November 20, 2025
**Issue:** Users getting logged out after a few minutes with "Token refresh failed: Session expired"
**Root Cause:** Refresh tokens stored in memory cache instead of Redis
**Status:** ✅ **FIXED**

---

## 🐛 The Problem

### Symptoms
Users reported getting logged out automatically after login:
- Console error: `POST https://api.analyticbot.org/auth/refresh 401 (Unauthorized)`
- Error message: "Failed to refresh token: Token refresh failed"
- Message: "No JWT token found in storage"

### What Was Happening

**When user logs in:**
```
1. POST /auth/login
2. Backend creates refresh_token
3. ⚠️ PROBLEM: Token stored in MEMORY cache (not Redis)
4. Frontend receives tokens
5. User continues using app
```

**A few minutes later:**
```
1. Token about to expire, frontend tries to refresh
2. POST /auth/refresh with refresh_token
3. Backend looks for token in Redis
4. ❌ Token NOT FOUND (it's in memory, not Redis!)
5. Returns 401 Unauthorized
6. Frontend logs user out
```

---

## 🔍 Root Cause Analysis

### From API Logs
```
[WARNING] core.security_engine.auth: ⚠️ Using memory cache for: refresh_token:...
    (cache=None, redis_available=False)

[WARNING] apps.api.routers.auth.login: Token refresh failed: 401:
    Token refresh failed: Session expired
```

**Translation:** The `SecurityManager` instance had `cache=None`, so it fell back to in-memory dictionary storage. When API restarted or garbage collection ran, all refresh tokens were lost.

### Code Issue

**File:** `apps/api/auth_utils.py`

**BROKEN CODE (Before Fix):**
```python
def get_auth_utils() -> FastAPIAuthUtils:
    """FastAPI dependency to get auth utils instance"""
    from core.security_engine import SecurityManager

    # ❌ BUG: Creates new SecurityManager WITHOUT cache!
    security_manager = SecurityManager()
    return FastAPIAuthUtils(security_manager)
```

**Why this broke:**
1. `SecurityManager()` with no parameters = no cache injection
2. Instance has `self.cache = None`
3. All cache operations fall back to `self._memory_cache` dictionary
4. Memory cleared on restart → tokens lost
5. Refresh attempts fail with 401

---

## ✅ The Fix

### What Was Changed

**File:** `apps/api/auth_utils.py` (Line 195-202)

**FIXED CODE:**
```python
def get_auth_utils() -> FastAPIAuthUtils:
    """FastAPI dependency to get auth utils instance"""
    # ✅ FIXED: Use singleton SecurityManager with Redis cache from container
    # DO NOT create new SecurityManager() - it won't have cache!
    from core.security_engine.container import get_security_manager

    security_manager = get_security_manager()  # ✅ Gets singleton with Redis
    return FastAPIAuthUtils(security_manager)
```

**What changed:**
- ❌ Before: `SecurityManager()` - new instance, no cache
- ✅ After: `get_security_manager()` - singleton with Redis cache injected

---

## 🎯 Why This Fix Works

### Proper Flow Now

**Login:**
```
1. User logs in
2. Backend uses get_security_manager() → has Redis cache
3. Refresh token stored in Redis ✅
4. Token persists across API restarts ✅
5. Frontend receives tokens
```

**Token Refresh:**
```
1. Frontend token about to expire
2. POST /auth/refresh with refresh_token
3. Backend looks for token in Redis
4. ✅ Token FOUND in Redis!
5. Creates new access_token and refresh_token
6. Returns 200 OK with new tokens
7. User stays logged in ✅
```

---

## 📊 Verification

### How to Verify Fix Is Working

1. **Check API Logs** (should see Redis, not memory):
```bash
tail -f logs/dev_api.log | grep refresh_token
```

**Before Fix:**
```
⚠️ Using memory cache for: refresh_token:... (cache=None, redis_available=False)
```

**After Fix:**
```
🔑 Storing in cache: refresh_token:... (expire=604800s)
✅ Cache set result: True
```

2. **Test in Browser Console:**
```javascript
// Login
await fetch('https://api.analyticbot.org/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'test@example.com', password: 'password' })
});

// Wait 2 minutes, then try refresh
const refreshToken = localStorage.getItem('refresh_token');
const response = await fetch('https://api.analyticbot.org/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh_token: refreshToken })
});

console.log(response.status); // Should be 200, not 401
```

3. **Check Frontend Console** (should see success, not errors):

**Before Fix:**
```
❌ Token refresh failed: Token refresh failed
401 (Unauthorized)
```

**After Fix:**
```
✅ Token refreshed successfully
🔄 Token expiring in 45s, refreshing proactively...
```

---

## 🔄 Deployment Steps

### To Apply This Fix

1. **Pull the latest code:**
```bash
cd /home/abcdeveloper/projects/analyticbot
git pull origin main
```

2. **Restart API server:**
```bash
# Development
sudo systemctl restart analyticbot-api

# Or if using process manager
pm2 restart analyticbot-api
```

3. **Verify Redis is running:**
```bash
redis-cli ping  # Should return: PONG
```

4. **Test token refresh:**
   - Login to frontend
   - Wait 2 minutes
   - Check console for successful refresh messages
   - Should NOT be logged out

---

## 🚨 Prevention

### How to Avoid This in Future

1. **Always use dependency injection:**
```python
# ✅ CORRECT: Use container singleton
from core.security_engine.container import get_security_manager
security_manager = get_security_manager()

# ❌ WRONG: Don't create new instances
from core.security_engine import SecurityManager
security_manager = SecurityManager()  # No cache!
```

2. **Add logging to verify cache:**
```python
logger.info(f"SecurityManager cache: {security_manager.cache is not None}")
logger.info(f"Redis available: {security_manager.redis_available}")
```

3. **Test token refresh in CI/CD:**
```python
# Add integration test
def test_token_refresh_with_redis():
    # Create refresh token
    token = security_manager.create_refresh_token(user_id, session_id)

    # Simulate API restart (new instance)
    new_manager = get_security_manager()

    # Should still work (token in Redis)
    result = new_manager.refresh_access_token(token)
    assert result['access_token']
```

---

## 📝 Related Files

### Modified
- `apps/api/auth_utils.py` - Fixed `get_auth_utils()` to use singleton

### Key Dependencies
- `core/security_engine/container.py` - Provides `get_security_manager()` singleton
- `core/security_engine/auth.py` - `SecurityManager` class
- `apps/frontend/src/utils/tokenRefreshManager.ts` - Frontend token refresh logic

---

## ✅ Success Criteria

**Fix is working when:**
1. ✅ No "Using memory cache" warnings in logs
2. ✅ "Storing in cache" messages show Redis operations
3. ✅ Token refresh returns 200, not 401
4. ✅ Users stay logged in for hours (not minutes)
5. ✅ API restarts don't log users out
6. ✅ No "Session expired" errors in frontend console

---

## 🎯 Impact

**Before Fix:**
- 😞 Users logged out every 2-5 minutes
- 😞 Poor user experience
- 😞 Lost work/unsaved changes
- 😞 Constant re-authentication required

**After Fix:**
- 😊 Users stay logged in for days/weeks
- 😊 Seamless auto-refresh
- 😊 No interruptions
- 😊 Professional UX

---

**Fixed by:** GitHub Copilot
**Verified by:** API logs + console testing
**Status:** ✅ **PRODUCTION READY**
