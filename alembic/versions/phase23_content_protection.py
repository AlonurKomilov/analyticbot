"""Create tables for Phase 2.3 Content Protection features

Revision ID: phase23_content_protection
Revises: phase22_payment_system  
Create Date: 2025-01-07 20:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers
revision: str = 'phase23_content_protection'
down_revision: Union[str, None] = 'phase22_payment_system'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create content protection tables"""
    
    # Content Protection main table
    op.create_table(
        'content_protection',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.Enum('IMAGE', 'VIDEO', 'TEXT', name='content_type'), nullable=False),
        sa.Column('original_file_path', sa.String(), nullable=True),
        sa.Column('protected_file_path', sa.String(), nullable=True),
        sa.Column('watermark_text', sa.String(), nullable=True),
        sa.Column('protection_level', sa.Enum('BASIC', 'STANDARD', 'PREMIUM', name='protection_level'), nullable=False),
        sa.Column('watermark_config', sa.JSON(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('protection_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('access_count', sa.Integer(), default=0, nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.Index('ix_content_protection_user_id', 'user_id'),
        sa.Index('ix_content_protection_created_at', 'created_at'),
        sa.Index('ix_content_protection_content_type', 'content_type')
    )
    
    # Premium Emoji Usage tracking
    op.create_table(
        'premium_emoji_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('emoji_id', sa.String(), nullable=False),
        sa.Column('emoji_unicode', sa.String(), nullable=False),
        sa.Column('usage_count', sa.Integer(), default=1, nullable=False),
        sa.Column('context', sa.String(), nullable=True),  # Where emoji was used
        sa.Column('tier_at_usage', sa.Enum('FREE', 'BASIC', 'PRO', 'ENTERPRISE', name='user_tier'), nullable=False),
        sa.Column('usage_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.Index('ix_premium_emoji_user_date', 'user_id', 'usage_date'),
        sa.Index('ix_premium_emoji_emoji_id', 'emoji_id'),
        sa.UniqueConstraint('user_id', 'emoji_id', 'usage_date', name='uq_user_emoji_daily')
    )
    
    # Content Theft Detection logs
    op.create_table(
        'content_theft_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),  # SHA256 hash of content
        sa.Column('content_preview', sa.Text(), nullable=True),    # First 500 chars for reference
        sa.Column('theft_indicators', sa.JSON(), nullable=False),  # Array of detected indicators
        sa.Column('risk_score', sa.Float(), nullable=False),       # 0.0 to 1.0
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='risk_level'), nullable=False),
        sa.Column('scan_metadata', sa.JSON(), nullable=True),      # Additional scan details
        sa.Column('recommendations', sa.JSON(), nullable=True),    # Array of suggested actions
        sa.Column('follow_up_required', sa.Boolean(), default=False, nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.Index('ix_theft_log_user_id', 'user_id'),
        sa.Index('ix_theft_log_risk_level', 'risk_level'),
        sa.Index('ix_theft_log_created_at', 'created_at'),
        sa.Index('ix_theft_log_content_hash', 'content_hash')
    )
    
    # User Premium Features usage tracking (monthly limits)
    op.create_table(
        'user_premium_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month_year', sa.String(7), nullable=False),  # Format: "2024-01"
        sa.Column('watermarks_used', sa.Integer(), default=0, nullable=False),
        sa.Column('custom_emojis_used', sa.Integer(), default=0, nullable=False),
        sa.Column('theft_scans_used', sa.Integer(), default=0, nullable=False),
        sa.Column('video_watermarks_used', sa.Integer(), default=0, nullable=False),
        sa.Column('premium_signatures_used', sa.Integer(), default=0, nullable=False),
        sa.Column('total_file_size_processed_mb', sa.Float(), default=0.0, nullable=False),
        sa.Column('tier_at_month', sa.Enum('FREE', 'BASIC', 'PRO', 'ENTERPRISE', name='user_tier'), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'month_year', name='uq_user_monthly_usage'),
        sa.Index('ix_user_premium_features_month', 'month_year'),
        sa.Index('ix_user_premium_features_user_month', 'user_id', 'month_year')
    )
    
    # Custom Emoji Packs (admin-managed)
    op.create_table(
        'custom_emoji_packs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pack_name', sa.String(100), nullable=False),
        sa.Column('pack_description', sa.Text(), nullable=True),
        sa.Column('tier_required', sa.Enum('FREE', 'BASIC', 'PRO', 'ENTERPRISE', name='user_tier'), nullable=False),
        sa.Column('emoji_data', sa.JSON(), nullable=False),  # {emoji_id: unicode_char}
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('sort_order', sa.Integer(), default=0, nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),  # Admin user ID
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.Index('ix_emoji_packs_tier', 'tier_required'),
        sa.Index('ix_emoji_packs_active', 'is_active'),
        sa.UniqueConstraint('pack_name', name='uq_emoji_pack_name')
    )


def downgrade() -> None:
    """Drop content protection tables"""
    
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('custom_emoji_packs')
    op.drop_table('user_premium_features')
    op.drop_table('content_theft_log')
    op.drop_table('premium_emoji_usage')
    op.drop_table('content_protection')
    
    # Drop custom enums
    sa.Enum(name='content_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='protection_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='risk_level').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='user_tier').drop(op.get_bind(), checkfirst=True)
