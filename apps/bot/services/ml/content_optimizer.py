"""
📝 Content Optimizer - AI-powered content analysis and optimization

Features:
- NLP sentiment analysis
- Hashtag optimization suggestions
- Readability scoring
- Content performance prediction
- Real-time content scoring
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import emoji
import numpy as np
from textstat import flesch_reading_ease

logger = logging.getLogger(__name__)


@dataclass
class ContentAnalysis:
    """Comprehensive content analysis result"""

    overall_score: float  # 0-100
    sentiment_score: float  # -1 to 1
    readability_score: float  # 0-100
    seo_score: float  # 0-100
    engagement_score: float  # 0-100

    # Detailed metrics
    word_count: int
    character_count: int
    hashtag_count: int
    mention_count: int
    emoji_count: int
    url_count: int

    # Analysis insights
    sentiment_label: str
    readability_level: str
    key_topics: list[str]
    suggested_hashtags: list[str]
    optimization_tips: list[str]

    # Performance prediction
    predicted_engagement: float
    confidence: float
    timestamp: datetime


@dataclass
class HashtagSuggestion:
    """Hashtag suggestion with relevance scoring"""

    tag: str
    relevance_score: float
    popularity_score: float
    competition_level: str
    estimated_reach: int


class ContentOptimizer:
    """
    🚀 AI-powered content optimization service

    Capabilities:
    - Real-time content analysis
    - NLP sentiment detection
    - Hashtag optimization
    - Readability assessment
    - SEO scoring
    - Performance prediction
    """

    def __init__(self, cache_service=None, analytics_service=None):
        self.cache_service = cache_service
        self.analytics_service = analytics_service

        # Pre-computed sentiment words for fast analysis
        self.positive_words = {
            "amazing",
            "awesome",
            "brilliant",
            "excellent",
            "fantastic",
            "great",
            "incredible",
            "outstanding",
            "perfect",
            "wonderful",
            "best",
            "top",
            "super",
            "love",
            "beautiful",
            "stunning",
            "impressive",
            "remarkable",
            "exceptional",
            "magnificent",
        }

        self.negative_words = {
            "awful",
            "terrible",
            "horrible",
            "disgusting",
            "worst",
            "bad",
            "poor",
            "disappointing",
            "annoying",
            "frustrating",
            "boring",
            "stupid",
            "hate",
            "ugly",
            "pathetic",
            "useless",
            "failed",
            "wrong",
            "broken",
            "disaster",
        }

        # Popular hashtag categories with base scores
        self.hashtag_categories = {
            "general": ["viral", "trending", "popular", "new", "amazing"],
            "business": ["entrepreneur", "startup", "business", "marketing", "growth"],
            "tech": ["tech", "ai", "innovation", "digital", "future"],
            "lifestyle": ["lifestyle", "inspiration", "motivation", "success", "life"],
            "social": ["community", "social", "together", "share", "connect"],
        }

        # Content optimization weights
        self.score_weights = {
            "sentiment": 0.25,
            "readability": 0.20,
            "hashtags": 0.20,
            "length": 0.15,
            "engagement_factors": 0.20,
        }

    async def analyze_content(
        self,
        text: str,
        media_urls: list[str] | None = None,
        target_audience: str = "general",
    ) -> ContentAnalysis:
        """
        🎯 Comprehensive content analysis with optimization suggestions

        Args:
            text: Content text to analyze
            media_urls: List of media URLs (images/videos)
            target_audience: Target audience category

        Returns:
            Detailed content analysis with scores and recommendations
        """
        try:
            # Check cache first
            cache_key = f"content_analysis:{hash(text)}:{target_audience}"
            if self.cache_service:
                cached_result = await self.cache_service.get(cache_key)
                if cached_result:
                    return ContentAnalysis(**cached_result)

            # Extract basic metrics
            metrics = await self._extract_content_metrics(text, media_urls)

            # Perform sentiment analysis
            sentiment_score, sentiment_label = await self._analyze_sentiment(text)

            # Analyze readability
            readability_score, readability_level = await self._analyze_readability(text)

            # SEO analysis
            seo_score = await self._analyze_seo_factors(text, metrics)

            # Engagement prediction
            engagement_score, predicted_engagement, confidence = await self._predict_engagement(
                text, metrics, sentiment_score, target_audience
            )

            # Generate hashtag suggestions
            suggested_hashtags = await self._suggest_hashtags(text, target_audience)

            # Extract key topics
            key_topics = await self._extract_key_topics(text)

            # Generate optimization tips
            optimization_tips = await self._generate_optimization_tips(
                metrics, sentiment_score, readability_score, seo_score
            )

            # Calculate overall score
            overall_score = await self._calculate_overall_score(
                sentiment_score, readability_score, seo_score, engagement_score
            )

            analysis = ContentAnalysis(
                overall_score=overall_score,
                sentiment_score=sentiment_score,
                readability_score=readability_score,
                seo_score=seo_score,
                engagement_score=engagement_score,
                word_count=metrics["word_count"],
                character_count=metrics["character_count"],
                hashtag_count=metrics["hashtag_count"],
                mention_count=metrics["mention_count"],
                emoji_count=metrics["emoji_count"],
                url_count=metrics["url_count"],
                sentiment_label=sentiment_label,
                readability_level=readability_level,
                key_topics=key_topics,
                suggested_hashtags=suggested_hashtags,
                optimization_tips=optimization_tips,
                predicted_engagement=predicted_engagement,
                confidence=confidence,
                timestamp=datetime.now(),
            )

            # Cache result for 30 minutes
            if self.cache_service:
                await self.cache_service.set(cache_key, analysis.__dict__, ttl=1800)

            return analysis

        except Exception as e:
            logger.error(f"❌ Content analysis failed: {e}")
            # Return fallback analysis
            return await self._create_fallback_analysis(text)

    async def optimize_hashtags(
        self,
        text: str,
        current_hashtags: list[str],
        target_audience: str = "general",
        max_suggestions: int = 10,
    ) -> list[HashtagSuggestion]:
        """
        📱 Optimize hashtags for maximum reach and engagement

        Returns:
            List of hashtag suggestions with scoring
        """
        try:
            # Extract content topics
            topics = await self._extract_key_topics(text)

            # Analyze current hashtag performance
            await self._analyze_current_hashtags(current_hashtags)

            # Generate new hashtag suggestions
            suggestions = []

            # Topic-based hashtags
            for topic in topics[:3]:  # Top 3 topics
                topic_hashtags = await self._generate_topic_hashtags(topic, target_audience)
                suggestions.extend(topic_hashtags)

            # Trending hashtags for audience
            trending = await self._get_trending_hashtags(target_audience)
            suggestions.extend(trending)

            # Category-specific hashtags
            category_hashtags = await self._get_category_hashtags(target_audience)
            suggestions.extend(category_hashtags)

            # Remove duplicates and current hashtags
            suggestions = [s for s in suggestions if s.tag not in current_hashtags]
            suggestions = list({s.tag: s for s in suggestions}.values())

            # Sort by combined score and limit
            suggestions.sort(key=lambda x: x.relevance_score * x.popularity_score, reverse=True)

            return suggestions[:max_suggestions]

        except Exception as e:
            logger.error(f"❌ Hashtag optimization failed: {e}")
            return []

    async def score_content_realtime(self, text: str) -> dict[str, float]:
        """
        ⚡ Real-time content scoring for live editing feedback

        Returns:
            Real-time scores for immediate feedback
        """
        try:
            # Fast analysis for real-time feedback
            scores = {}

            # Basic metrics
            word_count = len(text.split())
            len(text)

            # Length score (optimal 50-300 words)
            if 50 <= word_count <= 300:
                scores["length_score"] = 1.0
            elif word_count < 50:
                scores["length_score"] = word_count / 50.0
            else:
                scores["length_score"] = max(0.5, 1.0 - (word_count - 300) / 200.0)

            # Hashtag score (optimal 3-7 hashtags)
            hashtag_count = len(re.findall(r"#\w+", text))
            if 3 <= hashtag_count <= 7:
                scores["hashtag_score"] = 1.0
            elif hashtag_count < 3:
                scores["hashtag_score"] = hashtag_count / 3.0
            else:
                scores["hashtag_score"] = max(0.3, 1.0 - (hashtag_count - 7) / 5.0)

            # Quick sentiment score
            positive_count = sum(1 for word in text.lower().split() if word in self.positive_words)
            negative_count = sum(1 for word in text.lower().split() if word in self.negative_words)

            if positive_count + negative_count > 0:
                sentiment_ratio = positive_count / (positive_count + negative_count)
            else:
                sentiment_ratio = 0.5

            scores["sentiment_score"] = sentiment_ratio

            # Emoji score (1-3 emojis optimal)
            emoji_count = len(emoji.emoji_list(text))
            if 1 <= emoji_count <= 3:
                scores["emoji_score"] = 1.0
            elif emoji_count == 0:
                scores["emoji_score"] = 0.7
            else:
                scores["emoji_score"] = max(0.4, 1.0 - (emoji_count - 3) / 3.0)

            # Overall real-time score
            scores["overall_score"] = np.mean(list(scores.values()))

            return scores

        except Exception as e:
            logger.error(f"❌ Real-time scoring failed: {e}")
            return {"overall_score": 0.5}

    # ============ PRIVATE HELPER METHODS ============

    async def _extract_content_metrics(
        self, text: str, media_urls: list[str] | None = None
    ) -> dict[str, Any]:
        """Extract basic content metrics"""
        return {
            "word_count": len(text.split()),
            "character_count": len(text),
            "hashtag_count": len(re.findall(r"#\w+", text)),
            "mention_count": len(re.findall(r"@\w+", text)),
            "emoji_count": len(emoji.emoji_list(text)),
            "url_count": len(
                re.findall(
                    r"https?://(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(?:/[^\s<>\"']*)?",
                    text,
                )
            ),
            "media_count": len(media_urls) if media_urls else 0,
            "line_count": len(text.split("\n")),
            "avg_word_length": (
                np.mean([len(word) for word in text.split()]) if text.split() else 0
            ),
        }

    async def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Fast sentiment analysis using word-based approach"""
        words = text.lower().split()

        positive_score = sum(1 for word in words if word in self.positive_words)
        negative_score = sum(1 for word in words if word in self.negative_words)

        total_words = len(words)
        if total_words == 0:
            return 0.0, "neutral"

        # Calculate sentiment score (-1 to 1)
        sentiment_score = (positive_score - negative_score) / total_words

        # Normalize to -1 to 1 range
        sentiment_score = max(-1, min(1, sentiment_score * 5))

        # Determine label
        if sentiment_score > 0.1:
            label = "positive"
        elif sentiment_score < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return float(sentiment_score), label

    async def _analyze_readability(self, text: str) -> tuple[float, str]:
        """Analyze text readability"""
        try:
            if len(text.split()) < 3:
                return 70.0, "simple"

            # Use Flesch Reading Ease score
            flesch_score = flesch_reading_ease(text)

            # Convert to 0-100 scale where higher is better
            readability_score = max(0, min(100, flesch_score))

            # Determine level
            if flesch_score >= 90:
                level = "very_easy"
            elif flesch_score >= 80:
                level = "easy"
            elif flesch_score >= 70:
                level = "fairly_easy"
            elif flesch_score >= 60:
                level = "standard"
            elif flesch_score >= 50:
                level = "fairly_difficult"
            elif flesch_score >= 30:
                level = "difficult"
            else:
                level = "very_difficult"

            return float(readability_score), level

        except Exception as e:
            logger.warning(f"Readability analysis failed: {e}")
            return 70.0, "standard"

    async def _analyze_seo_factors(self, text: str, metrics: dict[str, Any]) -> float:
        """Analyze SEO optimization factors"""
        score = 0.0
        factors = 0

        # Hashtag presence (20%)
        if metrics["hashtag_count"] > 0:
            score += 20
        factors += 20

        # Optimal hashtag count (15%)
        if 3 <= metrics["hashtag_count"] <= 7:
            score += 15
        elif metrics["hashtag_count"] > 0:
            score += 8
        factors += 15

        # Content length (15%)
        if 50 <= metrics["word_count"] <= 300:
            score += 15
        elif metrics["word_count"] >= 20:
            score += 10
        factors += 15

        # Visual content (15%)
        if metrics["media_count"] > 0:
            score += 15
        factors += 15

        # Engagement elements (10%)
        if metrics["emoji_count"] > 0:
            score += 5
        if "?" in text or "!" in text:  # Questions/exclamations
            score += 5
        factors += 10

        # Mentions (10%)
        if metrics["mention_count"] > 0:
            score += 10
        factors += 10

        # URL presence (10%)
        if metrics["url_count"] > 0:
            score += 10
        factors += 10

        # Call-to-action detection (5%)
        cta_words = [
            "follow",
            "like",
            "share",
            "comment",
            "subscribe",
            "click",
            "visit",
        ]
        if any(word in text.lower() for word in cta_words):
            score += 5
        factors += 5

        return min(100.0, (score / factors) * 100) if factors > 0 else 0.0

    async def _predict_engagement(
        self,
        text: str,
        metrics: dict[str, Any],
        sentiment_score: float,
        target_audience: str,
    ) -> tuple[float, float, float]:
        """Predict content engagement performance"""

        # Base engagement score calculation
        engagement_score = 50.0  # Base score

        # Sentiment impact (positive sentiment boosts engagement)
        if sentiment_score > 0:
            engagement_score += sentiment_score * 20

        # Length impact (optimal length gets bonus)
        word_count = metrics["word_count"]
        if 50 <= word_count <= 200:
            engagement_score += 15
        elif 20 <= word_count <= 300:
            engagement_score += 10

        # Visual content boost
        if metrics["media_count"] > 0:
            engagement_score += 15

        # Hashtag impact
        hashtag_count = metrics["hashtag_count"]
        if 3 <= hashtag_count <= 7:
            engagement_score += 10
        elif hashtag_count > 0:
            engagement_score += 5

        # Emoji impact
        if 1 <= metrics["emoji_count"] <= 3:
            engagement_score += 8

        # Interactive elements
        if "?" in text:  # Questions encourage comments
            engagement_score += 5

        # Audience-specific adjustments
        if target_audience == "business":
            if any(word in text.lower() for word in ["growth", "strategy", "success"]):
                engagement_score += 5
        elif target_audience == "lifestyle":
            if any(word in text.lower() for word in ["inspiration", "motivation", "life"]):
                engagement_score += 5

        # Normalize to 0-100
        engagement_score = max(0, min(100, engagement_score))

        # Predicted numerical engagement (simplified)
        base_engagement = 100  # Base views
        multiplier = engagement_score / 50.0  # Score-based multiplier
        predicted_engagement = base_engagement * multiplier

        # Confidence based on content completeness
        confidence = min(0.9, 0.3 + (engagement_score / 100) * 0.6)

        return float(engagement_score), float(predicted_engagement), float(confidence)

    async def _suggest_hashtags(self, text: str, target_audience: str) -> list[str]:
        """Generate relevant hashtag suggestions"""
        suggestions = []

        # Extract key topics for topic-based hashtags
        key_topics = await self._extract_key_topics(text)

        # Add topic-based hashtags
        for topic in key_topics[:2]:  # Top 2 topics
            topic_tags = [f"#{topic.lower()}", f"#{topic.lower()}content"]
            suggestions.extend(topic_tags)

        # Add audience-specific hashtags
        audience_hashtags = self.hashtag_categories.get(target_audience, [])
        suggestions.extend([f"#{tag}" for tag in audience_hashtags[:3]])

        # Add general engagement hashtags
        general_tags = ["#viral", "#trending", "#new"]
        suggestions.extend(general_tags)

        # Remove duplicates and limit
        suggestions = list(set(suggestions))
        return suggestions[:8]

    async def _extract_key_topics(self, text: str) -> list[str]:
        """Extract key topics from content"""
        # Simple keyword extraction (in production, use NLP libraries)
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out common words
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
        }

        # Get content words (length > 3, not stopwords)
        content_words = [word for word in words if len(word) > 3 and word not in stopwords]

        # Get most frequent words as topics
        word_freq = {}
        for word in content_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Return top topics
        topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [topic[0] for topic in topics[:5]]

    async def _generate_optimization_tips(
        self,
        metrics: dict[str, Any],
        sentiment_score: float,
        readability_score: float,
        seo_score: float,
    ) -> list[str]:
        """Generate actionable optimization recommendations"""
        tips = []

        # Content length optimization
        word_count = metrics["word_count"]
        if word_count < 20:
            tips.append("📝 Add more content - aim for 50-200 words for optimal engagement")
        elif word_count > 300:
            tips.append("✂️ Consider shortening content - posts under 200 words perform better")

        # Hashtag optimization
        hashtag_count = metrics["hashtag_count"]
        if hashtag_count == 0:
            tips.append("📱 Add 3-5 relevant hashtags to increase discoverability")
        elif hashtag_count < 3:
            tips.append(f"📱 Add {3 - hashtag_count} more hashtags (currently {hashtag_count})")
        elif hashtag_count > 10:
            tips.append(
                f"⚠️ Reduce hashtags to 5-7 for better performance (currently {hashtag_count})"
            )

        # Sentiment optimization
        if sentiment_score < -0.2:
            tips.append("😊 Consider more positive language to boost engagement")
        elif sentiment_score > 0.8:
            tips.append("⚡ Great positive tone - this should perform well!")

        # Visual content
        if metrics["media_count"] == 0:
            tips.append("🖼️ Add images or videos to increase engagement by 50-80%")

        # Engagement elements
        if metrics["emoji_count"] == 0:
            tips.append("😀 Add 1-2 relevant emojis to make content more engaging")
        elif metrics["emoji_count"] > 5:
            tips.append("⚠️ Reduce emoji usage - 1-3 emojis work best")

        # Readability
        if readability_score < 50:
            tips.append("📖 Simplify language for better readability")

        # Call to action
        cta_words = ["follow", "like", "share", "comment", "subscribe"]
        has_cta = any(word in metrics.get("text", "").lower() for word in cta_words)
        if not has_cta:
            tips.append("💬 Add a call-to-action (like, share, comment) to boost engagement")

        if not tips:
            tips.append("✨ Content is well-optimized - ready to publish!")

        return tips

    async def _calculate_overall_score(
        self,
        sentiment_score: float,
        readability_score: float,
        seo_score: float,
        engagement_score: float,
    ) -> float:
        """Calculate weighted overall content score"""

        # Normalize sentiment score to 0-100
        sentiment_normalized = ((sentiment_score + 1) / 2) * 100

        # Apply weights
        weighted_score = (
            sentiment_normalized * self.score_weights["sentiment"]
            + readability_score * self.score_weights["readability"]
            + seo_score * self.score_weights["hashtags"]
            + engagement_score * self.score_weights["engagement_factors"]
        )

        return min(100.0, max(0.0, weighted_score))

    async def _create_fallback_analysis(self, text: str) -> ContentAnalysis:
        """Create fallback analysis when main analysis fails"""
        metrics = await self._extract_content_metrics(text)

        return ContentAnalysis(
            overall_score=70.0,
            sentiment_score=0.0,
            readability_score=70.0,
            seo_score=60.0,
            engagement_score=65.0,
            word_count=metrics["word_count"],
            character_count=metrics["character_count"],
            hashtag_count=metrics["hashtag_count"],
            mention_count=metrics["mention_count"],
            emoji_count=metrics["emoji_count"],
            url_count=metrics["url_count"],
            sentiment_label="neutral",
            readability_level="standard",
            key_topics=["general"],
            suggested_hashtags=["#content", "#post", "#social"],
            optimization_tips=["Analysis unavailable - using fallback recommendations"],
            predicted_engagement=100.0,
            confidence=0.3,
            timestamp=datetime.now(),
        )

    async def health_check(self) -> dict[str, Any]:
        """🏥 Health check for content optimizer"""
        return {
            "status": "healthy",
            "positive_words_loaded": len(self.positive_words),
            "negative_words_loaded": len(self.negative_words),
            "hashtag_categories": len(self.hashtag_categories),
            "cache_available": self.cache_service is not None,
            "timestamp": datetime.now().isoformat(),
        }
