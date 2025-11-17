# 🚀 Quick Fix: API Showing Instead of Frontend

## Problem
After refreshing pages on analyticbot.org, you see API JSON responses instead of your frontend.

## Root Cause
Both frontend and API are on the same domain without proper routing. When you visit `/auth`, the server doesn't know if you want the frontend route or API route.

## ✅ Quick Solution (Recommended)

### Option 1: Use API Prefix `/api/v1` ⭐ BEST

This is the industry standard (GitHub, Stripe, Twitter use this).

**30-Minute Fix:**

1. **Backend**: Add `/api/v1` prefix to all routes
2. **Frontend**: Update API base URL to include `/api/v1`
3. **Nginx**: Configure proper routing (file already created)

**Pros:**
- ✅ Same domain (no CORS issues)
- ✅ One SSL certificate
- ✅ Standard practice
- ✅ SEO friendly

**See**: `SAME_DOMAIN_SOLUTION.md` for detailed steps

---

### Option 2: Use Subdomain `api.analyticbot.org` ⭐ ENTERPRISE

Separate API on subdomain for better scalability.

**1-Hour Setup:**

1. **DNS**: Add A record for `api.analyticbot.org`
2. **SSL**: Get certificate for subdomain
3. **Nginx**: Separate server blocks
4. **Frontend**: Update API URL to `https://api.analyticbot.org`

**Pros:**
- ✅ Clean separation
- ✅ Better for large apps
- ✅ Easier to scale

**Cons:**
- ⚠️ CORS configuration needed
- ⚠️ Extra DNS/SSL setup

---

## 📋 Quick Start (Option 1 - API Prefix)

### Step 1: Update Backend (5 min)

**File**: `apps/api/main.py`

```python
# Find line ~390 and update:

# OLD (current)
app.include_router(auth_router)
app.include_router(channels_router)

# NEW (with prefix)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(channels_router, prefix="/api/v1")

# Do this for ALL routers except /health
```

### Step 2: Update Frontend (2 min)

**File**: `apps/frontend/.env.production`

```bash
# OLD
VITE_API_BASE_URL=https://www.analyticbot.org

# NEW
VITE_API_BASE_URL=https://www.analyticbot.org/api/v1
```

### Step 3: Deploy Nginx Config (5 min)

```bash
# Copy production nginx config
sudo cp infra/nginx/analyticbot.prod.conf /etc/nginx/sites-available/analyticbot

# Enable site
sudo ln -s /etc/nginx/sites-available/analyticbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Step 4: Test (2 min)

```bash
# Test API
curl https://www.analyticbot.org/api/v1/health
# Should return: {"status":"healthy"}

# Test frontend
curl https://www.analyticbot.org/
# Should return: HTML with <!DOCTYPE html>

# Test SPA routing
curl https://www.analyticbot.org/auth
# Should return: HTML (not JSON!)
```

---

## 🎯 Why This Happens

### Current Setup (Broken):
```
Frontend URL: /auth           → Server sees "/auth"
Backend URL:  /auth/login     → Server sees "/auth/login"

Problem: Server confused which "/auth" you want!
```

### Fixed Setup (Working):
```
Frontend URL: /auth           → Nginx: Serve index.html
Backend URL:  /api/v1/auth/login → Nginx: Proxy to :11400

Clear separation! No confusion!
```

---

## 📊 How Nginx Routes Requests

```nginx
# Request: https://analyticbot.org/auth?mode=login
# ↓
# Nginx checks:
#   1. Is it /api/v1/*? → NO → Continue
#   2. Is it a file? → NO → Continue
#   3. Is it a directory? → NO → Continue
#   4. Fallback to index.html → YES! ✅
# ↓
# Serves: /var/www/analyticbot/frontend/dist/index.html
# ↓
# React Router: Sees /auth?mode=login → Shows Login Page ✅
```

```nginx
# Request: https://analyticbot.org/api/v1/auth/login
# ↓
# Nginx checks:
#   1. Is it /api/v1/*? → YES! ✅
# ↓
# Proxies to: http://localhost:11400/api/v1/auth/login
# ↓
# FastAPI: Returns JSON {"access_token": "..."} ✅
```

---

## 🆘 Still Having Issues?

### Issue 1: API returns 404

**Check:**
```bash
# Is backend running?
curl http://localhost:11400/api/v1/health

# If not, start it:
cd /home/abcdeveloper/projects/analyticbot
source venv/bin/activate
uvicorn apps.api.main:app --host 0.0.0.0 --port 11400
```

### Issue 2: Still seeing JSON on frontend routes

**Check:**
```bash
# Is Nginx config correct?
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Issue 3: CORS errors

**Fix in** `apps/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.analyticbot.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📁 Files Already Created

✅ `infra/nginx/analyticbot.prod.conf` - Production Nginx config
✅ `SAME_DOMAIN_SOLUTION.md` - Detailed implementation guide
✅ `QUICK_API_FIX.md` - This file

---

## ⏱️ Time Estimate

- **Option 1 (API Prefix)**: 30-45 minutes
- **Option 2 (Subdomain)**: 1-2 hours

---

## 🎯 Recommendation

**Use Option 1**: API Prefix `/api/v1`

This is what I recommend because:
1. Fastest to implement
2. Industry standard
3. No CORS issues
4. One domain, one SSL cert
5. Same pattern as GitHub, Stripe, Twitter

---

**Next Step**: Read `SAME_DOMAIN_SOLUTION.md` for complete implementation guide.
