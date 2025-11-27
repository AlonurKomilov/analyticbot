# Database Storage Issue Analysis - Data Retention Problem

**Date:** November 27, 2025
**Severity:** 🚨 **CRITICAL**
**Impact:** High storage costs, slow queries, unnecessary resource usage

---

## Executive Summary

Your database has a **critical data retention problem** causing **93% of storage** (1.7 GB) to be consumed by excessive historical snapshots for a single user with only 2,770 posts.

### Problem Scale:
- **6.9 million post_metrics records** for 1 user
- **2,497 snapshots per post** (should be ~10-50 max)
- **3-6 snapshots per post per hour** (collecting every 10-20 minutes, 24/7)
- **No data retention/cleanup policy** implemented
- **33,612 MTProto audit log entries** in 24 days (also needs cleanup)

### Projected Growth:
- Current: **1.7 GB** for 21 days of data
- **1 year projection: ~30 GB** (if pattern continues)
- **Multi-user projection: 150-300 GB/year** (for 5-10 active users)

---

## Root Causes

### 1. Excessive Snapshot Frequency
**Current Behavior:**
- Collecting 3-6 snapshots per post per hour
- Running 24/7 without pause
- No intelligent scheduling (collecting at night when engagement is low)

**Evidence:**
```
Hour 08:00: 2,765 snapshots (1x per post)
Hour 07:00: 8,295 snapshots (3x per post)
Hour 06:00: 16,590 snapshots (6x per post) ← Peak collection
Hour 05:00: 8,295 snapshots (3x per post)
```

**Issue:** You're collecting data every 10-20 minutes when:
- Post metrics don't change that frequently
- Historical trends can be calculated from daily/hourly aggregates
- Real-time tracking is only needed for recent posts (<24-48 hours old)

### 2. No Data Retention Policy
**Current State:**
- ALL snapshots kept forever (oldest: Nov 6, newest: Nov 27)
- No archival to cheaper storage
- No aggregation of old data
- No cleanup jobs configured

**Evidence:**
```sql
total_snapshots: 6,918,136
older_than_30_days: 0 (all data is < 30 days old)
oldest_snapshot: 2025-11-06 (21 days ago)
```

### 3. No Data Aggregation
**Missing Strategy:**
- Raw snapshots should be aggregated after 48 hours
- Daily summaries should replace hourly data after 7 days
- Weekly summaries should replace daily data after 30 days
- Keep only critical inflection points (viral spikes, major changes)

### 4. MTProto Audit Log Bloat
**Secondary Issue:**
- 33,612 audit entries in 24 days (1,400/day)
- Tracking every `collection_progress_detail` event
- These logs should be: aggregated (progress events), rotated (30-day retention), or moved to cheaper storage

---

## Recommended Solutions

### Phase 1: Immediate Actions (Stop the bleeding)

#### A. Implement Data Retention Policy

**1. Keep Recent High-Frequency Data (Last 48 hours):**
```sql
-- These are for real-time dashboards
-- Keep all snapshots for posts < 48 hours old
DELETE FROM post_metrics
WHERE snapshot_time < NOW() - INTERVAL '48 hours'
  AND snapshot_time NOT IN (
    -- Keep one snapshot per hour for 48h-7d range
    SELECT DISTINCT ON (channel_id, msg_id, DATE_TRUNC('hour', snapshot_time))
      snapshot_time
    FROM post_metrics
    WHERE snapshot_time BETWEEN NOW() - INTERVAL '7 days' AND NOW() - INTERVAL '48 hours'
    ORDER BY channel_id, msg_id, DATE_TRUNC('hour', snapshot_time), snapshot_time DESC
  );
```

**Estimated savings:** ~5.5 million rows (~900 MB)

