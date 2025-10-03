"""
Feedback Microservice
===================

Complete feedback collection and processing capabilities.
Handles user feedback validation, quality assessment, and storage.
"""

from .feedback_collection import (
    FeedbackCollectionService,
    FeedbackCollectionConfig,
    FeedbackValidationConfig
)
from .feedback_storage import (
    FeedbackStorageService,
    FeedbackStorageConfig
)

__all__ = [
    # Main service
    'FeedbackCollectionService',
    'FeedbackCollectionConfig',
    'FeedbackValidationConfig',
    
    # Storage
    'FeedbackStorageService',
    'FeedbackStorageConfig'
]

# Microservice metadata
__microservice__ = {
    'name': 'feedback',
    'version': '1.0.0',
    'description': 'Complete feedback collection, validation, and storage system',
    'components': [
        'FeedbackCollectionService',
        'FeedbackStorageService'
    ]
}