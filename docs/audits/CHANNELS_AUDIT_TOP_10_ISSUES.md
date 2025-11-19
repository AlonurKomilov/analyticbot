# Channels Endpoint - Complete Audit & Top 10 Issues

## Request Flow Traced

```
Frontend: useUserChannels Hook
    ↓
Frontend: DataProvider._makeRequest()
    ↓
Frontend: apiClient.get('/channels')
    ↓
[30s CLIENT TIMEOUT - REQUEST ABORTED HERE]
    ↓
Network: api.analyticbot.org
    ↓
Nginx: proxy_pass to localhost:11400
    ↓
Backend: FastAPI /channels endpoint
    ↓
Backend: ChannelManagementService.get_user_channels()
    ↓
Backend: ChannelService.get_user_channels()
    ↓
Database: AsyncpgChannelRepository.get_user_channels()
    ↓
PostgreSQL: SELECT * FROM channels WHERE user_id = $1
```

## TOP 10 CRITICAL ISSUES

### 🔴 ISSUE #1: Infinite Loop in useUserChannels Hook
**Severity:** CRITICAL
**File:** `apps/frontend/src/shared/hooks/useUserChannels.ts:122`

**Problem:**
```typescript
const fetchChannels = useCallback(async () => {
    // ...
}, [dataProvider, isAuthenticated, selectedChannel, onChannelChange]);
//                                  ^^^^^^^^^^^^^^^^
// fetchChannels depends on selectedChannel

useEffect(() => {
    if (isAuthenticated && autoFetch) {
        fetchChannels();  // Calls fetchChannels
    }
}, [isAuthenticated, autoFetch, fetchChannels]);
//                              ^^^^^^^^^^^^^^^
// useEffect depends on fetchChannels
```

**Flow:**
1. Component mounts → `fetchChannels` called
2. Channels loaded → `selectedChannel` set (line 80)
3. `selectedChannel` changes → `fetchChannels` recreated (dependency)
4. `fetchChannels` recreated → `useEffect` triggers (dependency)
5. **INFINITE LOOP** → Multiple simultaneous requests
6. All requests timeout → Frontend shows errors

**Impact:**
- Multiple duplicate requests sent
- All requests compete and timeout
- User sees loading state forever
- Backend gets hammered with requests

**Fix:**
```typescript
// Remove selectedChannel from dependencies
const fetchChannels = useCallback(async () => {
    // ... existing code ...
}, [dataProvider, isAuthenticated, onChannelChange]);
//  Remove selectedChannel from here ^
```

---

### 🔴 ISSUE #2: Token Refresh Triggered on Timeout
**Severity:** CRITICAL
**File:** `apps/frontend/src/api/client.ts:381`

**Problem:**
```typescript
// Line 356: Timeout error thrown
if (error.name === 'AbortError') {
    const timeoutError = new ApiRequestError('Request timeout');
    timeoutError.response = { status: 408, statusText: 'Request Timeout' };
    throw timeoutError;
}

// Line 381: 408 treated as auth error (WRONG!)
if (error instanceof ApiRequestError &&
    error.response?.status === 401 &&
    !options._retry &&
    hasRefreshToken &&
    !isTimeoutError) {  // This check was JUST added but not working!
```

