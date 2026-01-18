"""Phase 3: Add rate limit configuration tables

Revision ID: 0058
Revises: 0057
Create Date: 2025-12-24 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0058"
down_revision = "0057"
branch_labels = None
depends_on = None


def upgrade():
    """
    Create tables for Phase 3 rate limit system:
    - rate_limit_configs: Configuration storage
    - rate_limit_audit_log: Full audit trail
    - rate_limit_stats: Usage statistics
    """

    # === rate_limit_configs table ===
    op.create_table(
        "rate_limit_configs",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column(
            "service_key",
            sa.String(length=100),
            nullable=False,
            unique=True,
            comment='Service identifier (e.g., "bot_operations", "auth_login")',
        ),
        sa.Column(
            "service_name",
            sa.String(length=200),
            nullable=False,
            comment='Human-readable service name (e.g., "Bot Operations")',
        ),
        sa.Column(
            "limit_value",
            sa.Integer(),
            nullable=False,
            comment="Maximum requests allowed in the period",
        ),
        sa.Column(
            "period",
            sa.String(length=20),
            nullable=False,
            comment='Time period: "minute", "hour", "day"',
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="Whether rate limiting is enabled for this service",
        ),
        sa.Column(
            "description",
            sa.Text(),
            comment="Detailed description of what this service does",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "created_by",
            sa.String(length=100),
            comment="Admin user ID who created this config",
        ),
        sa.Column(
            "updated_by",
            sa.String(length=100),
            comment="Admin user ID who last updated this config",
        ),
    )

    # Indexes for rate_limit_configs
    op.create_index("idx_rate_limit_configs_service_key", "rate_limit_configs", ["service_key"])
    op.create_index("idx_rate_limit_configs_enabled", "rate_limit_configs", ["enabled"])

    # === rate_limit_audit_log table ===
    op.create_table(
        "rate_limit_audit_log",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column(
            "service_key",
            sa.String(length=100),
            nullable=False,
            comment="Service that was modified",
        ),
        sa.Column(
            "action",
            sa.String(length=50),
            nullable=False,
            comment='Action performed: "create", "update", "delete", "reset", "enable", "disable"',
        ),
        sa.Column("old_limit", sa.Integer(), comment="Previous limit value"),
        sa.Column("new_limit", sa.Integer(), comment="New limit value"),
        sa.Column("old_period", sa.String(length=20), comment="Previous period"),
        sa.Column("new_period", sa.String(length=20), comment="New period"),
        sa.Column("old_enabled", sa.Boolean(), comment="Previous enabled state"),
        sa.Column("new_enabled", sa.Boolean(), comment="New enabled state"),
        sa.Column(
            "changed_by",
            sa.String(length=100),
            nullable=False,
            comment="Admin user ID who made the change",
        ),
        sa.Column("changed_by_username", sa.String(length=200), comment="Admin username"),
        sa.Column("changed_by_ip", sa.String(length=50), comment="IP address of the admin"),
        sa.Column("change_reason", sa.Text(), comment="Optional explanation for the change"),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            comment="Additional metadata (request info, etc.)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Indexes for rate_limit_audit_log
    op.create_index("idx_rate_limit_audit_service", "rate_limit_audit_log", ["service_key"])
    op.create_index("idx_rate_limit_audit_action", "rate_limit_audit_log", ["action"])
    op.create_index("idx_rate_limit_audit_user", "rate_limit_audit_log", ["changed_by"])
    op.create_index("idx_rate_limit_audit_created", "rate_limit_audit_log", ["created_at"])

    # === rate_limit_stats table ===
    op.create_table(
        "rate_limit_stats",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column(
            "service_key",
            sa.String(length=100),
            nullable=False,
            comment="Service being tracked",
        ),
        sa.Column(
            "ip_address",
            sa.String(length=50),
            nullable=False,
            comment="IP address making requests",
        ),
        sa.Column(
            "requests_made",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Total requests made in this window",
        ),
        sa.Column(
            "requests_blocked",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Requests blocked due to rate limit",
        ),
        sa.Column(
            "last_request_at",
            sa.DateTime(timezone=True),
            comment="When the last request was made",
        ),
        sa.Column(
            "last_blocked_at",
            sa.DateTime(timezone=True),
            comment="When the last request was blocked",
        ),
        sa.Column(
            "window_start",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Start of the time window",
        ),
        sa.Column(
            "window_end",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="End of the time window",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    # Indexes for rate_limit_stats
    op.create_index("idx_rate_limit_stats_service", "rate_limit_stats", ["service_key"])
    op.create_index("idx_rate_limit_stats_ip", "rate_limit_stats", ["ip_address"])
    op.create_index(
        "idx_rate_limit_stats_window",
        "rate_limit_stats",
        ["service_key", "window_start", "window_end"],
    )
    op.create_index(
        "idx_rate_limit_stats_ip_service",
        "rate_limit_stats",
        ["ip_address", "service_key"],
    )

    # Unique constraint for stats (one record per service/IP/window combination)
    op.create_unique_constraint(
        "uq_rate_limit_stats_service_ip_window",
        "rate_limit_stats",
        ["service_key", "ip_address", "window_start"],
    )

    # === Seed default configurations ===
    # Insert default rate limit configurations
    op.execute(
        """
        INSERT INTO rate_limit_configs (service_key, service_name, limit_value, period, enabled, description, created_by)
        VALUES
            ('bot_creation', 'Bot Creation', 5, 'hour', true, 'Rate limit for creating new bots (prevents spam)', 'system'),
            ('bot_operations', 'Bot Operations', 300, 'minute', true, 'Rate limit for general bot operations', 'system'),
            ('admin_operations', 'Admin Operations', 30, 'minute', true, 'Rate limit for admin panel operations', 'system'),
            ('auth_login', 'Authentication Login', 30, 'minute', true, 'Rate limit for login attempts', 'system'),
            ('auth_register', 'Authentication Register', 3, 'hour', true, 'Rate limit for new user registrations', 'system'),
            ('public_read', 'Public Read', 500, 'minute', true, 'Rate limit for public read-only endpoints', 'system'),
            ('webhook', 'Webhook', 1000, 'minute', true, 'Rate limit for webhook endpoints (very high limit)', 'system'),
            ('analytics', 'Analytics', 60, 'minute', true, 'Rate limit for analytics endpoints', 'system')
        ON CONFLICT (service_key) DO NOTHING;
    """
    )

    print("✅ Phase 3 rate limit tables created with default configurations")


def downgrade():
    """Drop all Phase 3 rate limit tables"""

    op.drop_table("rate_limit_stats")
    op.drop_table("rate_limit_audit_log")
    op.drop_table("rate_limit_configs")

    print("✅ Phase 3 rate limit tables dropped")
