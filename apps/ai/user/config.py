"""
User AI Configuration
=====================

Database-stored configuration for per-user AI features.
Unlike System AI (env-configured), User AI is:
- Configurable from frontend
- Per-user customizable
- Stored in database
- Integrates with marketplace services
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AIFeature(str, Enum):
    """Available AI features for users"""

    ANALYTICS_INSIGHTS = "analytics_insights"
    CONTENT_SUGGESTIONS = "content_suggestions"
    POSTING_OPTIMIZATION = "posting_optimization"
    AUDIENCE_ANALYSIS = "audience_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    TREND_DETECTION = "trend_detection"
    AUTO_REPORTS = "auto_reports"
    CUSTOM_QUERIES = "custom_queries"


class AIModel(str, Enum):
    """Available AI models for users"""

    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    # System default - uses system-configured model
    SYSTEM_DEFAULT = "system_default"


class AITier(str, Enum):
    """User AI tier levels"""

    FREE = "free"  # Basic features, limited usage
    BASIC = "basic"  # Standard features
    PRO = "pro"  # Advanced features
    ENTERPRISE = "enterprise"  # Full access


@dataclass
class UserAILimits:
    """Usage limits based on tier"""

    requests_per_day: int = 100
    requests_per_hour: int = 20
    max_tokens_per_request: int = 4000
    max_channels_analyzed: int = 5
    max_reports_per_day: int = 3
    custom_queries_enabled: bool = False
    marketplace_services_enabled: bool = False

    @classmethod
    def from_tier(cls, tier: AITier) -> "UserAILimits":
        """Create limits based on tier"""
        tier_limits = {
            AITier.FREE: cls(
                requests_per_day=10,
                requests_per_hour=3,
                max_tokens_per_request=2000,
                max_channels_analyzed=1,
                max_reports_per_day=1,
                custom_queries_enabled=False,
                marketplace_services_enabled=False,
            ),
            AITier.BASIC: cls(
                requests_per_day=50,
                requests_per_hour=10,
                max_tokens_per_request=4000,
                max_channels_analyzed=3,
                max_reports_per_day=3,
                custom_queries_enabled=False,
                marketplace_services_enabled=True,
            ),
            AITier.PRO: cls(
                requests_per_day=200,
                requests_per_hour=30,
                max_tokens_per_request=8000,
                max_channels_analyzed=10,
                max_reports_per_day=10,
                custom_queries_enabled=True,
                marketplace_services_enabled=True,
            ),
            AITier.ENTERPRISE: cls(
                requests_per_day=1000,
                requests_per_hour=100,
                max_tokens_per_request=16000,
                max_channels_analyzed=-1,  # Unlimited
                max_reports_per_day=-1,  # Unlimited
                custom_queries_enabled=True,
                marketplace_services_enabled=True,
            ),
        }
        return tier_limits.get(tier, cls())


@dataclass
class UserAISettings:
    """User-configurable AI settings"""

    # Model preferences
    preferred_model: AIModel = AIModel.SYSTEM_DEFAULT
    temperature: float = 0.7

    # Feature toggles
    enabled_features: list[AIFeature] = field(
        default_factory=lambda: [
            AIFeature.ANALYTICS_INSIGHTS,
            AIFeature.CONTENT_SUGGESTIONS,
        ]
    )

    # Communication preferences
    language: str = "en"
    response_style: str = "professional"  # casual, professional, technical
    include_recommendations: bool = True
    include_explanations: bool = True

    # Notification preferences
    auto_insights_enabled: bool = False
    auto_insights_frequency: str = "daily"  # daily, weekly, monthly

    # Privacy settings
    data_retention_days: int = 30
    anonymize_data: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "preferred_model": self.preferred_model.value,
            "temperature": self.temperature,
            "enabled_features": [f.value for f in self.enabled_features],
            "language": self.language,
            "response_style": self.response_style,
            "include_recommendations": self.include_recommendations,
            "include_explanations": self.include_explanations,
            "auto_insights_enabled": self.auto_insights_enabled,
            "auto_insights_frequency": self.auto_insights_frequency,
            "data_retention_days": self.data_retention_days,
            "anonymize_data": self.anonymize_data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserAISettings":
        """Create from dictionary"""
        return cls(
            preferred_model=AIModel(data.get("preferred_model", AIModel.SYSTEM_DEFAULT.value)),
            temperature=data.get("temperature", 0.7),
            enabled_features=[
                AIFeature(f)
                for f in data.get(
                    "enabled_features",
                    [
                        AIFeature.ANALYTICS_INSIGHTS.value,
                        AIFeature.CONTENT_SUGGESTIONS.value,
                    ],
                )
            ],
            language=data.get("language", "en"),
            response_style=data.get("response_style", "professional"),
            include_recommendations=data.get("include_recommendations", True),
            include_explanations=data.get("include_explanations", True),
            auto_insights_enabled=data.get("auto_insights_enabled", False),
            auto_insights_frequency=data.get("auto_insights_frequency", "daily"),
            data_retention_days=data.get("data_retention_days", 30),
            anonymize_data=data.get("anonymize_data", False),
        )


@dataclass
class UserAIConfig:
    """
    Complete AI configuration for a user.

    Stored in database and loaded per-request.
    """

    user_id: int
    tier: AITier
    limits: UserAILimits
    settings: UserAISettings

    # Usage tracking
    requests_today: int = 0
    requests_this_hour: int = 0
    last_request_at: datetime | None = None

    # Enabled marketplace services
    enabled_services: list[str] = field(default_factory=list)

    # API keys for external services (if user provides own keys)
    custom_api_keys: dict[str, str] = field(default_factory=dict)

    @classmethod
    async def from_database(cls, user_id: int) -> "UserAIConfig":
        """
        Load user AI config from database.

        In production, this queries the database. For now, returns defaults.
        """
        # TODO: Implement actual database loading
        # This would query user_ai_settings table

        logger.info(f"Loading AI config for user {user_id}")

        # Default config for new users
        return cls(
            user_id=user_id,
            tier=AITier.FREE,
            limits=UserAILimits.from_tier(AITier.FREE),
            settings=UserAISettings(),
        )

    async def save_to_database(self) -> bool:
        """Save config to database"""
        # TODO: Implement actual database saving
        logger.info(f"Saving AI config for user {self.user_id}")
        return True

    def can_make_request(self) -> tuple[bool, str]:
        """Check if user can make another AI request"""
        if self.limits.requests_per_day != -1:
            if self.requests_today >= self.limits.requests_per_day:
                return False, "Daily request limit reached"

        if self.limits.requests_per_hour != -1:
            if self.requests_this_hour >= self.limits.requests_per_hour:
                return False, "Hourly request limit reached"

        return True, "OK"

    def can_use_feature(self, feature: AIFeature) -> bool:
        """Check if user can use a specific feature"""
        return feature in self.settings.enabled_features

    def can_use_marketplace_service(self, service_id: str) -> bool:
        """Check if user can use a marketplace service"""
        if not self.limits.marketplace_services_enabled:
            return False
        return service_id in self.enabled_services

    def increment_usage(self):
        """Increment usage counters"""
        self.requests_today += 1
        self.requests_this_hour += 1
        self.last_request_at = datetime.utcnow()

    def get_effective_model(self, system_default: str = "gpt-4o-mini") -> str:
        """Get the effective model to use"""
        if self.settings.preferred_model == AIModel.SYSTEM_DEFAULT:
            return system_default
        return self.settings.preferred_model.value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "tier": self.tier.value,
            "limits": {
                "requests_per_day": self.limits.requests_per_day,
                "requests_per_hour": self.limits.requests_per_hour,
                "max_tokens_per_request": self.limits.max_tokens_per_request,
                "max_channels_analyzed": self.limits.max_channels_analyzed,
                "max_reports_per_day": self.limits.max_reports_per_day,
                "custom_queries_enabled": self.limits.custom_queries_enabled,
                "marketplace_services_enabled": self.limits.marketplace_services_enabled,
            },
            "settings": self.settings.to_dict(),
            "usage": {
                "requests_today": self.requests_today,
                "requests_this_hour": self.requests_this_hour,
                "last_request_at": (
                    self.last_request_at.isoformat() if self.last_request_at else None
                ),
            },
            "enabled_services": self.enabled_services,
        }
