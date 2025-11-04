# Tunnel Auto-Update Verification Guide

## What Happens When You Run `make -f Makefile.dev dev-start`

### 1. **Cloudflare Tunnel Starts**
The script starts a Cloudflare tunnel and writes the URL to `logs/dev_tunnel.log`.

### 2. **Auto-Update Script Runs**
`scripts/update-tunnel-url.sh` automatically:
- Waits for tunnel URL to appear in logs (up to 30 seconds)
- Extracts the new URL
- Updates `apps/frontend/.env.local` with the new URL
- Creates backup as `.env.local.backup`
- Writes tracking info to `.tunnel-current`
- Logs the update to `logs/tunnel-update.log`
- **Prints a big visible banner:**

```
==========================================
✅ TUNNEL URL AUTO-UPDATE COMPLETE
==========================================
📡 New URL: https://xxxxx.trycloudflare.com
📝 Updated: apps/frontend/.env.local
⏰ Time: Thu Oct 31 10:32:29 CET 2025
==========================================
```

## Quick Verification Commands

### Check Current Tunnel URL
```bash
# See the active tunnel URL:
cat .tunnel-current

# Or from frontend config:
grep "^VITE_API_BASE_URL=" apps/frontend/.env.local

# Or from tunnel logs:
grep -o "https://[a-z0-9-]*\.trycloudflare\.com" logs/dev_tunnel.log | tail -1
```

### Check Update History
```bash
# See recent tunnel updates:
cat logs/tunnel-update.log

# Or just the last one:
tail -1 logs/tunnel-update.log
```

### Check Tunnel Status (One Command)
```bash
# This shows everything:
make -f Makefile.dev dev-tunnel-status
```

Output:
```
🌐 CloudFlare Tunnel Status
===========================
TUNNEL_URL=https://fairy-touring-checking-strings.trycloudflare.com
UPDATED_AT=2025-10-31T10:32:29+01:00

Frontend .env.local:
VITE_API_BASE_URL=https://fairy-touring-checking-strings.trycloudflare.com

Recent tunnel updates:
[2025-10-31T10:32:29+01:00] ✅ FRONTEND ENV UPDATED: https://...

Tunnel process:
cloudflared tunnel --url http://localhost:11400
```

## What Gets Updated Automatically

When tunnel restarts:
1. ✅ `apps/frontend/.env.local` - Updated with new URL
2. ✅ `.env.local.backup` - Previous version backed up
3. ✅ `.tunnel-current` - Current URL + timestamp recorded
4. ✅ `logs/tunnel-update.log` - Update history logged

## After Tunnel Update

**You must:**
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R), OR
- Restart frontend dev server: `pkill -f "vite.*11300" && cd apps/frontend && npm run dev`

**The script will remind you:**
```
💡 Restart frontend or hard-refresh browser to apply changes
```

## Troubleshooting

### Problem: No tunnel URL found
```bash
# Check if tunnel is running:
ps aux | grep cloudflared

# Check tunnel logs:
tail -50 logs/dev_tunnel.log

# Manually run update script:
./scripts/update-tunnel-url.sh
```

### Problem: Frontend still uses old URL
```bash
# 1. Verify the update happened:
cat .tunnel-current
grep "VITE_API_BASE_URL" apps/frontend/.env.local

# 2. Hard refresh browser or restart frontend:
# Ctrl+Shift+R in browser
```

### Problem: Update script timeout
The script waits 30 seconds for tunnel to start. If timeout:
- Check tunnel is running: `ps aux | grep cloudflared`
- Check tunnel log has URL: `grep trycloudflare logs/dev_tunnel.log`
- Restart tunnel: `make -f Makefile.dev dev-tunnel`

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/update-tunnel-url.sh` | Auto-update script |
| `.tunnel-current` | Current tunnel URL + timestamp |
| `logs/tunnel-update.log` | Update history |
| `logs/dev_tunnel.log` | Cloudflare tunnel output |
| `apps/frontend/.env.local` | Frontend config (auto-updated) |
| `apps/frontend/.env.local.backup` | Previous config backup |

## Next Steps

### For Solo Development (Fastest)
Edit `.env.local` to use localhost:
```bash
VITE_API_BASE_URL=http://localhost:11400
```

### For Team/Public Access
Keep the auto-update system (current setup) or setup permanent tunnel:
```bash
./scripts/setup-cloudflare-tunnel.sh  # One-time setup for permanent URL
```
