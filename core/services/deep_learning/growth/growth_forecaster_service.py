"""
Growth Forecaster Service
========================

Microservice for growth forecasting using GRU + Attention neural networks.
Focused on predicting business/user growth patterns with uncertainty estimation.
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
import logging
from datetime import datetime, timedelta
import asyncio
import json
from pathlib import Path
import pickle

from core.services.deep_learning.infrastructure.gpu_config import GPUConfigService
from core.services.deep_learning.infrastructure.model_loader import ModelLoader
from core.services.deep_learning.growth.models.gru_growth_model import (
    GRUGrowthModel, 
    GRUGrowthModelConfig
)
from core.services.deep_learning.growth.data_processors.growth_data_processor import (
    GrowthDataProcessor
)

logger = logging.getLogger(__name__)


class GrowthForecasterService:
    """Growth forecasting service using GRU + Attention neural networks"""
    
    def __init__(
        self,
        gpu_config: GPUConfigService,
        model_loader: ModelLoader,
        model_config: Optional[GRUGrowthModelConfig] = None,
        cache_predictions: bool = True,
        max_cache_size: int = 1000
    ):
        self.gpu_config = gpu_config
        self.model_loader = model_loader
        self.model_config = model_config or GRUGrowthModelConfig()
        self.cache_predictions = cache_predictions
        self.max_cache_size = max_cache_size
        
        # Initialize model and processor
        self.model: Optional[GRUGrowthModel] = None
        self.data_processor: Optional[GrowthDataProcessor] = None
        self.device = self.gpu_config.device  # Use the device attribute
        
        # Prediction cache
        self.prediction_cache: Dict[str, Dict] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Health monitoring
        self.health_stats = {
            "predictions_made": 0,
            "batch_predictions": 0,
            "uncertainty_estimations": 0,
            "errors": 0,
            "last_prediction_time": None,
            "model_loaded": False
        }
        
        # Initialize components
        self._initialize_components()
        
        logger.info(f"🌱 Growth Forecaster Service initialized on device: {self.device}")
    
    def _initialize_components(self):
        """Initialize model and data processor"""
        try:
            # Initialize data processor
            self.data_processor = GrowthDataProcessor(
                sequence_length=self.model_config.sequence_length,
                scaling_method="standard",
                enable_feature_engineering=True
            )
            
            # Initialize model
            self.model = GRUGrowthModel(
                input_size=self.model_config.input_size,
                hidden_size=self.model_config.hidden_size,
                num_layers=self.model_config.num_layers,
                dropout_rate=self.model_config.dropout_rate,
                output_size=self.model_config.output_size,
                use_attention=self.model_config.use_attention
            )
            
            # Move model to optimal device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.health_stats["model_loaded"] = True
            logger.info("✅ Growth forecaster components initialized successfully")
            
        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Failed to initialize components: {e}")
            raise
    
    async def predict_growth(
        self,
        data: Union[pd.DataFrame, List[Dict], Dict],
        forecast_horizon: int = 1,
        include_uncertainty: bool = True,
        return_attention: bool = False
    ) -> Dict[str, Any]:
        """Predict growth with uncertainty estimation
        
        Args:
            data: Historical growth data
            forecast_horizon: Number of periods to forecast
            include_uncertainty: Whether to include uncertainty estimation
            return_attention: Whether to return attention weights
            
        Returns:
            Dictionary with predictions and metadata
        """
        try:
            # Check if service is properly initialized
            if self.model is None or self.data_processor is None:
                raise RuntimeError("Service not properly initialized")
            
            # Convert input to DataFrame
            df = self._prepare_input_data(data)
            
            # Check cache
            cache_key = self._generate_cache_key(df, forecast_horizon, include_uncertainty)
            if self.cache_predictions and cache_key in self.prediction_cache:
                self.cache_hits += 1
                logger.debug("📋 Returning cached prediction")
                return self.prediction_cache[cache_key]
            
            self.cache_misses += 1
            
            # Validate input data
            validation_result = self.data_processor.validate_data(df)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid input data: {validation_result['issues']}")
            
            # Process data for model
            if not self.data_processor.is_fitted:
                # First time - fit and transform
                X_scaled, _ = self.data_processor.fit_transform(df)
            else:
                # Already fitted - just transform
                X_sequences, _ = self.data_processor.create_sequences(df)
                X_scaled = self.data_processor._transform_sequences(X_sequences)
            
            # Convert to tensor
            X_tensor = torch.FloatTensor(X_scaled).to(self.device)
            
            # Make predictions
            predictions = []
            attention_weights_list = []
            uncertainty_list = []
            
            current_sequence = X_tensor[-1:].clone()  # Use last sequence
            
            self.model.eval()
            with torch.no_grad():
                for step in range(forecast_horizon):
                    # Single prediction
                    pred, attention_weights = self.model(current_sequence)
                    predictions.append(pred.cpu().numpy())
                    
                    if return_attention and attention_weights is not None:
                        attention_weights_list.append(attention_weights.cpu().numpy())
                    
                    # Uncertainty estimation if requested
                    if include_uncertainty:
                        _, uncertainty, _ = self.model.predict_with_uncertainty(
                            current_sequence, mc_samples=30
                        )
                        uncertainty_list.append(uncertainty.cpu().numpy())
                    
                    # Update sequence for next prediction (rolling window)
                    if step < forecast_horizon - 1:
                        # Create new sequence by shifting and adding prediction
                        new_features = self._create_features_from_prediction(pred.cpu().numpy())
                        new_sequence = torch.cat([
                            current_sequence[:, 1:, :],  # Remove first timestep
                            torch.FloatTensor(new_features).unsqueeze(0).to(self.device)
                        ], dim=1)
                        current_sequence = new_sequence
            
            # Process results
            result = self._process_prediction_results(
                predictions,
                uncertainty_list if include_uncertainty else None,
                attention_weights_list if return_attention else None,
                forecast_horizon
            )
            
            # Update health stats
            self.health_stats["predictions_made"] += 1
            self.health_stats["last_prediction_time"] = datetime.now().isoformat()
            if include_uncertainty:
                self.health_stats["uncertainty_estimations"] += 1
            
            # Cache result
            if self.cache_predictions:
                self._cache_prediction(cache_key, result)
            
            logger.info(f"🎯 Growth prediction completed for horizon: {forecast_horizon}")
            return result
            
        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Growth prediction failed: {e}")
            raise
    
    async def predict_growth_batch(
        self,
        data_batch: List[Union[pd.DataFrame, Dict]],
        forecast_horizon: int = 1,
        include_uncertainty: bool = True
    ) -> List[Dict[str, Any]]:
        """Predict growth for multiple datasets
        
        Args:
            data_batch: List of historical growth datasets
            forecast_horizon: Number of periods to forecast
            include_uncertainty: Whether to include uncertainty estimation
            
        Returns:
            List of prediction results
        """
        try:
            logger.info(f"🔄 Processing batch of {len(data_batch)} growth predictions")
            
            # Process each dataset
            tasks = []
            for i, data in enumerate(data_batch):
                task = self.predict_growth(
                    data=data,
                    forecast_horizon=forecast_horizon,
                    include_uncertainty=include_uncertainty,
                    return_attention=False  # Skip attention for batch processing
                )
                tasks.append(task)
            
            # Execute predictions concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = {
                        "success": False,
                        "error": str(result),
                        "batch_index": i,
                        "timestamp": datetime.now().isoformat()
                    }
                    processed_results.append(error_result)
                    self.health_stats["errors"] += 1
                else:
                    if isinstance(result, dict):
                        result["batch_index"] = i
                    processed_results.append(result)
            
            self.health_stats["batch_predictions"] += 1
            logger.info(f"✅ Batch prediction completed: {len(processed_results)} results")
            
            return processed_results
            
        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Batch prediction failed: {e}")
            raise
    
    def analyze_growth_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze growth patterns and trends
        
        Args:
            data: Historical growth data
            
        Returns:
            Growth pattern analysis
        """
        try:
            if self.model is None or self.data_processor is None:
                raise RuntimeError("Service not properly initialized")
                
            df = self._prepare_input_data(data)
            
            # Engineer features for analysis
            processed_df = self.data_processor.engineer_growth_features(df)
            
            # Basic growth statistics
            growth_stats = {
                "mean_growth": float(processed_df['growth_rate'].mean()),
                "std_growth": float(processed_df['growth_rate'].std()),
                "volatility": float(processed_df['growth_rate'].std() / abs(processed_df['growth_rate'].mean())) if processed_df['growth_rate'].mean() != 0 else float('inf'),
                "trend_strength": float(processed_df['trend_strength'].mean()),
                "momentum": float(processed_df['momentum'].iloc[-1] if len(processed_df) > 0 else 0),
                "recent_velocity": float(processed_df['velocity'].tail(5).mean()),
                "acceleration": float(processed_df['acceleration'].tail(5).mean())
            }
            
            # Pattern classification
            patterns = self._classify_growth_patterns(processed_df)
            
            # Attention analysis if model has attention
            attention_analysis = {}
            if self.model.use_attention:
                try:
                    X_sequences, _ = self.data_processor.create_sequences(df)
                    if len(X_sequences) > 0:
                        X_scaled = self.data_processor._transform_sequences(X_sequences[-1:])
                        X_tensor = torch.FloatTensor(X_scaled).to(self.device)
                        attention_analysis = self.model.get_temporal_attention_patterns(X_tensor)
                        # Convert tensors to lists for JSON serialization
                        for key, value in attention_analysis.items():
                            if isinstance(value, torch.Tensor):
                                attention_analysis[key] = value.cpu().numpy().tolist()
                except Exception as e:
                    logger.warning(f"Attention analysis failed: {e}")
            
            result = {
                "growth_statistics": growth_stats,
                "growth_patterns": patterns,
                "attention_analysis": attention_analysis,
                "data_quality": self.data_processor.validate_data(df),
                "feature_importance": self.data_processor.get_feature_importance_weights(),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info("📊 Growth pattern analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Growth pattern analysis failed: {e}")
            raise
    
    def _prepare_input_data(self, data: Union[pd.DataFrame, List[Dict], Dict]) -> pd.DataFrame:
        """Convert input data to standardized DataFrame"""
        if isinstance(data, pd.DataFrame):
            return data.copy()
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _generate_cache_key(
        self, 
        data: pd.DataFrame, 
        forecast_horizon: int, 
        include_uncertainty: bool
    ) -> str:
        """Generate cache key for prediction"""
        data_hash = hash(str(data.values.tobytes()))
        return f"growth_{data_hash}_{forecast_horizon}_{include_uncertainty}"
    
    def _cache_prediction(self, cache_key: str, result: Dict[str, Any]):
        """Cache prediction result"""
        if len(self.prediction_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.prediction_cache))
            del self.prediction_cache[oldest_key]
        
        self.prediction_cache[cache_key] = result
    
    def _create_features_from_prediction(self, prediction: np.ndarray) -> np.ndarray:
        """Create feature vector from prediction for rolling forecasts"""
        # Simple feature creation - in practice, this would be more sophisticated
        pred_value = float(prediction[0])
        features = np.array([[
            pred_value,        # growth_rate
            pred_value * 0.1,  # velocity (simplified)
            0.0,               # acceleration (unknown)
            pred_value * 0.8,  # momentum (simplified)
            0.5                # trend_strength (neutral)
        ]])
        return features
    
    def _process_prediction_results(
        self,
        predictions: List[np.ndarray],
        uncertainties: Optional[List[np.ndarray]],
        attention_weights: Optional[List[np.ndarray]],
        forecast_horizon: int
    ) -> Dict[str, Any]:
        """Process and format prediction results"""
        # Convert predictions to list
        pred_values = [float(pred[0][0]) for pred in predictions]
        
        # Prepare result
        model_info = None
        if self.model is not None:
            model_info = self.model.get_model_info()
        
        result = {
            "success": True,
            "predictions": pred_values,
            "forecast_horizon": forecast_horizon,
            "timestamp": datetime.now().isoformat(),
            "model_info": model_info,
            "confidence_level": 0.95 if uncertainties else None
        }
        
        # Add uncertainty if available
        if uncertainties:
            uncertainty_values = [float(unc[0][0]) for unc in uncertainties]
            result["uncertainties"] = uncertainty_values
            result["confidence_intervals"] = [
                {
                    "lower": pred - 1.96 * unc,
                    "upper": pred + 1.96 * unc
                }
                for pred, unc in zip(pred_values, uncertainty_values)
            ]
        
        # Add attention if available
        if attention_weights:
            result["attention_patterns"] = [
                weights[0].tolist() for weights in attention_weights
            ]
        
        return result
    
    def _classify_growth_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Classify growth patterns in the data"""
        patterns = {
            "trend": "unknown",
            "seasonality": "none",
            "volatility_level": "medium",
            "growth_phase": "unknown",
            "pattern_strength": 0.0
        }
        
        try:
            growth_rate = data['growth_rate'].dropna()
            
            if len(growth_rate) > 10:
                # Trend classification
                trend_strength = data['trend_strength'].mean()
                if trend_strength > 0.3:
                    patterns["trend"] = "upward"
                elif trend_strength < -0.3:
                    patterns["trend"] = "downward"
                else:
                    patterns["trend"] = "sideways"
                
                patterns["pattern_strength"] = float(abs(trend_strength))
                
                # Volatility classification
                volatility = growth_rate.std()
                if volatility < 0.1:
                    patterns["volatility_level"] = "low"
                elif volatility > 0.3:
                    patterns["volatility_level"] = "high"
                else:
                    patterns["volatility_level"] = "medium"
                
                # Growth phase
                recent_growth = growth_rate.tail(5).mean()
                if recent_growth > 0.05:
                    patterns["growth_phase"] = "expansion"
                elif recent_growth < -0.05:
                    patterns["growth_phase"] = "contraction"
                else:
                    patterns["growth_phase"] = "stable"
        
        except Exception as e:
            logger.warning(f"Pattern classification failed: {e}")
        
        return patterns
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health and statistics"""
        cache_efficiency = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0 else 0
        )
        
        return {
            "service_name": "GrowthForecasterService",
            "status": "healthy" if self.health_stats["model_loaded"] and self.model is not None else "unhealthy",
            "device": str(self.device),
            "model_info": self.model.get_model_info() if self.model is not None else None,
            "health_stats": self.health_stats.copy(),
            "cache_stats": {
                "enabled": self.cache_predictions,
                "size": len(self.prediction_cache),
                "max_size": self.max_cache_size,
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "efficiency": cache_efficiency
            },
            "processor_stats": self.data_processor.get_processor_stats() if self.data_processor is not None else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear prediction cache"""
        self.prediction_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("🧹 Prediction cache cleared")
    
    async def load_pretrained_model(self, model_path: str) -> bool:
        """Load a pre-trained model
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load model using model loader service
            model_info = await self.model_loader.load_model(model_path, "pytorch")
            
            if model_info and "model" in model_info:
                self.model = model_info["model"].to(self.device)
                if self.model:
                    self.model.eval()
                
                # Update health stats
                self.health_stats["model_loaded"] = True
                
                logger.info(f"✅ Pre-trained model loaded from: {model_path}")
                return True
            else:
                logger.error(f"❌ Failed to load model from: {model_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            self.health_stats["errors"] += 1
            return False
    
    async def save_model(self, model_path: str, include_processor: bool = True) -> bool:
        """Save current model and processor
        
        Args:
            model_path: Path to save the model
            include_processor: Whether to save the data processor
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is None:
                raise RuntimeError("No model to save")
                
            # Prepare model info
            model_info = {
                "model": self.model,
                "config": self.model_config.to_dict(),
                "model_state": self.model.get_model_info(),
                "service_stats": self.get_service_health()
            }
            
            if include_processor and self.data_processor:
                model_info["data_processor"] = self.data_processor
            
            # Save using model loader service
            success = await self.model_loader.save_model(model_info, model_path, "pytorch")
            
            if success:
                logger.info(f"✅ Model saved to: {model_path}")
            else:
                logger.error(f"❌ Failed to save model to: {model_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Model saving failed: {e}")
            self.health_stats["errors"] += 1
            return False