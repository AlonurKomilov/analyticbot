"""
Advanced Data Processing Package - Modular data processing engine.

This package provides comprehensive data processing capabilities split
into focused modules for better maintainability and testability.

Modules:
- base: Shared imports and configuration
- ingestion: Multi-source data ingestion
- cleaning: Data cleaning and validation
- quality: Data quality analysis and scoring
- transformation: Data transformation and feature engineering
- processor: Main AdvancedDataProcessor class
"""

from .processor import AdvancedDataProcessor, create_data_processor

__all__ = ["AdvancedDataProcessor", "create_data_processor"]
