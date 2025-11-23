# Nginx Configuration Files

**Last Cleaned:** November 20, 2025

## Active Configuration Files

### 1. `api.analyticbot.conf` (191 lines) ✅ PRODUCTION
**Domain:** api.analyticbot.org
**Purpose:** API subdomain with Cloudflare proxy
**Status:** Currently deployed to `/etc/nginx/sites-available/`
**Features:**
- Enterprise security headers
- SSL session caching
- Gzip compression
- Rate limiting ready (zones need nginx.conf)
- Health check optimization
- Separate auth/api routing

**Deploy:**
```bash
sudo cp api.analyticbot.conf /etc/nginx/sites-available/
sudo nginx -t && sudo systemctl reload nginx
```

---

### 2. `frontend.analyticbot.conf` (176 lines)
**Domain:** www.analyticbot.org
**Purpose:** React SPA serving with proper routing
**Status:** Alternative frontend config
**Use Case:** When frontend is on separate subdomain

---

### 3. `analyticbot.prod.conf` (290 lines)
**Domain:** www.analyticbot.org
**Purpose:** Full production config (frontend + API on same domain)
**Status:** Alternative architecture reference
**Use Case:** When frontend and API share the same domain with path routing

---

## Archived Files

**Location:** `../archive/nginx_cleanup_20251120/`

Files moved to archive (no longer needed):
- ❌ `api.analyticbot.conf.broken` - Had undefined rate limiting zones
- ❌ `api.analyticbot.simple.conf` - Too minimal, missing security
- ❌ `nginx.prod.conf` - Old generic config

---

## Quick Commands

**Test current config:**
```bash
sudo nginx -t
```

**Reload nginx (zero downtime):**
```bash
sudo systemctl reload nginx
```

**Check active config:**
```bash
sudo nginx -T | grep -A5 "server_name api.analyticbot.org"
```

**View logs:**
```bash
tail -f /var/log/nginx/api.analyticbot.org.access.log
tail -f /var/log/nginx/api.analyticbot.org.error.log
```

---

## Configuration Philosophy

**Clean & Organized:**
- One primary config per purpose
- Clear naming: `{domain}.conf`
- Archive old/broken files (don't delete - keep history)
- Production configs have full documentation

**Security First:**
- All configs include security headers
- Modern TLS only (1.2, 1.3)
- File blocking (.env, .git, etc.)
- Rate limiting support

**Performance Optimized:**
- SSL session caching
- Gzip compression
- Endpoint-specific timeouts
- Health check optimization

---

## File Naming Convention

- `api.analyticbot.conf` - Main API config (production)
- `frontend.analyticbot.conf` - Frontend serving config
- `analyticbot.prod.conf` - Alternative full-stack config
- `*.backup` - Temporary backups (auto-generated)
- Archive old files - don't accumulate in main folder

---

**Maintained by:** DevOps / Infrastructure Team
**Last Audit:** November 20, 2025
