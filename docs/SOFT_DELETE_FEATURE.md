# Soft Delete Feature for MTProto Messages

## Overview
Implemented soft delete functionality to detect and mark deleted Telegram messages while preserving historical data for analytics.

## Database Changes

### New Columns Added to `posts` Table:
```sql
ALTER TABLE posts ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE posts ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;

-- Indexes for performance
CREATE INDEX idx_posts_is_deleted ON posts(is_deleted);
CREATE INDEX idx_posts_channel_not_deleted ON posts(channel_id, is_deleted);
```

## How It Works

### 1. Detection Phase
After each collection, the system compares:
- **Telegram messages**: IDs fetched from Telegram API
- **Database messages**: IDs stored in the database

Messages in DB but NOT in Telegram = Deleted messages

### 2. Marking Deleted Messages
```python
UPDATE posts
SET is_deleted = TRUE,
    deleted_at = NOW(),
    updated_at = NOW()
WHERE channel_id = X
    AND msg_id NOT IN (fetched_message_ids)
    AND is_deleted = FALSE
```

### 3. Restoring Messages
If a previously deleted message reappears in Telegram:
```python
# Automatically restored during upsert
UPDATE posts
SET is_deleted = FALSE,
    deleted_at = NULL,
    text = <new_text>
WHERE channel_id = X AND msg_id = Y
```

## Example Workflow

```
Day 1: Channel has messages [1, 2, 3, 4, 5]
→ Database: [1, 2, 3, 4, 5] all with is_deleted=FALSE

Day 2: User deletes message 3 in Telegram
→ Channel: [1, 2, 4, 5]

Day 3: Collection runs
→ Telegram returns: [1, 2, 4, 5]
→ System detects: Message 3 is missing
→ Database updates: Message 3 marked is_deleted=TRUE, deleted_at=NOW()
→ Log: "🗑️ Marked 1 deleted messages for channel X"

Day 4: User restores message 3 (or it reappears)
→ Telegram returns: [1, 2, 3, 4, 5]
→ System detects: Message 3 exists again
→ Database updates: Message 3 marked is_deleted=FALSE, deleted_at=NULL
```

## API Behavior

### Default Queries (Exclude Deleted)
All API endpoints now exclude deleted messages by default:

```sql
-- Posts API
WHERE p.is_deleted = FALSE

-- Analytics API
WHERE p.is_deleted = FALSE
```

### Include Deleted (Optional)
To show deleted messages (for admin/audit views):
```sql
-- Show all including deleted
WHERE p.channel_id = X

-- Show only deleted
WHERE p.is_deleted = TRUE
```

## Statistics

### Per-Channel Stats
```sql
SELECT
    COUNT(*) FILTER (WHERE is_deleted = FALSE) as active_messages,
    COUNT(*) FILTER (WHERE is_deleted = TRUE) as deleted_messages,
    COUNT(*) as total_messages
FROM posts
WHERE channel_id = X;
```

**Example Output:**
```
active_messages | deleted_messages | total_messages
----------------|------------------|----------------
2763            | 3                | 2766
```

## Logging

Collection logs now include deletion stats:
```
INFO - 🗑️ Marked 3 deleted messages for channel -1002678877654
INFO - Completed peer -1002678877654: {
    'ingested': 0,
    'updated': 2763,
    'skipped': 0,
    'errors': 0,
    'deleted': 3
}
```

## Benefits

✅ **Data Preservation**: Historical messages kept for analytics
✅ **Accurate Stats**: Active vs deleted message counts
✅ **Audit Trail**: Know when messages were deleted (deleted_at)
✅ **Restoration Support**: Messages can be undeleted if they reappear
✅ **Clean UI**: Users see only active messages by default
✅ **Compliance**: Deleted content retained for legal/research needs

## Use Cases

### 1. Analytics & Reporting
- Show engagement trends excluding deleted content
- Compare active vs total messages over time
- Track content deletion patterns

### 2. Audit & Compliance
- See what content existed before deletion
- Preserve evidence for legal requirements
- Research historical content

### 3. Content Management
- Identify frequently deleted message types
- Track user content removal behavior
- Detect spam/abuse patterns

## Future Enhancements

### Optional: Show Deleted Messages in UI
```tsx
// Frontend option to show/hide deleted
<Checkbox
  label="Show deleted messages"
  onChange={(e) => setShowDeleted(e.target.checked)}
/>

// Display deleted messages differently
{message.is_deleted && (
  <Alert severity="warning">
    This message was deleted on {message.deleted_at}
  </Alert>
)}
```

### Optional: Permanent Deletion
```sql
-- Clean up old deleted messages (after 90 days)
DELETE FROM posts
WHERE is_deleted = TRUE
  AND deleted_at < NOW() - INTERVAL '90 days';
```

### Optional: Deletion Stats Dashboard
Show per-channel deletion metrics:
- Total deletions over time
- Most deleted message types
- Deletion rate trends

## Testing

Tested with real data:
```
Channel: ABC LEGACY NEWS (1002678877654)
- Total messages: 2766
- Active: 2763
- Deleted: 3 (messages 99999, 3271, 88888)
- Detection working: ✅
- Marking working: ✅
- API filtering: ✅
```

## Implementation Files

1. **Migration**: `infra/db/alembic/versions/0026_add_soft_delete_to_posts.py`
2. **Collector**: `apps/mtproto/collectors/history.py`
   - `_detect_and_mark_deleted_messages()` method
3. **Repository**: `infra/db/repositories/post_repository.py`
   - Updated `upsert_post()` with is_deleted support
4. **API Routers**:
   - `apps/api/routers/posts_router.py` - Added `is_deleted = FALSE` filter
   - `apps/api/routers/analytics_post_dynamics_router.py` - Added `is_deleted = FALSE` filter

## Summary

Soft delete is now fully functional:
- ✅ Database schema updated
- ✅ Detection logic implemented
- ✅ Marking/restoration working
- ✅ API queries filtered
- ✅ Tested with real data

Users will see only active messages, but deleted content is preserved for analytics and compliance needs.
