# Token System - Top 10 Issues Found

## 🔴 CRITICAL ISSUES

### Issue #1: SecurityManager NOT Connected to Redis
**Severity:** CRITICAL
**Impact:** ALL refresh tokens lost on restart, token refresh ALWAYS fails

**Problem:**
The `SecurityManager` singleton (`core/security_engine/container.py:36-38`) is initialized with NO parameters:

```python
@property
def security_manager(self) -> SecurityManager:
    if self._security_manager is None:
        self._security_manager = SecurityManager()  # ❌ No cache passed!
    return self._security_manager
```

When SecurityManager has no `cache` parameter (`core/security_engine/auth.py:102-107`):
```python
def __init__(self, config=None, cache=None, ...):
    ...
    if cache is None:
        self._setup_memory_cache()  # ❌ Falls back to _memory_cache dict
```

**Result:**
1. Login creates refresh_token
2. `create_refresh_token()` calls `self._cache_set()` (line 312-319)
3. Stores in `self._memory_cache` dictionary (NOT Redis!)
4. Dictionary is **wiped on server restart**
5. User tries to refresh → `_cache_get(f"refresh_token:{token}")` returns None
6. Returns 401 Unauthorized

**Evidence:**
```bash
$ docker exec analyticbot-redis redis-cli KEYS "refresh_token:*"
(empty array)  # ❌ NO TOKENS IN REDIS!
```

**Fix:**
```python
# core/security_engine/container.py
from infra.security.adapters import RedisCache
from config.settings import settings

@property
def security_manager(self) -> SecurityManager:
    if self._security_manager is None:
        # ✅ Initialize with Redis cache
        cache = RedisCache(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        self._security_manager = SecurityManager(cache=cache)
    return self._security_manager
```

---

### Issue #2: Token Rotation Breaks Subsequent Refreshes
**Severity:** CRITICAL
**Impact:** User can only refresh once, then gets logged out

**Problem:**
Token rotation flow (`core/security_engine/auth.py:717-758`):
1. User refreshes → Gets new access_token + new refresh_token
2. Old refresh_token deleted from Redis (line 717)
3. New refresh_token created (line 746)
4. **BUT**: Frontend may still use OLD refresh token due to race conditions!
5. Next refresh fails because old token was deleted

**Evidence from logs:**
```
🔄 Rotated refresh token for user 123
Token refresh failed: Invalid refresh token  # Old token already deleted
```

---

### Issue #3: No JWT Token Validation in Frontend Loop
**Severity:** HIGH
**Impact:** Continuous failed refresh attempts

**Problem:**
`tokenRefreshManager.ts` line 308-312 runs every 30 seconds:
```typescript
setInterval(() => {
    if (manager.isAuthenticated()) {
        manager.refreshIfNeeded();
    }
}, 30000);
```

BUT `isAuthenticated()` only checks if token exists locally - doesn't verify it's valid on backend.

**Result:**
- Invalid tokens keep triggering refresh
- Refresh fails with 401
- clearTokens() called
- Redirect to login
- **But setInterval still running!**
- Process repeats forever

---

### Issue #4: Missing Refresh Token in Redis During Login (CONFIRMED FALSE - THIS WORKS)
**Severity:** N/A - Not an issue
**File:** `apps/api/routers/auth/login.py:106-112`

~~**Problem:**~~
~~`auth_utils.create_refresh_token()` doesn't store in Redis~~

**CORRECTION:** This actually DOES work correctly:
```python
# apps/api/auth_utils.py:97-100
def create_refresh_token(self, user_id, session_token, remember_me=False):
    return self.security_manager.create_refresh_token(...)  # ✅ Calls SecurityManager
```

