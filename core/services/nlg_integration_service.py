"""
NLG Integration Service - Natural Language Generation Integration

Extracted from AIInsightsService to maintain Single Responsibility Principle.
Handles integration between AI insights and natural language generation.

Part of Phase 3 AI-First Architecture.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional, Dict

from .nlg_service import NaturalLanguageGenerationService, InsightType, NarrativeStyle

logger = logging.getLogger(__name__)


class NLGIntegrationService:
    """
    🗣️ Natural Language Generation Integration Service
    
    Specialized service for integrating AI insights with natural language generation:
    - Enhanced insights with narratives
    - Executive summary generation
    - Human-readable explanations
    - Multi-style narrative generation
    """

    def __init__(self):
        """Initialize NLG integration service"""
        self._nlg_service = NaturalLanguageGenerationService()

    async def enhance_insights_with_narrative(
        self,
        insights: dict,
        narrative_style: NarrativeStyle = NarrativeStyle.CONVERSATIONAL,
        days: int = 30
    ) -> dict:
        """
        🗣️ Enhance AI Insights with Natural Language Narratives
        
        Takes standard AI insights and adds human-readable narratives.
        Perfect for non-technical users who need insights explained in plain language.
        
        Args:
            insights: Standard AI insights from AIInsightsService
            narrative_style: How to present the insights (executive, conversational, technical)
            days: Analysis period for context
            
        Returns:
            Enhanced insights with natural language explanations
        """
        try:
            # Generate natural language narratives for key insights
            narratives = {}
            
            # Performance narrative
            if insights.get("performance_insights"):
                performance_narrative = await self._nlg_service.generate_insight_narrative(
                    insights["performance_insights"],
                    InsightType.PERFORMANCE,
                    narrative_style
                )
                narratives["performance"] = performance_narrative
            
            # Content pattern narrative
            if insights.get("content_insights"):
                content_narrative = await self._nlg_service.generate_insight_narrative(
                    insights["content_insights"],
                    InsightType.ENGAGEMENT,
                    narrative_style
                )
                narratives["content"] = content_narrative
            
            # Audience behavior narrative
            if insights.get("audience_insights"):
                audience_narrative = await self._nlg_service.generate_insight_narrative(
                    insights["audience_insights"],
                    InsightType.AUDIENCE,
                    narrative_style
                )
                narratives["audience"] = audience_narrative
            
            # Generate executive summary
            executive_summary = await self._nlg_service.generate_executive_summary(
                insights, f"{days} days"
            )
            
            # Enhanced response with narratives
            enhanced_insights = {
                **insights,
                "natural_language": {
                    "narratives": narratives,
                    "executive_summary": executive_summary,
                    "style": narrative_style.value,
                    "generated_at": datetime.now().isoformat()
                },
                "ai_narrator": {
                    "enabled": True,
                    "confidence": insights.get("confidence_score", 0.7),
                    "total_narratives": len(narratives)
                }
            }
            
            logger.info(f"Insights enhanced with {len(narratives)} narratives")
            return enhanced_insights
            
        except Exception as e:
            logger.error(f"Insight narrative enhancement failed: {e}")
            # Fallback to original insights
            return {
                **insights,
                "natural_language": {
                    "error": "Narrative generation temporarily unavailable",
                    "fallback": True
                }
            }

    async def generate_multi_style_narratives(
        self,
        insights: dict,
        styles: list[NarrativeStyle] = None
    ) -> dict:
        """
        🎨 Generate Multiple Narrative Styles for Same Insights
        
        Creates different narrative presentations of the same insights,
        allowing users to choose their preferred communication style.
        """
        try:
            if styles is None:
                styles = [
                    NarrativeStyle.EXECUTIVE,
                    NarrativeStyle.CONVERSATIONAL,
                    NarrativeStyle.ANALYTICAL
                ]
            
            multi_style_narratives = {}
            
            for style in styles:
                enhanced = await self.enhance_insights_with_narrative(insights, style)
                multi_style_narratives[style.value] = enhanced.get("natural_language", {})
            
            return {
                "multi_style_narratives": multi_style_narratives,
                "available_styles": [style.value for style in styles],
                "default_style": "conversational",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-style narrative generation failed: {e}")
            return {
                "error": "Multi-style narrative generation failed",
                "fallback_style": "conversational"
            }

    async def generate_narrative_summary(
        self,
        insights: dict,
        summary_type: str = "executive",
        target_audience: str = "general"
    ) -> dict:
        """
        📋 Generate Focused Narrative Summary
        
        Creates a concise narrative summary focused on specific aspects
        of the insights based on the intended audience and purpose.
        """
        try:
            # Determine narrative style based on target audience
            style_mapping = {
                "executives": NarrativeStyle.EXECUTIVE,
                "creators": NarrativeStyle.CONVERSATIONAL,
                "analysts": NarrativeStyle.ANALYTICAL,
                "technical": NarrativeStyle.TECHNICAL,
                "general": NarrativeStyle.CONVERSATIONAL
            }
            
            narrative_style = style_mapping.get(target_audience, NarrativeStyle.CONVERSATIONAL)
            
            # Generate focused summary
            if summary_type == "executive":
                summary = await self._nlg_service.generate_executive_summary(
                    insights, "analysis period"
                )
            else:
                # Generate custom summary based on type
                summary = await self._generate_custom_summary(insights, summary_type, narrative_style)
            
            return {
                "summary": summary,
                "summary_type": summary_type,
                "target_audience": target_audience,
                "narrative_style": narrative_style.value,
                "confidence": insights.get("confidence_score", 0.7),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Narrative summary generation failed: {e}")
            return {
                "summary": "Summary generation temporarily unavailable",
                "error": str(e)
            }

    async def _generate_custom_summary(
        self,
        insights: dict,
        summary_type: str,
        narrative_style: NarrativeStyle
    ) -> str:
        """Generate custom summary based on type and style"""
        try:
            if summary_type == "performance":
                # Focus on performance metrics
                performance_data = insights.get("performance_insights", {})
                return await self._nlg_service.generate_insight_narrative(
                    performance_data,
                    InsightType.PERFORMANCE,
                    narrative_style
                )
            
            elif summary_type == "recommendations":
                # Focus on actionable recommendations
                recommendations = insights.get("recommendations", [])
                if recommendations:
                    rec_data = {"recommendations": recommendations[:3]}  # Top 3
                    narrative = await self._nlg_service.generate_insight_narrative(
                        rec_data,
                        InsightType.STRATEGIES,
                        narrative_style
                    )
                    return narrative
                else:
                    return "No specific recommendations available at this time."
            
            elif summary_type == "trends":
                # Focus on pattern and trend analysis
                patterns = insights.get("key_patterns", [])
                if patterns:
                    pattern_data = {"patterns": patterns[:3]}  # Top 3 patterns
                    return await self._nlg_service.generate_insight_narrative(
                        pattern_data,
                        InsightType.TRENDS,
                        narrative_style
                    )
                else:
                    return "No significant trends identified in the current data."
            
            else:
                # Default to executive summary
                return await self._nlg_service.generate_executive_summary(
                    insights, "analysis period"
                )
                
        except Exception as e:
            logger.error(f"Custom summary generation failed: {e}")
            return "Custom summary generation encountered an issue."

    async def health_check(self) -> dict:
        """Health check for NLG integration service"""
        try:
            # Test NLG service availability
            test_data = {"test": "value"}
            await self._nlg_service.generate_insight_narrative(
                test_data, InsightType.PERFORMANCE, NarrativeStyle.CONVERSATIONAL
            )
            nlg_status = "healthy"
        except Exception:
            nlg_status = "degraded"
        
        return {
            "service": "NLGIntegrationService",
            "status": "healthy" if nlg_status == "healthy" else "degraded",
            "capabilities": [
                "narrative_enhancement",
                "multi_style_generation",
                "executive_summaries",
                "custom_summaries"
            ],
            "dependencies": {
                "nlg_service": nlg_status == "healthy"
            },
            "timestamp": datetime.now().isoformat()
        }