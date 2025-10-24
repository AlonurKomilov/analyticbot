"""
Add Telegram authentication fields to users table

Revision ID: telegram_auth_2025_10_22
Revises: previous_revision
Create Date: 2025-10-22

Adds fields needed for "Sign in with Telegram" functionality:
- telegram_id: User's Telegram ID (unique)
- telegram_username: Telegram username (optional)
- telegram_photo_url: Profile photo URL
- telegram_verified: Whether Telegram account is verified
- auth_provider: Updated to support 'telegram' option

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'telegram_auth_2025_10_22'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add Telegram authentication fields to users table.
    """
    
    # Add telegram_id column (BIGINT for Telegram's int64 user IDs)
    op.add_column(
        'users',
        sa.Column(
            'telegram_id',
            sa.BigInteger(),
            nullable=True,
            unique=True,
            comment='Telegram user ID for OAuth authentication'
        )
    )
    
    # Add telegram_username column
    op.add_column(
        'users',
        sa.Column(
            'telegram_username',
            sa.String(255),
            nullable=True,
            comment='Telegram username (without @)'
        )
    )
    
    # Add telegram_photo_url column
    op.add_column(
        'users',
        sa.Column(
            'telegram_photo_url',
            sa.Text(),
            nullable=True,
            comment='URL to Telegram profile photo'
        )
    )
    
    # Add telegram_verified column
    op.add_column(
        'users',
        sa.Column(
            'telegram_verified',
            sa.Boolean(),
            default=False,
            nullable=False,
            server_default='false',
            comment='Whether Telegram account is verified'
        )
    )
    
    # Create index on telegram_id for faster lookups
    op.create_index(
        'idx_users_telegram_id',
        'users',
        ['telegram_id'],
        unique=True
    )
    
    # Create index on telegram_username for searches
    op.create_index(
        'idx_users_telegram_username',
        'users',
        ['telegram_username'],
        unique=False
    )
    
    print("✅ Telegram authentication fields added successfully")


def downgrade() -> None:
    """
    Remove Telegram authentication fields from users table.
    """
    
    # Drop indexes
    op.drop_index('idx_users_telegram_username', table_name='users')
    op.drop_index('idx_users_telegram_id', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'telegram_verified')
    op.drop_column('users', 'telegram_photo_url')
    op.drop_column('users', 'telegram_username')
    op.drop_column('users', 'telegram_id')
    
    print("✅ Telegram authentication fields removed successfully")
