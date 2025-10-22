"""
Advanced Data Processor - Main class combining all processing capabilities.

This module provides the main AdvancedDataProcessor class that combines
all data processing capabilities through multiple mixins.
"""

from .cleaning import DataCleaningMixin
from .ingestion import DataIngestionMixin
from .quality import DataQualityMixin
from .transformation import DataTransformationMixin


class AdvancedDataProcessor(
    DataIngestionMixin, DataCleaningMixin, DataQualityMixin, DataTransformationMixin
):
    """
    🔄 Advanced Data Processing Engine

    Comprehensive data processing capabilities:
    - Multi-format data ingestion (CSV, JSON, Excel, Parquet, SQL)
    - Real-time data streaming via WebSocket
    - Automated data cleaning and validation
    - Statistical analysis and outlier detection
    - Data transformation and feature engineering
    """

    def __init__(self):
        """Initialize all processing components"""
        # Initialize mixin components
        DataCleaningMixin.__init__(self)
        DataTransformationMixin.__init__(self)

        # Additional state management
        self.processed_datasets = {}
        self.streaming_connections = {}


# Convenience function for easy integration with bot utils
async def create_data_processor():
    """Factory function to create and initialize data processor"""
    return AdvancedDataProcessor()


__all__ = ["AdvancedDataProcessor", "create_data_processor"]
