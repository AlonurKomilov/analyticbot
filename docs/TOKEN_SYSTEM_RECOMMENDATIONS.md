# 🔐 Production-Ready Token System - Comprehensive Recommendations

> **For Analyticbot Project - October 2025**
>
> Enterprise-grade authentication recommendations for a scalable, secure platform

---

## 📋 Executive Summary

**Current Issues Identified:**
- ✅ Refresh tokens exist but not auto-implemented in frontend
- ⚠️ Short access token expiry (30 min) without auto-refresh = poor UX
- ⚠️ Token expiration causes 90-second timeout instead of fast 401
- ⚠️ No sliding session mechanism
- ⚠️ Missing token rotation strategy
- ⚠️ No graceful degradation for network issues

**Priority Recommendations:**
1. **CRITICAL**: Implement automatic token refresh in frontend
2. **HIGH**: Add token rotation and revocation
3. **HIGH**: Implement proper 401 handling with fast-fail
4. **MEDIUM**: Add sliding sessions and "remember me"
5. **MEDIUM**: Implement device fingerprinting and anomaly detection

---

## 🎯 1. AUTOMATIC TOKEN REFRESH (CRITICAL - Implement First)

### Current State
```typescript
// ❌ Current: User must manually re-login every 30 minutes
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Too short without auto-refresh
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # Good, but not utilized

// ❌ Frontend: No interceptor to auto-refresh
// When token expires → 401 → manual logout → bad UX
```

### Recommended Implementation

#### Backend: Add refresh endpoint (ALREADY EXISTS ✅)
```python
# core/security_engine/auth.py - LINE 634
def refresh_access_token(self, refresh_token: str) -> str:
    """✅ Already implemented - just needs frontend integration"""
```

#### Frontend: Axios/Fetch Interceptor with Auto-Refresh

**Create: `apps/frontend/src/api/tokenRefreshInterceptor.ts`**
```typescript
/**
 * 🔄 Token Refresh Interceptor - Auto-refresh expired tokens
 *
 * Strategy: Intercept 401 responses, refresh token, retry original request
 */

interface QueueItem {
  resolve: (token: string) => void;
  reject: (error: any) => void;
}

class TokenRefreshManager {
  private isRefreshing = false;
  private refreshQueue: QueueItem[] = [];
  private tokenExpiryBuffer = 60; // Refresh 60s before expiry

  /**
   * Check if token is about to expire
   */
  isTokenExpiringSoon(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiryTime = payload.exp * 1000; // Convert to ms
      const now = Date.now();
      const timeUntilExpiry = expiryTime - now;

      return timeUntilExpiry < (this.tokenExpiryBuffer * 1000);
    } catch {
      return true; // If can't parse, assume expired
    }
  }

  /**
   * Refresh token with queue management (prevents race conditions)
   */
  async refreshToken(): Promise<string> {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    // If already refreshing, queue this request
    if (this.isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        this.refreshQueue.push({ resolve, reject });
      });
    }

    this.isRefreshing = true;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      const newAccessToken = data.access_token;

      // Store new tokens
      localStorage.setItem('auth_token', newAccessToken);
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }

      // Resolve all queued requests
      this.refreshQueue.forEach(item => item.resolve(newAccessToken));
      this.refreshQueue = [];

      return newAccessToken;
    } catch (error) {
      // Reject all queued requests
      this.refreshQueue.forEach(item => item.reject(error));
      this.refreshQueue = [];

      // Clear tokens and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';

      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Request interceptor - refresh token before request if expiring soon
   */
  async onRequest(config: RequestInit & { url: string }): Promise<RequestInit & { url: string }> {
    const token = localStorage.getItem('auth_token');

    if (token && this.isTokenExpiringSoon(token)) {
      console.log('🔄 Token expiring soon, refreshing proactively...');
      const newToken = await this.refreshToken();

      // Update authorization header
      config.headers = {
        ...config.headers,
        'Authorization': `Bearer ${newToken}`
      };
    }

    return config;
  }

  /**
   * Response interceptor - handle 401 and retry with new token
   */
  async onResponseError(error: any, originalRequest: () => Promise<any>): Promise<any> {
    // If 401 and not already retried
    if (error.response?.status === 401 && !error.config?._retry) {
      error.config._retry = true;

      try {
        console.log('🔄 Got 401, refreshing token and retrying...');
        await this.refreshToken();

        // Retry original request with new token
        return originalRequest();
      } catch (refreshError) {
        console.error('❌ Token refresh failed, logging out');
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
}

export const tokenRefreshManager = new TokenRefreshManager();
```

