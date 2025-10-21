-- Migration: Alert System Tables
-- Date: 2025-10-20
-- Description: Create tables for alert subscriptions and delivery tracking

-- Alert subscriptions table
CREATE TABLE IF NOT EXISTS alert_subscriptions (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    kind VARCHAR(50) NOT NULL,  -- 'spike', 'quiet', 'growth'
    threshold NUMERIC(10, 2),
    window_hours INTEGER NOT NULL DEFAULT 24,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for performance
    CONSTRAINT unique_subscription UNIQUE (chat_id, channel_id, kind)
);

CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_chat_id ON alert_subscriptions(chat_id);
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_channel_id ON alert_subscriptions(channel_id);
CREATE INDEX IF NOT EXISTS idx_alert_subscriptions_enabled ON alert_subscriptions(enabled) WHERE enabled = TRUE;

-- Alert sent tracking table (for deduplication)
CREATE TABLE IF NOT EXISTS alerts_sent (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    kind VARCHAR(50) NOT NULL,  -- 'spike', 'quiet', 'growth'
    key VARCHAR(255) NOT NULL,  -- Unique identifier for this specific alert instance
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Prevent duplicate alert sends
    CONSTRAINT unique_alert_sent UNIQUE (chat_id, channel_id, kind, key)
);

CREATE INDEX IF NOT EXISTS idx_alerts_sent_chat_channel ON alerts_sent(chat_id, channel_id);
CREATE INDEX IF NOT EXISTS idx_alerts_sent_sent_at ON alerts_sent(sent_at);
CREATE INDEX IF NOT EXISTS idx_alerts_sent_cleanup ON alerts_sent(sent_at) WHERE sent_at < NOW() - INTERVAL '7 days';

-- Alert delivery log (for retry tracking and monitoring)
CREATE TABLE IF NOT EXISTS alert_delivery_log (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    kind VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    delivery_status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'sent', 'failed', 'retry'
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_delivery_status ON alert_delivery_log(delivery_status);
CREATE INDEX IF NOT EXISTS idx_alert_delivery_pending ON alert_delivery_log(delivery_status, attempted_at)
    WHERE delivery_status IN ('pending', 'retry');
CREATE INDEX IF NOT EXISTS idx_alert_delivery_chat_id ON alert_delivery_log(chat_id);

-- Comments for documentation
COMMENT ON TABLE alert_subscriptions IS 'User subscriptions to channel alerts';
COMMENT ON TABLE alerts_sent IS 'Tracking table to prevent duplicate alert sends';
COMMENT ON TABLE alert_delivery_log IS 'Log of alert delivery attempts for monitoring and retry logic';

COMMENT ON COLUMN alert_subscriptions.kind IS 'Alert type: spike (unusual high), quiet (unusual low), growth (milestones)';
COMMENT ON COLUMN alert_subscriptions.threshold IS 'Optional custom threshold for alert triggering';
COMMENT ON COLUMN alert_subscriptions.window_hours IS 'Time window for alert evaluation';

COMMENT ON COLUMN alerts_sent.key IS 'Unique key for alert instance (e.g., "spike_2025-10-20_1000")';

COMMENT ON COLUMN alert_delivery_log.delivery_status IS 'Status: pending, sent, failed, retry';
COMMENT ON COLUMN alert_delivery_log.retry_count IS 'Number of delivery retry attempts';
