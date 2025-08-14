-- postgres-init/init.sql
-- Create base schema for AnalyticBot
-- This file runs automatically on a fresh Postgres volume via docker-entrypoint-initdb.d

SET client_min_messages = WARNING;
SET TIME ZONE 'UTC';

-- 1) Plans
CREATE TABLE IF NOT EXISTS plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    -- Some code (PlanRepository) queries "plan_name", so we keep a mirror column for now
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    max_channels INTEGER NOT NULL DEFAULT 1,
    max_posts_per_month INTEGER NOT NULL DEFAULT 30
);

-- 2) Users
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,                    -- Telegram user id
    username VARCHAR(255),
    plan_id INTEGER REFERENCES plans(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3) Channels
-- We treat Telegram channel id as the primary key `id`
CREATE TABLE IF NOT EXISTS channels (
    id BIGINT PRIMARY KEY,                    -- Telegram channel id
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- helpful index for lookups
CREATE INDEX IF NOT EXISTS idx_channels_user_id ON channels(user_id);

-- 4) Scheduled posts
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    post_text TEXT NOT NULL,
    schedule_time TIMESTAMPTZ NOT NULL,
    media_id TEXT,
    media_type TEXT,
    inline_buttons JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending' | 'sent' | 'error'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_scheduled_posts_status CHECK (status IN ('pending', 'sent', 'error'))
);

CREATE INDEX IF NOT EXISTS idx_sched_user_id ON scheduled_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_sched_channel_id ON scheduled_posts(channel_id);
CREATE INDEX IF NOT EXISTS idx_sched_status_time ON scheduled_posts(status, schedule_time);
CREATE INDEX IF NOT EXISTS idx_sched_created_at ON scheduled_posts(created_at);

-- 5) Sent posts
CREATE TABLE IF NOT EXISTS sent_posts (
    id SERIAL PRIMARY KEY,
    scheduled_post_id INTEGER NOT NULL REFERENCES scheduled_posts(id) ON DELETE CASCADE,
    channel_id BIGINT NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    message_id BIGINT NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6) Seed minimal plans (idempotent)
INSERT INTO plans (name, plan_name, max_channels, max_posts_per_month)
VALUES
    ('free',     'free',     1,   30),
    ('pro',      'pro',      3,  200),
    ('business', 'business',10, 2000)
ON CONFLICT (name) DO NOTHING;