**Update: `apps/frontend/src/api/client.ts`**
```typescript
// Add to UnifiedApiClient.request() method
async request<T = unknown>(endpoint: string, options: RequestConfig = {}, attempt = 1): Promise<T> {
  // BEFORE making request: Check if token needs refresh
  const token = localStorage.getItem('auth_token');
  if (token && tokenRefreshManager.isTokenExpiringSoon(token)) {
    await tokenRefreshManager.refreshToken();
  }

  const controller = new AbortController();
  // ... existing code ...

  try {
    const response = await fetch(url, requestConfig);
    // ... existing code ...
  } catch (error: any) {
    // Handle 401 with token refresh
    if (error.response?.status === 401 && !options._retry) {
      try {
        await tokenRefreshManager.refreshToken();
        options._retry = true;
        return this.request<T>(endpoint, options, attempt); // Retry
      } catch (refreshError) {
        // Token refresh failed, logout
        this.logout();
        throw error;
      }
    }
    // ... existing error handling ...
  }
}
```

**Benefits:**
- ✅ **Zero user interruption** - tokens refresh automatically
- ✅ **Proactive refresh** - refreshes 60s before expiry (no race conditions)
- ✅ **Retry failed requests** - 401 → refresh → retry original request
- ✅ **Queue management** - prevents multiple simultaneous refresh calls
- ✅ **Fast failure** - if refresh fails, immediate logout

---

## 🔄 2. TOKEN ROTATION & REVOCATION (HIGH PRIORITY)

### Problem: Stolen refresh tokens are valid for 7 days

**Current Risk:**
```python
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # If stolen, valid for 7 days!
```

### Solution: Refresh Token Rotation (RTR)

**Backend: Update `core/security_engine/auth.py`**
```python
def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
    """
    Refresh access token with rotation

    ✅ NEW BEHAVIOR:
    1. Validate old refresh token
    2. Issue NEW refresh token (rotate)
    3. Invalidate old refresh token
    4. Return both new access + new refresh tokens
    """
    # Verify old refresh token
    refresh_data_str = self._cache_get(f"refresh_token:{refresh_token}")
    if not refresh_data_str:
        raise AuthenticationError("Invalid refresh token", error_code="INVALID_REFRESH_TOKEN")

    refresh_data = json.loads(refresh_data_str)
    user_id = refresh_data["user_id"]

    # INVALIDATE old refresh token (rotation)
    self._cache_delete(f"refresh_token:{refresh_token}")

    # Issue NEW refresh token
    new_refresh_token = self.create_refresh_token(user_id, secrets.token_urlsafe(32))

    # Issue new access token
    user = await self.user_repository.get_user_by_id(user_id)
    new_access_token = self.create_access_token(user)

    # Log security event
    self._log_security_event({
        "event": "token_rotation",
        "user_id": user_id,
        "old_token_hash": hashlib.sha256(refresh_token.encode()).hexdigest()[:16],
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,  # ✅ NEW: Rotated token
        "token_type": "bearer"
    }
```

**Frontend: Handle rotated tokens**
```typescript
async refreshToken(): Promise<string> {
  // ... existing code ...

  const data = await response.json();
  localStorage.setItem('auth_token', data.access_token);

  // ✅ IMPORTANT: Store new refresh token
  if (data.refresh_token) {
    localStorage.setItem('refresh_token', data.refresh_token);
  }

  return data.access_token;
}
```

**Benefits:**
- ✅ **Stolen tokens auto-expire** - old refresh token invalidated immediately
- ✅ **Replay attack prevention** - can't reuse old refresh tokens
- ✅ **Audit trail** - track token rotation events

---

## ⚡ 3. FAST-FAIL 401 HANDLING (HIGH PRIORITY)

### Problem: Token validation takes 90 seconds to timeout

**Current Issue:**
```
Request timeout after 90000ms for /api/user-bot/status
```

### Root Cause Analysis
1. Invalid token → backend tries to verify → hangs somewhere
2. No circuit breaker for auth failures
3. Dev tunnel latency compounds the issue

### Solution: Fast-Fail Auth Middleware

