# 🌐 Same Domain Solution - Frontend & API Configuration

## 🔍 Problem Analysis

You're seeing API JSON responses instead of frontend HTML because:

1. **Root Route Conflict**: Your API has routes at root level (`/health`, `/auth/login`, etc.)
2. **Nginx Missing Configuration**: When you refresh `/auth?mode=login`, the browser requests `/auth` from server
3. **Server Returns API Response**: Without proper routing rules, server sends API JSON instead of frontend HTML

## ✅ Recommended Solution: API Prefix Pattern

**Best Practice**: Serve API under `/api/v1/*` prefix and frontend at root `/`

### Architecture:
```
https://analyticbot.org/              → Frontend (React SPA)
https://analyticbot.org/auth          → Frontend route
https://analyticbot.org/dashboard     → Frontend route

https://analyticbot.org/api/v1/health → Backend API
https://analyticbot.org/api/v1/auth/login → Backend API
https://analyticbot.org/api/v1/channels → Backend API
```

---

## 🚀 Implementation Steps

### Step 1: Update Backend API Prefix

**File**: `/apps/api/main.py`

Add API prefix to all routers (except special cases):

```python
# After line 390, wrap routers with /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(channels_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
# ... etc for all routers

# Keep root /health for monitoring (special case)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Step 2: Update Frontend API Client

**File**: `/apps/frontend/src/api/client.ts` or similar

Update API base URL to include `/api/v1`:

```typescript
// Current (wrong)
const API_BASE_URL = 'https://analyticbot.org'

