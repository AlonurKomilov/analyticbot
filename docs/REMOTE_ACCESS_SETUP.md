# Remote Access Setup Guide

## Current Issue
You're accessing the frontend via HTTPS devtunnel, but the API is HTTP. Browsers block mixed content (HTTP requests from HTTPS pages).

## ✅ Solution 1: Use HTTP for Both (RECOMMENDED FOR NOW)

**Access your application at:**
```
Frontend: http://185.211.5.244:11300
API:      http://185.211.5.244:11400
```

**Advantages:**
- ✅ Works immediately
- ✅ No additional setup needed
- ✅ Ports are already open
- ✅ CORS already configured

---

## 🔧 Solution 2: Set Up DevTunnels with HTTPS (For Persistent Remote Access)

If you need secure HTTPS access (e.g., for Telegram Web App or external demos):

### A. Using VS Code Port Forwarding (Easiest)

1. **Open VS Code Ports Panel:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type: "Ports: Focus on Ports View"
   - Or: View → Ports (bottom panel)

2. **Forward Ports:**
   - Click "+ Forward a Port"
   - Add port `11300` (Frontend)
     - Right-click → Port Visibility → **Public**
   - Add port `11400` (API)
     - Right-click → Port Visibility → **Public**

3. **Copy URLs:**
   VS Code will show URLs like:
   ```
   https://xxx-11300.app.github.dev  (Frontend)
   https://xxx-11400.app.github.dev  (API)
   ```

4. **Update Configuration:**
   ```bash
   # Update apps/frontend/.env.local
   VITE_API_URL=https://xxx-11400.app.github.dev
   VITE_API_BASE_URL=https://xxx-11400.app.github.dev

   # Update .env.development CORS_ORIGINS to include:
   # "https://xxx-11300.app.github.dev"
   # "https://xxx-11400.app.github.dev"
   ```

5. **Restart Services:**
   ```bash
   make dev-stop
   make dev-start
   ```

### B. Using Microsoft DevTunnel CLI

1. **Install DevTunnel:**
   ```bash
   curl -sL https://aka.ms/DevTunnelCliInstall | bash
   ```

2. **Login:**
   ```bash
   devtunnel user login
   ```

3. **Create Tunnels:**
   ```bash
   # Create frontend tunnel
   devtunnel create analyticbot-frontend -p 11300 --allow-anonymous

   # Create API tunnel
   devtunnel create analyticbot-api -p 11400 --allow-anonymous
   ```

4. **Start Tunnels:**
   ```bash
   # Terminal 1
   devtunnel host analyticbot-frontend

   # Terminal 2
   devtunnel host analyticbot-api
   ```

5. **Get URLs and update config as above**

### C. Using Ngrok (Alternative)

1. **Install Ngrok:**
   ```bash
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
   tar xvzf ngrok-v3-stable-linux-amd64.tgz
   sudo mv ngrok /usr/local/bin/
   ```

2. **Sign up and get auth token:** https://dashboard.ngrok.com/signup

3. **Configure auth:**
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

4. **Start Tunnels:**
   ```bash
   # Terminal 1 - Frontend
   ngrok http 11300

   # Terminal 2 - API
   ngrok http 11400
   ```

5. **Copy URLs and update config**

---

## 🔐 Solution 3: Set Up Nginx Reverse Proxy with SSL (Production-Ready)

For a proper production setup:

```bash
# Install certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Set up domain (example: api.yourdomain.com)
sudo certbot --nginx -d api.yourdomain.com -d frontend.yourdomain.com

# Nginx will handle SSL, proxy to your HTTP services
```

---

## 📝 Current Configuration

**File: `apps/frontend/.env.local`**
```bash
VITE_API_URL=http://185.211.5.244:11400
VITE_API_BASE_URL=http://185.211.5.244:11400
```

**File: `.env.development` (CORS_ORIGINS)**
```json
["http://localhost:11300","http://localhost:11400","http://185.211.5.244:11300","http://185.211.5.244:11400","https://b2qz1m0n-11300.euw.devtunnels.ms","https://b2qz1m0n-11400.euw.devtunnels.ms","https://*.devtunnels.ms"]
```

---

## 🚀 Quick Start (HTTP)

Just open your browser and go to:
```
http://185.211.5.244:11300
```

That's it! Everything should work. 🎉
