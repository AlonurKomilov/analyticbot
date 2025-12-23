"""Add AI services to marketplace

Revision ID: 0054
Revises: 0053
Create Date: 2025-12-17

Adds four AI-powered services to the marketplace:
- ai_content_optimizer: Post optimization suggestions (125 cr/mo)
- ai_sentiment_analyzer: Audience sentiment analysis (100 cr/mo)
- ai_smart_replies: AI-generated reply suggestions (150 cr/mo)
- ai_content_moderation: AI-powered content moderation (175 cr/mo)
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '0054'
down_revision = '0053_add_media_download'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get connection for raw SQL
    conn = op.get_bind()
    
    # First, ensure the ai_services category exists
    result = conn.execute(
        sa.text("SELECT id FROM marketplace_categories WHERE slug = 'ai_services'")
    ).fetchone()
    
    if result:
        ai_category_id = result[0]
    else:
        # Create category if it doesn't exist
        conn.execute(sa.text("""
            INSERT INTO marketplace_categories (name, slug, description, icon, color, sort_order, is_active, created_at, updated_at)
            VALUES (
                'AI Services',
                'ai_services',
                'AI-powered features for content optimization, analysis, and automation',
                'Psychology',
                '#6366F1',
                3,
                true,
                :now,
                :now
            )
        """), {"now": datetime.utcnow()})
        
        result = conn.execute(
            sa.text("SELECT id FROM marketplace_categories WHERE slug = 'ai_services'")
        ).fetchone()
        ai_category_id = result[0]
    
    # Insert AI services
    services = [
        {
            "service_key": "ai_content_optimizer",
            "name": "AI Content Optimizer",
            "description": "Get AI-powered suggestions to improve your posts for better engagement, reach, and clarity. Includes hashtag recommendations, tone adjustments, and call-to-action tips.",
            "category_id": ai_category_id,
            "price_credits": 125,
            "billing_period": "monthly",
            "features": '["Engagement optimization", "Tone & style suggestions", "Hashtag recommendations", "Emoji suggestions", "Call-to-action tips", "Length optimization"]',
            "icon": "AutoFixHigh",
            "color": "#6366F1",
            "is_active": True,
            "is_featured": True,
            "sort_order": 1,
            "quota_daily": 50,
            "quota_monthly": 1000,
        },
        {
            "service_key": "ai_sentiment_analyzer",
            "name": "AI Sentiment Analyzer",
            "description": "Understand your audience mood and reactions with AI-powered sentiment analysis. Track trends, detect spikes, and get detailed reports across multiple languages.",
            "category_id": ai_category_id,
            "price_credits": 100,
            "billing_period": "monthly",
            "features": '["Real-time sentiment tracking", "Comment & reaction analysis", "Trend detection", "Alert on sentiment spikes", "Multi-language support", "Detailed reports"]',
            "icon": "SentimentSatisfied",
            "color": "#EC4899",
            "is_active": True,
            "is_featured": False,
            "sort_order": 2,
            "quota_daily": 100,
            "quota_monthly": 2000,
        },
        {
            "service_key": "ai_smart_replies",
            "name": "AI Smart Replies",
            "description": "Generate intelligent, context-aware reply suggestions powered by AI. Customize tone, set up auto-replies, and let AI learn from your communication style.",
            "category_id": ai_category_id,
            "price_credits": 150,
            "billing_period": "monthly",
            "features": '["Context-aware suggestions", "Tone customization", "Auto-reply triggers", "Response timing control", "Signature support", "Learning from history"]',
            "icon": "QuickreplyRounded",
            "color": "#14B8A6",
            "is_active": True,
            "is_featured": True,
            "sort_order": 3,
            "quota_daily": 200,
            "quota_monthly": 4000,
        },
        {
            "service_key": "ai_content_moderation",
            "name": "AI Content Moderation",
            "description": "Automatically detect and moderate harmful content using advanced AI. Detect spam, hate speech, adult content, and more with configurable sensitivity and actions.",
            "category_id": ai_category_id,
            "price_credits": 175,
            "billing_period": "monthly",
            "features": '["Spam detection", "Hate speech filtering", "Adult content detection", "Violence detection", "Auto-moderation actions", "Appeal workflow"]',
            "icon": "Shield",
            "color": "#EF4444",
            "is_active": True,
            "is_featured": False,
            "sort_order": 4,
            "quota_daily": 500,
            "quota_monthly": 10000,
        },
    ]
    
    for service in services:
        # Check if service already exists
        exists = conn.execute(
            sa.text("SELECT id FROM marketplace_services WHERE service_key = :key"),
            {"key": service["service_key"]}
        ).fetchone()
        
        if not exists:
            conn.execute(sa.text("""
                INSERT INTO marketplace_services (
                    service_key, name, description, category_id, price_credits,
                    billing_period, features, icon, color, is_active, is_featured,
                    sort_order, quota_daily, quota_monthly, created_at, updated_at
                ) VALUES (
                    :service_key, :name, :description, :category_id, :price_credits,
                    :billing_period, :features, :icon, :color, :is_active, :is_featured,
                    :sort_order, :quota_daily, :quota_monthly, :now, :now
                )
            """), {**service, "now": datetime.utcnow()})
            print(f"✅ Added AI service: {service['name']}")
        else:
            print(f"⏭️  AI service already exists: {service['name']}")


def downgrade() -> None:
    conn = op.get_bind()
    
    # Remove AI services
    service_keys = [
        'ai_content_optimizer',
        'ai_sentiment_analyzer', 
        'ai_smart_replies',
        'ai_content_moderation',
    ]
    
    for key in service_keys:
        conn.execute(
            sa.text("DELETE FROM marketplace_services WHERE service_key = :key"),
            {"key": key}
        )
        print(f"🗑️  Removed AI service: {key}")
