"""
Competitive Intelligence Router
================================

API endpoints for competitive analysis and market intelligence.

Exposes CompetitiveIntelligenceService for:
- Comprehensive competitive intelligence reports
- Competitor discovery and profiling
- Performance comparisons
- Market position analysis
- Competitive opportunities
- Strategic recommendations

Phase 2 Enhancement - Added October 21, 2025
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.di import get_container

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Competitive Intelligence"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CompetitiveAnalysisRequest(BaseModel):
    """Request model for competitive intelligence analysis"""

    channel_id: int = Field(..., description="Channel ID to analyze")
    competitor_ids: list[int] | None = Field(
        None, description="List of competitor channel IDs (optional - will auto-discover)"
    )
    analysis_depth: str = Field(
        "standard", description="Analysis depth: 'basic', 'standard', or 'comprehensive'"
    )
    max_competitors: int = Field(5, ge=1, le=10, description="Maximum competitors to analyze")


class CompetitorDiscoveryRequest(BaseModel):
    """Request model for competitor discovery"""

    channel_id: int = Field(..., description="Channel ID to find competitors for")
    max_competitors: int = Field(5, ge=1, le=10, description="Maximum competitors to discover")


class ChannelProfileRequest(BaseModel):
    """Request model for channel profiling"""

    channel_id: int = Field(..., description="Channel ID to profile")


class PerformanceComparisonRequest(BaseModel):
    """Request model for performance comparison"""

    channel_id: int = Field(..., description="Channel ID to compare")
    competitor_ids: list[int] = Field(..., description="List of competitor channel IDs")


class CompetitiveAnalysisResponse(BaseModel):
    """Response model for competitive analysis"""

    channel_id: int
    analysis_timestamp: str
    analysis_depth: str
    channel_profile: dict[str, Any]
    competitors_analyzed: int
    competitor_analysis: dict[str, Any]
    performance_comparison: dict[str, Any]
    market_position: dict[str, Any]
    opportunities: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    status: str


class CompetitorDiscoveryResponse(BaseModel):
    """Response model for competitor discovery"""

    channel_id: int
    competitors_found: int
    competitors: list[dict[str, Any]]
    discovery_timestamp: str


class ChannelProfileResponse(BaseModel):
    """Response model for channel profile"""

    channel_id: int
    profiled_at: str
    followers_count: int
    posts_last_30_days: int
    avg_posting_frequency: float
    content_metrics: dict[str, Any]
    engagement_profile: dict[str, Any]
    activity_pattern: dict[str, Any]
    status: str


class HealthResponse(BaseModel):
    """Response model for health check"""

    service_name: str
    status: str
    version: str
    type: str
    responsibility: str
    dependencies: dict[str, Any]
    capabilities: list[str]
    configuration: dict[str, Any]


class StatsResponse(BaseModel):
    """Response model for service statistics"""

    service_name: str
    version: str
    features: dict[str, str]
    performance: dict[str, Any]
    capabilities: list[str]
    status: str


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================


async def get_competitive_service():
    """Get CompetitiveIntelligenceService from DI container"""
    try:
        container = get_container()
        service = await container.bot.competitive_intelligence_service()
        return service
    except Exception as e:
        logger.error(f"Failed to get CompetitiveIntelligenceService: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Competitive Intelligence Service unavailable",
        )


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/analyze/intelligence",
    response_model=CompetitiveAnalysisResponse,
    summary="Generate Competitive Intelligence",
    description="""
    Generate comprehensive competitive intelligence analysis for a channel.

    Features:
    - Automatic competitor discovery (if not provided)
    - Channel profiling and competitive analysis
    - Performance comparison against competitors
    - Market position analysis
    - Opportunity identification
    - Strategic recommendations

    Analysis Depth:
    - **basic**: Quick overview with minimal data
    - **standard**: Comprehensive analysis (recommended)
    - **comprehensive**: Deep dive with all available metrics
    """,
)
async def analyze_competitive_intelligence(
    request: CompetitiveAnalysisRequest,
    service=Depends(get_competitive_service),
) -> CompetitiveAnalysisResponse:
    """
    Generate comprehensive competitive intelligence analysis.

    This endpoint provides a complete competitive intelligence report including:
    - Competitor discovery and profiling
    - Performance benchmarking
    - Market position analysis
    - Opportunity identification
    - Strategic recommendations
    """
    try:
        logger.info(
            f"🎯 Competitive intelligence request for channel {request.channel_id}, "
            f"depth={request.analysis_depth}"
        )

        # Generate competitive intelligence
        intelligence = await service.generate_competitive_intelligence(
            channel_id=request.channel_id,
            competitor_ids=request.competitor_ids,
            analysis_depth=request.analysis_depth,
        )

        if intelligence.get("status") == "analysis_failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Competitive analysis failed: {intelligence.get('error', 'Unknown error')}",
            )

        logger.info(
            f"✅ Competitive intelligence generated for channel {request.channel_id}, "
            f"{intelligence.get('competitors_analyzed', 0)} competitors analyzed"
        )

        return CompetitiveAnalysisResponse(**intelligence)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Competitive intelligence analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitive intelligence analysis failed: {str(e)}",
        )


@router.post(
    "/discover/competitors",
    response_model=CompetitorDiscoveryResponse,
    summary="Discover Competitor Channels",
    description="""
    Automatically discover competitor channels based on similarity analysis.

    Discovery factors:
    - Content similarity
    - Audience overlap
    - Market segment
    - Performance metrics
    - Activity patterns

    Returns ranked list of potential competitors with similarity scores.
    """,
)
async def discover_competitors(
    request: CompetitorDiscoveryRequest,
    service=Depends(get_competitive_service),
) -> CompetitorDiscoveryResponse:
    """
    Discover competitor channels automatically.

    Uses sophisticated algorithms to identify channels that compete
    in similar markets or for similar audiences.
    """
    try:
        logger.info(f"🔎 Discovering competitors for channel {request.channel_id}")

        # Discover competitors
        competitors = await service.discover_competitor_channels(
            channel_id=request.channel_id, max_competitors=request.max_competitors
        )

        response = {
            "channel_id": request.channel_id,
            "competitors_found": len(competitors),
            "competitors": competitors,
            "discovery_timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"✅ Discovered {len(competitors)} competitors for channel {request.channel_id}"
        )

        return CompetitorDiscoveryResponse(**response)

    except Exception as e:
        logger.error(f"❌ Competitor discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitor discovery failed: {str(e)}",
        )


@router.post(
    "/profile/channel",
    response_model=ChannelProfileResponse,
    summary="Get Channel Profile",
    description="""
    Generate comprehensive channel profile for competitive analysis.

    Profile includes:
    - Follower/subscriber metrics
    - Content production metrics
    - Engagement patterns
    - Activity patterns
    - Content characteristics

    Used as foundation for competitive analysis.
    """,
)
async def get_channel_profile(
    request: ChannelProfileRequest,
    service=Depends(get_competitive_service),
) -> ChannelProfileResponse:
    """
    Get comprehensive channel profile.

    Provides detailed profiling of a channel's characteristics,
    content strategy, and performance metrics.
    """
    try:
        logger.info(f"📊 Generating channel profile for {request.channel_id}")

        # Get channel profile
        profile = await service.get_channel_profile(channel_id=request.channel_id)

        if profile.get("status") == "profile_failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Channel profiling failed: {profile.get('error', 'Unknown error')}",
            )

        logger.info(f"✅ Channel profile generated for {request.channel_id}")

        return ChannelProfileResponse(**profile)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Channel profiling failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Channel profiling failed: {str(e)}",
        )


@router.get(
    "/comparison/{channel_id}",
    response_model=dict[str, Any],
    summary="Get Performance Comparison",
    description="""
    Compare channel performance against specified competitors.

    Comparison metrics:
    - Follower growth
    - Content production
    - Engagement rates
    - Activity patterns
    - Market position

    Requires competitor_ids as query parameters.
    """,
)
async def get_performance_comparison(
    channel_id: int,
    competitor_ids: list[int] = Query(..., description="Competitor channel IDs"),
    service=Depends(get_competitive_service),
) -> dict[str, Any]:
    """
    Get performance comparison against competitors.

    Benchmarks channel performance across key metrics
    compared to specified competitor channels.
    """
    try:
        logger.info(
            f"📊 Performance comparison for channel {channel_id} vs {len(competitor_ids)} competitors"
        )

        # Get channel profile
        channel_profile = await service.get_channel_profile(channel_id)

        # Get competitor profiles
        competitor_profiles = []
        for comp_id in competitor_ids:
            profile = await service.get_channel_profile(comp_id)
            competitor_profiles.append(profile)

        # Compare performance
        comparison = await service._compare_performance(channel_id, competitor_ids)

        response = {
            "channel_id": channel_id,
            "channel_profile": channel_profile,
            "competitors_analyzed": len(competitor_ids),
            "competitor_profiles": competitor_profiles,
            "performance_comparison": comparison,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"✅ Performance comparison complete for channel {channel_id}")

        return response

    except Exception as e:
        logger.error(f"❌ Performance comparison failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance comparison failed: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Check Competitive Intelligence Service health and configuration",
)
async def health_check(service=Depends(get_competitive_service)) -> HealthResponse:
    """
    Health check endpoint for Competitive Intelligence Service.

    Returns service status, capabilities, and configuration.
    """
    try:
        health = await service.health_check()
        return HealthResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Service Statistics",
    description="Get Competitive Intelligence Service statistics and capabilities",
)
async def get_stats() -> StatsResponse:
    """
    Get service statistics and information.

    Returns metadata about the Competitive Intelligence Service.
    """
    return StatsResponse(
        service_name="Competitive Intelligence Service",
        version="1.0.0",
        features={
            "competitive_analysis": "Comprehensive competitive intelligence reports",
            "competitor_discovery": "Automatic competitor identification",
            "channel_profiling": "Detailed channel characteristic analysis",
            "performance_comparison": "Multi-channel performance benchmarking",
            "market_analysis": "Market position and opportunity analysis",
            "recommendations": "Strategic competitive recommendations",
        },
        performance={
            "avg_analysis_time": "12-18 seconds",
            "competitor_discovery_speed": "2-3 seconds",
            "profile_generation_time": "3-5 seconds",
        },
        capabilities=[
            "competitive_intelligence",
            "competitor_discovery",
            "channel_profiling",
            "performance_comparison",
            "market_position_analysis",
            "opportunity_identification",
            "competitive_recommendations",
        ],
        status="active",
    )
