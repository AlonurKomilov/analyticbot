-- Migration: Add User AI Tables
-- Date: 2025-12-21
-- Revision: 0055

-- =========================================================================
-- 1. user_ai_config - Per-user AI configuration
-- =========================================================================
CREATE TABLE user_ai_config (
    user_id BIGINT PRIMARY KEY,
    tier VARCHAR(20) NOT NULL DEFAULT 'free',
    enabled BOOLEAN NOT NULL DEFAULT true,
    settings JSONB,
    preferred_model VARCHAR(50),
    temperature REAL NOT NULL DEFAULT 0.7,
    enabled_features JSONB,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    response_style VARCHAR(20) NOT NULL DEFAULT 'professional',
    auto_insights_enabled BOOLEAN NOT NULL DEFAULT false,
    auto_insights_frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
    data_retention_days INTEGER NOT NULL DEFAULT 30,
    anonymize_data BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_user_ai_config_enabled ON user_ai_config(enabled);
CREATE INDEX ix_user_ai_config_tier ON user_ai_config(tier);

-- =========================================================================
-- 2. user_ai_usage - Daily usage tracking
-- =========================================================================
CREATE TABLE user_ai_usage (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    usage_date DATE NOT NULL,
    requests_count INTEGER NOT NULL DEFAULT 0,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    features_used JSONB,
    estimated_cost REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, usage_date)
);

CREATE INDEX ix_user_ai_usage_date ON user_ai_usage(usage_date);
CREATE INDEX ix_user_ai_usage_user_date ON user_ai_usage(user_id, usage_date);
CREATE INDEX ix_user_ai_usage_user_id ON user_ai_usage(user_id);

-- =========================================================================
-- 3. user_ai_hourly_usage - Hourly usage for rate limiting
-- =========================================================================
CREATE TABLE user_ai_hourly_usage (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    hour_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    requests_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, hour_timestamp)
);

CREATE INDEX ix_user_ai_hourly_timestamp ON user_ai_hourly_usage(hour_timestamp);
CREATE INDEX ix_user_ai_hourly_user_id ON user_ai_hourly_usage(user_id);

-- =========================================================================
-- 4. user_ai_services - User's active AI services
-- =========================================================================
CREATE TABLE user_ai_services (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    service_key VARCHAR(100) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT true,
    activated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    config JSONB,
    usage_count INTEGER NOT NULL DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    subscription_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, service_key)
);

CREATE INDEX ix_user_ai_service_enabled ON user_ai_services(enabled);
CREATE INDEX ix_user_ai_service_expires ON user_ai_services(expires_at);
CREATE INDEX ix_user_ai_service_key ON user_ai_services(service_key);
CREATE INDEX ix_user_ai_service_user_id ON user_ai_services(user_id);

-- =========================================================================
-- 5. ai_request_log - Detailed request logging
-- =========================================================================
CREATE TABLE ai_request_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    request_type VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    parameters JSONB,
    success BOOLEAN NOT NULL,
    status_code INTEGER NOT NULL,
    error_message TEXT,
    model_used VARCHAR(50),
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0,
    response_time_ms INTEGER NOT NULL,
    estimated_cost REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_ai_request_log_created_at ON ai_request_log(created_at);
CREATE INDEX ix_ai_request_log_success ON ai_request_log(success);
CREATE INDEX ix_ai_request_log_type ON ai_request_log(request_type);
CREATE INDEX ix_ai_request_log_user_id ON ai_request_log(user_id);

-- =========================================================================
-- Update alembic version
-- =========================================================================
UPDATE alembic_version SET version_num = '0055';
