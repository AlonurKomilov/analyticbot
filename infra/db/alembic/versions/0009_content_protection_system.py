"""Add content protection system tables and enhanced reporting

Revision ID: 0009_content_protection_system
Revises: 0008_create_superadmin_system
Create Date: 2025-01-27 10:45:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009_content_protection_system"
down_revision = "0008_create_superadmin_system"
branch_labels = None
depends_on = None


def upgrade():
    """Add content protection system and enhanced reporting tables."""
    # Create content_violations table
    op.create_table(
        "content_violations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.Column("violation_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("content_snippet", sa.Text(), nullable=True),
        sa.Column(
            "detected_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("reported_by", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, default="pending"),
        sa.Column("reviewed_by", sa.BigInteger(), nullable=True),
        sa.Column("reviewed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("action_taken", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create content_filters table
    op.create_table(
        "content_filters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("filter_type", sa.String(50), nullable=False),
        sa.Column("pattern", sa.Text(), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create whitelist_entries table
    op.create_table(
        "whitelist_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.String(50), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("added_by", sa.BigInteger(), nullable=False),
        sa.Column(
            "added_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create reporting_snapshots table
    op.create_table(
        "reporting_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("report_type", sa.String(50), nullable=False, default="daily"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("snapshot_date", "channel_id", "report_type"),
    )

    # Create content_analysis table
    op.create_table(
        "content_analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column(
            "analyzed_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(20), nullable=True),
        sa.Column("raw_output", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel_id", "message_id", "analysis_type"),
    )

    # Add new columns to existing tables
    op.add_column(
        "channels",
        sa.Column("protection_level", sa.String(20), nullable=False, server_default="standard"),
    )
    op.add_column(
        "channels",
        sa.Column("auto_moderation", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "channels",
        sa.Column("whitelist_enabled", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "channels", sa.Column("last_content_scan", sa.TIMESTAMP(timezone=True), nullable=True)
    )

    # Create indexes for performance
    op.create_index("ix_content_violations_channel_id", "content_violations", ["channel_id"])
    op.create_index(
        "ix_content_violations_violation_type", "content_violations", ["violation_type"]
    )
    op.create_index("ix_content_violations_severity", "content_violations", ["severity"])
    op.create_index("ix_content_violations_status", "content_violations", ["status"])
    op.create_index("ix_content_violations_detected_at", "content_violations", ["detected_at"])

    op.create_index("ix_content_filters_filter_type", "content_filters", ["filter_type"])
    op.create_index("ix_content_filters_is_active", "content_filters", ["is_active"])
    op.create_index("ix_content_filters_severity", "content_filters", ["severity"])

    op.create_index("ix_whitelist_entries_entry_type", "whitelist_entries", ["entry_type"])
    op.create_index("ix_whitelist_entries_is_active", "whitelist_entries", ["is_active"])
    op.create_index("ix_whitelist_entries_expires_at", "whitelist_entries", ["expires_at"])

    op.create_index("ix_reporting_snapshots_channel_id", "reporting_snapshots", ["channel_id"])
    op.create_index(
        "ix_reporting_snapshots_snapshot_date", "reporting_snapshots", ["snapshot_date"]
    )
    op.create_index("ix_reporting_snapshots_report_type", "reporting_snapshots", ["report_type"])

    op.create_index("ix_content_analysis_channel_id", "content_analysis", ["channel_id"])
    op.create_index("ix_content_analysis_analysis_type", "content_analysis", ["analysis_type"])
    op.create_index("ix_content_analysis_analyzed_at", "content_analysis", ["analyzed_at"])
    op.create_index(
        "ix_content_analysis_tags", "content_analysis", ["tags"], postgresql_using="gin"
    )

    op.create_index("ix_channels_protection_level", "channels", ["protection_level"])
    op.create_index("ix_channels_auto_moderation", "channels", ["auto_moderation"])
    op.create_index("ix_channels_last_content_scan", "channels", ["last_content_scan"])


def downgrade():
    """Remove content protection system and enhanced reporting tables."""
    # Drop indexes
    op.drop_index("ix_channels_last_content_scan", table_name="channels")
    op.drop_index("ix_channels_auto_moderation", table_name="channels")
    op.drop_index("ix_channels_protection_level", table_name="channels")

    op.drop_index("ix_content_analysis_tags", table_name="content_analysis")
    op.drop_index("ix_content_analysis_analyzed_at", table_name="content_analysis")
    op.drop_index("ix_content_analysis_analysis_type", table_name="content_analysis")
    op.drop_index("ix_content_analysis_channel_id", table_name="content_analysis")

    op.drop_index("ix_reporting_snapshots_report_type", table_name="reporting_snapshots")
    op.drop_index("ix_reporting_snapshots_snapshot_date", table_name="reporting_snapshots")
    op.drop_index("ix_reporting_snapshots_channel_id", table_name="reporting_snapshots")

    op.drop_index("ix_whitelist_entries_expires_at", table_name="whitelist_entries")
    op.drop_index("ix_whitelist_entries_is_active", table_name="whitelist_entries")
    op.drop_index("ix_whitelist_entries_entry_type", table_name="whitelist_entries")

    op.drop_index("ix_content_filters_severity", table_name="content_filters")
    op.drop_index("ix_content_filters_is_active", table_name="content_filters")
    op.drop_index("ix_content_filters_filter_type", table_name="content_filters")

    op.drop_index("ix_content_violations_detected_at", table_name="content_violations")
    op.drop_index("ix_content_violations_status", table_name="content_violations")
    op.drop_index("ix_content_violations_severity", table_name="content_violations")
    op.drop_index("ix_content_violations_violation_type", table_name="content_violations")
    op.drop_index("ix_content_violations_channel_id", table_name="content_violations")

    # Remove columns from existing tables
    op.drop_column("channels", "last_content_scan")
    op.drop_column("channels", "whitelist_enabled")
    op.drop_column("channels", "auto_moderation")
    op.drop_column("channels", "protection_level")

    # Drop tables
    op.drop_table("content_analysis")
    op.drop_table("reporting_snapshots")
    op.drop_table("whitelist_entries")
    op.drop_table("content_filters")
    op.drop_table("content_violations")
