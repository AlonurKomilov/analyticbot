-- Performance Optimization Indexes
-- Run these commands in your PostgreSQL database for significant performance improvements
-- Using CONCURRENTLY to avoid table locks during index creation

-- ============================================
-- User Bot Credentials (High Priority)
-- ============================================

-- User ID + Verification Status (most common query pattern)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_bot_user_verified 
ON user_bot_credentials(user_id, is_verified);

-- Status + Updated timestamp (for admin dashboards)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_bot_status_updated 
ON user_bot_credentials(status, updated_at DESC);

-- Bot username lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_bot_username 
ON user_bot_credentials(bot_username) 
WHERE bot_username IS NOT NULL;

-- MTProto enabled bots
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_bot_mtproto 
ON user_bot_credentials(mtproto_enabled) 
WHERE mtproto_enabled = true;

-- ============================================
-- Channels (High Priority)
-- ============================================

-- Active channels by user
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_active 
ON channels(user_id, is_active);

-- Active channels with recent updates
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_active_updated 
ON channels(is_active, updated_at DESC);

-- Channel ID + Active status (for joins)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_id_active 
ON channels(id, is_active);

-- Telegram ID lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_telegram_id 
ON channels(telegram_id);

-- ============================================
-- Posts (Medium Priority)
-- ============================================

-- Channel ID + Published date (chronological listings)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_channel_date 
ON posts(channel_id, published_at DESC);

-- User ID + Published date (user's posts)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_user_published 
ON posts(user_id, published_at DESC);

-- Post ID + Channel (for joins)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_id_channel 
ON posts(id, channel_id);

-- ============================================
-- Channel Statistics (High Priority)
-- ============================================

-- Channel + Date (time series queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channel_stats_channel_date 
ON channel_statistics(channel_id, date DESC);

-- Date range queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channel_stats_date 
ON channel_statistics(date DESC);

-- ============================================
-- Post Statistics (Medium Priority)
-- ============================================

-- Post + Date
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_stats_post_date 
ON post_statistics(post_id, date DESC);

-- Views sorting
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_post_stats_views 
ON post_statistics(views DESC);

-- ============================================
-- Users (Low Priority - Usually small table)
-- ============================================

-- Email lookup (for login)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email 
ON users(email);

-- Telegram ID lookup (for Telegram OAuth)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_telegram_id 
ON users(telegram_id) 
WHERE telegram_id IS NOT NULL;

-- Role-based queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role 
ON users(role);

-- ============================================
-- User AI Config (Medium Priority)
-- ============================================

-- User + Enabled status
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_ai_config_user_enabled 
ON user_ai_config(user_id, enabled);

-- Enabled configs (for bulk operations)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_ai_config_enabled 
ON user_ai_config(enabled) 
WHERE enabled = true;

-- ============================================
-- User AI Providers (Medium Priority)
-- ============================================

-- User + Provider lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_ai_providers_user_provider 
ON user_ai_providers(user_id, provider_key);

-- Active providers
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_ai_providers_active 
ON user_ai_providers(is_active, provider_key) 
WHERE is_active = true;

-- ============================================
-- Channel MTProto Settings (Medium Priority)
-- ============================================

-- User + Channel lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channel_mtproto_user_channel 
ON channel_mtproto_settings(user_id, channel_id);

-- Enabled MTProto sessions
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channel_mtproto_enabled 
ON channel_mtproto_settings(mtproto_enabled) 
WHERE mtproto_enabled = true;

-- ============================================
-- Audit Logs (Low Priority - Admin only)
-- ============================================

-- Admin user + Timestamp
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_admin_timestamp 
ON audit_logs(admin_user_id, timestamp DESC);

-- Action type filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_action 
ON audit_logs(action, timestamp DESC);

-- ============================================
-- Verification
-- ============================================

-- Verify indexes were created
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Check for missing indexes on foreign keys
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- ============================================
-- Performance Analysis Queries
-- ============================================

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find unused indexes (candidates for removal)
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
  AND idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexname::regclass) DESC;

-- Table sizes with index overhead
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) AS total_size,
    pg_size_pretty(pg_relation_size(tablename::regclass)) AS table_size,
    pg_size_pretty(pg_total_relation_size(tablename::regclass) - pg_relation_size(tablename::regclass)) AS indexes_size,
    round(100 * (pg_total_relation_size(tablename::regclass) - pg_relation_size(tablename::regclass))::numeric / 
          NULLIF(pg_total_relation_size(tablename::regclass), 0), 2) AS index_ratio
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
