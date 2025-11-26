# Replies vs Comments Implementation Plan

## 📊 Current State Analysis

### ✅ What We Have Now (Comments)
Your system currently tracks **"replies_count"** which represents **discussion group comments** on channel posts:
- When a channel has a linked discussion group
- Users click "Leave a comment" under a post
- Comments appear in the discussion group
- Backend field: `replies_count` in `post_metrics` table

### 🎯 What We Need to Add (Threaded Replies)
We need to add support for **threaded replies** - direct replies to specific messages:
- When users click "Reply" on a message
- Creates a threaded conversation
- Available in groups, supergroups, and channels
- New backend field needed: `threaded_replies_count`

---

## 🔍 Backend Analysis

### Database Schema

#### Current: `post_metrics` table (from migration 0023)
```sql
CREATE TABLE post_metrics (
    channel_id BIGINT NOT NULL,
    msg_id BIGINT NOT NULL,
    snapshot_time TIMESTAMP WITH TIME ZONE NOT NULL,
    views BIGINT,
    forwards BIGINT,
    replies_count BIGINT,           -- Currently: discussion comments
    reactions JSON,
    reactions_count BIGINT,
    PRIMARY KEY (channel_id, msg_id, snapshot_time)
)
```

#### Needed: Add new column
```sql
ALTER TABLE post_metrics
ADD COLUMN threaded_replies_count BIGINT DEFAULT 0
COMMENT 'Number of direct threaded replies to this message';
```

### Telegram MTProto Parser

**Current parsing** (`infra/tg/parsers.py:78-81`):
```python
replies_count = 0
if hasattr(message, "replies") and message.replies:
    replies_count = getattr(message.replies, "replies", 0) or 0
```

**Issue**: The current code reads `message.replies.replies` which gives the **total reply count**, but doesn't distinguish between:
- `message.replies.replies` - Total replies (includes both comments and threaded replies)
- `message.replies.comments` - Discussion group comments only
- Threaded replies = `replies.replies - replies.comments`

**Telegram MTProto `MessageReplies` structure**:
```python
class MessageReplies:
    replies: int              # Total number of replies (comments + threaded)
    replies_pts: int          # Points for updates
    comments: bool            # True if has discussion group
    recent_repliers: list     # Recent users who replied
    channel_id: int           # Discussion group channel ID (if comments=True)
    max_id: int              # Latest reply ID
    read_max_id: int         # Latest read reply ID
```

---

## 📋 Implementation Plan

### Phase 1: Database Migration ✅ HIGH PRIORITY

**File**: Create new migration `0031_add_threaded_replies_count.py`

```python
"""Add threaded_replies_count column to post_metrics

Revision ID: 0031_add_threaded_replies_count
Revises: 0030
Create Date: 2025-11-25
"""
import sqlalchemy as sa
from alembic import op

revision = "0031"
down_revision = "0030"  # Update to your latest migration
branch_labels = None
depends_on = None

def upgrade():
    """Add threaded_replies_count column"""
    op.add_column(
        'post_metrics',
        sa.Column(
            'threaded_replies_count',
            sa.BigInteger(),
            nullable=True,
            server_default='0',
            comment='Number of direct threaded replies (excluding discussion comments)'
        )
    )

    # Create index for analytics queries
    op.create_index(
        'idx_post_metrics_threaded_replies',
        'post_metrics',
        ['channel_id', 'threaded_replies_count']
    )

    # Backfill: Set to 0 for existing records
    op.execute("UPDATE post_metrics SET threaded_replies_count = 0 WHERE threaded_replies_count IS NULL")

def downgrade():
    """Remove threaded_replies_count column"""
    op.drop_index('idx_post_metrics_threaded_replies', 'post_metrics')
    op.drop_column('post_metrics', 'threaded_replies_count')
```

### Phase 2: Update Telegram Parser ✅ HIGH PRIORITY

**File**: `infra/tg/parsers.py` (lines 78-81)

**Current Code**:
```python
replies_count = 0
if hasattr(message, "replies") and message.replies:
    replies_count = getattr(message.replies, "replies", 0) or 0
```

**New Code**:
```python
# Extract reply metrics
replies_count = 0        # Discussion group comments
threaded_replies_count = 0  # Direct threaded replies
total_replies = 0        # Total (for logging/debugging)

if hasattr(message, "replies") and message.replies:
    total_replies = getattr(message.replies, "replies", 0) or 0
    is_comments_enabled = getattr(message.replies, "comments", False)

    if is_comments_enabled:
        # Has discussion group - total includes comments
        # We can't distinguish without fetching actual replies
        # Conservative approach: put all in replies_count for channels
        replies_count = total_replies
        threaded_replies_count = 0
    else:
        # No discussion group - these are threaded replies
        replies_count = 0
        threaded_replies_count = total_replies
```

