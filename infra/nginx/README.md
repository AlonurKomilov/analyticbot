# Nginx Configuration Files

**Last Updated:** December 15, 2025

## Active Configuration Files

### Production Configs (per subdomain)

| Config File | Domain | Port | Purpose |
|-------------|--------|------|---------|
| `api.analyticbot.conf` | api.analyticbot.org | 11400 | API backend |
| `public.analyticbot.conf` | analyticbot.org | 11320 | Public analytics catalog |
| `app.analyticbot.conf` | app.analyticbot.org | 11300 | User dashboard |
| `moderator.analyticbot.conf` | moderator.analyticbot.org | 11330 | Moderator dashboard |
| `admin.analyticbot.conf` | admin.analyticbot.org | 11310 | Admin panel |

### Alternative/Reference Configs

| Config File | Purpose |
|-------------|---------|
| `frontend.analyticbot.conf` | Generic frontend serving (legacy) |
| `analyticbot.prod.conf` | Full-stack single domain config |
| `analyticbot.cloudflare.conf` | Combined Cloudflare config (all domains) |

---

## Quick Deploy Guide

### Deploy Individual Config

```bash
# Example: Deploy public catalog config
sudo cp public.analyticbot.conf /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/public.analyticbot.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Deploy All Configs

```bash
cd /home/abcdev/projects/analyticbot/infra/nginx

# Copy all configs
for conf in api public app moderator admin; do
    sudo cp ${conf}.analyticbot.conf /etc/nginx/sites-available/
done

# Test and reload
sudo nginx -t && sudo systemctl reload nginx
```

---

## Configuration Details

### 1. `api.analyticbot.conf` ✅ PRODUCTION
- **Domain:** api.analyticbot.org
- **Backend:** 127.0.0.1:11400
- **Features:** Rate limiting, auth endpoints, health checks

### 2. `public.analyticbot.conf` 🆕
- **Domain:** analyticbot.org, www.analyticbot.org
- **Backend:** 127.0.0.1:11320
- **Purpose:** Public analytics catalog (TGStat-like)
- **Features:** SEO-friendly, Telegram widgets allowed

### 3. `app.analyticbot.conf` 🆕
- **Domain:** app.analyticbot.org
- **Backend:** 127.0.0.1:11300
- **Purpose:** Authenticated user dashboard
- **Features:** Telegram Login support

### 4. `moderator.analyticbot.conf` 🆕
- **Domain:** moderator.analyticbot.org
- **Backend:** 127.0.0.1:11330
- **Purpose:** Channel moderation interface
- **Features:** Strict CSP, no external frames

### 5. `admin.analyticbot.conf`
- **Domain:** admin.analyticbot.org
- **Backend:** 127.0.0.1:11310
- **Purpose:** System administration
- **Features:** Strictest security headers

---

## Development vs Production

Each config has two modes:

**Development Mode** (Vite dev server):
- Uncomment the proxy section
- Comment out the static files section
- Uses WebSocket for HMR

**Production Mode** (static files):
- Comment out the proxy section
- Uncomment the static files section
- Serves from `/var/www/analyticbot/{app}`

---

## Directory Structure (Production)

```
/var/www/analyticbot/
├── public/      # Public catalog (analyticbot.org)
├── app/         # User dashboard (app.analyticbot.org)
├── moderator/   # Moderator panel (moderator.analyticbot.org)
├── admin/       # Admin panel (admin.analyticbot.org)
└── api/         # API (if static docs needed)
```

---

## Quick Commands

```bash
# Test config
sudo nginx -t

# Reload (zero downtime)
sudo systemctl reload nginx

# View logs
tail -f /var/log/nginx/public.analyticbot.org.access.log
tail -f /var/log/nginx/moderator.analyticbot.org.error.log

# Check active server blocks
sudo nginx -T | grep "server_name"
```

---

## Archived Files

**Location:** `../archive/nginx_cleanup_20251120/`

Old/deprecated configs moved to archive for reference.

---

## File Naming Convention

- `{subdomain}.analyticbot.conf` - Per-subdomain config
- `analyticbot.{type}.conf` - Combined/alternative configs
- `*.backup` - Temporary backups

---

**Maintained by:** DevOps / Infrastructure Team
**Last Audit:** December 15, 2025
