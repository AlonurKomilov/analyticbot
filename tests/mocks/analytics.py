"""
Analytics Mock Data Generator
============================

This module provides comprehensive mock/demo data generation for analytics endpoints.
Consolidated from both backend and frontend to create single source of truth.
Moved from analytics_router.py to maintain clean separation of concerns.
"""

import random
from datetime import datetime, timedelta
from typing import Any

from .constants import (
    DEFAULT_DEMO_CHANNEL_ID,
    DEFAULT_DEMO_ENGAGEMENT_RATE,
    DEMO_METRICS_DAYS,
    DEMO_POSTS_COUNT,
)


def generate_post_dynamics(hours_back: int = 24) -> list[dict[str, Any]]:
    """
    Generate demo post dynamics data
    Consolidated from frontend demoAnalyticsService.js
    """
    dynamics = []
    now = datetime.now()

    for i in range(hours_back, -1, -1):
        timestamp = now - timedelta(hours=i)
        dynamics.append(
            {
                "id": len(dynamics) + 1,
                "timestamp": timestamp.isoformat(),
                "views": random.randint(100, 1100),
                "reactions": random.randint(5, 55),
                "shares": random.randint(1, 21),
                "comments": random.randint(2, 32),
                "engagement_rate": round(random.uniform(2.0, 10.0), 2),
                "hour": timestamp.hour,
                "day_of_week": timestamp.weekday(),
                "performance_score": round(random.uniform(60.0, 100.0), 2),
            }
        )

    return dynamics


def generate_top_posts(count: int = DEMO_POSTS_COUNT) -> list[dict[str, Any]]:
    """
    Generate demo top posts data
    Consolidated from frontend demoAnalyticsService.js
    """
    posts = []
    post_titles = [
        "Breaking: Major Tech Innovation Announced",
        "Market Analysis: Q3 Performance Review",
        "Tutorial: Advanced Analytics Techniques",
        "Industry News: Partnership Deal Confirmed",
        "Expert Opinion: Future Technology Trends",
        "Product Launch: New Features Available",
        "Research: User Behavior Insights",
        "Update: Platform Security Enhancements",
    ]

    for i in range(count):
        base_views = random.randint(1000, 10000)
        posts.append(
            {
                "id": f"post_{i + 1}",
                "title": random.choice(post_titles),
                "views": base_views,
                "likes": int(base_views * random.uniform(0.05, 0.15)),
                "shares": int(base_views * random.uniform(0.01, 0.05)),
                "comments": int(base_views * random.uniform(0.02, 0.08)),
                "engagement_rate": round(random.uniform(3.0, 15.0), 2),
                "published_at": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "channel_id": f"{DEFAULT_DEMO_CHANNEL_ID}_{random.randint(1, 3)}",
                "performance_score": round(random.uniform(60.0, 100.0), 2),
                "trending": random.random() > 0.7,
            }
        )

    return sorted(posts, key=lambda x: x["views"], reverse=True)


def generate_best_time_recommendations() -> dict[str, Any]:
    """
    Generate demo best time posting recommendations
    Consolidated from frontend demoAnalyticsService.js
    """
    optimal_hours = [9, 12, 15, 18, 20]
    best_hour = random.choice(optimal_hours)

    return {
        "optimal_times": [
            {
                "hour": best_hour,
                "day": "weekday",
                "engagement_rate": DEFAULT_DEMO_ENGAGEMENT_RATE,
                "confidence": 0.85,
                "reason": f"Peak engagement observed at {best_hour}:00",
            },
            {
                "hour": best_hour + 2,
                "day": "weekend",
                "engagement_rate": DEFAULT_DEMO_ENGAGEMENT_RATE * 0.9,
                "confidence": 0.78,
                "reason": "Weekend audience preferences",
            },
        ],
        "recommendations": [
            "Post during lunch hours (12-13:00) for maximum reach",
            "Evening posts (18-20:00) show higher engagement",
            "Avoid early morning posts (6-8:00) due to low activity",
        ],
        "analysis_period": f"Last {DEMO_METRICS_DAYS} days",
        "data_points": random.randint(100, 500),
    }


