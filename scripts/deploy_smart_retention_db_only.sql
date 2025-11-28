-- Smart Data Retention System - Direct Database Deployment
-- This script deploys the system without needing the application containers

-- Step 1: Create the post_metrics_checks table
CREATE TABLE IF NOT EXISTS post_metrics_checks (
    channel_id BIGINT NOT NULL,
    msg_id BIGINT NOT NULL,
    last_checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_changed_at TIMESTAMP WITH TIME ZONE,
    check_count INTEGER NOT NULL DEFAULT 0,
    save_count INTEGER NOT NULL DEFAULT 0,
    stable_since TIMESTAMP WITH TIME ZONE,
    post_age_hours NUMERIC(10, 2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (channel_id, msg_id),
    FOREIGN KEY (channel_id, msg_id) 
        REFERENCES posts(channel_id, msg_id) 
        ON DELETE CASCADE
);

COMMENT ON TABLE post_metrics_checks IS 'Tracks post metric collection history for smart change detection';
COMMENT ON COLUMN post_metrics_checks.last_checked_at IS 'When we last checked this post (even if metrics did not change)';
COMMENT ON COLUMN post_metrics_checks.last_changed_at IS 'When metrics last changed significantly';
COMMENT ON COLUMN post_metrics_checks.check_count IS 'Total number of times we checked this post';
COMMENT ON COLUMN post_metrics_checks.save_count IS 'Total number of times we saved a snapshot (changes detected)';
COMMENT ON COLUMN post_metrics_checks.stable_since IS 'When did metrics become stable (stop changing)';
COMMENT ON COLUMN post_metrics_checks.post_age_hours IS 'Cached post age in hours for query optimization';

-- Step 2: Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_checks_last_checked 
    ON post_metrics_checks(last_checked_at);

CREATE INDEX IF NOT EXISTS idx_checks_stable_since 
    ON post_metrics_checks(stable_since) 
    WHERE stable_since IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_checks_post_age 
    ON post_metrics_checks(post_age_hours);

CREATE INDEX IF NOT EXISTS idx_checks_efficiency 
    ON post_metrics_checks(check_count, save_count);

-- Step 3: Display current storage status
\echo '=== BEFORE CLEANUP ==='
SELECT 
    'post_metrics' as table_name,
    pg_size_pretty(pg_total_relation_size('post_metrics')) as total_size,
    pg_size_pretty(pg_relation_size('post_metrics')) as table_size,
    pg_size_pretty(pg_total_relation_size('post_metrics') - pg_relation_size('post_metrics')) as indexes_size,
    COUNT(*) as row_count,
    COUNT(DISTINCT (channel_id, msg_id)) as unique_posts,
    ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT (channel_id, msg_id)), 0), 1) as avg_snapshots_per_post
FROM post_metrics;

\echo ''
\echo '=== ANALYZING DUPLICATES ==='
-- Count how many duplicate snapshots exist
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT (channel_id, msg_id, views, forwards, COALESCE(reactions_count, 0), COALESCE(replies_count, 0))) as unique_metric_combinations,
    COUNT(*) - COUNT(DISTINCT (channel_id, msg_id, views, forwards, COALESCE(reactions_count, 0), COALESCE(replies_count, 0))) as duplicate_records,
    ROUND((COUNT(*) - COUNT(DISTINCT (channel_id, msg_id, views, forwards, COALESCE(reactions_count, 0), COALESCE(replies_count, 0))))::numeric / COUNT(*) * 100, 1) as duplicate_pct
FROM post_metrics;

\echo ''
\echo 'Table created successfully! ✅'
\echo 'Ready for cleanup. Run the cleanup script next.'
