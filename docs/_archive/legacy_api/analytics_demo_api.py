#!/usr/bin/env python3
"""
PHASE 2.1 Week 2 - Analytics API Demo Server
Simple FastAPI server for testing analytics components
"""

import random
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# Pydantic models
class PostDynamic(BaseModel):
    timestamp: datetime
    views: int
    likes: int
    shares: int
    comments: int


class TopPost(BaseModel):
    id: str
    title: str
    content: str
    views: int
    likes: int
    shares: int
    comments: int
    created_at: datetime
    type: str = "text"
    thumbnail: str | None = None


class BestTimeRecommendation(BaseModel):
    day: int
    hour: int
    confidence: float
    avg_engagement: int


class AIRecommendation(BaseModel):
    type: str
    title: str
    description: str
    confidence: float


# FastAPI app
app = FastAPI(
    title="Analytics API Demo",
    description="Phase 2.1 Week 2 - Analytics Dashboard Demo API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo uchun
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mock data generators
def generate_post_dynamics(hours_back: int = 24) -> list[PostDynamic]:
    """Generate mock post dynamics data"""
    data = []
    base_views = random.randint(1000, 5000)

    for i in range(hours_back):
        timestamp = datetime.now() - timedelta(hours=hours_back - i)

        # Simulate realistic engagement patterns
        hour = timestamp.hour
        day_factor = 1.2 if 9 <= hour <= 21 else 0.8  # More active during day
        weekend_factor = 1.3 if timestamp.weekday() in [5, 6] else 1.0

        views = int(base_views * day_factor * weekend_factor * random.uniform(0.7, 1.3))
        likes = int(views * random.uniform(0.02, 0.08))
        shares = int(views * random.uniform(0.005, 0.02))
        comments = int(views * random.uniform(0.001, 0.01))

        data.append(
            PostDynamic(
                timestamp=timestamp,
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
            )
        )

    return data


def generate_top_posts(count: int = 10) -> list[TopPost]:
    """Generate mock top posts data"""
    posts = []
    post_types = ["text", "photo", "video", "poll"]
    titles = [
        "Yangi mahsulot e'loni",
        "Savol-javob sessiyasi",
        "Haftalik yangliklar",
        "Konkurs e'loni",
        "Foydali maslahatlar",
        "Video dars",
        "Rasmiy bayonot",
        "Community yangiliklari",
        "Texnik yangilanish",
        "Maxsus taklif",
    ]

    for i in range(count):
        views = random.randint(500, 50000)
        likes = int(views * random.uniform(0.02, 0.12))
        shares = int(views * random.uniform(0.005, 0.03))
        comments = int(views * random.uniform(0.001, 0.02))

        posts.append(
            TopPost(
                id=f"post_{i + 1}",
                title=random.choice(titles),
                content=f"Post content for {titles[i % len(titles)]}...",
                views=views,
                likes=likes,
                shares=shares,
                comments=comments,
                created_at=datetime.now() - timedelta(hours=random.randint(1, 168)),
                type=random.choice(post_types),
                thumbnail=(
                    f"https://picsum.photos/64/64?random={i}"
                    if random.choice([True, False])
                    else None
                ),
            )
        )

    # Sort by views descending
    return sorted(posts, key=lambda x: x.views, reverse=True)


def generate_best_times() -> list[BestTimeRecommendation]:
    """Generate mock best posting times"""
    recommendations = []

    # Generate best times for different days/hours
    best_combinations = [
        (1, 14, 85.5),  # Tuesday 2 PM
        (4, 19, 82.3),  # Friday 7 PM
        (0, 12, 79.8),  # Monday noon
        (3, 16, 77.2),  # Thursday 4 PM
        (6, 10, 74.9),  # Sunday 10 AM
    ]

    for day, hour, confidence in best_combinations:
        recommendations.append(
            BestTimeRecommendation(
                day=day,
                hour=hour,
                confidence=confidence,
                avg_engagement=random.randint(150, 400),
            )
        )

    return recommendations


def generate_ai_recommendations() -> list[AIRecommendation]:
    """Generate mock AI recommendations"""
    recommendations = [
        AIRecommendation(
            type="time",
            title="Optimal posting time",
            description="Seshanba kuni soat 14:00 da post qo'ying, faollik 35% yuqori",
            confidence=85.5,
        ),
        AIRecommendation(
            type="content",
            title="Content suggestion",
            description="Video kontentlar 2.3x ko'proq engagement olmoqda",
            confidence=78.9,
        ),
        AIRecommendation(
            type="audience",
            title="Audience insight",
            description="Auditoriya kechqurun faolroq, 19:00-21:00 optimal",
            confidence=82.1,
        ),
        AIRecommendation(
            type="trend",
            title="Trending topic",
            description="'Tutorial' mavzusidagi postlar 45% ko'proq views olmoqda",
            confidence=71.3,
        ),
    ]
    return recommendations


# API Endpoints


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Analytics API Demo - Phase 2.1 Week 2",
        "status": "running",
        "endpoints": {
            "post_dynamics": "/api/analytics/post-dynamics",
            "top_posts": "/api/analytics/top-posts",
            "best_time": "/api/analytics/best-posting-time",
            "engagement": "/api/analytics/engagement",
        },
    }


