"""
Feedback Protocols for Adaptive Learning
========================================

Defines interfaces for user feedback collection, processing, and quality assessment.
These protocols ensure clean separation of concerns and dependency injection.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class FeedbackType(Enum):
    """Types of user feedback"""
    EXPLICIT_RATING = "explicit_rating"  # User provides explicit rating
    IMPLICIT_BEHAVIOR = "implicit_behavior"  # Inferred from user behavior
    CORRECTION = "correction"  # User corrects model output
    PREFERENCE = "preference"  # User preference indication
    COMPLAINT = "complaint"  # User complaint about result
    VALIDATION = "validation"  # User validates model output


class ContentType(Enum):
    """Types of content being rated/feedback on"""
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    ANALYSIS = "analysis"
    INSIGHT = "insight"
    RESPONSE = "response"


class FeedbackQuality(Enum):
    """Quality levels of feedback"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INVALID = "invalid"


class FeedbackSource(Enum):
    """Sources of feedback"""
    USER_INTERFACE = "user_interface"
    API_ENDPOINT = "api_endpoint"
    AUTOMATED_SYSTEM = "automated_system"
    ADMIN_PANEL = "admin_panel"
    BATCH_IMPORT = "batch_import"


@dataclass
class UserFeedback:
    """User feedback data structure"""
    user_id: str
    content_id: str
    content_type: ContentType
    feedback_type: FeedbackType
    rating: Optional[float] = None
    feedback_text: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class FeedbackBatch:
    """Batch of feedback for processing"""
    batch_id: str
    feedback_list: List[UserFeedback]
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_count: int = 0
    status: str = "pending"


@dataclass
class FeedbackAnalysis:
    """Analysis results of feedback"""
    analysis_id: str
    model_id: str
    feedback_count: int
    quality_distribution: Dict[FeedbackQuality, int]
    sentiment_score: float
    improvement_suggestions: List[str]
    timestamp: datetime


class FeedbackProtocol(ABC):
    """
    Protocol for feedback collection and processing services.
    
    This interface defines the contract for collecting user feedback,
    validating its quality, and preparing it for learning algorithms.
    """
    
    @abstractmethod
    async def collect_feedback(self, feedback: UserFeedback) -> bool:
        """
        Collect user feedback
        
        Args:
            feedback: User feedback to collect
            
        Returns:
            True if feedback was successfully collected
        """
        pass
    
    @abstractmethod
    async def validate_feedback(self, feedback: UserFeedback) -> FeedbackQuality:
        """
        Validate quality of feedback
        
        Args:
            feedback: Feedback to validate
            
        Returns:
            Quality level of the feedback
        """
        pass
    
    @abstractmethod
    async def get_feedback_batch(
        self,
        model_id: str,
        batch_size: int = 100,
        quality_filter: Optional[FeedbackQuality] = None
    ) -> FeedbackBatch:
        """
        Get batch of feedback for processing
        
        Args:
            model_id: ID of the model to get feedback for
            batch_size: Number of feedback items to include
            quality_filter: Optional filter for feedback quality
            
        Returns:
            Batch of feedback
        """
        pass
    
    @abstractmethod
    async def mark_feedback_processed(self, feedback_ids: List[str]) -> bool:
        """
        Mark feedback as processed
        
        Args:
            feedback_ids: List of feedback IDs to mark as processed
            
        Returns:
            True if all feedback was successfully marked
        """
        pass
    
    @abstractmethod
    async def get_feedback_stats(
        self,
        model_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """
        Get feedback statistics
        
        Args:
            model_id: ID of the model
            time_range: Optional time range filter
            
        Returns:
            Dictionary containing feedback statistics
        """
        pass


class FeedbackProcessorProtocol(ABC):
    """
    Protocol for processing and analyzing feedback.
    
    This interface defines methods for transforming raw feedback
    into structured data suitable for learning algorithms.
    """
    
    @abstractmethod
    async def process_feedback_batch(self, batch: FeedbackBatch) -> Dict[str, Any]:
        """
        Process a batch of feedback
        
        Args:
            batch: Batch of feedback to process
            
        Returns:
            Dictionary containing processing results
        """
        pass
    
    @abstractmethod
    async def extract_learning_signals(
        self,
        feedbacks: List[UserFeedback]
    ) -> Dict[str, Any]:
        """
        Extract learning signals from feedback
        
        Args:
            feedbacks: List of feedback to extract signals from
            
        Returns:
            Dictionary containing learning signals
        """
        pass
    
    @abstractmethod
    async def analyze_feedback_trends(
        self,
        model_id: str,
        time_window: int  # hours
    ) -> FeedbackAnalysis:
        """
        Analyze feedback trends over time
        
        Args:
            model_id: ID of the model
            time_window: Time window in hours to analyze
            
        Returns:
            Feedback analysis results
        """
        pass
    
    @abstractmethod
    async def detect_feedback_anomalies(
        self,
        model_id: str,
        sensitivity: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in feedback patterns
        
        Args:
            model_id: ID of the model
            sensitivity: Sensitivity threshold for anomaly detection
            
        Returns:
            List of detected anomalies
        """
        pass


class FeedbackStorageProtocol(ABC):
    """
    Protocol for feedback storage and retrieval.
    
    This interface defines methods for persistent storage
    of feedback data with efficient querying capabilities.
    """
    
    @abstractmethod
    async def store_feedback(self, feedback: UserFeedback) -> bool:
        """
        Store feedback persistently
        
        Args:
            feedback: Feedback to store
            
        Returns:
            True if feedback was successfully stored
        """
        pass
    
    @abstractmethod
    async def retrieve_feedback(
        self,
        model_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[UserFeedback]:
        """
        Retrieve feedback from storage
        
        Args:
            model_id: ID of the model
            filters: Optional filters for retrieval
            limit: Maximum number of feedback items to retrieve
            
        Returns:
            List of retrieved feedback
        """
        pass
    
    @abstractmethod
    async def update_feedback_status(
        self,
        feedback_ids: List[str],
        status_updates: Dict[str, Any]
    ) -> bool:
        """
        Update feedback status or metadata
        
        Args:
            feedback_ids: List of feedback IDs to update
            status_updates: Dictionary of updates to apply
            
        Returns:
            True if updates were successful
        """
        pass
    
    @abstractmethod
    async def cleanup_old_feedback(self, retention_days: int) -> int:
        """
        Clean up old feedback beyond retention period
        
        Args:
            retention_days: Number of days to retain feedback
            
        Returns:
            Number of feedback items cleaned up
        """
        pass