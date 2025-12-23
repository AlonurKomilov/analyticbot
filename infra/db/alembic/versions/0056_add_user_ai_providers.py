"""
Add user_ai_providers table for multi-provider AI support

Revision ID: 0056_add_user_ai_providers
Revises: 0055_add_user_ai_tables
Create Date: 2024-12-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0056_add_user_ai_providers'
down_revision = '0055'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add user_ai_providers table for storing user's AI provider API keys.
    
    Enables users to bring their own API keys for:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic Claude (Claude 3.5, Opus)
    - Google Gemini (Gemini Pro, Flash)
    - xAI Grok
    - And more...
    """
    
    # Create user_ai_providers table
    op.create_table(
        'user_ai_providers',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False, comment='Provider: openai, claude, gemini, grok, etc.'),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False, comment='Encrypted API key using Fernet'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false', comment='User\'s default provider'),
        sa.Column('model_preference', sa.String(length=100), nullable=True, comment='Preferred model: gpt-4-turbo, claude-3-opus, etc.'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Provider-specific config'),
        sa.Column('monthly_budget_usd', sa.Numeric(precision=10, scale=2), nullable=True, comment='Optional monthly spending limit'),
        sa.Column('current_month_spent_usd', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'provider_name', name='uq_user_provider'),
    )
    
    # Create indices for fast lookups
    op.create_index('ix_user_ai_providers_user_id', 'user_ai_providers', ['user_id'])
    op.create_index('ix_user_ai_providers_active', 'user_ai_providers', ['user_id', 'is_active'])
    op.create_index('ix_user_ai_providers_default', 'user_ai_providers', ['user_id', 'is_default'])
    
    # Create spending tracking table
    op.create_table(
        'user_ai_spending',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False),
        sa.Column('month', sa.Date(), nullable=False, comment='First day of month (YYYY-MM-01)'),
        sa.Column('total_cost_usd', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tokens_used', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'provider_name', 'month', name='uq_user_provider_month'),
    )
    
    op.create_index('ix_user_ai_spending_user_id', 'user_ai_spending', ['user_id'])
    op.create_index('ix_user_ai_spending_month', 'user_ai_spending', ['month'])
    
    # Add default_provider column to user_ai_config
    op.add_column(
        'user_ai_config',
        sa.Column(
            'default_provider',
            sa.String(length=50),
            nullable=False,
            server_default='system',
            comment='system = use platform keys, or provider name for user keys'
        )
    )
    
    print("✅ Created user_ai_providers table for multi-provider support")
    print("✅ Created user_ai_spending table for budget tracking")
    print("✅ Added default_provider to user_ai_config")


def downgrade() -> None:
    """Remove multi-provider tables."""
    op.drop_column('user_ai_config', 'default_provider')
    op.drop_index('ix_user_ai_spending_month', table_name='user_ai_spending')
    op.drop_index('ix_user_ai_spending_user_id', table_name='user_ai_spending')
    op.drop_table('user_ai_spending')
    op.drop_index('ix_user_ai_providers_default', table_name='user_ai_providers')
    op.drop_index('ix_user_ai_providers_active', table_name='user_ai_providers')
    op.drop_index('ix_user_ai_providers_user_id', table_name='user_ai_providers')
    op.drop_table('user_ai_providers')
    
    print("✅ Removed multi-provider tables")
