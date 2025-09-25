"""
Analytics Report Entity - Analytics Domain
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from uuid import uuid4

from ....shared_kernel.domain.base_entity import AggregateRoot
from ....shared_kernel.domain.value_objects import UserId, ValueObject
from ....shared_kernel.domain.exceptions import ValidationError, BusinessRuleViolationError
from ..value_objects.analytics_value_objects import (
    ChannelId, ViewCount, AnalyticsMetric
)
from ..events import AnalyticsInsightGenerated


class ReportId(ValueObject):
    """Report identifier value object"""
    
    def __init__(self, value: str):
        if not value or not isinstance(value, str):
            raise ValueError("Report ID must be a non-empty string")
        if len(value) < 3:
            raise ValueError("Report ID must be at least 3 characters")
        object.__setattr__(self, 'value', value)
    
    @classmethod
    def generate(cls) -> "ReportId":
        """Generate a new report ID"""
        return cls(f"report_{uuid4().hex[:12]}")
    
    def validate(self) -> None:
        """Validation is done in __init__"""
        pass
    
    def __str__(self) -> str:
        return self.value


class ReportType(str, Enum):
    """Report type enumeration"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class MetricTrend(str, Enum):
    """Metric trend direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    UNKNOWN = "unknown"


@dataclass
class ReportInsight:
    """Individual insight within an analytics report"""
    title: str
    description: str
    metric_name: str
    current_value: float
    previous_value: Optional[float] = None
    trend: MetricTrend = MetricTrend.UNKNOWN
    change_percentage: Optional[float] = None
    is_significant: bool = False
    
    def __post_init__(self):
        """Calculate trend and change percentage if previous value available"""
        if self.previous_value is not None:
            self.change_percentage = self._calculate_change_percentage()
            self.trend = self._determine_trend()
            self.is_significant = abs(self.change_percentage or 0) >= 10  # 10% threshold
    
    def _calculate_change_percentage(self) -> float:
        """Calculate percentage change from previous value"""
        if self.previous_value == 0:
            return 100.0 if self.current_value > 0 else 0.0
        return ((self.current_value - self.previous_value) / self.previous_value) * 100
    
    def _determine_trend(self) -> MetricTrend:
        """Determine trend based on change percentage"""
        if self.change_percentage is None:
            return MetricTrend.UNKNOWN
        
        if abs(self.change_percentage) < 5:  # Less than 5% change
            return MetricTrend.STABLE
        elif self.change_percentage > 0:
            return MetricTrend.UP
        else:
            return MetricTrend.DOWN


class AnalyticsReport(AggregateRoot[ReportId]):
    """
    Analytics Report aggregate root
    
    Represents a comprehensive analytics report for channels and posts
    within a specific time period. Contains aggregated metrics, insights,
    and trend analysis.
    """
    
    def __init__(
        self,
        id: ReportId,
        user_id: UserId,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime,
        title: str,
        description: Optional[str] = None,
        status: ReportStatus = ReportStatus.PENDING,
        generated_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        generation_duration_seconds: Optional[float] = None,
        included_channels: Optional[List[str]] = None,
        total_channels: int = 0,
        total_posts: int = 0,
        metrics: Optional[Dict[str, AnalyticsMetric]] = None,
        insights: Optional[List[ReportInsight]] = None,
        channel_summaries: Optional[List[Dict[str, Any]]] = None,
        top_performing_posts: Optional[List[Dict[str, Any]]] = None,
        previous_period_metrics: Optional[Dict[str, float]] = None,
        export_formats: Optional[List[str]] = None,
        is_shared: bool = False,
        share_token: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(
            id=id,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow()
        )
        
        # Core identity and metadata
        self.user_id = user_id
        self.report_type = report_type
        self.period_start = period_start
        self.period_end = period_end
        
        # Report content
        self.title = title
        self.description = description
        
        # Generation metadata
        self.status = status
        self.generated_at = generated_at
        self.expires_at = expires_at
        self.generation_duration_seconds = generation_duration_seconds
        
        # Scope (what channels/data this report covers)
        self.included_channels = included_channels or []
        self.total_channels = total_channels
        self.total_posts = total_posts
        
        # Aggregated metrics
        self.metrics = metrics or {}
        
        # Key insights and trends
        self.insights = insights or []
        
        # Raw data summaries
        self.channel_summaries = channel_summaries or []
        self.top_performing_posts = top_performing_posts or []
        
        # Comparison data (if available)
        self.previous_period_metrics = previous_period_metrics
        
        # Export and sharing
        self.export_formats = export_formats or ["json"]
        self.is_shared = is_shared
        self.share_token = share_token
        
        # Validate and set expiration
        self._validate_report_data()
        self._set_expiration()
    
    def _validate_report_data(self) -> None:
        """Validate report data consistency"""
        if self.period_start >= self.period_end:
            raise ValidationError("Period start must be before period end")
        
        if self.period_end > datetime.utcnow():
            raise ValidationError("Cannot create reports for future periods")
        
        # Validate report type and period alignment
        period_days = (self.period_end - self.period_start).days
        
        if self.report_type == ReportType.DAILY and period_days != 1:
            raise ValidationError("Daily reports must cover exactly 1 day")
        elif self.report_type == ReportType.WEEKLY and period_days != 7:
            raise ValidationError("Weekly reports must cover exactly 7 days")
        elif self.report_type == ReportType.MONTHLY and period_days not in range(28, 32):
            raise ValidationError("Monthly reports must cover 28-31 days")
    
    def _set_expiration(self) -> None:
        """Set report expiration based on type"""
        if self.expires_at is None:
            # Reports expire after different periods based on type
            if self.report_type == ReportType.DAILY:
                # Daily reports expire after 30 days
                self.expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59) + \
                                 timedelta(days=30)
            elif self.report_type == ReportType.WEEKLY:
                # Weekly reports expire after 90 days
                self.expires_at = datetime.utcnow() + timedelta(days=90)
            elif self.report_type == ReportType.MONTHLY:
                # Monthly reports expire after 1 year
                self.expires_at = datetime.utcnow() + timedelta(days=365)
            else:
                # Quarterly/Yearly/Custom expire after 2 years
                self.expires_at = datetime.utcnow() + timedelta(days=730)
    
    @classmethod
    def create_new_report(
        cls,
        user_id: UserId,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime,
        title: Optional[str] = None
    ) -> "AnalyticsReport":
        """
        Factory method to create a new analytics report
        """
        report_id = ReportId.generate()
        
        if title is None:
            title = cls._generate_default_title(report_type, period_start, period_end)
        
        report = cls(
            id=report_id,
            user_id=user_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            title=title,
            status=ReportStatus.PENDING
        )
        
        return report
    
    @classmethod
    def _generate_default_title(
        cls,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime
    ) -> str:
        """Generate a default title based on report type and period"""
        start_str = period_start.strftime("%Y-%m-%d")
        end_str = period_end.strftime("%Y-%m-%d")
        
        type_names = {
            ReportType.DAILY: "Daily",
            ReportType.WEEKLY: "Weekly",
            ReportType.MONTHLY: "Monthly",
            ReportType.QUARTERLY: "Quarterly",
            ReportType.YEARLY: "Yearly",
            ReportType.CUSTOM: "Custom"
        }
        
        type_name = type_names.get(report_type, "Analytics")
        
        if report_type == ReportType.DAILY:
            return f"{type_name} Analytics Report - {start_str}"
        else:
            return f"{type_name} Analytics Report - {start_str} to {end_str}"
    
    def start_generation(self) -> None:
        """Mark report generation as started"""
        if self.status != ReportStatus.PENDING:
            raise BusinessRuleViolationError("Can only start generation for pending reports")
        
        self.status = ReportStatus.GENERATING
        self.generated_at = datetime.utcnow()
        self.mark_as_updated()
    
    def complete_generation(self, generation_duration: Optional[float] = None) -> None:
        """
        Mark report generation as completed
        
        Business Rules:
        - Must have been in generating status
        - Must have at least one metric or insight
        """
        if self.status != ReportStatus.GENERATING:
            raise BusinessRuleViolationError("Can only complete reports that are being generated")
        
        if not self.metrics and not self.insights:
            raise BusinessRuleViolationError("Cannot complete report without metrics or insights")
        
        self.status = ReportStatus.COMPLETED
        if generation_duration is not None:
            self.generation_duration_seconds = generation_duration
        
        self.mark_as_updated()
        
        # Generate summary insights
        self._generate_automatic_insights()
        
        # Emit domain event
        self.add_domain_event(AnalyticsInsightGenerated(
            user_id=self.user_id.value,
            channel_id="",  # Report covers multiple channels
            insight_type="report_completion",
            insight_data={
                "report_id": self.id.value,
                "report_type": self.report_type.value,
                "total_channels": self.total_channels,
                "total_posts": self.total_posts,
                "key_metrics": len(self.metrics),
                "insights_count": len(self.insights)
            }
        ))
    
    def fail_generation(self, error_message: str) -> None:
        """Mark report generation as failed"""
        self.status = ReportStatus.FAILED
        self.description = f"Generation failed: {error_message}"
        self.mark_as_updated()
    
    def add_metric(self, metric: AnalyticsMetric) -> None:
        """Add a metric to the report"""
        if self.status != ReportStatus.GENERATING:
            raise BusinessRuleViolationError("Can only add metrics to reports being generated")
        
        self.metrics[metric.name] = metric
        self.mark_as_updated()
    
    def add_insight(self, insight: ReportInsight) -> None:
        """Add an insight to the report"""
        if self.status != ReportStatus.GENERATING:
            raise BusinessRuleViolationError("Can only add insights to reports being generated")
        
        self.insights.append(insight)
        self.mark_as_updated()
    
    def add_channel_data(
        self,
        channel_id: str,
        channel_data: Dict[str, Any]
    ) -> None:
        """Add channel data to the report"""
        if self.status != ReportStatus.GENERATING:
            raise BusinessRuleViolationError("Can only add data to reports being generated")
        
        # Add to included channels if not already present
        if channel_id not in self.included_channels:
            self.included_channels.append(channel_id)
        
        # Add to channel summaries
        summary = {"channel_id": channel_id, **channel_data}
        self.channel_summaries.append(summary)
        
        # Update totals
        self.total_channels = len(self.included_channels)
        if "post_count" in channel_data:
            self.total_posts += channel_data["post_count"]
        
        self.mark_as_updated()
    
    def add_top_performing_post(self, post_data: Dict[str, Any]) -> None:
        """Add a top-performing post to the report"""
        if self.status != ReportStatus.GENERATING:
            raise BusinessRuleViolationError("Can only add data to reports being generated")
        
        self.top_performing_posts.append(post_data)
        # Keep only top 50 posts to avoid memory issues
        if len(self.top_performing_posts) > 50:
            # Sort by performance score and keep top 50
            self.top_performing_posts.sort(
                key=lambda x: x.get("performance_score", 0), 
                reverse=True
            )
            self.top_performing_posts = self.top_performing_posts[:50]
        
        self.mark_as_updated()
    
    def set_comparison_data(self, previous_metrics: Dict[str, float]) -> None:
        """Set comparison data from previous period"""
        self.previous_period_metrics = previous_metrics
        self._update_insights_with_comparisons()
        self.mark_as_updated()
    
    def _update_insights_with_comparisons(self) -> None:
        """Update existing insights with comparison data"""
        if not self.previous_period_metrics:
            return
        
        for insight in self.insights:
            if insight.metric_name in self.previous_period_metrics:
                insight.previous_value = self.previous_period_metrics[insight.metric_name]
                insight.__post_init__()  # Recalculate trend and change
    
    def _generate_automatic_insights(self) -> None:
        """Generate automatic insights based on metrics"""
        if not self.metrics:
            return
        
        # Find the metric with highest value (could be views, posts, etc.)
        max_metric = max(self.metrics.values(), key=lambda m: m.value)
        self.add_insight(ReportInsight(
            title=f"Top Metric: {max_metric.display_name}",
            description=f"Highest value metric in this period: {max_metric.formatted_value}",
            metric_name=max_metric.name,
            current_value=max_metric.value
        ))
        
        # Generate insights for metrics with significant changes
        if self.previous_period_metrics:
            for metric_name, metric in self.metrics.items():
                if metric_name in self.previous_period_metrics:
                    previous_value = self.previous_period_metrics[metric_name]
                    change_pct = ((metric.value - previous_value) / previous_value) * 100 if previous_value > 0 else 0
                    
                    if abs(change_pct) >= 20:  # Significant change threshold
                        direction = "increased" if change_pct > 0 else "decreased"
                        self.add_insight(ReportInsight(
                            title=f"{metric.display_name} {direction.capitalize()}",
                            description=f"{metric.display_name} {direction} by {abs(change_pct):.1f}% compared to previous period",
                            metric_name=metric_name,
                            current_value=metric.value,
                            previous_value=previous_value,
                            is_significant=True
                        ))
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive summary of the report"""
        if self.status != ReportStatus.COMPLETED:
            raise BusinessRuleViolationError("Can only generate summaries for completed reports")
        
        # Calculate key statistics
        significant_insights = [i for i in self.insights if i.is_significant]
        positive_trends = [i for i in self.insights if i.trend == MetricTrend.UP]
        negative_trends = [i for i in self.insights if i.trend == MetricTrend.DOWN]
        
        return {
            "report_id": self.id.value,
            "title": self.title,
            "report_type": self.report_type.value,
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat(),
                "days": (self.period_end - self.period_start).days
            },
            "scope": {
                "total_channels": self.total_channels,
                "total_posts": self.total_posts,
                "included_channels": len(self.included_channels)
            },
            "metrics_summary": {
                "total_metrics": len(self.metrics),
                "key_metrics": {name: m.formatted_value for name, m in self.metrics.items()},
            },
            "insights_summary": {
                "total_insights": len(self.insights),
                "significant_insights": len(significant_insights),
                "positive_trends": len(positive_trends),
                "negative_trends": len(negative_trends),
                "key_insights": [
                    {
                        "title": i.title,
                        "trend": i.trend.value,
                        "change_percentage": i.change_percentage
                    } for i in significant_insights[:5]  # Top 5 significant insights
                ]
            },
            "performance": {
                "top_performing_posts": len(self.top_performing_posts),
                "generation_duration": self.generation_duration_seconds,
                "generated_at": self.generated_at.isoformat() if self.generated_at else None
            },
            "status": self.status.value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None
        }
    
    def export_data(self, format: str = "json") -> Dict[str, Any]:
        """Export report data in specified format"""
        if self.status != ReportStatus.COMPLETED:
            raise BusinessRuleViolationError("Can only export completed reports")
        
        if format not in self.export_formats:
            raise ValidationError(f"Export format {format} not supported")
        
        return {
            "report_metadata": {
                "id": self.id.value,
                "title": self.title,
                "description": self.description,
                "type": self.report_type.value,
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "generated_at": self.generated_at.isoformat() if self.generated_at else None,
                "generation_duration": self.generation_duration_seconds
            },
            "scope": {
                "user_id": self.user_id.value,
                "total_channels": self.total_channels,
                "total_posts": self.total_posts,
                "included_channels": self.included_channels
            },
            "metrics": {name: metric.to_dict() for name, metric in self.metrics.items()},
            "insights": [
                {
                    "title": i.title,
                    "description": i.description,
                    "metric_name": i.metric_name,
                    "current_value": i.current_value,
                    "previous_value": i.previous_value,
                    "trend": i.trend.value,
                    "change_percentage": i.change_percentage,
                    "is_significant": i.is_significant
                } for i in self.insights
            ],
            "channel_summaries": self.channel_summaries,
            "top_performing_posts": self.top_performing_posts,
            "export_info": {
                "format": format,
                "exported_at": datetime.utcnow().isoformat()
            }
        }
    
    def enable_sharing(self) -> str:
        """Enable report sharing and return share token"""
        if self.status != ReportStatus.COMPLETED:
            raise BusinessRuleViolationError("Can only share completed reports")
        
        if not self.share_token:
            self.share_token = f"share_{uuid4().hex[:16]}"
        
        self.is_shared = True
        self.mark_as_updated()
        return self.share_token
    
    def disable_sharing(self) -> None:
        """Disable report sharing"""
        self.is_shared = False
        self.share_token = None
        self.mark_as_updated()
    
    def is_expired(self) -> bool:
        """Check if report has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def extend_expiration(self, days: int = 30) -> None:
        """Extend report expiration"""
        if self.expires_at:
            self.expires_at += timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        self.mark_as_updated()
    
    def get_metric(self, metric_name: str) -> Optional[AnalyticsMetric]:
        """Get a specific metric by name"""
        return self.metrics.get(metric_name)
    
    def has_significant_insights(self) -> bool:
        """Check if report has significant insights"""
        return any(insight.is_significant for insight in self.insights)
    
    def get_period_description(self) -> str:
        """Get human-readable description of the report period"""
        start_str = self.period_start.strftime("%B %d, %Y")
        end_str = self.period_end.strftime("%B %d, %Y")
        
        if self.report_type == ReportType.DAILY:
            return f"Daily report for {start_str}"
        else:
            return f"Report covering {start_str} to {end_str}"