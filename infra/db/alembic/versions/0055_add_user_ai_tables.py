"""Add user AI configuration tables

Revision ID: 0055
Revises: 0054
Create Date: 2025-12-21

Creates tables for User AI system:
- user_ai_config: Per-user AI configuration and tier
- user_ai_usage: Daily AI usage tracking
- user_ai_hourly_usage: Hourly usage for rate limiting
- user_ai_services: User's active AI marketplace services
- ai_request_log: Detailed request logging
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0055'
down_revision = '0054'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================================================
    # 1. user_ai_config - Per-user AI configuration
    # =========================================================================
    op.create_table(
        'user_ai_config',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('tier', sa.String(length=20), server_default='free', nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferred_model', sa.String(length=50), nullable=True),
        sa.Column('temperature', sa.Float(), server_default='0.7', nullable=False),
        sa.Column('enabled_features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('language', sa.String(length=10), server_default='en', nullable=False),
        sa.Column('response_style', sa.String(length=20), server_default='professional', nullable=False),
        sa.Column('auto_insights_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('auto_insights_frequency', sa.String(length=20), server_default='daily', nullable=False),
        sa.Column('data_retention_days', sa.Integer(), server_default='30', nullable=False),
        sa.Column('anonymize_data', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index('ix_user_ai_config_enabled', 'user_ai_config', ['enabled'])
    op.create_index('ix_user_ai_config_tier', 'user_ai_config', ['tier'])

    # =========================================================================
    # 2. user_ai_usage - Daily usage tracking
    # =========================================================================
    op.create_table(
        'user_ai_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('requests_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('tokens_used', sa.Integer(), server_default='0', nullable=False),
        sa.Column('features_used', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('estimated_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'usage_date', name='uq_user_ai_usage_user_date')
    )
    op.create_index('ix_user_ai_usage_date', 'user_ai_usage', ['usage_date'])
    op.create_index('ix_user_ai_usage_user_date', 'user_ai_usage', ['user_id', 'usage_date'])
    op.create_index('ix_user_ai_usage_user_id', 'user_ai_usage', ['user_id'])

    # =========================================================================
    # 3. user_ai_hourly_usage - Hourly usage for rate limiting
    # =========================================================================
    op.create_table(
        'user_ai_hourly_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('hour_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('requests_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'hour_timestamp', name='uq_user_ai_hourly_user_hour')
    )
    op.create_index('ix_user_ai_hourly_timestamp', 'user_ai_hourly_usage', ['hour_timestamp'])
    op.create_index('ix_user_ai_hourly_user_id', 'user_ai_hourly_usage', ['user_id'])

    # =========================================================================
    # 4. user_ai_services - User's active AI services
    # =========================================================================
    op.create_table(
        'user_ai_services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('service_key', sa.String(length=100), nullable=False),
        sa.Column('enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('activated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('usage_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'service_key', name='uq_user_ai_service_user_key')
    )
    op.create_index('ix_user_ai_service_enabled', 'user_ai_services', ['enabled'])
    op.create_index('ix_user_ai_service_expires', 'user_ai_services', ['expires_at'])
    op.create_index('ix_user_ai_service_key', 'user_ai_services', ['service_key'])
    op.create_index('ix_user_ai_service_user_id', 'user_ai_services', ['user_id'])

    # =========================================================================
    # 5. ai_request_log - Detailed request logging
    # =========================================================================
    op.create_table(
        'ai_request_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('request_type', sa.String(length=50), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('model_used', sa.String(length=50), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('completion_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_tokens', sa.Integer(), server_default='0', nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('estimated_cost', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_request_log_created_at', 'ai_request_log', ['created_at'])
    op.create_index('ix_ai_request_log_success', 'ai_request_log', ['success'])
    op.create_index('ix_ai_request_log_type', 'ai_request_log', ['request_type'])
    op.create_index('ix_ai_request_log_user_id', 'ai_request_log', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_ai_request_log_user_id', table_name='ai_request_log')
    op.drop_index('ix_ai_request_log_type', table_name='ai_request_log')
    op.drop_index('ix_ai_request_log_success', table_name='ai_request_log')
    op.drop_index('ix_ai_request_log_created_at', table_name='ai_request_log')
    op.drop_table('ai_request_log')
    
    op.drop_index('ix_user_ai_service_user_id', table_name='user_ai_services')
    op.drop_index('ix_user_ai_service_key', table_name='user_ai_services')
    op.drop_index('ix_user_ai_service_expires', table_name='user_ai_services')
    op.drop_index('ix_user_ai_service_enabled', table_name='user_ai_services')
    op.drop_table('user_ai_services')
    
    op.drop_index('ix_user_ai_hourly_user_id', table_name='user_ai_hourly_usage')
    op.drop_index('ix_user_ai_hourly_timestamp', table_name='user_ai_hourly_usage')
    op.drop_table('user_ai_hourly_usage')
    
    op.drop_index('ix_user_ai_usage_user_id', table_name='user_ai_usage')
    op.drop_index('ix_user_ai_usage_user_date', table_name='user_ai_usage')
    op.drop_index('ix_user_ai_usage_date', table_name='user_ai_usage')
    op.drop_table('user_ai_usage')
    
    op.drop_index('ix_user_ai_config_tier', table_name='user_ai_config')
    op.drop_index('ix_user_ai_config_enabled', table_name='user_ai_config')
    op.drop_table('user_ai_config')
