"""
Add first_name and last_name columns to users table

Splits full_name into separate first_name and last_name fields
for better profile management like Telegram.

Revision ID: 0057_add_user_name_fields
Revises: 0056_add_user_ai_providers
Create Date: 2024-12-24
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0057_add_user_name_fields"
down_revision = "0056_add_user_ai_providers"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add first_name and last_name columns to users table.

    Migrate existing full_name data by splitting on first space:
    - "John Doe" -> first_name="John", last_name="Doe"
    - "John" -> first_name="John", last_name=null
    - "John Paul Jones" -> first_name="John", last_name="Paul Jones"
    """

    # Add new columns
    op.add_column("users", sa.Column("first_name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(length=100), nullable=True))

    # Migrate existing full_name data to first_name/last_name
    # Split on first space: "John Doe" -> first="John", last="Doe"
    op.execute(
        """
        UPDATE users 
        SET 
            first_name = CASE 
                WHEN full_name IS NOT NULL AND full_name != '' 
                THEN split_part(full_name, ' ', 1)
                ELSE NULL
            END,
            last_name = CASE 
                WHEN full_name IS NOT NULL AND full_name LIKE '% %' 
                THEN substring(full_name from position(' ' in full_name) + 1)
                ELSE NULL
            END
        WHERE full_name IS NOT NULL AND full_name != '';
    """
    )

    # Add indexes for name searches
    op.create_index("idx_users_first_name", "users", ["first_name"])
    op.create_index("idx_users_last_name", "users", ["last_name"])


def downgrade() -> None:
    """
    Remove first_name and last_name columns.
    full_name is kept as is since we didn't drop it.
    """
    op.drop_index("idx_users_last_name", table_name="users")
    op.drop_index("idx_users_first_name", table_name="users")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
