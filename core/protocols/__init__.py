"""
Service Protocols for Dependency Injection
Clean Architecture interfaces for all services
"""

from datetime import datetime
from typing import Any, Protocol

# ✅ PHASE 2 FIX: Import infrastructure protocols (Oct 19, 2025)
from core.protocols.infrastructure_protocols import (
    AdminRepositoryProtocol,
    AnalyticsRepositoryProtocol,
    CacheProtocol,
    ChannelDailyRepositoryProtocol,
    DatabaseManagerProtocol,
    PostMetricsRepositoryProtocol,
    StatsRawRepositoryProtocol,
    TelegramClientProtocol,
    UserRepositoryProtocol,
)


class ServiceProtocol(Protocol):
    """Base protocol for all services"""

    def get_service_name(self) -> str:
        """Get service identifier"""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Service health check"""
        ...


class AnalyticsServiceProtocol(ServiceProtocol):
    """Analytics service interface"""

    async def get_channel_metrics(self, channel_id: str, period: str = "7d") -> dict[str, Any]:
        """Get channel analytics metrics"""
        ...

    async def get_engagement_data(self, channel_id: str, period: str = "24h") -> dict[str, Any]:
        """Get engagement analytics"""
        ...

    async def get_post_performance(self, channel_id: str, post_id: str) -> dict[str, Any]:
        """Get individual post performance"""
        ...

    async def get_best_posting_times(self, channel_id: str) -> dict[str, Any]:
        """Get optimal posting times"""
        ...

    async def get_audience_insights(self, channel_id: str) -> dict[str, Any]:
        """Get audience demographics and insights"""
        ...


class AnalyticsFusionServiceProtocol(ServiceProtocol):
    """Analytics fusion service interface for real-time analytics"""

    async def get_realtime_metrics(self, channel_id: int) -> dict[str, Any]:
        """Get real-time metrics for a channel"""
        ...

    async def calculate_performance_score(self, channel_id: int, period: int) -> dict[str, Any]:
        """Calculate performance score for a channel"""
        ...

    async def get_live_monitoring_data(self, channel_id: int) -> dict[str, Any]:
        """Get live monitoring data"""
        ...

    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> dict[str, Any]:
        """Get real-time live metrics for monitoring dashboard"""
        ...

    async def generate_analytical_report(
        self, channel_id: int, report_type: str, days: int
    ) -> dict[str, Any]:
        """Generate comprehensive analytical reports"""
        ...

    async def generate_recommendations(self, channel_id: int) -> dict[str, Any]:
        """Generate AI-powered recommendations"""
        ...

    # Historical analytics methods
    async def get_last_updated_at(self, channel_id: int) -> datetime | None:
        """Get last updated timestamp for channel data"""
        ...

    async def get_channel_overview(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> dict[str, Any]:
        """Get channel overview with historical metrics"""
        ...

    async def get_growth_time_series(
        self, channel_id: int, from_date: datetime, to_date: datetime, window_days: int
    ) -> list[dict[str, Any]]:
        """Get growth time series data"""
        ...

    async def get_historical_metrics(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> dict[str, Any]:
        """Get historical metrics data"""
        ...

    async def get_top_posts(
        self, channel_id: int, from_date: datetime, to_date: datetime, limit: int
    ) -> list[dict[str, Any]]:
        """Get top performing posts"""
        ...

    async def get_traffic_sources(
        self, channel_id: int, from_date: datetime, to_date: datetime
    ) -> dict[str, Any]:
        """Get traffic sources data"""
        ...

    # Orchestration methods
    async def coordinate_comprehensive_analysis(
        self, channel_id: int, parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Coordinate comprehensive analytics analysis"""
        ...

    # Admin and system methods
    async def get_system_statistics_admin(self) -> dict[str, Any]:
        """Get system statistics for admin"""
        ...

    async def get_admin_audit_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get admin audit logs"""
        ...

    async def check_system_health(self) -> dict[str, Any]:
        """Check system health status"""
        ...

    # Engagement analytics methods
    async def get_engagement_insights(
        self, channel_id: int, period: str, metrics_type: str
    ) -> dict[str, Any]:
        """Get engagement insights for channel"""
        ...

    async def get_engagement_trends(self, channel_id: int, period: str) -> dict[str, Any]:
        """Get engagement trends data"""
        ...

    async def get_audience_insights(self, channel_id: int, period: str) -> dict[str, Any]:
        """Get audience insights"""
        ...

    async def get_audience_demographics(self, channel_id: int) -> dict[str, Any]:
        """Get audience demographics"""
        ...

    async def get_audience_behavior_patterns(self, channel_id: int) -> dict[str, Any]:
        """Get audience behavior patterns"""
        ...

    # Report and comparison methods
    async def get_period_comparison(self, channel_id: int) -> dict[str, Any]:
        """Get period comparison data"""
        ...

    async def get_metrics_comparison(self, channel_id: int) -> dict[str, Any]:
        """Get metrics comparison data"""
        ...

    async def get_performance_summary(self, channel_id: int, days: int) -> dict[str, Any]:
        """Get performance summary"""
        ...

    # Content analytics methods
    async def get_trending_posts(
        self, channel_id: int, from_date: datetime, to_date: datetime, limit: int
    ) -> dict[str, Any]:
        """Get trending posts"""
        ...

    async def get_temporal_engagement_patterns(self, channel_id: int) -> dict[str, Any]:
        """Get temporal engagement patterns"""
        ...

    async def get_content_engagement_patterns(self, channel_id: int) -> dict[str, Any]:
        """Get content engagement patterns"""
        ...

    async def get_user_engagement_patterns(self, channel_id: int) -> dict[str, Any]:
        """Get user engagement patterns"""
        ...


class RedisClientProtocol(ServiceProtocol):
    """Redis client interface for caching and session management"""

    async def get(self, key: str) -> Any:
        """Get value from Redis"""
        ...

    async def set(self, key: str, value: Any, ex: int | None = None) -> bool:
        """Set value in Redis with optional expiry"""
        ...

    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        ...

    async def ping(self) -> bool:
        """Check Redis connection"""
        ...

    async def close(self) -> None:
        """Close Redis connection"""
        ...


class PaymentServiceProtocol(ServiceProtocol):
    """Payment service interface"""

    async def process_payment(self, amount: int, currency: str, user_id: int) -> dict[str, Any]:
        """Process a payment"""
        ...

    async def create_subscription(self, user_id: int, plan_id: str) -> dict[str, Any]:
        """Create a subscription"""
        ...

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Cancel a subscription"""
        ...

    async def get_payment_methods(self, user_id: int) -> list[dict[str, Any]]:
        """Get user's payment methods"""
        ...

    async def refund_payment(self, payment_id: str, amount: int | None = None) -> dict[str, Any]:
        """Process a refund"""
        ...