def generate_engagement_metrics(period: str = "7d") -> dict[str, Any]:
    """
    Generate demo engagement metrics
    Consolidated from frontend demoAnalyticsService.js
    """
    days = {"1d": 1, "7d": 7, "30d": 30}.get(period, 7)

    return {
        "period": period,
        "total_views": random.randint(10000, 50000),
        "total_engagements": random.randint(1000, 5000),
        "average_engagement_rate": DEFAULT_DEMO_ENGAGEMENT_RATE,
        "growth_rate": round(random.uniform(-5.0, 15.0), 2),
        "top_performing_content": "video",
        "daily_breakdown": [
            {
                "date": (datetime.now() - timedelta(days=i)).date().isoformat(),
                "views": random.randint(1000, 3000),
                "engagements": random.randint(100, 400),
                "engagement_rate": round(random.uniform(5.0, 12.0), 2),
            }
            for i in range(days)
        ],
    }


def generate_ai_recommendations() -> list[dict[str, Any]]:
    """Generate AI-powered recommendations for analytics optimization"""
    return [
        {
            "type": "optimization",
            "title": "Post Timing Optimization",
            "description": "Your posts perform 23% better when published between 2-4 PM UTC",
            "priority": "high",
            "impact": "engagement",
        },
        {
            "type": "content",
            "title": "Content Format Recommendation",
            "description": "Videos with captions show 31% higher engagement than without",
            "priority": "medium",
            "impact": "reach",
        },
        {
            "type": "audience",
            "title": "Audience Growth Strategy",
            "description": "Focus on hashtag optimization to reach 15% more targeted users",
            "priority": "medium",
            "impact": "growth",
        },
    ]


def generate_best_time_recommendations() -> list[dict[str, Any]]:
    """Generate best time recommendations for posting"""
    return [
        {"time": "14:00", "day": "weekday", "engagement_score": 92, "confidence": 0.85},
        {"time": "19:00", "day": "weekend", "engagement_score": 88, "confidence": 0.82},
        {"time": "16:30", "day": "weekday", "engagement_score": 86, "confidence": 0.79},
        {"time": "21:00", "day": "weekend", "engagement_score": 84, "confidence": 0.76},
    ]


def generate_post_dynamics(period_hours: int = 24) -> dict[str, Any]:
    """Generate post dynamics data for the specified period"""
    base_time = datetime.utcnow() - timedelta(hours=period_hours)
    dynamics = []

    for i in range(min(period_hours, 24)):  # Limit to 24 data points max
        # Add some realistic patterns to the data
        hour_of_day = (base_time + timedelta(hours=i)).hour

        # Peak hours between 6-8 PM and 12-2 PM
        engagement_multiplier = 1.0
        if 18 <= hour_of_day <= 20:  # Evening peak
            engagement_multiplier = 1.5
        elif 12 <= hour_of_day <= 14:  # Lunch peak
            engagement_multiplier = 1.3
        elif 6 <= hour_of_day <= 8:  # Morning
            engagement_multiplier = 1.2
        elif 22 <= hour_of_day or hour_of_day <= 5:  # Late night/early morning
            engagement_multiplier = 0.6

        base_views = random.randint(50, 500)
        base_engagement = random.randint(5, 50)

        dynamics.append(
            {
                "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                "views": int(base_views * engagement_multiplier),
                "engagement": int(base_engagement * engagement_multiplier),
                "reactions": random.randint(1, int(25 * engagement_multiplier)),
            }
        )

    return {
        "period_hours": period_hours,
        "data": dynamics,
        "total_views": sum(d["views"] for d in dynamics),
        "total_engagement": sum(d["engagement"] for d in dynamics),
        "peak_hour": max(dynamics, key=lambda x: x["engagement"])["timestamp"],
    }


