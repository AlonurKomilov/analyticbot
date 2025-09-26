"""
Backend API Mock Data Index
Centralized exports for all backend mock data modules
"""

# Initial Data Mocks
from .initial_data.mock_data import (
    create_mock_user,
    create_mock_plan, 
    create_mock_channels,
    create_mock_scheduled_posts,
    get_mock_initial_data
)

# Auth Mocks
from .auth.mock_users import (
    create_mock_users_database,
    get_mock_user_by_email,
    simulate_password_update
)

# Admin Mocks
from .admin.mock_admin_data import (
    create_mock_user_channels,
    simulate_channel_deletion,
    create_mock_admin_stats
)

# AI Services Mocks
from .ai_services.mock_ai_data import (
    create_mock_security_analysis,
    create_mock_content_optimization,
    create_mock_churn_prediction,
    create_mock_ai_service_stats
)

# Database Mocks
from .database.mock_database import (
    create_mock_analytics_data,
    create_mock_snapshot_data,
    get_mock_value_by_query,
    create_enhanced_mock_pool,
    create_legacy_mock_pool,
    EnhancedMockPool,
    MockPool
)

# Convenience exports
__all__ = [
    # Initial Data
    "create_mock_user",
    "create_mock_plan", 
    "create_mock_channels",
    "create_mock_scheduled_posts",
    "get_mock_initial_data",
    
    # Auth
    "create_mock_users_database",
    "get_mock_user_by_email", 
    "simulate_password_update",
    
    # Admin
    "create_mock_user_channels",
    "simulate_channel_deletion",
    "create_mock_admin_stats",
    
    # AI Services
    "create_mock_security_analysis",
    "create_mock_content_optimization",
    "create_mock_churn_prediction",
    "create_mock_ai_service_stats",
    
    # Database
    "create_mock_analytics_data",
    "create_mock_snapshot_data",
    "get_mock_value_by_query",
    "create_enhanced_mock_pool",
    "create_legacy_mock_pool",
    "EnhancedMockPool",
    "MockPool"
]