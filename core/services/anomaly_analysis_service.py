"""
Anomaly Analysis Service - AI-Powered Anomaly Detection and Explanation

Extracted from AIInsightsService to maintain Single Responsibility Principle.
Handles anomaly detection, root cause analysis, and explanations.

Part of Phase 3 AI-First Architecture.
"""

from __future__ import annotations

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List

from .nlg_service import NarrativeStyle

logger = logging.getLogger(__name__)


class AnomalyAnalysisService:
    """
    🚨 Anomaly Analysis Service
    
    Specialized service for anomaly detection and explanation:
    - Performance anomaly detection
    - Root cause analysis
    - Natural language explanations
    - Severity assessment
    - Recommendation generation
    """

    def __init__(self, nlg_service, channel_daily_repo, post_repo):
        """Initialize with required dependencies"""
        self._nlg_service = nlg_service
        self._daily = channel_daily_repo
        self._posts = post_repo

    async def analyze_and_explain_anomaly(
        self,
        channel_id: int,
        anomaly_data: dict,
        narrative_style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL
    ) -> dict:
        """
        🚨 Comprehensive Anomaly Analysis with Natural Language Explanation
        
        When unusual patterns are detected, this method provides AI-powered
        analysis and explanations in human-readable language.
        
        Args:
            channel_id: Target channel ID
            anomaly_data: Detected anomaly information
            narrative_style: How to present the explanation
            
        Returns:
            Comprehensive anomaly analysis with explanations and recommendations
        """
        try:
            # Get historical context for comparison
            now = datetime.now()
            start_date = now - timedelta(days=30)
            
            # Gather historical data for context
            historical_context = await self._gather_historical_context(
                channel_id, start_date, now
            )
            
            # Perform root cause analysis
            root_causes = await self._analyze_anomaly_root_causes(
                channel_id, anomaly_data, historical_context
            )
            
            # Generate natural language explanation
            explanation = await self._nlg_service.explain_anomaly(
                anomaly_data, historical_context, narrative_style
            )
            
            # Assess severity and impact
            severity_assessment = await self._assess_anomaly_severity(
                anomaly_data, historical_context
            )
            
            # Generate actionable recommendations
            recommendations = await self._generate_anomaly_recommendations(
                anomaly_data, root_causes, severity_assessment
            )
            
            return {
                "anomaly_detected": True,
                "anomaly_data": anomaly_data,
                "explanation": explanation,
                "root_cause_analysis": root_causes,
                "severity_assessment": severity_assessment,
                "recommendations": recommendations,
                "narrative_style": narrative_style.value,
                "historical_context_available": bool(historical_context),
                "analyzed_at": datetime.now().isoformat(),
                "confidence": self._calculate_analysis_confidence(
                    anomaly_data, historical_context, root_causes
                )
            }
            
        except Exception as e:
            logger.error(f"Anomaly analysis failed: {e}")
            return {
                "anomaly_detected": True,
                "explanation": "An unusual pattern was detected that requires investigation.",
                "error": str(e),
                "recommendations": ["Manual review recommended", "Check recent changes"],
                "severity": "unknown"
            }

    async def detect_performance_anomalies(
        self,
        channel_id: int,
        metrics: List[str] = None,
        sensitivity: float = 2.0,
        days: int = 30
    ) -> List[dict]:
        """
        🔍 Detect Performance Anomalies in Channel Metrics
        
        Analyzes channel performance data to automatically detect unusual patterns
        that deviate significantly from historical norms.
        
        Args:
            channel_id: Target channel ID
            metrics: List of metrics to analyze (views, engagement, growth)
            sensitivity: Standard deviations threshold (lower = more sensitive)
            days: Historical period to analyze
            
        Returns:
            List of detected anomalies with details
        """
        try:
            if metrics is None:
                metrics = ["views", "engagement", "growth"]
            
            detected_anomalies = []
            now = datetime.now()
            start_date = now - timedelta(days=days)
            
            # Analyze each metric for anomalies
            for metric in metrics:
                anomalies = await self._detect_metric_anomalies(
                    channel_id, metric, start_date, now, sensitivity
                )
                detected_anomalies.extend(anomalies)
            
            # Sort by severity and recency
            detected_anomalies.sort(
                key=lambda x: (
                    self._severity_score(x.get("severity", "low")),
                    x.get("detected_at", "")
                ),
                reverse=True
            )
            
            logger.info(f"Detected {len(detected_anomalies)} anomalies for channel {channel_id}")
            return detected_anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []

    async def _gather_historical_context(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> dict:
        """Gather comprehensive historical context for anomaly analysis"""
        try:
            context = {}
            
            # Get historical posts data
            posts = await self._posts.top_by_views(channel_id, start_date, end_date, 100)
            context["posts"] = posts
            
            # Get time series data
            daily_views = await self._daily.series_data(channel_id, "views", start_date, end_date)
            daily_followers = await self._daily.series_data(channel_id, "followers", start_date, end_date)
            
            context["daily_metrics"] = {
                "views": daily_views or [],
                "followers": daily_followers or []
            }
            
            # Calculate baseline metrics
            if posts:
                view_counts = [p.get("views", 0) for p in posts]
                context["baselines"] = {
                    "avg_views": np.mean(view_counts),
                    "std_views": np.std(view_counts),
                    "median_views": np.median(view_counts),
                    "percentile_90": np.percentile(view_counts, 90),
                    "percentile_10": np.percentile(view_counts, 10)
                }
                
                # Calculate engagement baselines
                engagement_scores = []
                for post in posts:
                    views = post.get("views", 0)
                    forwards = post.get("forwards", 0)
                    replies = post.get("replies", 0)
                    
                    if views > 0:
                        engagement = (forwards + replies) / views * 100
                        engagement_scores.append(engagement)
                
                if engagement_scores:
                    context["baselines"]["avg_engagement"] = np.mean(engagement_scores)
                    context["baselines"]["std_engagement"] = np.std(engagement_scores)
            
            return context
            
        except Exception as e:
            logger.error(f"Historical context gathering failed: {e}")
            return {}

    async def _analyze_anomaly_root_causes(
        self, channel_id: int, anomaly_data: dict, historical_context: dict
    ) -> List[dict]:
        """Analyze potential root causes of detected anomalies"""
        try:
            root_causes = []
            anomaly_metric = anomaly_data.get("metric", "unknown")
            anomaly_type = anomaly_data.get("type", "unknown")
            
            # Content strategy changes
            if anomaly_metric in ["engagement", "views"]:
                content_causes = await self._analyze_content_related_causes(
                    anomaly_data, historical_context
                )
                root_causes.extend(content_causes)
            
            # Timing and frequency changes
            if anomaly_type == "temporal" or anomaly_metric == "frequency":
                timing_causes = await self._analyze_timing_related_causes(
                    anomaly_data, historical_context
                )
                root_causes.extend(timing_causes)
            
            # Growth-related causes
            if anomaly_metric in ["growth", "followers", "subscribers"]:
                growth_causes = await self._analyze_growth_related_causes(
                    anomaly_data, historical_context
                )
                root_causes.extend(growth_causes)
            
            # External factor analysis
            external_causes = await self._analyze_external_factors(
                anomaly_data, historical_context
            )
            root_causes.extend(external_causes)
            
            # Sort by confidence and relevance
            root_causes.sort(key=lambda x: x.get("confidence", 0), reverse=True)
            
            return root_causes[:5]  # Top 5 most likely causes
            
        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            return [{
                "category": "unknown",
                "description": "Unable to determine root cause",
                "confidence": 0.1
            }]

    async def _analyze_content_related_causes(
        self, anomaly_data: dict, historical_context: dict
    ) -> List[dict]:
        """Analyze content-related potential causes"""
        causes = []
        posts = historical_context.get("posts", [])
        
        if posts and len(posts) >= 10:
            recent_posts = posts[:5]  # Most recent 5 posts
            historical_posts = posts[5:15]  # Previous 10 posts
            
            # Analyze content length changes
            recent_lengths = [len(p.get("title", "")) for p in recent_posts]
            hist_lengths = [len(p.get("title", "")) for p in historical_posts]
            
            if recent_lengths and hist_lengths:
                recent_avg = np.mean(recent_lengths)
                hist_avg = np.mean(hist_lengths)
                
                if abs(recent_avg - hist_avg) > hist_avg * 0.3:  # 30% change
                    causes.append({
                        "category": "content_length",
                        "description": f"Significant change in content length: {recent_avg:.0f} vs {hist_avg:.0f} characters",
                        "confidence": 0.7,
                        "change_percentage": ((recent_avg - hist_avg) / hist_avg * 100)
                    })
            
            # Analyze posting frequency changes
            if len(posts) >= 20:
                recent_dates = []
                hist_dates = []
                
                for post in recent_posts:
                    if post.get("date"):
                        try:
                            date = datetime.fromisoformat(post["date"].replace("Z", "+00:00"))
                            recent_dates.append(date)
                        except:
                            continue
                
                for post in historical_posts:
                    if post.get("date"):
                        try:
                            date = datetime.fromisoformat(post["date"].replace("Z", "+00:00"))
                            hist_dates.append(date)
                        except:
                            continue
                
                if len(recent_dates) >= 3 and len(hist_dates) >= 3:
                    # Calculate posting frequency
                    recent_span = (max(recent_dates) - min(recent_dates)).days
                    hist_span = (max(hist_dates) - min(hist_dates)).days
                    
                    if recent_span > 0 and hist_span > 0:
                        recent_freq = len(recent_dates) / recent_span
                        hist_freq = len(hist_dates) / hist_span
                        
                        if abs(recent_freq - hist_freq) > hist_freq * 0.4:  # 40% change
                            causes.append({
                                "category": "posting_frequency",
                                "description": f"Posting frequency changed from {hist_freq:.1f} to {recent_freq:.1f} posts per day",
                                "confidence": 0.8,
                                "frequency_change": ((recent_freq - hist_freq) / hist_freq * 100)
                            })
        
        return causes

    async def _analyze_timing_related_causes(
        self, anomaly_data: dict, historical_context: dict
    ) -> List[dict]:
        """Analyze timing and schedule related causes"""
        causes = []
        
        # Placeholder for timing analysis
        # In a real implementation, this would analyze posting time changes
        causes.append({
            "category": "posting_schedule",
            "description": "Potential changes in posting timing or schedule",
            "confidence": 0.6,
            "details": "Schedule analysis requires more detailed timestamp data"
        })
        
        return causes

    async def _analyze_growth_related_causes(
        self, anomaly_data: dict, historical_context: dict
    ) -> List[dict]:
        """Analyze growth and audience related causes"""
        causes = []
        daily_metrics = historical_context.get("daily_metrics", {})
        followers_data = daily_metrics.get("followers", [])
        
        if followers_data and len(followers_data) >= 7:
            # Analyze follower growth patterns
            recent_followers = [f.get("value", 0) for f in followers_data[-7:]]
            
            if len(recent_followers) >= 2:
                growth_rates = []
                for i in range(1, len(recent_followers)):
                    if recent_followers[i-1] > 0:
                        rate = (recent_followers[i] - recent_followers[i-1]) / recent_followers[i-1]
                        growth_rates.append(rate)
                
                if growth_rates:
                    avg_growth = np.mean(growth_rates)
                    if abs(avg_growth) > 0.05:  # 5% change threshold
                        causes.append({
                            "category": "audience_growth",
                            "description": f"Audience growth rate: {avg_growth*100:.1f}% daily average",
                            "confidence": 0.7,
                            "growth_trend": "positive" if avg_growth > 0 else "negative"
                        })
        
        return causes

    async def _analyze_external_factors(
        self, anomaly_data: dict, historical_context: dict
    ) -> List[dict]:
        """Analyze potential external factors"""
        causes = []
        
        # General external factors (in a real implementation, this could integrate with external APIs)
        causes.append({
            "category": "external_factors",
            "description": "Market conditions, platform changes, or competitive factors",
            "confidence": 0.4,
            "details": "External factor analysis requires additional data sources"
        })
        
        # Seasonal factors
        now = datetime.now()
        if now.month == 12 or now.month == 1:  # Holiday season
            causes.append({
                "category": "seasonal",
                "description": "Holiday season impact on engagement patterns",
                "confidence": 0.6,
                "season": "holiday"
            })
        
        return causes

    async def _detect_metric_anomalies(
        self,
        channel_id: int,
        metric: str,
        start_date: datetime,
        end_date: datetime,
        sensitivity: float
    ) -> List[dict]:
        """Detect anomalies in a specific metric"""
        anomalies = []
        
        try:
            if metric == "views":
                # Analyze view anomalies
                posts = await self._posts.top_by_views(channel_id, start_date, end_date, 50)
                if posts:
                    view_counts = [p.get("views", 0) for p in posts]
                    anomalies.extend(
                        self._statistical_anomaly_detection(view_counts, "views", sensitivity)
                    )
            
            elif metric == "engagement":
                # Analyze engagement anomalies
                posts = await self._posts.top_by_views(channel_id, start_date, end_date, 50)
                if posts:
                    engagement_scores = []
                    for post in posts:
                        views = post.get("views", 0)
                        forwards = post.get("forwards", 0)
                        replies = post.get("replies", 0)
                        
                        if views > 0:
                            engagement = (forwards + replies) / views * 100
                            engagement_scores.append(engagement)
                    
                    if engagement_scores:
                        anomalies.extend(
                            self._statistical_anomaly_detection(engagement_scores, "engagement", sensitivity)
                        )
            
            elif metric == "growth":
                # Analyze growth anomalies
                daily_data = await self._daily.series_data(channel_id, "followers", start_date, end_date)
                if daily_data:
                    growth_rates = []
                    values = [d.get("value", 0) for d in daily_data]
                    
                    for i in range(1, len(values)):
                        if values[i-1] > 0:
                            rate = (values[i] - values[i-1]) / values[i-1]
                            growth_rates.append(rate)
                    
                    if growth_rates:
                        anomalies.extend(
                            self._statistical_anomaly_detection(growth_rates, "growth", sensitivity)
                        )
            
        except Exception as e:
            logger.error(f"Metric anomaly detection failed for {metric}: {e}")
        
        return anomalies

    def _statistical_anomaly_detection(
        self, data: List[float], metric_name: str, sensitivity: float
    ) -> List[dict]:
        """Perform statistical anomaly detection using z-score method"""
        anomalies = []
        
        if len(data) < 5:  # Need minimum data points
            return anomalies
        
        try:
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if std_val == 0:  # No variation
                return anomalies
            
            for i, value in enumerate(data):
                z_score = abs((value - mean_val) / std_val)
                
                if z_score > sensitivity:
                    severity = "high" if z_score > sensitivity * 1.5 else "medium"
                    
                    anomalies.append({
                        "metric": metric_name,
                        "value": value,
                        "expected_value": mean_val,
                        "z_score": z_score,
                        "deviation_percentage": ((value - mean_val) / mean_val * 100),
                        "severity": severity,
                        "position": i,
                        "type": "statistical",
                        "detected_at": datetime.now().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Statistical anomaly detection failed: {e}")
        
        return anomalies

    async def _assess_anomaly_severity(
        self, anomaly_data: dict, historical_context: dict
    ) -> dict:
        """Assess the severity and potential impact of an anomaly"""
        try:
            severity_factors = {
                "magnitude": 0,
                "duration": 0,
                "trend": 0,
                "impact_scope": 0
            }
            
            # Magnitude assessment
            deviation = abs(anomaly_data.get("deviation_percentage", 0))
            if deviation > 50:
                severity_factors["magnitude"] = 3  # High
            elif deviation > 25:
                severity_factors["magnitude"] = 2  # Medium
            elif deviation > 10:
                severity_factors["magnitude"] = 1  # Low
            
            # Duration assessment (placeholder - would need time series data)
            severity_factors["duration"] = 1  # Default to low
            
            # Overall severity calculation
            total_score = sum(severity_factors.values())
            max_score = len(severity_factors) * 3
            
            severity_percentage = (total_score / max_score) * 100
            
            if severity_percentage > 66:
                overall_severity = "critical"
            elif severity_percentage > 33:
                overall_severity = "high"
            elif severity_percentage > 15:
                overall_severity = "medium"
            else:
                overall_severity = "low"
            
            return {
                "overall_severity": overall_severity,
                "severity_score": severity_percentage,
                "factors": severity_factors,
                "impact_assessment": self._assess_business_impact(anomaly_data, overall_severity),
                "urgency": "immediate" if overall_severity in ["critical", "high"] else "moderate"
            }
            
        except Exception as e:
            logger.error(f"Severity assessment failed: {e}")
            return {
                "overall_severity": "unknown",
                "error": str(e)
            }

    def _assess_business_impact(self, anomaly_data: dict, severity: str) -> str:
        """Assess potential business impact of the anomaly"""
        metric = anomaly_data.get("metric", "unknown")
        
        impact_map = {
            "critical": {
                "views": "Significant audience reach reduction - immediate attention required",
                "engagement": "Severe engagement drop - content strategy review needed",
                "growth": "Critical growth issue - retention strategies required"
            },
            "high": {
                "views": "Notable performance decline - strategy adjustment recommended",
                "engagement": "Engagement concerns - content optimization needed",
                "growth": "Growth slowdown - audience acquisition review suggested"
            },
            "medium": {
                "views": "Moderate performance variation - monitoring recommended",
                "engagement": "Engagement fluctuation - minor adjustments may help",
                "growth": "Growth variation - continue current strategies with monitoring"
            },
            "low": {
                "views": "Minor performance variation - normal fluctuation range",
                "engagement": "Slight engagement change - minimal concern",
                "growth": "Small growth variation - within normal parameters"
            }
        }
        
        return impact_map.get(severity, {}).get(metric, "Impact assessment unavailable")

    async def _generate_anomaly_recommendations(
        self, anomaly_data: dict, root_causes: List[dict], severity_assessment: dict
    ) -> List[dict]:
        """Generate specific recommendations based on anomaly analysis"""
        recommendations = []
        
        try:
            severity = severity_assessment.get("overall_severity", "medium")
            urgency = severity_assessment.get("urgency", "moderate")
            
            # Severity-based immediate actions
            if severity in ["critical", "high"]:
                recommendations.append({
                    "priority": "immediate",
                    "category": "emergency_response",
                    "action": "Conduct immediate strategy review and implement corrective measures",
                    "timeline": "Within 24 hours",
                    "expected_outcome": "Stabilize performance metrics"
                })
            
            # Root cause specific recommendations
            for cause in root_causes[:3]:  # Top 3 causes
                category = cause.get("category", "unknown")
                
                if category == "content_length":
                    recommendations.append({
                        "priority": "high",
                        "category": "content_optimization",
                        "action": f"Adjust content length based on analysis: {cause.get('description', '')}",
                        "timeline": "Next 3-5 posts",
                        "expected_outcome": "Improved content performance"
                    })
                
                elif category == "posting_frequency":
                    recommendations.append({
                        "priority": "medium",
                        "category": "schedule_optimization",
                        "action": "Optimize posting frequency based on historical performance",
                        "timeline": "Next 2 weeks",
                        "expected_outcome": "Better audience engagement"
                    })
                
                elif category == "posting_schedule":
                    recommendations.append({
                        "priority": "medium",
                        "category": "timing_optimization",
                        "action": "Review and optimize posting schedule for audience activity",
                        "timeline": "Next week",
                        "expected_outcome": "Increased reach and engagement"
                    })
                
                elif category == "external_factors":
                    recommendations.append({
                        "priority": "low",
                        "category": "market_analysis",
                        "action": "Monitor competitor activity and market trends",
                        "timeline": "Ongoing",
                        "expected_outcome": "Better strategic positioning"
                    })
            
            # General monitoring recommendation
            recommendations.append({
                "priority": "ongoing",
                "category": "monitoring",
                "action": "Implement enhanced monitoring for early anomaly detection",
                "timeline": "Immediate setup, ongoing monitoring",
                "expected_outcome": "Faster response to future anomalies"
            })
            
            # Sort by priority
            priority_order = {"immediate": 4, "high": 3, "medium": 2, "low": 1, "ongoing": 0}
            recommendations.sort(
                key=lambda x: priority_order.get(x.get("priority", "low"), 0),
                reverse=True
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Anomaly recommendation generation failed: {e}")
            return [{
                "priority": "high",
                "category": "manual_review",
                "action": "Conduct manual analysis of recent performance changes",
                "timeline": "As soon as possible",
                "expected_outcome": "Identify and address performance issues"
            }]

    def _calculate_analysis_confidence(
        self, anomaly_data: dict, historical_context: dict, root_causes: List[dict]
    ) -> float:
        """Calculate confidence score for the anomaly analysis"""
        try:
            confidence_factors = []
            
            # Data availability
            if historical_context.get("posts"):
                confidence_factors.append(0.3)
            if historical_context.get("daily_metrics"):
                confidence_factors.append(0.2)
            
            # Root cause confidence
            if root_causes:
                avg_cause_confidence = np.mean([c.get("confidence", 0) for c in root_causes])
                confidence_factors.append(avg_cause_confidence * 0.3)
            
            # Anomaly strength
            z_score = anomaly_data.get("z_score", 0)
            if z_score > 3:
                confidence_factors.append(0.2)
            elif z_score > 2:
                confidence_factors.append(0.15)
            else:
                confidence_factors.append(0.1)
            
            return min(1.0, sum(confidence_factors))
            
        except Exception:
            return 0.5  # Default moderate confidence

    def _severity_score(self, severity: str) -> int:
        """Convert severity string to numeric score for sorting"""
        severity_map = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "unknown": 0
        }
        return severity_map.get(severity.lower(), 0)

    async def health_check(self) -> dict:
        """Health check for anomaly analysis service"""
        return {
            "service": "AnomalyAnalysisService",
            "status": "healthy",
            "capabilities": [
                "anomaly_detection",
                "root_cause_analysis",
                "severity_assessment",
                "natural_language_explanations",
                "recommendation_generation",
                "statistical_analysis"
            ],
            "supported_metrics": [
                "views",
                "engagement",
                "growth",
                "followers"
            ],
            "dependencies": {
                "nlg_service": True,
                "numpy": True
            },
            "timestamp": datetime.now().isoformat()
        }