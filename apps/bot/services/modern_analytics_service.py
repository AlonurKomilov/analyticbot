"""
Modern Analytics Service with Adapter Pattern
High-level analytics operations using adapter pattern for mock/real data separation
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from apps.bot.services.adapters.analytics_adapter_factory import AnalyticsAdapterFactory, AnalyticsProvider

logger = logging.getLogger(__name__)


class ModernAnalyticsService:
    """
    Modern analytics service using adapter pattern for clean mock/real data separation
    This service provides high-level analytics operations while the legacy AnalyticsService
    handles Telegram-specific optimizations and batch processing
    """
    
    def __init__(self, provider: Optional[AnalyticsProvider] = None, **kwargs):
        """
        Initialize modern analytics service
        
        Args:
            provider: Optional specific provider to use, otherwise uses current configured provider
            **kwargs: Additional configuration options
        """
        if provider:
            self.adapter = AnalyticsAdapterFactory.set_current_adapter(provider, **kwargs)
        else:
            self.adapter = AnalyticsAdapterFactory.get_current_adapter(**kwargs)
        
        logger.info(f"ModernAnalyticsService initialized with {self.adapter.get_adapter_name()} adapter")
    
    async def get_channel_overview(
        self, 
        channel_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive channel overview for the specified period
        
        Args:
            channel_id: Channel identifier
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dict with channel overview data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get analytics data
            analytics = await self.adapter.get_channel_analytics(channel_id, start_date, end_date)
            
            # Enhance with additional calculated metrics
            overview = {
                "channel_id": channel_id,
                "analysis_period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": days
                },
                "raw_analytics": analytics,
                "summary": self._calculate_summary_metrics(analytics),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name()
                }
            }
            
            logger.info(f"Generated channel overview for {channel_id} ({days} days)")
            return overview
            
        except Exception as e:
            logger.error(f"Error generating channel overview for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "error": True
                }
            }
    
    async def get_post_performance(
        self, 
        post_id: str,
        channel_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed post performance analysis
        
        Args:
            post_id: Post identifier
            channel_id: Channel identifier
            
        Returns:
            Dict with post performance data
        """
        try:
            analytics = await self.adapter.get_post_analytics(post_id, channel_id)
            
            # Add performance analysis
            performance = {
                "post_id": post_id,
                "channel_id": channel_id,
                "raw_analytics": analytics,
                "performance_analysis": self._analyze_post_performance(analytics),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name()
                }
            }
            
            logger.info(f"Generated post performance analysis for {post_id}")
            return performance
            
        except Exception as e:
            logger.error(f"Error generating post performance for {post_id}: {e}")
            return {
                "post_id": post_id,
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "error": True
                }
            }
    
    async def get_audience_insights(
        self, 
        channel_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive audience insights
        
        Args:
            channel_id: Channel identifier
            
        Returns:
            Dict with audience insights
        """
        try:
            demographics = await self.adapter.get_audience_demographics(channel_id)
            
            insights = {
                "channel_id": channel_id,
                "raw_demographics": demographics,
                "insights": self._generate_audience_insights(demographics),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name()
                }
            }
            
            logger.info(f"Generated audience insights for {channel_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating audience insights for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "error": True
                }
            }
    
    async def get_engagement_analysis(
        self, 
        channel_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get detailed engagement analysis
        
        Args:
            channel_id: Channel identifier
            days: Number of days to analyze
            
        Returns:
            Dict with engagement analysis
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            engagement = await self.adapter.get_engagement_metrics(channel_id, start_date, end_date)
            
            analysis = {
                "channel_id": channel_id,
                "analysis_period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": days
                },
                "raw_engagement": engagement,
                "engagement_analysis": self._analyze_engagement_trends(engagement),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name()
                }
            }
            
            logger.info(f"Generated engagement analysis for {channel_id} ({days} days)")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating engagement analysis for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "error": True
                }
            }
    
    async def get_growth_analysis(
        self, 
        channel_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Get comprehensive growth analysis
        
        Args:
            channel_id: Channel identifier
            days: Number of days to analyze
            
        Returns:
            Dict with growth analysis
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            growth = await self.adapter.get_growth_metrics(channel_id, start_date, end_date)
            
            analysis = {
                "channel_id": channel_id,
                "analysis_period": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "days": days
                },
                "raw_growth": growth,
                "growth_analysis": self._analyze_growth_patterns(growth),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name()
                }
            }
            
            logger.info(f"Generated growth analysis for {channel_id} ({days} days)")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating growth analysis for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "error": True
                }
            }
    
    async def get_comprehensive_report(
        self, 
        channel_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics report combining all data sources
        
        Args:
            channel_id: Channel identifier
            days: Number of days to analyze
            
        Returns:
            Dict with comprehensive report
        """
        try:
            # Gather all analytics data concurrently
            import asyncio
            
            tasks = [
                self.get_channel_overview(channel_id, days),
                self.get_audience_insights(channel_id),
                self.get_engagement_analysis(channel_id, days),
                self.get_growth_analysis(channel_id, min(days, 90))  # Limit growth analysis
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            overview, audience, engagement, growth = results
            
            report = {
                "channel_id": channel_id,
                "report_period": {
                    "days": days,
                    "generated_at": datetime.now().isoformat()
                },
                "sections": {
                    "overview": overview if not isinstance(overview, Exception) else {"error": str(overview)},
                    "audience": audience if not isinstance(audience, Exception) else {"error": str(audience)},
                    "engagement": engagement if not isinstance(engagement, Exception) else {"error": str(engagement)},
                    "growth": growth if not isinstance(growth, Exception) else {"error": str(growth)}
                },
                "executive_summary": self._generate_executive_summary(overview, audience, engagement, growth),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "report_type": "comprehensive"
                }
            }
            
            logger.info(f"Generated comprehensive report for {channel_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report for {channel_id}: {e}")
            return {
                "channel_id": channel_id,
                "error": True,
                "error_message": str(e),
                "service_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "service": "ModernAnalyticsService",
                    "adapter": self.adapter.get_adapter_name(),
                    "error": True
                }
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check analytics service health"""
        try:
            adapter_health = await self.adapter.health_check()
            
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "degraded",
                "service": "ModernAnalyticsService",
                "adapter_health": adapter_health,
                "adapter_name": self.adapter.get_adapter_name(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Modern analytics service health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": "ModernAnalyticsService",
                "error": str(e),
                "adapter_name": self.adapter.get_adapter_name(),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_adapter_name(self) -> str:
        """Get the name of the current adapter"""
        return self.adapter.get_adapter_name()
    
    def switch_adapter(self, provider: AnalyticsProvider, **kwargs):
        """
        Switch to a different analytics adapter
        
        Args:
            provider: The new provider to use
            **kwargs: Additional configuration options
        """
        self.adapter = AnalyticsAdapterFactory.set_current_adapter(provider, **kwargs)
        logger.info(f"Switched to {self.adapter.get_adapter_name()} adapter")
    
    # Private helper methods for data analysis
    
    def _calculate_summary_metrics(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary metrics from raw analytics data"""
        if analytics.get("error"):
            return {"error": "Cannot calculate metrics due to analytics error"}
        
        overview = analytics.get("overview", {})
        
        return {
            "total_subscribers": overview.get("total_subscribers", 0),
            "growth_rate": self._safe_percentage(overview.get("subscriber_change", 0), overview.get("total_subscribers", 1)),
            "engagement_rate": overview.get("avg_engagement_rate", 0),
            "content_velocity": overview.get("total_posts", 0),
            "reach_efficiency": self._calculate_reach_efficiency(overview)
        }
    
    def _analyze_post_performance(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze post performance metrics"""
        if analytics.get("error") or analytics.get("limitations"):
            return {"analysis": "Limited analysis due to data constraints"}
        
        metrics = analytics.get("metrics", {})
        
        return {
            "performance_score": self._calculate_performance_score(metrics),
            "engagement_quality": self._assess_engagement_quality(metrics),
            "reach_effectiveness": self._assess_reach_effectiveness(metrics),
            "viral_potential": self._assess_viral_potential(metrics)
        }
    
    def _generate_audience_insights(self, demographics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from demographic data"""
        if demographics.get("error") or demographics.get("limitations"):
            return {"insights": "Limited insights due to data constraints"}
        
        return {
            "audience_maturity": "Data-driven insights available with full demographic access",
            "geographic_diversity": "Geographic analysis requires detailed location data", 
            "engagement_patterns": "Engagement patterns available with full analytics access",
            "optimization_recommendations": [
                "Enable detailed analytics for deeper insights",
                "Monitor audience growth trends",
                "Track engagement patterns over time"
            ]
        }
    
    def _analyze_engagement_trends(self, engagement: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze engagement trends and patterns"""
        if engagement.get("error") or engagement.get("limitations"):
            return {"trend_analysis": "Limited analysis due to data constraints"}
        
        return {
            "trend_direction": "Analysis available with full engagement data",
            "peak_periods": "Peak analysis requires historical data",
            "engagement_distribution": "Distribution analysis needs detailed metrics",
            "recommendations": [
                "Track engagement over longer periods",
                "Monitor peak activity times",
                "Analyze content performance correlation"
            ]
        }
    
    def _analyze_growth_patterns(self, growth: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze growth patterns and trends"""
        if growth.get("error") or growth.get("limitations"):
            return {"growth_analysis": "Limited analysis due to data constraints"}
        
        current_data = growth.get("current_data", {})
        
        return {
            "current_status": f"Current member count: {current_data.get('current_member_count', 'Unknown')}",
            "growth_trend": "Historical tracking needed for trend analysis",
            "acquisition_analysis": "Acquisition channel data not available via current API",
            "retention_insights": "Retention analysis requires historical user data",
            "recommendations": [
                "Implement periodic member count snapshots",
                "Track growth over multiple time periods",
                "Monitor acquisition sources separately",
                "Set up retention tracking system"
            ]
        }
    
    def _generate_executive_summary(self, overview, audience, engagement, growth) -> Dict[str, Any]:
        """Generate executive summary from all analysis sections"""
        
        summary = {
            "key_metrics": {
                "data_availability": "Mixed - depends on analytics provider capabilities",
                "analysis_depth": "Basic to comprehensive based on data source"
            },
            "recommendations": [
                "Verify analytics provider capabilities",
                "Implement data tracking for missing metrics", 
                "Consider upgrading to full analytics API access",
                "Set up regular reporting cadence"
            ],
            "action_items": [
                "Review current analytics setup",
                "Identify key metrics for business goals",
                "Implement tracking for missing data points",
                "Schedule regular performance reviews"
            ]
        }
        
        # Add specific insights if data is available
        if not overview.get("error"):
            summary["overview_status"] = "Overview data available"
        if not audience.get("error"):
            summary["audience_status"] = "Audience data available"
        if not engagement.get("error"):
            summary["engagement_status"] = "Engagement data available"
        if not growth.get("error"):
            summary["growth_status"] = "Growth data available"
        
        return summary
    
    # Utility methods
    
    def _safe_percentage(self, numerator: float, denominator: float) -> float:
        """Safely calculate percentage avoiding division by zero"""
        if denominator == 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)
    
    def _calculate_reach_efficiency(self, overview: Dict[str, Any]) -> float:
        """Calculate reach efficiency metric"""
        views = overview.get("total_views", 0)
        posts = overview.get("total_posts", 1)
        return round(views / max(posts, 1), 2)
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score for a post"""
        engagement_rate = metrics.get("engagement_rate", 0)
        # Simple scoring based on engagement rate
        if engagement_rate > 10:
            return 9.0
        elif engagement_rate > 5:
            return 7.0
        elif engagement_rate > 2:
            return 5.0
        else:
            return 3.0
    
    def _assess_engagement_quality(self, metrics: Dict[str, Any]) -> str:
        """Assess the quality of engagement"""
        engagement_rate = metrics.get("engagement_rate", 0)
        if engagement_rate > 8:
            return "Excellent"
        elif engagement_rate > 5:
            return "Good"
        elif engagement_rate > 2:
            return "Average"
        else:
            return "Below Average"
    
    def _assess_reach_effectiveness(self, metrics: Dict[str, Any]) -> str:
        """Assess reach effectiveness"""
        reach = metrics.get("reach", 0)
        impressions = metrics.get("impressions", 1)
        ratio = reach / max(impressions, 1)
        
        if ratio > 0.8:
            return "Highly Effective"
        elif ratio > 0.6:
            return "Effective"
        elif ratio > 0.4:
            return "Moderately Effective"
        else:
            return "Low Effectiveness"
    
    def _assess_viral_potential(self, metrics: Dict[str, Any]) -> str:
        """Assess viral potential based on sharing metrics"""
        shares = metrics.get("total_shares", 0)
        views = metrics.get("total_views", 1)
        share_rate = shares / max(views, 1) * 100
        
        if share_rate > 5:
            return "High Viral Potential"
        elif share_rate > 2:
            return "Moderate Viral Potential"
        elif share_rate > 0.5:
            return "Low Viral Potential"
        else:
            return "Minimal Viral Potential"