**Backend: Add auth timeout + circuit breaker**
```python
# apps/api/middleware/auth.py

import asyncio
from functools import wraps

AUTH_TIMEOUT_SECONDS = 5  # Auth should never take >5s

async def get_current_user_with_timeout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> dict[str, Any]:
    """
    Fast-fail authentication with timeout
    """
    try:
        # Wrap auth with timeout
        return await asyncio.wait_for(
            get_current_user(credentials, user_repo),
            timeout=AUTH_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        logger.error(f"❌ Auth timeout after {AUTH_TIMEOUT_SECONDS}s")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication timeout",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"❌ Auth error: {e}")
        # FAST FAIL - don't hang
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

**Frontend: Reduce timeout for auth endpoints**
```typescript
// apps/frontend/src/api/client.ts

const ENDPOINT_TIMEOUTS: Record<string, number> = {
  '/auth/': 10000,        // Auth: 10s max
  '/api/user-bot/': 30000,  // Bot ops: 30s (reduce from 90s)
  'default': 20000          // Default: 20s (reduce from 30s)
};

// Add fast retry for 401s
if (error.response?.status === 401) {
  // Don't wait 90s - fail fast
  const quickError = new ApiRequestError('Authentication failed');
  quickError.response = error.response;
  throw quickError; // Immediate throw, no retry
}
```

**Benefits:**
- ✅ **5-second auth timeout** instead of 90 seconds
- ✅ **Fast 401 response** - immediate user feedback
- ✅ **Better error handling** - log and fail gracefully

---

## 🔐 4. SLIDING SESSIONS & "REMEMBER ME" (MEDIUM PRIORITY)

### Goal: Balance security with user convenience

**Current State:**
- Access token: 30 min
- Refresh token: 7 days
- No activity-based extension

### Recommended: Sliding Session Window

**Backend: Extend session on activity**
```python
# core/security_engine/auth.py

async def extend_session_on_activity(self, user_id: int, session_id: str) -> None:
    """
    Extend session expiry on user activity (sliding window)

    Rules:
    - If activity within last 30 min → extend by 30 min
    - Max session length: 12 hours (or 30 days with "remember me")
    """
    session_key = f"session:{session_id}"
    session_data = self._cache_get(session_key)

    if not session_data:
        return

    # Parse session
    session = json.loads(session_data)
    last_activity = datetime.fromisoformat(session["last_activity"])
    created_at = datetime.fromisoformat(session["created_at"])

    # Check if within sliding window (30 min)
    if (datetime.utcnow() - last_activity).seconds < 1800:
        # Update last activity
        session["last_activity"] = datetime.utcnow().isoformat()

        # Calculate new expiry
        if session.get("remember_me"):
            # Remember me: 30 days max
            max_age = timedelta(days=30)
        else:
            # Regular: 12 hours max
            max_age = timedelta(hours=12)

        # Don't exceed max age from creation
        time_since_creation = datetime.utcnow() - created_at
        remaining_time = max_age - time_since_creation

        if remaining_time.total_seconds() > 0:
            # Extend session
            self._cache_set(
                session_key,
                json.dumps(session),
                int(remaining_time.total_seconds())
            )
```

**"Remember Me" Implementation**
```python
def create_refresh_token(
    self,
    user_id: str,
    session_id: str,
    remember_me: bool = False  # ✅ NEW PARAMETER
) -> str:
    """Create refresh token with optional extended expiry"""

    if remember_me:
        expire_days = 30  # 30 days for "remember me"
    else:
        expire_days = 7   # 7 days regular

    expire = datetime.utcnow() + timedelta(days=expire_days)

    claims = {
        "sub": user_id,
        "session_id": session_id,
        "remember_me": remember_me,  # Include in token
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
    }

    # ... rest of implementation
```

**Frontend: Add "Remember Me" checkbox**
```typescript
// Login form
<FormControlLabel
  control={
    <Checkbox
      checked={rememberMe}
      onChange={(e) => setRememberMe(e.target.checked)}
    />
  }
  label="Keep me signed in for 30 days"
/>

// Send to backend
const response = await apiClient.post('/auth/login', {
  email,
  password,
  remember_me: rememberMe  // ✅ Send flag
});
```

**Benefits:**
- ✅ **Sliding sessions** - active users stay logged in
- ✅ **Remember me** - optional 30-day sessions
- ✅ **Security limits** - max 12 hours regular, 30 days "remember me"
- ✅ **Better UX** - fewer re-logins for active users

---

## 🛡️ 5. DEVICE FINGERPRINTING & ANOMALY DETECTION (MEDIUM PRIORITY)

### Goal: Detect and prevent token theft/abuse

**Implementation: Device fingerprinting**
```typescript
// apps/frontend/src/utils/deviceFingerprint.ts

