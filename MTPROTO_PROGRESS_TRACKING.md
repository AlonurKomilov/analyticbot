# MTProto Collection Progress Tracking System

## Overview
Enhanced progress tracking system for MTProto message collection with real-time visibility into:
- Message-level progress (e.g., 122,304 / 1,000,000)
- Session tracking (e.g., Session 134 / 200)
- Current batch progress (e.g., 3,240 / 5,000 in current session)
- Performance metrics (messages/second, ETA)
- Phase tracking (fetching, processing, complete)

## Implementation Status

### ✅ Backend - Progress Tracking (COMPLETED)

**File**: `apps/mtproto/collectors/history.py`

**Added Features**:
1. **`_log_collection_progress()` method** - Logs detailed progress to `mtproto_audit_log` table with metadata:
   - `messages_current` / `messages_total` - Overall progress
   - `progress_percent` - Completion percentage
   - `session_current` / `session_total` - Session tracking
   - `session_messages_current` / `session_messages_limit` - Current batch progress
   - `speed_messages_per_second` - Collection speed
   - `eta_seconds` / `eta_minutes` - Time remaining
   - `phase` - Collection phase (fetching/processing/complete)

2. **Enhanced logging during collection**:
   - Progress logged every 500 messages during fetch
   - Progress logged every 500 messages during processing
   - Performance metrics calculated (speed, ETA)
   - Formatted output with commas for readability

3. **Audit log event type**: `collection_progress_detail`

### Example Progress Log Entry
```json
{
  "action": "collection_progress_detail",
  "user_id": 844338517,
  "channel_id": 1002678877654,
  "metadata": {
    "channel_id": 1002678877654,
    "phase": "fetching",
    "messages_current": 3240,
    "messages_total": 5000,
    "progress_percent": 64.8,
    "session_current": 134,
    "session_total": 200,
    "session_progress_percent": 67.0,
    "session_messages_current": 3240,
    "session_messages_limit": 5000,
    "session_messages_percent": 64.8,
    "speed_messages_per_second": 45.3,
    "eta_seconds": 38,
    "eta_minutes": 0.6
  }
}
```

## Frontend Display Options

### Option 1: Real-Time Progress Card (RECOMMENDED)
**Best for**: Active monitoring during collection

```
┌─────────────────────────────────────────────────────┐
│  🔄 Collection in Progress                          │
├─────────────────────────────────────────────────────┤
│  Channel: ABC LEGACY NEWS                           │
│                                                      │
│  Overall Progress                                   │
│  ████████████░░░░░░░░░░  67.0% (134/200 sessions)  │
│  672,000 / 1,000,000 messages                       │
│                                                      │
│  Current Session #134                               │
│  ████████████████░░░░  80.0% (4,000/5,000)         │
│                                                      │
│  Performance                                        │
│  ⚡ Speed: 45.3 messages/sec                        │
│  ⏱️ ETA: 12 minutes 34 seconds                      │
│  📊 Phase: Processing messages                      │
└─────────────────────────────────────────────────────┘
```

### Option 2: Compact Progress Bar
**Best for**: Dashboard summary

```
🔄 ABC LEGACY NEWS
Progress: [████████████████████░░░░░░░░░░] 67% (672K/1M)
Session 134/200 | 4.0K/5.0K | 45 msg/s | ETA: 12m
```

### Option 3: Detailed Table View
**Best for**: Technical users wanting full details

```
┌──────────────┬──────────────────────────────────────┐
│ Metric       │ Value                                │
├──────────────┼──────────────────────────────────────┤
│ Overall      │ 672,000 / 1,000,000 (67.2%)         │
│ Sessions     │ 134 / 200 (67.0%)                   │
│ Current Batch│ 4,000 / 5,000 (80.0%)               │
│ Phase        │ Processing                           │
│ Speed        │ 45.3 messages/second                │
│ ETA          │ 12 minutes 34 seconds               │
│ Started      │ 2 hours 15 minutes ago              │
└──────────────┴──────────────────────────────────────┘
```

### Option 4: Live Activity Feed
**Best for**: Real-time monitoring

```
📥 [12:45:23] Fetching messages... 3,240/5,000 (64.8%)
💾 [12:46:15] Processing messages... 3,500/5,000 (70.0%)
⚡ [12:46:45] Speed: 45.3 msg/s, ETA: 38 seconds
✅ [12:47:18] Session 134 complete: 5,000 messages
🔄 [12:47:20] Starting session 135/200...
```

