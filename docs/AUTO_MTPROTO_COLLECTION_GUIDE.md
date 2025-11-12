# 🤖 Auto MTProto Collection System - Complete Guide

## ✅ YES! Your System HAS Automatic MTProto Collection

You have **6 MTProto workers** running automatically in the background! They collect data from all channels every **10 minutes** by default.

---

## 📊 Current Status

### Active Workers:
```bash
# Currently running MTProto workers:
PID: 1884979 - Running since Nov 06 (5h 25m uptime)
PID: 1948772 - Running since 05:44 (1h 20m uptime)
PID: 1990551 - Running since 08:45 (44m uptime)
PID: 2000201 - Running since 09:34 (35m uptime)
PID: 2017333 - Running since 10:52 (23m uptime)
PID: 2035673 - Running since 12:08 (16m uptime)
```

**Total**: 6 workers running with `--interval 10` (every 10 minutes)

---

## 🔄 How Automatic Collection Works

### 1. **Continuous Worker Service**

**File**: `apps/mtproto/worker.py`

The worker runs continuously and:
- Collects data from **ALL users** with MTProto enabled
- Runs every **10 minutes** by default (configurable)
- Fetches new messages from all channels
- Updates existing message metrics (views, reactions, etc.)

### 2. **Collection Cycle**

```
Every 10 minutes:
  ↓
Get all users with MTProto enabled
  ↓
For each user:
  ├─ Get user's MTProto credentials
  ├─ Connect to Telegram
  ├─ Get user's channels from database
  ├─ For each channel:
  │   ├─ Fetch latest 50 messages (configurable)
  │   ├─ Store new posts
  │   └─ Update existing metrics
  └─ Disconnect
  ↓
Wait 10 minutes
  ↓
Repeat
```

### 3. **What Gets Collected Automatically**

- ✅ **New messages** posted to channels
- ✅ **Updated view counts** for existing posts
- ✅ **Reactions** (likes, emoji reactions)
- ✅ **Forwards** count
- ✅ **Replies** count
- ✅ **Message edits** and updates

---

## ⚙️ Configuration

### Current Settings (from your `.env`):

```bash
MTPROTO_ENABLED=true                      # Master switch: ON
MTPROTO_HISTORY_ENABLED=true              # Historical collection: ON
MTPROTO_UPDATES_ENABLED=true              # Real-time updates: ON
MTPROTO_STATS_ENABLED=true                # Official stats: ON
MTPROTO_HISTORY_LIMIT_PER_RUN=5000        # Max messages per run
MTPROTO_CONCURRENCY=4                     # Parallel requests
```

### Worker Interval:

**Default**: 10 minutes between collection cycles
**Configurable**: Change with `--interval` flag

---

## 🎛️ Managing the Workers

### Check Running Workers:
```bash
ps aux | grep "mtproto.worker" | grep -v grep
```

### Check Worker Logs:
```bash
# If run with systemd (not currently)
journalctl -u mtproto-worker -f

# If run in Docker
docker logs analyticbot-mtproto -f

# If run manually
tail -f /tmp/mtproto_worker.log  # Or wherever logs are stored
```

### Start Worker Manually:
```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate

# Run with default 10-minute interval
python -m apps.mtproto.worker

# Run with custom interval (every 5 minutes)
python -m apps.mtproto.worker --interval 5

# Run once and exit
python -m apps.mtproto.worker --once

# Run for specific user only
python -m apps.mtproto.worker --user-id 844338517

# Check status
python -m apps.mtproto.worker --status
```

### Stop Workers:
```bash
# Stop all MTProto workers
pkill -f "mtproto.worker"

# Stop specific worker by PID
kill <PID>
```

### Start Worker in Background:
```bash
cd /home/abcdeveloper/projects/analyticbot
nohup .venv/bin/python -m apps.mtproto.worker --interval 10 > /tmp/mtproto_worker.log 2>&1 &
```

---

## 📋 Worker Command Options

```bash
python -m apps.mtproto.worker [OPTIONS]

Options:
  --interval MINUTES    Collection interval in minutes (default: 10)
  --once               Run collection once and exit
  --user-id USER_ID    Collect only for specific user
  --status             Show service status and exit
  --log-level LEVEL    Set logging level (DEBUG, INFO, WARNING, ERROR)
```

---

## 🔍 How to Verify It's Working

### 1. Check Worker Status:
```bash
python -m apps.mtproto.worker --status
```

### 2. Check Database Growth:
```bash
docker exec analyticbot-db psql -U analytic -d analytic_bot -c "
SELECT
    channel_id,
    COUNT(*) as posts,
    MAX(date) as latest_post
FROM posts
WHERE channel_id = 1002678877654
GROUP BY channel_id;
"
```

### 3. Check Recent Activity:
```bash
docker exec analyticbot-db psql -U analytic -d analytic_bot -c "
SELECT
    msg_id,
    LEFT(text, 50) as preview,
    date,
    views
FROM posts
WHERE channel_id = 1002678877654
ORDER BY date DESC
LIMIT 10;
"
```