/**
 * Generate device fingerprint (client-side)
 */
export function generateDeviceFingerprint(): string {
  const navigator = window.navigator;
  const screen = window.screen;

  const fingerprint = {
    userAgent: navigator.userAgent,
    language: navigator.language,
    platform: navigator.platform,
    screenResolution: `${screen.width}x${screen.height}`,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    colorDepth: screen.colorDepth,
    // Don't include IP - handled server-side
  };

  // Hash for privacy
  return btoa(JSON.stringify(fingerprint)).substring(0, 32);
}

// Send with auth requests
const deviceId = generateDeviceFingerprint();
headers['X-Device-ID'] = deviceId;
```

**Backend: Track and validate devices**
```python
# core/security_engine/auth.py

async def validate_device_fingerprint(
    self,
    user_id: int,
    device_id: str,
    ip_address: str
) -> bool:
    """
    Validate device fingerprint and detect anomalies

    Returns: True if device is trusted, False if suspicious
    """
    # Get user's known devices
    devices_key = f"user_devices:{user_id}"
    known_devices = self._cache_get(devices_key) or "[]"
    devices = json.loads(known_devices)

    # Check if device is known
    for device in devices:
        if device["device_id"] == device_id:
            # Known device - update last seen
            device["last_seen"] = datetime.utcnow().isoformat()
            device["last_ip"] = ip_address
            self._cache_set(devices_key, json.dumps(devices), 86400 * 90)  # 90 days
            return True

    # New device detected
    logger.warning(f"🚨 New device for user {user_id}: {device_id[:8]}...")

    # Add to known devices (after email verification in production)
    devices.append({
        "device_id": device_id,
        "first_seen": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat(),
        "last_ip": ip_address
    })
    self._cache_set(devices_key, json.dumps(devices), 86400 * 90)

    # TODO: Send email notification about new device
    # await send_new_device_alert(user_id, device_id, ip_address)

    return True  # Allow for now, email user
```

**Anomaly Detection Rules**
```python
async def detect_suspicious_activity(
    self,
    user_id: int,
    ip_address: str,
    device_id: str
) -> tuple[bool, str | None]:
    """
    Detect suspicious authentication patterns

    Returns: (is_suspicious, reason)
    """
    # Get recent login attempts
    attempts_key = f"login_attempts:{user_id}"
    attempts_str = self._cache_get(attempts_key) or "[]"
    attempts = json.loads(attempts_str)

    # Add current attempt
    attempts.append({
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip_address,
        "device": device_id
    })

    # Keep last 100 attempts
    attempts = attempts[-100:]
    self._cache_set(attempts_key, json.dumps(attempts), 86400)  # 24 hours

    # Anomaly checks
    recent_attempts = [a for a in attempts if
        (datetime.utcnow() - datetime.fromisoformat(a["timestamp"])).seconds < 3600
    ]

    # 1. Too many logins in short time
    if len(recent_attempts) > 10:
        return True, "Too many login attempts (>10/hour)"

    # 2. Multiple IPs in short time (VPN hopping / account sharing)
    recent_ips = set(a["ip"] for a in recent_attempts)
    if len(recent_ips) > 5:
        return True, "Multiple IPs detected (possible account sharing)"

    # 3. Geolocation jump (if you add GeoIP)
    # if geoip_distance(last_ip, current_ip) > 1000km and time_delta < 1hour:
    #     return True, "Impossible travel detected"

    return False, None
```

**Benefits:**
- ✅ **Detect stolen tokens** - unusual device/IP triggers alert
- ✅ **Email notifications** - user alerted to new devices
- ✅ **Anomaly detection** - catch account sharing, VPN hopping
- ✅ **Audit trail** - track all devices and IPs

---

## 📊 6. TOKEN MONITORING & ANALYTICS (RECOMMENDED)

### Metrics to Track

**Create: `core/monitoring/auth_metrics.py`**
```python
from prometheus_client import Counter, Histogram, Gauge

# Token metrics
token_issued_total = Counter(
    'auth_tokens_issued_total',
    'Total tokens issued',
    ['token_type']  # access, refresh
)

