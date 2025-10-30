-- Migration: Multi-Tenant User Bot Credentials
-- Date: 2025-10-27
-- Description: Create tables for user bot credentials and admin actions

-- User bot credentials table
CREATE TABLE IF NOT EXISTS user_bot_credentials (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,

    -- Telegram Bot credentials (encrypted)
    bot_token VARCHAR(255) NOT NULL,
    bot_username VARCHAR(255),
    bot_id BIGINT,

    -- MTProto credentials (encrypted)
    telegram_api_id INTEGER NOT NULL,
    telegram_api_hash VARCHAR(255) NOT NULL,
    telegram_phone VARCHAR(20),
    session_string TEXT,

    -- Status & Control
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    suspension_reason TEXT,

    -- Rate limiting
    rate_limit_rps NUMERIC(10, 2) NOT NULL DEFAULT 1.0,
    max_concurrent_requests INTEGER NOT NULL DEFAULT 3,

    -- Usage tracking
    total_requests BIGINT NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT one_bot_per_user UNIQUE (user_id),
    CONSTRAINT unique_bot_token UNIQUE (bot_token),
    CONSTRAINT unique_bot_username UNIQUE (bot_username)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bot_credentials_user_id ON user_bot_credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_bot_credentials_status ON user_bot_credentials(status);
CREATE INDEX IF NOT EXISTS idx_bot_credentials_last_used ON user_bot_credentials(last_used_at);

-- Admin bot actions log table
CREATE TABLE IF NOT EXISTS admin_bot_actions (
    id SERIAL PRIMARY KEY,
    admin_user_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    action VARCHAR(100) NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign key to users table
    CONSTRAINT fk_admin_bot_actions_user FOREIGN KEY (target_user_id)
        REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for admin actions
CREATE INDEX IF NOT EXISTS idx_admin_actions_admin_id ON admin_bot_actions(admin_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_target_user ON admin_bot_actions(target_user_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_timestamp ON admin_bot_actions(timestamp);
CREATE INDEX IF NOT EXISTS idx_admin_actions_action ON admin_bot_actions(action);

-- Comments for documentation
COMMENT ON TABLE user_bot_credentials IS 'Stores encrypted bot credentials for multi-tenant bot system';
COMMENT ON TABLE admin_bot_actions IS 'Audit log for all admin actions on user bots';

COMMENT ON COLUMN user_bot_credentials.bot_token IS 'Encrypted Telegram bot token';
COMMENT ON COLUMN user_bot_credentials.telegram_api_hash IS 'Encrypted Telegram API hash for MTProto';
COMMENT ON COLUMN user_bot_credentials.status IS 'Bot status: pending, active, suspended, rate_limited, error';
COMMENT ON COLUMN user_bot_credentials.rate_limit_rps IS 'Maximum requests per second for this bot';
COMMENT ON COLUMN user_bot_credentials.suspension_reason IS 'Reason for suspension (if status=suspended)';
