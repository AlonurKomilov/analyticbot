# 🚀 API Subdomain Deployment Guide
## api.analyticbot.org Configuration

## ✅ Completed Steps

1. **DNS Configuration** ✅
   - Added `api` A record in Cloudflare
   - Proxy enabled (Orange cloud)
   - Points to: 185.211.5.244

2. **Backend Configuration** ✅
   - Updated `.env` CORS_ORIGINS to include `https://api.analyticbot.org`
   - FastAPI will accept requests from the frontend

3. **Frontend Configuration** ✅
   - Updated `.env.production` to use `https://api.analyticbot.org`
   - Frontend will send API requests to subdomain

4. **Nginx Configurations Created** ✅
   - `infra/nginx/api.analyticbot.conf` - API subdomain config
   - `infra/nginx/frontend.analyticbot.conf` - Frontend config

---

## 📋 Deployment Steps (30 minutes)

### Step 1: Get SSL Certificate (10 minutes)

**Option A: Let's Encrypt Wildcard Certificate** ⭐ RECOMMENDED

```bash
# Install certbot with Cloudflare plugin
sudo apt-get update
sudo apt-get install certbot python3-certbot-dns-cloudflare

# Create Cloudflare credentials file
sudo mkdir -p /root/.secrets
sudo nano /root/.secrets/cloudflare.ini
```

Add to file:
```ini
# Cloudflare API token
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN
```

Get your API token from: https://dash.cloudflare.com/profile/api-tokens
- Click "Create Token"
- Use "Edit zone DNS" template
- Include: analyticbot.org zone
- Copy the token

```bash
# Secure the file
sudo chmod 600 /root/.secrets/cloudflare.ini

# Get wildcard certificate (covers *.analyticbot.org + analyticbot.org)
sudo certbot certonly \
  --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  -d analyticbot.org \
  -d '*.analyticbot.org' \
  --preferred-challenges dns-01

# Certificates will be saved to:
# /etc/letsencrypt/live/analyticbot.org/fullchain.pem
# /etc/letsencrypt/live/analyticbot.org/privkey.pem
```

**Option B: Cloudflare Origin Certificate** (If preferred)

1. Go to Cloudflare Dashboard → SSL/TLS → Origin Server
2. Click "Create Certificate"
3. Select: `*.analyticbot.org, analyticbot.org`
4. Validity: 15 years
5. Save certificate and key:

```bash
sudo mkdir -p /etc/ssl/cloudflare
sudo nano /etc/ssl/cloudflare/analyticbot_origin_cert.pem
# Paste certificate

sudo nano /etc/ssl/cloudflare/analyticbot_origin_key.pem
# Paste private key

sudo chmod 600 /etc/ssl/cloudflare/*
```

Update nginx configs to use these paths (uncomment the Cloudflare Origin lines).

---

### Step 2: Deploy Nginx Configurations (5 minutes)

```bash
# Copy configurations to nginx
sudo cp /home/abcdeveloper/projects/analyticbot/infra/nginx/api.analyticbot.conf /etc/nginx/sites-available/
sudo cp /home/abcdeveloper/projects/analyticbot/infra/nginx/frontend.analyticbot.conf /etc/nginx/sites-available/

# Enable sites
sudo ln -sf /etc/nginx/sites-available/api.analyticbot.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/frontend.analyticbot.conf /etc/nginx/sites-enabled/

# Remove default site if exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

---

### Step 3: Deploy Backend API (5 minutes)

```bash
# Navigate to project
cd /home/abcdeveloper/projects/analyticbot

# Activate virtual environment
source venv/bin/activate

# Create systemd service for API
sudo nano /etc/systemd/system/analyticbot-api.service
```

Add this content:
```ini
[Unit]
Description=AnalyticBot FastAPI Application
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=abcdeveloper
Group=abcdeveloper
WorkingDirectory=/home/abcdeveloper/projects/analyticbot
Environment="PATH=/home/abcdeveloper/projects/analyticbot/venv/bin"
Environment="PYTHONPATH=/home/abcdeveloper/projects/analyticbot"

# Load environment variables
EnvironmentFile=/home/abcdeveloper/projects/analyticbot/.env

