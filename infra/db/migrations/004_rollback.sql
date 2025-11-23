-- Rollback Migration: 004_add_post_content_type_detection.sql
-- Purpose: Remove content type detection columns if needed
-- Date: 2025-11-21
-- CAUTION: This will remove data. Only use if absolutely necessary!

-- ============================================================================
-- ROLLBACK STEPS (Execute in order)
-- ============================================================================

-- Step 1: Drop indexes first
DROP INDEX IF EXISTS idx_posts_content_type;
DROP INDEX IF EXISTS idx_posts_date_content;

-- Step 2: Drop columns
ALTER TABLE posts DROP COLUMN IF EXISTS has_video;
ALTER TABLE posts DROP COLUMN IF EXISTS has_media;

-- Step 3: Verify rollback
\d posts;

SELECT 'Rollback completed successfully' as status;