---

## 📦 Docker Deployment (Optional)

Your system can also run MTProto as a Docker service:

**File**: `docker/docker-compose.yml`

```yaml
mtproto:
  command: python scripts/mtproto_service.py service
  container_name: analyticbot-mtproto
  profiles:
    - mtproto
  restart: unless-stopped
```

### Start Docker Service:
```bash
docker-compose --profile mtproto up -d
```

---

## 🎯 What's Happening Now

### Your ABC LEGACY NEWS Channel:

1. **Manual collection** you ran earlier collected **203 posts**
2. **Automatic workers** (6 running) collect new posts every **10 minutes**
3. **Real-time updates** track view counts, reactions as they change

### Why You Only Saw 52 Posts Initially:

The automatic workers were running with the **old limit of 50** messages per run. They would collect:
- First run: 50 messages
- Wait 10 minutes
- Second run: 50 more messages (but only NEW ones, not re-collecting old ones)

So it was slowly collecting, but:
- You have **hundreds or thousands** of historical posts
- Workers collect **50 new/recent** messages per cycle
- Without full backfill, you only see recent posts

---

## 🚀 Optimizing Automatic Collection

### For Better Coverage:

1. **Increase collection limit** (already done):
   ```bash
   MTPROTO_HISTORY_LIMIT_PER_RUN=5000
   ```

2. **Run full backfill once** (recommended):
   ```bash
   python -m apps.mtproto.worker --once --user-id 844338517
   ```
   This will fetch up to 5000 historical messages

3. **Reduce interval for frequent channels**:
   ```bash
   # Restart workers with 5-minute interval
   pkill -f "mtproto.worker"
   python -m apps.mtproto.worker --interval 5 &
   ```

---

## 🔐 Multi-Tenant Support

The system supports **multiple users**, each with their own:
- MTProto credentials
- Channels
- Collection settings
- Session management

**Current User**: ID 844338517 (your account)

---

## 📈 Performance & Rate Limiting

### Telegram Rate Limits:
- Workers respect Telegram's flood protection
- Automatic 15-20 second delays when rate limited
- Smart retry with exponential backoff

### Your Configuration:
```bash
MTPROTO_CONCURRENCY=4          # 4 parallel requests
MTPROTO_SLEEP_THRESHOLD=2.0    # 2 second delay between requests
```

---

## 🛠️ Troubleshooting

### Workers Not Collecting?

1. **Check workers are running**:
   ```bash
   ps aux | grep mtproto.worker
   ```

2. **Check MTProto is enabled**:
   ```bash
   grep MTPROTO_ENABLED .env
   ```

3. **Check user has credentials**:
   ```bash
   docker exec analyticbot-db psql -U analytic -d analytic_bot -c "
   SELECT user_id, mtproto_enabled
   FROM user_bot_credentials
   WHERE user_id = 844338517;
   "
   ```

4. **Check worker logs**:
   ```bash
   tail -f /tmp/mtproto_worker.log
   ```

### Workers Running but Not Collecting?

1. **Check collection interval** - might be waiting for next cycle
2. **Check if hitting rate limits** - Telegram enforces delays
3. **Run manual collection** to force immediate run:
   ```bash
   python -m apps.mtproto.worker --once
   ```

---

## 📊 Monitoring Dashboard

### Check Collection Stats:
```sql
-- Total posts per channel
SELECT
    c.title,
    COUNT(p.id) as total_posts,
    MIN(p.date) as oldest,
    MAX(p.date) as newest
FROM channels c
LEFT JOIN posts p ON c.id = p.channel_id
WHERE c.user_id = 844338517
GROUP BY c.id, c.title;

-- Posts collected today
SELECT
    COUNT(*) as posts_today
FROM posts
WHERE channel_id = 1002678877654
  AND date >= CURRENT_DATE;

-- Recent collection activity
SELECT
    msg_id,
    date,
    views,
    reactions_count
FROM posts
WHERE channel_id = 1002678877654
ORDER BY date DESC
LIMIT 20;
```

---

## 🎉 Summary

### ✅ You Have Automatic Collection:
- **6 workers** running in background
- **Every 10 minutes** collection cycle
- **Automatic** for all users with MTProto enabled
- **Real-time** view count updates
- **Multi-tenant** support

### ✅ Configuration Updated:
- Collection limit increased to **5000** per run
- Reaction serialization bug **fixed**
- Manual backfill script **created**

### ✅ Next Steps:
1. **Wait for automatic workers** to collect more posts (every 10 min)
2. **Run manual backfill** if you want all historical posts now
3. **Check "All Posts" page** in frontend to see results

---

**Generated**: November 7, 2025
**Workers Running**: 6 active
**Collection Interval**: 10 minutes
**Your User ID**: 844338517
**Channel**: ABC LEGACY NEWS (1002678877654)
