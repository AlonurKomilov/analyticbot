-- Migration 005 Rollback: Remove Performance Optimization Indexes
-- Phase 6: Rollback script to remove all indexes from migration 005
-- Date: 2025-11-21

BEGIN;

-- Drop all indexes created in migration 005
DROP INDEX IF EXISTS idx_posts_channel_date_active;
DROP INDEX IF EXISTS idx_posts_channel_date_content_type;
DROP INDEX IF EXISTS idx_posts_videos_only;
DROP INDEX IF EXISTS idx_posts_images_only;
DROP INDEX IF EXISTS idx_post_metrics_covering;
DROP INDEX IF EXISTS idx_posts_hour_extraction;
DROP INDEX IF EXISTS idx_posts_dow_extraction;
DROP INDEX IF EXISTS idx_post_metrics_channel_msg;

-- Note: Original indexes from migration 004 remain intact:
-- - idx_posts_content_type
-- - idx_posts_date_content

COMMIT;

-- Verify rollback
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE tablename IN ('posts', 'post_metrics')
ORDER BY tablename, indexname;
