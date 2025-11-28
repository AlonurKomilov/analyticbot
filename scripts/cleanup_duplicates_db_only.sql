-- Smart Data Retention - Cleanup Duplicate Snapshots
-- This script removes duplicate post_metrics records, keeping only unique snapshots

\echo '🧹 Starting duplicate cleanup...'
\echo ''

-- Step 1: Create temporary table with unique snapshots to keep
CREATE TEMP TABLE snapshots_to_keep AS
SELECT DISTINCT ON (channel_id, msg_id, views, forwards, COALESCE(reactions_count, 0), COALESCE(replies_count, 0))
    channel_id,
    msg_id,
    snapshot_time,
    views,
    forwards,
    reactions_count,
    replies_count
FROM post_metrics
ORDER BY channel_id, msg_id, views, forwards, COALESCE(reactions_count, 0), COALESCE(replies_count, 0), snapshot_time DESC;

\echo 'Created list of snapshots to keep...'

-- Step 2: Count what will be deleted (dry run info)
SELECT 
    COUNT(*) as total_before,
    (SELECT COUNT(*) FROM snapshots_to_keep) as will_keep,
    COUNT(*) - (SELECT COUNT(*) FROM snapshots_to_keep) as will_delete,
    ROUND((COUNT(*) - (SELECT COUNT(*) FROM snapshots_to_keep))::numeric / COUNT(*) * 100, 1) as delete_pct
FROM post_metrics;

\echo ''
\echo '⚠️  WARNING: This will delete duplicate records!'
\echo 'Press Ctrl+C to cancel, or press Enter to continue...'
\prompt 'Continue? ' confirm

-- Step 3: Delete duplicates in batches
DO $$
DECLARE
    deleted_count INTEGER := 0;
    batch_size INTEGER := 10000;
    total_deleted INTEGER := 0;
BEGIN
    RAISE NOTICE 'Starting deletion in batches of %...', batch_size;
    
    LOOP
        -- Delete records that are NOT in the keep list
        WITH to_delete AS (
            SELECT channel_id, msg_id, snapshot_time
            FROM post_metrics
            WHERE (channel_id, msg_id, snapshot_time) NOT IN (
                SELECT channel_id, msg_id, snapshot_time
                FROM snapshots_to_keep
            )
            LIMIT batch_size
        )
        DELETE FROM post_metrics
        WHERE (channel_id, msg_id, snapshot_time) IN (
            SELECT channel_id, msg_id, snapshot_time FROM to_delete
        );
        
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        total_deleted := total_deleted + deleted_count;
        
        RAISE NOTICE 'Deleted % records (total: %)', deleted_count, total_deleted;
        
        -- Exit if no more records to delete
        EXIT WHEN deleted_count = 0;
        
        -- Commit after each batch
        COMMIT;
    END LOOP;
    
    RAISE NOTICE 'Cleanup complete! Total deleted: %', total_deleted;
END $$;

-- Step 4: Vacuum to reclaim space
\echo ''
\echo '🧹 Running VACUUM to reclaim disk space...'
VACUUM FULL ANALYZE post_metrics;

-- Step 5: Show final results
\echo ''
\echo '=== AFTER CLEANUP ==='
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
\echo '✅ Cleanup complete!'
\echo 'Storage has been significantly reduced.'
