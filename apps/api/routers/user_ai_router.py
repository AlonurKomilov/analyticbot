"""
🤖 User AI API Router
======================

User-facing AI endpoints for:
- AI settings management
- Analytics insights
- Content suggestions
- AI-powered recommendations

Unlike admin AI endpoints, these are per-user and respect tier limits.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_container

logger = logging.getLogger(__name__)

router = APIRouter(tags=["User AI"])


# =====================================
# Dependency Providers
# =====================================


async def get_user_ai_config_repo():
    """Get User AI Config Repository from DI container."""
    container = get_container()
    return await container.database.user_ai_config_repo()


async def get_user_ai_usage_repo():
    """Get User AI Usage Repository from DI container."""
    container = get_container()
    return await container.database.user_ai_usage_repo()


async def get_user_ai_services_repo():
    """Get User AI Services Repository from DI container."""
    container = get_container()
    return await container.database.user_ai_services_repo()


# =====================================
# Request/Response Models
# =====================================


class UserAISettingsResponse(BaseModel):
    """User AI settings response"""

    user_id: int
    tier: str
    enabled: bool
    features: list[str]
    limits: dict[str, Any]
    usage: dict[str, Any]
    settings: dict[str, Any]


class UpdateUserAISettingsRequest(BaseModel):
    """Request to update user AI settings"""

    enabled_features: list[str] | None = None
    preferred_model: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    language: str | None = None
    response_style: str | None = None
    include_recommendations: bool | None = None
    include_explanations: bool | None = None
    auto_insights_enabled: bool | None = None
    auto_insights_frequency: str | None = None


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis"""

    channel_id: int = Field(..., description="Channel ID to analyze")
    analysis_type: str = Field(
        default="overview", description="Type: overview, engagement, growth, content"
    )
    period_days: int = Field(default=30, ge=1, le=365)


class AIAnalysisResponse(BaseModel):
    """Response from AI analysis"""

    success: bool
    channel_id: int
    analysis_type: str
    insights: list[dict[str, Any]]
    recommendations: list[str]
    generated_at: str


class ContentSuggestionRequest(BaseModel):
    """Request for content suggestions"""

    channel_id: int = Field(..., description="Channel ID for context")
    topic: str | None = Field(None, description="Specific topic (optional)")
    content_type: str = Field(default="text_post", description="Type of content")
    tone: str = Field(default="professional", description="Content tone")
    count: int = Field(default=3, ge=1, le=10)


class ContentSuggestionResponse(BaseModel):
    """Response with content suggestions"""

    success: bool
    channel_id: int
    suggestions: list[dict[str, Any]]
    generated_at: str


class PostingRecommendationRequest(BaseModel):
    """Request for posting recommendations"""

    channel_id: int = Field(..., description="Channel ID to analyze")


class PostingRecommendationResponse(BaseModel):
    """Response with posting recommendations"""

    success: bool
    channel_id: int
    optimal_times: list[str]
    frequency_recommendation: str
    content_mix: dict[str, float]
    generated_at: str


class CustomQueryRequest(BaseModel):
    """Request for custom AI query (Pro/Enterprise)"""

    query: str = Field(..., min_length=10, max_length=1000)
    context: dict[str, Any] | None = None


class CustomQueryResponse(BaseModel):
    """Response from custom AI query"""

    success: bool
    query: str
    response: str
    tokens_used: int
    generated_at: str


class AIStatusResponse(BaseModel):
    """User AI status response"""

    user_id: int
    tier: str
    enabled: bool
    usage_today: int
    usage_limit: int
    remaining_requests: int
    features_enabled: list[str]
    services_enabled: list[str]


# =====================================
# Helper Functions
# =====================================


async def get_user_ai_agent(user_id: int):
    """Get or create User AI Agent for a user with repository injection"""
    from apps.ai.user import UserAIAgent, UserAIConfig
    from apps.ai.user.config import AITier, UserAILimits, UserAISettings
    from apps.di import get_container

    # Get repositories from DI container
    container = get_container()
    providers_repo = await container.database.user_ai_providers_repo()
    usage_repo = await container.database.user_ai_usage_repo()

    # TODO: Load from database in production
    # For now, create default config
    config = UserAIConfig(
        user_id=user_id,
        tier=AITier.BASIC,
        limits=UserAILimits.from_tier(AITier.BASIC),
        settings=UserAISettings(),
    )

    # Create agent with repository injection
    return UserAIAgent(
        config=config,
        providers_repo=providers_repo,
        usage_repo=usage_repo,
    )


