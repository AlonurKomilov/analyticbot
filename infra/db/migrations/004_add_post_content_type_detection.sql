-- Migration: 004_add_post_content_type_detection.sql
-- Purpose: Add content type detection columns for advanced recommendations
-- Date: 2025-11-21
-- Author: Analytics Bot System

-- ============================================================================
-- PHASE 1: Add Content Type Detection Columns
-- ============================================================================

-- Add columns for content type detection
ALTER TABLE posts
  ADD COLUMN IF NOT EXISTS has_video BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS has_media BOOLEAN DEFAULT FALSE;

-- Add comment for documentation
COMMENT ON COLUMN posts.has_video IS 'Indicates if post contains video content';
COMMENT ON COLUMN posts.has_media IS 'Indicates if post contains image/photo media';

-- ============================================================================
-- PHASE 2: Backfill Existing Data (Optional - can be run separately)
-- ============================================================================

-- Note: This backfill is basic and may need refinement based on actual data
-- Recommend running analysis first to determine accurate detection patterns

-- Detect video posts (conservative approach - only update if clearly has video)
-- You may need to adjust based on your actual Telegram message format
UPDATE posts SET
  has_video = TRUE
WHERE
  is_deleted = FALSE
  AND has_video = FALSE
  AND (
    text ILIKE '%video%'
    OR text ILIKE '%mp4%'
    OR text ILIKE '%webm%'
    OR text ILIKE '%mov%'
  );

-- Detect media/photo posts (conservative approach)
UPDATE posts SET
  has_media = TRUE
WHERE
  is_deleted = FALSE
  AND has_media = FALSE
  AND has_video = FALSE  -- Don't mark videos as media
  AND (
    text ILIKE '%photo%'
    OR text ILIKE '%image%'
    OR text ILIKE '%jpg%'
    OR text ILIKE '%png%'
    OR text ILIKE '%gif%'
  );

-- ============================================================================
-- PHASE 3: Create Performance Indexes
-- ============================================================================

-- Index for content type filtering (improves recommendation query performance)
CREATE INDEX IF NOT EXISTS idx_posts_content_type
ON posts(channel_id, has_video, has_media)
WHERE is_deleted = FALSE;

-- Index for time-based content analysis
CREATE INDEX IF NOT EXISTS idx_posts_date_content
ON posts(channel_id, date DESC, has_video, has_media)
WHERE is_deleted = FALSE;

-- ============================================================================
-- PHASE 4: Verify Migration
-- ============================================================================

-- Show updated schema
\d posts;

-- Show sample of detected content types
SELECT
  channel_id,
  COUNT(*) as total_posts,
  SUM(CASE WHEN has_video THEN 1 ELSE 0 END) as video_posts,
  SUM(CASE WHEN has_media THEN 1 ELSE 0 END) as media_posts,
  SUM(CASE WHEN NOT has_video AND NOT has_media THEN 1 ELSE 0 END) as text_posts
FROM posts
WHERE is_deleted = FALSE
GROUP BY channel_id
ORDER BY total_posts DESC
LIMIT 10;

-- Show performance of new indexes
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan as times_used,
  pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'posts'
  AND indexname LIKE 'idx_posts_content%'
ORDER BY idx_scan DESC;

-- ============================================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- ============================================================================

-- To rollback this migration, run:
-- DROP INDEX IF EXISTS idx_posts_content_type;
-- DROP INDEX IF EXISTS idx_posts_date_content;
-- ALTER TABLE posts DROP COLUMN IF EXISTS has_video;
-- ALTER TABLE posts DROP COLUMN IF EXISTS has_media;
