"""
Mock Analytics Adapter
======================

Mock implementation for development and testing.
"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Any

from core.adapters.analytics import AnalyticsAdapter

logger = logging.getLogger(__name__)


class MockAnalyticsAdapter(AnalyticsAdapter):
    """
    Mock implementation of AnalyticsAdapter for development/testing
    """

    def __init__(self):
        self.channels_cache = {}
        self.posts_cache = {}
        logger.info("MockAnalyticsAdapter initialized")

    def get_adapter_name(self) -> str:
        return "mock_analytics"

    def _generate_realistic_data(
        self, base_value: int, days: int, trend: float = 0.0
    ) -> list[dict[str, Any]]:
        """Generate realistic mock data with trends and variations"""
        data = []
        current_value = base_value

        for i in range(days):
            # Add random variation (±10-30%)
            variation = random.uniform(-0.3, 0.3)
            daily_value = int(current_value * (1 + variation))

            # Apply trend
            current_value *= 1 + trend / 100

            # Ensure minimum values
            daily_value = max(daily_value, int(base_value * 0.1))

            date = datetime.now() - timedelta(days=days - i - 1)
            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "value": daily_value,
                    "timestamp": int(date.timestamp()),
                }
            )

        return data

    async def get_channel_analytics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get mock channel analytics"""

        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.1, 0.5))

        days = (end_date - start_date).days + 1

        # Generate base metrics based on channel_id hash for consistency
        base_subscribers = 1000 + (hash(channel_id) % 10000)
        base_views = 500 + (hash(channel_id) % 5000)
        base_posts = 5 + (hash(channel_id) % 15)

        # Generate trend data
        subscribers_data = self._generate_realistic_data(base_subscribers, days, trend=2.0)
        views_data = self._generate_realistic_data(base_views, days, trend=1.5)
        posts_data = self._generate_realistic_data(base_posts, days, trend=0.0)

        analytics = {
            "channel_id": channel_id,
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days,
            },
            "overview": {
                "total_subscribers": subscribers_data[-1]["value"],
                "subscriber_change": subscribers_data[-1]["value"] - subscribers_data[0]["value"],
                "total_views": sum(item["value"] for item in views_data),
                "total_posts": sum(item["value"] for item in posts_data),
                "avg_engagement_rate": round(random.uniform(3.5, 8.5), 2),
                "avg_views_per_post": round(
                    sum(item["value"] for item in views_data)
                    / max(sum(item["value"] for item in posts_data), 1)
                ),
            },
            "time_series": {
                "subscribers": subscribers_data,
                "views": views_data,
                "posts": posts_data,
                "engagement": self._generate_realistic_data(
                    int(base_views * 0.05), days, trend=0.5
                ),
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "mock_analytics",
                "mock": True,
            },
        }

        logger.info(f"Generated mock channel analytics for {channel_id}")
        return analytics

    async def get_post_analytics(self, post_id: str, channel_id: str) -> dict[str, Any]:
        """Get mock post analytics"""

        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Generate consistent data based on post_id
        base_views = 100 + (hash(post_id) % 2000)
        base_likes = int(base_views * random.uniform(0.03, 0.08))
        base_shares = int(base_likes * random.uniform(0.1, 0.3))
        base_comments = int(base_likes * random.uniform(0.05, 0.15))

        # Simulate hourly data for last 24 hours
        hourly_views = []
        for i in range(24):
            hour_date = datetime.now() - timedelta(hours=23 - i)
            hourly_views.append(
                {
                    "hour": hour_date.strftime("%Y-%m-%d %H:00"),
                    "views": random.randint(int(base_views * 0.02), int(base_views * 0.1)),
                    "timestamp": int(hour_date.timestamp()),
                }
            )

        analytics = {
            "post_id": post_id,
            "channel_id": channel_id,
            "metrics": {
                "total_views": base_views,
                "total_likes": base_likes,
                "total_shares": base_shares,
                "total_comments": base_comments,
                "engagement_rate": round(
                    (base_likes + base_shares + base_comments) / base_views * 100, 2
                ),
                "reach": int(base_views * random.uniform(0.8, 1.2)),
                "impressions": int(base_views * random.uniform(1.2, 2.0)),
            },
            "time_series": {
                "hourly_views": hourly_views,
                "engagement_by_hour": [
                    {
                        "hour": item["hour"],
                        "engagement": random.randint(1, 20),
                        "timestamp": item["timestamp"],
                    }
                    for item in hourly_views
                ],
            },
            "demographics": {
                "age_groups": {
                    "18-24": random.randint(15, 25),
                    "25-34": random.randint(30, 45),
                    "35-44": random.randint(20, 30),
                    "45-54": random.randint(10, 20),
                    "55+": random.randint(5, 15),
                },
                "gender": {"male": random.randint(45, 65), "female": random.randint(35, 55)},
                "top_locations": [
                    {"country": "United States", "percentage": random.randint(20, 35)},
                    {"country": "United Kingdom", "percentage": random.randint(10, 20)},
                    {"country": "Canada", "percentage": random.randint(8, 15)},
                    {"country": "Germany", "percentage": random.randint(5, 12)},
                    {"country": "France", "percentage": random.randint(4, 10)},
                ],
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "mock_analytics",
                "mock": True,
            },
        }

        logger.info(f"Generated mock post analytics for {post_id}")
        return analytics

    async def get_audience_demographics(self, channel_id: str) -> dict[str, Any]:
        """Get mock audience demographics"""

        await asyncio.sleep(random.uniform(0.1, 0.3))

        demographics = {
            "channel_id": channel_id,
            "total_audience": 1000 + (hash(channel_id) % 10000),
            "age_distribution": {
                "13-17": random.randint(5, 15),
                "18-24": random.randint(20, 30),
                "25-34": random.randint(30, 40),
                "35-44": random.randint(15, 25),
                "45-54": random.randint(8, 18),
                "55-64": random.randint(3, 10),
                "65+": random.randint(1, 5),
            },
            "gender_distribution": {
                "male": random.randint(40, 60),
                "female": random.randint(40, 60),
                "other": random.randint(0, 3),
            },
            "geographic_distribution": {
                "North America": random.randint(25, 40),
                "Europe": random.randint(20, 35),
                "Asia": random.randint(15, 30),
                "South America": random.randint(5, 15),
                "Africa": random.randint(2, 8),
                "Oceania": random.randint(1, 5),
            },
            "device_usage": {
                "mobile": random.randint(60, 80),
                "desktop": random.randint(15, 30),
                "tablet": random.randint(5, 15),
            },
            "activity_patterns": {
                "most_active_hours": [
                    {"hour": "09:00", "activity_percentage": random.randint(8, 15)},
                    {"hour": "12:00", "activity_percentage": random.randint(10, 18)},
                    {"hour": "18:00", "activity_percentage": random.randint(15, 25)},
                    {"hour": "21:00", "activity_percentage": random.randint(12, 20)},
                ],
                "most_active_days": {
                    "Monday": random.randint(12, 18),
                    "Tuesday": random.randint(10, 16),
                    "Wednesday": random.randint(11, 17),
                    "Thursday": random.randint(13, 19),
                    "Friday": random.randint(15, 22),
                    "Saturday": random.randint(14, 20),
                    "Sunday": random.randint(16, 24),
                },
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "mock_analytics",
                "mock": True,
            },
        }

        logger.info(f"Generated mock audience demographics for {channel_id}")
        return demographics

    async def get_engagement_metrics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get mock engagement metrics"""

        await asyncio.sleep(random.uniform(0.2, 0.4))

        days = (end_date - start_date).days + 1

        # Generate engagement metrics
        base_engagement = 100 + (hash(channel_id) % 500)
        engagement_data = self._generate_realistic_data(base_engagement, days, trend=1.0)

        metrics = {
            "channel_id": channel_id,
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days,
            },
            "overview": {
                "total_engagements": sum(item["value"] for item in engagement_data),
                "average_daily_engagement": round(
                    sum(item["value"] for item in engagement_data) / days, 2
                ),
                "engagement_growth": round(
                    (engagement_data[-1]["value"] - engagement_data[0]["value"])
                    / engagement_data[0]["value"]
                    * 100,
                    2,
                ),
                "peak_engagement_day": max(engagement_data, key=lambda x: x["value"])["date"],
            },
            "breakdown": {
                "likes": {
                    "total": sum(item["value"] for item in engagement_data)
                    * random.uniform(0.6, 0.8),
                    "percentage": random.randint(60, 75),
                },
                "shares": {
                    "total": sum(item["value"] for item in engagement_data)
                    * random.uniform(0.1, 0.2),
                    "percentage": random.randint(10, 20),
                },
                "comments": {
                    "total": sum(item["value"] for item in engagement_data)
                    * random.uniform(0.1, 0.15),
                    "percentage": random.randint(8, 18),
                },
                "saves": {
                    "total": sum(item["value"] for item in engagement_data)
                    * random.uniform(0.05, 0.1),
                    "percentage": random.randint(3, 12),
                },
            },
            "time_series": {
                "daily_engagement": engagement_data,
                "engagement_rate": [
                    {
                        "date": item["date"],
                        "rate": round(random.uniform(3.0, 8.0), 2),
                        "timestamp": item["timestamp"],
                    }
                    for item in engagement_data
                ],
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "mock_analytics",
                "mock": True,
            },
        }

        logger.info(f"Generated mock engagement metrics for {channel_id}")
        return metrics

    async def get_growth_metrics(
        self, channel_id: str, start_date: datetime, end_date: datetime
    ) -> dict[str, Any]:
        """Get mock growth metrics"""

        await asyncio.sleep(random.uniform(0.2, 0.4))

        days = (end_date - start_date).days + 1

        # Generate growth data
        base_followers = 1000 + (hash(channel_id) % 10000)
        followers_data = self._generate_realistic_data(base_followers, days, trend=1.5)

        # Calculate growth rates
        growth_rates = []
        for i in range(1, len(followers_data)):
            prev_value = followers_data[i - 1]["value"]
            curr_value = followers_data[i]["value"]
            growth_rate = (curr_value - prev_value) / prev_value * 100 if prev_value > 0 else 0
            growth_rates.append(
                {
                    "date": followers_data[i]["date"],
                    "growth_rate": round(growth_rate, 2),
                    "new_followers": curr_value - prev_value,
                    "timestamp": followers_data[i]["timestamp"],
                }
            )

        metrics = {
            "channel_id": channel_id,
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days,
            },
            "overview": {
                "total_followers_start": followers_data[0]["value"],
                "total_followers_end": followers_data[-1]["value"],
                "net_growth": followers_data[-1]["value"] - followers_data[0]["value"],
                "growth_percentage": round(
                    (followers_data[-1]["value"] - followers_data[0]["value"])
                    / followers_data[0]["value"]
                    * 100,
                    2,
                ),
                "average_daily_growth": round(
                    (followers_data[-1]["value"] - followers_data[0]["value"]) / days, 2
                ),
                "best_growth_day": max(growth_rates, key=lambda x: x["new_followers"])["date"]
                if growth_rates
                else None,
            },
            "acquisition_channels": {
                "organic_search": random.randint(30, 45),
                "direct": random.randint(20, 35),
                "social_media": random.randint(15, 25),
                "referrals": random.randint(5, 15),
                "paid_advertising": random.randint(2, 10),
            },
            "retention_metrics": {
                "7_day_retention": round(random.uniform(70, 85), 2),
                "30_day_retention": round(random.uniform(55, 75), 2),
                "90_day_retention": round(random.uniform(40, 60), 2),
                "churn_rate": round(random.uniform(5, 15), 2),
            },
            "time_series": {"followers_count": followers_data, "growth_rates": growth_rates},
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "mock_analytics",
                "mock": True,
            },
        }

        logger.info(f"Generated mock growth metrics for {channel_id}")
        return metrics

    async def get_best_posting_times(self, channel_id: str) -> dict[str, Any]:
        """Get mock best posting times analysis"""
        await asyncio.sleep(random.uniform(0.1, 0.3))

        # Generate realistic posting time recommendations
        best_times = {
            "channel_id": channel_id,
            "analysis_period": "last_30_days",
            "best_hours": [
                {"hour": 9, "engagement_score": round(random.uniform(7.5, 9.5), 2), "time": "09:00"},
                {"hour": 13, "engagement_score": round(random.uniform(7.0, 9.0), 2), "time": "13:00"},
                {"hour": 18, "engagement_score": round(random.uniform(8.0, 9.5), 2), "time": "18:00"},
                {"hour": 21, "engagement_score": round(random.uniform(7.5, 9.0), 2), "time": "21:00"},
            ],
            "best_days": [
                {"day": "Tuesday", "engagement_score": round(random.uniform(8.0, 9.5), 2)},
                {"day": "Wednesday", "engagement_score": round(random.uniform(7.5, 9.0), 2)},
                {"day": "Thursday", "engagement_score": round(random.uniform(7.8, 9.2), 2)},
            ],
            "worst_hours": [
                {"hour": 3, "engagement_score": round(random.uniform(2.0, 4.0), 2), "time": "03:00"},
                {"hour": 5, "engagement_score": round(random.uniform(2.5, 4.5), 2), "time": "05:00"},
            ],
            "recommendations": [
                "Post between 6 PM and 9 PM for maximum engagement",
                "Avoid posting between 3 AM and 6 AM",
                "Tuesday and Wednesday show highest engagement",
                "Weekend posts get 15-20% lower engagement",
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "adapter": "mock_analytics",
                "mock": True,
            },
        }

        logger.info(f"Generated mock posting times for {channel_id}")
        return best_times

    async def health_check(self) -> dict[str, Any]:
        """Mock analytics health check"""
        return {
            "status": "healthy",
            "adapter": "mock_analytics",
            "timestamp": int(datetime.now().timestamp()),
            "mock_data": {
                "channels_cached": len(self.channels_cache),
                "posts_cached": len(self.posts_cache),
                "uptime": "100%",
                "response_time_ms": random.randint(50, 200),
            },
            "features": [
                "channel_analytics",
                "post_analytics",
                "audience_demographics",
                "engagement_metrics",
                "growth_metrics",
            ],
        }

    async def close(self):
        """Close mock analytics adapter (no-op for mock)"""
        logger.info("MockAnalyticsAdapter closed")
        pass
