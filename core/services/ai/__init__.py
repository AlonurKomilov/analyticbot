"""
AI Services Module
==================

All AI/ML related services organized by capability:
- deep_learning: CNN, Transformer models for content/engagement/growth
- nlg: Natural Language Generation for reports and explanations
- insights: AI-powered insights fusion and pattern detection
- churn: Churn prediction and retention strategies
- predictive: Predictive intelligence and forecasting
- anomaly: Anomaly detection and analysis
- adaptive: Adaptive learning and model versioning

Usage:
    from core.services.ai import AIChatService
    from core.services.ai.churn import ChurnPredictionService
    from core.services.ai.predictive import PredictiveIntelligenceOrchestrator
"""

# AI Chat service
from core.services.ai.ai_chat_service import AIChatService

# NLG Integration
from core.services.ai.nlg_integration_service import NLGIntegrationService

# Strategy Generation
from core.services.ai.strategy_generation_service import StrategyGenerationService

__all__ = [
    "AIChatService",
    "NLGIntegrationService",
    "StrategyGenerationService",
]
