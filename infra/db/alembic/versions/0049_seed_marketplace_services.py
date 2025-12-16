"""
0049_seed_marketplace_services

Seeds initial marketplace services catalog with bot moderation and MTProto features.

Revision ID: 0049_seed_services
Revises: 0048_marketplace_services
Create Date: 2025-12-14
"""

from alembic import op


# revision identifiers, used by Alembic
revision = "0049_seed_services"
down_revision = "0048_marketplace_services"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed initial marketplace services"""

    # ============================================
    # Bot Moderation Services
    # ============================================
    op.execute(
        """
        INSERT INTO marketplace_services (
            service_key, name, description, short_description,
            price_credits_monthly, price_credits_yearly,
            category, subcategory,
            features, usage_quota_daily, usage_quota_monthly, rate_limit_per_minute,
            requires_bot, requires_mtproto, min_tier,
            icon, color, is_featured, is_popular, is_new, sort_order, is_active
        ) VALUES
        
        -- Anti-Spam Protection (FEATURED & POPULAR)
        (
            'bot_anti_spam',
            'Anti-Spam Protection',
            'Advanced spam detection and prevention for your Telegram bot. Automatically detects and removes spam messages, malicious links, and bot-like behavior. Protects your community from unwanted content.',
            'Automatic spam detection and removal',
            50,
            500,
            'bot_service',
            'spam_prevention',
            '["Real-time spam detection", "Malicious link blocking", "Bot detection", "Flood prevention", "Customizable sensitivity", "Detailed logs"]'::jsonb,
            NULL,  -- Unlimited daily
            NULL,  -- Unlimited monthly
            100,   -- 100 checks per minute
            true,  -- Requires bot
            false,
            NULL,  -- No tier requirement
            'shield',
            '#E91E63',
            true,  -- Featured
            true,  -- Popular
            false,
            1,
            true
        ),
        
        -- Auto-Delete Join/Leave Messages
        (
            'bot_auto_delete_joins',
            'Auto-Delete Join/Leave',
            'Automatically removes "User joined" and "User left" system messages to keep your chat clean and focused. Configurable delay and chat-specific settings.',
            'Remove join/leave notifications',
            30,
            300,
            'bot_service',
            'chat_cleanup',
            '["Auto-delete joins", "Auto-delete leaves", "Configurable delay", "Per-chat settings", "Bulk cleanup"]'::jsonb,
            NULL,
            NULL,
            200,
            true,
            false,
            NULL,
            'auto_delete',
            '#9C27B0',
            false,
            true,  -- Popular
            false,
            2,
            true
        ),
        
        -- Banned Words Filter
        (
            'bot_banned_words',
            'Banned Words Filter',
            'Create custom lists of banned words and phrases. Automatically deletes messages containing forbidden content and optionally warns or bans repeat offenders.',
            'Custom word filtering and blocking',
            40,
            400,
            'bot_service',
            'content_filter',
            '["Custom word lists", "Regex support", "Auto-delete", "Warning system", "Case-insensitive", "Multi-language"]'::jsonb,
            NULL,
            NULL,
            150,
            true,
            false,
            NULL,
            'block',
            '#F44336',
            false,
            false,
            false,
            3,
            true
        ),
        
        -- Welcome Messages
        (
            'bot_welcome_messages',
            'Welcome Messages',
            'Greet new members with customizable welcome messages. Support for text, images, buttons, and personalized variables like username and chat name.',
            'Custom greetings for new members',
            20,
            200,
            'bot_service',
            'engagement',
            '["Custom messages", "Media support", "Buttons/keyboards", "Variable substitution", "Per-chat customization"]'::jsonb,
            NULL,
            NULL,
            50,
            true,
            false,
            NULL,
            'waving_hand',
            '#4CAF50',
            false,
            false,
            false,
            4,
            true
        ),
        
        -- Invite Link Tracking
        (
            'bot_invite_tracking',
            'Invite Link Tracking',
            'Track who invited each member to your chat. Generate unique invite links and see detailed statistics about member recruitment and engagement.',
            'Track member invites and sources',
            35,
            350,
            'bot_service',
            'analytics',
            '["Unique invite links", "Member tracking", "Invite statistics", "Leaderboards", "CSV export"]'::jsonb,
            NULL,
            NULL,
            100,
            true,
            false,
            NULL,
            'link',
            '#FF9800',
            false,
            false,
            false,
            5,
            true
        ),
        
        -- Warning System
        (
            'bot_warning_system',
            'Warning System',
            'Issue warnings to members who violate rules. Automatic escalation system with configurable thresholds. Track warning history and automatically ban repeat offenders.',
            'Automated warning and ban system',
            45,
            450,
            'bot_service',
            'enforcement',
            '["Manual warnings", "Auto-warnings", "Escalation rules", "Warning history", "Automatic bans", "Custom thresholds"]'::jsonb,
            NULL,
            NULL,
            80,
            true,
            false,
            NULL,
            'warning',
            '#FF5722',
            false,
            false,
            false,
            6,
            true
        );
    """
    )

    # ============================================
    # MTProto Premium Services
    # ============================================
    op.execute(
        """
        INSERT INTO marketplace_services (
            service_key, name, description, short_description,
            price_credits_monthly, price_credits_yearly,
            category, subcategory,
            features, usage_quota_daily, usage_quota_monthly, rate_limit_per_minute,
            requires_bot, requires_mtproto, min_tier,
            icon, color, is_featured, is_popular, is_new, sort_order, is_active
        ) VALUES
        
        -- MTProto History Access (FEATURED)
        (
            'mtproto_history_access',
            'MTProto History Access',
            'Access full message history from any Telegram chat using MTProto. Download messages, media, and metadata for analysis and archival purposes.',
            'Full chat history download via MTProto',
            100,
            1000,
            'mtproto_services',
            'data_access',
            '["Full history access", "Media download", "Message search", "Date range filters", "Export to JSON/CSV", "API access"]'::jsonb,
            1000,   -- 1000 messages per day
            20000,  -- 20k messages per month
            30,     -- 30 requests per minute
            false,
            true,   -- Requires MTProto
            'premium',  -- Requires premium tier
            'history',
            '#2196F3',
            true,   -- Featured
            true,   -- Popular
            false,
            10,
            true
        ),
        
        -- Bulk Message Export
        (
            'mtproto_bulk_export',
            'Bulk Message Export',
            'Export large volumes of messages and media from multiple chats simultaneously. Optimized for archival and data analysis workflows.',
            'High-volume message and media export',
            150,
            1500,
            'mtproto_services',
            'bulk_operations',
            '["Multi-chat export", "Media download", "Parallel processing", "Resume support", "Progress tracking", "Custom filters"]'::jsonb,
            5000,   -- 5k messages per day
            100000, -- 100k messages per month
            20,     -- 20 requests per minute
            false,
            true,
            'enterprise',
            'cloud_download',
            '#00BCD4',
            false,
            false,
            true,   -- New
            11,
            true
        ),
        
        -- MTProto Auto-Collection
        (
            'mtproto_auto_collect',
            'MTProto Auto-Collection',
            'Automatically collect new messages from monitored chats in real-time. Perfect for continuous monitoring and analytics pipelines.',
            'Real-time message collection',
            80,
            800,
            'mtproto_services',
            'automation',
            '["Real-time collection", "Multi-chat monitoring", "Webhook support", "Filter rules", "Automatic scheduling", "Low latency"]'::jsonb,
            NULL,   -- Unlimited
            NULL,
            60,
            false,
            true,
            'premium',
            'sync',
            '#3F51B5',
            false,
            true,
            false,
            12,
            true
        );
    """
    )

    # ============================================
    # Bot Analytics Services
    # ============================================
    op.execute(
        """
        INSERT INTO marketplace_services (
            service_key, name, description, short_description,
            price_credits_monthly, price_credits_yearly,
            category, subcategory,
            features, usage_quota_daily, usage_quota_monthly, rate_limit_per_minute,
            requires_bot, requires_mtproto, min_tier,
            icon, color, is_featured, is_popular, is_new, sort_order, is_active
        ) VALUES
        
        -- Bot Analytics Dashboard
        (
            'bot_analytics_advanced',
            'Advanced Bot Analytics',
            'Comprehensive analytics dashboard for your Telegram bot. Track user engagement, command usage, popular features, and growth metrics over time.',
            'Detailed bot usage analytics',
            60,
            600,
            'bot_analytics',
            'insights',
            '["User metrics", "Command analytics", "Growth tracking", "Retention analysis", "Custom dashboards", "PDF reports"]'::jsonb,
            NULL,
            NULL,
            50,
            true,
            false,
            NULL,
            'analytics',
            '#673AB7',
            false,
            false,
            true,
            20,
            true
        );
    """
    )


def downgrade() -> None:
    """Remove seeded marketplace services"""
    op.execute("DELETE FROM marketplace_services")
