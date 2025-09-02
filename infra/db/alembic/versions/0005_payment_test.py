"""Simple Payment System Test - SQLite Compatible

Revision ID: 0005_payment_test
Revises: 0004_unique_sent_posts
Create Date: 2025-08-24 12:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_payment_test"
down_revision: str | Sequence[str] | None = "0004_unique_sent_posts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Check if pricing columns already exist, skip if they do
    try:
        op.add_column("plans", sa.Column("price_monthly", sa.REAL, nullable=True))
    except Exception:
        pass  # Column already exists

    try:
        op.add_column("plans", sa.Column("price_yearly", sa.REAL, nullable=True))
    except Exception:
        pass  # Column already exists

    # Update existing plans with pricing (simplified for testing)
    op.execute(
        """
        UPDATE plans SET 
            price_monthly = CASE 
                WHEN name = 'Free' THEN 0.00
                WHEN name = 'Starter' THEN 9.99
                WHEN name = 'Pro' THEN 29.99
                WHEN name = 'Enterprise' THEN 99.99
                ELSE 0.00
            END,
            price_yearly = CASE 
                WHEN name = 'Free' THEN 0.00
                WHEN name = 'Starter' THEN 99.99
                WHEN name = 'Pro' THEN 299.99
                WHEN name = 'Enterprise' THEN 999.99
                ELSE 0.00
            END
    """
    )

    # Payment Methods table
    op.create_table(
        "payment_methods",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_method_id", sa.String(255), nullable=False),
        sa.Column("method_type", sa.String(50), nullable=False),
        sa.Column("last_four", sa.String(4), nullable=True),
        sa.Column("brand", sa.String(50), nullable=True),
        sa.Column("expires_at", sa.Date(), nullable=True),
        sa.Column("is_default", sa.Boolean(), default=False, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("metadata_json", sa.TEXT(), nullable=True),  # Store JSON as TEXT
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Subscriptions table
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("payment_method_id", sa.String(36), nullable=True),
        sa.Column("provider_subscription_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("billing_cycle", sa.String(20), nullable=False),
        sa.Column("amount", sa.REAL, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("trial_ends_at", sa.DateTime(), nullable=True),
        sa.Column("current_period_start", sa.DateTime(), nullable=False),
        sa.Column("current_period_end", sa.DateTime(), nullable=False),
        sa.Column("canceled_at", sa.DateTime(), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), default=False, nullable=False),
        sa.Column("metadata_json", sa.TEXT(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"], ondelete="SET NULL"),
    )

    # Payments table
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("subscription_id", sa.String(36), nullable=True),
        sa.Column("payment_method_id", sa.String(36), nullable=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_payment_id", sa.String(255), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True),
        sa.Column("amount", sa.REAL, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("description", sa.TEXT(), nullable=True),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.Column("failure_message", sa.TEXT(), nullable=True),
        sa.Column("webhook_verified", sa.Boolean(), default=False, nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("metadata_json", sa.TEXT(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_method_id"], ["payment_methods.id"], ondelete="SET NULL"),
    )

    # Webhook Events table
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("provider_event_id", sa.String(255), nullable=True),
        sa.Column("object_id", sa.String(255), nullable=True),
        sa.Column("payload_json", sa.TEXT(), nullable=False),
        sa.Column("signature", sa.String(255), nullable=True),
        sa.Column("processed", sa.Boolean(), default=False, nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("retry_count", sa.Integer(), default=0, nullable=False),
        sa.Column("last_error", sa.TEXT(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("datetime('now')"),
            nullable=False,
        ),
    )

    # Create indexes for better performance
    op.create_index("ix_payment_methods_user_id", "payment_methods", ["user_id"])
    op.create_index("ix_payment_methods_provider", "payment_methods", ["provider"])
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_idempotency_key", "payments", ["idempotency_key"])
    op.create_index("ix_webhook_events_provider", "webhook_events", ["provider"])
    op.create_index("ix_webhook_events_processed", "webhook_events", ["processed"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_webhook_events_processed")
    op.drop_index("ix_webhook_events_provider")
    op.drop_index("ix_payments_idempotency_key")
    op.drop_index("ix_payments_status")
    op.drop_index("ix_payments_user_id")
    op.drop_index("ix_subscriptions_status")
    op.drop_index("ix_subscriptions_user_id")
    op.drop_index("ix_payment_methods_provider")
    op.drop_index("ix_payment_methods_user_id")

    # Drop tables
    op.drop_table("webhook_events")
    op.drop_table("payments")
    op.drop_table("subscriptions")
    op.drop_table("payment_methods")

    # Remove pricing columns
    op.drop_column("plans", "price_yearly")
    op.drop_column("plans", "price_monthly")
