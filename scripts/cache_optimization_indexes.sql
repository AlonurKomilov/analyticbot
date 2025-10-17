-- Cache Optimization Indexes for Phase 2 Redis Caching
-- Applied: $(date)

-- 1. User ID lookup (for cache key generation)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_id_active
ON users (id) WHERE is_active = TRUE;

-- 2. Channel list covering index (cache:analytics:channels:{user_id})
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_analytics_cover
ON channels (user_id, id, title, username, created_at);

-- 3. Fast channel count (cache:analytics:channels:{user_id})
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_count
ON channels (user_id) WHERE user_id IS NOT NULL;

-- 4. Analytics aggregation (trending posts)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_trending
ON scheduled_posts (status, views DESC, created_at DESC)
WHERE views > 0;

-- 5. Recent activity tracking (7-day window)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_recent_activity
ON scheduled_posts (user_id, created_at DESC)
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';

-- 6. Active user count (health check optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active_count
ON users (created_at)
WHERE is_active = TRUE AND created_at >= CURRENT_DATE - INTERVAL '30 days';

-- 7. Channel statistics (30-day window)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sent_posts_channel_stats
ON sent_posts (channel_id, sent_at DESC)
WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days';

-- 8. User lookup by username (auth middleware)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_lookup
ON users (username) WHERE is_active = TRUE;

-- 9. Time-series analytics (90-day window)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_scheduled_posts_timeseries
ON scheduled_posts (created_at, status, views)
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days';

-- 10. Multi-channel dashboard queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_channels_user_dashboard
ON channels (user_id, is_active, created_at DESC);

-- Verify indexes created
SELECT 'Index Creation Complete' AS status;
