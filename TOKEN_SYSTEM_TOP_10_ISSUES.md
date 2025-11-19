# Token System - Top 10 Issues Found

## 🔴 CRITICAL ISSUES

### Issue #1: Refresh Token Not Stored in Redis on Login
**Severity:** CRITICAL
**Impact:** Token refresh always fails with 401

**Problem:**
Looking at the login flow and refresh logic:

1. **Login** (`apps/api/routers/auth/login.py:75-120`):
   - Creates access_token ✅
   - Creates refresh_token ✅
   - Returns both tokens ✅
   - **BUT**: Refresh token is NOT stored in Redis!

2. **Refresh** (`core/security_engine/auth.py:674-780`):
   - Line 694: Tries to read `refresh_token:{token}` from Redis
   - **ALWAYS FAILS** because token was never stored!
   - Returns 401 Unauthorized

**Root Cause:**
The `create_refresh_token()` method (line 291-347) stores the token in Redis, BUT the login endpoint doesn't call `security_manager.create_refresh_token()`. Instead, it uses `auth_utils.create_refresh_token()` or JWT adapter directly, which doesn't store in Redis.

**Evidence from logs:**
```
Token refresh failed: 401 (Unauthorized)
refresh_token:{token} → NULL (not found in Redis)
```

---

### Issue #2: Token Rotation Breaks Subsequent Refreshes
**Severity:** CRITICAL
**Impact:** User can only refresh once, then gets logged out

**Problem:**
Token rotation flow (line 717-758):
1. User refreshes → Gets new access_token + new refresh_token
2. Old refresh_token deleted from Redis (line 717)
3. New refresh_token created (line 746)
4. **BUT**: Frontend still uses OLD refresh token!
5. Next refresh fails because old token was deleted

**Root Cause:**
Frontend doesn't update its stored refresh_token after receiving rotated token. The tokenRefreshManager stores it (line 179) but if there's any error or race condition, old token persists.

---

### Issue #3: No JWT Token Exists Check in Frontend
**Severity:** HIGH
**Impact:** Continuous token refresh attempts even when not logged in

**Problem:**
`tokenRefreshManager.ts` line 308-312 runs every 30 seconds:
```typescript
setInterval(() => {
    if (manager.isAuthenticated()) {
        manager.refreshIfNeeded();
    }
}, 30000);
```

BUT `isAuthenticated()` only checks if token exists and is not expired - it doesn't verify the token is VALID on backend.

**Result:**
- Invalid tokens keep triggering refresh
- Refresh fails with 401
- clearTokens() called
- Redirect to login
- **But interval still running!**
- Process repeats forever

---

### Issue #4: Missing Refresh Token in Redis During Login
**Severity:** CRITICAL
**File:** `apps/api/routers/auth/login.py:75-120`

**Problem:**
```python
# Line 106-115
refresh_token = auth_utils.create_refresh_token(
    user_id=str(new_user.id),
    session_id=session_id
)

# This creates the JWT string BUT doesn't store in Redis!
# Should be: security_manager.create_refresh_token()
```

The `auth_utils.create_refresh_token()` only creates the JWT string. It doesn't call the SecurityManager's method which stores in Redis.

---

### Issue #5: Dual Token Storage - localStorage vs Constants
**Severity:** MEDIUM
**Impact:** Token mismatches, inconsistent auth state

**Problem:**
Multiple token keys used across codebase:
- `tokenRefreshManager.ts` line 36: `TOKEN_KEY = 'auth_token'`
- `AuthContext.tsx` line 69: `TOKEN_KEY = 'auth_token'` ✅ Same
- `shared/constants/index.ts` line 21: `ACCESS_TOKEN: 'auth_token'` ✅ Same
- BUT also: `'token'`, `'access_token'` used in some places
- Refresh token: `'refresh_token'` everywhere ✅ Consistent

**Risk:** If one file uses wrong key, tokens won't be found.

---

### Issue #6: No Refresh Token Expiry Validation
**Severity:** MEDIUM
**Impact:** Expired refresh tokens cause silent failures

**Problem:**
Refresh tokens have 30-day expiry but frontend never checks:
- Frontend tries to refresh even with expired refresh token
- Backend returns 401
- Frontend logs user out
- **No clear error message** to user

Should check refresh token expiry BEFORE attempting refresh.

---

### Issue #7: Token Refresh on Every Request
**Severity:** MEDIUM
**Impact:** Unnecessary load, slow requests

**Problem:**
`client.ts` line 235-242: EVERY API request calls:
```typescript
await tokenRefreshManager.refreshIfNeeded();
```

This checks token expiry on EVERY request. With 60s buffer, this means:
- If token expires in 59 minutes → refresh triggered
- But we just logged in 1 minute ago!
- Constant refreshing even when not needed

**Solution:** Should only refresh if expiring within next 5 minutes, not 60 seconds.

---

### Issue #8: Hardcoded API URL in tokenRefreshManager
**Severity:** MEDIUM
**File:** `apps/frontend/src/utils/tokenRefreshManager.ts:154-156`

**Problem:**
```typescript
const baseURL = import.meta.env.VITE_API_BASE_URL ||
                import.meta.env.VITE_API_URL ||
                'https://b2qz1m0n-11400.euw.devtunnels.ms';  // ❌ Hardcoded!
```

If DevTunnel URL changes, token refresh breaks silently.

---

### Issue #9: No Refresh Token in Response Type
**Severity:** LOW
**Impact:** TypeScript doesn't enforce refresh_token in responses

**Problem:**
`types/api.ts` line 51: `refresh_token?: string` - Optional!

Should be required for login/register responses:
```typescript
interface LoginResponse {
    access_token: string;
    refresh_token: string;  // ✅ Required, not optional
    user: User;
}
```

---

### Issue #10: Race Condition in Token Refresh Queue
**Severity:** MEDIUM
**Impact:** Some requests may use stale tokens

**Problem:**
`tokenRefreshManager.ts` line 139-147: If multiple requests trigger refresh:
1. First request starts refresh
2. Other requests queued
3. New token received
4. Queued requests resolved with new token
5. **BUT**: Original requests may have already been sent with old token!

The queue resolves AFTER the new token is stored, but the original HTTP requests may have already been constructed with the old token in headers.

---

## Summary

**Root Cause of Current Issue:**
The main problem is **Issue #1** - refresh tokens are never stored in Redis during login, so ALL refresh attempts fail with 401.

**Fix Priority:**
1. **Issue #1**: Fix token storage in Redis (CRITICAL)
2. **Issue #2**: Fix token rotation frontend storage (CRITICAL)
3. **Issue #3**: Stop background refresh on logout (HIGH)
4. **Issue #4**: Use correct SecurityManager method (CRITICAL)
5. Issues #5-10: Medium/Low priority improvements
