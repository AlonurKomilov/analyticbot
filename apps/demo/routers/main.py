"""
Demo Router - Project Showcase Endpoints
=========================================

Main router for all user-facing demonstration endpoints.
Provides comprehensive showcase of project capabilities for new users.

Path: /demo/*
Purpose: Professional demonstration of all pr        from apps.demo.services.sample_data_service import sample_data_service

        best_times_data = await sample_data_service.generate_best_times_data(channel_id, timezone)ct features
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create router with demo prefix
router = APIRouter(
    prefix="/demo",
    tags=["Project Demo"],
)


# Demo Response Models
class DemoPostDynamicsResponse(BaseModel):
    """Response model for demo post dynamics data"""

    success: bool
    data: dict[str, Any]
    message: str
    demo_info: dict[str, Any]


class DemoTopPostsResponse(BaseModel):
    """Response model for demo top posts data"""

    success: bool
    posts: list[dict[str, Any]]
    total: int
    demo_info: dict[str, Any]


class DemoBestTimeResponse(BaseModel):
    """Response model for demo best time recommendations"""

    success: bool
    recommendations: dict[str, Any]
    optimal_times: list[str]
    demo_info: dict[str, Any]


class DemoAIRecommendationsResponse(BaseModel):
    """Response model for demo AI recommendations"""

    success: bool
    recommendations: list[dict[str, Any]]
    insights: dict[str, Any]
    demo_info: dict[str, Any]


class DemoProjectInfoResponse(BaseModel):
    """Response model for project information"""

    success: bool
    project: dict[str, Any]
    capabilities: list[str]
    demo_features: list[str]


# === SHOWCASE ENDPOINTS ===


@router.get("/", response_model=DemoProjectInfoResponse)
async def get_project_showcase():
    """
    Main demo endpoint: Project overview and capabilities

    Perfect entry point for new users to understand what this project does.
    """
    try:
        from apps.demo.config import demo_config

        project_info = {
            "name": "AnalyticBot",
            "description": "Advanced Telegram analytics and automation platform",
            "version": "2.0.0",
            "architecture": "Clean Architecture with FastAPI",
            "database": "PostgreSQL with Redis caching",
            "key_features": [
                "Real-time analytics dashboard",
                "AI-powered content recommendations",
                "Automated posting optimization",
                "Advanced user engagement tracking",
                "Multi-channel management",
                "Custom reporting and insights",
            ],
            "target_users": [
                "Telegram channel owners",
                "Social media managers",
                "Content creators",
                "Marketing professionals",
                "Data analysts",
            ],
            "demo_quality": demo_config.get_demo_quality_level(),
        }

        capabilities = [
            "Analytics Dashboard",
            "Content Management",
            "AI Recommendations",
            "User Management",
            "Automated Reporting",
            "API Integration",
            "Real-time Monitoring",
            "Performance Optimization",
        ]

        demo_features = [
            "Interactive analytics with 30 days of sample data",
            "AI-powered content suggestions",
            "Best posting time recommendations",
            "Top performing posts analysis",
            "User engagement insights",
            "Clean Architecture demonstration",
            "API documentation and examples",
        ]

        return DemoProjectInfoResponse(
            success=True,
            project=project_info,
            capabilities=capabilities,
            demo_features=demo_features,
        )

    except Exception as e:
        logger.error(f"Error generating project showcase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate project showcase",
        )


@router.get("/analytics/post-dynamics", response_model=DemoPostDynamicsResponse)
async def get_demo_post_dynamics(
    channel_id: int = Query(1, description="Channel ID for demo data"),
    days: int = Query(30, description="Number of days for demo data"),
):
    """
    Demo Analytics: Post engagement dynamics over time

    Shows sample post performance metrics and trends that would be available
    with real data. Perfect for demonstrating analytics capabilities.
    """
    try:
        from apps.demo.services.sample_data_service import sample_data_service

        # Generate sample engagement dynamics
        sample_dynamics = await sample_data_service.generate_post_dynamics_data(
            channel_id=channel_id, days=days
        )

        demo_info = {
            "data_type": "sample_generated",
            "note": "Real system tracks actual post engagement over time",
            "features_demonstrated": [
                "Time-based analytics",
                "Engagement trends",
                "Performance metrics",
                "Growth indicators",
            ],
        }

        return DemoPostDynamicsResponse(
            success=True,
            data=sample_dynamics,
            message="Demo post dynamics generated successfully",
            demo_info=demo_info,
        )

    except Exception as e:
        logger.error(f"Demo post dynamics error: {e}")
        return DemoPostDynamicsResponse(
            success=False,
            data={},
            message=f"Demo data generation failed: {e}",
            demo_info={"error": "Demo data generation failed"},
        )


@router.get("/analytics/top-posts", response_model=DemoTopPostsResponse)
async def get_demo_top_posts(
    channel_id: int = Query(1, description="Channel ID for demo data"),
    limit: int = Query(15, description="Number of top posts to return"),
    period: str = Query("week", description="Time period (day/week/month)"),
):
    """
    Demo Analytics: Top performing posts

    Showcases how the system identifies and ranks top-performing content.
    Includes realistic engagement metrics and performance indicators.
    """
    try:
        from apps.demo.services.sample_data_service import sample_data_service

        posts = await sample_data_service.generate_top_posts_data(channel_id, limit, period)

        demo_info = {
            "data_type": "curated_samples",
            "metrics_included": ["views", "reactions", "shares", "comments", "engagement_rate"],
            "ranking_algorithm": "engagement_score_weighted",
            "note": "Real system uses ML algorithms to identify optimal content patterns",
        }

        return DemoTopPostsResponse(
            success=True, posts=posts, total=len(posts), demo_info=demo_info
        )

    except Exception as e:
        logger.error(f"Error generating demo top posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo top posts",
        )


@router.get("/ai/recommendations", response_model=DemoAIRecommendationsResponse)
async def get_demo_ai_recommendations(
    channel_id: int = Query(1, description="Channel ID for demo data"),
    category: str = Query("all", description="Recommendation category"),
):
    """
    Demo AI: Content and strategy recommendations

    Demonstrates AI-powered insights that help optimize content strategy.
    Shows real-world recommendations based on performance patterns.
    """
    try:
        from apps.demo.services.sample_data_service import sample_data_service

        recommendations_data = await sample_data_service.generate_ai_recommendations(
            channel_id, category
        )

        demo_info = {
            "ai_model": "content_optimization_v2",
            "analysis_scope": "30_day_performance_window",
            "recommendation_types": ["content", "timing", "engagement", "strategy"],
            "confidence_threshold": "85%",
            "note": "Production system uses advanced ML models trained on successful content patterns",
        }

        return DemoAIRecommendationsResponse(
            success=True,
            recommendations=recommendations_data["recommendations"],
            insights=recommendations_data["insights"],
            demo_info=demo_info,
        )

    except Exception as e:
        logger.error(f"Error generating demo AI recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo AI recommendations",
        )


@router.get("/analytics/best-times", response_model=DemoBestTimeResponse)
async def get_demo_best_posting_times(
    channel_id: int = Query(1, description="Channel ID for demo data"),
    timezone: str = Query("UTC", description="Timezone for recommendations"),
):
    """
    Demo Analytics: Optimal posting time recommendations

    Shows AI-driven analysis of when your audience is most active.
    Includes day-by-day recommendations and engagement predictions.
    """
    try:
        from apps.demo.services.sample_data_service import sample_data_service

        timing_data = await sample_data_service.generate_best_times_data(channel_id, timezone)

        demo_info = {
            "analysis_method": "audience_activity_ml_model",
            "data_sources": [
                "historical_engagement",
                "user_activity_patterns",
                "content_performance",
            ],
            "timezone_support": "global_timezone_aware",
            "update_frequency": "daily_recalculation",
            "note": "Real system analyzes your specific audience patterns for personalized recommendations",
        }

        return DemoBestTimeResponse(
            success=True,
            recommendations=timing_data["recommendations"],
            optimal_times=timing_data["optimal_times"],
            demo_info=demo_info,
        )

    except Exception as e:
        logger.error(f"Error generating demo best times: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo best times",
        )


# === ARCHITECTURE DEMONSTRATION ===


@router.get("/architecture/clean-demo")
async def demonstrate_clean_architecture():
    """
    Demo: Clean Architecture implementation

    Shows how the project uses proper dependency injection and layer separation.
    Demonstrates the difference between real and demo services.
    """
    try:
        # ✅ MIGRATED: Use unified DI container from apps/di
        from apps.di import get_container

        container = get_container()

        # Demonstrate service resolution through DI - get analytics service as example
        try:
            analytics_service = await container.core_services.analytics_fusion_service()
            service_info = {
                "type": "AnalyticsFusionService",
                "status": "available"
            }
        except Exception as e:
            service_info = {
                "type": "unavailable",
                "status": f"error: {str(e)}"
            }

        # Get sample data - simplified for demo
        admin_stats = {
            "total_users": 150,
            "active_channels": 45,
            "total_posts": 1200
        }
        sample_permissions = ["read:analytics", "write:posts", "manage:channels"]

        return {
            "architecture_pattern": "Clean Architecture",
            "dependency_injection": "dependency-injector library (apps/di)",
            "layer_separation": {
                "apps": "FastAPI routers and endpoints",
                "infra": "Database adapters and external services",
                "core": "Business logic and domain models",
            },
            "di_container": {
                "type": "ApplicationContainer",
                "location": "apps/di/",
                "services_available": service_info,
            },
            "sample_data": {"admin_stats": admin_stats, "user_permissions": sample_permissions},
            "benefits": [
                "Testable business logic",
                "Swappable implementations",
                "Clear separation of concerns",
                "Easy to mock and demo",
            ],
        }

    except Exception as e:
        logger.error(f"Error demonstrating clean architecture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to demonstrate clean architecture",
        )


# === HEALTH AND STATUS ===


@router.get("/health")
async def demo_health_check():
    """Health check for demo functionality"""
    from apps.demo.config import demo_config

    return {
        "status": "healthy",
        "service": "demo_showcase",
        "demo_config": {
            "enabled": demo_config.is_demo_enabled(),
            "strategy": demo_config.DEMO_STRATEGY.value,
            "quality_level": demo_config.get_demo_quality_level(),
        },
        "available_endpoints": {
            "project_overview": "/demo/",
            "analytics_demo": [
                "/demo/analytics/post-dynamics",
                "/demo/analytics/top-posts",
                "/demo/analytics/best-times",
            ],
            "ai_demo": "/demo/ai/recommendations",
            "architecture_demo": "/demo/architecture/clean-demo",
        },
        "timestamp": datetime.now().isoformat(),
    }
