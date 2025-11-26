"""Fix foreign key ON DELETE consistency

Revision ID: 0026_fix_fk_consistency
Revises: 0025_add_channel_mtproto_settings
Create Date: 2025-11-26 12:00:00.000000

This migration standardizes ON DELETE behavior across all foreign keys:

BUSINESS RULES:
1. Users deletion: RESTRICT (prevent accidental data loss)
   - Exception: Audit tables CASCADE (logs should be deleted with user)

2. Channels deletion: CASCADE (clean up all related data)
   - scheduled_posts, sent_posts, channel_mtproto_settings, etc.

3. Plans deletion: SET NULL (preserve user accounts)

FIXES:
- scheduled_posts.channel_id: RESTRICT → CASCADE
  (When channel deleted, scheduled posts should be deleted)

This ensures clean data deletion and prevents orphaned records.
"""

from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade():
    """Standardize foreign key ON DELETE behavior"""

    # ========================================================================
    # FIX #1: scheduled_posts.channel_id should CASCADE
    # ========================================================================
    # Problem: Currently RESTRICT - prevents channel deletion if posts exist
    # Solution: Change to CASCADE - delete scheduled posts when channel deleted

    op.execute("""
        -- Drop existing constraint
        ALTER TABLE scheduled_posts
        DROP CONSTRAINT IF EXISTS scheduled_posts_channel_id_fkey;

        -- Recreate with CASCADE
        ALTER TABLE scheduled_posts
        ADD CONSTRAINT scheduled_posts_channel_id_fkey
            FOREIGN KEY (channel_id)
            REFERENCES channels(id)
            ON DELETE CASCADE;
    """)

    # ========================================================================
    # Verification: Document current FK patterns (no changes needed)
    # ========================================================================

    # Users → RESTRICT (correct - prevents accidental user deletion)
    # ✅ channels.user_id → users.id (RESTRICT)
    # ✅ payment_methods.user_id → users.id (RESTRICT)
    # ✅ payments.user_id → users.id (RESTRICT)
    # ✅ scheduled_posts.user_id → users.id (RESTRICT)
    # ✅ subscriptions.user_id → users.id (RESTRICT)

    # Users → CASCADE (correct - audit/temp data deleted with user)
    # ✅ admin_bot_actions.target_user_id → users.id (CASCADE)
    # ✅ channel_mtproto_settings.user_id → users.id (CASCADE)
    # ✅ mtproto_audit_log.user_id → users.id (CASCADE)
    # ✅ telegram_media.user_id → users.id (CASCADE)
    # ✅ user_storage_channels.user_id → users.id (CASCADE)

    # Channels → CASCADE (correct - child data deleted with channel)
    # ✅ channel_mtproto_settings.channel_id → channels.id (CASCADE)
    # ✅ sent_posts.channel_id → channels.id (CASCADE)
    # ✅ scheduled_posts.channel_id → channels.id (NOW FIXED)

    # Other tables → SET NULL (correct - preserve records)
    # ✅ users.plan_id → plans.id (SET NULL)
    # ✅ payments.payment_method_id → payment_methods.id (SET NULL)
    # ✅ payments.subscription_id → subscriptions.id (SET NULL)
    # ✅ subscriptions.payment_method_id → payment_methods.id (SET NULL)

    # Composite FK
    # ✅ post_metrics → posts (CASCADE)
    # ✅ sent_posts.scheduled_post_id → scheduled_posts.id (CASCADE)
    # ✅ deliveries.scheduled_post_id → scheduled_posts.id (CASCADE)


def downgrade():
    """Revert foreign key changes"""

    # Revert scheduled_posts.channel_id to RESTRICT
    op.execute("""
        ALTER TABLE scheduled_posts
        DROP CONSTRAINT IF EXISTS scheduled_posts_channel_id_fkey;

        ALTER TABLE scheduled_posts
        ADD CONSTRAINT scheduled_posts_channel_id_fkey
            FOREIGN KEY (channel_id)
            REFERENCES channels(id)
            ON DELETE RESTRICT;
    """)
