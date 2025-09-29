"""
Demo Router - Comprehensive Demo & Mock Data Endpoints
======================================================

Consolidated router for all demo, mock, and educational endpoints.
Includes analytics demos, service demos, and development utilities.

Domain: Demo data, mock services, educational examples, development utilities
Path: /demo/*
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create router with demo prefix
router = APIRouter(
    prefix="/demo",
    tags=["Demo & Development"],
)


# Demo Response Models
class DemoPostDynamicsResponse(BaseModel):
    """Response model for demo post dynamics data"""

    success: bool
    data: dict[str, Any]
    message: str


class DemoTopPostsResponse(BaseModel):
    """Response model for demo top posts data"""

    success: bool
    posts: list[dict[str, Any]]
    total: int


class DemoBestTimeResponse(BaseModel):
    """Response model for demo best time recommendations"""

    success: bool
    recommendations: dict[str, Any]
    optimal_times: list[str]


class DemoAIRecommendationsResponse(BaseModel):
    """Response model for demo AI recommendations"""

    success: bool
    recommendations: list[dict[str, Any]]
    insights: dict[str, Any]


# === DEMO ENDPOINTS ===


@router.get("/post-dynamics", response_model=DemoPostDynamicsResponse)
async def get_demo_post_dynamics(
    channel_id: int = Query(..., description="Channel ID for demo data"),
    days: int = Query(30, description="Number of days for demo data"),
):
    """
    Demo endpoint: Get mock post dynamics data

    Provides sample post engagement dynamics over time for frontend testing.
    """
    try:
        # Generate mock post dynamics data
        demo_data = {
            "channel_id": channel_id,
            "period_days": days,
            "dynamics": [
                {
                    "date": (datetime.now() - timedelta(days=i)).isoformat(),
                    "views": 1500 + (i * 50),
                    "reactions": 120 + (i * 5),
                    "shares": 25 + (i * 2),
                    "comments": 15 + i,
                    "engagement_rate": min(15.0, 8.0 + (i * 0.1)),
                }
                for i in range(days)
            ],
            "summary": {
                "total_views": 45000 + (days * 1500),
                "avg_engagement": 10.5,
                "trend": "increasing",
                "best_performing_time": "18:00-20:00",
            },
        }

        return DemoPostDynamicsResponse(
            success=True,
            data=demo_data,
            message="Demo post dynamics generated successfully",
        )

    except Exception as e:
        logger.error(f"Error generating demo post dynamics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo post dynamics",
        )


@router.get("/top-posts", response_model=DemoTopPostsResponse)
async def get_demo_top_posts(
    channel_id: int = Query(..., description="Channel ID for demo data"),
    limit: int = Query(10, description="Number of top posts to return"),
    period: str = Query("week", description="Time period (day/week/month)"),
):
    """
    Demo endpoint: Get mock top posts data

    Provides sample top-performing posts for frontend testing.
    """
    try:
        # Generate mock top posts data
        posts = []
        for i in range(limit):
            post = {
                "id": f"demo_post_{i + 1}",
                "title": f"Demo Post #{i + 1}: Engaging Content Example",
                "content": f"This is demo content for post {i + 1} showcasing high engagement.",
                "published_at": (datetime.now() - timedelta(days=i)).isoformat(),
                "metrics": {
                    "views": 5000 - (i * 300),
                    "reactions": 400 - (i * 25),
                    "shares": 80 - (i * 5),
                    "comments": 45 - (i * 3),
                    "engagement_rate": max(5.0, 12.5 - (i * 0.8)),
                },
                "performance_score": max(70, 95 - (i * 3)),
            }
            posts.append(post)

        return DemoTopPostsResponse(success=True, posts=posts, total=len(posts))

    except Exception as e:
        logger.error(f"Error generating demo top posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo top posts",
        )


@router.get("/best-time", response_model=DemoBestTimeResponse)
async def get_demo_best_time(
    channel_id: int = Query(..., description="Channel ID for demo data"),
    timezone: str = Query("UTC", description="Timezone for recommendations"),
):
    """
    Demo endpoint: Get mock best time recommendations

    Provides sample optimal posting time recommendations for frontend testing.
    """
    try:
        # Generate mock best time recommendations
        recommendations = {
            "timezone": timezone,
            "analysis_period": "30 days",
            "optimal_posting_windows": [
                {
                    "day": "Monday",
                    "times": ["09:00-11:00", "18:00-20:00"],
                    "engagement_score": 8.5,
                },
                {
                    "day": "Tuesday",
                    "times": ["10:00-12:00", "19:00-21:00"],
                    "engagement_score": 9.2,
                },
                {
                    "day": "Wednesday",
                    "times": ["08:00-10:00", "17:00-19:00"],
                    "engagement_score": 8.8,
                },
                {
                    "day": "Thursday",
                    "times": ["11:00-13:00", "20:00-22:00"],
                    "engagement_score": 9.5,
                },
                {
                    "day": "Friday",
                    "times": ["12:00-14:00", "18:00-20:00"],
                    "engagement_score": 8.9,
                },
                {
                    "day": "Saturday",
                    "times": ["14:00-16:00", "19:00-21:00"],
                    "engagement_score": 7.8,
                },
                {
                    "day": "Sunday",
                    "times": ["15:00-17:00", "20:00-22:00"],
                    "engagement_score": 8.1,
                },
            ],
            "peak_engagement_time": "Thursday 20:00-22:00",
            "audience_activity_pattern": "evening_focused",
        }

        optimal_times = [
            "Thursday 20:00-22:00",
            "Tuesday 19:00-21:00",
            "Friday 18:00-20:00",
        ]

        return DemoBestTimeResponse(
            success=True, recommendations=recommendations, optimal_times=optimal_times
        )

    except Exception as e:
        logger.error(f"Error generating demo best time recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo best time recommendations",
        )


@router.get("/ai-recommendations", response_model=DemoAIRecommendationsResponse)
async def get_demo_ai_recommendations(
    channel_id: int = Query(..., description="Channel ID for demo data"),
    category: str = Query(
        "all", description="Recommendation category (content/timing/engagement/all)"
    ),
):
    """
    Demo endpoint: Get mock AI recommendations

    Provides sample AI-powered content and strategy recommendations for frontend testing.
    """
    try:
        # Generate mock AI recommendations
        recommendations = [
            {
                "id": "rec_1",
                "type": "content",
                "title": "Optimize Visual Content",
                "description": "Posts with images receive 65% more engagement. Consider adding visuals to text-only posts.",
                "priority": "high",
                "impact_score": 8.7,
                "suggested_actions": [
                    "Add relevant images to upcoming posts",
                    "Create infographics for data-heavy content",
                    "Use consistent visual branding",
                ],
            },
            {
                "id": "rec_2",
                "type": "timing",
                "title": "Shift Evening Posting Schedule",
                "description": "Your audience shows highest activity between 7-9 PM. Current posts are mostly during afternoon.",
                "priority": "medium",
                "impact_score": 7.3,
                "suggested_actions": [
                    "Schedule more posts for 7-9 PM window",
                    "Test weekend morning slots",
                    "Reduce afternoon posting frequency",
                ],
            },
            {
                "id": "rec_3",
                "type": "engagement",
                "title": "Increase Interactive Elements",
                "description": "Posts with questions or polls generate 40% more comments and shares.",
                "priority": "high",
                "impact_score": 9.1,
                "suggested_actions": [
                    "End posts with engaging questions",
                    "Create weekly polls on relevant topics",
                    "Respond to comments within 2 hours",
                ],
            },
            {
                "id": "rec_4",
                "type": "content",
                "title": "Diversify Content Types",
                "description": "Current content is 80% text. Mixed content types perform better.",
                "priority": "medium",
                "impact_score": 6.8,
                "suggested_actions": [
                    "Share behind-the-scenes content",
                    "Create video summaries of popular posts",
                    "Post user-generated content",
                ],
            },
        ]

        insights = {
            "channel_performance": "above_average",
            "growth_trend": "steady_increase",
            "engagement_health": "good",
            "content_strategy_score": 7.5,
            "optimization_potential": "25% improvement possible",
            "key_strengths": [
                "Consistent posting schedule",
                "High-quality content",
                "Good audience retention",
            ],
            "improvement_areas": [
                "Visual content integration",
                "Posting time optimization",
                "Interactive engagement",
            ],
        }

        # Filter by category if specified
        if category != "all":
            recommendations = [r for r in recommendations if r["type"] == category]

        return DemoAIRecommendationsResponse(
            success=True, recommendations=recommendations, insights=insights
        )

    except Exception as e:
        logger.error(f"Error generating demo AI recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate demo AI recommendations",
        )


# === CLEAN ARCHITECTURE DEMO ENDPOINTS ===
# Migrated from clean_analytics_router.py for consolidated demo functionality


@router.get("/status")
async def service_status():
    """Service status check - Clean architecture demo"""
    from apps.api.di import configure_services, container

    if not getattr(container, "_initialized", True):
        configure_services()

    # Use mock health check for demo
    health_results = {
        "status": "healthy",
        "services": {
            "database": "connected",
            "cache": "connected",
            "telegram": "connected",
        },
    }

    return {
        "status": "healthy",
        "services": health_results,
        "clean_architecture": True,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/admin/stats")
async def get_admin_stats():
    """Get admin statistics using DI container - Clean architecture demo"""
    from apps.api.di import configure_services, container
    from config.demo_mode_config import demo_config
    from core.protocols import AdminServiceProtocol

    if not getattr(container, "_initialized", True):
        configure_services(container, demo_config)

    admin_service = container.get_service(AdminServiceProtocol)
    stats = await admin_service.get_system_stats()

    return {
        "system_stats": stats,
        "service_used": admin_service.get_service_name(),
        "clean_architecture": True,
    }


@router.get("/auth/permissions/{user_id}")
async def get_user_permissions(user_id: int):
    """Get user permissions using DI container - Clean architecture demo"""
    from apps.api.di import configure_services, container
    from config.demo_mode_config import demo_config
    from core.protocols import AuthServiceProtocol

    if not getattr(container, "_initialized", True):
        configure_services(container, demo_config)

    auth_service = container.get_service(AuthServiceProtocol)
    permissions = await auth_service.get_user_permissions(user_id)
    is_demo = await auth_service.is_demo_user(user_id)

    return {
        "user_id": user_id,
        "permissions": permissions,
        "is_demo_user": is_demo,
        "service_used": auth_service.get_service_name(),
        "clean_architecture": True,
    }


@router.get("/ai/suggestions")
async def get_ai_suggestions_demo(topic: str = "technology"):
    """Get AI content suggestions using DI container - Clean architecture demo"""
    from apps.api.di import configure_services, container
    from config.demo_mode_config import demo_config
    from core.protocols import AIServiceProtocol

    if not getattr(container, "_initialized", True):
        configure_services(container, demo_config)

    ai_service = container.get_service(AIServiceProtocol)
    suggestions = await ai_service.generate_content_suggestions("demo_channel", topic)

    return {
        "topic": topic,
        "suggestions": suggestions,
        "service_used": ai_service.get_service_name(),
        "clean_architecture": True,
    }


# === HEALTH CHECK ===


@router.get("/health")
async def demo_health_check():
    """Health check endpoint for consolidated demo router"""
    return {
        "status": "healthy",
        "service": "demo_router",
        "endpoint_categories": {
            "analytics_demos": [
                "/demo/post-dynamics",
                "/demo/top-posts",
                "/demo/best-time",
                "/demo/ai-recommendations",
            ],
            "clean_architecture_demos": [
                "/demo/status",
                "/demo/admin/stats",
                "/demo/auth/permissions/{user_id}",
                "/demo/ai/suggestions",
            ],
            "utility": ["/demo/health"],
        },
        "timestamp": datetime.now().isoformat(),
    }
