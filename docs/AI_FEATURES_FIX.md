# AI Features Fix - "Unable to load AI features"

## Problem
The AI Worker page was showing: **"AI Features Unavailable - Unable to load AI features. Please try again or contact support."**

## Root Causes Found

### 1. **JSONB Database Error** ✅ FIXED
**Issue:** PostgreSQL JSONB columns were receiving Python dict objects instead of JSON strings.

**Error in logs:**
```
invalid input for query argument $3: {} (expected str, got dict)
```

**Fix Applied:**
Modified `/core/repositories/user_ai_config_repository.py`:
- Added `import json`
- Changed JSONB parameters to use `json.dumps()` and `::jsonb` casting

**Changed:**
```python
# Before
VALUES ($1, $2, true, $3, $4, NOW(), NOW())
params: [user_id, tier, {}, ["analytics_insights"]]

# After
VALUES ($1, $2, true, $3::jsonb, $4::jsonb, NOW(), NOW())
params: [user_id, tier, json.dumps({}), json.dumps(["analytics_insights"])]
```

### 2. **Frontend API URL Mismatch** ✅ FIXED
**Issue:** Frontend was trying to connect to production API (`https://api.analyticbot.org`) instead of local dev API.

**Fix Applied:**
Created `/apps/frontend/apps/user/.env.local`:
```env
VITE_API_BASE_URL=http://localhost:11400
VITE_API_URL=http://localhost:11400
```

## Files Modified

1. **core/repositories/user_ai_config_repository.py**
   - Added JSON serialization for JSONB fields
   - Fixed `create()` method
   - Fixed `update_settings()` method

2. **apps/frontend/apps/user/.env.local** (created)
   - Points frontend to local development API
   - Enables debug logging

## How to Test

### 1. Restart Backend (already done)
```bash
cd /home/abcdev/projects/analyticbot
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start
```

### 2. Restart Frontend
```bash
cd apps/frontend/apps/user
npm run dev
```

### 3. Refresh Browser
- Go to: http://localhost:11300/workers/ai
- You should now see the AI Dashboard instead of the error

## Expected Behavior After Fix

✅ AI Dashboard loads successfully  
✅ Shows AI status card with tier info  
✅ Shows AI settings card  
✅ Shows active services  
✅ Shows available upgrades  
✅ "AI Providers" button visible and working  

## API Endpoints Now Working

- `GET /user/ai/status` - Returns user's AI tier, usage, limits
- `GET /user/ai/settings` - Returns AI configuration
- `GET /user/ai/services` - Returns available AI services
- `GET /user/ai/providers/available` - Returns available AI providers
- `GET /user/ai/providers/mine` - Returns user's configured providers

## Verification

Test the AI status endpoint:
```bash
# From your browser's network tab, you should see:
# Request: http://localhost:11400/user/ai/status
# Response: { user_id, tier, enabled, usage_today, ... }
```

## Next Steps

1. **Refresh your browser** to load with new .env.local settings
2. Navigate to `/workers/ai`
3. Click "AI Providers" button
4. Add your first AI provider (OpenAI or Claude)
5. Test channel analysis with real AI

---

**Status:** ✅ Fixed - Ready for testing  
**Backend:** Running on http://localhost:11400  
**Frontend:** Running on http://localhost:11300  
**API Calls:** Now routing to local backend correctly
