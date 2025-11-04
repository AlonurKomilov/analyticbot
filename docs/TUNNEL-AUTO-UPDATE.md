# Cloudflare Tunnel Auto-Update System

## Problem Solved
Cloudflare free tunnels get a **new random URL every restart**, which would break your frontend if `.env.local` has the old URL.

## Solution
Automatic tunnel URL synchronization between backend and frontend.

## How It Works

### 1. Start Development Environment
```bash
make -f Makefile.dev dev-start
```

This will:
1. Start PostgreSQL & Redis
2. Start API server on port 11400
3. Start Telegram bot
4. Start frontend on port 11300
5. Start Cloudflare tunnel
6. **AUTOMATICALLY** update `apps/frontend/.env.local` with the new tunnel URL

### 2. The Auto-Update Script
Location: `scripts/update-tunnel-url.sh`

This script:
- Waits for the tunnel to start
- Extracts the new Cloudflare URL from logs
- Updates `.env.local` with the new URL
- Creates a backup (`.env.local.backup`)
- Records the URL in `.tunnel-current` for reference

### 3. Manual Update (if needed)
If you need to manually update the tunnel URL:

```bash
./scripts/update-tunnel-url.sh
```

Then restart the frontend or hard-refresh your browser (Ctrl+Shift+R).

## Usage Scenarios

### Scenario 1: Normal Development (Alone)
**Best Option: Use localhost (fastest)**

```bash
# Edit apps/frontend/.env.local:
VITE_API_BASE_URL=http://localhost:11400
VITE_API_URL=http://localhost:11400
VITE_API_TIMEOUT=30000
```

- ✅ **Fast**: 0.15 seconds
- ✅ **Reliable**: No network issues
- ❌ **Local only**: Can't share with others

### Scenario 2: Testing with Others
**Use Cloudflare tunnel (automatic URL update)**

```bash
make -f Makefile.dev dev-start
# URL automatically updates in .env.local
# Share the URL shown in the console
```

- ✅ **Public**: Anyone can access
- ✅ **Auto-updates**: No manual config needed
- ⚠️ **Changes**: New URL on every restart (~500ms response time)

### Scenario 3: Production-like Testing
**Setup permanent Cloudflare tunnel (recommended for teams)**

```bash
./scripts/setup-cloudflare-tunnel.sh
```

- ✅ **Permanent URL**: Never changes
- ✅ **Free**: Cloudflare Tunnel is free forever
- ✅ **Fast**: ~500ms response time
- ✅ **Professional**: Use custom domain

## Current Tunnel URL

Check the current tunnel URL:
```bash
cat .tunnel-current
```

Or check logs:
```bash
grep "trycloudflare.com" logs/dev_tunnel.log | tail -1
```

## Troubleshooting

### Problem: Frontend still uses old URL
**Solution:**
```bash
# Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
# Or restart frontend:
pkill -f "vite.*11300"
cd apps/frontend && npm run dev -- --port 11300 --host 0.0.0.0
```

### Problem: Tunnel URL not updating automatically
**Solution:**
```bash
# Manually run the update script:
./scripts/update-tunnel-url.sh

# Check if tunnel is running:
ps aux | grep cloudflared
```

### Problem: 504 Gateway Timeout
**Likely cause:** Microsoft Dev Tunnel is configured instead of Cloudflare

**Solution:**
```bash
# Check which tunnel is configured:
grep "VITE_API_BASE_URL" apps/frontend/.env.local

# If you see b2qz1m0n-11400.euw.devtunnels.ms (Microsoft):
# Run the update script to switch to Cloudflare:
./scripts/update-tunnel-url.sh
```

## Performance Comparison

| Method | Response Time | Stability | Public Access |
|--------|--------------|-----------|---------------|
| **Localhost** | 0.15s | ✅ Excellent | ❌ No |
| **Cloudflare (free)** | 0.43s | ✅ Good | ✅ Yes (URL changes) |
| **Cloudflare (permanent)** | 0.43s | ✅ Excellent | ✅ Yes (fixed URL) |
| **Microsoft Dev Tunnel** | 100s+ ❌ | ❌ Broken | ⚠️ If working |

## Next Steps

### For Solo Development
Keep using localhost - it's the fastest!

### For Team Development
Setup permanent Cloudflare tunnel:
```bash
./scripts/setup-cloudflare-tunnel.sh
```

This gives you a permanent URL that never changes!
