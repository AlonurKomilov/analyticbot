"""
Natural Language Generation (NLG) Service Package

Refactored microservices architecture for NLG capabilities.

This package provides a clean, focused microservices architecture for
natural language generation, replacing the original 841-line monolithic service.

Architecture:
- TemplateManager: Manages templates, patterns, and descriptions
- ContentFormatter: Handles text formatting and cleaning
- NarrativeGenerator: Generates narratives and insights
- ExplanationGenerator: Creates specialized explanations
- NLGOrchestrator: Coordinates all microservices

Primary Interface:
    from core.services.nlg import NLGOrchestrator

    orchestrator = NLGOrchestrator()
    insight = await orchestrator.generate_insight_narrative(data, InsightType.TREND)

Backwards Compatibility:
    The NLGOrchestrator provides the same API as the original
    NaturalLanguageGenerationService, ensuring zero breaking changes.

Part of Fat Services Refactoring (Priority #2)
"""

# Main orchestrator (primary interface)
from .explanation.explanation_generator import ExplanationGenerator
from .formatting.content_formatter import ContentFormatter
from .narrative.narrative_generator import InsightNarrative, NarrativeGenerator
from .orchestrator.nlg_orchestrator import (
    NaturalLanguageGenerationService,  # Backwards compatibility alias
    NLGOrchestrator,
)

# Microservices (for direct access if needed)
from .templates.template_manager import InsightType, NarrativeStyle, TemplateManager

__all__ = [
    # Primary interface
    "NLGOrchestrator",
    "NaturalLanguageGenerationService",
    # Enums and data structures
    "InsightType",
    "NarrativeStyle",
    "InsightNarrative",
    # Microservices (for direct access)
    "TemplateManager",
    "ContentFormatter",
    "NarrativeGenerator",
    "ExplanationGenerator",
]
