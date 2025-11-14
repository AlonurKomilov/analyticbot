# 🔧 API URL Configuration Changes

## Summary
Fixed all hardcoded API URLs in the frontend to use **relative URLs** (empty string) instead of old CloudFlare tunnel URLs.

---

## Problem
Frontend was still making requests to old tunnel URL:
```
https://ongoing-ear-asus-piano.trycloudflare.com/health/
```

This caused **CORS errors** because:
- Frontend domain: `https://analyticbot.org`
- API requests going to: `https://ongoing-ear-asus-piano.trycloudflare.com`
- Different origins = CORS blocked ❌

---

## Solution
Use **relative URLs** (empty baseURL) so all requests go to the same domain:
```
https://analyticbot.org/health  ✅
```

---

## Files Changed

### 1. `.env.local` (Environment Variables)
**Before:**
```bash
VITE_API_BASE_URL=https://ongoing-ear-asus-piano.trycloudflare.com
VITE_API_URL=https://ongoing-ear-asus-piano.trycloudflare.com
```

**After:**
```bash
VITE_API_BASE_URL=
VITE_API_URL=
```

### 2. `src/api/client.ts` (Main API Client)
**Before:**
```typescript
baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:11400'
```

**After:**
```typescript
baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''
```

### 3. `src/config/env.ts` (Environment Config)
**Before:**
```typescript
API_BASE_URL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms'
```

**After:**
```typescript
API_BASE_URL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''
```

### 4. `src/utils/initializeApp.ts` (App Initialization)
**Before:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms'
```

**After:**
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || ''
```

### 5. `src/shared/services/api/apiClient.ts` (Shared API Client)
**Before:**
```typescript
baseURL: import.meta.env.VITE_API_BASE_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms'
```

**After:**
```typescript
baseURL: import.meta.env.VITE_API_BASE_URL || ''
```

### 6. `src/shared/components/ui/DataSourceSettings.tsx` (Health Check)
**Before:**
```typescript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ||
                  import.meta.env.VITE_API_URL ||
                  'https://b2qz1m0n-11400.euw.devtunnels.ms'
```

**After:**
```typescript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ||
                  import.meta.env.VITE_API_URL ||
                  ''
```

---

## How It Works Now

### Request Flow:
1. **Frontend makes request:** `fetch('/health')`
2. **Browser sees relative URL:** Prepends current domain → `https://analyticbot.org/health`
3. **Vite proxy intercepts:** Matches `/health` pattern
4. **Proxy forwards to:** `http://127.0.0.1:11400/health`
5. **Backend responds:** JSON data
6. **Proxy returns to browser:** Same origin ✅

### Benefits:
- ✅ **No CORS errors** - Same domain for all requests
- ✅ **Clean URLs** - `analyticbot.org/health` instead of tunnel URLs
- ✅ **Flexible** - Works in any environment (dev, staging, prod)
- ✅ **Secure** - No hardcoded URLs to change
- ✅ **Fast** - No external tunnels in production

---

## Testing

### Check Configuration:
```bash
# Verify .env.local
cat apps/frontend/.env.local

# Should show:
# VITE_API_BASE_URL=
# VITE_API_URL=
```

### Test Endpoints:
```bash
# Local (through proxy)
curl http://localhost:11300/health

# Production domain
curl https://analyticbot.org/health

# Should both return:
# {"status":"healthy", ...}
```

### Browser Console:
Open https://analyticbot.org and check console - should see:
```
🔧 Unified API Client Configuration: {baseURL: '', timeout: 30000, ...}
```

**Note:** Empty `baseURL` means relative URLs ✅

---

## Troubleshooting

### Still seeing old tunnel URLs?

1. **Hard refresh browser:**
   - Chrome/Firefox: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
   - Clear browser cache

2. **Restart Vite:**
   ```bash
   pkill -f "vite.*11300"
   cd apps/frontend && npx vite --port 11300 --host 0.0.0.0
   ```

3. **Verify .env.local:**
   ```bash
   cat apps/frontend/.env.local
   # Must have empty values:
   # VITE_API_BASE_URL=
   ```

4. **Check for other .env files:**
   ```bash
   # These might override .env.local
   ls -la apps/frontend/.env*
   ```

### CORS errors still appearing?

Should NOT happen with this setup. If you see CORS:
1. Verify frontend is making relative requests (check Network tab)
2. Ensure Vite proxy is running and configured
3. Check browser is accessing via `analyticbot.org` (not localhost)

---

## Important Notes

### ⚠️ Don't change these back!

The `.env.local` file should ALWAYS have empty values:
```bash
VITE_API_BASE_URL=
VITE_API_URL=
```

**Why?** Because:
- Empty = relative URLs
- Relative URLs = same domain
- Same domain = no CORS
- Vite proxy handles routing to backend

### 🔒 Environment-specific URLs (if needed)

If you need different URLs for different environments:

**Development** (already using proxy):
```bash
VITE_API_BASE_URL=
```

**Staging** (if you have separate staging server):
```bash
VITE_API_BASE_URL=https://staging.analyticbot.org
```

**Production** (same domain):
```bash
VITE_API_BASE_URL=
```

---

## Summary

**Old Setup:**
- ❌ Hardcoded tunnel URLs everywhere
- ❌ CORS errors
- ❌ Complex configuration
- ❌ Different domains

**New Setup:**
- ✅ Relative URLs (empty baseURL)
- ✅ No CORS errors
- ✅ Simple configuration
- ✅ Same domain for everything

**Result:** Clean, production-ready API configuration! 🎉

---

**Fixed Date:** November 14, 2025
**Status:** ✅ All hardcoded URLs removed
**CORS Issues:** ✅ Resolved
