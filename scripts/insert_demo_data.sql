-- Insert demo data for testing exports and analytics
-- This creates a demo_channel with sample analytics data

-- Insert demo channel if not exists
INSERT INTO channels (id, username, title, type, subscriber_count, created_at, updated_at)
VALUES (
    -1001234567890,
    'demo_channel',
    'Demo Analytics Channel',
    'channel',
    1500,
    NOW() - INTERVAL '30 days',
    NOW()
) ON CONFLICT (id) DO UPDATE SET
    subscriber_count = EXCLUDED.subscriber_count,
    updated_at = EXCLUDED.updated_at;

-- Insert demo daily analytics data for the last 30 days
INSERT INTO channel_daily (channel_id, date, subscribers, views, posts, engagement_rate)
SELECT 
    -1001234567890,
    date_series.date,
    1500 + (EXTRACT(DAY FROM date_series.date) * 2), -- Growing subscribers
    FLOOR(RANDOM() * 1000 + 500)::int, -- Random views 500-1500
    FLOOR(RANDOM() * 5 + 1)::int, -- Random posts 1-5
    ROUND((RANDOM() * 0.1 + 0.05)::numeric, 3) -- Random engagement 5-15%
FROM (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '30 days',
        CURRENT_DATE - INTERVAL '1 day',
        INTERVAL '1 day'
    )::date AS date
) AS date_series
ON CONFLICT (channel_id, date) DO UPDATE SET
    subscribers = EXCLUDED.subscribers,
    views = EXCLUDED.views,
    posts = EXCLUDED.posts,
    engagement_rate = EXCLUDED.engagement_rate,
    updated_at = NOW();

-- Insert some demo posts for top posts analytics
INSERT INTO posts (id, channel_id, message_id, content, views, date, created_at)
VALUES 
    (1, -1001234567890, 1001, 'Welcome to our analytics demo! 🚀', 2500, CURRENT_DATE - INTERVAL '5 days', NOW()),
    (2, -1001234567890, 1002, 'Check out these amazing analytics features! 📊', 1800, CURRENT_DATE - INTERVAL '3 days', NOW()),
    (3, -1001234567890, 1003, 'Export your data easily with CSV and PNG options! 📈', 2200, CURRENT_DATE - INTERVAL '2 days', NOW()),
    (4, -1001234567890, 1004, 'Share reports with secure time-limited links! 🔗', 1600, CURRENT_DATE - INTERVAL '1 day', NOW()),
    (5, -1001234567890, 1005, 'Advanced analytics coming soon! ⚡', 1200, CURRENT_DATE, NOW())
ON CONFLICT (id) DO UPDATE SET
    views = EXCLUDED.views,
    updated_at = NOW();

-- Verify the data was inserted
SELECT 'Demo channel created with ID:' as status, id, username, title, subscriber_count 
FROM channels WHERE id = -1001234567890;

SELECT 'Daily analytics records:' as status, COUNT(*) as record_count 
FROM channel_daily WHERE channel_id = -1001234567890;

SELECT 'Demo posts created:' as status, COUNT(*) as post_count
FROM posts WHERE channel_id = -1001234567890;