**2. Aggregate Older Data (7-30 days):**
```sql
-- Create daily aggregates table
CREATE TABLE IF NOT EXISTS post_metrics_daily (
    channel_id BIGINT NOT NULL,
    msg_id BIGINT NOT NULL,
    date DATE NOT NULL,
    min_views BIGINT,
    max_views BIGINT,
    avg_views NUMERIC,
    min_forwards BIGINT,
    max_forwards BIGINT,
    avg_forwards NUMERIC,
    snapshots_count INT,
    PRIMARY KEY (channel_id, msg_id, date)
);

-- Aggregate old data
INSERT INTO post_metrics_daily
SELECT
    channel_id,
    msg_id,
    DATE(snapshot_time) as date,
    MIN(views) as min_views,
    MAX(views) as max_views,
    AVG(views) as avg_views,
    MIN(forwards) as min_forwards,
    MAX(forwards) as max_forwards,
    AVG(forwards) as avg_forwards,
    COUNT(*) as snapshots_count
FROM post_metrics
WHERE snapshot_time < NOW() - INTERVAL '7 days'
GROUP BY channel_id, msg_id, DATE(snapshot_time)
ON CONFLICT (channel_id, msg_id, date) DO NOTHING;

-- Delete aggregated raw data
DELETE FROM post_metrics
WHERE snapshot_time < NOW() - INTERVAL '7 days';
```

**Estimated savings:** ~4 million rows (~650 MB)

**3. Archive Very Old Data (>30 days):**
```sql
-- Export to CSV/Parquet and delete
COPY (
  SELECT * FROM post_metrics_daily
  WHERE date < CURRENT_DATE - INTERVAL '30 days'
) TO '/backups/post_metrics_archive_$(date +%Y%m%d).csv' WITH CSV HEADER;

DELETE FROM post_metrics_daily
WHERE date < CURRENT_DATE - INTERVAL '30 days';
```

#### B. Reduce Collection Frequency

**Current Config (assumed from Celery/cron):**
```python
# apps/celery/beat_schedule.py or similar
'collect-post-metrics': {
    'task': 'collect_post_metrics',
    'schedule': crontab(minute='*/10'),  # Every 10 minutes ❌
}
```

**Recommended Config:**
```python
# Intelligent collection based on post age
'collect-post-metrics-realtime': {
    'task': 'collect_recent_post_metrics',  # Posts < 24h old
    'schedule': crontab(minute='*/30'),  # Every 30 min
    'kwargs': {'max_age_hours': 24}
},
'collect-post-metrics-daily': {
    'task': 'collect_older_post_metrics',  # Posts 1-7 days old
    'schedule': crontab(hour='*/6', minute=0),  # Every 6 hours
    'kwargs': {'min_age_hours': 24, 'max_age_days': 7}
},
'collect-post-metrics-weekly': {
    'task': 'collect_old_post_metrics',  # Posts > 7 days old
    'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Weekly
    'kwargs': {'min_age_days': 7}
}
```

**Savings:** 80-90% reduction in new data (from 200K rows/day → 20-30K rows/day)

#### C. Clean MTProto Audit Log

**Immediate Cleanup:**
```sql
-- Keep only last 30 days
DELETE FROM mtproto_audit_log
WHERE timestamp < NOW() - INTERVAL '30 days';

-- Aggregate progress_detail events (they're too verbose)
-- Keep only start/end events + errors
DELETE FROM mtproto_audit_log
WHERE action IN ('collection_progress_detail', 'collection_progress')
  AND timestamp < NOW() - INTERVAL '7 days';
```

**Estimated savings:** ~25K rows (~10 MB)

### Phase 2: Automated Maintenance (Prevent recurrence)

#### A. Create Cleanup Celery Task

```python
# apps/celery/tasks/maintenance_tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from apps.di import get_db_connection

@shared_task(name="cleanup_old_post_metrics")
def cleanup_old_post_metrics():
    """
    Cleanup old post_metrics data:
    - Delete raw snapshots older than 48 hours (keep hourly)
    - Aggregate 7-30 day data into daily summaries
    - Archive data older than 30 days
    """
    # Implementation here
    pass

@shared_task(name="cleanup_mtproto_audit_log")
def cleanup_mtproto_audit_log():
    """
    Cleanup MTProto audit log:
    - Keep last 30 days of all events
    - Delete progress_detail events older than 7 days
    """
    # Implementation here
    pass

# Add to beat schedule
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'cleanup-post-metrics-daily': {
        'task': 'cleanup_old_post_metrics',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'cleanup-audit-log-weekly': {
        'task': 'cleanup_mtproto_audit_log',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),  # Sundays
    },
}
```

#### B. Add Partitioning (Advanced)

For very large datasets, partition post_metrics by time:

