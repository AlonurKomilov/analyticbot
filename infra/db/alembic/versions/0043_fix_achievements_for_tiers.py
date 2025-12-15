"""Fix achievements to align with tier limits

Revision ID: 0043_fix_achievements_for_tiers
Revises: 0042_enhance_credit_system_tiers
Create Date: 2025-12-07

Fixes:
1. Channel achievements now match max channel limits (5 max)
2. Adjusted rewards to be meaningful for each tier
3. Added new tier-relevant achievements
4. Increased free tier monthly cap to allow earning rewards
"""

from alembic import op

# revision identifiers
revision = "0043_fix_achievements_for_tiers"
down_revision = "0042_enhance_credit_system_tiers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("=" * 70)
    print("MIGRATION 0043: Fix Achievements for Tier System")
    print("=" * 70)

    # =========================================================================
    # 1. FIX CHANNEL ACHIEVEMENTS (max channels is now 5)
    # =========================================================================
    print("\n📦 Fixing channel achievements...")

    # Remove impossible 10-channel achievement
    op.execute(
        """
        DELETE FROM achievements WHERE achievement_key = 'ten_channels'
    """
    )
    print("   ✅ Removed unreachable 'ten_channels' achievement")

    # Update five_channels to be more achievable (3 channels for Pro users)
    op.execute(
        """
        UPDATE achievements
        SET requirement_value = 3,
            name = 'Multi-Channel Pro',
            description = 'Connect 3 channels to your account',
            credit_reward = 75
        WHERE achievement_key = 'five_channels'
    """
    )
    print("   ✅ Updated 'five_channels' → 'Multi-Channel Pro' (3 channels, 75 credits)")

    # Add new achievement for reaching max channels (5)
    op.execute(
        """
        INSERT INTO achievements (achievement_key, name, description, credit_reward, category, requirement_type, requirement_value, sort_order, is_active)
        VALUES ('max_channels', 'Channel Master', 'Reach the maximum channel limit (5 channels)', 150, 'channels', 'count', 5, 30, true)
        ON CONFLICT (achievement_key) DO UPDATE SET
            name = 'Channel Master',
            description = 'Reach the maximum channel limit (5 channels)',
            credit_reward = 150,
            requirement_value = 5
    """
    )
    print("   ✅ Added 'max_channels' achievement (5 channels, 150 credits)")

    # =========================================================================
    # 2. INCREASE FREE TIER MONTHLY CAP
    # =========================================================================
    print("\n📦 Adjusting free tier monthly cap...")

    # Increase from 100 to 300 so free users can actually earn achievements
    # Daily: 5-8 × 30 = 150-240 credits
    # Signup bonus: 50 credits
    # Some achievements: ~100 credits
    # Total possible: ~400 credits - cap at 300 is fair
    op.execute(
        """
        UPDATE plans
        SET monthly_credits_cap = 300
        WHERE name = 'free'
    """
    )
    print("   ✅ Free tier monthly cap: 100 → 300 credits")

    # =========================================================================
    # 3. ADD TIER-UPGRADE ACHIEVEMENTS
    # =========================================================================
    print("\n📦 Adding tier-related achievements...")

    op.execute(
        """
        INSERT INTO achievements (achievement_key, name, description, credit_reward, category, requirement_type, requirement_value, sort_order, is_active)
        VALUES
            ('upgrade_pro', 'Pro Member', 'Upgrade to Pro plan', 100, 'account', 'action', 1, 15, true),
            ('upgrade_business', 'Business Elite', 'Upgrade to Business plan', 250, 'account', 'action', 1, 16, true)
        ON CONFLICT (achievement_key) DO NOTHING
    """
    )
    print("   ✅ Added 'upgrade_pro' (100 credits) and 'upgrade_business' (250 credits)")

    # =========================================================================
    # 4. ADJUST STREAK REWARDS TO BE TIER-APPROPRIATE
    # =========================================================================
    print("\n📦 Adjusting streak rewards...")

    # Reduce the crazy high streak rewards - they shouldn't be more than monthly bonus
    op.execute(
        """
        UPDATE achievements SET credit_reward = 50 WHERE achievement_key = 'streak_30'
    """
    )
    op.execute(
        """
        UPDATE achievements SET credit_reward = 200 WHERE achievement_key = 'streak_100'
    """
    )
    print("   ✅ streak_30: 100 → 50 credits")
    print("   ✅ streak_100: 500 → 200 credits")

    # =========================================================================
    # 5. ADD USAGE-BASED ACHIEVEMENTS
    # =========================================================================
    print("\n📦 Adding usage-based achievements...")

    op.execute(
        """
        INSERT INTO achievements (achievement_key, name, description, credit_reward, category, requirement_type, requirement_value, sort_order, is_active)
        VALUES
            ('first_ai_use', 'AI Explorer', 'Use an AI-powered feature for the first time', 10, 'engagement', 'action', 1, 40, true),
            ('ai_power_user', 'AI Power User', 'Use AI features 50 times', 50, 'engagement', 'count', 50, 41, true),
            ('first_export', 'Data Exporter', 'Export your first report', 5, 'engagement', 'action', 1, 42, true)
        ON CONFLICT (achievement_key) DO NOTHING
    """
    )
    print("   ✅ Added AI and export achievements")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE - Achievements aligned with tier system")
    print("=" * 70)
    print(
        """
Summary of changes:
  • Channel achievements: Now max at 5 (matching Business tier)
  • Free tier cap: 100 → 300 credits/month (allows earning rewards)
  • New upgrade achievements: Pro (100), Business (250)
  • Streak rewards: Reduced to be tier-appropriate
  • New usage achievements: AI Explorer, Power User, Data Exporter
"""
    )


def downgrade() -> None:
    # Restore original achievements
    op.execute(
        """
        INSERT INTO achievements (achievement_key, name, description, credit_reward, category, requirement_type, requirement_value, sort_order, is_active)
        VALUES ('ten_channels', 'Channel Empire', 'Connect 10 channels to your account', 100, 'channels', 'count', 10, 30, true)
        ON CONFLICT (achievement_key) DO UPDATE SET
            name = 'Channel Empire',
            credit_reward = 100,
            requirement_value = 10
    """
    )

    op.execute(
        """
        UPDATE achievements
        SET requirement_value = 5,
            name = 'Channel Master',
            description = 'Connect 5 channels to your account',
            credit_reward = 50
        WHERE achievement_key = 'five_channels'
    """
    )

    op.execute("""DELETE FROM achievements WHERE achievement_key = 'max_channels'""")
    op.execute(
        """DELETE FROM achievements WHERE achievement_key IN ('upgrade_pro', 'upgrade_business')"""
    )
    op.execute(
        """DELETE FROM achievements WHERE achievement_key IN ('first_ai_use', 'ai_power_user', 'first_export')"""
    )

    op.execute(
        """UPDATE achievements SET credit_reward = 100 WHERE achievement_key = 'streak_30'"""
    )
    op.execute(
        """UPDATE achievements SET credit_reward = 500 WHERE achievement_key = 'streak_100'"""
    )

    op.execute("""UPDATE plans SET monthly_credits_cap = 100 WHERE name = 'free'""")
