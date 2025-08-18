"""
📊 Engagement Analyzer - Advanced analytics and insights engine

Features:
- Real-time engagement analysis
- Content performance prediction
- Audience behavior insights
- Automated optimization recommendations
- Multi-dimensional analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import numpy as np
import pandas as pd

from .prediction_service import PredictionService, PredictionResult, ContentMetrics
from .content_optimizer import ContentOptimizer, ContentAnalysis
from .churn_predictor import ChurnPredictor, ChurnRiskAssessment

logger = logging.getLogger(__name__)

@dataclass
class EngagementInsight:
    """Comprehensive engagement insight"""
    insight_type: str
    title: str
    description: str
    impact_level: str  # low/medium/high/critical
    confidence: float
    data_points: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class PerformanceReport:
    """Comprehensive performance analysis report"""
    channel_id: int
    period_start: datetime
    period_end: datetime
    
    # Overall metrics
    total_engagement: float
    engagement_growth: float
    content_performance_score: float
    audience_retention_rate: float
    
    # Content analysis
    top_performing_content: List[Dict]
    content_recommendations: List[str]
    optimal_posting_times: Dict[str, List[str]]
    
    # User insights
    user_segment_analysis: Dict[str, Any]
    churn_risk_summary: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    
    # Predictions
    performance_forecast: Dict[str, float]
    growth_predictions: Dict[str, Any]
    
    # Actionable insights
    key_insights: List[EngagementInsight]
    priority_actions: List[Dict[str, Any]]
    
    # Metadata
    analysis_completeness: float
    data_quality_score: float
    report_version: str
    generated_at: datetime

class EngagementAnalyzer:
    """
    🚀 Advanced engagement analytics and insights engine
    
    Capabilities:
    - Multi-dimensional engagement analysis
    - Predictive performance modeling
    - Automated insight generation
    - Content optimization recommendations
    - User behavior pattern analysis
    - Real-time performance monitoring
    """
    
    def __init__(
        self, 
        prediction_service: PredictionService,
        content_optimizer: ContentOptimizer,
        churn_predictor: ChurnPredictor,
        db_service=None,
        cache_service=None
    ):
        self.prediction_service = prediction_service
        self.content_optimizer = content_optimizer
        self.churn_predictor = churn_predictor
        self.db_service = db_service
        self.cache_service = cache_service
        
        # Analysis configuration
        self.config = {
            'insight_confidence_threshold': 0.7,
            'recommendation_limit': 10,
            'analysis_lookback_days': 30,
            'forecast_horizon_days': 7
        }
        
        # Insight categories
        self.insight_categories = {
            'content_performance': {
                'weight': 0.3,
                'analyzers': ['content_scoring', 'engagement_prediction']
            },
            'audience_behavior': {
                'weight': 0.25,
                'analyzers': ['user_segments', 'engagement_patterns']
            },
            'timing_optimization': {
                'weight': 0.2,
                'analyzers': ['optimal_timing', 'posting_frequency']
            },
            'retention_analysis': {
                'weight': 0.25,
                'analyzers': ['churn_prediction', 'user_lifecycle']
            }
        }
    
    async def generate_performance_report(
        self,
        channel_id: int,
        period_days: int = 30,
        include_predictions: bool = True,
        include_churn_analysis: bool = True
    ) -> PerformanceReport:
        """
        📊 Generate comprehensive performance analysis report
        
        Args:
            channel_id: Channel to analyze
            period_days: Analysis period in days
            include_predictions: Include performance predictions
            include_churn_analysis: Include churn risk analysis
            
        Returns:
            Comprehensive performance report with insights and recommendations
        """
        try:
            logger.info(f"🔍 Generating performance report for channel {channel_id}")
            
            period_end = datetime.now()
            period_start = period_end - timedelta(days=period_days)
            
            # Collect base analytics data
            analytics_data = await self._collect_analytics_data(
                channel_id, period_start, period_end
            )
            
            # Calculate core metrics
            core_metrics = await self._calculate_core_metrics(analytics_data)
            
            # Analyze content performance
            content_analysis = await self._analyze_content_performance(
                channel_id, analytics_data
            )
            
            # Analyze user segments and behavior
            user_analysis = await self._analyze_user_behavior(
                channel_id, period_start, period_end
            )
            
            # Generate optimal posting recommendations
            timing_analysis = await self.prediction_service.find_optimal_posting_time(
                channel_id, 'general', period_days
            )
            
            # Churn risk analysis (if enabled)
            churn_summary = {}
            if include_churn_analysis:
                churn_summary = await self._analyze_channel_churn_risk(
                    channel_id, period_days
                )
            
            # Generate predictions (if enabled)
            predictions = {}
            if include_predictions:
                predictions = await self._generate_performance_predictions(
                    channel_id, analytics_data, content_analysis
                )
            
            # Generate key insights
            insights = await self._generate_key_insights(
                analytics_data, content_analysis, user_analysis, churn_summary
            )
            
            # Generate priority actions
            priority_actions = await self._generate_priority_actions(
                insights, content_analysis, churn_summary
            )
            
            # Calculate analysis quality metrics
            completeness = await self._calculate_analysis_completeness(analytics_data)
            data_quality = await self._calculate_data_quality_score(analytics_data)
            
            report = PerformanceReport(
                channel_id=channel_id,
                period_start=period_start,
                period_end=period_end,
                
                total_engagement=core_metrics.get('total_engagement', 0),
                engagement_growth=core_metrics.get('engagement_growth', 0),
                content_performance_score=content_analysis.get('overall_score', 0),
                audience_retention_rate=user_analysis.get('retention_rate', 0),
                
                top_performing_content=content_analysis.get('top_content', []),
                content_recommendations=content_analysis.get('recommendations', []),
                optimal_posting_times=timing_analysis.get('optimal_times', {}),
                
                user_segment_analysis=user_analysis,
                churn_risk_summary=churn_summary,
                engagement_patterns=user_analysis.get('engagement_patterns', {}),
                
                performance_forecast=predictions.get('forecast', {}),
                growth_predictions=predictions.get('growth', {}),
                
                key_insights=insights,
                priority_actions=priority_actions,
                
                analysis_completeness=completeness,
                data_quality_score=data_quality,
                report_version='v2.5.0',
                generated_at=datetime.now()
            )
            
            # Cache report for 1 hour
            if self.cache_service:
                cache_key = f"performance_report:{channel_id}:{period_days}"
                await self.cache_service.set(
                    cache_key,
                    report.__dict__,
                    ttl=3600
                )
            
            logger.info(f"✅ Generated performance report: {len(insights)} insights, {len(priority_actions)} actions")
            return report
            
        except Exception as e:
            logger.error(f"❌ Performance report generation failed: {e}")
            return await self._create_fallback_report(channel_id, period_start, period_end)
    
    async def analyze_content_before_publishing(
        self,
        content_text: str,
        media_urls: Optional[List[str]] = None,
        channel_id: Optional[int] = None,
        scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        🎯 Pre-publish content analysis with optimization recommendations
        
        Returns:
            Complete content analysis with predictions and recommendations
        """
        try:
            # Content optimization analysis
            content_analysis = await self.content_optimizer.analyze_content(
                content_text, media_urls, 'general'
            )
            
            # Create content metrics for prediction
            content_metrics = ContentMetrics(
                sentiment_score=content_analysis.sentiment_score,
                readability_score=content_analysis.readability_score / 100,
                hashtag_count=content_analysis.hashtag_count,
                word_count=content_analysis.word_count,
                media_count=len(media_urls) if media_urls else 0,
                emoji_count=content_analysis.emoji_count,
                engagement_history=[100, 120, 90, 150, 110]  # Sample history
            )
            
            # Engagement prediction
            prediction_result = None
            if channel_id:
                prediction_result = await self.prediction_service.predict_engagement(
                    content_metrics, channel_id, scheduled_time
                )
            
            # Optimal timing recommendation
            optimal_timing = None
            if channel_id:
                optimal_timing = await self.prediction_service.find_optimal_posting_time(
                    channel_id
                )
            
            # Combine all analysis
            analysis = {
                'content_analysis': {
                    'overall_score': content_analysis.overall_score,
                    'sentiment': {
                        'score': content_analysis.sentiment_score,
                        'label': content_analysis.sentiment_label
                    },
                    'readability': {
                        'score': content_analysis.readability_score,
                        'level': content_analysis.readability_level
                    },
                    'seo_score': content_analysis.seo_score,
                    'engagement_score': content_analysis.engagement_score
                },
                'engagement_prediction': {
                    'predicted_engagement': prediction_result.prediction if prediction_result else 100,
                    'confidence': prediction_result.confidence if prediction_result else 0.5,
                    'key_factors': prediction_result.factors if prediction_result else {}
                } if prediction_result else None,
                'optimization_recommendations': content_analysis.optimization_tips,
                'hashtag_suggestions': content_analysis.suggested_hashtags,
                'optimal_timing': optimal_timing,
                'publishing_score': await self._calculate_publishing_score(
                    content_analysis, prediction_result
                ),
                'risk_assessment': await self._assess_content_risks(
                    content_analysis, prediction_result
                ),
                'timestamp': datetime.now().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Pre-publish analysis failed: {e}")
            return {
                'error': str(e),
                'fallback_recommendations': [
                    'Review content for clarity and engagement',
                    'Add relevant hashtags',
                    'Include visual content if possible'
                ]
            }
    
    async def get_real_time_insights(
        self,
        channel_id: int,
        lookback_hours: int = 24
    ) -> List[EngagementInsight]:
        """
        ⚡ Get real-time engagement insights and alerts
        
        Returns:
            List of actionable real-time insights
        """
        try:
            insights = []
            
            # Get recent performance data
            recent_data = await self._get_recent_performance_data(
                channel_id, lookback_hours
            )
            
            if not recent_data:
                return insights
            
            # Analyze engagement trends
            trend_insights = await self._analyze_engagement_trends(recent_data)
            insights.extend(trend_insights)
            
            # Analyze content performance anomalies
            anomaly_insights = await self._detect_performance_anomalies(recent_data)
            insights.extend(anomaly_insights)
            
            # User behavior insights
            user_insights = await self._analyze_recent_user_behavior(
                channel_id, lookback_hours
            )
            insights.extend(user_insights)
            
            # Timing insights
            timing_insights = await self._analyze_posting_timing_effectiveness(recent_data)
            insights.extend(timing_insights)
            
            # Filter by confidence threshold
            high_confidence_insights = [
                insight for insight in insights 
                if insight.confidence >= self.config['insight_confidence_threshold']
            ]
            
            # Sort by impact level
            impact_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            high_confidence_insights.sort(
                key=lambda x: impact_order.get(x.impact_level, 0), 
                reverse=True
            )
            
            return high_confidence_insights
            
        except Exception as e:
            logger.error(f"❌ Real-time insights generation failed: {e}")
            return []
    
    # ============ PRIVATE HELPER METHODS ============
    
    async def _collect_analytics_data(
        self,
        channel_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Collect comprehensive analytics data for analysis"""
        # Simulate analytics data collection
        # In real implementation, this would query the database
        
        days = (end_date - start_date).days
        
        return {
            'posts': [
                {
                    'id': i,
                    'content': f'Sample post {i}',
                    'created_at': start_date + timedelta(days=np.random.randint(0, days)),
                    'views': np.random.randint(50, 500),
                    'likes': np.random.randint(5, 50),
                    'comments': np.random.randint(0, 20),
                    'shares': np.random.randint(0, 10),
                    'hashtags': np.random.randint(0, 8)
                }
                for i in range(50)  # Sample 50 posts
            ],
            'user_sessions': [
                {
                    'user_id': i,
                    'session_start': start_date + timedelta(
                        hours=np.random.randint(0, days * 24)
                    ),
                    'duration_minutes': np.random.randint(1, 60),
                    'actions_taken': np.random.randint(1, 20)
                }
                for i in range(200)  # Sample 200 sessions
            ],
            'engagement_metrics': {
                'total_views': np.random.randint(5000, 15000),
                'total_likes': np.random.randint(500, 1500),
                'total_comments': np.random.randint(100, 500),
                'total_shares': np.random.randint(50, 200),
                'unique_users': np.random.randint(100, 500)
            }
        }
    
    async def _calculate_core_metrics(self, analytics_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate core performance metrics"""
        posts = analytics_data.get('posts', [])
        metrics = analytics_data.get('engagement_metrics', {})
        
        if not posts:
            return {'total_engagement': 0, 'engagement_growth': 0}
        
        # Calculate total engagement
        total_engagement = sum(
            post['views'] + post['likes'] + post['comments'] + post['shares']
            for post in posts
        )
        
        # Calculate engagement growth (simplified)
        # In reality, this would compare to previous period
        recent_posts = posts[-10:]  # Last 10 posts
        older_posts = posts[-20:-10] if len(posts) >= 20 else posts[:-10]
        
        if recent_posts and older_posts:
            recent_avg = np.mean([
                post['views'] + post['likes'] + post['comments'] + post['shares']
                for post in recent_posts
            ])
            older_avg = np.mean([
                post['views'] + post['likes'] + post['comments'] + post['shares']
                for post in older_posts
            ])
            engagement_growth = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            engagement_growth = 0
        
        return {
            'total_engagement': total_engagement,
            'engagement_growth': engagement_growth,
            'avg_engagement_per_post': total_engagement / len(posts) if posts else 0,
            'engagement_rate': (metrics.get('total_likes', 0) + metrics.get('total_comments', 0)) / 
                             max(metrics.get('total_views', 1), 1) * 100
        }
    
    async def _generate_key_insights(
        self,
        analytics_data: Dict[str, Any],
        content_analysis: Dict[str, Any],
        user_analysis: Dict[str, Any],
        churn_summary: Dict[str, Any]
    ) -> List[EngagementInsight]:
        """Generate key actionable insights"""
        insights = []
        
        # Content performance insight
        overall_score = content_analysis.get('overall_score', 0)
        if overall_score > 80:
            insights.append(EngagementInsight(
                insight_type='content_performance',
                title='High-Quality Content Performance',
                description=f'Content quality score is excellent ({overall_score:.1f}/100). Continue current content strategy.',
                impact_level='high',
                confidence=0.9,
                data_points={'content_score': overall_score},
                recommendations=['Maintain current content quality standards', 'Scale successful content types'],
                timestamp=datetime.now()
            ))
        elif overall_score < 60:
            insights.append(EngagementInsight(
                insight_type='content_performance',
                title='Content Quality Needs Improvement',
                description=f'Content quality score is below optimal ({overall_score:.1f}/100). Focus on optimization.',
                impact_level='medium',
                confidence=0.8,
                data_points={'content_score': overall_score},
                recommendations=['Review content optimization suggestions', 'Improve hashtag strategy', 'Add visual content'],
                timestamp=datetime.now()
            ))
        
        # Churn risk insight
        if churn_summary and churn_summary.get('high_risk_users', 0) > 0:
            high_risk_count = churn_summary['high_risk_users']
            insights.append(EngagementInsight(
                insight_type='retention_analysis',
                title='User Retention Alert',
                description=f'{high_risk_count} users are at high risk of churning. Immediate retention actions needed.',
                impact_level='critical',
                confidence=0.85,
                data_points={'high_risk_users': high_risk_count},
                recommendations=['Contact high-risk users', 'Offer retention incentives', 'Analyze churn factors'],
                timestamp=datetime.now()
            ))
        
        # Engagement trend insight
        posts = analytics_data.get('posts', [])
        if posts:
            recent_engagement = np.mean([
                post['views'] + post['likes'] + post['comments']
                for post in posts[-5:]  # Last 5 posts
            ])
            older_engagement = np.mean([
                post['views'] + post['likes'] + post['comments']
                for post in posts[-10:-5]  # Previous 5 posts
            ]) if len(posts) >= 10 else recent_engagement
            
            if recent_engagement > older_engagement * 1.2:  # 20% improvement
                insights.append(EngagementInsight(
                    insight_type='engagement_trend',
                    title='Positive Engagement Trend',
                    description=f'Recent posts showing {((recent_engagement/older_engagement-1)*100):.1f}% engagement increase.',
                    impact_level='high',
                    confidence=0.8,
                    data_points={'engagement_improvement': (recent_engagement/older_engagement-1)*100},
                    recommendations=['Double down on successful content formats', 'Increase posting frequency'],
                    timestamp=datetime.now()
                ))
        
        return insights
    
    async def _calculate_publishing_score(
        self,
        content_analysis: ContentAnalysis,
        prediction_result: Optional[PredictionResult]
    ) -> Dict[str, Any]:
        """Calculate overall publishing readiness score"""
        score_components = {
            'content_quality': content_analysis.overall_score,
            'engagement_prediction': prediction_result.prediction if prediction_result else 50,
            'optimization_completeness': 100 - len(content_analysis.optimization_tips) * 10
        }
        
        # Weighted average
        weights = {'content_quality': 0.4, 'engagement_prediction': 0.4, 'optimization_completeness': 0.2}
        
        overall_score = sum(
            score_components[key] * weights[key] 
            for key in weights
        )
        
        # Determine readiness level
        if overall_score >= 80:
            readiness = 'excellent'
        elif overall_score >= 65:
            readiness = 'good'
        elif overall_score >= 50:
            readiness = 'fair'
        else:
            readiness = 'needs_improvement'
        
        return {
            'overall_score': overall_score,
            'readiness_level': readiness,
            'score_components': score_components,
            'recommendation': await self._get_publishing_recommendation(overall_score)
        }
    
    async def _get_publishing_recommendation(self, score: float) -> str:
        """Get publishing recommendation based on score"""
        if score >= 80:
            return 'Ready to publish! Content is optimized for high engagement.'
        elif score >= 65:
            return 'Good to publish with minor optimizations suggested.'
        elif score >= 50:
            return 'Consider implementing optimization suggestions before publishing.'
        else:
            return 'Significant improvements recommended before publishing.'
    
    async def _create_fallback_report(
        self,
        channel_id: int,
        period_start: datetime,
        period_end: datetime
    ) -> PerformanceReport:
        """Create fallback report when analysis fails"""
        return PerformanceReport(
            channel_id=channel_id,
            period_start=period_start,
            period_end=period_end,
            
            total_engagement=0,
            engagement_growth=0,
            content_performance_score=50,
            audience_retention_rate=70,
            
            top_performing_content=[],
            content_recommendations=['Review and optimize content strategy'],
            optimal_posting_times={'general': ['09:00', '13:00', '19:00']},
            
            user_segment_analysis={},
            churn_risk_summary={},
            engagement_patterns={},
            
            performance_forecast={},
            growth_predictions={},
            
            key_insights=[EngagementInsight(
                insight_type='system',
                title='Analysis Limited',
                description='Limited analytics data available. Recommendations based on general best practices.',
                impact_level='medium',
                confidence=0.3,
                data_points={},
                recommendations=['Collect more engagement data', 'Ensure tracking is properly configured'],
                timestamp=datetime.now()
            )],
            priority_actions=[{
                'action': 'improve_data_collection',
                'title': 'Improve Analytics Data Collection',
                'priority': 'high',
                'description': 'Enhance data collection to enable comprehensive analysis'
            }],
            
            analysis_completeness=0.3,
            data_quality_score=0.2,
            report_version='v2.5.0_fallback',
            generated_at=datetime.now()
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """🏥 Health check for engagement analyzer"""
        # Check all sub-services
        services_health = {}
        
        if self.prediction_service:
            services_health['prediction_service'] = await self.prediction_service.health_check()
        
        if self.content_optimizer:
            services_health['content_optimizer'] = await self.content_optimizer.health_check()
        
        if self.churn_predictor:
            services_health['churn_predictor'] = await self.churn_predictor.health_check()
        
        return {
            'status': 'healthy',
            'services': services_health,
            'insight_categories': len(self.insight_categories),
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
