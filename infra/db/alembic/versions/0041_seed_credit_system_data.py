"""Seed credit system data

Revision ID: 0040_seed_credit_system_data
Revises: 0039_credit_system_tables
Create Date: 2025-12-05

Seeds initial data for the credit system:
- Credit packages (Starter, Popular, Pro, Enterprise)
- Credit services (AI features, exports, etc.)
- Achievements (account, streaks, referrals, etc.)
- Marketplace items (themes, AI models, widgets)
- Marketplace bundles
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0041_seed_credit_system_data"
down_revision = "0040_credit_system_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # Seed Credit Packages
    # ============================================
    op.execute("""
        INSERT INTO credit_packages (name, slug, credits, bonus_credits, price, currency, description, is_popular, sort_order)
        VALUES
            ('Starter Pack', 'starter', 100, 0, 4.99, 'USD', 'Perfect for trying out premium features', false, 1),
            ('Popular Pack', 'popular', 500, 50, 19.99, 'USD', 'Most popular choice - 10% bonus credits!', true, 2),
            ('Pro Pack', 'pro', 1200, 200, 39.99, 'USD', 'Best value for power users - 17% bonus!', false, 3),
            ('Enterprise Pack', 'enterprise', 3000, 750, 89.99, 'USD', 'Maximum savings - 25% bonus credits!', false, 4)
    """)

    # ============================================
    # Seed Credit Services
    # ============================================
    op.execute("""
        INSERT INTO credit_services (service_key, name, description, credit_cost, category, icon, usage_limit_per_day, sort_order)
        VALUES
            -- AI Features
            ('ai_content_analysis', 'AI Content Analysis', 'Deep analysis of your post performance using AI', 25, 'ai', 'psychology', NULL, 1),
            ('ai_caption_generator', 'AI Caption Generator', 'Generate engaging captions for your posts', 10, 'ai', 'auto_awesome', 20, 2),
            ('ai_hashtag_suggestions', 'AI Hashtag Suggestions', 'Get AI-powered hashtag recommendations', 5, 'ai', 'tag', 50, 3),
            ('ai_best_time_predictor', 'Best Time Predictor', 'AI predicts optimal posting times', 15, 'ai', 'schedule', 10, 4),
            ('ai_competitor_analysis', 'Competitor Analysis', 'Analyze competitor channels with AI', 50, 'ai', 'compare_arrows', 5, 5),
            ('ai_trend_detection', 'Trend Detection', 'Detect emerging trends in your niche', 30, 'ai', 'trending_up', 10, 6),
            
            -- Export Features
            ('export_pdf_report', 'PDF Report Export', 'Export detailed analytics as PDF', 20, 'export', 'picture_as_pdf', NULL, 10),
            ('export_csv_data', 'CSV Data Export', 'Export raw data as CSV', 10, 'export', 'table_chart', NULL, 11),
            ('export_excel_report', 'Excel Report', 'Export comprehensive Excel report', 25, 'export', 'grid_on', NULL, 12),
            
            -- Premium Features
            ('advanced_analytics', 'Advanced Analytics', 'Access advanced analytics dashboard', 30, 'feature', 'analytics', NULL, 20),
            ('custom_reports', 'Custom Reports', 'Create customized report templates', 40, 'feature', 'dashboard_customize', 5, 21),
            ('api_access_hour', 'API Access (1 Hour)', 'Programmatic API access for 1 hour', 50, 'api', 'api', NULL, 30),
            ('api_access_day', 'API Access (24 Hours)', 'Programmatic API access for 24 hours', 200, 'api', 'api', NULL, 31),
            
            -- Upgrades
            ('priority_processing', 'Priority Processing', 'Get your analytics processed first', 15, 'upgrade', 'bolt', NULL, 40),
            ('extended_history', 'Extended History', 'Access 1 year of historical data', 100, 'upgrade', 'history', NULL, 41)
    """)

    # ============================================
    # Seed Achievements
    # ============================================
    op.execute("""
        INSERT INTO achievements (achievement_key, name, description, credit_reward, icon, category, requirement_type, requirement_value, sort_order)
        VALUES
            -- Account Achievements
            ('first_login', 'Welcome Aboard!', 'Complete your first login', 10, 'rocket_launch', 'account', NULL, NULL, 1),
            ('profile_complete', 'Profile Pro', 'Complete your profile information', 25, 'person_check', 'account', NULL, NULL, 2),
            ('verified_email', 'Verified', 'Verify your email address', 15, 'verified', 'account', NULL, NULL, 3),
            
            -- Channel Achievements
            ('first_channel', 'Channel Pioneer', 'Connect your first channel', 50, 'tv', 'channels', 'count', 1, 10),
            ('five_channels', 'Channel Collector', 'Connect 5 channels', 100, 'workspace_premium', 'channels', 'count', 5, 11),
            ('ten_channels', 'Channel Empire', 'Connect 10 channels', 250, 'castle', 'channels', 'count', 10, 12),
            
            -- Engagement Achievements
            ('first_1k_views', 'Rising Star', 'Get 1,000 total views across channels', 25, 'visibility', 'engagement', 'value', 1000, 20),
            ('first_10k_views', 'Going Viral', 'Get 10,000 total views across channels', 75, 'star', 'engagement', 'value', 10000, 21),
            ('first_100k_views', 'Superstar', 'Get 100,000 total views across channels', 200, 'diamond', 'engagement', 'value', 100000, 22),
            
            -- Streak Achievements
            ('streak_3', 'Getting Started', 'Maintain a 3-day login streak', 15, 'local_fire_department', 'streaks', 'streak', 3, 30),
            ('streak_7', 'Week Warrior', 'Maintain a 7-day login streak', 35, 'whatshot', 'streaks', 'streak', 7, 31),
            ('streak_30', 'Monthly Master', 'Maintain a 30-day login streak', 150, 'emoji_events', 'streaks', 'streak', 30, 32),
            ('streak_100', 'Century Club', 'Maintain a 100-day login streak', 500, 'military_tech', 'streaks', 'streak', 100, 33),
            
            -- Credit Achievements
            ('first_purchase', 'First Investment', 'Make your first credit purchase', 20, 'shopping_cart', 'credits', NULL, NULL, 40),
            ('big_spender', 'Big Spender', 'Spend 1,000 credits total', 100, 'savings', 'credits', 'value', 1000, 41),
            ('whale', 'Whale', 'Spend 10,000 credits total', 500, 'paid', 'credits', 'value', 10000, 42),
            
            -- Referral Achievements
            ('first_referral', 'Friendly Face', 'Refer your first friend', 50, 'person_add', 'referrals', 'count', 1, 50),
            ('five_referrals', 'Social Butterfly', 'Refer 5 friends', 150, 'groups', 'referrals', 'count', 5, 51),
            ('ten_referrals', 'Community Builder', 'Refer 10 friends', 400, 'diversity_3', 'referrals', 'count', 10, 52)
    """)

    # ============================================
    # Seed Marketplace Items - Themes
    # ============================================
    op.execute("""
        INSERT INTO marketplace_items (name, slug, description, category, subcategory, price_credits, is_premium, is_featured, icon_url, metadata, download_count, rating, rating_count)
        VALUES
            ('Dark Mode Pro', 'dark-mode-pro', 'Premium dark theme with OLED-optimized colors and reduced eye strain', 'themes', 'dark', 150, true, true, '/marketplace/themes/dark-pro.png', '{"colors": {"primary": "#1a1a2e", "accent": "#6366f1"}}', 1245, 4.8, 156),
            ('Ocean Breeze', 'ocean-breeze', 'Calming blue theme inspired by ocean waves', 'themes', 'light', 100, false, false, '/marketplace/themes/ocean.png', '{"colors": {"primary": "#0ea5e9", "accent": "#06b6d4"}}', 856, 4.5, 92),
            ('Sunset Gradient', 'sunset-gradient', 'Beautiful warm gradient theme with sunset colors', 'themes', 'gradient', 125, false, true, '/marketplace/themes/sunset.png', '{"colors": {"primary": "#f97316", "accent": "#ec4899"}}', 723, 4.7, 84),
            ('Minimalist White', 'minimalist-white', 'Clean, distraction-free white theme', 'themes', 'light', 75, false, false, '/marketplace/themes/minimal.png', '{"colors": {"primary": "#ffffff", "accent": "#374151"}}', 1532, 4.3, 201),
            ('Neon Cyberpunk', 'neon-cyberpunk', 'Futuristic neon theme with cyberpunk aesthetics', 'themes', 'dark', 200, true, true, '/marketplace/themes/neon.png', '{"colors": {"primary": "#0f0f23", "accent": "#00ff88"}}', 967, 4.9, 178),
            ('Forest Green', 'forest-green', 'Nature-inspired green theme', 'themes', 'nature', 100, false, false, '/marketplace/themes/forest.png', '{"colors": {"primary": "#064e3b", "accent": "#10b981"}}', 445, 4.4, 56)
    """)

    # ============================================
    # Seed Marketplace Items - AI Models
    # ============================================
    op.execute("""
        INSERT INTO marketplace_items (name, slug, description, category, subcategory, price_credits, is_premium, is_featured, icon_url, metadata, download_count, rating, rating_count)
        VALUES
            ('Advanced Sentiment Analyzer', 'advanced-sentiment', 'Deep learning model for nuanced sentiment analysis of comments and reactions', 'ai_models', 'analysis', 500, true, true, '/marketplace/ai/sentiment.png', '{"model_type": "transformer", "accuracy": 0.94}', 324, 4.9, 67),
            ('Engagement Predictor Pro', 'engagement-predictor', 'Predict post engagement before publishing with 85% accuracy', 'ai_models', 'prediction', 400, true, true, '/marketplace/ai/engagement.png', '{"model_type": "ensemble", "accuracy": 0.85}', 567, 4.7, 89),
            ('Content Optimizer', 'content-optimizer', 'AI-powered suggestions to optimize your content for maximum reach', 'ai_models', 'optimization', 350, true, false, '/marketplace/ai/optimizer.png', '{"model_type": "gpt-based", "features": ["title", "hashtags", "timing"]}', 423, 4.6, 71),
            ('Audience Insights Engine', 'audience-insights', 'Deep dive into your audience demographics and behavior patterns', 'ai_models', 'analysis', 450, true, false, '/marketplace/ai/audience.png', '{"model_type": "clustering", "insights": ["demographics", "interests", "activity"]}', 289, 4.5, 45),
            ('Viral Content Detector', 'viral-detector', 'Identify content with viral potential before competitors', 'ai_models', 'prediction', 600, true, true, '/marketplace/ai/viral.png', '{"model_type": "neural-network", "accuracy": 0.78}', 198, 4.8, 34),
            ('Auto-Reply Generator', 'auto-reply', 'Generate contextual replies to comments automatically', 'ai_models', 'automation', 300, false, false, '/marketplace/ai/reply.png', '{"model_type": "seq2seq", "languages": ["en", "es", "fr"]}', 756, 4.4, 112)
    """)

    # ============================================
    # Seed Marketplace Items - Widgets
    # ============================================
    op.execute("""
        INSERT INTO marketplace_items (name, slug, description, category, subcategory, price_credits, is_premium, is_featured, icon_url, metadata, download_count, rating, rating_count)
        VALUES
            ('Real-time Analytics Widget', 'realtime-widget', 'Live updating analytics widget for your dashboard', 'widgets', 'analytics', 200, false, true, '/marketplace/widgets/realtime.png', '{"refresh_rate": "5s", "metrics": ["views", "engagement", "growth"]}', 876, 4.7, 134),
            ('Competitor Tracker', 'competitor-tracker', 'Side-by-side competitor comparison widget', 'widgets', 'comparison', 250, true, false, '/marketplace/widgets/competitor.png', '{"max_competitors": 5, "metrics": ["followers", "engagement", "posts"]}', 445, 4.5, 67),
            ('Growth Heatmap', 'growth-heatmap', 'Visual heatmap showing growth patterns', 'widgets', 'visualization', 175, false, false, '/marketplace/widgets/heatmap.png', '{"time_range": "30d", "granularity": "hourly"}', 623, 4.6, 89),
            ('Post Scheduler Pro', 'scheduler-widget', 'Advanced scheduling widget with AI-powered time suggestions', 'widgets', 'scheduling', 225, false, true, '/marketplace/widgets/scheduler.png', '{"features": ["drag-drop", "ai-timing", "queue"]}', 1023, 4.8, 167),
            ('Notification Center', 'notification-widget', 'Customizable notification center for important alerts', 'widgets', 'alerts', 150, false, false, '/marketplace/widgets/notifications.png', '{"channels": ["email", "push", "telegram"]}', 534, 4.3, 78),
            ('Revenue Tracker', 'revenue-tracker', 'Track monetization and revenue across channels', 'widgets', 'monetization', 300, true, false, '/marketplace/widgets/revenue.png', '{"currencies": ["USD", "EUR", "GBP"], "integrations": ["stripe", "paypal"]}', 267, 4.7, 42)
    """)

    # ============================================
    # Seed Marketplace Bundles
    # ============================================
    op.execute("""
        INSERT INTO marketplace_bundles (name, slug, description, price_credits, original_price, discount_percent, is_featured, valid_days)
        VALUES
            ('Starter Bundle', 'starter-bundle', 'Perfect for beginners - includes essential themes and widgets', 400, 525, 24, false, 365),
            ('Pro Analytics Bundle', 'pro-analytics', 'Complete analytics toolkit with AI models and widgets', 1200, 1600, 25, true, 365),
            ('Theme Collection', 'theme-collection', 'All premium themes at a discounted price', 600, 850, 29, false, 365),
            ('AI Power Pack', 'ai-power-pack', 'All AI models for maximum insights', 2000, 2600, 23, true, 365),
            ('Ultimate Bundle', 'ultimate-bundle', 'Everything included - themes, widgets, and AI models', 3500, 5000, 30, true, 365)
    """)

    # ============================================
    # Link Bundle Items
    # ============================================
    # Starter Bundle: Dark Mode Pro, Minimalist White, Real-time Widget
    op.execute("""
        INSERT INTO bundle_items (bundle_id, item_id)
        SELECT b.id, i.id FROM marketplace_bundles b, marketplace_items i
        WHERE b.slug = 'starter-bundle' AND i.slug IN ('dark-mode-pro', 'minimalist-white', 'realtime-widget')
    """)

    # Pro Analytics Bundle: Engagement Predictor, Content Optimizer, Growth Heatmap, Real-time Widget
    op.execute("""
        INSERT INTO bundle_items (bundle_id, item_id)
        SELECT b.id, i.id FROM marketplace_bundles b, marketplace_items i
        WHERE b.slug = 'pro-analytics' AND i.slug IN ('engagement-predictor', 'content-optimizer', 'growth-heatmap', 'realtime-widget')
    """)

    # Theme Collection: All themes
    op.execute("""
        INSERT INTO bundle_items (bundle_id, item_id)
        SELECT b.id, i.id FROM marketplace_bundles b, marketplace_items i
        WHERE b.slug = 'theme-collection' AND i.category = 'themes'
    """)

    # AI Power Pack: All AI models
    op.execute("""
        INSERT INTO bundle_items (bundle_id, item_id)
        SELECT b.id, i.id FROM marketplace_bundles b, marketplace_items i
        WHERE b.slug = 'ai-power-pack' AND i.category = 'ai_models'
    """)

    # Ultimate Bundle: Everything
    op.execute("""
        INSERT INTO bundle_items (bundle_id, item_id)
        SELECT b.id, i.id FROM marketplace_bundles b, marketplace_items i
        WHERE b.slug = 'ultimate-bundle' AND i.is_active = true
    """)


def downgrade() -> None:
    # Delete all seeded data in reverse order
    op.execute("DELETE FROM bundle_items")
    op.execute("DELETE FROM marketplace_bundles")
    op.execute("DELETE FROM marketplace_items")
    op.execute("DELETE FROM achievements")
    op.execute("DELETE FROM credit_services")
    op.execute("DELETE FROM credit_packages")
