# Admin Rate Limits Management Guide

**Quick Reference Guide for Managing Rate Limits via Admin Dashboard**

---

## Quick Start

### View Current Rate Limits

1. Navigate to **Admin Panel** → **Rate Limits**
2. See all 13 services with their current limits and usage

### Update a Rate Limit

1. Click **Edit** button on any service
2. Change **Limit** (number of requests)
3. Change **Period** (minute/hour/day)
4. Click **Save**
5. **Restart API** for changes to take effect

---

## How It Works

### Rate Limiting System

- **Per-IP Limits**: Each IP address gets its own quota
- **Real-time Monitoring**: Usage tracked in Redis
- **Redis Storage**: Configurations stored for persistence
- **Startup Loading**: API loads configs from Redis on startup

### When Changes Apply

⚠️ **Important**: Rate limit changes require API restart to take full effect.

**Why?** Rate limit decorators are evaluated at application startup:
```python
@limiter.limit(RateLimitConfig.BOT_OPERATIONS)  # Evaluated once at startup
async def create_bot():
    ...
```

---

## Step-by-Step: Update Rate Limits

### Method 1: Via Admin Dashboard UI

**Step 1: Login as Admin**
```
https://admin.analyticbot.org/login
Email: admin@analyticbot.org
Password: [your admin password]
```

**Step 2: Navigate to Rate Limits**
- Click **Rate Limits** in sidebar
- View dashboard with all services

**Step 3: Edit a Service**
- Click **Edit** (✏️) button on service row
- Modal opens with current configuration

**Step 4: Update Configuration**
```
Service: Bot Operations
Limit: 500              ← Change this
Period: minute          ← Or this
Enabled: ✓ Yes          ← Or disable
Description: Custom description
```

**Step 5: Save Changes**
- Click **Save**
- Configuration saved to Redis ✅
- See success message

**Step 6: Restart API**
```bash
# Development
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start

# Production (with zero downtime)
systemctl restart analyticbot-api
```

**Step 7: Verify**
- Refresh dashboard
- Check "Reset At" time updated
- Make test API requests

---

### Method 2: Via API Endpoint

**Update a specific service:**
```bash
# Get admin JWT token
TOKEN="your_admin_jwt_token_here"

# Update bot operations to 500/minute
curl -X PUT https://api.analyticbot.org/admin/rate-limits/configs/bot_operations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 500,
    "period": "minute",
    "enabled": true,
    "description": "Increased for high traffic"
  }'
```

**Reload configurations without restart:**
```bash
curl -X POST https://api.analyticbot.org/admin/rate-limits/reload \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "success": true,
  "updated_count": 1,
  "message": "Successfully reloaded 1 rate limit configuration(s). API restart recommended for full effect.",
  "requires_restart": true
}
```

---

### Method 3: Via Script

**Use the reload script:**
```bash
# Set admin token
export ADMIN_TOKEN="your_admin_jwt_token"

# Run reload script
./scripts/reload-rate-limits.sh
```

The script will:
1. ✅ Call the reload endpoint
2. ✅ Show updated count
3. ⚠️ Prompt for API restart if needed
4. 🔄 Optionally restart API automatically

---

## Available Services

| Service | Default Limit | Period | Description |
|---------|--------------|--------|-------------|
| **bot_creation** | 5 | hour | Bot creation operations |
| **bot_operations** | 300 | minute | General bot operations |
| **admin_operations** | 30 | minute | Admin panel operations |
| **auth_login** | 30 | minute | Login attempts |
| **auth_register** | 3 | hour | Registration attempts |
| **public_read** | 500 | minute | Public API reads |
| **webhook** | 1000 | minute | Webhook callbacks |
| **analytics** | 60 | minute | Analytics queries |
| **export** | 10 | minute | Data export operations |
| **ai_chat** | 20 | minute | AI chat requests |
| **channel_add** | 30 | minute | Channel add operations |
| **report_generate** | 5 | minute | Report generation |
| **global** | 2000 | minute | Global API rate limit |

---

## Recommended Limits

### For 100k Users (Conservative)

