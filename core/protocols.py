"""
Service Protocols for Dependency Injection
Clean Architecture interfaces for all services
"""

from typing import Protocol, Dict, Any, List, Optional
from abc import ABC, abstractmethod


class ServiceProtocol(Protocol):
    """Base protocol for all services"""
    
    def get_service_name(self) -> str:
        """Get service identifier"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        ...


class AnalyticsServiceProtocol(ServiceProtocol):
    """Analytics service interface"""
    
    async def get_channel_metrics(self, channel_id: str, period: str = "7d") -> Dict[str, Any]:
        """Get channel analytics metrics"""
        ...
    
    async def get_engagement_data(self, channel_id: str, period: str = "24h") -> Dict[str, Any]:
        """Get engagement analytics"""
        ...
    
    async def get_post_performance(self, channel_id: str, post_id: str) -> Dict[str, Any]:
        """Get individual post performance"""
        ...
    
    async def get_best_posting_times(self, channel_id: str) -> Dict[str, Any]:
        """Get optimal posting times"""
        ...
    
    async def get_audience_insights(self, channel_id: str) -> Dict[str, Any]:
        """Get audience demographics and insights"""
        ...


class AnalyticsFusionServiceProtocol(ServiceProtocol):
    """Analytics fusion service interface for real-time analytics"""
    
    async def get_realtime_metrics(self, channel_id: int) -> Dict[str, Any]:
        """Get real-time metrics for a channel"""
        ...
    
    async def calculate_performance_score(self, channel_id: int, period: int) -> Dict[str, Any]:
        """Calculate performance score for a channel"""
        ...
    
    async def get_live_monitoring_data(self, channel_id: int) -> Dict[str, Any]:
        """Get live monitoring data"""
        ...
    
    async def get_live_metrics(self, channel_id: int, hours: int = 6) -> Dict[str, Any]:
        """Get real-time live metrics for monitoring dashboard"""
        ...
    
    async def generate_analytical_report(self, channel_id: int, report_type: str, days: int) -> Dict[str, Any]:
        """Generate comprehensive analytical reports"""
        ...
    
    async def generate_recommendations(self, channel_id: int) -> Dict[str, Any]:
        """Generate AI-powered recommendations"""
        ...


class RedisClientProtocol(ServiceProtocol):
    """Redis client interface for caching and session management"""
    
    async def get(self, key: str) -> Any:
        """Get value from Redis"""
        ...
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
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
    
    async def process_payment(self, amount: int, currency: str, user_id: int) -> Dict[str, Any]:
        """Process a payment"""
        ...
    
    async def create_subscription(self, user_id: int, plan_id: str) -> Dict[str, Any]:
        """Create a subscription"""
        ...
    
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription"""
        ...
    
    async def get_payment_methods(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's payment methods"""
        ...
    
    async def refund_payment(self, payment_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Process a refund"""
        ...


class DatabaseServiceProtocol(ServiceProtocol):
    """Database service interface"""
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        ...
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        ...
    
    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data"""
        ...
    
    async def get_user_channels(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's channels"""
        ...


class AIServiceProtocol(ServiceProtocol):
    """AI services interface"""
    
    async def generate_content_suggestions(self, channel_id: str, topic: str) -> List[str]:
        """Generate content suggestions"""
        ...
    
    async def analyze_content_performance(self, content: str) -> Dict[str, Any]:
        """Analyze content for performance prediction"""
        ...
    
    async def get_optimal_hashtags(self, content: str) -> List[str]:
        """Get optimal hashtags for content"""
        ...
    
    async def predict_engagement(self, content: str, posting_time: str) -> Dict[str, Any]:
        """Predict engagement for content"""
        ...


class TelegramAPIServiceProtocol(ServiceProtocol):
    """Telegram API service interface"""
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get channel information"""
        ...
    
    async def get_channel_posts(self, channel_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get channel posts"""
        ...
    
    async def send_message(self, chat_id: str, message: str) -> Dict[str, Any]:
        """Send message to chat"""
        ...
    
    async def get_chat_members_count(self, chat_id: str) -> int:
        """Get chat members count"""
        ...


class EmailServiceProtocol(ServiceProtocol):
    """Email service interface"""
    
    async def send_email(self, to: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send email"""
        ...
    
    async def send_template_email(self, to: str, template_id: str, variables: Dict[str, Any]) -> bool:
        """Send templated email"""
        ...
    
    async def verify_email_delivery(self, email_id: str) -> Dict[str, Any]:
        """Check email delivery status"""
        ...


class AuthServiceProtocol(ServiceProtocol):
    """Authentication service interface"""
    
    async def is_demo_user(self, user_id: int) -> bool:
        """Check if user is a demo user"""
        ...
    
    async def get_demo_user_type(self, user_id: int) -> Optional[str]:
        """Get demo user type"""
        ...
    
    async def authenticate_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user by token"""
        ...
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """Get user permissions"""
        ...


class AdminServiceProtocol(ServiceProtocol):
    """Admin service interface"""
    
    async def get_user_channels(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user channels for admin"""
        ...
    
    async def get_operations_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get admin operations log"""
        ...
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        ...


class DemoDataServiceProtocol(ServiceProtocol):
    """Demo data service interface"""
    
    async def get_initial_data(self, user_id: int = None, demo_type: str = None) -> Dict[str, Any]:
        """Get initial demo data for TWA initialization"""
        ...
    
    async def reset_demo_data(self) -> Dict[str, Any]:
        """Reset demo data to initial state"""
        ...
    
    async def seed_demo_channels(self, user_id: int) -> List[Dict[str, Any]]:
        """Seed demo channels for user"""
        ...


class PostsRepositoryProtocol(Protocol):
    """Posts repository interface"""
    
    async def get_posts_by_channel(self, channel_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts for a channel"""
        ...
    
    async def get_post_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific post"""
        ...
    
    async def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new post"""
        ...
    
    async def update_post(self, post_id: int, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a post"""
        ...


# Service registry type hints
ServiceType = type[ServiceProtocol]
ServiceInstance = ServiceProtocol