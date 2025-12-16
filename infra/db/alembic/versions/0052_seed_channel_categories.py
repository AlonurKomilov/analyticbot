"""
0052_seed_channel_categories

Seeds initial channel categories for the public catalog.

Revision ID: 0052_seed_categories
Revises: 0051_public_catalog
Create Date: 2025-12-15
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = "0052_seed_categories"
down_revision = "0051_public_catalog"
branch_labels = None
depends_on = None


# Initial categories with icons and colors
CATEGORIES = [
    {"name": "News & Media", "slug": "news", "icon": "📰", "color": "#2196F3", "sort_order": 1},
    {"name": "Blogs", "slug": "blogs", "icon": "✍️", "color": "#9C27B0", "sort_order": 2},
    {"name": "Technology", "slug": "tech", "icon": "💻", "color": "#4CAF50", "sort_order": 3},
    {"name": "Entertainment", "slug": "entertainment", "icon": "🎬", "color": "#F44336", "sort_order": 4},
    {"name": "Education", "slug": "education", "icon": "📚", "color": "#FF9800", "sort_order": 5},
    {"name": "Business", "slug": "business", "icon": "💼", "color": "#3F51B5", "sort_order": 6},
    {"name": "Crypto", "slug": "crypto", "icon": "₿", "color": "#FFC107", "sort_order": 7},
    {"name": "Sports", "slug": "sports", "icon": "⚽", "color": "#8BC34A", "sort_order": 8},
    {"name": "Music", "slug": "music", "icon": "🎵", "color": "#E91E63", "sort_order": 9},
    {"name": "Art & Design", "slug": "art", "icon": "🎨", "color": "#673AB7", "sort_order": 10},
    {"name": "Gaming", "slug": "gaming", "icon": "🎮", "color": "#7C4DFF", "sort_order": 11},
    {"name": "Science", "slug": "science", "icon": "🔬", "color": "#009688", "sort_order": 12},
    {"name": "Travel", "slug": "travel", "icon": "✈️", "color": "#03A9F4", "sort_order": 13},
    {"name": "Food", "slug": "food", "icon": "🍕", "color": "#FF5722", "sort_order": 14},
    {"name": "Fashion", "slug": "fashion", "icon": "👗", "color": "#EC407A", "sort_order": 15},
    {"name": "Politics", "slug": "politics", "icon": "🏛️", "color": "#607D8B", "sort_order": 16},
    {"name": "Health & Fitness", "slug": "health", "icon": "💪", "color": "#00BCD4", "sort_order": 17},
    {"name": "Finance", "slug": "finance", "icon": "💰", "color": "#795548", "sort_order": 18},
    {"name": "Movies & TV", "slug": "movies", "icon": "🎥", "color": "#FF7043", "sort_order": 19},
    {"name": "Other", "slug": "other", "icon": "📁", "color": "#9E9E9E", "sort_order": 99},
]


def upgrade() -> None:
    """Seed initial channel categories"""
    
    # Get connection for parameterized queries
    connection = op.get_bind()
    
    for cat in CATEGORIES:
        connection.execute(
            sa.text("""
                INSERT INTO channel_categories (name, slug, icon, color, sort_order, channel_count)
                VALUES (:name, :slug, :icon, :color, :sort_order, 0)
            """),
            cat
        )


def downgrade() -> None:
    """Remove seeded categories"""
    op.execute("DELETE FROM channel_categories")
