"""
Growth Data Processor
====================

Feature processing and normalization specifically for growth forecasting.
This processor handles growth metrics and time series preparation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class GrowthDataProcessor:
    """Specialized data processor for growth forecasting features"""
    
    def __init__(
        self,
        sequence_length: int = 30,
        scaling_method: str = "standard",  # standard, minmax, robust
        enable_feature_engineering: bool = True,
        smoothing_window: int = 7
    ):
        self.sequence_length = sequence_length
        self.scaling_method = scaling_method
        self.enable_feature_engineering = enable_feature_engineering
        self.smoothing_window = smoothing_window
        
        # Feature engineering parameters (define before scalers)
        self.feature_columns = [
            'growth_rate',
            'velocity',
            'acceleration',
            'momentum',
            'trend_strength'
        ]
        
        # Initialize scalers
        self.scalers = {}
        self._initialize_scalers()
        
        self.is_fitted = False
        logger.info(f"🌱 Growth Data Processor initialized with {scaling_method} scaling")
    
    def _initialize_scalers(self):
        """Initialize scalers based on method"""
        if self.scaling_method == "standard":
            scaler_class = StandardScaler
        elif self.scaling_method == "minmax":
            scaler_class = MinMaxScaler
        elif self.scaling_method == "robust":
            scaler_class = RobustScaler
        else:
            raise ValueError(f"Unknown scaling method: {self.scaling_method}")
        
        for feature in self.feature_columns:
            self.scalers[feature] = scaler_class()
    
    def engineer_growth_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Engineer growth-specific features
        
        Args:
            data: DataFrame with growth metrics
            
        Returns:
            DataFrame with engineered features
        """
        if not self.enable_feature_engineering:
            return data
        
        df = data.copy()
        
        try:
            # Ensure we have a numeric growth column
            if 'growth' not in df.columns:
                logger.warning("No 'growth' column found, using first numeric column")
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    df['growth'] = df[numeric_cols[0]]
                else:
                    raise ValueError("No numeric columns found in data")
            
            # 1. Growth Rate (percentage change)
            df['growth_rate'] = df['growth'].pct_change().fillna(0)
            
            # 2. Velocity (first derivative approximation)
            df['velocity'] = df['growth'].diff().fillna(0)
            
            # 3. Acceleration (second derivative approximation)
            df['acceleration'] = df['velocity'].diff().fillna(0)
            
            # 4. Momentum (exponentially weighted growth)
            alpha = 0.3
            df['momentum'] = df['growth'].ewm(alpha=alpha).mean()
            
            # 5. Trend Strength (rolling correlation with time index)
            window = min(self.smoothing_window, len(df))
            if window >= 3:
                df['trend_strength'] = df['growth'].rolling(window=window).apply(
                    lambda x: np.corrcoef(np.arange(len(x)), x)[0, 1] if len(x) > 1 else 0
                ).fillna(0)
            else:
                df['trend_strength'] = 0
            
            # Handle infinite values
            df = df.replace([np.inf, -np.inf], 0)
            
            # Apply smoothing if enabled
            if self.smoothing_window > 1:
                for col in self.feature_columns:
                    if col in df.columns:
                        df[col] = df[col].rolling(
                            window=self.smoothing_window, 
                            center=True
                        ).mean().fillna(df[col])
            
            logger.info(f"✨ Engineered {len(self.feature_columns)} growth features")
            
        except Exception as e:
            logger.error(f"❌ Feature engineering failed: {e}")
            # Create default features if engineering fails
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0.0
        
        return df
    
    def create_sequences(
        self, 
        data: pd.DataFrame, 
        target_column: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series modeling
        
        Args:
            data: DataFrame with growth features
            target_column: Column to use as target (if None, uses 'growth')
            
        Returns:
            Tuple of (X_sequences, y_targets)
        """
        if target_column is None:
            target_column = 'growth'
        
        # Engineer features first
        df = self.engineer_growth_features(data)
        
        # Select feature columns that exist in the data
        available_features = [col for col in self.feature_columns if col in df.columns]
        
        if not available_features:
            raise ValueError("No feature columns available in data")
        
        # Extract features and target
        features = df[available_features].values
        
        if target_column in df.columns:
            targets = df[target_column].values
        else:
            logger.warning(f"Target column '{target_column}' not found, using growth_rate")
            targets = df['growth_rate'].values
        
        # Create sequences
        X_sequences = []
        y_targets = []
        
        for i in range(len(features) - self.sequence_length):
            X_sequences.append(features[i:(i + self.sequence_length)])
            y_targets.append(targets[i + self.sequence_length])
        
        X_sequences = np.array(X_sequences)
        y_targets = np.array(y_targets).reshape(-1, 1)
        
        logger.info(f"📊 Created {len(X_sequences)} sequences of length {self.sequence_length}")
        logger.info(f"📊 Feature shape: {X_sequences.shape}, Target shape: {y_targets.shape}")
        
        return X_sequences, y_targets
    
    def fit_transform(self, data: pd.DataFrame, target_column: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Fit scalers and transform data
        
        Args:
            data: DataFrame with growth data
            target_column: Target column name
            
        Returns:
            Tuple of (scaled_sequences, scaled_targets)
        """
        # Create sequences first
        X_sequences, y_targets = self.create_sequences(data, target_column)
        
        # Fit scalers on flattened sequences
        n_samples, n_timesteps, n_features = X_sequences.shape
        X_flat = X_sequences.reshape(-1, n_features)
        
        # Fit feature scalers
        for i, feature in enumerate(self.feature_columns[:n_features]):
            self.scalers[feature].fit(X_flat[:, i].reshape(-1, 1))
        
        # Fit target scaler
        if 'target' not in self.scalers:
            if self.scaling_method == "standard":
                self.scalers['target'] = StandardScaler()
            elif self.scaling_method == "minmax":
                self.scalers['target'] = MinMaxScaler()
            else:
                self.scalers['target'] = RobustScaler()
        
        self.scalers['target'].fit(y_targets)
        
        # Transform data
        X_scaled = self._transform_sequences(X_sequences)
        y_scaled = self.scalers['target'].transform(y_targets)
        
        self.is_fitted = True
        logger.info("✅ Data processor fitted and transformed")
        
        return X_scaled, y_scaled
    
    def transform(self, data: pd.DataFrame, target_column: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Transform data using fitted scalers
        
        Args:
            data: DataFrame with growth data
            target_column: Target column name
            
        Returns:
            Tuple of (scaled_sequences, scaled_targets)
        """
        if not self.is_fitted:
            raise ValueError("Processor must be fitted before transform")
        
        # Create sequences
        X_sequences, y_targets = self.create_sequences(data, target_column)
        
        # Transform data
        X_scaled = self._transform_sequences(X_sequences)
        y_scaled = self.scalers['target'].transform(y_targets)
        
        return X_scaled, y_scaled
    
    def _transform_sequences(self, X_sequences: np.ndarray) -> np.ndarray:
        """Transform sequence data using fitted scalers"""
        n_samples, n_timesteps, n_features = X_sequences.shape
        X_scaled = np.zeros_like(X_sequences)
        
        for i, feature in enumerate(self.feature_columns[:n_features]):
            # Scale each feature across all samples and timesteps
            feature_data = X_sequences[:, :, i].reshape(-1, 1)
            scaled_data = self.scalers[feature].transform(feature_data)
            X_scaled[:, :, i] = scaled_data.reshape(n_samples, n_timesteps)
        
        return X_scaled
    
    def inverse_transform_target(self, scaled_targets: np.ndarray) -> np.ndarray:
        """Inverse transform target values
        
        Args:
            scaled_targets: Scaled target values
            
        Returns:
            Original scale target values
        """
        if not self.is_fitted:
            raise ValueError("Processor must be fitted before inverse transform")
        
        return self.scalers['target'].inverse_transform(scaled_targets)
    
    def get_feature_importance_weights(self) -> Dict[str, float]:
        """Get feature importance weights based on variance
        
        Returns:
            Dictionary with feature importance weights
        """
        if not self.is_fitted:
            return {feature: 1.0 for feature in self.feature_columns}
        
        weights = {}
        for feature in self.feature_columns:
            if feature in self.scalers:
                # Use variance as importance indicator
                scaler = self.scalers[feature]
                if hasattr(scaler, 'var_'):
                    weights[feature] = float(scaler.var_[0])
                elif hasattr(scaler, 'scale_'):
                    weights[feature] = float(1.0 / scaler.scale_[0])
                else:
                    weights[feature] = 1.0
            else:
                weights[feature] = 1.0
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate input data quality
        
        Args:
            data: Input DataFrame
            
        Returns:
            Validation report
        """
        report = {
            "valid": True,
            "issues": [],
            "recommendations": [],
            "data_shape": data.shape,
            "null_count": data.isnull().sum().sum(),
            "inf_count": 0
        }
        
        try:
            # Check for missing values
            null_count = data.isnull().sum().sum()
            if null_count > 0:
                report["issues"].append(f"Found {null_count} missing values")
                report["recommendations"].append("Consider interpolation or forward fill")
            
            # Check for infinite values
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            inf_count = 0
            for col in numeric_cols:
                inf_count += np.isinf(data[col]).sum()
            
            report["inf_count"] = inf_count
            if inf_count > 0:
                report["issues"].append(f"Found {inf_count} infinite values")
                report["recommendations"].append("Replace infinite values with appropriate bounds")
            
            # Check minimum data requirements
            if len(data) < self.sequence_length + 1:
                report["valid"] = False
                report["issues"].append(f"Insufficient data: need at least {self.sequence_length + 1} rows")
            
            # Check for constant columns
            for col in numeric_cols:
                if data[col].nunique() <= 1:
                    report["issues"].append(f"Column '{col}' has constant values")
                    report["recommendations"].append(f"Check data source for '{col}'")
            
        except Exception as e:
            report["valid"] = False
            report["issues"].append(f"Validation error: {e}")
        
        return report
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Get processor statistics and configuration
        
        Returns:
            Dictionary with processor information
        """
        stats = {
            "sequence_length": self.sequence_length,
            "scaling_method": self.scaling_method,
            "feature_engineering_enabled": self.enable_feature_engineering,
            "smoothing_window": self.smoothing_window,
            "is_fitted": self.is_fitted,
            "feature_columns": self.feature_columns,
            "scaler_count": len(self.scalers)
        }
        
        if self.is_fitted:
            stats["feature_importance"] = self.get_feature_importance_weights()
        
        return stats
