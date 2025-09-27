"""
Mock AI Service Implementation
Protocol-compliant AI service for demo mode
"""

import asyncio
import random
from typing import Any

from apps.api.__mocks__.constants import DEMO_API_DELAY_MS

from core.protocols import AIServiceProtocol


class MockAIService(AIServiceProtocol):
    """Mock AI service for demo mode"""

    def __init__(self):
        self.content_topics = [
            "Technology trends",
            "Social media marketing",
            "Business growth",
            "Digital transformation",
            "AI and automation",
            "Cryptocurrency",
            "Health and wellness",
            "Education",
            "Entertainment",
            "News",
        ]

        self.hashtag_pools = {
            "technology": [
                "#tech",
                "#innovation",
                "#AI",
                "#digitaltransformation",
                "#startup",
            ],
            "business": [
                "#business",
                "#entrepreneur",
                "#success",
                "#growth",
                "#marketing",
            ],
            "social": [
                "#socialmedia",
                "#content",
                "#engagement",
                "#community",
                "#viral",
            ],
            "general": ["#trending", "#amazing", "#awesome", "#must_see", "#daily"],
        }

    def get_service_name(self) -> str:
        return "mock_ai_service"

    async def health_check(self) -> dict[str, Any]:
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "service": "ai",
            "status": "healthy",
            "demo_mode": True,
            "ai_models_loaded": [
                "content_generator",
                "engagement_predictor",
                "hashtag_optimizer",
            ],
        }

    async def generate_content_suggestions(self, channel_id: str, topic: str) -> list[str]:
        """Generate content suggestions"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        base_suggestions = [
            f"Exploring the latest in {topic}: What you need to know",
            f"5 key insights about {topic} that will surprise you",
            f"Why {topic} is trending and how it affects your business",
            f"The future of {topic}: Expert predictions for 2024",
            f"Behind the scenes: How {topic} is changing industries",
            f"Quick tips to get started with {topic} today",
            f"Common mistakes people make with {topic}",
            f"Success stories: How {topic} transformed these companies",
        ]

        return random.sample(base_suggestions, random.randint(3, 6))

    async def analyze_content_performance(self, content: str) -> dict[str, Any]:
        """Analyze content for performance prediction"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        # Mock content analysis based on length and keywords
        word_count = len(content.split())
        has_question = "?" in content
        has_emoji = any(ord(char) > 127 for char in content)
        has_hashtags = "#" in content

        # Calculate mock engagement score
        base_score = random.uniform(60, 85)
        if has_question:
            base_score += 5
        if has_emoji:
            base_score += 3
        if has_hashtags:
            base_score += 4
        if 50 <= word_count <= 150:
            base_score += 7

        engagement_score = min(100, base_score)

        return {
            "engagement_score": round(engagement_score, 1),
            "predicted_reach": random.randint(500, 5000),
            "predicted_likes": random.randint(50, 500),
            "predicted_comments": random.randint(5, 50),
            "predicted_shares": random.randint(2, 20),
            "content_analysis": {
                "word_count": word_count,
                "has_question": has_question,
                "has_emoji": has_emoji,
                "has_hashtags": has_hashtags,
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "readability": random.choice(["easy", "medium", "hard"]),
            },
            "recommendations": [
                "Add engaging questions to boost interaction",
                "Use 2-3 relevant hashtags for better discovery",
                "Consider adding emojis for visual appeal",
                "Post during peak hours (7-9 PM)",
            ][: random.randint(2, 4)],
            "demo_mode": True,
        }

    async def get_optimal_hashtags(self, content: str) -> list[str]:
        """Get optimal hashtags for content"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        # Simple keyword matching for demo
        content_lower = content.lower()
        relevant_hashtags = []

        if any(word in content_lower for word in ["tech", "ai", "digital", "innovation"]):
            relevant_hashtags.extend(self.hashtag_pools["technology"])

        if any(word in content_lower for word in ["business", "marketing", "growth", "success"]):
            relevant_hashtags.extend(self.hashtag_pools["business"])

        if any(word in content_lower for word in ["social", "content", "engagement", "viral"]):
            relevant_hashtags.extend(self.hashtag_pools["social"])

        # Always add some general hashtags
        relevant_hashtags.extend(self.hashtag_pools["general"])

        # Remove duplicates and return random selection
        unique_hashtags = list(set(relevant_hashtags))
        return random.sample(unique_hashtags, min(len(unique_hashtags), random.randint(3, 7)))

    async def predict_engagement(self, content: str, posting_time: str) -> dict[str, Any]:
        """Predict engagement for content"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)

        # Mock prediction based on content and timing
        content_analysis = await self.analyze_content_performance(content)
        base_engagement = content_analysis["engagement_score"]

        # Time-based adjustments (mock)
        hour = int(posting_time.split(":")[0]) if ":" in posting_time else 12
        if 7 <= hour <= 9 or 19 <= hour <= 21:  # Peak hours
            time_multiplier = 1.2
        elif 22 <= hour <= 6:  # Low activity hours
            time_multiplier = 0.7
        else:
            time_multiplier = 1.0

        adjusted_engagement = base_engagement * time_multiplier

        return {
            "predicted_engagement_rate": round(adjusted_engagement, 1),
            "optimal_posting_time": random.choice(["19:00", "20:00", "21:00", "08:00", "09:00"]),
            "expected_metrics": {
                "views": int(content_analysis["predicted_reach"] * time_multiplier),
                "likes": int(content_analysis["predicted_likes"] * time_multiplier),
                "comments": int(content_analysis["predicted_comments"] * time_multiplier),
                "shares": int(content_analysis["predicted_shares"] * time_multiplier),
            },
            "confidence": round(random.uniform(70, 95), 1),
            "factors": {
                "content_quality": content_analysis["engagement_score"],
                "posting_time_factor": round(time_multiplier, 2),
                "audience_activity": random.choice(["high", "medium", "low"]),
            },
            "demo_mode": True,
        }
