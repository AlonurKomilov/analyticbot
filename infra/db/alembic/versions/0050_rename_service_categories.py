"""
0050_rename_service_categories

Renames service categories for clarity:
- bot_moderation -> bot_service
- mtproto_access -> mtproto_services

Revision ID: 0050_rename_categories
Revises: 0049_seed_services
Create Date: 2025-12-14
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = "0050_rename_categories"
down_revision = "0049_seed_services"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename service categories for clarity"""
    
    # Update bot_moderation to bot_service
    op.execute("""
        UPDATE marketplace_services 
        SET category = 'bot_service' 
        WHERE category = 'bot_moderation'
    """)
    
    # Update mtproto_access to mtproto_services
    op.execute("""
        UPDATE marketplace_services 
        SET category = 'mtproto_services' 
        WHERE category = 'mtproto_access'
    """)


def downgrade() -> None:
    """Revert category name changes"""
    
    # Revert bot_service to bot_moderation
    op.execute("""
        UPDATE marketplace_services 
        SET category = 'bot_moderation' 
        WHERE category = 'bot_service'
    """)
    
    # Revert mtproto_services to mtproto_access
    op.execute("""
        UPDATE marketplace_services 
        SET category = 'mtproto_access' 
        WHERE category = 'mtproto_services'
    """)
