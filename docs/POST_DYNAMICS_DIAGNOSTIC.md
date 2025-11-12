# 🔍 MTProto Post Dynamics Diagnostic Report

**Date**: November 7, 2025
**Issue**: Post Dynamics analytics showing no data despite MTProto being enabled

## ❌ PROBLEM IDENTIFIED

**Root Cause**: The `posts` and `post_metrics` tables required for Post Dynamics are NOT in the database yet!

### Critical Finding:
The migration `0023_create_mtproto_posts_table.py` that creates these tables **exists in code** but has **NOT been run** on the database.

## 📊 Required Tables for Post Dynamics

### 1. `posts` table
- Stores Telegram messages
- Columns: channel_id, msg_id, date, text, created_at, updated_at
- Primary key: (channel_id, msg_id)

### 2. `post_metrics` table
- Stores time-series metrics (the KEY table for Post Dynamics!)
- Columns: channel_id, msg_id, snapshot_time, views, forwards, replies_count, reactions, reactions_count
- Primary key: (channel_id, msg_id, snapshot_time)
- Foreign key to posts table

## 🔄 Data Flow (When Working Properly)

```
MTProto Collectors → posts table → post_metrics table → Post Dynamics API → Frontend
      ↓                   ↓                ↓                      ↓              ↓
  Collect msgs      Store msgs     Store metrics      Query metrics   Display charts
```

## 🛠️ What's Currently Happening

1. ✅ **Frontend**: Correctly calling `/analytics/posts/dynamics/post-dynamics/{channel_id}`
2. ✅ **Backend Router**: Correctly configured to query `post_metrics` table
3. ❌ **Database**: `posts` and `post_metrics` tables DON'T EXIST!
4. ❌ **MTProto Collectors**: Even if running, have nowhere to store metrics

## 📝 Frontend Code Analysis

### API Call (Correct ✅)
```typescript
// File: apps/frontend/src/shared/services/api/authAwareAPI.ts
async getPostDynamics(channelId: string, period: string = '24h'): Promise<any> {
    return this.makeRequest(`/analytics/posts/dynamics/post-dynamics/${channelId}?period=${period}`);
}
```

### Store Usage (Correct ✅)
```typescript
// File: apps/frontend/src/store/slices/analytics/useAnalyticsStore.ts
fetchPostDynamics: async (channelId: string, period: TimePeriod = '7d') => {
    const endpoint = channelId === 'demo_channel'
        ? '/demo/analytics/post-dynamics'
        : `/analytics/posts/dynamics/post-dynamics/${channelId}`;

    const postDynamics = await apiClient.get<PostDynamics>(endpoint, { params: { period } });
}
```

## 🔧 Backend Code Analysis

### Router Endpoint (Correct ✅)
```python
# File: apps/api/routers/analytics_post_dynamics_router.py
@router.get("/post-dynamics/{channel_id}", response_model=list[PostDynamicsPoint])
async def get_post_dynamics(
    channel_id: str,
    period: str = Query(default="24h", regex="^(1h|6h|12h|24h|7d|30d)$"),
    ...
):
    # Queries post_metrics table:
    query = """
        SELECT
            date_trunc($1, snapshot_time) as time_bucket,
            AVG(views)::int as avg_views,
            AVG(forwards)::int as avg_forwards,
            AVG(replies_count)::int as avg_replies,
            AVG(reactions_count)::int as avg_reactions,
            COUNT(DISTINCT msg_id) as post_count
        FROM post_metrics  ← THIS TABLE DOESN'T EXIST YET!
        WHERE channel_id = $2
            AND snapshot_time >= $3
            AND snapshot_time <= $4
        GROUP BY time_bucket
        ORDER BY time_bucket ASC
    """
```

## 🗄️ Database Migration Status

### Migration File: `0023_create_mtproto_posts_table.py`
```python
def upgrade():
    """Create posts and post_metrics tables for MTProto data collection"""

    # Creates posts table
    op.create_table("posts", ...)

    # Creates post_metrics table with foreign key to posts
    op.create_table("post_metrics", ...)
```

**Status**: ⚠️ **NOT RUN ON DATABASE YET**

### Current Database State:
- ❌ `posts` table: NOT EXISTS
- ❌ `post_metrics` table: NOT EXISTS
- ✅ `channels` table: EXISTS (1 row - ABC LEGACY NEWS)
- ⚠️ `channel_mtproto_settings` table: NOT EXISTS (migration issue)

## 🎯 SOLUTION

### Step 1: Run Pending Migrations
```bash
cd /home/abcdeveloper/projects/analyticbot
.venv/bin/alembic upgrade head
```

This will create:
- `posts` table
- `post_metrics` table
- `channel_mtproto_settings` table (if migration fixed)

### Step 2: Verify Tables Created
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name IN ('posts', 'post_metrics');
```

### Step 3: Enable MTProto Collection
Ensure MTProto collectors are running:
- `updates_collector` - for real-time updates
- `history_collector` - for historical data

### Step 4: Verify Data Collection
```sql
-- Check if posts are being collected
SELECT COUNT(*) FROM posts;

-- Check if metrics are being tracked
SELECT COUNT(*) FROM post_metrics;

-- Check recent metrics
SELECT * FROM post_metrics ORDER BY snapshot_time DESC LIMIT 5;
```

### Step 5: Test Frontend
Once data exists, the Post Dynamics chart should show data automatically!

## 🔍 Additional Checks Needed

1. **MTProto Collectors Status**: Are they running?
   ```bash
   # Check if collector processes are running
   ps aux | grep collector
   ```

2. **MTProto Settings**: Is MTProto enabled for ABC LEGACY NEWS channel?
   ```sql
   SELECT * FROM channel_mtproto_settings WHERE channel_id = 1002678877654;
   ```

3. **Channel Access**: Does the user have MTProto credentials configured?

## 📌 Key Takeaways

1. **Frontend Code**: ✅ Perfect - no changes needed
2. **Backend Code**: ✅ Perfect - no changes needed
3. **Database Schema**: ❌ **MISSING TABLES** - Need to run migrations
4. **MTProto Collectors**: ⚠️ Status unknown - need to verify

## 🚀 Next Actions

1. Run `alembic upgrade head` to create missing tables
2. Verify MTProto collectors are running
3. Check if data starts appearing in `post_metrics`
4. Test Post Dynamics chart in frontend

---

**Conclusion**: The issue is NOT with the code - both frontend and backend are correctly implemented. The problem is that the database tables don't exist yet because migrations haven't been run.
