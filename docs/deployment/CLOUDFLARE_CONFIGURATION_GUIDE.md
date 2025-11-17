# ✅ Complete Configuration Summary - analyticbot.org

## Current Status
- ✅ Nginx configured correctly
- ✅ Frontend deployed at `/var/www/analyticbot/frontend/`
- ✅ API running on port 11400
- ✅ SSL certificates in place
- ❌ **Cloudflare routing to wrong port**

---

## 🔴 PROBLEM IDENTIFIED

**Cloudflare is routing directly to port 11400 (API) instead of port 443 (nginx)**

### Evidence:
```bash
# Direct nginx test (works):
curl -k -H "Host: www.analyticbot.org" https://127.0.0.1/auth?mode=login
# Returns: HTML (index.html) ✅

# Via Cloudflare (broken):
curl -s https://www.analyticbot.org/auth?mode=login
# Returns: {"detail":"Not Found"} ❌ (from API, not frontend)
```

---

## ✅ SOLUTION: Fix Cloudflare Configuration

### Option 1: DNS Records (Recommended)

Go to **Cloudflare Dashboard** → **DNS** → **DNS Records**

#### 1. Frontend Domain Records
```
Type: A
Name: www
Content: 138.201.243.107 (your server IP)
Proxy status: ✅ Proxied (orange cloud)
TTL: Auto

Type: A
Name: @
Content: 138.201.243.107
Proxy status: ✅ Proxied (orange cloud)
TTL: Auto
```

#### 2. API Subdomain Record
```
Type: A
Name: api
Content: 138.201.243.107
Proxy status: ✅ Proxied (orange cloud)
TTL: Auto
```

**IMPORTANT:** Cloudflare should connect on default ports (80/443), NOT custom ports!

---

### Option 2: Cloudflare Tunnel (If Using)

If you're using Cloudflare Tunnel, update `/etc/cloudflared/config.yml`:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  # Frontend - Route to NGINX (port 443)
  - hostname: www.analyticbot.org
    service: https://localhost:443
    originRequest:
      noTLSVerify: true

  - hostname: analyticbot.org
    service: https://localhost:443
    originRequest:
      noTLSVerify: true

  # API Subdomain - Route to NGINX (port 443), nginx proxies to 11400
  - hostname: api.analyticbot.org
    service: https://localhost:443
    originRequest:
      noTLSVerify: true

  # Catch-all
  - service: http_status:404
```

**After updating, restart tunnel:**
```bash
sudo systemctl restart cloudflared
```

---

## 🏗️ Current Architecture (Correct Setup)

```
┌─────────────────────────────────────────────────────────────┐
│                       CLOUDFLARE CDN                         │
│  • www.analyticbot.org                                      │
│  • analyticbot.org                                          │
│  • api.analyticbot.org                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ Port 443 (HTTPS)
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (Port 443)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ www.analyticbot.org                                    │ │
│  │ • Serves: /var/www/analyticbot/frontend/              │ │
│  │ • Returns: index.html for all routes                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ api.analyticbot.org                                    │ │
│  │ • Proxies to: http://127.0.0.1:11400                  │ │
│  │ • Handles: /health, /auth, /api/*, etc.               │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ Port 11400 (HTTP)
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (Port 11400)                 │
│  • Authentication: /auth/*                                   │
│  • API Endpoints: /api/*                                     │
│  • Health Check: /health                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 What Was Fixed in This Session

### 1. Nginx Configuration ✅
- Frontend config: `/etc/nginx/sites-available/frontend.analyticbot.conf`
- API config: `/etc/nginx/sites-available/api.analyticbot.conf`
- Fixed `root` path: `/var/www/analyticbot/frontend/` (not `/dist/`)

### 2. Frontend Code ✅
- **Vite Config** (`apps/frontend/vite.config.js`):
  - ✅ Removed hardcoded devtunnels URL
  - ✅ Fixed proxy configuration for local development
  - ✅ Proper proxy routes: `/api`, `/auth`, `/health`, `/docs`

- **API Client** (`apps/frontend/src/api/client.ts`):
  - ✅ Simplified baseURL detection
  - ✅ Respects `.env.production` in production builds

- **Environment Files**:
  - ✅ `.env.local`: Uses `http://localhost:11400` (local dev)
  - ✅ `.env.production`: Uses `https://api.analyticbot.org` (production)

### 3. Deployment Script ✅
- Created: `scripts/deploy-frontend.sh`
- Builds with production config
- Deploys to `/var/www/analyticbot/frontend/`
- Sets correct permissions
- Reloads nginx

---

## ✅ Verification Commands

### Test Nginx Locally (Bypassing Cloudflare)
```bash
# Should return HTML
curl -k -H "Host: www.analyticbot.org" https://127.0.0.1/auth?mode=login

# Should return JSON health check
curl -k -H "Host: api.analyticbot.org" https://127.0.0.1/health
```

### Test via Cloudflare (After DNS Fix)
```bash
# Should return HTML
curl -s https://www.analyticbot.org/auth?mode=login | head -20

# Should return JSON health check
curl -s https://api.analyticbot.org/health
```

---

## 🚀 Next Steps

1. **Fix Cloudflare DNS/Tunnel** (see solutions above)
2. **Wait 1-2 minutes** for DNS propagation
3. **Test in browser**: https://www.analyticbot.org
4. **Verify API**: https://api.analyticbot.org/health

---

## 📞 Need Help?

If you need help configuring Cloudflare:
1. Share your Cloudflare Tunnel config (if using tunnel)
2. Share DNS records screenshot from Cloudflare dashboard
3. Check if you're using Cloudflare Tunnel or just DNS

---

## 🎯 Expected Behavior After Fix

| URL | Should Serve | Status |
|-----|--------------|--------|
| `https://www.analyticbot.org/` | React SPA (index.html) | ✅ |
| `https://www.analyticbot.org/auth?mode=login` | React SPA (index.html) | ✅ |
| `https://www.analyticbot.org/dashboard` | React SPA (index.html) | ✅ |
| `https://api.analyticbot.org/health` | JSON health check | ✅ |
| `https://api.analyticbot.org/auth/login` | API endpoint | ✅ |
| `https://api.analyticbot.org/api/storage/channels` | API endpoint | ✅ |

---

**Status**: Ready for Cloudflare configuration update
