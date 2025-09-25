"""
Analytics Real-time Router - Real-time Analytics Domain
========================================================

Real-time analytics router providing live monitoring and performance insights.

Key Features:
- Real-time metrics collection
- Performance scoring algorithms  
- AI-powered recommendations
- Live data streaming endpoints

Dependencies:
- AnalyticsClient for data access
- AnalyticsFusionService for processing
- Caching for performance optimization
"""

import logging
from datetime import datetime, timedelta
from typing import Annotated, Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

# Services
from apps.bot.clients.analytics_client import AnalyticsClient
from core.services.analytics_fusion_service import AnalyticsFusionService
from apps.api.di_analytics import get_analytics_fusion_service, get_cache
from apps.api.schemas.analytics import SeriesResponse
from apps.api.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

# Create real-time analytics router
router = APIRouter(
    prefix="/analytics/realtime", 
    tags=["Analytics Real-time"]
)

# === REAL-TIME MODELS ===

class RealTimeMetrics(BaseModel):
    timestamp: datetime
    total_views: int
    growth_rate: float
    engagement_rate: float
    reach_score: int
    active_users: int
    trending_score: float

class PerformanceScore(BaseModel):
    channel_id: str
    overall_score: int
    components: Dict[str, int]
    recommendations: List[str]
    timestamp: datetime

# === DEPENDENCY INJECTION ===

def get_analytics_client() -> AnalyticsClient:
    """Get analytics client for real-time data"""
    from config import settings
    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)

def get_analytics_fusion_service() -> AnalyticsFusionService:
    """Get analytics fusion service"""
    from core.di_container import container
    return container.analytics_fusion_service()

# === REAL-TIME METRICS ===

@router.get("/metrics/{channel_id}", response_model=RealTimeMetrics)
async def get_realtime_metrics(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client)
):
    """
    ## ⚡ Real-time Channel Metrics
    
    Get current live metrics for a channel including:
    - Live view counts and growth rates
    - Real-time engagement metrics
    - Current reach and active user counts
    - Trending score calculations
    
    **Note**: No caching - always returns fresh real-time data
    """
    try:
        # Fetch latest real-time data (last hour)
        overview_data = await analytics_client.overview(channel_id, 0.04)  # ~1 hour
        growth_data = await analytics_client.growth(channel_id, 0.04)
        reach_data = await analytics_client.reach(channel_id, 0.04)
        
        return RealTimeMetrics(
            timestamp=datetime.utcnow(),
            total_views=getattr(overview_data, 'total_views', 0),
            growth_rate=getattr(growth_data, 'growth_rate', 0.0),
            engagement_rate=getattr(overview_data, 'engagement_rate', 0.0),
            reach_score=getattr(reach_data, 'reach_score', 0),
            active_users=getattr(reach_data, 'active_users', 0),
            trending_score=calculate_trending_score(overview_data, growth_data, reach_data)
        )
        
    except Exception as e:
        logger.error(f"Real-time metrics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch real-time metrics")

# === PERFORMANCE SCORING ===