@app.get("/api/analytics/post-dynamics")
async def get_post_dynamics(period: str = "24h"):
    """Get post view dynamics data"""
    try:
        # Parse period
        hours_map = {"1h": 1, "6h": 6, "24h": 24, "7d": 24 * 7, "30d": 24 * 30}
        hours = hours_map.get(period, 24)

        data = generate_post_dynamics(min(hours, 168))  # Max 1 week for demo

        return {
            "success": True,
            "period": period,
            "data_points": len(data),
            "data": [item.dict() for item in data],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/top-posts")
async def get_top_posts(period: str = "today", sort: str = "views"):
    """Get top performing posts"""
    try:
        posts = generate_top_posts(20)

        # Apply sorting
        if sort == "likes":
            posts = sorted(posts, key=lambda x: x.likes, reverse=True)
        elif sort == "engagement":
            posts = sorted(posts, key=lambda x: (x.likes + x.shares + x.comments), reverse=True)
        elif sort == "date":
            posts = sorted(posts, key=lambda x: x.created_at, reverse=True)
        # Default is views (already sorted)

        return {
            "success": True,
            "period": period,
            "sort_by": sort,
            "total": len(posts),
            "posts": [post.dict() for post in posts[:15]],  # Return top 15
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/best-posting-time")
async def get_best_posting_time(timeframe: str = "week", content_type: str = "all"):
    """Get AI-powered best posting time recommendations"""
    try:
        best_times = generate_best_times()
        ai_recommendations = generate_ai_recommendations()

        # Generate hourly performance data
        hourly_performance = {}
        for hour in range(24):
            # Simulate engagement levels throughout the day
            if 9 <= hour <= 12:  # Morning peak
                performance = random.randint(300, 500)
            elif 14 <= hour <= 16:  # Afternoon peak
                performance = random.randint(400, 600)
            elif 19 <= hour <= 21:  # Evening peak
                performance = random.randint(350, 550)
            else:  # Off-peak hours
                performance = random.randint(100, 300)

            hourly_performance[hour] = performance

        # Weekly summary
        weekly_summary = {}
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for i, day in enumerate(days):
            weekly_summary[day] = {
                "best_hour": random.randint(9, 21),
                "performance": random.randint(45, 90),
            }

        return {
            "success": True,
            "timeframe": timeframe,
            "content_type": content_type,
            "best_times": [time.dict() for time in best_times],
            "ai_recommendations": [rec.dict() for rec in ai_recommendations],
            "hourly_performance": hourly_performance,
            "weekly_summary": weekly_summary,
            "accuracy": random.randint(75, 90),
            "generated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/engagement")
async def get_engagement_metrics(period: str = "7d"):
    """Get engagement analytics"""
    try:
        # Generate mock engagement data
        total_views = random.randint(10000, 100000)
        total_likes = int(total_views * 0.05)
        total_shares = int(total_views * 0.01)
        total_comments = int(total_views * 0.005)

        engagement_rate = ((total_likes + total_shares + total_comments) / total_views) * 100

        return {
            "success": True,
            "period": period,
            "metrics": {
                "total_views": total_views,
                "total_likes": total_likes,
                "total_shares": total_shares,
                "total_comments": total_comments,
                "engagement_rate": round(engagement_rate, 2),
                "avg_views_per_post": random.randint(500, 2000),
                "growth_rate": round(random.uniform(-10, 25), 2),
            },
            "trends": {
                "views_trend": "up" if random.choice([True, False]) else "down",
                "engagement_trend": "up" if random.choice([True, False]) else "stable",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("🚀 Starting Analytics API Demo Server...")
    print("📊 Analytics Dashboard: http://localhost:3000")
    print("🔗 API Documentation: http://localhost:8001/docs")
    print("🎯 Phase 2.1 Week 2 - Rich Analytics & AI Recommendations")

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True, access_log=True)