def generate_top_posts(limit: int = 10) -> list[dict[str, Any]]:
    """Generate top posts data"""
    post_types = ["text", "photo", "video", "document", "poll"]
    content_topics = [
        "AI and Machine Learning",
        "Digital Marketing Trends",
        "Business Growth Strategies",
        "Technology Updates",
        "Industry Analysis",
        "Product Announcements",
        "Market Insights",
        "Customer Success Stories",
        "Behind the Scenes",
        "Expert Interviews",
    ]

    posts = []
    for i in range(limit):
        post_type = random.choice(post_types)
        topic = random.choice(content_topics)

        # Generate realistic view counts based on post type
        if post_type == "video":
            views = random.randint(3000, 15000)
        elif post_type == "photo":
            views = random.randint(2000, 12000)
        elif post_type == "poll":
            views = random.randint(1500, 8000)
        else:  # text, document
            views = random.randint(1000, 10000)

        engagement = int(views * random.uniform(0.02, 0.08))  # 2-8% engagement rate

        posts.append(
            {
                "id": f"post_{i + 1}",
                "title": f"{topic} - Part {i + 1}",
                "content": f"Sample content about {topic.lower()}...",
                "views": views,
                "engagement": engagement,
                "reactions": int(engagement * 0.7),
                "shares": int(engagement * 0.2),
                "comments": int(engagement * 0.1),
                "date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
                "type": post_type,
                "engagement_rate": round(engagement / views * 100, 2),
            }
        )

    return sorted(posts, key=lambda x: x["views"], reverse=True)


