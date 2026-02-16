"""
0053_add_mtproto_media_download_service

Adds the mtproto_media_download service to marketplace_services.
This service was implemented in code but missing from the seed data.

Revision ID: 0053_add_media_download
Revises: 0052_seed_categories
Create Date: 2025-12-17
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "0053_add_media_download"
down_revision = "0052_seed_categories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add mtproto_media_download service to marketplace_services"""

    op.execute("""
        INSERT INTO marketplace_services (
            service_key, name, description, short_description,
            price_credits_monthly, price_credits_yearly,
            category, subcategory,
            features, usage_quota_daily, usage_quota_monthly, rate_limit_per_minute,
            requires_bot, requires_mtproto, min_tier,
            icon, color, is_featured, is_popular, is_new, sort_order, is_active
        ) VALUES (
            'mtproto_media_download',
            'Media Download Service',
            'Bulk download photos, videos, and documents from any Telegram channel using MTProto. Supports progress tracking, resume capability, and multiple media types.',
            'Bulk media file downloads from channels',
            75,
            750,
            'mtproto_services',
            'media_operations',
            '["Bulk media download", "Photo/video/document support", "Progress tracking", "Resume capability", "Date range filters", "Multiple format support"]'::jsonb,
            500,    -- 500 files per day
            10000,  -- 10k files per month
            25,     -- 25 requests per minute
            false,
            true,   -- Requires MTProto
            'premium',  -- Requires premium tier
            'cloud_download',
            '#00ACC1',
            false,  -- Not featured
            false,  -- Not popular (new)
            true,   -- Is new!
            13,     -- Sort after auto-collection
            true
        )
        ON CONFLICT (service_key) DO NOTHING;
    """)


def downgrade() -> None:
    """Remove mtproto_media_download service"""
    op.execute("""
        DELETE FROM marketplace_services WHERE service_key = 'mtproto_media_download'
    """)