# =====================================
# Endpoints: AI Settings
# =====================================


@router.get("/settings", response_model=UserAISettingsResponse)
async def get_ai_settings(
    user_id: int = Depends(get_current_user_id),
    config_repo=Depends(get_user_ai_config_repo),
    usage_repo=Depends(get_user_ai_usage_repo),
    services_repo=Depends(get_user_ai_services_repo),
) -> UserAISettingsResponse:
    """
    Get user's AI settings and current status.

    Returns tier, enabled features, usage limits, and preferences.
    """
    try:
        # Get or create user AI configuration
        config_data = await config_repo.get_or_create_default(user_id)

        # Get today's usage
        usage_data = await usage_repo.get_today(user_id)
        usage_today = usage_data["requests_count"] if usage_data else 0

        # Get active services
        services = await services_repo.get_active_services(user_id)
        [s["service_type"] for s in services]

        # Calculate limits based on tier
        from apps.ai.user.config import AITier, UserAILimits

        tier = AITier(config_data["tier"])
        limits = UserAILimits.from_tier(tier)

        # Parse settings if it's a JSON string
        import json as json_lib

        settings = config_data["settings"]
        if isinstance(settings, str):
            settings = json_lib.loads(settings) if settings else {}

        return UserAISettingsResponse(
            user_id=user_id,
            tier=config_data["tier"],
            enabled=config_data["enabled"],
            features=settings.get("enabled_features", ["content_analysis", "recommendations"]),
            limits={
                "requests_per_day": limits.requests_per_day,
                "requests_per_hour": limits.requests_per_hour,
                "max_tokens": limits.max_tokens_per_request,
                "max_channels": limits.max_channels_analyzed,
            },
            usage={
                "requests_today": usage_today,
                "requests_this_hour": 0,  # TODO: Implement hourly tracking
            },
            settings=settings,
        )

    except Exception as e:
        logger.error(f"Failed to get AI settings for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI settings: {str(e)}",
        )


@router.put("/settings", response_model=UserAISettingsResponse)
async def update_ai_settings(
    request: UpdateUserAISettingsRequest,
    user_id: int = Depends(get_current_user_id),
    config_repo=Depends(get_user_ai_config_repo),
    usage_repo=Depends(get_user_ai_usage_repo),
    services_repo=Depends(get_user_ai_services_repo),
) -> UserAISettingsResponse:
    """
    Update user's AI settings.

    Allows configuring enabled features, model preferences, and behavior.
    """
    try:
        # Get current config
        config_data = await config_repo.get_or_create_default(user_id)

        # Build settings update
        settings = config_data["settings"].copy()

        if request.temperature is not None:
            settings["temperature"] = request.temperature
        if request.language is not None:
            settings["language"] = request.language
        if request.response_style is not None:
            settings["response_style"] = request.response_style
        if request.include_recommendations is not None:
            settings["include_recommendations"] = request.include_recommendations
        if request.include_explanations is not None:
            settings["include_explanations"] = request.include_explanations
        if request.auto_insights_enabled is not None:
            settings["auto_insights_enabled"] = request.auto_insights_enabled
        if request.auto_insights_frequency is not None:
            settings["auto_insights_frequency"] = request.auto_insights_frequency

        # Save to database
        await config_repo.update_settings(user_id, settings)
        logger.info(f"Updated AI settings for user {user_id}")

        # Return updated settings
        return await get_ai_settings(user_id, config_repo, usage_repo, services_repo)

    except Exception as e:
        logger.error(f"Failed to update AI settings for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update AI settings: {str(e)}",
        )


