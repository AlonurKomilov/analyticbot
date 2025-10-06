"""Intelligence Protocol Interfaces"""

from .reporting_protocols import (
    InsightData,
    InsightGeneratorProtocol,
    InsightType,
    IntelligenceProtocol,
    PatternAnalyzerProtocol,
    TrendAnalyzerProtocol,
)

# Additional intelligence-specific types
TrendAnalysis = dict
PatternResult = dict

__all__ = [
    "IntelligenceProtocol",
    "TrendAnalyzerProtocol",
    "PatternAnalyzerProtocol",
    "InsightGeneratorProtocol",
    "InsightData",
    "InsightType",
    "TrendAnalysis",
    "PatternResult",
]