// Updated (correct)
const API_BASE_URL = 'https://analyticbot.org/api/v1'
```

### Step 3: Configure Nginx for Production

**File**: `/infra/nginx/analyticbot.prod.conf` (create new)

```nginx
# ============================================================================
# AnalyticBot Production Nginx Configuration
# Domain: analyticbot.org
# ============================================================================

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name analyticbot.org www.analyticbot.org;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/analyticbot.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/analyticbot.org/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https://telegram.org https://*.telegram.org; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://telegram.org; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;

    # Logging
    access_log /var/log/nginx/analyticbot_access.log;
    error_log /var/log/nginx/analyticbot_error.log warn;

    # ========================================================================
    # API Routes - Proxy to Backend
    # ========================================================================

    # API v1 endpoints
    location /api/v1/ {
        proxy_pass http://localhost:11400/api/v1/;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support (if needed)
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint (monitoring)
    location /health {
        proxy_pass http://localhost:11400/health;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        access_log off;
    }

    # API documentation (Swagger/OpenAPI)
    location /docs {
        proxy_pass http://localhost:11400/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /openapi.json {
        proxy_pass http://localhost:11400/openapi.json;
        proxy_set_header Host $host;
    }

    # ========================================================================
    # Frontend - React SPA
    # ========================================================================

    # Frontend root directory
    root /var/www/analyticbot/frontend/dist;
    index index.html;

    # Static assets with aggressive caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|webp|avif)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # Service worker (no caching)
    location = /service-worker.js {
        expires off;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        try_files $uri =404;
    }

    # Manifest and favicon
    location ~* \.(json|webmanifest|xml)$ {
        expires 7d;
        add_header Cache-Control "public";
        try_files $uri =404;
    }

    # Frontend SPA - All other routes
    location / {
        try_files $uri $uri/ /index.html;

        # No caching for HTML
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # ========================================================================
    # Security & Rate Limiting
    # ========================================================================

    # Rate limiting zones (defined in http block)
    # limit_req zone=api burst=20 nodelay;

    # Block common exploits
    location ~* (\.php|\.asp|\.aspx|\.jsp)$ {
        return 404;
    }

    # Block hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# ============================================================================
# HTTP to HTTPS Redirect
# ============================================================================
server {
    listen 80;
    listen [::]:80;
    server_name analyticbot.org www.analyticbot.org;

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# ============================================================================
# Redirect www to non-www (or vice versa)
# ============================================================================
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name analyticbot.org;

    ssl_certificate /etc/letsencrypt/live/analyticbot.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/analyticbot.org/privkey.pem;

    # Redirect to www
    return 301 https://www.analyticbot.org$request_uri;
}
```

### Step 4: Update Environment Variables

**Backend** (`.env`):
```bash
# API will be accessed via /api/v1 prefix
FRONTEND_URL=https://www.analyticbot.org
CORS_ORIGINS=https://www.analyticbot.org,https://analyticbot.org
```

**Frontend** (`.env.production`):
```bash
# API accessed on same domain with /api/v1 prefix
VITE_API_BASE_URL=https://www.analyticbot.org/api/v1
VITE_API_URL=https://www.analyticbot.org/api/v1
```

---

## 🔧 Alternative Solution: Separate Subdomains

If you prefer keeping API routes without prefix:

### Architecture:
```
https://analyticbot.org           → Frontend
https://api.analyticbot.org       → Backend API
```

### Pros:
- ✅ No API code changes needed
- ✅ Clean separation of concerns
- ✅ Easier to scale separately
- ✅ Better caching strategies

### Cons:
- ⚠️ Requires DNS configuration
- ⚠️ Need SSL cert for subdomain
- ⚠️ CORS configuration more complex

### Implementation:

**DNS Records**:
```
A    analyticbot.org       → SERVER_IP
A    www.analyticbot.org   → SERVER_IP
A    api.analyticbot.org   → SERVER_IP
```

**Nginx Configuration**:
```nginx
# Frontend
server {
    listen 443 ssl http2;
    server_name www.analyticbot.org analyticbot.org;
    root /var/www/analyticbot/frontend/dist;
    # ... frontend config
}

# API
server {
    listen 443 ssl http2;
    server_name api.analyticbot.org;

    location / {
        proxy_pass http://localhost:11400;
        # ... proxy config
    }
}
```

**Frontend Environment**:
```bash
VITE_API_BASE_URL=https://api.analyticbot.org
```

---

## 📊 Comparison: Same Domain vs Subdomain

| Feature | Same Domain (/api/v1) | Subdomain (api.) |
|---------|----------------------|------------------|
| **Setup Complexity** | ⭐⭐ Simple | ⭐⭐⭐ Medium |
| **CORS Issues** | ✅ None | ⚠️ Need config |
| **SSL Certificates** | 1 cert | 2 certs (or wildcard) |
| **Caching** | ⭐⭐⭐ Excellent | ⭐⭐ Good |
| **Scalability** | ⭐⭐ Good | ⭐⭐⭐ Excellent |
| **Code Changes** | Backend prefix | Frontend URL only |
| **Best For** | Small-Medium apps | Large/Enterprise apps |

---

## 🎯 Recommendation for Your Project

### **Use Same Domain with `/api/v1` Prefix** ✅

**Why?**
1. ✅ **Simplest setup** - One domain, one SSL cert
2. ✅ **No CORS issues** - Same origin
3. ✅ **Better SEO** - Single domain authority
4. ✅ **Easier development** - No subdomain juggling
5. ✅ **Standard practice** - Most modern apps use this pattern

**Examples using this pattern:**
- GitHub: `github.com` (frontend) + `github.com/api/v3` (API)
- Stripe: `stripe.com` (frontend) + `stripe.com/api` (API)
- Twitter: `twitter.com` (frontend) + `twitter.com/api/1.1` (API)

---

## 📝 Migration Checklist

- [ ] Update backend routers with `/api/v1` prefix
- [ ] Update frontend API client base URL
- [ ] Create production Nginx config
- [ ] Test locally with dev server
- [ ] Deploy to production server
- [ ] Update DNS if needed
- [ ] Install SSL certificate
- [ ] Test all API endpoints
- [ ] Test frontend routing
- [ ] Verify Telegram login works

---

## 🧪 Testing After Implementation

### 1. Test Frontend Routes
```bash
# Should return HTML
curl https://www.analyticbot.org/
curl https://www.analyticbot.org/auth
curl https://www.analyticbot.org/dashboard
```

### 2. Test API Routes
```bash
# Should return JSON
curl https://www.analyticbot.org/api/v1/health
curl https://www.analyticbot.org/api/v1/channels
```

### 3. Test SPA Routing
- Navigate to: `https://www.analyticbot.org/auth?mode=login`
- Refresh page (F5)
- Should see login page, NOT API JSON ✅

---

## 🆘 Troubleshooting

### Problem: Still seeing API JSON on refresh

**Check**:
1. Nginx config applied? `sudo nginx -t && sudo systemctl reload nginx`
2. Frontend built correctly? Check `/var/www/analyticbot/frontend/dist/index.html` exists
3. API prefix updated? Check `/api/v1/` in API calls

### Problem: CORS errors

**Solution**:
```python
# apps/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.analyticbot.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Problem: 404 on API routes

**Check**:
- API is running: `curl http://localhost:11400/api/v1/health`
- Nginx proxy working: `sudo tail -f /var/log/nginx/error.log`

---

## 📞 Quick Reference

```bash
# Check Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# View logs
sudo tail -f /var/log/nginx/analyticbot_access.log
sudo tail -f /var/log/nginx/analyticbot_error.log

# Test API locally
curl http://localhost:11400/api/v1/health

# Test API through Nginx
curl https://www.analyticbot.org/api/v1/health

# Test frontend
curl https://www.analyticbot.org/
```

---

**Status**: ⚠️ Implementation required
**Priority**: High (blocks production deployment)
**Estimated time**: 2-3 hours to implement and test