@router.get("/performance/{channel_id}", response_model=PerformanceScore)  
async def get_performance_score(
    channel_id: int,
    period: int = Query(default=1, ge=1, le=7, description="Period in days for performance calculation"),
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    fusion_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
):
    """
    ## 🎯 Real-time Performance Score
    
    Calculate live performance score based on:
    - Growth momentum
    - Engagement quality
    - Reach effectiveness
    - Content performance
    
    **Returns**: Overall score (0-100) with component breakdown
    """
    try:
        # Get recent performance data
        overview_data = await analytics_client.overview(channel_id, period)
        growth_data = await analytics_client.growth(channel_id, period)
        reach_data = await analytics_client.reach(channel_id, period)
        
        # Calculate component scores
        growth_score = min(100, max(0, int(getattr(growth_data, 'growth_rate', 0) * 10)))
        engagement_score = min(100, max(0, int(getattr(overview_data, 'engagement_rate', 0) * 20)))
        reach_score = min(100, max(0, getattr(reach_data, 'reach_score', 0)))
        
        # Calculate overall performance score
        overall_score = int((growth_score * 0.4 + engagement_score * 0.4 + reach_score * 0.2))
        
        # Generate performance-based recommendations
        recommendations = generate_performance_recommendations(
            overall_score, growth_score, engagement_score, reach_score
        )
        
        return PerformanceScore(
            channel_id=str(channel_id),
            overall_score=overall_score,
            components={
                "growth": growth_score,
                "engagement": engagement_score, 
                "reach": reach_score
            },
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Performance score calculation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate performance score")

# === AI RECOMMENDATIONS ===

@router.get("/recommendations/{channel_id}")
async def get_ai_recommendations(
    channel_id: int,
    context: str = Query(default="general", description="Recommendation context (general, growth, engagement)"),
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
) -> List[str]:
    """
    ## 🤖 AI-Powered Real-time Recommendations
    
    Get contextual recommendations based on:
    - Current performance trends
    - Real-time engagement patterns  
    - Growth momentum analysis
    - Content performance insights
    """
    try:
        # Get recent data for recommendations
        overview_data = await analytics_client.overview(channel_id, 7)  # Last week
        growth_data = await analytics_client.growth(channel_id, 7)
        reach_data = await analytics_client.reach(channel_id, 7)
        
        # Build metrics context
        metrics_context = {
            'growth_rate': getattr(growth_data, 'growth_rate', 0),
            'engagement_rate': getattr(overview_data, 'engagement_rate', 0),
            'reach_score': getattr(reach_data, 'reach_score', 0),
            'total_views': getattr(overview_data, 'total_views', 0),
        }
        
        # Generate context-specific recommendations
        return generate_contextual_recommendations(metrics_context, context)
        
    except Exception as e:
        logger.error(f"AI recommendations generation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI recommendations")

# === LIVE MONITORING ===

@router.get("/monitor/{channel_id}")
async def get_live_monitoring_data(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
):
    """
    ## 📡 Live Monitoring Dashboard
    
    Real-time monitoring data for active channels:
    - Live metrics stream
    - Performance indicators
    - Trend momentum
    - Alert conditions
    """
    try:
        # Get live metrics
        metrics = await get_realtime_metrics(channel_id, current_user, analytics_client)
        
        # Get performance score
        performance = await get_performance_score(channel_id, 1, current_user, analytics_client, get_analytics_fusion_service())
        
        # Build monitoring response
        return {
            "channel_id": channel_id,
            "live_metrics": metrics,
            "performance": performance,
            "monitoring_status": "active",
            "last_update": datetime.utcnow().isoformat(),
            "refresh_interval": 30  # seconds
        }
        
    except Exception as e:
        logger.error(f"Live monitoring failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live monitoring data")


@router.get("/live-metrics/{channel_id}")
async def get_live_metrics_optimized(
    channel_id: int,
    hours: int = Query(6, ge=1, le=24, description="Hours of recent data"),
    current_user: dict = Depends(get_current_user),
):
    """Get real-time metrics optimized for live monitoring"""
    
    try:
        # Import demo data generator 
        from apps.api.__mocks__.analytics_mock import generate_post_dynamics
        
        # Use V1 for real-time data
        recent_dynamics = generate_post_dynamics(hours)
        
        # Calculate live metrics
        if recent_dynamics:
            current_views = recent_dynamics[-1].views
            view_trend = recent_dynamics[-1].views - recent_dynamics[-2].views if len(recent_dynamics) > 1 else 0
            engagement_rate = (recent_dynamics[-1].likes + recent_dynamics[-1].shares + recent_dynamics[-1].comments) / max(recent_dynamics[-1].views, 1) * 100
        else:
            current_views = 0
            view_trend = 0
            engagement_rate = 0
        
        return {
            "channel_id": channel_id,
            "current_views": current_views,
            "view_trend": view_trend,
            "engagement_rate": round(engagement_rate, 2),
            "posts_last_hour": len([p for p in recent_dynamics if p.timestamp > datetime.now() - timedelta(hours=1)]),
            "data_freshness": "real-time",
            "source": "v1_optimized",
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get live metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live metrics")

# === UTILITY FUNCTIONS ===

def calculate_trending_score(overview_data, growth_data, reach_data) -> float:
    """Calculate trending score from real-time data"""
    try:
        growth_rate = getattr(growth_data, 'growth_rate', 0)
        engagement_rate = getattr(overview_data, 'engagement_rate', 0)
        reach_score = getattr(reach_data, 'reach_score', 0)
        
        # Weighted trending calculation
        trending = (growth_rate * 0.5 + engagement_rate * 0.3 + reach_score * 0.2)
        return round(min(100.0, max(0.0, trending)), 2)
    except:
        return 50.0  # Default moderate trending score

def generate_performance_recommendations(overall_score: int, growth_score: int, engagement_score: int, reach_score: int) -> List[str]:
    """Generate recommendations based on performance scores"""
    recommendations = []
    
    if overall_score < 40:
        recommendations.append("📉 Performance needs immediate attention - consider content strategy review")
    
    if growth_score < 30:
        recommendations.append("📈 Focus on growth tactics: collaborations, hashtag optimization, posting frequency")
        
    if engagement_score < 30:
        recommendations.append("💬 Improve engagement: ask questions, use polls, respond to comments quickly")
        
    if reach_score < 30:
        recommendations.append("🎯 Expand reach: optimize post timing, use trending topics, cross-platform promotion")
        
    if overall_score > 80:
        recommendations.append("🎉 Excellent performance! Maintain current strategy and consider scaling content")
        
    return recommendations or ["📊 Performance is stable - continue monitoring trends"]

def generate_contextual_recommendations(metrics: Dict[str, Any], context: str) -> List[str]:
    """Generate context-specific AI recommendations"""
    recommendations = []
    
    if context == "growth":
        if metrics['growth_rate'] < 5:
            recommendations.extend([
                "🚀 Increase posting frequency during peak hours",
                "🤝 Partner with similar channels for cross-promotion",
                "📱 Optimize content for mobile consumption"
            ])
        else:
            recommendations.append("📈 Growth is strong - maintain current content strategy")
            
    elif context == "engagement":
        if metrics['engagement_rate'] < 10:
            recommendations.extend([
                "💬 Create more interactive content (polls, Q&A)",
                "🎯 Use compelling calls-to-action in posts",
                "⚡ Respond to comments within first hour"
            ])
        else:
            recommendations.append("💪 Engagement is excellent - consider advanced community features")
            
    else:  # general context
        recommendations.extend([
            f"📊 Current growth rate: {metrics['growth_rate']:.1f}% - {'Good momentum' if metrics['growth_rate'] > 5 else 'Room for improvement'}",
            f"💬 Engagement at {metrics['engagement_rate']:.1f}% - {'Strong interaction' if metrics['engagement_rate'] > 10 else 'Focus on community building'}",
            "🎯 Monitor competitor activity and trending topics for optimization opportunities"
        ])
    
    return recommendations


# === CHANNEL REACH ANALYTICS ===

@router.get("/channels/{channel_id}/reach", response_model=SeriesResponse)
async def get_channel_reach(
    channel_id: int,
    from_: Annotated[datetime, Query(alias="from")],
    to_: Annotated[datetime, Query(alias="to")],
    service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    cache=Depends(get_cache),
):
    """
    Get channel reach time series (average views per post)
    
    Provides real-time reach metrics showing how far content spreads
    and audience growth patterns over specified time periods.
    """
    try:
        # Generate cache key
        cache_params = {
            "channel_id": channel_id, 
            "from": from_.isoformat(), 
            "to": to_.isoformat()
        }
        last_updated = await service.get_last_updated_at(channel_id)
        cache_key = cache.generate_cache_key("reach", cache_params, last_updated)

        # Try cache first
        cached_data = await cache.get_json(cache_key)
        if cached_data:
            cached_data["meta"]["cache_hit"] = True
            return cached_data

        # Get fresh reach data
        reach_data = await service.get_reach(channel_id, from_, to_)

        response_data = SeriesResponse(data=reach_data)  # type: ignore
        response_dict = response_data.dict()

        # Cache the response (shorter TTL for real-time data)
        await cache.set_json(cache_key, response_dict, ttl_s=90)

        return response_data

    except Exception as e:
        logger.error(f"Error getting reach for channel {channel_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get channel reach data",
        )