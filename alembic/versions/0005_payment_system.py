"""Payment System Implementation

Revision ID: 0005
Revises: 0004
Create Date: 2025-08-24 12:00:00.000000

"""

from typing import Sequence, Union
from decimal import Decimal
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0005_payment_system"
down_revision: Union[str, Sequence[str], None] = "0004_unique_sent_posts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add payment system tables and extend existing tables."""
    
    # Add pricing columns to existing plans table
    op.add_column('plans', sa.Column('price_monthly', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('plans', sa.Column('price_yearly', sa.DECIMAL(10, 2), nullable=True))
    op.add_column('plans', sa.Column('currency', sa.String(3), default='USD', nullable=False))
    op.add_column('plans', sa.Column('is_active', sa.Boolean(), default=True, nullable=False))
    
    # Payment methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),  # stripe, payme, click
        sa.Column('provider_method_id', sa.String(255), nullable=False),  # External ID
        sa.Column('method_type', sa.String(50), nullable=False),  # card, bank_account
        sa.Column('last_four', sa.String(4), nullable=True),
        sa.Column('brand', sa.String(50), nullable=True),  # visa, mastercard
        sa.Column('expires_at', sa.Date(), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.Index('ix_payment_methods_user_id', 'user_id'),
        sa.Index('ix_payment_methods_provider', 'provider'),
    )
    
    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('payment_method_id', sa.String(36), nullable=True),
        sa.Column('provider_subscription_id', sa.String(255), nullable=True),  # External ID
        sa.Column('status', sa.String(50), nullable=False),  # active, canceled, past_due, etc.
        sa.Column('billing_cycle', sa.String(20), nullable=False),  # monthly, yearly
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), default=False, nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ondelete='SET NULL'),
        sa.Index('ix_subscriptions_user_id', 'user_id'),
        sa.Index('ix_subscriptions_status', 'status'),
        sa.Index('ix_subscriptions_current_period', 'current_period_start', 'current_period_end'),
        sa.CheckConstraint("status IN ('active', 'canceled', 'past_due', 'unpaid', 'trialing', 'incomplete')"),
        sa.CheckConstraint("billing_cycle IN ('monthly', 'yearly')"),
    )
    
    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('subscription_id', sa.String(36), nullable=True),
        sa.Column('payment_method_id', sa.String(36), nullable=True),
        sa.Column('provider', sa.String(50), nullable=False),  # stripe, payme, click
        sa.Column('provider_payment_id', sa.String(255), nullable=True),  # External ID
        sa.Column('idempotency_key', sa.String(255), nullable=False, unique=True),
        sa.Column('amount', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),  # pending, succeeded, failed, canceled
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('failure_code', sa.String(100), nullable=True),
        sa.Column('failure_message', sa.Text(), nullable=True),
        sa.Column('webhook_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ondelete='SET NULL'),
        sa.Index('ix_payments_user_id', 'user_id'),
        sa.Index('ix_payments_status', 'status'),
        sa.Index('ix_payments_provider', 'provider'),
        sa.Index('ix_payments_created_at', 'created_at'),
        sa.Index('ix_payments_idempotency_key', 'idempotency_key'),
        sa.CheckConstraint("status IN ('pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded')"),
    )
    
    # Webhook events table for audit and replay
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('provider_event_id', sa.String(255), nullable=True),
        sa.Column('object_id', sa.String(255), nullable=True),  # payment_id, subscription_id, etc.
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('signature', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('processed', sa.Boolean(), default=False, nullable=False),
        sa.Column('retry_count', sa.Integer(), default=0, nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Index('ix_webhook_events_provider', 'provider'),
        sa.Index('ix_webhook_events_event_type', 'event_type'),
        sa.Index('ix_webhook_events_processed', 'processed'),
        sa.Index('ix_webhook_events_created_at', 'created_at'),
    )
    
    # Update plans with default pricing
    op.execute("""
        UPDATE plans SET 
            price_monthly = CASE 
                WHEN name = 'free' THEN 0.00
                WHEN name = 'pro' THEN 9.99  
                WHEN name = 'business' THEN 29.99
                ELSE 0.00
            END,
            price_yearly = CASE
                WHEN name = 'free' THEN 0.00
                WHEN name = 'pro' THEN 99.99
                WHEN name = 'business' THEN 299.99
                ELSE 0.00
            END,
            currency = 'USD',
            is_active = true
    """)


def downgrade() -> None:
    """Remove payment system tables and columns."""
    
    # Drop tables in reverse order due to foreign keys
    op.drop_table('webhook_events')
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('payment_methods')
    
    # Remove columns from plans table
    op.drop_column('plans', 'price_monthly')
    op.drop_column('plans', 'price_yearly')
    op.drop_column('plans', 'currency')
    op.drop_column('plans', 'is_active')