The SecurityManager DOES store it, but in `_memory_cache` not Redis (because of Issue #1).

---

### Issue #5: Dual Token Storage Keys
**Severity:** MEDIUM
**Impact:** Token mismatches, inconsistent auth state

**Problem:**
Multiple token keys used:
- `tokenRefreshManager.ts`: `'auth_token'` & `'refresh_token'` ✅
- `AuthContext.tsx`: `'auth_token'` & `'refresh_token'` ✅
- `shared/constants/index.ts`: `'auth_token'` & `'refresh_token'` ✅
- `client.ts`: Direct localStorage access in some places

**Risk:** If implementation changes in one file, others break.

---

### Issue #6: No Refresh Token Expiry Check Before Refresh
**Severity:** MEDIUM
**Impact:** Unnecessary failed requests, poor UX

**Problem:**
Frontend tries to refresh even with expired refresh token (30 days):
```typescript
async refreshToken(): Promise<string> {
    const refreshToken = this.getRefreshToken();
    // ❌ No check if refresh token itself is expired!

    const response = await fetch(`${baseURL}/auth/refresh`, {
        body: JSON.stringify({ refresh_token: refreshToken })
    });
}
```

Should parse refresh token JWT and check exp before attempting refresh.

---

### Issue #7: Token Refresh on EVERY Request (60s Buffer)
**Severity:** MEDIUM
**Impact:** Unnecessary load, token churn

**Problem:**
`client.ts` line 235-242: EVERY API request calls:
```typescript
await tokenRefreshManager.refreshIfNeeded();
```

With 60-second buffer (`EXPIRY_BUFFER_SECONDS = 60`):
- Token expires in 30 minutes
- Starts refreshing at 29 minutes
- **That's 29 minutes of constant refreshing!**

**Fix:** Reduce buffer to 5 minutes (300 seconds).

---

### Issue #8: Hardcoded DevTunnel URL
**Severity:** MEDIUM
**File:** `apps/frontend/src/utils/tokenRefreshManager.ts:154-156`

**Problem:**
```typescript
const baseURL = import.meta.env.VITE_API_BASE_URL ||
                import.meta.env.VITE_API_URL ||
                'https://b2qz1m0n-11400.euw.devtunnels.ms';  // ❌ Hardcoded!
```

If DevTunnel changes, token refresh silently breaks.

---

### Issue #9: Optional refresh_token in Response Types
**Severity:** LOW
**Impact:** TypeScript doesn't enforce required fields

**Problem:**
`types/api.ts` line 51: `refresh_token?: string` - Optional!

Should be required for login/register:
```typescript
interface LoginResponse {
    access_token: string;
    refresh_token: string;  // ✅ Required
    user: User;
}
```

---

### Issue #10: Race Condition in Refresh Queue
**Severity:** MEDIUM
**Impact:** Some requests may fail despite successful refresh

**Problem:**
`tokenRefreshManager.ts` line 139-147: Multiple concurrent requests:
1. Request A triggers refresh, starts fetch
2. Requests B, C, D queued
3. Refresh completes, new token stored
4. Queued requests resolved with new token
5. **BUT**: Original request A headers already sent with old token!

The queue helps with subsequent requests, but the original triggering request may still fail.

---

## Summary

**Root Cause of Current Issue:**
**Issue #1** is the PRIMARY problem - SecurityManager uses memory cache instead of Redis, so ALL refresh tokens are lost on server restart or memory cleanup.

**Fix Priority:**
1. **Issue #1**: Connect SecurityManager to Redis (CRITICAL - MUST FIX)
2. **Issue #3**: Stop background interval on logout (HIGH)
3. **Issue #2**: Fix token rotation race condition (CRITICAL)
4. **Issue #7**: Reduce refresh buffer from 60s to 300s (MEDIUM)
5. **Issue #6**: Check refresh token expiry (MEDIUM)
6. Issues #5, #8, #9, #10: Lower priority improvements

**Verification:**
After fixing Issue #1, check:
```bash
# Should see refresh tokens in Redis
docker exec analyticbot-redis redis-cli KEYS "refresh_token:*"
```
