"""Add MTProto interval configuration to plans and users.

Revision ID: 0045_mtproto_interval
Revises: 0044_unique_phone_and_bot_constraints
Create Date: 2025-12-10 07:30:00.000000

This migration adds configurable MTProto collection intervals:
- Plans get base_interval and min_interval settings
- Users can have an interval override (for credit-based boosts)
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0045_mtproto_interval"
down_revision = "0044_unique_phone_and_bot_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add MTProto interval columns to plans and users tables."""

    # Add MTProto interval columns to plans table
    op.add_column(
        "plans",
        sa.Column(
            "mtproto_interval_minutes",
            sa.Integer(),
            nullable=False,
            server_default="60",
            comment="Base MTProto collection interval in minutes for this plan",
        ),
    )
    op.add_column(
        "plans",
        sa.Column(
            "min_mtproto_interval_minutes",
            sa.Integer(),
            nullable=False,
            server_default="30",
            comment="Minimum allowed interval (can be boosted with credits)",
        ),
    )
    op.add_column(
        "plans",
        sa.Column(
            "interval_boost_credits",
            sa.Integer(),
            nullable=False,
            server_default="5",
            comment="Credits required to boost interval by one step",
        ),
    )
    op.add_column(
        "plans",
        sa.Column(
            "interval_boost_minutes",
            sa.Integer(),
            nullable=False,
            server_default="10",
            comment="Minutes reduced per interval boost",
        ),
    )

    # Add interval override to users table (for credit-based boosts)
    op.add_column(
        "users",
        sa.Column(
            "mtproto_interval_override",
            sa.Integer(),
            nullable=True,
            comment="User's current MTProto interval override (if boosted)",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "mtproto_interval_boost_expires",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When the interval boost expires",
        ),
    )

    # Update existing plans with appropriate intervals
    # Free: 60 min base, can boost to 30 min
    # Pro: 20 min base, can boost to 10 min
    # Business: 10 min base, can boost to 5 min
    op.execute(
        """
        UPDATE plans SET
            mtproto_interval_minutes = 60,
            min_mtproto_interval_minutes = 30,
            interval_boost_credits = 5,
            interval_boost_minutes = 10
        WHERE name = 'free';
    """
    )

    op.execute(
        """
        UPDATE plans SET
            mtproto_interval_minutes = 20,
            min_mtproto_interval_minutes = 10,
            interval_boost_credits = 5,
            interval_boost_minutes = 5
        WHERE name = 'pro';
    """
    )

    op.execute(
        """
        UPDATE plans SET
            mtproto_interval_minutes = 10,
            min_mtproto_interval_minutes = 5,
            interval_boost_credits = 10,
            interval_boost_minutes = 2
        WHERE name = 'business';
    """
    )

    # Add index for efficient interval lookups
    op.create_index(
        "idx_users_mtproto_interval",
        "users",
        ["mtproto_interval_override"],
        postgresql_where=sa.text("mtproto_interval_override IS NOT NULL"),
    )


def downgrade() -> None:
    """Remove MTProto interval columns."""

    # Drop index
    op.drop_index("idx_users_mtproto_interval", table_name="users")

    # Drop user columns
    op.drop_column("users", "mtproto_interval_boost_expires")
    op.drop_column("users", "mtproto_interval_override")

    # Drop plan columns
    op.drop_column("plans", "interval_boost_minutes")
    op.drop_column("plans", "interval_boost_credits")
    op.drop_column("plans", "min_mtproto_interval_minutes")
    op.drop_column("plans", "mtproto_interval_minutes")
