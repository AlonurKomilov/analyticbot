"""
GRU Growth Forecasting Model
===========================

PyTorch GRU model with attention mechanism for growth forecasting.
This is a focused neural network for time series growth prediction.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Tuple, Optional, List, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)


class AttentionLayer(nn.Module):
    """Attention mechanism for GRU outputs"""
    
    def __init__(self, hidden_size: int, attention_size: Optional[int] = None):
        super().__init__()
        self.hidden_size = hidden_size
        self.attention_size = attention_size or hidden_size // 2
        
        # Attention layers
        self.attention_layer = nn.Linear(hidden_size, self.attention_size)
        self.context_vector = nn.Linear(self.attention_size, 1, bias=False)
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, gru_output: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Apply attention mechanism to GRU outputs
        
        Args:
            gru_output: GRU output tensor (batch_size, seq_len, hidden_size)
            
        Returns:
            Tuple of (context_vector, attention_weights)
        """
        # Calculate attention scores
        attention_scores = torch.tanh(self.attention_layer(gru_output))
        attention_scores = self.context_vector(attention_scores).squeeze(-1)
        
        # Apply softmax to get weights
        attention_weights = self.softmax(attention_scores)
        
        # Calculate weighted context vector
        context_vector = torch.sum(gru_output * attention_weights.unsqueeze(-1), dim=1)
        
        return context_vector, attention_weights


