"""
Analytics Core Service
=====================

Microservice for core analytics processing.
Single responsibility: Analytics calculations and processing only.

Replaces the god object methods with focused analytics functionality.
"""

import logging
from datetime import datetime
from typing import Any

from ..infrastructure.data_access import DataAccessService
from ..protocols.analytics_protocols import (
    AnalyticsCoreProtocol,
    AnalyticsResult,
    MetricsData,
    ProcessingConfig,
)
from .engines.analytics_engine import AnalyticsEngine
from .processors.data_processor import DataProcessor
from .processors.metrics_processor import MetricsProcessor

logger = logging.getLogger(__name__)


class AnalyticsCoreService(AnalyticsCoreProtocol):
    """
    Core analytics processing microservice.

    Single responsibility: Core analytics calculations and processing.
    Extracted from AnalyticsFusionService god object.
    """

    def __init__(
        self,
        data_access_service: DataAccessService,
        data_processor: DataProcessor | None = None,
        metrics_processor: MetricsProcessor | None = None,
        analytics_engine: AnalyticsEngine | None = None,
    ):
        self.data_access = data_access_service
        self.data_processor = data_processor or DataProcessor()
        self.metrics_processor = metrics_processor or MetricsProcessor()
        self.analytics_engine = analytics_engine or AnalyticsEngine()

        # Service state
        self.processing_count = 0
        self.last_processing_time: datetime | None = None
        self.total_processing_time_ms = 0

        # Cache for performance
        self.analytics_cache = {}
        self.cache_ttl_seconds = 300  # 5 minutes

        logger.info("🎯 Analytics Core Service initialized - single responsibility")

    async def process_channel_metrics(
        self, channel_id: int, config: ProcessingConfig | None = None
    ) -> AnalyticsResult:
        """Process comprehensive metrics for a channel"""
        start_time = datetime.utcnow()
        processing_config = config or ProcessingConfig()

        try:
            logger.info(f"📊 Processing metrics for channel {channel_id}")

            # Get comprehensive channel data
            channel_data = await self.data_access.get_comprehensive_channel_data(
                channel_id, processing_config.time_range_days
            )

            # Validate data availability
            if not await self._validate_channel_data(channel_data):
                return AnalyticsResult(
                    channel_id=channel_id,
                    analysis_type="metrics_processing",
                    results={"error": "Insufficient data for analysis"},
                    confidence_score=0.0,
                    timestamp=datetime.utcnow(),
                    processing_time_ms=0,
                )

            # Process data through pipeline
            processed_data = await self.data_processor.process_raw_data(channel_data)

            # Calculate metrics based on configuration
            metrics_results = {}

            if processing_config.include_engagement:
                engagement_metrics = await self.metrics_processor.calculate_engagement_metrics(
                    channel_data
                )
                metrics_results["engagement"] = engagement_metrics

            if processing_config.include_performance:
                performance_metrics = await self.metrics_processor.calculate_performance_metrics(
                    channel_data
                )
                metrics_results["performance"] = performance_metrics

            # Run analytics engine
            analytics_results = await self.analytics_engine.run_analytics_pipeline(
                channel_id, processing_config
            )

            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                metrics_results, analytics_results
            )

            # Track performance
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.processing_count += 1
            self.total_processing_time_ms += processing_time
            self.last_processing_time = datetime.utcnow()

            result = AnalyticsResult(
                channel_id=channel_id,
                analysis_type="comprehensive_metrics",
                results={
                    "metrics": metrics_results,
                    "analytics": analytics_results,
                    "processed_data_points": len(channel_data.get("daily_data", [])),
                    "processing_config": processing_config.__dict__,
                },
                confidence_score=confidence_score,
                timestamp=datetime.utcnow(),
                processing_time_ms=int(processing_time),
            )

            # Cache result for performance
            cache_key = f"metrics_{channel_id}_{processing_config.time_range_days}"
            self.analytics_cache[cache_key] = {"result": result, "cached_at": datetime.utcnow()}

            logger.info(
                f"✅ Processed metrics in {processing_time:.1f}ms with confidence {confidence_score:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error processing channel metrics: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return AnalyticsResult(
                channel_id=channel_id,
                analysis_type="metrics_processing_error",
                results={"error": str(e)},
                confidence_score=0.0,
                timestamp=datetime.utcnow(),
                processing_time_ms=int(processing_time),
            )

    async def calculate_performance_scores(self, metrics: MetricsData) -> dict[str, Any]:
        """Calculate normalized performance scores"""
        try:
            logger.info(f"📈 Calculating performance scores for channel {metrics.channel_id}")

            # Use metrics processor for calculations
            performance_scores = {}

            # Engagement score (0-100)
            engagement_score = await self._calculate_engagement_score(metrics.engagement_metrics)
            performance_scores["engagement_score"] = engagement_score

            # Performance score (0-100)
            performance_score = await self._calculate_performance_score(metrics.performance_metrics)
            performance_scores["performance_score"] = performance_score

            # Content quality score (0-100)
            content_score = await self._calculate_content_score(metrics.content_metrics)
            performance_scores["content_score"] = content_score

            # Overall score (weighted average)
            overall_score = engagement_score * 0.4 + performance_score * 0.4 + content_score * 0.2
            performance_scores["overall_score"] = overall_score

            logger.info(f"✅ Calculated performance scores: overall={overall_score:.1f}")
            return performance_scores

        except Exception as e:
            logger.error(f"❌ Error calculating performance scores: {e}")
            return {
                "engagement_score": 0.0,
                "performance_score": 0.0,
                "content_score": 0.0,
                "overall_score": 0.0,
                "error": str(e),
            }

    async def analyze_engagement_patterns(
        self, channel_id: int, time_range_days: int = 30
    ) -> dict[str, Any]:
        """Analyze engagement patterns and trends"""
        try:
            logger.info(f"🔍 Analyzing engagement patterns for channel {channel_id}")

            # Get channel data
            channel_data = await self.data_access.get_comprehensive_channel_data(
                channel_id, time_range_days
            )

            # Use analytics engine for pattern analysis
            patterns = await self.analytics_engine.analyze_channel_performance(channel_id)

            # Extract engagement patterns
            engagement_patterns = {
                "daily_patterns": await self._analyze_daily_patterns(channel_data),
                "weekly_patterns": await self._analyze_weekly_patterns(channel_data),
                "content_patterns": await self._analyze_content_patterns(channel_data),
                "trend_analysis": patterns.get("trends", {}),
                "anomaly_detection": patterns.get("anomalies", []),
            }

            logger.info(f"✅ Analyzed engagement patterns for {time_range_days} days")
            return engagement_patterns

        except Exception as e:
            logger.error(f"❌ Error analyzing engagement patterns: {e}")
            return {"error": str(e)}

    async def validate_analytics_data(self, data: MetricsData) -> bool:
        """Validate analytics data quality"""
        try:
            # Use data processor for validation
            return await self.data_processor.validate_data_quality(data)

        except Exception as e:
            logger.error(f"❌ Error validating analytics data: {e}")
            return False

    async def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        avg_processing_time = (
            self.total_processing_time_ms / self.processing_count
            if self.processing_count > 0
            else 0
        )

        return {
            "service": "analytics_core",
            "status": "healthy",
            "processing_count": self.processing_count,
            "average_processing_time_ms": avg_processing_time,
            "last_processing_time": self.last_processing_time,
            "cache_size": len(self.analytics_cache),
            "components": {
                "data_processor": True,
                "metrics_processor": True,
                "analytics_engine": True,
                "data_access": True,
            },
        }

    # Private helper methods

    async def _validate_channel_data(self, channel_data: dict[str, Any]) -> bool:
        """Validate that channel data is sufficient for analysis"""
        if not channel_data or "error" in channel_data:
            return False

        daily_data = channel_data.get("daily_data", [])
        post_data = channel_data.get("post_data", [])

        return len(daily_data) >= 5 and len(post_data) >= 10  # Minimum data requirements

    async def _calculate_confidence_score(
        self, metrics_results: dict[str, Any], analytics_results: Any
    ) -> float:
        """Calculate confidence score for analysis results"""
        try:
            # Simple confidence calculation based on data completeness
            data_completeness = 0.8  # Placeholder
            metrics_quality = 0.9  # Placeholder
            analytics_quality = 0.85  # Placeholder

            confidence = (data_completeness + metrics_quality + analytics_quality) / 3
            return min(max(confidence, 0.0), 1.0)

        except Exception:
            return 0.5  # Default medium confidence

    async def _calculate_engagement_score(self, engagement_metrics: dict[str, float]) -> float:
        """Calculate normalized engagement score"""
        # Simplified engagement score calculation
        try:
            base_score = sum(engagement_metrics.values()) / len(engagement_metrics)
            return min(max(base_score * 100, 0.0), 100.0)
        except (ZeroDivisionError, TypeError):
            return 0.0

    async def _calculate_performance_score(self, performance_metrics: dict[str, float]) -> float:
        """Calculate normalized performance score"""
        # Simplified performance score calculation
        try:
            base_score = sum(performance_metrics.values()) / len(performance_metrics)
            return min(max(base_score * 100, 0.0), 100.0)
        except (ZeroDivisionError, TypeError):
            return 0.0

    async def _calculate_content_score(self, content_metrics: dict[str, Any]) -> float:
        """Calculate normalized content quality score"""
        # Simplified content score calculation
        try:
            # This would analyze content quality metrics
            return 75.0  # Placeholder
        except Exception:
            return 0.0

    async def _analyze_daily_patterns(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze daily engagement patterns"""
        # Placeholder for daily pattern analysis
        return {
            "peak_hours": [18, 19, 20],
            "low_hours": [3, 4, 5],
            "average_daily_engagement": 0.75,
        }

    async def _analyze_weekly_patterns(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze weekly engagement patterns"""
        # Placeholder for weekly pattern analysis
        return {
            "peak_days": ["Saturday", "Sunday"],
            "low_days": ["Tuesday", "Wednesday"],
            "weekly_trend": "stable",
        }

    async def _analyze_content_patterns(self, channel_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze content engagement patterns"""
        # Placeholder for content pattern analysis
        return {
            "top_content_types": ["video", "image"],
            "content_performance": {"video": 0.85, "image": 0.72, "text": 0.68},
            "optimal_content_length": "100-200 words",
        }
