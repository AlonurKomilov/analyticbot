-- Migration: Add user_ai_providers for multi-provider AI support
-- Enables users to add their own API keys for OpenAI, Claude, Gemini, Grok, etc.

BEGIN;

-- Create user_ai_providers table
CREATE TABLE IF NOT EXISTS user_ai_providers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_default BOOLEAN NOT NULL DEFAULT false,
    model_preference VARCHAR(100),
    config JSONB,
    monthly_budget_usd NUMERIC(10,2),
    current_month_spent_usd NUMERIC(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_provider UNIQUE (user_id, provider_name)
);

-- Create indices
CREATE INDEX IF NOT EXISTS ix_user_ai_providers_user_id ON user_ai_providers(user_id);
CREATE INDEX IF NOT EXISTS ix_user_ai_providers_active ON user_ai_providers(user_id, is_active);
CREATE INDEX IF NOT EXISTS ix_user_ai_providers_default ON user_ai_providers(user_id, is_default);

-- Create spending tracking table
CREATE TABLE IF NOT EXISTS user_ai_spending (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_name VARCHAR(50) NOT NULL,
    month DATE NOT NULL,
    total_cost_usd NUMERIC(10,2) NOT NULL DEFAULT 0,
    request_count INTEGER NOT NULL DEFAULT 0,
    tokens_used BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_user_provider_month UNIQUE (user_id, provider_name, month)
);

CREATE INDEX IF NOT EXISTS ix_user_ai_spending_user_id ON user_ai_spending(user_id);
CREATE INDEX IF NOT EXISTS ix_user_ai_spending_month ON user_ai_spending(month);

-- Add default_provider to user_ai_config
ALTER TABLE user_ai_config 
ADD COLUMN IF NOT EXISTS default_provider VARCHAR(50) NOT NULL DEFAULT 'system';

COMMENT ON COLUMN user_ai_config.default_provider IS 'system = use platform keys, or provider name for user keys';
COMMENT ON TABLE user_ai_providers IS 'Stores encrypted API keys for multiple AI providers per user';
COMMENT ON TABLE user_ai_spending IS 'Tracks spending per provider for budget limits';

COMMIT;

-- Verify tables created
\dt user_ai_providers
\dt user_ai_spending
SELECT 'Migration 0056 completed successfully!' as result;