def generate_channel_analytics_summary(channel_id: int, days: int = 30) -> dict[str, Any]:
    """Generate comprehensive analytics summary for a channel"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Generate realistic metrics based on channel activity
    base_views = random.randint(10000, 100000)
    base_subscribers = random.randint(1000, 50000)

    return {
        "channel_id": channel_id,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
        },
        "metrics": {
            "total_views": base_views,
            "total_subscribers": base_subscribers,
            "new_subscribers": random.randint(100, 1000),
            "total_posts": random.randint(20, 200),
            "average_engagement_rate": round(random.uniform(3.5, 8.2), 2),
            "total_reactions": random.randint(500, 5000),
            "total_shares": random.randint(100, 1000),
            "total_comments": random.randint(50, 500),
        },
        "growth": {
            "views_growth": round(random.uniform(-5.0, 25.0), 2),
            "subscribers_growth": round(random.uniform(0.0, 15.0), 2),
            "engagement_growth": round(random.uniform(-2.0, 12.0), 2),
        },
        "top_content_types": [
            {
                "type": "video",
                "count": random.randint(10, 50),
                "avg_engagement": round(random.uniform(5.0, 9.0), 2),
            },
            {
                "type": "photo",
                "count": random.randint(15, 60),
                "avg_engagement": round(random.uniform(4.0, 7.5), 2),
            },
            {
                "type": "text",
                "count": random.randint(20, 80),
                "avg_engagement": round(random.uniform(3.0, 6.0), 2),
            },
        ],
        "audience_insights": {
            "peak_activity_hours": [18, 19, 20],
            "most_active_days": ["tuesday", "wednesday", "thursday"],
            "top_locations": ["US", "UK", "DE", "FR", "IT"],
        },
    }


def generate_engagement_metrics(channel_id: int, days: int = 7) -> dict[str, Any]:
    """Generate detailed engagement metrics"""
    metrics = []
    base_date = datetime.utcnow() - timedelta(days=days)

    for i in range(days):
        date = base_date + timedelta(days=i)

        # Weekend vs weekday patterns
        is_weekend = date.weekday() >= 5
        multiplier = 0.8 if is_weekend else 1.0

        daily_metrics = {
            "date": date.strftime("%Y-%m-%d"),
            "views": int(random.randint(1000, 5000) * multiplier),
            "likes": int(random.randint(50, 400) * multiplier),
            "shares": int(random.randint(10, 100) * multiplier),
            "comments": int(random.randint(5, 50) * multiplier),
            "reactions": int(random.randint(60, 500) * multiplier),
        }

        # Calculate engagement rate
        total_engagement = (
            daily_metrics["likes"] + daily_metrics["shares"] + daily_metrics["comments"]
        )
        daily_metrics["engagement_rate"] = round(total_engagement / daily_metrics["views"] * 100, 2)

        metrics.append(daily_metrics)

    return {
        "channel_id": channel_id,
        "period_days": days,
        "daily_metrics": metrics,
        "totals": {
            "total_views": sum(m["views"] for m in metrics),
            "total_engagement": sum(m["likes"] + m["shares"] + m["comments"] for m in metrics),
            "average_engagement_rate": round(
                sum(m["engagement_rate"] for m in metrics) / len(metrics), 2
            ),
        },
    }


def generate_ai_insights(channel_id: int) -> dict[str, Any]:
    """Generate AI insights for a specific channel"""
    return {
        "channel_id": channel_id,
        "insights": [
            {
                "type": "engagement_pattern",
                "title": "Peak Engagement Hours",
                "description": "Your audience is most active between 6-8 PM",
                "confidence": 0.89,
                "actionable": True,
            },
            {
                "type": "content_performance",
                "title": "Video Content Success",
                "description": "Video posts show 45% higher engagement",
                "confidence": 0.92,
                "actionable": True,
            },
            {
                "type": "audience_growth",
                "title": "Optimal Posting Frequency",
                "description": "2-3 posts per day show optimal engagement rates",
                "confidence": 0.86,
                "actionable": True,
            },
        ],
        "generated_at": datetime.utcnow(),
        "insights_count": 3,
    }


def generate_prediction_result(
    model_type: str, features: list[float], parameters: dict[str, Any] = None
) -> dict[str, Any]:
    """Generate prediction results for ML models"""
    # Simulate different model accuracies based on type
    model_accuracies = {
        "engagement_forecast": 0.92,
        "growth_prediction": 0.88,
        "churn_prediction": 0.94,
        "content_performance": 0.87,
    }

    base_accuracy = model_accuracies.get(model_type, 0.85)

    return {
        "status": "predicted",
        "model_type": model_type,
        "features_count": len(features),
        "prediction": {
            "value": round(random.uniform(0.1, 1.0), 3),
            "confidence": round(random.uniform(0.7, 0.95), 3),
            "model_accuracy": base_accuracy,
        },
        "parameters": parameters or {},
        "timestamp": datetime.utcnow(),
        "model_version": "v2.1.0",
    }


def generate_data_analysis_result(
    data_source: str, processing_type: str, parameters: dict[str, Any] = None
) -> dict[str, Any]:
    """Generate data analysis results"""
    # Simulate different processing results based on type
    processing_results = {
        "engagement_analysis": {
            "records_processed": random.randint(5000, 50000),
            "quality_score": round(random.uniform(0.85, 0.98), 3),
            "anomalies_detected": random.randint(1, 15),
            "processing_time_ms": random.randint(150, 800),
        },
        "content_analysis": {
            "records_processed": random.randint(1000, 10000),
            "quality_score": round(random.uniform(0.90, 0.99), 3),
            "anomalies_detected": random.randint(0, 5),
            "processing_time_ms": random.randint(100, 500),
        },
        "user_behavior": {
            "records_processed": random.randint(10000, 100000),
            "quality_score": round(random.uniform(0.88, 0.96), 3),
            "anomalies_detected": random.randint(2, 20),
            "processing_time_ms": random.randint(300, 1200),
        },
    }

    result_data = processing_results.get(processing_type, processing_results["engagement_analysis"])

    return {
        "status": "processed",
        "data_source": data_source,
        "processing_type": processing_type,
        "parameters": parameters or {},
        "timestamp": datetime.utcnow(),
        "result_summary": result_data,
        "recommendations": [
            "Consider increasing content frequency during peak hours",
            "Focus on video content for better engagement",
            "Monitor anomalies for unusual activity patterns",
        ][: random.randint(1, 3)],
    }


# Export all mock functions for easy import
__all__ = [
    "generate_ai_recommendations",
    "generate_best_time_recommendations",
    "generate_post_dynamics",
    "generate_top_posts",
    "generate_channel_analytics_summary",
    "generate_engagement_metrics",
    "generate_ai_insights",
    "generate_prediction_result",
    "generate_data_analysis_result",
]