**Better approach (if you want accurate split)**:
```python
# For accurate distinction, check message type
if channel_id and not is_supergroup:
    # Channel post with discussion group
    replies_count = total_replies  # Discussion comments
    threaded_replies_count = 0
else:
    # Group/supergroup message - direct threaded replies
    replies_count = 0
    threaded_replies_count = total_replies
```

**Update metrics dict** (line 132):
```python
"metrics": {
    "channel_id": channel_id,
    "msg_id": message_id,
    "views": views,
    "forwards": forwards,
    "replies_count": replies_count,              # Discussion comments
    "threaded_replies_count": threaded_replies_count,  # NEW
    "reactions_json": reactions,
    "reactions_count": reactions_count,
    "ts": datetime.utcnow(),
},
```

### Phase 3: Update Repository Layer ✅ MEDIUM PRIORITY

**File**: `infra/db/repositories/post_metrics_repository.py`

**Update `save_metrics` method** (line 53):
```python
INSERT INTO post_metrics (
    channel_id, msg_id, views, forwards, replies_count,
    threaded_replies_count,  -- NEW
    reactions, reactions_count, snapshot_time
) VALUES (...)
ON CONFLICT (channel_id, msg_id, snapshot_time)
DO UPDATE SET
    views = GREATEST(post_metrics.views, EXCLUDED.views),
    forwards = GREATEST(post_metrics.forwards, EXCLUDED.forwards),
    replies_count = GREATEST(post_metrics.replies_count, EXCLUDED.replies_count),
    threaded_replies_count = GREATEST(post_metrics.threaded_replies_count, EXCLUDED.threaded_replies_count),  -- NEW
    reactions_count = GREATEST(post_metrics.reactions_count, EXCLUDED.reactions_count),
    ...
```

**Add parameter**:
```python
def save_metrics(
    self,
    channel_id: int,
    msg_id: int,
    views: int = 0,
    forwards: int = 0,
    replies_count: int = 0,
    threaded_replies_count: int = 0,  # NEW
    reactions_count: int = 0,
    ...
):
```

### Phase 4: Update API Models ✅ MEDIUM PRIORITY

**File**: `apps/api/routers/posts_router.py`

**Update `PostMetrics` model** (line 32):
```python
class PostMetrics(BaseModel):
    """Metrics for a specific post"""
    views: int = 0
    forwards: int = 0
    replies_count: int = 0           # Discussion group comments
    threaded_replies_count: int = 0  # NEW: Threaded replies
    reactions_count: int = 0
    snapshot_time: str | None = None
```

**File**: `apps/api/routers/analytics_top_posts_router.py`

**Update `TopPostMetrics` model** (line 20):
```python
class TopPostMetrics(BaseModel):
    msg_id: int
    date: str
    text: str | None
    views: int
    forwards: int
    replies_count: int           # Discussion comments
    threaded_replies_count: int  # NEW: Threaded replies
    reactions_count: int
    engagement_rate: float
```

**Update `TopPostsSummary` model** (line 33):
```python
class TopPostsSummary(BaseModel):
    total_views: int
    total_forwards: int
    total_reactions: int
    total_replies: int              # Discussion comments
    total_threaded_replies: int     # NEW: Threaded replies
    average_engagement_rate: float
    post_count: int
```

### Phase 5: Update SQL Queries ✅ MEDIUM PRIORITY

**Files to update**:
- `apps/api/routers/analytics_top_posts_router.py`
- `apps/api/routers/analytics_post_dynamics_router.py`
- `infra/db/repositories/post_repository.py`

**Example query update** (analytics_top_posts_router.py:162):
```sql
SELECT
    p.channel_id,
    p.msg_id,
    p.date,
    p.text,
    latest_metrics.views,
    latest_metrics.forwards,
    latest_metrics.replies_count,
    latest_metrics.threaded_replies_count,  -- NEW
    latest_metrics.reactions_count,
    COALESCE(
        ((latest_metrics.forwards +
          latest_metrics.replies_count +
          latest_metrics.threaded_replies_count +  -- NEW
          latest_metrics.reactions_count)::float
         / NULLIF(latest_metrics.views, 0) * 100),
        0
    ) as engagement_rate
FROM posts p
CROSS JOIN LATERAL (
    SELECT views, forwards, replies_count,
           threaded_replies_count,  -- NEW
           reactions_count
    FROM post_metrics
    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
    ORDER BY snapshot_time DESC
    LIMIT 1
) latest_metrics
```