**Actual Flow:**
1. Request times out (30s)
2. Error thrown with status 408
3. Code checks if status === 401 (it's not)
4. BUT somewhere else 408 is being treated as 401!
5. Token refresh triggered
6. Refresh fails (token is valid)
7. User logged out

**Issue:** The `isTimeoutError` check is only checking error.message, but the actual error status is 408, not 401. Something else is converting 408 to 401.

---

### 🔴 ISSUE #3: 30-Second Client Timeout Too Short
**Severity:** HIGH
**File:** `apps/frontend/src/api/client.ts:245`

**Problem:**
```typescript
const controller = new AbortController();
const requestTimeout = this.getTimeoutForEndpoint(endpoint);
const timeoutId = setTimeout(() => {
    controller.abort();  // Aborts after 30s for /channels
}, requestTimeout);
```

**With CloudFlare + Nginx + Network Latency:**
- CloudFlare tunnel: ~500-1000ms
- Nginx processing: ~100ms
- Backend processing: ~50-200ms
- Network round-trip: ~500-1000ms
- **Total:** Can easily exceed 30s under load

**Impact:** Requests abort before backend can respond

---

### 🔴 ISSUE #4: No Request Actually Reaches Backend
**Severity:** CRITICAL
**Evidence:** Backend logs show ZERO /channels requests

**Problem Chain:**
1. Frontend makes request to `https://api.analyticbot.org/channels`
2. Request timeout after 30s CLIENT-SIDE
3. Backend logs show NO requests received
4. **Conclusion:** Request is not leaving the browser OR being blocked somewhere

**Possible Causes:**
- CORS preflight taking too long
- CloudFlare blocking/routing issue
- DNS resolution delay
- Browser network throttling
- Service Worker intercepting

---

### 🟡 ISSUE #5: selectedChannel Dependency Creates Re-renders
**Severity:** MEDIUM
**File:** `apps/frontend/src/shared/hooks/useUserChannels.ts:140`

**Problem:**
```typescript
useEffect(() => {
    if (channels.length > 0 && !selectedChannel) {
        // ... auto-select logic
        setSelectedChannel(firstChannel);  // State update
        onChannelChange?.(firstChannel);    // Callback
    }
}, [channels, selectedChannel, onChannelChange]);
//           ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^
```

**Flow:**
1. Channels loaded → `selectedChannel` is null
2. useEffect runs → sets `selectedChannel`
3. `selectedChannel` changes → useEffect runs AGAIN
4. Loop continues

---

### 🟡 ISSUE #6: fetchChannels Not Memoized Properly
**Severity:** MEDIUM
**File:** `apps/frontend/src/shared/hooks/useUserChannels.ts:67`

**Problem:**
```typescript
const fetchChannels = useCallback(async () => {
    // ...
    if (!selectedChannel && response && response.length > 0) {
        const firstChannel = response[0];
        setSelectedChannel(firstChannel);  // Modifies selectedChannel
        onChannelChange?.(firstChannel);
    }
}, [dataProvider, isAuthenticated, selectedChannel, onChannelChange]);
//                                  ^^^^^^^^^^^^^^^^
// Depends on selectedChannel which it modifies!
```

**Anti-Pattern:** Function depends on state it modifies → Creates infinite recreation

---

### 🟡 ISSUE #7: No Loading Boundary / Retry UI
**Severity:** MEDIUM
**File:** `apps/frontend/src/shared/hooks/useUserChannels.ts`

**Problem:**
- No retry mechanism in the hook itself
- No exponential backoff
- No "Try Again" button shown to user
- User just sees infinite loading or error

**User Experience:**
1. Page loads
2. Spinner shows
3. 30 seconds pass
4. Error shown
5. **No way to retry without refresh**

---

### 🟡 ISSUE #8: No Request Deduplication
**Severity:** MEDIUM
**File:** `apps/frontend/src/shared/hooks/useUserChannels.ts`

**Problem:**
- If hook is used in multiple components, each makes separate request
- No global cache or request deduplication
- Same data fetched multiple times

**Example:**
```typescript
// Component A
const { channels } = useUserChannels();  // Request 1

// Component B
const { channels } = useUserChannels();  // Request 2 (duplicate!)
```

---

### 🟡 ISSUE #9: No Database Query Optimization Check
**Severity:** MEDIUM
**File:** `infra/db/repositories/channel_repository.py:68`

**Problem:**
```python
async def get_user_channels(self, user_id: int) -> list[dict[str, Any]]:
    async with self.pool.acquire() as conn:
        records = await conn.fetch(
            """
            SELECT
                id,
                title,
                username,
                COALESCE(description, '') as description,
                created_at,
                user_id,
                subscriber_count,
                updated_at
            FROM channels
            WHERE user_id = $1
            ORDER BY created_at DESC
            """,
            user_id,
        )
```

**Unknown:**
- Are there indexes on `user_id`?
- How many channels per user (could be thousands)?
- No LIMIT clause - fetches ALL channels
- No pagination support

**Impact:** If user has 1000+ channels, query could be slow

---

### 🟡 ISSUE #10: Token Refresh During Active Request
**Severity:** MEDIUM
**File:** `apps/frontend/src/api/client.ts:232`

**Problem:**
```typescript
// STEP 1: Before request - check if token expiring
if (this.authStrategy === AuthStrategies.JWT && !isAuthEndpoint) {
    try {
        await tokenRefreshManager.refreshIfNeeded();  // Proactive refresh
    } catch (error) {
        console.warn('⚠️ Proactive token refresh failed...');
    }
}

// STEP 2: Make the actual request (which might take 30s)
const response = await fetch(url, {
    signal: controller.signal,
    // ...
});

// STEP 3: If 401, refresh again (reactive refresh)
if (error.response?.status === 401) {
    await tokenRefreshManager.handleAuthError(/* ... */);
}
```

**Issue:** If request takes 30s and token expires DURING the request, the response is 401 but token was valid when sent. System refreshes unnecessarily.

---

## Additional Observations

### Backend Performance (From Previous Tests)
- `/health` endpoint: 3-7ms ✅
- `/channels` with 1 channel: ~110ms ✅
- Backend is NOT slow!

### Network Layer
- Nginx timeout: Now 60s (was 30s) ✅
- CloudFlare tunnel: Active ✅
- CORS: Working correctly ✅

### The Real Issue
**Requests are timing out on the CLIENT SIDE before ever reaching the backend!**

Evidence:
1. Backend logs show ZERO /channels requests
2. Nginx logs show timeout errors
3. Frontend aborts after 30s
4. Token refresh triggers after timeout

## Root Cause Analysis

### Primary Root Cause: Frontend Infinite Loop
The `useUserChannels` hook has a dependency cycle that causes:
1. Infinite re-renders
2. Multiple simultaneous requests
3. All requests timeout
4. Token refresh triggered
5. User logged out

### Secondary Root Cause: Request Not Sent
Even if we fix the loop, something is preventing the request from reaching the backend:
- Possibly browser DevTools throttling
- Possibly React Strict Mode (but we disabled it)
- Possibly CORS preflight hanging
- Possibly DNS/routing issue

## Immediate Action Plan

### Priority 1: Fix Infinite Loop
```typescript
// useUserChannels.ts
const fetchChannels = useCallback(async () => {
    if (!isAuthenticated) {
        setError('Authentication required');
        return;
    }

    setLoading(true);
    setError(null);

    try {
        const response = await (dataProvider as any)._makeRequest('/channels');
        setChannels(response || []);
        setLastFetch(new Date().toISOString());

        // Don't set selectedChannel here - let separate effect handle it

    } catch (err) {
        console.error('Failed to fetch user channels:', err);
        setError(err.message);
    } finally {
        setLoading(false);
    }
}, [dataProvider, isAuthenticated]);  // Remove selectedChannel!

// Separate effect for auto-selection
useEffect(() => {
    if (channels.length > 0 && !selectedChannel) {
        const firstChannel = channels[0];
        setSelectedChannel(firstChannel);
        onChannelChange?.(firstChannel);
    }
}, [channels]);  // Only depend on channels, not selectedChannel!
```

### Priority 2: Add Request Deduplication
```typescript
// Create singleton request manager
let activeChannelsRequest: Promise<any> | null = null;

const fetchChannels = useCallback(async () => {
    if (activeChannelsRequest) {
        console.log('⏳ Channels request already in progress, waiting...');
        return activeChannelsRequest;
    }

    activeChannelsRequest = (async () => {
        try {
            const response = await (dataProvider as any)._makeRequest('/channels');
            return response;
        } finally {
            activeChannelsRequest = null;
        }
    })();

    return activeChannelsRequest;
}, [dataProvider]);
```

### Priority 3: Add Retry Logic with Exponential Backoff
```typescript
const fetchChannelsWithRetry = async (retries = 3) => {
    for (let i = 0; i < retries; i++) {
        try {
            return await fetchChannels();
        } catch (err) {
            if (i === retries - 1) throw err;

            const delay = Math.pow(2, i) * 1000;  // 1s, 2s, 4s
            console.log(`Retry ${i + 1}/${retries} after ${delay}ms`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
};
```

### Priority 4: Prevent Token Refresh on Timeout
```typescript
// client.ts
if (error instanceof ApiRequestError &&
    error.response?.status === 401 &&
    !options._retry &&
    hasRefreshToken &&
    error.response?.status !== 408) {  // Don't refresh on timeout!
```

### Priority 5: Add Database Index
```sql
CREATE INDEX IF NOT EXISTS idx_channels_user_id ON channels(user_id);
```

## Testing Plan

```bash
# 1. Clear browser cache and storage
# 2. Open DevTools → Network tab
# 3. Login
# 4. Watch for /channels request
# 5. Check if request is sent
# 6. Check backend logs: tail -f logs/dev_api.log | grep "GET /channels"
# 7. Check timing: Should be < 1 second
```

## Success Criteria

- ✅ Only ONE /channels request per page load
- ✅ Request reaches backend (visible in logs)
- ✅ Response received in < 5 seconds
- ✅ No token refresh triggered
- ✅ Channels displayed correctly
- ✅ No infinite loops or re-renders