token_refresh_total = Counter(
    'auth_token_refresh_total',
    'Total token refreshes',
    ['status']  # success, failed
)

token_revocation_total = Counter(
    'auth_token_revocation_total',
    'Total token revocations',
    ['reason']  # logout, expired, suspicious
)

auth_duration_seconds = Histogram(
    'auth_duration_seconds',
    'Time spent in authentication',
    ['endpoint']
)

active_sessions_gauge = Gauge(
    'auth_active_sessions',
    'Number of active sessions'
)

# Use in SecurityManager
class SecurityManager:
    def create_access_token(self, user, expires_delta=None):
        token = # ... create token ...
        token_issued_total.labels(token_type='access').inc()
        return token

    def refresh_access_token(self, refresh_token):
        try:
            token = # ... refresh logic ...
            token_refresh_total.labels(status='success').inc()
            return token
        except Exception as e:
            token_refresh_total.labels(status='failed').inc()
            raise
```

**Dashboard Alerts:**
- 🚨 Token refresh failure rate > 5%
- 🚨 Authentication duration > 2 seconds
- 🚨 Suspicious activity detected
- 📊 Active sessions count
- 📊 Token refresh rate

---

## 🗺️ IMPLEMENTATION ROADMAP

### Phase 1: Critical Fixes (Week 1)
- [ ] **Day 1-2**: Implement automatic token refresh in frontend
- [ ] **Day 3**: Add fast-fail 401 handling (5s timeout)
- [ ] **Day 4**: Reduce endpoint timeouts (90s → 30s for bot ops)
- [ ] **Day 5**: Test and deploy

**Expected Impact:**
- ✅ Zero user logouts from token expiry
- ✅ Fast 401 responses (<5s instead of 90s)
- ✅ Better user experience

### Phase 2: Security Enhancements (Week 2)
- [ ] **Day 1-2**: Implement token rotation
- [ ] **Day 3-4**: Add device fingerprinting
- [ ] **Day 5**: Add anomaly detection rules

**Expected Impact:**
- ✅ Stolen tokens auto-expire
- ✅ Detect suspicious activity
- ✅ Email alerts for new devices

### Phase 3: Advanced Features (Week 3)
- [ ] **Day 1-2**: Implement sliding sessions
- [ ] **Day 3**: Add "Remember Me" functionality
- [ ] **Day 4-5**: Token monitoring and metrics

**Expected Impact:**
- ✅ Better UX with sliding sessions
- ✅ Optional long sessions
- ✅ Visibility into auth health

### Phase 4: Production Hardening (Week 4)
- [ ] Load testing auth endpoints
- [ ] Add rate limiting per device
- [ ] Implement account lockout policies
- [ ] Security audit and penetration testing

---

## 🔧 CONFIGURATION RECOMMENDATIONS

### Update `config/settings.py`
```python
# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Reduce to 15 min (auto-refresh handles this)
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # Keep 7 days
JWT_REFRESH_ROTATION_ENABLED: bool = True   # ✅ NEW: Enable token rotation
JWT_SLIDING_SESSION_ENABLED: bool = True    # ✅ NEW: Enable sliding sessions
JWT_SLIDING_SESSION_MAX_HOURS: int = 12     # ✅ NEW: Max regular session
JWT_REMEMBER_ME_MAX_DAYS: int = 30          # ✅ NEW: Max "remember me" session

# Authentication Security
AUTH_TIMEOUT_SECONDS: int = 5               # ✅ NEW: Auth timeout
AUTH_MAX_DEVICES_PER_USER: int = 10         # ✅ NEW: Max simultaneous devices
AUTH_ANOMALY_DETECTION_ENABLED: bool = True # ✅ NEW: Enable anomaly detection
AUTH_DEVICE_FINGERPRINT_REQUIRED: bool = True # ✅ NEW: Require device tracking

# Rate Limiting
AUTH_RATE_LIMIT_PER_IP: int = 5             # Max login attempts per IP per minute
AUTH_RATE_LIMIT_PER_USER: int = 10          # Max login attempts per user per hour
AUTH_ACCOUNT_LOCKOUT_ATTEMPTS: int = 5      # Lock account after N failed attempts
AUTH_ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 15  # Lockout duration
```

---

## 🧪 TESTING RECOMMENDATIONS

### Unit Tests
```python
# tests/test_auth/test_token_refresh.py

