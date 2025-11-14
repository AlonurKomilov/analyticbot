# 🚀 Production Setup - analyticbot.org

## ✅ Setup Complete!

Your AnalyticBot is now live at **https://analyticbot.org**

---

## 🌐 Domain Configuration

- **Domain:** analyticbot.org
- **Created:** November 14, 2025
- **DNS Provider:** CloudFlare
- **Server IP:** 185.211.5.244 (IPv4), 2a02:c207:2282:5673::1 (IPv6)

### DNS Records (CloudFlare)
```
Type: CNAME
Name: analyticbot.org
Target: a73d4c82-39c2-4e75-b2b7-eb7cdc91a8f0.cfargotunnel.com
Proxy: ✅ Enabled

Type: CNAME
Name: www
Target: a73d4c82-39c2-4e75-b2b7-eb7cdc91a8f0.cfargotunnel.com
Proxy: ✅ Enabled
```

---

## 🔐 CloudFlare Tunnel

### Tunnel Details
- **Tunnel Name:** analyticbot-prod
- **Tunnel ID:** a73d4c82-39c2-4e75-b2b7-eb7cdc91a8f0
- **Type:** Permanent Named Tunnel
- **Status:** ✅ Running as System Service

### Tunnel Configuration
**Config File:** `/etc/cloudflared/config.yml`

```yaml
tunnel: a73d4c82-39c2-4e75-b2b7-eb7cdc91a8f0
credentials-file: /home/abcdeveloper/.cloudflared/a73d4c82-39c2-4e75-b2b7-eb7cdc91a8f0.json

ingress:
  - hostname: analyticbot.org
    service: http://localhost:11300
  - hostname: www.analyticbot.org
    service: http://localhost:11300
  - service: http_status:404
```

### Service Management

```bash
# Check tunnel status
sudo systemctl status cloudflared

# Restart tunnel
sudo systemctl restart cloudflared

# Stop tunnel
sudo systemctl stop cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f

# Tunnel info
cloudflared tunnel info analyticbot-prod
```

---

## 🏗️ Architecture

```
Internet (HTTPS)
    ↓
CloudFlare CDN (SSL/DDoS Protection)
    ↓
CloudFlare Tunnel (analyticbot-prod)
    ↓
localhost:11300 (Vite Frontend)
    ↓ (Proxy /api/* requests)
localhost:11400 (FastAPI Backend)
    ↓
PostgreSQL (localhost:10100)
Redis (localhost:10200)
```

### URL Routing
- **Frontend:** https://analyticbot.org → localhost:11300
- **API:** https://analyticbot.org/api/* → localhost:11400 (proxied through Vite)

---

## 🖥️ Server Services

### Port Configuration
- **Frontend (Vite):** 11300
- **Backend (FastAPI):** 11400
- **PostgreSQL:** 10100
- **Redis:** 10200
- **CloudFlare Metrics:** 20243

### Service Status
```bash
# Check all services
make -f Makefile.dev dev-status

# Start services
make -f Makefile.dev dev-start

# Stop services
make -f Makefile.dev dev-stop
```

---

## 🔄 Auto-Start on Boot

The CloudFlare tunnel is configured to start automatically on server reboot via systemd.

**Your application services** need to be started manually after reboot:
```bash
cd /home/abcdeveloper/projects/analyticbot
make -f Makefile.dev dev-start
```

### Optional: Auto-Start App Services

If you want the app to start on boot, create a systemd service:

```bash
sudo nano /etc/systemd/system/analyticbot.service
```

Add:
```ini
[Unit]
Description=AnalyticBot Application
After=network.target cloudflared.service postgresql.service

[Service]
Type=forking
User=abcdeveloper
WorkingDirectory=/home/abcdeveloper/projects/analyticbot
ExecStart=/usr/bin/make -f Makefile.dev dev-start
ExecStop=/usr/bin/make -f Makefile.dev dev-stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable analyticbot
sudo systemctl start analyticbot
```

---

## 🧪 Testing

### Test Domain Locally
```bash
# Test HTTPS connection
curl -I https://analyticbot.org

# Test API through domain
curl https://analyticbot.org/api/health

# Test frontend
curl -s https://analyticbot.org | grep "<title>"
```

### Test Local Services
```bash
# Frontend
curl http://localhost:11300

# Backend
curl http://localhost:11400/health

# API through proxy
curl http://localhost:11300/api/health
```

---

## 🐛 Troubleshooting

### Issue: "This site can't be reached" (DNS_PROBE_FINISHED_NXDOMAIN)

**Cause:** Browser DNS cache

**Solutions:**
1. Clear browser DNS cache:
   - Chrome: `chrome://net-internals/#dns` → "Clear host cache"
   - Firefox: Restart browser
2. Use Incognito/Private mode
3. Wait 2-5 minutes for DNS propagation
4. Flush local DNS cache (on your computer, not server)

### Issue: Tunnel Not Running

```bash
# Check tunnel service
sudo systemctl status cloudflared

# Restart tunnel
sudo systemctl restart cloudflared

# View logs
sudo journalctl -u cloudflared -f
```

### Issue: Services Not Responding

```bash
# Check if services are running
make -f Makefile.dev dev-status

# Restart services
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start

# Check logs
make -f Makefile.dev dev-logs
```

### Issue: API Requests Failing

1. Check backend is running: `curl http://localhost:11400/health`
2. Check proxy config: `cat apps/frontend/vite.config.js`
3. Check frontend env: `cat apps/frontend/.env.local`
4. Restart frontend: `make -f Makefile.dev dev-stop && make -f Makefile.dev dev-start`

---

## 📝 Environment Variables

### Frontend (.env.local)
```bash
# Use relative URLs for same-domain access
VITE_API_BASE_URL=

# Frontend runs on port 11300
VITE_PORT=11300
```

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://analyticbot:your_password@localhost:10100/analyticbot

# Redis
REDIS_URL=redis://localhost:10200

# API runs on port 11400
PORT=11400
```

---

## 🔒 Security Notes

1. **SSL/TLS:** Automatically handled by CloudFlare (HTTPS)
2. **DDoS Protection:** Provided by CloudFlare
3. **Firewall:** No ports need to be opened (tunnel handles everything)
4. **Credentials:** Stored in `/etc/cloudflared/` (root-only access)

---

## 📊 Monitoring

### Check Tunnel Health
```bash
# Tunnel info
cloudflared tunnel info analyticbot-prod

# Service status
sudo systemctl status cloudflared

# Live logs
sudo journalctl -u cloudflared -f
```

### Check Application Health
```bash
# Health endpoint
curl https://analyticbot.org/api/health

# Service status
make -f Makefile.dev dev-status
```

---

## 🎉 Success!

Your AnalyticBot is now:
- ✅ Live at https://analyticbot.org
- ✅ Secured with CloudFlare SSL
- ✅ Protected by CloudFlare DDoS protection
- ✅ Auto-starts on server reboot (tunnel)
- ✅ Using permanent named tunnel (no more DNS timeouts)

**Access your app:** https://analyticbot.org

---

## 📞 Quick Commands Reference

```bash
# Tunnel
sudo systemctl status cloudflared
sudo systemctl restart cloudflared
cloudflared tunnel info analyticbot-prod

# Application
make -f Makefile.dev dev-start
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-status

# Testing
curl -I https://analyticbot.org
curl https://analyticbot.org/api/health
```

---

**Setup Date:** November 14, 2025  
**Tunnel Type:** CloudFlare Permanent Named Tunnel  
**Domain Status:** Active  
**SSL:** Enabled via CloudFlare
