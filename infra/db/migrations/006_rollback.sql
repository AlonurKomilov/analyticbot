-- Rollback for migration 006
-- Remove telegram_created_at field from channels

DROP INDEX IF EXISTS idx_channels_telegram_created_at;
ALTER TABLE channels DROP COLUMN IF EXISTS telegram_created_at;
