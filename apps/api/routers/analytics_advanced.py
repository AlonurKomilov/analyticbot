"""
Advanced Analytics API v2 - Enhanced Endpoints
Real-time analytics with alerting and advanced metrics
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user
from apps.shared.models.alerts import AlertEvent as SharedAlertEvent, AlertRule
from apps.bot.clients.analytics_v2_client import AnalyticsV2Client
from core.services.analytics_fusion_service import AnalyticsFusionService
from apps.bot.services.alerting_service import AlertingService
from apps.bot.container import Container
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics/advanced", tags=["Advanced Analytics"])


# Enhanced Response Models
class RealTimeMetrics(BaseModel):
    timestamp: datetime
    total_views: int
    growth_rate: float
    engagement_rate: float
    reach_score: int
    active_users: int
    trending_score: float


# Alert models imported from apps.shared.models.alerts
AlertEvent = SharedAlertEvent  # Type alias for consistency


class AdvancedAnalyticsResponse(BaseModel):
    channel_id: str
    period: str
    real_time_metrics: RealTimeMetrics
    trend_analysis: Dict[str, Any]
    performance_score: int
    alerts: List[AlertEvent]
    recommendations: List[str]


def get_analytics_client() -> AnalyticsV2Client:
    """Get analytics client instance"""
    return AnalyticsV2Client(settings.ANALYTICS_V2_BASE_URL)


def get_analytics_fusion_service() -> AnalyticsFusionService:
    """Get analytics fusion service instance (now includes performance analytics)"""
    container = Container()
    return container.analytics_fusion_service()


def get_alerting_service() -> AlertingService:
    """Get alerting service instance"""
    container = Container()
    return container.alerting_service()



def generate_recommendations(metrics: Dict[str, Any], alerts: List[AlertEvent]) -> List[str]:
    """Generate AI-powered recommendations based on current metrics and alerts"""
    recommendations = []
    
    try:
        growth_rate = metrics.get('growth_rate', 0)
        engagement_rate = metrics.get('engagement_rate', 0)
        reach_score = metrics.get('reach_score', 0)
        
        # Growth recommendations
        if growth_rate < 5:
            recommendations.append("📈 Consider posting more frequently to boost growth")
            recommendations.append("🎯 Try posting during peak hours (6-9 PM) for better reach")
        elif growth_rate > 20:
            recommendations.append("🚀 Excellent growth! Maintain current posting strategy")
        
        # Engagement recommendations
        if engagement_rate < 3:
            recommendations.append("💬 Add more interactive content (polls, questions) to boost engagement")
            recommendations.append("🖼️ Use more visual content - images and videos perform better")
        elif engagement_rate > 8:
            recommendations.append("⭐ Amazing engagement! Consider creating premium content")
        
        # Reach recommendations
        if reach_score < 50:
            recommendations.append("📢 Use trending hashtags to improve content discoverability")
            recommendations.append("🔗 Cross-promote on other social platforms")
        
        # Alert-based recommendations
        for alert in alerts:
            if alert.severity == 'warning' and 'engagement' in alert.rule_id:
                recommendations.append("⚠️ Low engagement detected - review recent post performance")
            elif alert.severity == 'success' and 'growth' in alert.rule_id:
                recommendations.append("🎉 Growth spike! Analyze what content drove this success")
        
        # Always provide at least one recommendation
        if not recommendations:
            recommendations.append("📊 Your analytics look stable. Keep monitoring for optimization opportunities")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return ["📊 Unable to generate recommendations at this time"]




@router.get("/dashboard/{channel_id}")
async def get_advanced_dashboard(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    include_alerts: bool = Query(default=True),
    include_recommendations: bool = Query(default=True),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    analytics_fusion_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
    alerting_service: AlertingService = Depends(get_alerting_service),
) -> AdvancedAnalyticsResponse:
    """Get comprehensive advanced analytics dashboard data"""
    
    try:
        # Fetch base analytics data
        overview_data = await analytics_client.overview(channel_id, period)
        growth_data = await analytics_client.growth(channel_id, period)
        reach_data = await analytics_client.reach(channel_id, period)
        
        # Combine metrics
        combined_metrics = {
            'total_views': overview_data.overview.total_views,
            'growth_rate': growth_data.growth.growth_rate,
            'engagement_rate': overview_data.overview.engagement_rate,
            'reach_score': reach_data.reach.view_reach_ratio,  # Use view_reach_ratio as reach_score
            'active_users': reach_data.reach.unique_viewers,
        }
        
        # Create real-time metrics
        # Create real-time metrics  
        real_time_metrics = RealTimeMetrics(
            timestamp=datetime.utcnow(),
            total_views=overview_data.overview.total_views,
            growth_rate=0,  # overview_data doesn't have growth_rate
            engagement_rate=overview_data.overview.engagement_rate,
            reach_score=0,  # overview_data doesn't have reach_score
            active_users=0,  # overview_data doesn't have active_users
            trending_score=50.0  # Placeholder for trending algorithm
        )
        
        # Generate alerts if requested
        alerts = []
        if include_alerts:
            alerts = alerting_service.check_alert_conditions(combined_metrics, channel_id)
        
        # Generate recommendations if requested
        recommendations = []
        if include_recommendations:
            recommendations = generate_recommendations(combined_metrics, alerts)
        
        # Calculate performance score
        performance_score = analytics_fusion_service.calculate_performance_score(combined_metrics)
        
        # Trend analysis (simplified)
        trend_analysis = {
            'weekly_trend': 'upward' if combined_metrics['growth_rate'] > 0 else 'downward',
            'engagement_trend': 'improving' if combined_metrics['engagement_rate'] > 5 else 'needs_attention',
            'consistency_score': 78,  # Placeholder
            'peak_hours': ['18:00', '19:00', '20:00'],
            'best_content_types': ['images', 'videos', 'polls']
        }
        
        return AdvancedAnalyticsResponse(
            channel_id=channel_id,
            period=f"{period}d",
            real_time_metrics=real_time_metrics,
            trend_analysis=trend_analysis,
            performance_score=performance_score,
            alerts=alerts,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error fetching advanced dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch advanced analytics")


@router.get("/metrics/real-time/{channel_id}")
async def get_real_time_metrics(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client)
):
    """Get current realtime metrics for a channel"""
    
    try:
        # Fetch latest data
        overview_data = await analytics_client.overview(channel_id, 1)  # Last day
        
        return RealTimeMetrics(
            timestamp=datetime.utcnow(),
            total_views=getattr(overview_data, 'total_views', 0),
            growth_rate=getattr(overview_data, 'growth_rate', 0),
            engagement_rate=getattr(overview_data, 'engagement_rate', 0),
            reach_score=getattr(overview_data, 'reach_score', 0),
            active_users=getattr(overview_data, 'active_users', 0),
            trending_score=getattr(overview_data, 'trending_score', 50.0)
        )
        
    except Exception as e:
        logger.error(f"Error fetching real-time metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch real-time metrics")


@router.get("/alerts/check/{channel_id}")
async def check_alerts(
    channel_id: str,
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    alerting_service: AlertingService = Depends(get_alerting_service),
) -> List[AlertEvent]:
    """Check for active alerts for a channel"""
    
    try:
        # Get current metrics
        overview_data = await analytics_client.overview(channel_id, 1)
        growth_data = await analytics_client.growth(channel_id, 1)
        reach_data = await analytics_client.reach(channel_id, 1)
        
        combined_metrics = {
            'growth_rate': getattr(growth_data, 'growth_rate', 0),
            'engagement_rate': getattr(overview_data, 'engagement_rate', 0),
            'reach_score': getattr(reach_data, 'reach_score', 0),
        }
        
        return alerting_service.check_alert_conditions(combined_metrics, channel_id)
        
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to check alerts")


@router.get("/recommendations/{channel_id}")
async def get_recommendations(
    channel_id: str,
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    alerting_service: AlertingService = Depends(get_alerting_service),
) -> List[str]:
    """Get AI-powered recommendations for a channel"""
    
    try:
        # Get current metrics
        overview_data = await analytics_client.overview(channel_id, 7)  # Last week
        growth_data = await analytics_client.growth(channel_id, 7)
        reach_data = await analytics_client.reach(channel_id, 7)
        
        combined_metrics = {
            'growth_rate': getattr(growth_data, 'growth_rate', 0),
            'engagement_rate': getattr(overview_data, 'engagement_rate', 0),
            'reach_score': getattr(reach_data, 'reach_score', 0),
        }
        
        # Get any active alerts for context
        alerts = alerting_service.check_alert_conditions(combined_metrics, channel_id)
        
        return generate_recommendations(combined_metrics, alerts)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get("/performance/score/{channel_id}")
async def get_performance_score(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    analytics_fusion_service: AnalyticsFusionService = Depends(get_analytics_fusion_service),
) -> Dict[str, Any]:
    """Get detailed performance score breakdown"""
    
    try:
        # Get metrics for the period
        overview_data = await analytics_client.overview(channel_id, period)
        growth_data = await analytics_client.growth(channel_id, period)
        reach_data = await analytics_client.reach(channel_id, period)
        
        metrics = {
            'growth_rate': getattr(growth_data, 'growth_rate', 0),
            'engagement_rate': getattr(overview_data, 'engagement_rate', 0),
            'reach_score': getattr(reach_data, 'reach_score', 0),
        }
        
        # Calculate individual scores
        growth_score = min(100, max(0, (metrics['growth_rate'] / 20) * 100))
        engagement_score = min(100, max(0, (metrics['engagement_rate'] / 10) * 100))
        reach_score = metrics['reach_score']
        consistency_score = 75  # Placeholder
        
        overall_score = analytics_fusion_service.calculate_performance_score(metrics)
        
        return {
            'overall_score': overall_score,
            'breakdown': {
                'growth': int(growth_score),
                'engagement': int(engagement_score),
                'reach': int(reach_score),
                'consistency': int(consistency_score),
            },
            'grade': 'A' if overall_score >= 80 else 'B' if overall_score >= 60 else 'C',
            'period': f"{period} days",
            'last_updated': datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate performance score")
