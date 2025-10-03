"""
LSTM Engagement Model
====================

PyTorch LSTM model specifically designed for engagement prediction.
This is a focused neural network for single-purpose engagement forecasting.
"""

import logging

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)


class LSTMEngagementModel(nn.Module):
    """LSTM neural network for engagement prediction"""

    def __init__(
        self,
        input_size: int = 8,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout_rate: float = 0.2,
    ):
        super().__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.version = "1.0.0"

        # LSTM layers with dropout
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0.0,
            bidirectional=False,
        )

        # Dense layers for final prediction
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, 1)

        # Regularization
        self.dropout = nn.Dropout(dropout_rate)
        self.batch_norm = nn.BatchNorm1d(32)

        # Activation functions
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

        # Initialize weights
        self._initialize_weights()

        logger.info(f"🧠 LSTM Engagement Model initialized: {self.get_param_count()} parameters")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the LSTM model

        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)

        Returns:
            Engagement prediction tensor of shape (batch_size, 1)
        """
        batch_size = x.size(0)

        # Initialize hidden states
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)

        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x, (h0, c0))

        # Take the output from the last time step
        last_output = lstm_out[:, -1, :]  # Shape: (batch_size, hidden_size)

        # Dense layers with regularization
        out = self.relu(self.fc1(last_output))

        # Apply batch normalization only if batch size > 1
        if out.size(0) > 1:
            out = self.batch_norm(out)

        out = self.dropout(out)
        out = self.relu(self.fc2(out))
        out = self.dropout(out)

        # Final prediction (sigmoid for 0-1 range)
        out = self.sigmoid(self.fc3(out))

        return out

    def predict_with_confidence(
        self, x: torch.Tensor, mc_samples: int = 10
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Predict with Monte Carlo dropout for uncertainty estimation

        Args:
            x: Input tensor
            mc_samples: Number of Monte Carlo samples for uncertainty

        Returns:
            Tuple of (mean_prediction, std_deviation)
        """
        self.train()  # Enable dropout for MC sampling

        predictions = []
        with torch.no_grad():
            for _ in range(mc_samples):
                pred = self(x)
                predictions.append(pred)

        self.eval()  # Return to eval mode

        # Calculate mean and std
        predictions_tensor = torch.stack(predictions, dim=0)
        mean_pred = torch.mean(predictions_tensor, dim=0)
        std_pred = torch.std(predictions_tensor, dim=0)

        return mean_pred, std_pred

    def get_feature_importance(self, x: torch.Tensor) -> dict[str, float]:
        """Calculate feature importance using gradient-based method

        Args:
            x: Input tensor (must require gradients)

        Returns:
            Dictionary with feature importance scores
        """
        try:
            self.eval()

            # Ensure input requires gradients
            if not x.requires_grad:
                x = x.requires_grad_(True)

            # Forward pass
            output = self(x)

            # Backward pass to get gradients
            if output.grad_fn is not None:
                output.backward(torch.ones_like(output), retain_graph=True)

                # Calculate importance as absolute gradient magnitude
            if x.grad is not None:
                gradients = x.grad.abs().mean(dim=(0, 1))  # Average over batch and sequence

                # Convert to feature importance dict
                feature_names = [
                    "views",
                    "forwards",
                    "replies",
                    "reactions",
                    "hour_of_day",
                    "day_of_week",
                    "content_length",
                    "has_media",
                ]

                importance_dict = {}
                for i, name in enumerate(feature_names[: len(gradients)]):
                    importance_dict[name] = float(gradients[i])

                return importance_dict
            else:
                # Return empty dict if no gradients available
                return {}

        except Exception as e:
            logger.warning(f"Feature importance calculation failed: {e}")
            return {}

    def _initialize_weights(self):
        """Initialize model weights using best practices"""
        for name, param in self.named_parameters():
            if "weight" in name:
                if "lstm" in name and param.dim() >= 2:
                    # Xavier initialization for LSTM weights (only if 2D or more)
                    nn.init.xavier_uniform_(param)
                elif param.dim() >= 2:
                    # He initialization for dense layers (only if 2D or more)
                    nn.init.kaiming_uniform_(param, nonlinearity="relu")
            elif "bias" in name:
                # Initialize biases to zero
                nn.init.zeros_(param)

    def get_model_info(self) -> dict:
        """Get comprehensive model information"""
        return {
            "name": "LSTM Engagement Predictor",
            "version": self.version,
            "architecture": {
                "input_size": self.input_size,
                "hidden_size": self.hidden_size,
                "num_layers": self.num_layers,
                "dropout_rate": self.dropout_rate,
            },
            "parameters": {
                "total": self.get_param_count(),
                "trainable": self.get_trainable_param_count(),
            },
            "model_type": "LSTM",
            "framework": "PyTorch",
            "output_range": "0-1 (sigmoid activation)",
        }

    def get_param_count(self) -> int:
        """Get total parameter count"""
        return sum(p.numel() for p in self.parameters())

    def get_trainable_param_count(self) -> int:
        """Get trainable parameter count"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def freeze_layers(self, layers_to_freeze: list):
        """Freeze specific layers for transfer learning

        Args:
            layers_to_freeze: List of layer names to freeze
        """
        for name, param in self.named_parameters():
            if any(layer in name for layer in layers_to_freeze):
                param.requires_grad = False
                logger.info(f"🔒 Frozen layer: {name}")

    def unfreeze_all_layers(self):
        """Unfreeze all layers"""
        for param in self.parameters():
            param.requires_grad = True
        logger.info("🔓 All layers unfrozen")

    def get_layer_output(self, x: torch.Tensor, layer_name: str) -> torch.Tensor:
        """Get output from specific layer for analysis

        Args:
            x: Input tensor
            layer_name: Name of layer to extract output from

        Returns:
            Output tensor from specified layer
        """
        if layer_name == "lstm":
            batch_size = x.size(0)
            h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)
            c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size, device=x.device)
            lstm_out, _ = self.lstm(x, (h0, c0))
            return lstm_out
        elif layer_name == "fc1":
            lstm_out = self.get_layer_output(x, "lstm")
            last_output = lstm_out[:, -1, :]
            return self.relu(self.fc1(last_output))
        # Add more layers as needed
        else:
            raise ValueError(f"Unknown layer: {layer_name}")


class LSTMEngagementModelConfig:
    """Configuration class for LSTM Engagement Model"""

    def __init__(
        self,
        input_size: int = 8,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001,
        sequence_length: int = 30,
    ):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.sequence_length = sequence_length

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "num_layers": self.num_layers,
            "dropout_rate": self.dropout_rate,
            "learning_rate": self.learning_rate,
            "sequence_length": self.sequence_length,
        }
