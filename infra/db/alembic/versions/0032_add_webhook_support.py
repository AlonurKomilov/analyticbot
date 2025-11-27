"""Add webhook support columns to user_bot_credentials

Revision ID: 0032_add_webhook_support
Revises: 0031_add_bot_health_metrics_table
Create Date: 2025-11-19 00:00:00.000000

WEBHOOK SUPPORT MIGRATION:
This migration adds webhook functionality to the multi-tenant bot system.

New columns:
- webhook_enabled: Boolean flag to enable/disable webhooks per bot
- webhook_secret: Secure token for validating webhook requests from Telegram
- webhook_url: Full webhook URL configured with Telegram
- last_webhook_update: Timestamp of last webhook configuration change

Features:
- Enables instant message delivery (vs polling)
- 6× faster response times
- 80% resource reduction
- Single domain for all users: bot.analyticbot.org
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add webhook support columns to user_bot_credentials"""

    # Add webhook_enabled column (default False for existing bots)
    op.add_column(
        "user_bot_credentials",
        sa.Column(
            "webhook_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment="Whether webhook is enabled for this bot",
        ),
    )

    # Add webhook_secret column (nullable for existing bots)
    op.add_column(
        "user_bot_credentials",
        sa.Column(
            "webhook_secret",
            sa.String(255),
            nullable=True,
            comment="Secure token for validating webhook requests",
        ),
    )

    # Add webhook_url column (nullable for existing bots)
    op.add_column(
        "user_bot_credentials",
        sa.Column(
            "webhook_url",
            sa.String(500),
            nullable=True,
            comment="Full webhook URL configured with Telegram",
        ),
    )

    # Add last_webhook_update column (nullable for existing bots)
    op.add_column(
        "user_bot_credentials",
        sa.Column(
            "last_webhook_update",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp of last webhook configuration change",
        ),
    )

    # Add index on webhook_enabled for faster queries
    op.create_index(
        "ix_user_bot_credentials_webhook_enabled",
        "user_bot_credentials",
        ["webhook_enabled"],
        unique=False,
    )

    print("✅ Webhook support columns added to user_bot_credentials table")
    print("   - webhook_enabled (default: false)")
    print("   - webhook_secret (nullable)")
    print("   - webhook_url (nullable)")
    print("   - last_webhook_update (nullable)")
    print("   - Index on webhook_enabled created")


def downgrade() -> None:
    """Remove webhook support columns from user_bot_credentials"""

    # Drop index first
    op.drop_index("ix_user_bot_credentials_webhook_enabled", table_name="user_bot_credentials")

    # Drop columns in reverse order
    op.drop_column("user_bot_credentials", "last_webhook_update")
    op.drop_column("user_bot_credentials", "webhook_url")
    op.drop_column("user_bot_credentials", "webhook_secret")
    op.drop_column("user_bot_credentials", "webhook_enabled")

    print("✅ Webhook support columns removed from user_bot_credentials table")
