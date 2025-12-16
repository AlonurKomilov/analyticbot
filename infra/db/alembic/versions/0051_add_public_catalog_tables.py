"""
0051_add_public_catalog_tables

Creates tables for the public analytics catalog:
- channel_categories: Category taxonomy for public channels
- public_channel_catalog: Public channel directory
- channel_stats_cache: Database backup for Redis cache

Revision ID: 0051_public_catalog
Revises: 0050_rename_categories
Create Date: 2025-12-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic
revision = "0051_public_catalog"
down_revision = "0050_rename_categories"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create public catalog tables"""
    
    # 1. Channel Categories Table
    op.create_table(
        "channel_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("channel_categories.id"), nullable=True),
        sa.Column("sort_order", sa.Integer(), default=0, nullable=False),
        sa.Column("channel_count", sa.Integer(), default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Index for slug lookups
    op.create_index("idx_channel_categories_slug", "channel_categories", ["slug"])
    op.create_index("idx_channel_categories_parent", "channel_categories", ["parent_id"])
    
    # 2. Public Channel Catalog Table
    op.create_table(
        "public_channel_catalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), unique=True, nullable=False),
        sa.Column("username", sa.String(100), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("channel_categories.id"), nullable=True),
        sa.Column("country_code", sa.String(2), nullable=True),
        sa.Column("language_code", sa.String(5), nullable=True),
        sa.Column("is_featured", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_verified", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("added_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("added_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(), nullable=True),
        sa.Column("metadata", JSONB(), default={}, nullable=False),
    )
    
    # Indexes for public catalog
    op.create_index("idx_public_catalog_telegram_id", "public_channel_catalog", ["telegram_id"])
    op.create_index("idx_public_catalog_username", "public_channel_catalog", ["username"])
    op.create_index("idx_public_catalog_category", "public_channel_catalog", ["category_id"])
    op.create_index("idx_public_catalog_featured", "public_channel_catalog", ["is_featured"], postgresql_where=sa.text("is_featured = TRUE"))
    op.create_index("idx_public_catalog_active", "public_channel_catalog", ["is_active"], postgresql_where=sa.text("is_active = TRUE"))
    
    # 3. Channel Stats Cache Table (Database backup for Redis)
    op.create_table(
        "channel_stats_cache",
        sa.Column("telegram_id", sa.BigInteger(), primary_key=True),
        sa.Column("subscriber_count", sa.Integer(), nullable=True),
        sa.Column("avg_views", sa.Integer(), nullable=True),
        sa.Column("avg_reactions", sa.Integer(), nullable=True),
        sa.Column("avg_comments", sa.Integer(), nullable=True),
        sa.Column("posts_per_day", sa.Numeric(5, 2), nullable=True),
        sa.Column("growth_rate", sa.Numeric(5, 2), nullable=True),  # % change in 30 days
        sa.Column("last_post_at", sa.DateTime(), nullable=True),
        sa.Column("cached_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    """Drop public catalog tables"""
    op.drop_table("channel_stats_cache")
    op.drop_table("public_channel_catalog")
    op.drop_table("channel_categories")