**Summary query update** (analytics_top_posts_router.py:302):
```sql
SELECT
    COALESCE(SUM(latest_metrics.views), 0)::int as total_views,
    COALESCE(SUM(latest_metrics.forwards), 0)::int as total_forwards,
    COALESCE(SUM(latest_metrics.reactions_count), 0)::int as total_reactions,
    COALESCE(SUM(latest_metrics.replies_count), 0)::int as total_replies,
    COALESCE(SUM(latest_metrics.threaded_replies_count), 0)::int as total_threaded_replies,  -- NEW
    ...
```

### Phase 6: Frontend Updates ✅ ALREADY DONE

Frontend is already prepared (from our previous changes):
- Type definitions support both `comments_count` and `replies_count`
- Store interfaces ready for `totalComments` and `totalReplies`
- Components can display both metrics separately
- Just need to update API response mapping

---

## 🧪 Testing Plan

### 1. Database Migration Test
```bash
# Apply migration
cd /home/abcdeveloper/projects/analyticbot
make db-migrate-up

# Verify column exists
make db-shell
\d post_metrics
SELECT channel_id, msg_id, replies_count, threaded_replies_count
FROM post_metrics LIMIT 5;
```

### 2. MTProto Parser Test
```python
# Add test in infra/tg/test_parsers.py
def test_parse_message_with_threaded_replies():
    message = MockMessage(
        id=123,
        replies=MockReplies(replies=10, comments=False)
    )
    result = normalize_message(message, None)
    assert result['metrics']['threaded_replies_count'] == 10
    assert result['metrics']['replies_count'] == 0
```

### 3. API Response Test
```bash
curl http://localhost:8000/api/posts/list?channel_id=123 | jq '.posts[0].metrics'
# Should show both replies_count and threaded_replies_count
```

### 4. Frontend Integration Test
- Check browser console for API responses
- Verify metrics display correctly in UI
- Test filtering by comments vs replies

---

## 📝 Summary of Changes Required

### Backend Files to Modify:
1. ✅ **New migration**: `infra/db/alembic/versions/0031_add_threaded_replies_count.py`
2. ✅ **Parser**: `infra/tg/parsers.py` (lines 78-132)
3. ✅ **Repository**: `infra/db/repositories/post_metrics_repository.py` (line 25, 53, 59)
4. ✅ **API Models**:
   - `apps/api/routers/posts_router.py` (line 32)
   - `apps/api/routers/analytics_top_posts_router.py` (line 20, 33)
5. ✅ **SQL Queries**: Update all SELECT/INSERT queries in:
   - `apps/api/routers/analytics_top_posts_router.py` (multiple locations)
   - `apps/api/routers/analytics_post_dynamics_router.py` (line 253, 258)
   - `infra/db/repositories/post_repository.py` (line 238, 242)

### Frontend Files (Already Done):
- ✅ Type definitions updated
- ✅ Store interfaces ready
- ✅ Components support both metrics

---

## 🚀 Rollout Strategy

### Option A: Gradual Rollout (Recommended)
1. **Week 1**: Add database column, update parser
2. **Week 2**: Collect data, verify accuracy
3. **Week 3**: Update API responses, test frontend
4. **Week 4**: Enable UI display of both metrics

### Option B: Fast Rollout
1. **Day 1**: Database migration + parser update
2. **Day 2**: API models + queries update
3. **Day 3**: Frontend integration + testing
4. **Day 4**: Production deployment

---

## ⚠️ Important Notes

### Data Accuracy Limitations
The Telegram MTProto API doesn't provide a direct way to distinguish between:
- Discussion group comments
- Direct threaded replies

**Our solution**:
- For **channels** with discussion groups: `replies_count` = all replies (mostly comments)
- For **groups/supergroups**: `threaded_replies_count` = all replies (threaded conversations)

**For 100% accuracy**, you would need to:
1. Fetch the actual replies using `GetRepliesRequest`
2. Check if each reply is in the discussion group or threaded
3. This adds significant API calls and complexity

### Performance Considerations
- New column adds ~8 bytes per metric snapshot
- Index on `threaded_replies_count` improves query performance
- Minimal impact on existing queries

### Backward Compatibility
- Old data will have `threaded_replies_count = 0`
- Frontend gracefully handles missing values
- API responses remain compatible

---

## 📞 Next Steps

**Ready to proceed?** Choose your approach:

1. **I'll implement everything** - Just say "yes, implement it all"
2. **Phase by phase** - Say "start with Phase 1" and we'll go step by step
3. **Custom approach** - Tell me which parts you want prioritized

**Estimated time**:
- Database migration: 10 minutes
- Parser + repository: 30 minutes
- API updates: 45 minutes
- Testing: 30 minutes
- **Total: ~2 hours**

Let me know how you want to proceed! 🚀
