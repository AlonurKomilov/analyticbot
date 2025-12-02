-- Migration 006: Add telegram_created_at field to channels
-- This stores the actual Telegram channel creation date (from Telegram API)
-- Separate from created_at which stores when the channel was added to our system

-- Add the new column
ALTER TABLE channels 
ADD COLUMN IF NOT EXISTS telegram_created_at TIMESTAMP WITH TIME ZONE;

-- Add comment to clarify the difference
COMMENT ON COLUMN channels.telegram_created_at IS 'Actual channel creation date from Telegram API';
COMMENT ON COLUMN channels.created_at IS 'Date when channel was added to analytics system';

-- Create index for potential queries by Telegram creation date
CREATE INDEX IF NOT EXISTS idx_channels_telegram_created_at 
ON channels (telegram_created_at) 
WHERE telegram_created_at IS NOT NULL;