```
bot_operations:    300/minute per IP
public_read:       500/minute per IP
auth_login:        30/minute per IP
webhook:          1000/minute per IP
```

**Total Capacity**: 100k users × 500 req/min = **50 million req/min**

### For 100k Users (Aggressive)

```
bot_operations:    1000/minute per IP
public_read:      1500/minute per IP
auth_login:        100/minute per IP
webhook:          2000/minute per IP
```

**Total Capacity**: 100k users × 1500 req/min = **150 million req/min**

### When to Increase

Increase limits if:
- ✅ Legitimate users hitting rate limits
- ✅ 429 errors in monitoring dashboards
- ✅ User complaints about "too many requests"
- ✅ Traffic patterns show consistent high usage

### When NOT to Increase

Keep limits if:
- ❌ Seeing DDoS attack patterns
- ❌ Single IPs making excessive requests
- ❌ Bot/scraper traffic detected
- ❌ No legitimate user complaints

---

## Monitoring Usage

### Real-time Dashboard

**Navigate to Admin → Rate Limits**

View:
- 🟢 **Green bar** (0-50%): Healthy usage
- 🟡 **Yellow bar** (50-80%): Moderate usage
- 🟠 **Orange bar** (80-95%): High usage
- 🔴 **Red bar** (95-100%): At limit

### Check Specific Service

```bash
TOKEN="your_admin_jwt_token"

curl https://api.analyticbot.org/admin/rate-limits/stats/bot_operations \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

Response:
```json
{
  "service": "bot_operations",
  "current_usage": 187,
  "limit": 300,
  "period": "minute",
  "remaining": 113,
  "reset_at": "2025-12-24T12:35:00Z",
  "utilization_percent": 62.3,
  "is_at_limit": false
}
```

### Check Redis Directly

```bash
docker exec analyticbot-redis redis-cli

# View all rate limit configs
> HGETALL "ratelimit:config"

# View specific service stats
> GET "ratelimit:stats:bot_operations:global:202512241230"
"187"

# View all stat keys
> KEYS "ratelimit:stats:*"
```

---

## Troubleshooting

### Changes Not Applying

**Problem**: Updated rate limits but still seeing old limits

**Solution**:
1. Verify save was successful (check Redis)
2. Restart API server
3. Clear any CDN/proxy caches

```bash
# Check if config is in Redis
docker exec analyticbot-redis redis-cli HGET ratelimit:config bot_operations

# Restart API
make -f Makefile.dev dev-stop
make -f Makefile.dev dev-start

# Verify new limits loaded
tail -f logs/dev_api.log | grep "rate limit"
```

### 429 Too Many Requests

**Problem**: Users getting "Too Many Requests" errors

**Solutions**:

1. **Check if legitimate traffic**:
   ```bash
   # View top IPs
   curl https://api.analyticbot.org/admin/rate-limits/stats \
     -H "Authorization: Bearer $TOKEN" | jq '.stats[] | select(.utilization_percent > 80)'
   ```

2. **Increase limit temporarily**:
   - Go to admin dashboard
   - Edit service
   - Increase limit by 2x
   - Save and restart API

3. **Whitelist specific IPs** (if trusted):
   ```bash
   # Add to .env.production
   RATE_LIMIT_WHITELIST=10.0.0.1,10.0.0.2
   ```

4. **Reset user's limits**:
   ```bash
   curl -X POST https://api.analyticbot.org/admin/rate-limits/reset/user/12345 \
     -H "Authorization: Bearer $TOKEN"
   ```

### Rate Limits Disabled

**Problem**: Rate limiting not working at all

**Check**:
```bash
# Check if disabled in env
grep RATE_LIMIT .env.production

# Should be:
RATE_LIMITING_ENABLED=true
RATE_LIMIT_ENABLED=true
```

**Fix**:
```bash
# Enable in .env.production
echo "RATE_LIMITING_ENABLED=true" >> .env.production
echo "RATE_LIMIT_ENABLED=true" >> .env.production

