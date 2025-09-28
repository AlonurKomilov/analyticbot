"""
Mock Analytics Service
Implements AnalyticsServiceProtocol for demo mode
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Any

from apps.api.__mocks__.constants import DEMO_API_DELAY_MS

from core.protocols import AnalyticsServiceProtocol

logger = logging.getLogger(__name__)


class MockAnalyticsService(AnalyticsServiceProtocol):
    """Mock analytics service for demo mode"""

    def __init__(self):
        self.service_name = "MockAnalyticsService"
        logger.info(f"Initialized {self.service_name}")

    def get_service_name(self) -> str:
        return self.service_name

    async def health_check(self) -> dict[str, Any]:
        """Mock service health check"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "status": "healthy",
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True,
        }

    async def get_channel_metrics(self, channel_id: str, period: str = "7d") -> dict[str, Any]:
        """Get mock channel analytics metrics"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        # Generate realistic mock data based on period
        self._parse_period_days(period)
        base_views = random.randint(10000, 50000)

        return {
            "channel_id": channel_id,
            "period": period,
            "metrics": {
                "total_views": base_views + random.randint(-5000, 15000),
                "total_subscribers": random.randint(1000, 10000),
                "average_engagement_rate": round(random.uniform(0.05, 0.15), 3),
                "total_posts": random.randint(5, 50),
                "growth_rate": round(random.uniform(-0.02, 0.08), 3),
                "best_performing_time": random.choice(["09:00", "12:00", "18:00", "21:00"]),
                "top_hashtags": ["#analytics", "#telegram", "#growth", "#engagement"],
            },
            "timestamp": datetime.utcnow().isoformat(),
            "generated_by": "MockAnalyticsService",
        }

    async def get_engagement_data(self, channel_id: str, period: str = "24h") -> dict[str, Any]:
        """Get mock engagement analytics"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        hours = self._parse_period_hours(period)
        hourly_data = []

        for i in range(hours):
            timestamp = datetime.utcnow() - timedelta(hours=hours - i)
            hourly_data.append(
                {
                    "hour": timestamp.strftime("%Y-%m-%d %H:00"),
                    "views": random.randint(100, 1000),
                    "likes": random.randint(10, 100),
                    "shares": random.randint(1, 20),
                    "comments": random.randint(0, 15),
                    "engagement_rate": round(random.uniform(0.03, 0.12), 3),
                }
            )

        return {
            "channel_id": channel_id,
            "period": period,
            "engagement_data": hourly_data,
            "summary": {
                "total_engagement": sum(
                    h["likes"] + h["shares"] + h["comments"] for h in hourly_data
                ),
                "average_engagement_rate": round(
                    sum(h["engagement_rate"] for h in hourly_data) / len(hourly_data), 3
                ),
                "peak_hour": max(hourly_data, key=lambda x: x["engagement_rate"])["hour"],
            },
            "timestamp": datetime.utcnow().isoformat(),
            "generated_by": "MockAnalyticsService",
        }

    async def get_post_performance(self, channel_id: str, post_id: str) -> dict[str, Any]:
        """Get mock individual post performance"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        return {
            "channel_id": channel_id,
            "post_id": post_id,
            "performance": {
                "views": random.randint(500, 5000),
                "likes": random.randint(20, 200),
                "shares": random.randint(5, 50),
                "comments": random.randint(1, 30),
                "reach": random.randint(400, 4500),
                "engagement_rate": round(random.uniform(0.04, 0.16), 3),
                "click_through_rate": round(random.uniform(0.01, 0.05), 3),
            },
            "post_details": {
                "published_at": (
                    datetime.utcnow() - timedelta(hours=random.randint(1, 72))
                ).isoformat(),
                "content_type": random.choice(["text", "image", "video", "poll"]),
                "hashtags_count": random.randint(0, 5),
                "word_count": random.randint(10, 200),
            },
            "timestamp": datetime.utcnow().isoformat(),
            "generated_by": "MockAnalyticsService",
        }

    async def get_best_posting_times(self, channel_id: str) -> dict[str, Any]:
        """Get mock optimal posting times"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        # Generate best times for each day
        best_times = {}
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        for day in days:
            best_times[day] = {
                "optimal_hour": random.choice([9, 12, 15, 18, 21]),
                "engagement_score": round(random.uniform(0.8, 1.0), 2),
                "confidence": round(random.uniform(0.7, 0.95), 2),
            }

        return {
            "channel_id": channel_id,
            "best_times": best_times,
            "overall_best": {
                "day": random.choice(days),
                "hour": random.choice([18, 19, 20, 21]),
                "engagement_score": round(random.uniform(0.85, 1.0), 2),
            },
            "analysis_period": "30 days",
            "data_points": random.randint(50, 200),
            "timestamp": datetime.utcnow().isoformat(),
            "generated_by": "MockAnalyticsService",
        }

    async def get_audience_insights(self, channel_id: str) -> dict[str, Any]:
        """Get mock audience demographics and insights"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        return {
            "channel_id": channel_id,
            "audience_insights": {
                "demographics": {
                    "age_groups": {
                        "18-24": random.randint(15, 30),
                        "25-34": random.randint(25, 40),
                        "35-44": random.randint(15, 30),
                        "45-54": random.randint(10, 20),
                        "55+": random.randint(5, 15),
                    },
                    "gender_distribution": {
                        "male": random.randint(45, 65),
                        "female": random.randint(35, 55),
                    },
                    "top_countries": [
                        {
                            "country": "United States",
                            "percentage": random.randint(20, 35),
                        },
                        {
                            "country": "United Kingdom",
                            "percentage": random.randint(10, 20),
                        },
                        {"country": "Germany", "percentage": random.randint(8, 15)},
                        {"country": "Canada", "percentage": random.randint(5, 12)},
                    ],
                },
                "behavior": {
                    "most_active_hours": [18, 19, 20, 21, 22],
                    "engagement_patterns": {
                        "peak_days": ["wednesday", "thursday", "sunday"],
                        "response_time": "2-4 hours",
                        "content_preference": random.choice(["images", "videos", "text", "polls"]),
                    },
                },
                "growth": {
                    "subscriber_growth_rate": round(random.uniform(0.02, 0.08), 3),
                    "retention_rate": round(random.uniform(0.75, 0.92), 3),
                    "churn_rate": round(random.uniform(0.05, 0.15), 3),
                },
            },
            "timestamp": datetime.utcnow().isoformat(),
            "generated_by": "MockAnalyticsService",
        }

    def _parse_period_days(self, period: str) -> int:
        """Parse period string to days"""
        if period.endswith("d"):
            return int(period[:-1])
        elif period.endswith("w"):
            return int(period[:-1]) * 7
        elif period.endswith("m"):
            return int(period[:-1]) * 30
        return 7  # default

    def _parse_period_hours(self, period: str) -> int:
        """Parse period string to hours"""
        if period.endswith("h"):
            return int(period[:-1])
        elif period.endswith("d"):
            return int(period[:-1]) * 24
        return 24  # default
