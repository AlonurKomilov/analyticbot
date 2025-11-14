# ✅ API Configuration - Direct Access (No /api Prefix)

## Configuration Complete!

Your API is now accessible **directly** without the `/api` prefix:

### ✅ Before vs After

**Before:**
- ❌ `https://analyticbot.org/api/health`
- ❌ `https://analyticbot.org/api/channels`
- ❌ `https://analyticbot.org/api/analytics`

**After:**
- ✅ `https://analyticbot.org/health`
- ✅ `https://analyticbot.org/channels`
- ✅ `https://analyticbot.org/analytics`

---

## 🔧 Changes Made

### 1. **Vite Proxy Configuration** (`apps/frontend/vite.config.js`)

```javascript
server: {
  port: 11300,
  host: '0.0.0.0',
  proxy: {
    '^/(health|docs|openapi\\.json|auth|channels|analytics|insights|predictions|alerts|payment|superadmin|telegram-storage)': {
      target: 'http://127.0.0.1:11400',
      changeOrigin: true,
      secure: false,
      ws: true,
    }
  }
}
```

**What it does:**
- Intercepts requests to API endpoints
- Forwards them to backend at `127.0.0.1:11400`
- Returns response to client
- Client sees `https://analyticbot.org/health` (clean URL)

### 2. **Environment Variables** (`.env.local`)

```bash
# Use empty string for relative URLs (same-domain)
VITE_API_BASE_URL=
VITE_API_URL=
```

**What it does:**
- Frontend makes requests to same domain
- No CORS issues
- Cleaner URLs

### 3. **CloudFlare Tunnel** (`~/.cloudflared/config.yml`)

```yaml
ingress:
  - hostname: analyticbot.org
    service: http://localhost:11300  # Routes to frontend
  - hostname: www.analyticbot.org
    service: http://localhost:11300
  - service: http_status:404
```

**What it does:**
- CloudFlare routes all traffic to frontend (port 11300)
- Vite proxy handles API routing internally
- Single entry point for all requests

---

## 📋 Available Endpoints (Direct Access)

### Authentication
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Channels
- `GET /channels`
- `GET /channels/{id}`
- `POST /channels`

### Analytics
- `GET /analytics/overview`
- `GET /analytics/posts`
- `GET /analytics/engagement`

### Insights
- `GET /insights/recommendations`
- `GET /insights/trends`

### Predictions
- `GET /predictions/forecast`

### Alerts
- `GET /alerts`
- `POST /alerts`

### Payment
- `POST /payment/create-checkout-session`
- `GET /payment/plans`

### System
- `GET /health` - Health check
- `GET /docs` - API documentation
- `GET /openapi.json` - OpenAPI schema

---

## 🧪 Testing

### Test from Command Line

```bash
# Health check
curl https://analyticbot.org/health

# API documentation
curl https://analyticbot.org/docs

# With authentication
curl -H "Authorization: Bearer YOUR_TOKEN" https://analyticbot.org/channels
```

### Test from Browser

- **Health:** https://analyticbot.org/health
- **Docs:** https://analyticbot.org/docs
- **Frontend:** https://analyticbot.org

### Test Locally

```bash
# Through proxy (same as production)
curl http://localhost:11300/health

# Direct backend (bypassing proxy)
curl http://127.0.0.1:11400/health
```

---

## 🏗️ Architecture Flow

```
User Browser
    ↓
https://analyticbot.org/health
    ↓
CloudFlare CDN (SSL/DDoS)
    ↓
CloudFlare Tunnel (analyticbot-prod)
    ↓
localhost:11300 (Vite Frontend)
    ↓ [Proxy Match: /health]
127.0.0.1:11400 (FastAPI Backend)
    ↓
PostgreSQL/Redis
```

### How It Works:

1. **User requests:** `https://analyticbot.org/health`
2. **CloudFlare** routes to tunnel → `localhost:11300`
3. **Vite proxy** sees `/health` matches pattern
4. **Proxy forwards** to `127.0.0.1:11400/health`
5. **Backend responds** with JSON
6. **Proxy returns** response to user

---

## 🔄 Frontend API Client Usage

Your frontend can now make requests like:

```typescript
// Old way (with /api prefix)
fetch('/api/health')  // ❌ No longer needed

// New way (direct)
fetch('/health')  // ✅ Clean and simple
fetch('/channels')  // ✅
fetch('/analytics/overview')  // ✅
```

The `VITE_API_BASE_URL` is empty, so all requests are relative:

```typescript
// api/client.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Makes request to: https://analyticbot.org/health (same domain)
fetch(`${API_BASE_URL}/health`)
```

---

## 🐛 Troubleshooting

### Issue: 404 Not Found

**Check if endpoint is in proxy regex:**
```javascript
'^/(health|docs|...|YOUR_ENDPOINT)'
```

**Add new endpoint:**
```javascript
'^/(health|docs|...|new-endpoint)'
```

**Restart Vite:**
```bash
cd /home/abcdeveloper/projects/analyticbot
pkill -f "vite.*11300"
cd apps/frontend && npx vite --port 11300 --host 0.0.0.0
```

### Issue: Proxy Not Working

**Check Vite is running:**
```bash
ps aux | grep vite
```

**Check logs:**
```bash
tail -f /tmp/vite-fixed.log
```

**Test locally first:**
```bash
# Direct backend
curl http://127.0.0.1:11400/health

# Through proxy
curl http://localhost:11300/health
```

### Issue: CORS Errors

**Should not happen** since frontend and API are on same domain now!

If you see CORS errors:
1. Check `VITE_API_BASE_URL` is empty in `.env.local`
2. Restart frontend
3. Clear browser cache

---

## 📝 Maintenance

### Adding New API Endpoint

1. **Update proxy regex** in `vite.config.js`:
```javascript
'^/(health|...|new-endpoint)'
```

2. **Restart Vite:**
```bash
pkill -f "vite.*11300"
cd apps/frontend && npx vite --port 11300 --host 0.0.0.0 &
```

3. **Test:**
```bash
curl http://localhost:11300/new-endpoint
```

### Updating Configuration

**Frontend:**
```bash
cd /home/abcdeveloper/projects/analyticbot/apps/frontend
nano vite.config.js  # Edit proxy
pkill -f "vite.*11300"  # Restart
npx vite --port 11300 --host 0.0.0.0 &
```

**Tunnel:**
```bash
nano ~/.cloudflared/config.yml  # Edit config
sudo cp ~/.cloudflared/config.yml /etc/cloudflared/
sudo systemctl restart cloudflared  # Restart
```

---

## 🎉 Benefits of This Setup

1. **✅ Clean URLs** - No `/api` prefix needed
2. **✅ No CORS Issues** - Same domain for frontend and API
3. **✅ Easier to Use** - Simpler API calls
4. **✅ Better SEO** - Clean URL structure
5. **✅ Single Domain** - Everything under `analyticbot.org`
6. **✅ Flexible** - Easy to add new endpoints

---

## 📊 Quick Reference

| What | URL |
|------|-----|
| Frontend | https://analyticbot.org |
| Health Check | https://analyticbot.org/health |
| API Docs | https://analyticbot.org/docs |
| Channels API | https://analyticbot.org/channels |
| Analytics API | https://analyticbot.org/analytics |
| Auth API | https://analyticbot.org/auth |

---

**Configuration Date:** November 14, 2025  
**Status:** ✅ Active  
**Type:** Direct API Access (No /api Prefix)
