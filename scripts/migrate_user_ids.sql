-- Migration Script: Migrate users from id=telegram_id to 9-digit sequence IDs
-- This script assigns new 9-digit IDs to existing Telegram users
-- and updates all foreign key references

-- ============================================
-- SAFETY: Run in transaction
-- ============================================
BEGIN;

-- ============================================
-- Step 1: Create mapping table for old_id -> new_id
-- ============================================
CREATE TEMP TABLE user_id_migration (
    old_id BIGINT PRIMARY KEY,
    new_id BIGINT NOT NULL,
    telegram_id BIGINT NOT NULL,
    username VARCHAR(255)
);

-- ============================================
-- Step 2: Generate new IDs for users where id = telegram_id
-- ============================================
INSERT INTO user_id_migration (old_id, new_id, telegram_id, username)
SELECT
    id as old_id,
    nextval('users_id_seq') as new_id,
    telegram_id,
    username
FROM users
WHERE telegram_id IS NOT NULL AND id = telegram_id
ORDER BY created_at;

-- Show the mapping
SELECT 'User ID Migration Map:' as info;
SELECT old_id, new_id, telegram_id, username FROM user_id_migration ORDER BY new_id;

-- ============================================
-- Step 3: Disable foreign key checks temporarily
-- ============================================
SET session_replication_role = 'replica';

-- ============================================
-- Step 4: Update foreign keys in all related tables
-- ============================================

-- Update channels
UPDATE channels c
SET user_id = m.new_id
FROM user_id_migration m
WHERE c.user_id = m.old_id;

-- Update channel_mtproto_settings
UPDATE channel_mtproto_settings cms
SET user_id = m.new_id
FROM user_id_migration m
WHERE cms.user_id = m.old_id;

-- Update user_storage_channels
UPDATE user_storage_channels usc
SET user_id = m.new_id
FROM user_id_migration m
WHERE usc.user_id = m.old_id;

-- Update subscriptions
UPDATE subscriptions s
SET user_id = m.new_id
FROM user_id_migration m
WHERE s.user_id = m.old_id;

-- Update payments
UPDATE payments p
SET user_id = m.new_id
FROM user_id_migration m
WHERE p.user_id = m.old_id;

-- Update payment_methods
UPDATE payment_methods pm
SET user_id = m.new_id
FROM user_id_migration m
WHERE pm.user_id = m.old_id;

-- Update scheduled_posts
UPDATE scheduled_posts sp
SET user_id = m.new_id
FROM user_id_migration m
WHERE sp.user_id = m.old_id;

-- Update telegram_media
UPDATE telegram_media tm
SET user_id = m.new_id
FROM user_id_migration m
WHERE tm.user_id = m.old_id;

-- Update mtproto_audit_log
UPDATE mtproto_audit_log mal
SET user_id = m.new_id
FROM user_id_migration m
WHERE mal.user_id = m.old_id;

-- Update admin_bot_actions
UPDATE admin_bot_actions aba
SET target_user_id = m.new_id
FROM user_id_migration m
WHERE aba.target_user_id = m.old_id;

-- ============================================
-- Step 5: Update users table itself
-- ============================================
UPDATE users u
SET id = m.new_id
FROM user_id_migration m
WHERE u.id = m.old_id;

-- ============================================
-- Step 6: Re-enable foreign key checks
-- ============================================
SET session_replication_role = 'origin';

-- ============================================
-- Step 7: Verify migration
-- ============================================
SELECT 'Migration Complete! Verification:' as info;

SELECT id, telegram_id, username,
       CASE WHEN id = telegram_id THEN 'SAME (ERROR!)' ELSE 'DIFFERENT (OK)' END as status
FROM users
WHERE telegram_id IS NOT NULL
ORDER BY id;

-- Show sequence current value
SELECT 'Current sequence value:' as info, last_value FROM users_id_seq;

COMMIT;

-- ============================================
-- Summary
-- ============================================
SELECT 'Migration completed successfully!' as result;
