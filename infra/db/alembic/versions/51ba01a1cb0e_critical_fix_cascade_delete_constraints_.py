"""CRITICAL: Fix CASCADE DELETE constraints to prevent data loss

Revision ID: 51ba01a1cb0e
Revises: 1655f4348dad
Create Date: 2025-09-17 07:27:38.151610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51ba01a1cb0e'
down_revision: Union[str, Sequence[str], None] = '1655f4348dad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix dangerous CASCADE DELETE constraints to prevent accidental data loss."""
    
    # CRITICAL FIX: Replace CASCADE DELETE with RESTRICT to protect user data
    
    # 1. Fix channels table - prevent user deletion from destroying all channels
    op.execute("""
        ALTER TABLE channels 
        DROP CONSTRAINT IF EXISTS channels_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE channels 
        ADD CONSTRAINT channels_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
    """)
    
    # 2. Fix scheduled_posts table - prevent channel deletion from destroying posts
    op.execute("""
        ALTER TABLE scheduled_posts 
        DROP CONSTRAINT IF EXISTS scheduled_posts_channel_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE scheduled_posts 
        ADD CONSTRAINT scheduled_posts_channel_id_fkey 
        FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE RESTRICT;
    """)
    
    # 3. Fix scheduled_posts user relationship
    op.execute("""
        ALTER TABLE scheduled_posts 
        DROP CONSTRAINT IF EXISTS scheduled_posts_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE scheduled_posts 
        ADD CONSTRAINT scheduled_posts_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
    """)
    
    # 4. Fix payment_methods table - prevent user deletion from destroying payment info
    op.execute("""
        ALTER TABLE payment_methods 
        DROP CONSTRAINT IF EXISTS payment_methods_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE payment_methods 
        ADD CONSTRAINT payment_methods_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
    """)
    
    # 5. Fix subscriptions table - prevent user deletion from destroying subscription history
    op.execute("""
        ALTER TABLE subscriptions 
        DROP CONSTRAINT IF EXISTS subscriptions_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE subscriptions 
        ADD CONSTRAINT subscriptions_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
    """)
    
    # 6. Fix payments table - prevent user deletion from destroying payment records
    op.execute("""
        ALTER TABLE payments 
        DROP CONSTRAINT IF EXISTS payments_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE payments 
        ADD CONSTRAINT payments_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
    """)


def downgrade() -> None:
    """Revert to original CASCADE DELETE constraints (DANGEROUS - NOT RECOMMENDED)."""
    
    # WARNING: This rollback restores dangerous CASCADE DELETE behavior
    # Only use in development environments
    
    # 1. Restore channels CASCADE DELETE
    op.execute("""
        ALTER TABLE channels 
        DROP CONSTRAINT IF EXISTS channels_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE channels 
        ADD CONSTRAINT channels_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    """)
    
    # 2. Restore scheduled_posts CASCADE DELETE
    op.execute("""
        ALTER TABLE scheduled_posts 
        DROP CONSTRAINT IF EXISTS scheduled_posts_channel_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE scheduled_posts 
        ADD CONSTRAINT scheduled_posts_channel_id_fkey 
        FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE scheduled_posts 
        DROP CONSTRAINT IF EXISTS scheduled_posts_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE scheduled_posts 
        ADD CONSTRAINT scheduled_posts_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    """)
    
    # 3. Restore payment_methods CASCADE DELETE
    op.execute("""
        ALTER TABLE payment_methods 
        DROP CONSTRAINT IF EXISTS payment_methods_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE payment_methods 
        ADD CONSTRAINT payment_methods_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    """)
    
    # 4. Restore subscriptions CASCADE DELETE
    op.execute("""
        ALTER TABLE subscriptions 
        DROP CONSTRAINT IF EXISTS subscriptions_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE subscriptions 
        ADD CONSTRAINT subscriptions_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    """)
    
    # 5. Restore payments CASCADE DELETE
    op.execute("""
        ALTER TABLE payments 
        DROP CONSTRAINT IF EXISTS payments_user_id_fkey CASCADE;
    """)
    
    op.execute("""
        ALTER TABLE payments 
        ADD CONSTRAINT payments_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    """)   