async def test_token_auto_refresh():
    """Test automatic token refresh before expiry"""
    # Create token that expires in 30 seconds
    token = create_short_lived_token(expires_in=30)

    # Simulate request 25 seconds later (within buffer)
    await asyncio.sleep(25)

    # Should auto-refresh
    new_token = await tokenRefreshManager.refreshToken()
    assert new_token != token
    assert is_token_valid(new_token)

async def test_token_rotation():
    """Test refresh token rotation"""
    refresh_token = create_refresh_token(user_id=1)

    # Refresh
    result = await security_manager.refresh_access_token(refresh_token)
    new_refresh = result["refresh_token"]

    # Old refresh token should be invalid
    with pytest.raises(AuthenticationError):
        await security_manager.refresh_access_token(refresh_token)

    # New refresh token should work
    result2 = await security_manager.refresh_access_token(new_refresh)
    assert result2["access_token"]

async def test_anomaly_detection():
    """Test suspicious activity detection"""
    user_id = 1

    # Simulate 15 logins in 5 minutes (suspicious)
    for i in range(15):
        await attempt_login(user_id, ip=f"192.168.1.{i}")

    # Should flag as suspicious
    is_suspicious, reason = await detect_suspicious_activity(user_id)
    assert is_suspicious
    assert "Too many login attempts" in reason
```

### Integration Tests
```typescript
// tests/integration/auth.test.ts

describe('Token Refresh Flow', () => {
  it('should auto-refresh token before expiry', async () => {
    // Login
    const { token } = await login('user@example.com', 'password');

    // Wait until token is about to expire
    await waitForTokenExpiry(token, bufferSeconds: 10);

    // Make API request - should auto-refresh
    const response = await apiClient.get('/api/user-bot/status');

    // Should succeed without manual re-login
    expect(response.status).toBe(200);

    // Token should be different (refreshed)
    const newToken = localStorage.getItem('auth_token');
    expect(newToken).not.toBe(token);
  });

  it('should handle 401 and retry with refreshed token', async () => {
    // Set expired token
    localStorage.setItem('auth_token', EXPIRED_TOKEN);
    localStorage.setItem('refresh_token', VALID_REFRESH_TOKEN);

    // Make API request
    const response = await apiClient.get('/api/user-bot/status');

    // Should auto-refresh and succeed
    expect(response.status).toBe(200);
  });
});
```

---

## 📚 ADDITIONAL RESOURCES

### Security Best Practices
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [JWT Best Practices (RFC 8725)](https://datatracker.ietf.org/doc/html/rfc8725)
- [OAuth 2.0 Threat Model](https://datatracker.ietf.org/doc/html/rfc6819)

### Libraries to Consider
- **Frontend**: `axios-auth-refresh` - automatic token refresh for Axios
- **Backend**: `python-jose` - JWT library (already using ✅)
- **Monitoring**: Prometheus + Grafana for auth metrics
- **Device Fingerprinting**: FingerprintJS (commercial) or DIY solution

---

## ✅ SUCCESS METRICS

### After Implementation

**User Experience:**
- 📊 Zero unexpected logouts (down from current issues)
- 📊 <5s authentication response time (down from 90s)
- 📊 99.9% token refresh success rate
- 📊 <1% manual re-login rate

**Security:**
- 🔒 Token rotation enabled (100% of refreshes)
- 🔒 Anomaly detection active
- 🔒 Device tracking for all users
- 🔒 <1% suspicious activity rate

**Operations:**
- 📈 Auth endpoint latency p99 < 500ms
- 📈 Token refresh latency p99 < 200ms
- 📉 401 error rate < 0.1%
- 📉 Auth timeout rate < 0.01%

---

## 🎯 CONCLUSION

Your current token system has a solid foundation (refresh tokens, JWT, session management), but needs:

1. **CRITICAL**: Automatic token refresh in frontend
2. **HIGH**: Token rotation for security
3. **HIGH**: Fast-fail auth (5s timeout instead of 90s)
4. **MEDIUM**: Sliding sessions and "remember me"
5. **RECOMMENDED**: Device fingerprinting and monitoring

**Estimated effort:**
- Phase 1 (Critical): ~3-5 days
- Phase 2 (Security): ~3-5 days
- Phase 3 (Advanced): ~3-5 days
- Phase 4 (Hardening): ~5-7 days

**Total: ~3-4 weeks** for production-ready auth system

Start with Phase 1 (automatic refresh + fast-fail) for immediate UX improvement! 🚀