## Implementation Recommendations

### For User Comfort:
1. **Use Option 1 (Real-Time Progress Card)** with auto-refresh every 2-3 seconds
2. Add **visual progress bars** (MUI LinearProgress) with animations
3. Show **estimated completion time** prominently
4. Use **color coding**:
   - 🟢 Green: 75-100% complete
   - 🟡 Yellow: 25-75% complete
   - 🔴 Red: 0-25% complete or errors
5. Add **"Show Details" collapse** for technical metrics

### For Performance:
1. **Debounce updates** - Update UI max once per second even if data arrives faster
2. **Aggregate multiple audit events** - Batch database queries
3. **Cache progress data** - Use Redis with 5-second TTL
4. **WebSocket connection** (optional) - Push updates instead of polling

### For Multi-Channel Support:
```
┌─────────────────────────────────────────────────────┐
│  📊 Collection Status (3 channels active)           │
├─────────────────────────────────────────────────────┤
│  ABC NEWS        ████████████████████░ 80%  4/5     │
│  Tech Channel    ██████████░░░░░░░░░ 50%  10/20    │
│  Sports Feed     ██░░░░░░░░░░░░░░░░░ 10%  1/10     │
└─────────────────────────────────────────────────────┘
```

## API Endpoint Additions Needed

### 1. Get Latest Progress
```
GET /api/user-mtproto/monitoring/progress
Response:
{
  "channels": [
    {
      "channel_id": 1002678877654,
      "channel_name": "ABC LEGACY NEWS",
      "phase": "fetching",
      "messages_current": 3240,
      "messages_total": 5000,
      "progress_percent": 64.8,
      "session_current": 134,
      "session_total": 200,
      "speed_messages_per_second": 45.3,
      "eta_seconds": 38,
      "started_at": "2025-11-10T12:30:00Z",
      "last_update": "2025-11-10T12:45:23Z"
    }
  ]
}
```

### 2. Progress History (for graphs)
```
GET /api/user-mtproto/monitoring/progress/history?channel_id=X&hours=24
Response:
{
  "data_points": [
    {"timestamp": "2025-11-10T12:00:00Z", "messages": 100000, "speed": 42.5},
    {"timestamp": "2025-11-10T12:30:00Z", "messages": 250000, "speed": 45.3},
    ...
  ]
}
```

## Database Schema (Already Supported)

Audit log table already has JSONB `metadata` column, so no schema changes needed!

```sql
SELECT
  timestamp,
  channel_id,
  metadata->'messages_current' as current,
  metadata->'messages_total' as total,
  metadata->'progress_percent' as percent,
  metadata->'session_current' as session,
  metadata->'speed_messages_per_second' as speed
FROM mtproto_audit_log
WHERE user_id = $1
  AND action = 'collection_progress_detail'
  AND timestamp > NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC
LIMIT 100;
```

## Testing Scenario

For a channel with 1,000,000 messages and limit of 5,000 per session:

1. **Session 1**: Fetch 5,000 messages (IDs 1,000,000 - 995,001)
   - Progress logged at: 500, 1000, 1500, ..., 5000
   - Processing logged at: 500, 1000, ..., 5000

2. **Session 2**: Fetch next 5,000 (IDs 995,000 - 990,001)
   - UI shows: "Session 2/200, Messages 5,000/5,000"

3. **Session 134**: User sees:
   - Overall: 670,000 / 1,000,000 (67%)
   - Session: 134 / 200
   - Current batch: 3,240 / 5,000
   - Speed: 45.3 msg/s
   - ETA: 2 hours 15 minutes

## Next Steps

1. ✅ Backend progress tracking implemented
2. ⏳ Create API endpoint `/api/user-mtproto/monitoring/progress`
3. ⏳ Add frontend component `ProgressCard.tsx`
4. ⏳ Update `MTProtoMonitoringPage.tsx` to display progress
5. ⏳ Add real-time updates (WebSocket or polling)
6. ⏳ Test with large channel (>100K messages)

## Benefits

- **User Confidence**: Users see exactly what's happening
- **Performance Visibility**: Speed metrics help identify issues
- **Planning**: ETA helps users plan when to check back
- **Debugging**: Detailed logs help diagnose collection problems
- **Multi-tenant**: Each user sees their own progress independently
