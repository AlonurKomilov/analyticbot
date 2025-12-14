"""Enhance credit system with tier-based features

Revision ID: 0042_enhance_credit_system_tiers
Revises: 0041_seed_credit_system_data
Create Date: 2025-12-07

This migration adds tier-based credit features:
- Adds monthly_credits, daily_credits_base, daily_credits_max to plans
- Updates plans with credit allowances
- Updates Business plan to 5 channels
- Adds monthly_credits_used, monthly_credits_reset_at to user_credits
- Updates credit services pricing for new economy
"""

import sqlalchemy as sa
from alembic import op

revision = "0042_enhance_credit_system_tiers"
down_revision = "0041_seed_credit_system_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("\n" + "=" * 70)
    print("MIGRATION 0042: Enhance Credit System with Tier-Based Features")
    print("=" * 70 + "\n")

    # ============================================
    # 1. Add credit columns to plans table
    # ============================================
    print("📦 Adding credit columns to plans table...")

    op.add_column(
        "plans",
        sa.Column("monthly_credits", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "plans",
        sa.Column("daily_credits_base", sa.Integer(), server_default="5", nullable=False),
    )
    op.add_column(
        "plans",
        sa.Column("daily_credits_max", sa.Integer(), server_default="8", nullable=False),
    )
    op.add_column(
        "plans",
        sa.Column("monthly_credits_cap", sa.Integer(), nullable=True),  # NULL = unlimited
    )
    op.add_column(
        "plans",
        sa.Column("features_json", sa.JSON(), nullable=True),
    )
    print("   ✅ Added plan credit columns\n")

    # ============================================
    # 2. Add monthly tracking to user_credits
    # ============================================
    print("📦 Adding monthly credit tracking to user_credits...")

    op.add_column(
        "user_credits",
        sa.Column("monthly_credits_used", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "user_credits",
        sa.Column("monthly_credits_reset_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "user_credits",
        sa.Column("signup_bonus_claimed", sa.Boolean(), server_default="false", nullable=False),
    )
    print("   ✅ Added monthly tracking columns\n")

    # ============================================
    # 3. Update plans with new credit system
    # ============================================
    print("📦 Updating plans with credit allowances...")

    # FREE plan: 5 base, 8 max daily, 100/month cap, 1 channel
    op.execute(
        """
        UPDATE plans SET
            monthly_credits = 0,
            daily_credits_base = 5,
            daily_credits_max = 8,
            monthly_credits_cap = 100,
            max_channels = 1,
            features_json = '{
                "basic_analytics": true,
                "ai_features": "pay_per_use",
                "exports": "pay_per_use",
                "priority_sync": false,
                "remove_branding": false,
                "api_access": false
            }'::jsonb
        WHERE name = 'free'
    """
    )
    print("   ✅ Updated FREE plan: 5-8 credits/day, 100/month cap, 1 channel")

    # PRO plan: 200 monthly + 10 base, 15 max daily, 3 channels
    op.execute(
        """
        UPDATE plans SET
            monthly_credits = 200,
            daily_credits_base = 10,
            daily_credits_max = 15,
            monthly_credits_cap = NULL,
            max_channels = 3,
            features_json = '{
                "basic_analytics": true,
                "ai_features": "basic_unlimited",
                "exports": "unlimited",
                "priority_sync": true,
                "remove_branding": false,
                "api_access": false
            }'::jsonb
        WHERE name = 'pro'
    """
    )
    print("   ✅ Updated PRO plan: 200/mo + 10-15/day bonus, 3 channels")

    # BUSINESS plan: 1000 monthly + 20 base, 30 max daily, 5 channels
    op.execute(
        """
        UPDATE plans SET
            monthly_credits = 1000,
            daily_credits_base = 20,
            daily_credits_max = 30,
            monthly_credits_cap = NULL,
            max_channels = 5,
            features_json = '{
                "basic_analytics": true,
                "ai_features": "all_unlimited",
                "exports": "unlimited",
                "priority_sync": true,
                "remove_branding": true,
                "api_access": false,
                "priority_support": true
            }'::jsonb
        WHERE name = 'business'
    """
    )
    print("   ✅ Updated BUSINESS plan: 1000/mo + 20-30/day bonus, 5 channels")

    # ============================================
    # 4. Update credit services pricing
    # ============================================
    print("\n📦 Updating credit services pricing...")

    # AI Services - adjusted for new economy
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 3
        WHERE service_key = 'ai_post_analysis'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 5
        WHERE service_key = 'ai_content_suggestions'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 5
        WHERE service_key = 'ai_optimal_time'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 10
        WHERE service_key = 'ai_competitor_analysis'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 15
        WHERE service_key = 'ai_trend_prediction'
    """
    )
    print("   ✅ AI: Post=3, Suggestions=5, Timing=5, Competitor=10, Trends=15")

    # Export Services - cheaper for accessibility
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 1
        WHERE service_key = 'export_image_chart'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 2
        WHERE service_key = 'export_csv_data'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 3
        WHERE service_key = 'export_pdf_report'
    """
    )
    print("   ✅ Exports: Image=1, CSV=2, PDF=3")

    # Premium features - one-time purchases
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 20
        WHERE service_key = 'advanced_filters'
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 25
        WHERE service_key = 'remove_watermark'
    """
    )
    print("   ✅ Features: Filters=20, No Watermark=25")

    # Themes - cosmetic, slightly lower
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 30
        WHERE service_key IN ('theme_premium_dark', 'theme_premium_light')
    """
    )
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 50
        WHERE service_key = 'theme_custom_colors'
    """
    )
    print("   ✅ Themes: Premium=30, Custom=50")

    # Channel slot - valuable but accessible
    op.execute(
        """
        UPDATE credit_services SET credit_cost = 150
        WHERE service_key = 'extra_channel_slot'
    """
    )
    print("   ✅ Extra Channel: 150 credits")

    # ============================================
    # 5. Update achievements for new economy
    # ============================================
    print("\n📦 Updating achievement rewards...")

    op.execute(
        """
        UPDATE achievements SET credit_reward = 50
        WHERE achievement_key = 'first_login'
    """
    )
    op.execute(
        """
        UPDATE achievements SET credit_reward = 20
        WHERE achievement_key = 'first_channel'
    """
    )
    op.execute(
        """
        UPDATE achievements SET credit_reward = 10
        WHERE achievement_key = 'first_ai_analysis'
    """
    )
    op.execute(
        """
        UPDATE achievements SET credit_reward = 25
        WHERE achievement_key = 'streak_7'
    """
    )
    op.execute(
        """
        UPDATE achievements SET credit_reward = 100
        WHERE achievement_key = 'streak_30'
    """
    )
    print("   ✅ Signup=50, First Channel=20, First AI=10, 7-day=25, 30-day=100")

    # ============================================
    # 6. Update credit packages for new pricing
    # ============================================
    print("\n📦 Updating credit packages...")

    op.execute(
        """
        UPDATE credit_packages SET
            credits = 50, bonus_credits = 0, price = 2.99,
            description = 'Try premium features - enough for ~15 AI analyses'
        WHERE slug = 'starter'
    """
    )
    op.execute(
        """
        UPDATE credit_packages SET
            credits = 200, bonus_credits = 25, price = 9.99,
            description = 'Most popular - great value for regular users'
        WHERE slug = 'popular'
    """
    )
    op.execute(
        """
        UPDATE credit_packages SET
            credits = 500, bonus_credits = 100, price = 19.99,
            description = 'Power user pack - 20% bonus credits!'
        WHERE slug = 'pro'
    """
    )
    op.execute(
        """
        UPDATE credit_packages SET
            credits = 1500, bonus_credits = 500, price = 49.99,
            description = 'Best value - 33% bonus for heavy users!'
        WHERE slug = 'enterprise'
    """
    )
    print("   ✅ Starter=$2.99(50), Popular=$9.99(225), Pro=$19.99(600), Enterprise=$49.99(2000)")

    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE - Credit System Enhanced")
    print("=" * 70)
    print(
        """
Summary:
  • FREE: 5-8 credits/day, 100/month cap, 1 channel
  • PRO ($9.99): 200/mo + 10-15/day, unlimited cap, 3 channels
  • BUSINESS ($29.99): 1000/mo + 20-30/day, unlimited, 5 channels
  • API access: NOT included (separate product)
  • AI pricing: 3-15 credits (affordable for daily users)
  • Signup bonus: 50 credits
"""
    )


def downgrade() -> None:
    # Remove columns from user_credits
    op.drop_column("user_credits", "signup_bonus_claimed")
    op.drop_column("user_credits", "monthly_credits_reset_at")
    op.drop_column("user_credits", "monthly_credits_used")

    # Remove columns from plans
    op.drop_column("plans", "features_json")
    op.drop_column("plans", "monthly_credits_cap")
    op.drop_column("plans", "daily_credits_max")
    op.drop_column("plans", "daily_credits_base")
    op.drop_column("plans", "monthly_credits")

    # Restore original max_channels for business
    op.execute("UPDATE plans SET max_channels = 10 WHERE name = 'business'")