# =====================================
# Endpoints: AI Analysis
# =====================================


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_channel(
    request: AIAnalysisRequest,
    user_id: int = Depends(get_current_user_id),
) -> AIAnalysisResponse:
    """
    Get AI-powered analysis of a channel.

    Provides insights, patterns, and recommendations based on channel data.
    """
    try:
        agent = await get_user_ai_agent(user_id)

        result = await agent.analyze_channel(
            channel_id=request.channel_id,
            analysis_type=request.analysis_type,
            period_days=request.period_days,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Analysis failed"),
            )

        return AIAnalysisResponse(
            success=True,
            channel_id=request.channel_id,
            analysis_type=request.analysis_type,
            insights=result.get("insights", []),
            recommendations=result.get("recommendations", []),
            generated_at=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Channel analysis failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.get("/insights/{channel_id}")
async def get_channel_insights(
    channel_id: int,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Get AI insights for a specific channel.

    Quick endpoint for getting pre-generated or cached insights.
    """
    try:
        agent = await get_user_ai_agent(user_id)

        result = await agent.analyze_channel(
            channel_id=channel_id,
            analysis_type="overview",
            period_days=30,
        )

        return {
            "channel_id": channel_id,
            "insights": result.get("insights", []),
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get insights for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insights: {str(e)}",
        )


# =====================================
# Endpoints: Content Suggestions
# =====================================


@router.post("/suggest/content", response_model=ContentSuggestionResponse)
async def get_content_suggestions(
    request: ContentSuggestionRequest,
    user_id: int = Depends(get_current_user_id),
) -> ContentSuggestionResponse:
    """
    Get AI-generated content suggestions.

    Provides ideas and drafts based on channel context and preferences.
    """
    try:
        agent = await get_user_ai_agent(user_id)

        result = await agent.suggest_content(
            channel_id=request.channel_id,
            topic=request.topic,
            content_type=request.content_type,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Content generation failed"),
            )

        return ContentSuggestionResponse(
            success=True,
            channel_id=request.channel_id,
            suggestions=result.get("suggestions", []),
            generated_at=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Content suggestions failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}",
        )


@router.post("/suggest/posting", response_model=PostingRecommendationResponse)
async def get_posting_recommendations(
    request: PostingRecommendationRequest,
    user_id: int = Depends(get_current_user_id),
) -> PostingRecommendationResponse:
    """
    Get AI recommendations for optimal posting times and frequency.

    Analyzes channel data to suggest the best posting strategy.
    """
    try:
        agent = await get_user_ai_agent(user_id)

        result = await agent.get_posting_recommendations(
            channel_id=request.channel_id,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Recommendations failed"),
            )

        recommendations = result.get("recommendations", {})

        return PostingRecommendationResponse(
            success=True,
            channel_id=request.channel_id,
            optimal_times=recommendations.get("optimal_times", []),
            frequency_recommendation=recommendations.get("frequency", "2-3 posts per day"),
            content_mix=recommendations.get("content_mix", {}),
            generated_at=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Posting recommendations failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendations failed: {str(e)}",
        )


# =====================================
# Endpoints: Custom Query (Pro/Enterprise)
# =====================================


@router.post("/query", response_model=CustomQueryResponse)
async def custom_ai_query(
    request: CustomQueryRequest,
    user_id: int = Depends(get_current_user_id),
) -> CustomQueryResponse:
    """
    Execute a custom AI query.

    **Pro/Enterprise tier only.**
    Allows asking natural language questions about channel data.
    """
    try:
        agent = await get_user_ai_agent(user_id)

        result = await agent.custom_query(
            query=request.query,
            context=request.context,
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Query failed"),
            )

        return CustomQueryResponse(
            success=True,
            query=request.query,
            response=result.get("response", ""),
            tokens_used=result.get("tokens_used", 0),
            generated_at=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Custom query failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )


# =====================================
# Endpoints: AI Status
# =====================================


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(
    user_id: int = Depends(get_current_user_id),
    config_repo=Depends(get_user_ai_config_repo),
    usage_repo=Depends(get_user_ai_usage_repo),
    services_repo=Depends(get_user_ai_services_repo),
) -> AIStatusResponse:
    """
    Get current AI usage status.

    Returns usage counts, limits, and remaining quota.
    """
    try:
        # Get user config
        config_data = await config_repo.get_or_create_default(user_id)

        # Get today's usage
        usage_data = await usage_repo.get_today(user_id)
        usage_today = usage_data["requests_count"] if usage_data else 0

        # Get active services
        services = await services_repo.get_active_services(user_id)
        service_names = [s["service_type"] for s in services]

        # Calculate limits based on tier
        from apps.ai.user.config import AITier, UserAILimits

        tier = AITier(config_data["tier"])
        limits = UserAILimits.from_tier(tier)

        # Parse settings if it's a JSON string
        import json as json_lib

        settings = config_data["settings"]
        if isinstance(settings, str):
            settings = json_lib.loads(settings) if settings else {}

        remaining = max(0, limits.requests_per_day - usage_today)

        return AIStatusResponse(
            user_id=user_id,
            tier=config_data["tier"],
            enabled=config_data["enabled"],
            usage_today=usage_today,
            usage_limit=limits.requests_per_day,
            remaining_requests=remaining,
            features_enabled=settings.get(
                "enabled_features", ["content_analysis", "recommendations"]
            ),
            services_enabled=service_names,
        )

    except Exception as e:
        logger.error(f"Failed to get AI status for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}",
        )


# =====================================
# Endpoints: Marketplace Services
# =====================================


@router.get("/services")
async def list_ai_services(
    user_id: int = Depends(get_current_user_id),
    config_repo=Depends(get_user_ai_config_repo),
    services_repo=Depends(get_user_ai_services_repo),
) -> dict[str, Any]:
    """
    List available AI-enhanced marketplace services.

    Returns services that can be AI-powered for this user.
    """
    try:
        # Get user config for tier info
        config_data = await config_repo.get_or_create_default(user_id)

        # Get active services
        active_services = await services_repo.get_active_services(user_id)
        active_service_ids = {s["service_key"] for s in active_services}

        # TODO: Get from marketplace registry
        available_services = [
            {
                "id": "content_scheduler",
                "name": "AI Content Scheduler",
                "description": "AI-powered content scheduling and optimization",
                "enabled": "content_scheduler" in active_service_ids,
                "tier_required": "basic",
            },
            {
                "id": "auto_reply",
                "name": "AI Auto Reply",
                "description": "Intelligent auto-replies for comments",
                "enabled": "auto_reply" in active_service_ids,
                "tier_required": "pro",
            },
            {
                "id": "competitor_analysis",
                "name": "AI Competitor Analysis",
                "description": "AI-powered competitor tracking and insights",
                "enabled": "competitor_analysis" in active_service_ids,
                "tier_required": "pro",
            },
        ]

        return {
            "user_id": user_id,
            "tier": config_data["tier"],
            "services": available_services,
        }

    except Exception as e:
        logger.error(f"Failed to list AI services for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list services: {str(e)}",
        )


@router.post("/services/{service_id}/enable")
async def enable_ai_service(
    service_id: str,
    user_id: int = Depends(get_current_user_id),
    services_repo=Depends(get_user_ai_services_repo),
) -> dict[str, Any]:
    """
    Enable an AI-enhanced marketplace service.
    """
    try:
        # Activate service in database
        await services_repo.activate_service(
            user_id=user_id,
            service_key=service_id,
        )

        return {
            "success": True,
            "service_id": service_id,
            "enabled": True,
            "message": f"Service {service_id} enabled",
        }

    except Exception as e:
        logger.error(f"Failed to enable service {service_id} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable service: {str(e)}",
        )


@router.post("/services/{service_id}/disable")
async def disable_ai_service(
    service_id: str,
    user_id: int = Depends(get_current_user_id),
    services_repo=Depends(get_user_ai_services_repo),
) -> dict[str, Any]:
    """
    Disable an AI-enhanced marketplace service.
    """
    try:
        # Deactivate service in database
        await services_repo.deactivate_service(user_id, service_id)

        return {
            "success": True,
            "service_id": service_id,
            "enabled": False,
            "message": f"Service {service_id} disabled",
        }

    except Exception as e:
        logger.error(f"Failed to disable service {service_id} for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable service: {str(e)}",
        )