# Restart API
make -f Makefile.dev dev-start
```

---

## Best Practices

### 1. Monitor Before Changing

- ✅ Check current utilization
- ✅ Look at historical patterns
- ✅ Identify peak usage times
- ❌ Don't change blindly

### 2. Change Gradually

- ✅ Increase by 50% at a time
- ✅ Monitor for 24 hours
- ✅ Adjust again if needed
- ❌ Don't 10x limits immediately

### 3. Document Changes

- ✅ Note why you changed
- ✅ Record old and new values
- ✅ Track impact on users
- ❌ Don't forget what you changed

### 4. Test After Changes

```bash
# Make 100 test requests
for i in {1..100}; do
  curl https://api.analyticbot.org/dashboard \
    -H "Authorization: Bearer $TOKEN" &
done
wait

# Check if any were rate limited (429)
```

### 5. Have Rollback Plan

```bash
# Before changing, note current config
curl https://api.analyticbot.org/admin/rate-limits/configs/bot_operations \
  -H "Authorization: Bearer $TOKEN" > backup_bot_ops.json

# If issues, restore
curl -X PUT https://api.analyticbot.org/admin/rate-limits/configs/bot_operations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @backup_bot_ops.json
```

---

## API Reference

### Get All Configs

```http
GET /admin/rate-limits/configs
Authorization: Bearer {admin_token}
```

### Get Specific Config

```http
GET /admin/rate-limits/configs/{service_name}
Authorization: Bearer {admin_token}
```

### Update Config

```http
PUT /admin/rate-limits/configs/{service_name}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "limit": 500,
  "period": "minute",
  "enabled": true,
  "description": "Updated limit"
}
```

### Get Dashboard

```http
GET /admin/rate-limits/dashboard
Authorization: Bearer {admin_token}
```

### Reload Configs

```http
POST /admin/rate-limits/reload
Authorization: Bearer {admin_token}
```

### Reset User Limits

```http
POST /admin/rate-limits/reset/user/{user_id}
Authorization: Bearer {admin_token}
```

### Reset IP Limits

```http
POST /admin/rate-limits/reset/ip/{ip_address}
Authorization: Bearer {admin_token}
```

---

## Production Deployment Checklist

Before deploying rate limit changes to production:

- [ ] Test changes in development environment
- [ ] Verify configs saved to Redis
- [ ] Check API restart doesn't cause errors
- [ ] Monitor first hour after deployment
- [ ] Have rollback commands ready
- [ ] Document the changes
- [ ] Notify team of the update
- [ ] Watch for 429 errors
- [ ] Check user complaints/support tickets
- [ ] Verify performance impact

---

## Emergency Procedures

### Too Many 429 Errors

```bash
# 1. Increase all limits by 2x
for service in bot_operations public_read auth_login; do
  CURRENT=$(curl -s https://api.analyticbot.org/admin/rate-limits/configs/$service \
    -H "Authorization: Bearer $TOKEN" | jq '.limit')
  NEW=$((CURRENT * 2))
  curl -X PUT https://api.analyticbot.org/admin/rate-limits/configs/$service \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"limit\": $NEW}"
done

# 2. Restart API
make -f Makefile.dev dev-stop && make -f Makefile.dev dev-start
```

### DDoS Attack

```bash
# 1. Identify attacking IPs
curl https://api.analyticbot.org/admin/rate-limits/stats \
  -H "Authorization: Bearer $TOKEN" | \
  jq '.stats[] | select(.utilization_percent == 100)'

# 2. Block at firewall level
sudo ufw deny from 1.2.3.4

# 3. Lower global limit temporarily
curl -X PUT https://api.analyticbot.org/admin/rate-limits/configs/global \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 100, "period": "minute"}'
```

### Redis Down

Rate limiting will fall back to in-memory storage (per-process). This means:
- ⚠️ Limits are per API instance, not global
- ⚠️ Config updates won't persist
- ⚠️ Stats won't be tracked

**Fix**: Restart Redis ASAP.

---

**Last Updated**: December 24, 2025  
**Version**: 1.0 (Phase 1 Implementation)  
**Status**: ✅ Functional with API restart requirement
