"""
🎯 Standalone Content Optimizer - Independent content analysis service

This service provides content analysis without external dependencies.
Designed for standalone API usage.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class StandaloneContentAnalysis:
    """Content analysis result for standalone usage"""
    overall_score: float
    sentiment_score: float
    sentiment_label: str
    readability_score: float
    word_count: int
    hashtag_count: int
    emoji_count: int
    optimization_tips: List[str]
    suggested_hashtags: List[str]
    performance_indicators: Dict[str, float]

class StandaloneContentOptimizer:
    """
    🎯 Standalone Content Optimizer
    
    Features:
    - Basic sentiment analysis
    - Readability scoring
    - Hashtag optimization
    - Performance prediction
    - Real-time scoring
    """
    
    def __init__(self):
        self.logger = logger
        
        # Sentiment keywords
        self.positive_words = {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'love', 'best',
            'wonderful', 'perfect', 'brilliant', 'outstanding', 'incredible', 'superb',
            'exciting', 'thrilled', 'happy', 'delighted', 'pleased', 'satisfied',
            'success', 'achievement', 'victory', 'win', 'breakthrough', 'innovative'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate', 'disgusting',
            'disappointing', 'frustrating', 'annoying', 'useless', 'pathetic',
            'disaster', 'failure', 'problem', 'issue', 'error', 'bug', 'broken',
            'difficult', 'hard', 'struggle', 'pain', 'stress', 'worry'
        }
        
        # Popular hashtags by category
        self.hashtag_suggestions = {
            'general': ['#viral', '#trending', '#popular', '#content', '#social', '#digital'],
            'tech': ['#AI', '#ML', '#technology', '#innovation', '#digital', '#future', '#tech'],
            'business': ['#business', '#entrepreneur', '#success', '#growth', '#marketing', '#strategy'],
            'lifestyle': ['#lifestyle', '#daily', '#motivation', '#inspiration', '#life', '#wellness'],
            'social': ['#community', '#network', '#connection', '#share', '#engage', '#together']
        }
    
    async def analyze_content(self, text: str, target_audience: str = "general") -> StandaloneContentAnalysis:
        """
        🔍 Comprehensive content analysis
        
        Args:
            text: Content to analyze
            target_audience: Target audience type
        
        Returns:
            Complete content analysis with scoring and recommendations
        """
        try:
            # Basic text metrics
            word_count = len(text.split())
            hashtag_count = len(re.findall(r'#\w+', text))
            emoji_count = len(re.findall(r'[😀-🿿]|[🎀-🏿]|[🐀-🟿]', text))
            
            # Sentiment analysis
            sentiment_score, sentiment_label = self._analyze_sentiment(text)
            
            # Readability score (simplified)
            readability_score = self._calculate_readability(text)
            
            # Overall score calculation
            overall_score = self._calculate_overall_score(
                word_count, hashtag_count, emoji_count, 
                sentiment_score, readability_score
            )
            
            # Generate optimization tips
            optimization_tips = self._generate_optimization_tips(
                word_count, hashtag_count, emoji_count, 
                sentiment_score, readability_score
            )
            
            # Suggest hashtags
            suggested_hashtags = self._suggest_hashtags(text, target_audience)
            
            # Performance indicators
            performance_indicators = {
                'engagement_potential': min(overall_score * 1.2, 1.0),
                'readability_factor': readability_score / 100,
                'sentiment_impact': abs(sentiment_score),
                'hashtag_effectiveness': min(hashtag_count / 5, 1.0),
                'length_optimization': self._score_content_length(word_count)
            }
            
            return StandaloneContentAnalysis(
                overall_score=overall_score,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                readability_score=readability_score,
                word_count=word_count,
                hashtag_count=hashtag_count,
                emoji_count=emoji_count,
                optimization_tips=optimization_tips,
                suggested_hashtags=suggested_hashtags,
                performance_indicators=performance_indicators
            )
            
        except Exception as e:
            self.logger.error(f"❌ Content analysis failed: {e}")
            # Return default analysis on error
            return StandaloneContentAnalysis(
                overall_score=0.5,
                sentiment_score=0.0,
                sentiment_label="neutral",
                readability_score=50.0,
                word_count=len(text.split()),
                hashtag_count=0,
                emoji_count=0,
                optimization_tips=["Content analysis temporarily unavailable"],
                suggested_hashtags=["#content"],
                performance_indicators={'default': 0.5}
            )
    
    async def score_content_realtime(self, text: str) -> Dict[str, float]:
        """
        ⚡ Real-time content scoring for live editing
        
        Args:
            text: Content to score in real-time
        
        Returns:
            Dictionary with real-time scores
        """
        try:
            word_count = len(text.split())
            hashtag_count = len(re.findall(r'#\w+', text))
            emoji_count = len(re.findall(r'[😀-🿿]|[🎀-🏿]|[🐀-🟿]', text))
            
            # Quick scoring
            length_score = self._score_content_length(word_count)
            hashtag_score = min(hashtag_count / 3, 1.0)  # Optimal 3 hashtags
            sentiment_score, _ = self._analyze_sentiment(text)
            emoji_score = min(emoji_count / 2, 1.0)  # Optimal 1-2 emojis
            
            # Overall score
            overall_score = (
                length_score * 0.3 +
                hashtag_score * 0.25 +
                abs(sentiment_score) * 0.25 +
                emoji_score * 0.2
            )
            
            return {
                'overall_score': overall_score,
                'length_score': length_score,
                'hashtag_score': hashtag_score,
                'sentiment_score': sentiment_score,
                'emoji_score': emoji_score
            }
            
        except Exception as e:
            self.logger.error(f"❌ Real-time scoring failed: {e}")
            return {
                'overall_score': 0.5,
                'length_score': 0.5,
                'hashtag_score': 0.5,
                'sentiment_score': 0.0,
                'emoji_score': 0.5
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """🏥 Health check for standalone content optimizer"""
        try:
            # Test basic functionality
            test_text = "This is a test message #test 🎯"
            analysis = await self.analyze_content(test_text)
            
            return {
                'status': 'healthy',
                'features': {
                    'sentiment_analysis': True,
                    'readability_scoring': True,
                    'hashtag_optimization': True,
                    'real_time_scoring': True
                },
                'test_analysis_score': analysis.overall_score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """Simple sentiment analysis"""
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0, "neutral"
        
        sentiment_score = (positive_count - negative_count) / len(words)
        
        if sentiment_score > 0.1:
            sentiment_label = "positive"
        elif sentiment_score < -0.1:
            sentiment_label = "negative"  
        else:
            sentiment_label = "neutral"
        
        return sentiment_score, sentiment_label
    
    def _calculate_readability(self, text: str) -> float:
        """Simplified readability scoring (0-100)"""
        words = text.split()
        sentences = len(re.findall(r'[.!?]+', text))
        
        if not words or sentences == 0:
            return 50.0
        
        avg_words_per_sentence = len(words) / max(sentences, 1)
        
        # Simple readability formula
        if avg_words_per_sentence <= 10:
            readability = 90
        elif avg_words_per_sentence <= 15:
            readability = 80
        elif avg_words_per_sentence <= 20:
            readability = 70
        elif avg_words_per_sentence <= 25:
            readability = 60
        else:
            readability = 50
        
        return float(readability)
    
    def _calculate_overall_score(self, word_count: int, hashtag_count: int, 
                               emoji_count: int, sentiment_score: float, 
                               readability_score: float) -> float:
        """Calculate overall content score"""
        
        # Length score (optimal 20-100 words)
        if 20 <= word_count <= 100:
            length_score = 1.0
        elif word_count < 20:
            length_score = word_count / 20
        else:
            length_score = max(0.5, 100 / word_count)
        
        # Hashtag score (optimal 2-5)
        if 2 <= hashtag_count <= 5:
            hashtag_score = 1.0
        elif hashtag_count < 2:
            hashtag_score = hashtag_count / 2
        else:
            hashtag_score = max(0.3, 5 / hashtag_count)
        
        # Emoji score (optimal 1-3)
        if 1 <= emoji_count <= 3:
            emoji_score = 1.0
        elif emoji_count == 0:
            emoji_score = 0.7
        else:
            emoji_score = max(0.5, 3 / emoji_count)
        
        # Sentiment score (positive is better)
        sentiment_boost = max(0, sentiment_score) * 0.2
        
        # Readability score
        readability_factor = readability_score / 100
        
        # Combined score
        overall_score = (
            length_score * 0.25 +
            hashtag_score * 0.2 +
            emoji_score * 0.15 +
            readability_factor * 0.25 +
            0.15  # Base score
        ) + sentiment_boost
        
        return min(1.0, overall_score)
    
    def _score_content_length(self, word_count: int) -> float:
        """Score content based on length"""
        if 20 <= word_count <= 100:
            return 1.0
        elif word_count < 20:
            return word_count / 20
        else:
            return max(0.3, 100 / word_count)
    
    def _generate_optimization_tips(self, word_count: int, hashtag_count: int,
                                  emoji_count: int, sentiment_score: float,
                                  readability_score: float) -> List[str]:
        """Generate content optimization tips"""
        tips = []
        
        # Length optimization
        if word_count < 20:
            tips.append("📏 Consider adding more content (aim for 20-100 words)")
        elif word_count > 150:
            tips.append("✂️ Consider shortening your content for better engagement")
        
        # Hashtag optimization
        if hashtag_count < 2:
            tips.append("🏷️ Add 2-5 relevant hashtags to increase discoverability")
        elif hashtag_count > 8:
            tips.append("🚫 Reduce hashtags (5-8 is optimal)")
        
        # Emoji optimization
        if emoji_count == 0:
            tips.append("😊 Add 1-2 emojis to make content more engaging")
        elif emoji_count > 5:
            tips.append("📉 Reduce emoji usage for professional appeal")
        
        # Sentiment optimization
        if sentiment_score < -0.1:
            tips.append("💪 Add more positive language to boost engagement")
        elif sentiment_score > 0.2:
            tips.append("✨ Great positive tone! This should perform well")
        
        # Readability optimization
        if readability_score < 60:
            tips.append("📚 Simplify sentences for better readability")
        elif readability_score > 85:
            tips.append("🎯 Excellent readability! Easy to understand")
        
        if not tips:
            tips.append("🎉 Your content is well-optimized!")
        
        return tips
    
    def _suggest_hashtags(self, text: str, target_audience: str) -> List[str]:
        """Suggest relevant hashtags"""
        suggestions = self.hashtag_suggestions.get(target_audience, self.hashtag_suggestions['general'])
        
        # Add context-based hashtags
        text_lower = text.lower()
        
        if 'ai' in text_lower or 'artificial intelligence' in text_lower:
            suggestions.extend(['#AI', '#MachineLearning', '#ArtificialIntelligence'])
        
        if 'business' in text_lower or 'company' in text_lower:
            suggestions.extend(['#business', '#entrepreneur', '#startup'])
        
        if 'social' in text_lower or 'media' in text_lower:
            suggestions.extend(['#socialmedia', '#marketing', '#digital'])
        
        # Remove duplicates and limit
        unique_suggestions = list(set(suggestions))
        return unique_suggestions[:8]  # Limit to 8 suggestions
