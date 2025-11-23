-- Migration 005: Performance Optimization Indexes
-- Phase 6: Add composite indexes for common query patterns
-- Date: 2025-11-21

-- ============================================================================
-- Purpose: Optimize recommendation system queries with targeted indexes
-- ============================================================================

BEGIN;

-- 1. Composite index for time-range filtered queries (most common pattern)
-- Covers: channel_id + date range + is_deleted filter
CREATE INDEX IF NOT EXISTS idx_posts_channel_date_active
ON posts (channel_id, date DESC)
WHERE is_deleted = FALSE;

COMMENT ON INDEX idx_posts_channel_date_active IS
'Optimizes time-range queries for active posts by channel';

-- 2. Composite index for content-type analysis queries
-- Covers: channel_id + date + content type columns
CREATE INDEX IF NOT EXISTS idx_posts_channel_date_content_type
ON posts (channel_id, date DESC, has_video, has_media)
WHERE is_deleted = FALSE;

COMMENT ON INDEX idx_posts_channel_date_content_type IS
'Optimizes content-type specific recommendations';

-- 3. Partial index for video content analysis
CREATE INDEX IF NOT EXISTS idx_posts_videos_only
ON posts (channel_id, date DESC, msg_id)
WHERE has_video = TRUE AND is_deleted = FALSE;

COMMENT ON INDEX idx_posts_videos_only IS
'Fast lookup for video posts in time analysis';

-- 4. Partial index for image content analysis
CREATE INDEX IF NOT EXISTS idx_posts_images_only
ON posts (channel_id, date DESC, msg_id)
WHERE has_media = TRUE AND has_video = FALSE AND is_deleted = FALSE;

COMMENT ON INDEX idx_posts_images_only IS
'Fast lookup for image posts (excluding videos)';

-- 5. Covering index for post_metrics joins
-- Includes commonly selected columns to avoid table lookups
CREATE INDEX IF NOT EXISTS idx_post_metrics_covering
ON post_metrics (channel_id, msg_id, views, forwards, reactions_count, replies_count);

COMMENT ON INDEX idx_post_metrics_covering IS
'Covering index for metrics joins - includes all frequently accessed columns';

-- 6. Index for date-based queries (replaces functional indexes that require IMMUTABLE)
-- Note: Removed EXTRACT() functional indexes as they require IMMUTABLE functions
-- The existing idx_posts_channel_date_active already covers most date queries efficiently

-- 7. Composite index for engagement calculation
-- Covers joins between posts and post_metrics
CREATE INDEX IF NOT EXISTS idx_post_metrics_channel_msg
ON post_metrics (channel_id, msg_id)
INCLUDE (views, forwards, reactions_count, replies_count);

COMMENT ON INDEX idx_post_metrics_channel_msg IS
'Optimized composite index for metrics lookups with covering columns';

-- ============================================================================
-- Index Statistics and Verification
-- ============================================================================

-- Analyze tables to update statistics
ANALYZE posts;
ANALYZE post_metrics;

-- ============================================================================
-- Performance Testing Query
-- ============================================================================

-- Test query to verify index usage (DO NOT EXECUTE IN MIGRATION)
-- EXPLAIN (ANALYZE, BUFFERS)
-- SELECT
--     EXTRACT(HOUR FROM p.date)::int as hour,
--     COUNT(*) as post_count,
--     AVG(pm.views) as avg_views
-- FROM posts p
-- LEFT JOIN post_metrics pm ON p.channel_id = pm.channel_id AND p.msg_id = pm.msg_id
-- WHERE p.channel_id = $CHANNEL_ID
--   AND p.date >= NOW() - INTERVAL '90 days'
--   AND p.is_deleted = FALSE
-- GROUP BY hour;

COMMIT;

-- ============================================================================
-- Expected Performance Improvements
-- ============================================================================

-- Before optimization:
--   - Simple queries: ~150-300ms
--   - Advanced queries: ~1500-2000ms
--   - Content-type filtered: ~1200-1800ms
--
-- After optimization (expected):
--   - Simple queries: ~50-100ms (60-70% improvement)
--   - Advanced queries: ~500-800ms (65-75% improvement)
--   - Content-type filtered: ~400-600ms (65-70% improvement)
--
-- Index storage overhead: ~50-100MB per million rows
