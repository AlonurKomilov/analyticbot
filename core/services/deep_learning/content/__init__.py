"""
Content Analysis Module
======================

Deep learning-based content analysis using CNN + Transformer neural networks.
Provides microservices for analyzing text content across multiple dimensions.
"""

from .content_analyzer_service import ContentAnalyzerService
from .data_processors.content_data_processor import ContentDataProcessor
from .models.cnn_transformer_model import CNNTransformerConfig, CNNTransformerModel

__all__ = [
    "ContentAnalyzerService",
    "CNNTransformerModel",
    "CNNTransformerConfig",
    "ContentDataProcessor",
]

__version__ = "1.0.0"
