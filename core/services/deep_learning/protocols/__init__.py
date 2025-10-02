"""
Service Protocol Interfaces for Deep Learning Microservices
===========================================================

These protocols define the contracts that all deep learning services must implement.
This enables dependency injection and easy testing with mocks.
"""

from typing import Protocol, Dict, List, Optional, Any
from abc import abstractmethod
from datetime import datetime


class PredictorProtocol(Protocol):
    """Protocol for prediction services (engagement, growth, etc.)"""
    
    @abstractmethod
    async def predict(self, input_data: Dict) -> Dict:
        """Make prediction from input data
        
        Args:
            input_data: Dictionary containing prediction parameters
            
        Returns:
            Dictionary with prediction results and metadata
        """
        ...
    
    @abstractmethod
    async def validate_input(self, input_data: Dict) -> bool:
        """Validate input data format and content
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        ...
    
    @abstractmethod
    async def get_service_health(self) -> Dict:
        """Get service health status
        
        Returns:
            Dictionary with health information
        """
        ...
    
    @abstractmethod
    async def get_model_info(self) -> Dict:
        """Get model information and metadata
        
        Returns:
            Dictionary with model details
        """
        ...


class EngagementPredictorProtocol(PredictorProtocol):
    """Protocol specifically for engagement prediction services"""
    
    @abstractmethod
    async def predict_engagement(self, channel_id: int, features: Dict) -> Dict:
        """Predict engagement for given channel and features
        
        Args:
            channel_id: Telegram channel ID
            features: Feature dictionary for prediction
            
        Returns:
            Engagement prediction results
        """
        ...
    
    @abstractmethod
    async def batch_predict_engagement(self, requests: List[Dict]) -> List[Dict]:
        """Batch engagement prediction for multiple requests
        
        Args:
            requests: List of prediction requests
            
        Returns:
            List of prediction results
        """
        ...


class GrowthForecasterProtocol(PredictorProtocol):
    """Protocol specifically for growth forecasting services"""
    
    @abstractmethod
    async def forecast_growth(self, channel_id: int, days: int) -> Dict:
        """Forecast growth for specified number of days
        
        Args:
            channel_id: Telegram channel ID
            days: Number of days to forecast
            
        Returns:
            Growth forecast results
        """
        ...
    
    @abstractmethod
    async def analyze_growth_patterns(self, channel_id: int) -> Dict:
        """Analyze historical growth patterns
        
        Args:
            channel_id: Telegram channel ID
            
        Returns:
            Growth pattern analysis
        """
        ...


class ContentAnalyzerProtocol(PredictorProtocol):
    """Protocol specifically for content analysis services"""
    
    @abstractmethod
    async def analyze_content_patterns(self, text_data: List[str]) -> Dict:
        """Analyze patterns in content data
        
        Args:
            text_data: List of text content to analyze
            
        Returns:
            Content pattern analysis results
        """
        ...
    
    @abstractmethod
    async def detect_viral_potential(self, content: str) -> Dict:
        """Detect viral potential of content
        
        Args:
            content: Text content to analyze
            
        Returns:
            Viral potential analysis
        """
        ...


class ModelLoaderProtocol(Protocol):
    """Protocol for model loading and management services"""
    
    @abstractmethod
    async def load_model(self, model_path: str, model_type: str) -> Any:
        """Load a model from file
        
        Args:
            model_path: Path to model file
            model_type: Type of model (pytorch, tensorflow, etc.)
            
        Returns:
            Loaded model instance
        """
        ...
    
    @abstractmethod
    async def save_model(self, model: Any, path: str) -> bool:
        """Save model to file
        
        Args:
            model: Model instance to save
            path: Path where to save the model
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    @abstractmethod
    async def get_model_metadata(self, model_path: str) -> Dict:
        """Get metadata for a saved model
        
        Args:
            model_path: Path to model file
            
        Returns:
            Model metadata dictionary
        """
        ...


class GPUConfigProtocol(Protocol):
    """Protocol for GPU configuration services"""
    
    @abstractmethod
    def get_optimal_batch_size(self) -> int:
        """Get optimal batch size for current hardware
        
        Returns:
            Recommended batch size
        """
        ...
    
    @abstractmethod
    def get_device_info(self) -> Dict:
        """Get device information
        
        Returns:
            Dictionary with device details
        """
        ...
    
    @abstractmethod
    def is_gpu_available(self) -> bool:
        """Check if GPU is available
        
        Returns:
            True if GPU available, False otherwise
        """
        ...


class DataProcessorProtocol(Protocol):
    """Protocol for data processing services"""
    
    @abstractmethod
    async def process_features(self, raw_data: Dict) -> Any:
        """Process raw data into model-ready features
        
        Args:
            raw_data: Raw input data
            
        Returns:
            Processed features ready for model input
        """
        ...
    
    @abstractmethod
    def validate_features(self, features: Dict) -> bool:
        """Validate feature data format
        
        Args:
            features: Feature data to validate
            
        Returns:
            True if valid, False otherwise
        """
        ...
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Get list of expected feature names
        
        Returns:
            List of feature names
        """
        ...