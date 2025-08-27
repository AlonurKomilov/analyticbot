"""Create SuperAdmin Management Panel tables

Revision ID: 001_create_superadmin_tables
Revises: 
Create Date: 2025-08-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision = '001_create_superadmin_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create admin_users table
    op.create_table(
        'admin_users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('failed_login_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.DateTime(timezone=True)),
        sa.Column('allowed_ips', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('admin_users.id')),
    )

    # Create admin_sessions table
    op.create_table(
        'admin_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('admin_user_id', UUID(as_uuid=True), sa.ForeignKey('admin_users.id'), nullable=False),
        sa.Column('session_token', sa.String(255), unique=True, nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create system_users table
    op.create_table(
        'system_users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('telegram_id', sa.Integer(), unique=True, nullable=False),
        sa.Column('username', sa.String(50)),
        sa.Column('full_name', sa.String(100)),
        sa.Column('email', sa.String(255)),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('subscription_tier', sa.String(20)),
        sa.Column('total_channels', sa.Integer(), default=0),
        sa.Column('total_posts', sa.Integer(), default=0),
        sa.Column('last_activity', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('suspended_at', sa.DateTime(timezone=True)),
        sa.Column('suspended_by', UUID(as_uuid=True), sa.ForeignKey('admin_users.id')),
        sa.Column('suspension_reason', sa.Text()),
    )

    # Create admin_audit_logs table
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('admin_user_id', UUID(as_uuid=True), sa.ForeignKey('admin_users.id'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('ip_address', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.Text()),
        sa.Column('request_method', sa.String(10)),
        sa.Column('request_path', sa.String(500)),
        sa.Column('old_values', sa.JSON()),
        sa.Column('new_values', sa.JSON()),
        sa.Column('success', sa.Boolean(), default=True),
        sa.Column('error_message', sa.Text()),
        sa.Column('additional_data', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create system_configurations table
    op.create_table(
        'system_configurations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('value_type', sa.String(20), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('is_sensitive', sa.Boolean(), default=False),
        sa.Column('requires_restart', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('updated_by', UUID(as_uuid=True), sa.ForeignKey('admin_users.id'), nullable=False),
    )

    # Create system_metrics table
    op.create_table(
        'system_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_type', sa.String(20), nullable=False),
        sa.Column('labels', sa.JSON()),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Create indexes for better performance
    op.create_index('idx_admin_sessions_token', 'admin_sessions', ['session_token'])
    op.create_index('idx_admin_sessions_user_active', 'admin_sessions', ['admin_user_id', 'is_active'])
    op.create_index('idx_system_users_telegram_id', 'system_users', ['telegram_id'])
    op.create_index('idx_system_users_status', 'system_users', ['status'])
    op.create_index('idx_audit_logs_admin_user', 'admin_audit_logs', ['admin_user_id'])
    op.create_index('idx_audit_logs_action', 'admin_audit_logs', ['action'])
    op.create_index('idx_audit_logs_created_at', 'admin_audit_logs', ['created_at'])
    op.create_index('idx_system_config_category', 'system_configurations', ['category'])
    op.create_index('idx_system_metrics_name_timestamp', 'system_metrics', ['metric_name', 'timestamp'])

    # Insert default super admin user (password: SuperAdmin123!)
    # Note: In production, this should be changed immediately
    op.execute("""
        INSERT INTO admin_users (id, username, email, full_name, role, password_hash, is_active)
        VALUES (
            gen_random_uuid(),
            'superadmin',
            'admin@analyticbot.com',
            'System Administrator',
            'super_admin',
            '$2b$12$LQv3c1yqBWVHxkd0LQ4YCOvRkRcqpWp1zxGQ3EfM6.j0Zr9mGm9QO',
            true
        )
    """)

    # Insert some default system configurations
    op.execute("""
        INSERT INTO system_configurations (id, key, value, value_type, category, description, updated_by)
        SELECT 
            gen_random_uuid(),
            'max_login_attempts',
            '5',
            'integer',
            'security',
            'Maximum failed login attempts before account lockout',
            id
        FROM admin_users 
        WHERE username = 'superadmin'
        LIMIT 1
    """)

    op.execute("""
        INSERT INTO system_configurations (id, key, value, value_type, category, description, updated_by)
        SELECT 
            gen_random_uuid(),
            'session_timeout_hours',
            '8',
            'integer',
            'security',
            'Admin session timeout in hours',
            id
        FROM admin_users 
        WHERE username = 'superadmin'
        LIMIT 1
    """)


def downgrade():
    # Drop indexes
    op.drop_index('idx_system_metrics_name_timestamp', 'system_metrics')
    op.drop_index('idx_system_config_category', 'system_configurations')
    op.drop_index('idx_audit_logs_created_at', 'admin_audit_logs')
    op.drop_index('idx_audit_logs_action', 'admin_audit_logs')
    op.drop_index('idx_audit_logs_admin_user', 'admin_audit_logs')
    op.drop_index('idx_system_users_status', 'system_users')
    op.drop_index('idx_system_users_telegram_id', 'system_users')
    op.drop_index('idx_admin_sessions_user_active', 'admin_sessions')
    op.drop_index('idx_admin_sessions_token', 'admin_sessions')

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('system_metrics')
    op.drop_table('system_configurations')
    op.drop_table('admin_audit_logs')
    op.drop_table('admin_sessions')
    op.drop_table('system_users')
    op.drop_table('admin_users')