```sql
-- Convert to partitioned table
CREATE TABLE post_metrics_new (
    channel_id BIGINT NOT NULL,
    msg_id BIGINT NOT NULL,
    snapshot_time TIMESTAMP WITH TIME ZONE NOT NULL,
    views BIGINT,
    forwards BIGINT,
    ...
) PARTITION BY RANGE (snapshot_time);

-- Create monthly partitions
CREATE TABLE post_metrics_2025_11 PARTITION OF post_metrics_new
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE post_metrics_2025_12 PARTITION OF post_metrics_new
    FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');

-- Migrate data
INSERT INTO post_metrics_new SELECT * FROM post_metrics;

-- Swap tables
ALTER TABLE post_metrics RENAME TO post_metrics_old;
ALTER TABLE post_metrics_new RENAME TO post_metrics;

-- Drop old partitions easily
DROP TABLE post_metrics_2025_10;  -- Much faster than DELETE
```

---

## Implementation Priority

### 🔴 CRITICAL (Do immediately):
1. **Stop collection for 7+ day old posts** (reduce frequency to weekly)
2. **Delete old post_metrics data** (keep last 48h raw, hourly for 7d, daily for 30d)
3. **Clean MTProto audit log** (keep 30 days max)

### 🟡 HIGH (This week):
4. **Create automated cleanup tasks**
5. **Implement post_metrics_daily aggregation table**
6. **Add monitoring for table sizes**

### 🟢 MEDIUM (This month):
7. **Implement table partitioning**
8. **Setup archive storage** (S3/cheaper storage for old data)
9. **Create owner dashboard** for storage monitoring

---

## Expected Results

### After Phase 1 (Immediate cleanup):
- **Current:** 1.7 GB post_metrics, 17 MB audit log
- **After:** 200-300 MB post_metrics, 5 MB audit log
- **Savings:** ~1.4 GB (~82% reduction)

### After Phase 2 (Ongoing):
- **Daily growth:** 20-30K rows (~3-5 MB/day)
- **Monthly growth:** ~150 MB/month (vs current 2.4 GB/month)
- **Annual growth:** ~1.8 GB/year (vs current 30 GB/year)
- **Cost savings:** 95% reduction in storage costs

---

## Monitoring Queries

**Add to owner dashboard:**

```sql
-- Storage by table
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Post metrics age distribution
SELECT
    CASE
        WHEN snapshot_time >= NOW() - INTERVAL '24 hours' THEN '< 24h'
        WHEN snapshot_time >= NOW() - INTERVAL '48 hours' THEN '24-48h'
        WHEN snapshot_time >= NOW() - INTERVAL '7 days' THEN '2-7d'
        WHEN snapshot_time >= NOW() - INTERVAL '30 days' THEN '7-30d'
        ELSE '> 30d'
    END as age_bucket,
    COUNT(*) as row_count,
    pg_size_pretty(COUNT(*) * 100) as estimated_size
FROM post_metrics
GROUP BY age_bucket
ORDER BY age_bucket;

-- Collection rate (last 24h)
SELECT
    DATE_TRUNC('hour', snapshot_time) as hour,
    COUNT(*) as snapshots,
    COUNT(DISTINCT (channel_id, msg_id)) as unique_posts,
    ROUND(COUNT(*)::numeric / COUNT(DISTINCT (channel_id, msg_id)), 1) as avg_per_post
FROM post_metrics
WHERE snapshot_time >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', snapshot_time)
ORDER BY hour DESC;
```

---

## Files to Modify

1. **apps/celery/tasks/maintenance_tasks.py** - Add cleanup tasks
2. **apps/celery/beat_schedule.py** - Reduce collection frequency
3. **infra/db/alembic/versions/0038_add_post_metrics_retention.py** - New migration
4. **apps/api/routers/owner_router.py** - Add storage monitoring endpoint
5. **docs/DATABASE_RETENTION_POLICY.md** - Document retention policy

---

## Next Steps

1. **Review and approve** this retention policy
2. **Test cleanup queries** on a staging database first
3. **Schedule maintenance window** for large DELETE operations
4. **Implement automated cleanup tasks**
5. **Monitor** storage trends for 1 week post-implementation

**Need help implementing these changes?** I can create the:
- Cleanup SQL scripts
- Celery maintenance tasks
- Owner dashboard monitoring
- Migration files