class DatabaseServiceProtocol(ServiceProtocol):
    """Database service interface"""

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        """Get user by ID"""
        ...

    async def create_user(self, user_data: dict[str, Any]) -> dict[str, Any]:
        """Create new user"""
        ...

    async def update_user(self, user_id: int, user_data: dict[str, Any]) -> dict[str, Any]:
        """Update user data"""
        ...

    async def get_user_channels(self, user_id: int) -> list[dict[str, Any]]:
        """Get user's channels"""
        ...


class AIServiceProtocol(ServiceProtocol):
    """AI services interface"""

    async def generate_content_suggestions(self, channel_id: str, topic: str) -> list[str]:
        """Generate content suggestions"""
        ...

    async def analyze_content_performance(self, content: str) -> dict[str, Any]:
        """Analyze content for performance prediction"""
        ...

    async def get_optimal_hashtags(self, content: str) -> list[str]:
        """Get optimal hashtags for content"""
        ...

    async def predict_engagement(self, content: str, posting_time: str) -> dict[str, Any]:
        """Predict engagement for content"""
        ...


class TelegramAPIServiceProtocol(ServiceProtocol):
    """Telegram API service interface"""

    async def get_channel_info(self, channel_id: str) -> dict[str, Any]:
        """Get channel information"""
        ...

    async def get_channel_posts(self, channel_id: str, limit: int = 100) -> list[dict[str, Any]]:
        """Get channel posts"""
        ...

    async def send_message(self, chat_id: str, message: str) -> dict[str, Any]:
        """Send message to chat"""
        ...

    async def get_chat_members_count(self, chat_id: str) -> int:
        """Get chat members count"""
        ...


