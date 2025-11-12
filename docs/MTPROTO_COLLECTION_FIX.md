# MTProto Collection Issue & Solution Report

## 🔍 Problem Identified

Your ABC LEGACY NEWS channel was only showing **52 posts** instead of all available posts.

### Root Causes:

1. **Low Collection Limit**: `MTPROTO_HISTORY_LIMIT_PER_RUN` was set to only **50** messages per collection run
2. **Reaction Serialization Bug**: `ReactionEmoji` objects couldn't be JSON serialized, causing some messages to fail
3. **No Automatic Re-collection**: The system collected once and stopped

## ✅ Solutions Applied

### 1. Increased Collection Limit
**File**: `.env`
```bash
# OLD
MTPROTO_HISTORY_LIMIT_PER_RUN=50

# NEW
MTPROTO_HISTORY_LIMIT_PER_RUN=5000
MTPROTO_CONCURRENCY=4
```

### 2. Fixed Reaction Serialization Bug
**File**: `infra/tg/parsers.py`

Fixed the parser to properly convert `ReactionEmoji` objects to JSON-serializable strings:
```python
# Now handles:
- ReactionEmoji (emoji reactions)
- ReactionCustomEmoji (custom emoji reactions)
- String reactions
- Unknown reaction types
```

### 3. Created Batch Collection Script
**File**: `scripts/batch_collect_abc.py`

Created a new script that:
- Collects in batches of 1000 messages
- Respects Telegram's rate limits
- Runs up to 10 batches
- Logs progress to `/tmp/abc_collection.log`

## 📊 Current Status

### Before Fixes:
- **Posts collected**: 52
- **Date range**: Limited
- **Issues**: Serialization errors, low limits

### After Fixes (Currently Running):
- **Posts collected**: 203+ (increasing)
- **Collection status**: Running in background (PID: 2034188)
- **Rate limiting**: Active (Telegram enforces 15-20s delays)
- **Expected completion**: 30-60 minutes for full collection

## 🎯 How to Monitor Progress

### Check post count:
```bash
docker exec analyticbot-db psql -U analytic -d analytic_bot -c "SELECT COUNT(*) as total_posts FROM posts WHERE channel_id = 1002678877654;"
```

### Check collection logs:
```bash
tail -f /tmp/abc_collection.log
```

### Check if collection is running:
```bash
ps aux | grep batch_collect_abc
```

## 🔄 How Collection Works Now

### Data Flow:
```
Telegram MTProto API
        ↓
History Collector (batches of 1000)
        ↓
Parser (fixed reaction handling)
        ↓
Database (posts table)
        ↓
Frontend (your "All Posts" page)
```

### Rate Limiting:
- Telegram enforces **flood wait** (15-20 second delays)
- This is normal and protects against API abuse
- Collection continues automatically after delays

## 📈 Expected Results

### Full Collection Will Include:
- ✅ All historical messages from your channel
- ✅ Message content, dates, IDs
- ✅ View counts, forwards, replies
- ✅ Emoji reactions (now properly serialized)
- ✅ Links and media info

### Final Post Count:
- The script is collecting all available messages
- Your channel may have hundreds or thousands of posts
- Message IDs range from 3046 to 99999 (with gaps for deleted messages)

## 🛠️ Future Collections

### Manual Collection:
```bash
cd /home/abcdeveloper/projects/analyticbot
source .venv/bin/activate
python scripts/batch_collect_abc.py
```

### Background Collection:
```bash
cd /home/abcdeveloper/projects/analyticbot
nohup .venv/bin/python scripts/batch_collect_abc.py > /tmp/abc_collection.log 2>&1 &
```

### Check Progress:
```bash
# Watch logs in real-time
tail -f /tmp/abc_collection.log

# Check database count
docker exec analyticbot-db psql -U analytic -d analytic_bot -c \
  "SELECT COUNT(*) FROM posts WHERE channel_id = 1002678877654;"
```

## ⚙️ Configuration Settings

### Current .env Settings:
```bash
MTPROTO_ENABLED=true
MTPROTO_HISTORY_ENABLED=true
MTPROTO_UPDATES_ENABLED=true
MTPROTO_STATS_ENABLED=true
MTPROTO_HISTORY_LIMIT_PER_RUN=5000
MTPROTO_CONCURRENCY=4
```

### What These Mean:
- `MTPROTO_ENABLED`: Master switch for MTProto features
- `MTPROTO_HISTORY_ENABLED`: Allows backfilling message history
- `MTPROTO_UPDATES_ENABLED`: Collects real-time new messages
- `MTPROTO_STATS_ENABLED`: Fetches official Telegram statistics
- `MTPROTO_HISTORY_LIMIT_PER_RUN`: Max messages per collection (5000)
- `MTPROTO_CONCURRENCY`: Parallel requests (4 at a time)

## 🚀 Next Steps

### Wait for Collection:
The background collection is running now and will:
1. Collect up to 5000 messages in first batch
2. Wait 30 seconds
3. Collect next batch
4. Repeat up to 10 times or until all messages collected

### Verify Results:
After collection completes (30-60 minutes):
1. Go to your "All Posts" page
2. Filter by "ABC LEGACY NEWS" channel
3. You should see hundreds of posts instead of 52
4. Check the date range spans your entire channel history

### If Issues Persist:
1. Check logs: `tail -100 /tmp/abc_collection.log`
2. Check for errors in the output
3. Verify MTProto connection is active
4. Run collection manually to see detailed output

## 📞 Support Information

### Collection Running:
- **Process**: Background (nohup)
- **PID**: Check with `ps aux | grep batch_collect_abc`
- **Logs**: `/tmp/abc_collection.log`
- **Database**: `posts` table, channel_id = 1002678877654

### Key Files Modified:
1. `.env` - Added collection limits
2. `infra/tg/parsers.py` - Fixed reaction serialization
3. `scripts/batch_collect_abc.py` - New batch collection script

---

**Report Generated**: November 7, 2025, 12:03 UTC
**Status**: ✅ Collection in progress
**Expected Completion**: ~30-60 minutes
