-- Channel Management Fix - Manual Migration Script
-- Run this if Alembic is not available
-- Date: October 28, 2025

-- ===========================================================================
-- Step 1: Add description column to channels table
-- ===========================================================================

ALTER TABLE channels ADD COLUMN IF NOT EXISTS description TEXT;

COMMENT ON COLUMN channels.description IS
'Channel description from Telegram API or user-provided text';

-- ===========================================================================
-- Step 2: Verify column was added
-- ===========================================================================

SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'channels'
ORDER BY ordinal_position;

-- Expected output should include:
-- column_name  | data_type              | is_nullable
-- -------------+------------------------+-------------
-- id           | bigint                 | NO
-- user_id      | bigint                 | NO
-- title        | character varying      | YES
-- username     | character varying      | YES
-- description  | text                   | YES  <-- NEW!
-- created_at   | timestamp without...   | YES

-- ===========================================================================
-- Step 3: Mark migration as applied in Alembic (if using Alembic tracking)
-- ===========================================================================

-- Check if alembic_version table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_name = 'alembic_version'
);

-- If exists, insert migration version
INSERT INTO alembic_version (version_num)
VALUES ('0020_add_channel_description')
ON CONFLICT (version_num) DO NOTHING;

-- ===========================================================================
-- Step 4: Test query to ensure description works
-- ===========================================================================

-- Sample insert (replace with real data)
INSERT INTO channels (id, user_id, title, username, description, created_at)
VALUES (
    9999999999,  -- Temporary test ID
    1,           -- Your user ID
    'Test Channel',
    '@test_channel',
    'This is a test description',
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- Query to verify
SELECT id, title, username, description, created_at
FROM channels
WHERE id = 9999999999;

-- Clean up test data
DELETE FROM channels WHERE id = 9999999999;

-- ===========================================================================
-- Done! 🎉
-- ===========================================================================

-- Next steps:
-- 1. Restart your backend API server
-- 2. Clear frontend cache (Ctrl+Shift+R)
-- 3. Test adding a channel through the UI