class GRUGrowthModel(nn.Module):
    """GRU + Attention model for growth forecasting"""
    
    def __init__(
        self,
        input_size: int = 5,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout_rate: float = 0.2,
        output_size: int = 1,
        use_attention: bool = True
    ):
        super().__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.output_size = output_size
        self.use_attention = use_attention
        self.version = "1.0.0"
        
        # GRU layers
        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0.0,
            bidirectional=False
        )
        
        # Attention mechanism (optional)
        if use_attention:
            self.attention = AttentionLayer(hidden_size)
            dense_input_size = hidden_size
        else:
            self.attention = None
            dense_input_size = hidden_size
        
        # Dense layers for prediction
        self.fc1 = nn.Linear(dense_input_size, hidden_size // 2)
        self.fc2 = nn.Linear(hidden_size // 2, hidden_size // 4)
        self.fc3 = nn.Linear(hidden_size // 4, output_size)
        
        # Regularization
        self.dropout = nn.Dropout(dropout_rate)
        self.batch_norm1 = nn.BatchNorm1d(hidden_size // 2)
        self.batch_norm2 = nn.BatchNorm1d(hidden_size // 4)
        
        # Activation functions
        self.relu = nn.ReLU()
        self.leaky_relu = nn.LeakyReLU(0.1)
        
        # Initialize weights
        self._initialize_weights()
        
        logger.info(f"🌱 GRU Growth Model initialized: {self.get_param_count()} parameters")
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """Forward pass through the GRU model
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
            
        Returns:
            Tuple of (growth_prediction, attention_weights)
        """
        batch_size = x.size(0)
        
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)
        
        # GRU forward pass
        gru_output, hidden = self.gru(x, h0)
        
        # Apply attention or use last output
        if self.use_attention and self.attention is not None:
            context_vector, attention_weights = self.attention(gru_output)
            features = context_vector
        else:
            features = gru_output[:, -1, :]  # Use last time step
            attention_weights = None
        
        # Dense layers with regularization
        out = self.relu(self.fc1(features))
        
        # Apply batch normalization only if batch size > 1
        if out.size(0) > 1:
            out = self.batch_norm1(out)
        
        out = self.dropout(out)
        out = self.leaky_relu(self.fc2(out))
        
        if out.size(0) > 1:
            out = self.batch_norm2(out)
        
        out = self.dropout(out)
        
        # Final prediction (no activation for regression)
        prediction = self.fc3(out)
        
        return prediction, attention_weights
    
    def predict_with_uncertainty(
        self, 
        x: torch.Tensor, 
        mc_samples: int = 50
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict with uncertainty estimation using Monte Carlo dropout
        
        Args:
            x: Input tensor
            mc_samples: Number of Monte Carlo samples
            
        Returns:
            Tuple of (mean_prediction, std_prediction, all_predictions)
        """
        self.train()  # Enable dropout
        
        predictions = []
        with torch.no_grad():
            for _ in range(mc_samples):
                pred, _ = self(x)
                predictions.append(pred)
        
        self.eval()  # Return to eval mode
        
        # Stack predictions and calculate statistics
        all_predictions = torch.stack(predictions, dim=0)  # (mc_samples, batch, output)
        mean_pred = torch.mean(all_predictions, dim=0)
        std_pred = torch.std(all_predictions, dim=0)
        
        return mean_pred, std_pred, all_predictions
    
    def get_temporal_attention_patterns(self, x: torch.Tensor) -> Dict[str, Any]:
        """Analyze temporal attention patterns
        
        Args:
            x: Input tensor
            
        Returns:
            Dictionary with attention analysis
        """
        if not self.use_attention or self.attention is None:
            return {"error": "Attention mechanism not enabled"}
        
        self.eval()
        with torch.no_grad():
            _, attention_weights = self(x)
            
        # Analyze attention patterns
        analysis = {
            "attention_weights": attention_weights,
            "peak_attention_timesteps": torch.argmax(attention_weights, dim=1),
            "attention_entropy": -torch.sum(attention_weights * torch.log(attention_weights + 1e-8), dim=1),
            "attention_focus": torch.max(attention_weights, dim=1)[0],  # How focused the attention is
        }
        
        return analysis
    
    def _initialize_weights(self):
        """Initialize model weights using best practices"""
        for name, param in self.named_parameters():
            if 'weight' in name:
                if 'gru' in name and param.dim() >= 2:
                    # Xavier initialization for GRU weights
                    nn.init.xavier_uniform_(param)
                elif param.dim() >= 2:
                    # He initialization for dense layers
                    nn.init.kaiming_uniform_(param, nonlinearity='relu')
            elif 'bias' in name:
                # Initialize biases to zero
                nn.init.zeros_(param)
    
    def get_model_info(self) -> Dict:
        """Get comprehensive model information"""
        return {
            "name": "GRU Growth Forecaster",
            "version": self.version,
            "architecture": {
                "input_size": self.input_size,
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "dropout_rate": self.dropout_rate,
                "output_size": self.output_size,
                "use_attention": self.use_attention
            },
            "parameters": {
                "total": self.get_param_count(),
                "trainable": self.get_trainable_param_count()
            },
            "model_type": "GRU_with_Attention" if self.use_attention else "GRU",
            "framework": "PyTorch",
            "capabilities": [
                "growth_forecasting",
                "uncertainty_estimation",
                "attention_analysis" if self.use_attention else None
            ]
        }
    
    def get_param_count(self) -> int:
        """Get total parameter count"""
        return sum(p.numel() for p in self.parameters())
    
    def get_trainable_param_count(self) -> int:
        """Get trainable parameter count"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def freeze_layers(self, layers_to_freeze: List[str]):
        """Freeze specific layers for transfer learning
        
        Args:
            layers_to_freeze: List of layer name patterns to freeze
        """
        frozen_count = 0
        for name, param in self.named_parameters():
            if any(layer in name for layer in layers_to_freeze):
                param.requires_grad = False
                frozen_count += 1
                logger.info(f"🔒 Frozen parameter: {name}")
        
        logger.info(f"🔒 Frozen {frozen_count} parameters")
    
    def unfreeze_all_layers(self):
        """Unfreeze all layers"""
        for param in self.parameters():
            param.requires_grad = True
        logger.info("🔓 All layers unfrozen")
    
    def get_layer_activations(self, x: torch.Tensor, layer_name: str) -> torch.Tensor:
        """Get activations from specific layer for analysis
        
        Args:
            x: Input tensor
            layer_name: Name of layer to extract activations from
            
        Returns:
            Activation tensor from specified layer
        """
        if layer_name == "gru":
            batch_size = x.size(0)
            h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)
            gru_output, _ = self.gru(x, h0)
            return gru_output
        elif layer_name == "attention" and self.use_attention and self.attention is not None:
            gru_output = self.get_layer_activations(x, "gru")
            context_vector, attention_weights = self.attention(gru_output)
            return context_vector  # Return context vector only
        else:
            raise ValueError(f"Unknown layer: {layer_name}")


class GRUGrowthModelConfig:
    """Configuration class for GRU Growth Model"""
    
    def __init__(
        self,
        input_size: int = 5,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout_rate: float = 0.2,
        output_size: int = 1,
        use_attention: bool = True,
        learning_rate: float = 0.001,
        sequence_length: int = 30
    ):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.output_size = output_size
        self.use_attention = use_attention
        self.learning_rate = learning_rate
        self.sequence_length = sequence_length
    
    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout_rate": self.dropout_rate,
            "output_size": self.output_size,
            "use_attention": self.use_attention,
            "learning_rate": self.learning_rate,
            "sequence_length": self.sequence_length
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'GRUGrowthModelConfig':
        """Create config from dictionary"""
        return cls(**config_dict)