class EmailServiceProtocol(ServiceProtocol):
    """Email service interface"""

    async def send_email(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> bool:
        """Send email"""
        ...

    async def send_template_email(
        self, to: str, template_id: str, variables: dict[str, Any]
    ) -> bool:
        """Send templated email"""
        ...

    async def verify_email_delivery(self, email_id: str) -> dict[str, Any]:
        """Check email delivery status"""
        ...


class AuthServiceProtocol(ServiceProtocol):
    """Authentication service interface"""

    async def is_demo_user(self, user_id: int) -> bool:
        """Check if user is a demo user"""
        ...

    async def get_demo_user_type(self, user_id: int) -> str | None:
        """Get demo user type"""
        ...

    async def authenticate_user(self, token: str) -> dict[str, Any] | None:
        """Authenticate user by token"""
        ...

    async def get_user_permissions(self, user_id: int) -> list[str]:
        """Get user permissions"""
        ...


class AdminServiceProtocol(ServiceProtocol):
    """Admin service interface"""

    async def get_user_channels(self, user_id: int) -> list[dict[str, Any]]:
        """Get user channels for admin"""
        ...

    async def get_operations_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get admin operations log"""
        ...

    async def get_system_stats(self) -> dict[str, Any]:
        """Get system statistics"""
        ...


class DemoDataServiceProtocol(ServiceProtocol):
    """Demo data service interface"""

    async def get_initial_data(
        self, user_id: int | None = None, demo_type: str | None = None
    ) -> dict[str, Any]:
        """Get initial demo data for TWA initialization"""
        ...

    async def reset_demo_data(self) -> dict[str, Any]:
        """Reset demo data to initial state"""
        ...

    async def seed_demo_channels(self, user_id: int) -> list[dict[str, Any]]:
        """Seed demo channels for user"""
        ...


class PostsRepositoryProtocol(Protocol):
    """Posts repository interface"""

    async def get_posts_by_channel(self, channel_id: int, limit: int = 100) -> list[dict[str, Any]]:
        """Get posts for a channel"""
        ...

    async def get_post_by_id(self, post_id: int) -> dict[str, Any] | None:
        """Get a specific post"""
        ...

    async def create_post(self, post_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new post"""
        ...

    async def update_post(self, post_id: int, post_data: dict[str, Any]) -> dict[str, Any]:
        """Update a post"""
        ...


class DailyRepositoryProtocol(Protocol):
    """Daily analytics repository interface"""

    async def get_daily_metrics(
        self, channel_id: int, start_date: "datetime", end_date: "datetime"
    ) -> list[dict[str, Any]]:
        """Get daily metrics for a channel"""
        ...

    async def get_daily_by_date(self, channel_id: int, date: "datetime") -> dict[str, Any] | None:
        """Get daily metrics for a specific date"""
        ...

    async def create_daily_record(self, daily_data: dict[str, Any]) -> dict[str, Any]:
        """Create a new daily record"""
        ...

    async def update_daily_record(
        self, record_id: int, daily_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a daily record"""
        ...


class ChannelRepositoryProtocol(Protocol):
    """Channel repository interface"""

    async def get_channel_by_id(self, channel_id: int) -> dict[str, Any] | None:
        """Get channel by ID"""
        ...

    async def get_channels_by_user(self, user_id: int) -> list[dict[str, Any]]:
        """Get channels for a user"""
        ...

    async def add_channel(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Add an existing Telegram channel for analytics"""
        ...

    async def update_channel(self, channel_id: int, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Update a channel"""
        ...


class DeepLearningServiceProtocol(ServiceProtocol):
    """Deep learning service interface for ML predictions and training"""

    async def predict_growth(
        self,
        channel_id: int,
        historical_data: list[dict[str, Any]],
        forecast_horizon: int = 7,
        include_uncertainty: bool = True,
    ) -> dict[str, Any]:
        """Predict channel growth using ML models"""
        ...

    async def predict_engagement(
        self,
        content: str,
        channel_id: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Predict content engagement"""
        ...

    async def analyze_content(
        self,
        content: str,
        analysis_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Analyze content quality and characteristics"""
        ...

    async def train_model(
        self,
        channel_id: int,
        model_type: str,
        training_data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Train ML model with new data"""
        ...

    async def get_model_performance(
        self,
        channel_id: int,
        model_type: str,
    ) -> dict[str, Any]:
        """Get model performance metrics"""
        ...

    def clear_cache(self) -> None:
        """Clear prediction cache"""
        ...


# Service registry type hints
ServiceType = type[ServiceProtocol]
ServiceInstance = ServiceProtocol


# ✅ PHASE 2 FIX: Export all protocols (Oct 19, 2025)
__all__ = [
    # Base protocols
    "ServiceProtocol",
    "ServiceType",
    "ServiceInstance",
    # Service protocols
    "AnalyticsServiceProtocol",
    "AnalyticsFusionServiceProtocol",
    # "DemoServiceProtocol",  # REMOVED Oct 19, 2025: Protocol doesn't exist
    "DeepLearningServiceProtocol",
    # Repository protocols (existing)
    "PostsRepositoryProtocol",
    "DailyRepositoryProtocol",
    "ChannelRepositoryProtocol",
    # Infrastructure protocols (Phase 2 - NEW)
    "UserRepositoryProtocol",
    "AdminRepositoryProtocol",
    "AnalyticsRepositoryProtocol",
    "ChannelDailyRepositoryProtocol",
    "PostMetricsRepositoryProtocol",
    "StatsRawRepositoryProtocol",
    "CacheProtocol",
    "DatabaseManagerProtocol",
    "TelegramClientProtocol",
]
