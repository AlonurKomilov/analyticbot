"""Create credit system tables

Revision ID: 0039_credit_system_tables
Revises: 0038_add_user_suspension_fields
Create Date: 2025-12-05

Creates all tables needed for the credit system:
- user_credits: User credit balances and stats
- credit_transactions: Transaction history
- credit_packages: Purchasable credit packages
- credit_services: Services that cost credits
- achievements: Achievement definitions
- user_achievements: User's earned achievements
- user_referrals: Referral tracking
- marketplace_items: Marketplace products
- user_purchases: User's marketplace purchases
- marketplace_bundles: Bundle deals
- bundle_items: Items in bundles
- item_reviews: Product reviews
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0040_credit_system_tables"
down_revision = "0039_add_user_suspension_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================
    # Add credit columns to users table
    # ============================================
    op.add_column(
        "users",
        sa.Column("credit_balance", sa.Numeric(12, 2), server_default="0", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("referral_code", sa.String(20), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("referred_by_user_id", sa.BigInteger(), nullable=True),
    )

    # Add unique constraint for referral codes
    op.create_index(
        "ix_users_referral_code",
        "users",
        ["referral_code"],
        unique=True,
        postgresql_where=sa.text("referral_code IS NOT NULL"),
    )

    # ============================================
    # User Credits Table - Extended balance info
    # ============================================
    op.create_table(
        "user_credits",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("balance", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("lifetime_earned", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("lifetime_spent", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("daily_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_daily_reward_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_credits_user_id"),
    )
    op.create_index("ix_user_credits_user_id", "user_credits", ["user_id"])

    # ============================================
    # Credit Transactions Table
    # ============================================
    op.create_table(
        "credit_transactions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("balance_after", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "type", sa.String(50), nullable=False
        ),  # purchase, reward, spend, bonus, referral, adjustment
        sa.Column(
            "category", sa.String(50), nullable=True
        ),  # signup, daily, referral, purchase, admin, achievement
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column(
            "reference_id", sa.String(100), nullable=True
        ),  # External reference (payment ID, etc.)
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_credit_transactions_user_id", "credit_transactions", ["user_id"])
    op.create_index("ix_credit_transactions_type", "credit_transactions", ["type"])
    op.create_index("ix_credit_transactions_created_at", "credit_transactions", ["created_at"])
    op.create_index(
        "ix_credit_transactions_user_created",
        "credit_transactions",
        ["user_id", "created_at"],
    )

    # ============================================
    # Credit Packages Table - Purchasable bundles
    # ============================================
    op.create_table(
        "credit_packages",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False, unique=True),
        sa.Column("credits", sa.Numeric(12, 2), nullable=False),
        sa.Column("bonus_credits", sa.Numeric(12, 2), server_default="0", nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_popular", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("stripe_price_id", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_packages_slug", "credit_packages", ["slug"], unique=True)
    op.create_index("ix_credit_packages_active", "credit_packages", ["is_active"])

    # ============================================
    # Credit Services Table - Things to spend on
    # ============================================
    op.create_table(
        "credit_services",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("service_key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("credit_cost", sa.Numeric(10, 2), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),  # ai, export, feature, api
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("usage_limit_per_day", sa.Integer(), nullable=True),  # NULL = unlimited
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_credit_services_service_key",
        "credit_services",
        ["service_key"],
        unique=True,
    )
    op.create_index("ix_credit_services_category", "credit_services", ["category"])
    op.create_index("ix_credit_services_active", "credit_services", ["is_active"])

    # ============================================
    # Achievements Table - Achievement definitions
    # ============================================
    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("achievement_key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("credit_reward", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column(
            "category", sa.String(50), nullable=False
        ),  # account, channels, engagement, streaks, credits, referrals
        sa.Column("requirement_type", sa.String(50), nullable=True),  # streak, count, value
        sa.Column("requirement_value", sa.Integer(), nullable=True),  # e.g., 7 for 7-day streak
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_achievements_key", "achievements", ["achievement_key"], unique=True)
    op.create_index("ix_achievements_category", "achievements", ["category"])

    # ============================================
    # User Achievements Table - Earned achievements
    # ============================================
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("achievement_key", sa.String(50), nullable=False),
        sa.Column("achievement_name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("credits_awarded", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column(
            "achieved_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "achievement_key", name="uq_user_achievement"),
    )
    op.create_index("ix_user_achievements_user_id", "user_achievements", ["user_id"])
    op.create_index("ix_user_achievements_key", "user_achievements", ["achievement_key"])

    # ============================================
    # User Referrals Table - Referral tracking
    # ============================================
    op.create_table(
        "user_referrals",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("referrer_user_id", sa.BigInteger(), nullable=False),
        sa.Column("referred_user_id", sa.BigInteger(), nullable=False),
        sa.Column("referral_code", sa.String(20), nullable=False),
        sa.Column("credits_awarded", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column(
            "status", sa.String(20), server_default="pending", nullable=False
        ),  # pending, completed, expired
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["referrer_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["referred_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("referred_user_id", name="uq_referred_user"),
    )
    op.create_index("ix_user_referrals_referrer", "user_referrals", ["referrer_user_id"])
    op.create_index("ix_user_referrals_referred", "user_referrals", ["referred_user_id"])
    op.create_index("ix_user_referrals_status", "user_referrals", ["status"])

    # ============================================
    # Marketplace Items Table
    # ============================================
    op.create_table(
        "marketplace_items",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),  # ai_models, themes, widgets
        sa.Column("subcategory", sa.String(50), nullable=True),
        sa.Column("price_credits", sa.Integer(), nullable=False),
        sa.Column("is_premium", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_featured", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("preview_url", sa.String(500), nullable=True),
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("download_url", sa.String(500), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("download_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rating", sa.Numeric(3, 2), server_default="0", nullable=False),
        sa.Column("rating_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_marketplace_items_slug", "marketplace_items", ["slug"], unique=True)
    op.create_index("ix_marketplace_items_category", "marketplace_items", ["category"])
    op.create_index("ix_marketplace_items_featured", "marketplace_items", ["is_featured"])
    op.create_index("ix_marketplace_items_active", "marketplace_items", ["is_active"])

    # ============================================
    # User Purchases Table
    # ============================================
    op.create_table(
        "user_purchases",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("price_paid", sa.Integer(), nullable=False),
        sa.Column(
            "purchased_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),  # NULL = permanent
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["marketplace_items.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "item_id", name="uq_user_purchase"),
    )
    op.create_index("ix_user_purchases_user_id", "user_purchases", ["user_id"])
    op.create_index("ix_user_purchases_item_id", "user_purchases", ["item_id"])

    # ============================================
    # Marketplace Bundles Table
    # ============================================
    op.create_table(
        "marketplace_bundles",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_credits", sa.Integer(), nullable=False),
        sa.Column(
            "original_price", sa.Integer(), nullable=False
        ),  # Sum of items if bought separately
        sa.Column("discount_percent", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_featured", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "valid_days", sa.Integer(), server_default="365", nullable=False
        ),  # How long items last
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_marketplace_bundles_slug", "marketplace_bundles", ["slug"], unique=True)
    op.create_index("ix_marketplace_bundles_featured", "marketplace_bundles", ["is_featured"])

    # ============================================
    # Bundle Items Table - Links bundles to items
    # ============================================
    op.create_table(
        "bundle_items",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("bundle_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["bundle_id"], ["marketplace_bundles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["marketplace_items.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("bundle_id", "item_id", name="uq_bundle_item"),
    )

    # ============================================
    # Item Reviews Table
    # ============================================
    op.create_table(
        "item_reviews",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),  # 1-5
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column("is_verified_purchase", sa.Boolean(), server_default="false", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["marketplace_items.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "item_id", name="uq_user_item_review"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
    )
    op.create_index("ix_item_reviews_item_id", "item_reviews", ["item_id"])
    op.create_index("ix_item_reviews_user_id", "item_reviews", ["user_id"])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("item_reviews")
    op.drop_table("bundle_items")
    op.drop_table("marketplace_bundles")
    op.drop_table("user_purchases")
    op.drop_table("marketplace_items")
    op.drop_table("user_referrals")
    op.drop_table("user_achievements")
    op.drop_table("achievements")
    op.drop_table("credit_services")
    op.drop_table("credit_packages")
    op.drop_table("credit_transactions")
    op.drop_table("user_credits")

    # Drop indexes and columns from users table
    op.drop_index("ix_users_referral_code", table_name="users")
    op.drop_column("users", "referred_by_user_id")
    op.drop_column("users", "referral_code")
    op.drop_column("users", "credit_balance")
