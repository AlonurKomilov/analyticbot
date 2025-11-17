# 🚀 Production Deployment Checklist - www.analyticbot.org

## ✅ Configuration Updated

Your project has been configured for production deployment at **www.analyticbot.org**.

---

## 📋 Step-by-Step Deployment Guide

### **Step 1: Configure Telegram Bot Domain** ⚡ CRITICAL

1. Open Telegram → [@BotFather](https://t.me/BotFather)
2. Send: `/setdomain`
3. Select: `@abccontrol_bot`
4. Enter: `analyticbot.org` (no www, no https)
5. Wait for confirmation: "Success! Domain analyticbot.org has been set"

**Note**: This fixes the "Bot domain invalid" error. The domain works for both:
- ✅ `https://www.analyticbot.org`
- ✅ `https://analyticbot.org`

---

### **Step 2: Backend Configuration** ✅ COMPLETED

Your `.env` file has been updated with:

```bash
# Production URLs
FRONTEND_URL=https://www.analyticbot.org

# CORS - allows both www and non-www
CORS_ORIGINS=http://localhost:11300,http://localhost:11400,https://www.analyticbot.org,https://analyticbot.org,https://*.trycloudflare.com

# Telegram Bot (already configured)
TELEGRAM_BOT_USERNAME=abccontrol_bot
```

**Action Required**: When deploying to production server:
1. Copy `.env` to production server
2. Update sensitive values (database passwords, JWT secrets, etc.)
3. Ensure `FRONTEND_URL=https://www.analyticbot.org`

---

### **Step 3: Frontend Build** 📦

Build your frontend for production:

```bash
cd apps/frontend

# Install dependencies (if not already done)
npm install

# Build for production
npm run build

# Output will be in: apps/frontend/dist/
```

The `.env.production` file (created) will be used automatically during build.

**Production environment variables**:
- ✅ `VITE_API_BASE_URL=https://www.analyticbot.org`
- ✅ `VITE_TELEGRAM_BOT_USERNAME=abccontrol_bot`
- ✅ Health checks enabled

---

### **Step 4: Web Server Configuration** 🌐

Your web server (Nginx/Apache) needs to:

#### **A. Serve Frontend Files**
```nginx
# Nginx example
server {
    listen 443 ssl http2;
    server_name www.analyticbot.org analyticbot.org;

    # SSL certificates
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Frontend - serve built files
    location / {
        root /path/to/analyticbot/apps/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API proxy - forward to backend
    location /api/ {
        proxy_pass http://localhost:11400/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health endpoint
    location /health {
        proxy_pass http://localhost:11400/health;
    }
}
```

#### **B. Redirect non-www to www** (Optional)
```nginx
server {
    listen 443 ssl http2;
    server_name analyticbot.org;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    return 301 https://www.analyticbot.org$request_uri;
}
```

---

### **Step 5: SSL Certificate** 🔒

Ensure SSL/TLS certificate is installed:

**Option 1: Let's Encrypt (Free)**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d www.analyticbot.org -d analyticbot.org

# Auto-renewal is configured automatically
```

**Option 2: Commercial SSL**
- Purchase from CA (Comodo, DigiCert, etc.)
- Install certificate files
- Configure in web server

---

### **Step 6: Database Setup** 💾

On production server:

```bash
# 1. Create production database
createdb analyticbot_production

# 2. Run migrations
cd /path/to/analyticbot
source venv/bin/activate
alembic upgrade head

# 3. Verify
psql analyticbot_production -c "\dt"
```

---

### **Step 7: Backend Deployment** 🖥️

**Option 1: Systemd Service** (Recommended)

Create `/etc/systemd/system/analyticbot-api.service`:
```ini
[Unit]
Description=AnalyticBot API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/analyticbot
Environment="PATH=/path/to/analyticbot/venv/bin"
ExecStart=/path/to/analyticbot/venv/bin/uvicorn apps.api.main:app --host 0.0.0.0 --port 11400 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable analyticbot-api
sudo systemctl start analyticbot-api
sudo systemctl status analyticbot-api
```

**Option 2: Docker** (Alternative)
```bash
cd /path/to/analyticbot
docker-compose -f docker-compose.prod.yml up -d
```

---

### **Step 8: Bot Deployment** 🤖

Create `/etc/systemd/system/analyticbot-bot.service`:
```ini
[Unit]
Description=AnalyticBot Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/analyticbot
Environment="PATH=/path/to/analyticbot/venv/bin"
ExecStart=/path/to/analyticbot/venv/bin/python -m apps.bot.run_bot
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable analyticbot-bot
sudo systemctl start analyticbot-bot
sudo systemctl status analyticbot-bot
```

---

### **Step 9: DNS Configuration** 🌍

Verify DNS records point to your server:

```bash
# Check DNS
nslookup www.analyticbot.org
nslookup analyticbot.org

# Should point to your server IP
```

**Required DNS Records**:
```
A     analyticbot.org         → YOUR_SERVER_IP
A     www.analyticbot.org     → YOUR_SERVER_IP
```

---

### **Step 10: Testing** 🧪

1. **Health Check**:
   ```bash
   curl https://www.analyticbot.org/health
   ```
   Should return: `{"status": "healthy"}`

2. **Frontend**:
   - Open: https://www.analyticbot.org
   - Should see login page

3. **Telegram Login**:
   - Click on Telegram login section
   - Should see blue Telegram button (NOT "Bot domain invalid")
   - Click button → authenticate → should redirect to dashboard

4. **API**:
   ```bash
   curl https://www.analyticbot.org/api/v1/health
   ```

---

## 🔍 Troubleshooting

### "Bot domain invalid" still appears

**Cause**: Domain not set in BotFather
**Fix**:
1. Go to @BotFather
2. `/setdomain` → `analyticbot.org`
3. Wait 2 minutes
4. Clear browser cache (Ctrl+F5)

### CORS errors in browser console

**Cause**: Backend CORS not configured
**Fix**: Verify `.env`:
```bash
CORS_ORIGINS=http://localhost:11300,http://localhost:11400,https://www.analyticbot.org,https://analyticbot.org,https://*.trycloudflare.com
```

### API returns 502 Bad Gateway

**Cause**: Backend not running
**Fix**:
```bash
sudo systemctl status analyticbot-api
sudo systemctl restart analyticbot-api
sudo journalctl -u analyticbot-api -f
```

### SSL certificate errors

**Cause**: Certificate expired or not installed
**Fix**:
```bash
# Check certificate
sudo certbot certificates

# Renew if needed
sudo certbot renew
```

---

## 📊 Post-Deployment Verification

### Critical Checks ✅

- [ ] DNS resolves to server IP
- [ ] SSL certificate valid (https works)
- [ ] `/health` endpoint returns 200 OK
- [ ] Frontend loads at www.analyticbot.org
- [ ] Login page displays correctly
- [ ] Telegram button appears (no "Bot domain invalid")
- [ ] Can authenticate via Telegram
- [ ] Can login with email/password
- [ ] Dashboard loads after login
- [ ] API requests work (check Network tab)
- [ ] Bot responds to commands in Telegram

### Performance Checks ⚡

- [ ] Page load < 3 seconds
- [ ] API response < 200ms
- [ ] No console errors
- [ ] Images load correctly
- [ ] Fonts load correctly

### Security Checks 🔒

- [ ] HTTPS only (no HTTP)
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] No sensitive data in frontend
- [ ] JWT tokens secure
- [ ] Database credentials secure

---

## 🎯 Quick Commands Reference

```bash
# Check backend logs
sudo journalctl -u analyticbot-api -f

# Check bot logs
sudo journalctl -u analyticbot-bot -f

# Restart services
sudo systemctl restart analyticbot-api
sudo systemctl restart analyticbot-bot

# Check DNS
nslookup www.analyticbot.org

# Test API
curl https://www.analyticbot.org/health

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 Support

If you encounter issues:

1. Check logs: `sudo journalctl -u analyticbot-api -n 100`
2. Verify configuration: `cat /path/to/analyticbot/.env`
3. Test locally first: `make -f Makefile.dev dev-start`

---

## ✅ Status

- [x] Backend configuration updated
- [x] Frontend production build configured
- [x] CORS origins include production domain
- [ ] **PENDING**: Set domain in BotFather (`analyticbot.org`)
- [ ] **PENDING**: Deploy to production server
- [ ] **PENDING**: Configure web server (Nginx/Apache)
- [ ] **PENDING**: Install SSL certificate
- [ ] **PENDING**: Start services
- [ ] **PENDING**: Test deployment

**Next Action**: Set domain in BotFather (5 minutes) → Deploy to server