# Start FastAPI with uvicorn
ExecStart=/home/abcdeveloper/projects/analyticbot/venv/bin/uvicorn \
    apps.api.main:app \
    --host 0.0.0.0 \
    --port 11400 \
    --workers 4 \
    --log-level info

# Restart on failure
Restart=always
RestartSec=5

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable analyticbot-api
sudo systemctl start analyticbot-api

# Check status
sudo systemctl status analyticbot-api

# View logs
sudo journalctl -u analyticbot-api -f
```

---

### Step 4: Build and Deploy Frontend (10 minutes)

```bash
cd /home/abcdeveloper/projects/analyticbot/apps/frontend

# Install dependencies (if not already done)
npm install

# Build for production (uses .env.production)
npm run build

# Create web directory
sudo mkdir -p /var/www/analyticbot/frontend

# Copy built files
sudo cp -r dist/* /var/www/analyticbot/frontend/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/analyticbot
sudo chmod -R 755 /var/www/analyticbot
```

---

### Step 5: Configure Cloudflare SSL Settings (2 minutes)

Go to Cloudflare Dashboard → SSL/TLS:

1. **Encryption mode**: Set to **"Full (strict)"**
   - Ensures end-to-end encryption
   - Validates your server certificate

2. **Always Use HTTPS**: Turn **ON**
   - Automatically redirects HTTP to HTTPS

3. **Minimum TLS Version**: Set to **TLS 1.2**
   - Modern security standards

4. **Automatic HTTPS Rewrites**: Turn **ON**
   - Fixes mixed content issues

---

## 🧪 Testing (5 minutes)

### Test 1: DNS Resolution
```bash
# Check DNS propagation
dig api.analyticbot.org +short
# Should return: Cloudflare IP addresses

dig www.analyticbot.org +short
# Should return: Cloudflare IP addresses

# Or use online tool:
# https://dnschecker.org
```

### Test 2: API Health Check
```bash
# Test API is responding
curl https://api.analyticbot.org/health

# Expected output:
# {"status":"healthy","timestamp":"...","service":"analyticbot","version":"7.5.0"}
```

### Test 3: Frontend Access
```bash
# Test frontend is serving
curl https://www.analyticbot.org/ | head -20

# Should return HTML starting with:
# <!DOCTYPE html>
```

### Test 4: CORS Configuration
Open browser console (F12) and visit https://www.analyticbot.org

```javascript
// Test API request
fetch('https://api.analyticbot.org/health')
  .then(r => r.json())
  .then(data => console.log('API Response:', data))
  .catch(err => console.error('CORS Error:', err));
```

Should show: `API Response: {status: "healthy", ...}` ✅
No CORS errors in console ✅

### Test 5: Full Login Flow
1. Visit: `https://www.analyticbot.org/auth?mode=login`
2. Should see login page (not JSON)
3. Refresh page (F5) - Should still see login page ✅
4. Check Network tab - API calls go to `https://api.analyticbot.org` ✅
5. No CORS errors ✅

### Test 6: Telegram Login
1. Go to login page
2. Telegram login button should appear (not "Bot domain invalid")
3. Click button → Authenticate → Redirects back ✅

---

## 🆘 Troubleshooting

### Issue: "502 Bad Gateway"

**Cause**: Backend not running

**Fix**:
```bash
# Check if API is running
sudo systemctl status analyticbot-api

# If not, start it
sudo systemctl start analyticbot-api

# Check logs
sudo journalctl -u analyticbot-api -n 100
```

### Issue: "Connection refused"

**Cause**: Backend not listening on 11400

**Fix**:
```bash
# Check if port is open
sudo netstat -tlnp | grep 11400

# Or use ss
sudo ss -tlnp | grep 11400

# Manually start for testing
cd /home/abcdeveloper/projects/analyticbot
source venv/bin/activate
uvicorn apps.api.main:app --host 0.0.0.0 --port 11400
```

### Issue: CORS Errors in Browser

**Check 1**: Verify backend CORS settings
```bash
grep CORS_ORIGINS /home/abcdeveloper/projects/analyticbot/.env
# Should include: https://www.analyticbot.org
```

**Check 2**: Verify Nginx CORS headers
```bash
sudo nginx -T | grep -A 5 "Access-Control-Allow-Origin"
```

**Check 3**: Restart services
```bash
sudo systemctl restart analyticbot-api
sudo systemctl reload nginx
```

### Issue: SSL Certificate Error

**Check certificate**:
```bash
# Test SSL
curl -vI https://api.analyticbot.org 2>&1 | grep -i 'ssl\|certificate'

# Check certificate files
sudo ls -l /etc/letsencrypt/live/analyticbot.org/
```

**Renew certificate**:
```bash
sudo certbot renew
sudo systemctl reload nginx
```

### Issue: Frontend Shows 404

**Check files**:
```bash
# Verify frontend files exist
ls -la /var/www/analyticbot/frontend/
# Should show: index.html, assets/, etc.

# Check nginx error log
sudo tail -f /var/log/nginx/frontend_analyticbot_error.log
```

**Rebuild frontend**:
```bash
cd /home/abcdeveloper/projects/analyticbot/apps/frontend
npm run build
sudo cp -r dist/* /var/www/analyticbot/frontend/
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                       │
│                                                         │
│  https://www.analyticbot.org      (Frontend)           │
│  https://api.analyticbot.org      (API calls)          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Cloudflare CDN                         │
│  • DDoS Protection                                      │
│  • SSL/TLS Termination                                  │
│  • Caching                                              │
│  • WAF (Web Application Firewall)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Your Server (185.211.5.244)                │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │              Nginx (Port 443)                    │  │
│  │                                                  │  │
│  │  www.analyticbot.org  →  /var/www/.../dist/    │  │
│  │  api.analyticbot.org  →  localhost:11400        │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                     │
│                   ▼                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │     FastAPI Backend (Port 11400)                 │  │
│  │     • JWT Authentication                         │  │
│  │     • Business Logic                             │  │
│  │     • Database Access                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │     PostgreSQL Database (Port 10100)             │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │     Redis Cache (Port 10200)                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Final Checklist

### Pre-Deployment
- [x] DNS record added in Cloudflare
- [x] Backend `.env` updated with CORS
- [x] Frontend `.env.production` updated with API URL
- [x] Nginx configs created

### Deployment
- [ ] SSL certificate obtained
- [ ] Nginx configs deployed and tested
- [ ] Backend systemd service created and running
- [ ] Frontend built and deployed
- [ ] Cloudflare SSL settings configured

### Testing
- [ ] DNS resolves correctly
- [ ] API health endpoint returns 200
- [ ] Frontend loads at www.analyticbot.org
- [ ] No CORS errors in browser console
- [ ] Login page works (shows form, not JSON)
- [ ] Telegram login button appears
- [ ] Can authenticate and access dashboard

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Set up SSL auto-renewal
- [ ] Configure backup system
- [ ] Set up monitoring alerts

---

## 📞 Quick Commands Reference

```bash
# Check services
sudo systemctl status analyticbot-api
sudo systemctl status nginx

# View logs
sudo journalctl -u analyticbot-api -f
sudo tail -f /var/log/nginx/api_analyticbot_access.log
sudo tail -f /var/log/nginx/api_analyticbot_error.log

# Restart services
sudo systemctl restart analyticbot-api
sudo systemctl reload nginx

# Test API locally
curl http://localhost:11400/health

# Test API through nginx
curl https://api.analyticbot.org/health

# Test frontend
curl https://www.analyticbot.org/

# Check SSL certificate
sudo certbot certificates

# Renew SSL
sudo certbot renew --dry-run
sudo certbot renew
```

---

## 🎉 Success Criteria

Your deployment is successful when:
1. ✅ `https://api.analyticbot.org/health` returns JSON
2. ✅ `https://www.analyticbot.org` shows login page
3. ✅ No CORS errors in browser console
4. ✅ Can login and see dashboard
5. ✅ Telegram login works
6. ✅ All green padlocks (valid SSL)

---

**Total Time**: ~30-45 minutes
**Next**: Follow steps 1-5 above to complete deployment
