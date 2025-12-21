"""
Marketplace Service Adapter
===========================

Base adapter interface for integrating marketplace services with AI.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ServiceCapability(str, Enum):
    """Capabilities a marketplace service can have"""
    # Content capabilities
    CONTENT_GENERATION = "content_generation"
    CONTENT_SCHEDULING = "content_scheduling"
    CONTENT_OPTIMIZATION = "content_optimization"
    
    # Analytics capabilities
    ANALYTICS_PROCESSING = "analytics_processing"
    TREND_DETECTION = "trend_detection"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    
    # Automation capabilities
    AUTO_POSTING = "auto_posting"
    AUTO_MODERATION = "auto_moderation"
    AUTO_RESPONSE = "auto_response"
    
    # Integration capabilities
    CROSS_PLATFORM = "cross_platform"
    EXTERNAL_API = "external_api"
    WEBHOOK = "webhook"


@dataclass
class ServiceDefinition:
    """Definition of a marketplace service"""
    service_id: str
    name: str
    description: str
    version: str
    
    # Capabilities
    capabilities: list[ServiceCapability] = field(default_factory=list)
    
    # Requirements
    required_permissions: list[str] = field(default_factory=list)
    required_tier: str = "basic"  # free, basic, pro, enterprise
    
    # Pricing
    is_free: bool = False
    price_per_use: float = 0.0
    monthly_price: float = 0.0
    
    # Configuration schema (JSON Schema format)
    config_schema: dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    author: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    rating: float = 0.0
    install_count: int = 0


@dataclass
class ServiceExecutionContext:
    """Context for service execution"""
    user_id: int
    channel_id: int | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    ai_enhancement: bool = True  # Whether to use AI enhancement
    dry_run: bool = False


@dataclass
class ServiceResult:
    """Result of service execution"""
    success: bool
    service_id: str
    result_data: dict[str, Any] = field(default_factory=dict)
    ai_insights: list[str] = field(default_factory=list)
    execution_time_ms: int = 0
    error_message: str | None = None


class MarketplaceServiceAdapter(ABC):
    """
    Base adapter for marketplace services.
    
    Any marketplace service that wants AI integration
    must implement this adapter interface.
    
    Example:
        class AutoPostingAdapter(MarketplaceServiceAdapter):
            @property
            def definition(self) -> ServiceDefinition:
                return ServiceDefinition(
                    service_id="auto_posting_v1",
                    name="Auto Posting",
                    capabilities=[ServiceCapability.AUTO_POSTING],
                )
            
            async def execute(self, context: ServiceExecutionContext) -> ServiceResult:
                # Implementation
                pass
    """
    
    @property
    @abstractmethod
    def definition(self) -> ServiceDefinition:
        """Get service definition"""
        pass
    
    @abstractmethod
    async def execute(
        self,
        context: ServiceExecutionContext,
    ) -> ServiceResult:
        """
        Execute the service.
        
        Args:
            context: Execution context with user/channel info and parameters
            
        Returns:
            Execution result
        """
        pass
    
    async def validate_parameters(
        self,
        parameters: dict[str, Any],
    ) -> tuple[bool, str]:
        """
        Validate execution parameters.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Default implementation - no validation
        return True, ""
    
    async def get_ai_enhancement(
        self,
        context: ServiceExecutionContext,
        raw_result: dict[str, Any],
    ) -> list[str]:
        """
        Get AI-generated insights for the service result.
        
        Override this to provide service-specific AI insights.
        
        Args:
            context: Execution context
            raw_result: Raw service execution result
            
        Returns:
            List of AI insights
        """
        return []
    
    def check_permissions(
        self,
        user_permissions: list[str],
    ) -> bool:
        """Check if user has required permissions"""
        required = set(self.definition.required_permissions)
        available = set(user_permissions)
        return required.issubset(available)
    
    def check_tier(self, user_tier: str) -> bool:
        """Check if user tier is sufficient"""
        tier_order = ["free", "basic", "pro", "enterprise"]
        
        try:
            required_idx = tier_order.index(self.definition.required_tier)
            user_idx = tier_order.index(user_tier)
            return user_idx >= required_idx
        except ValueError:
            return False


class DemoServiceAdapter(MarketplaceServiceAdapter):
    """
    Demo service adapter for testing.
    """
    
    @property
    def definition(self) -> ServiceDefinition:
        return ServiceDefinition(
            service_id="demo_service_v1",
            name="Demo AI Service",
            description="A demo service for testing marketplace integration",
            version="1.0.0",
            capabilities=[
                ServiceCapability.CONTENT_GENERATION,
                ServiceCapability.ANALYTICS_PROCESSING,
            ],
            required_tier="free",
            is_free=True,
            author="System",
            config_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "count": {"type": "integer", "default": 1},
                },
            },
        )
    
    async def execute(
        self,
        context: ServiceExecutionContext,
    ) -> ServiceResult:
        """Execute demo service"""
        import time
        start = time.time()
        
        try:
            message = context.parameters.get("message", "Hello from Demo Service!")
            count = context.parameters.get("count", 1)
            
            result_data = {
                "message": message,
                "repeated": [message] * count,
                "user_id": context.user_id,
                "channel_id": context.channel_id,
            }
            
            # Get AI insights if enabled
            ai_insights = []
            if context.ai_enhancement:
                ai_insights = await self.get_ai_enhancement(context, result_data)
            
            execution_time = int((time.time() - start) * 1000)
            
            return ServiceResult(
                success=True,
                service_id=self.definition.service_id,
                result_data=result_data,
                ai_insights=ai_insights,
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            return ServiceResult(
                success=False,
                service_id=self.definition.service_id,
                error_message=str(e),
            )
    
    async def get_ai_enhancement(
        self,
        context: ServiceExecutionContext,
        raw_result: dict[str, Any],
    ) -> list[str]:
        """Get AI insights for demo"""
        return [
            "This is a demo AI insight",
            f"Service was called for user {context.user_id}",
            "AI enhancement is working correctly",
        ]
