"""
CNN + Transformer Content Analysis Model
=======================================

PyTorch model combining CNN feature extraction with Transformer attention
for comprehensive content analysis and classification.
"""

import logging
import math
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer layers"""

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Access registered buffer safely
        pe_buffer = self.pe
        pe_slice = pe_buffer[: x.size(0), :].clone().detach()
        x = x + pe_slice
        return self.dropout(x)


class CNNFeatureExtractor(nn.Module):
    """CNN layers for local feature extraction from content"""

    def __init__(
        self,
        input_channels: int = 1,
        feature_channels: list[int] | None = None,
        kernel_sizes: list[int] | None = None,
        pool_sizes: list[int] | None = None,
        dropout_rate: float = 0.2,
    ):
        super().__init__()

        self.input_channels = input_channels
        self.feature_channels = feature_channels or [64, 128, 256]
        self.kernel_sizes = kernel_sizes or [3, 3, 3]
        self.pool_sizes = pool_sizes or [2, 2, 2]
        self.dropout_rate = dropout_rate

        # Build CNN layers
        self.conv_layers = nn.ModuleList()
        self.pool_layers = nn.ModuleList()
        self.norm_layers = nn.ModuleList()

        in_channels = input_channels
        for i, (out_channels, kernel_size, pool_size) in enumerate(
            zip(self.feature_channels, self.kernel_sizes, self.pool_sizes, strict=False)
        ):
            # Convolution layer
            conv = nn.Conv1d(
                in_channels=in_channels,
                out_channels=out_channels,
                kernel_size=kernel_size,
                padding=kernel_size // 2,
                bias=False,
            )
            self.conv_layers.append(conv)

            # Batch normalization
            self.norm_layers.append(nn.BatchNorm1d(out_channels))

            # Pooling layer
            self.pool_layers.append(nn.MaxPool1d(kernel_size=pool_size, stride=pool_size))

            in_channels = out_channels

        # Dropout and activation
        self.dropout = nn.Dropout(dropout_rate)
        self.activation = nn.ReLU()

        # Output feature dimension
        self.output_dim = self.feature_channels[-1]

        logger.info(f"🔍 CNN Feature Extractor initialized with {len(self.conv_layers)} layers")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features using CNN layers

        Args:
            x: Input tensor (batch_size, input_channels, sequence_length)

        Returns:
            Extracted features (batch_size, feature_dim, reduced_length)
        """
        for i, (conv, norm, pool) in enumerate(
            zip(self.conv_layers, self.norm_layers, self.pool_layers, strict=False)
        ):
            x = conv(x)

            # Apply batch norm only if batch size > 1
            if x.size(0) > 1:
                x = norm(x)

            x = self.activation(x)
            x = pool(x)

            if i < len(self.conv_layers) - 1:  # Don't apply dropout to last layer
                x = self.dropout(x)

        return x

    def get_output_length(self, input_length: int) -> int:
        """Calculate output sequence length after CNN processing"""
        length = input_length
        for pool_size in self.pool_sizes:
            length = length // pool_size
        return length


class TransformerEncoder(nn.Module):
    """Transformer encoder for global context understanding"""

    def __init__(
        self,
        d_model: int = 256,
        nhead: int = 8,
        num_layers: int = 4,
        dim_feedforward: int = 1024,
        dropout: float = 0.1,
        activation: str = "relu",
    ):
        super().__init__()

        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers

        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, dropout)

        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation=activation,
            batch_first=True,
        )

        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Layer normalization
        self.layer_norm = nn.LayerNorm(d_model)

        logger.info(f"🔄 Transformer Encoder initialized: {num_layers} layers, {nhead} heads")

    def forward(
        self, x: torch.Tensor, src_key_padding_mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        """Process features through transformer encoder

        Args:
            x: Input features (batch_size, seq_len, d_model)
            src_key_padding_mask: Mask for padding tokens

        Returns:
            Encoded features (batch_size, seq_len, d_model)
        """
        # Add positional encoding
        x = x.transpose(0, 1)  # (seq_len, batch_size, d_model)
        x = self.pos_encoder(x)
        x = x.transpose(0, 1)  # (batch_size, seq_len, d_model)

        # Apply transformer encoder
        encoded = self.transformer_encoder(x, src_key_padding_mask=src_key_padding_mask)

        # Layer normalization
        encoded = self.layer_norm(encoded)

        return encoded


class CNNTransformerModel(nn.Module):
    """Combined CNN + Transformer model for content analysis"""

    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        max_seq_length: int = 512,
        cnn_channels: list[int] | None = None,
        transformer_layers: int = 4,
        transformer_heads: int = 8,
        num_classes: int = 5,  # sentiment, toxicity, quality, engagement, relevance
        dropout_rate: float = 0.1,
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_seq_length = max_seq_length
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        self.version = "1.0.0"

        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

        # CNN feature extractor
        cnn_channels = cnn_channels or [embed_dim, embed_dim * 2, embed_dim]
        self.cnn_extractor = CNNFeatureExtractor(
            input_channels=embed_dim,
            feature_channels=cnn_channels,
            kernel_sizes=[3, 5, 3],
            pool_sizes=[1, 2, 1],  # More conservative pooling
            dropout_rate=dropout_rate,
        )

        # Projection layer to match transformer dimension
        self.feature_projection = nn.Linear(cnn_channels[-1], embed_dim)

        # Transformer encoder
        self.transformer = TransformerEncoder(
            d_model=embed_dim,
            nhead=transformer_heads,
            num_layers=transformer_layers,
            dim_feedforward=embed_dim * 4,
            dropout=dropout_rate,
        )

        # Classification heads for different content aspects
        self.classification_heads = nn.ModuleDict(
            {
                "sentiment": nn.Linear(embed_dim, 3),  # positive, neutral, negative
                "toxicity": nn.Linear(embed_dim, 2),  # toxic, non-toxic
                "quality": nn.Linear(embed_dim, 5),  # 1-5 quality score
                "engagement": nn.Linear(embed_dim, 4),  # low, medium, high, viral
                "relevance": nn.Linear(embed_dim, 3),  # relevant, somewhat, irrelevant
            }
        )

        # Global content representation
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.dropout = nn.Dropout(dropout_rate)

        # Initialize weights
        self._initialize_weights()

        logger.info(f"📊 CNN+Transformer Model initialized: {self.get_param_count()} parameters")

    def forward(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None
    ) -> dict[str, torch.Tensor]:
        """Forward pass through CNN + Transformer

        Args:
            input_ids: Token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)

        Returns:
            Dictionary with predictions for each content aspect
        """
        batch_size, seq_len = input_ids.shape

        # Token embedding
        embedded = self.token_embedding(input_ids)  # (batch_size, seq_len, embed_dim)
        embedded = self.dropout(embedded)

        # CNN feature extraction
        # Transpose for CNN: (batch_size, embed_dim, seq_len)
        cnn_input = embedded.transpose(1, 2)
        cnn_features = self.cnn_extractor(cnn_input)  # (batch_size, cnn_dim, reduced_seq_len)

        # Project CNN features and transpose back
        cnn_features = cnn_features.transpose(1, 2)  # (batch_size, reduced_seq_len, cnn_dim)
        projected_features = self.feature_projection(
            cnn_features
        )  # (batch_size, reduced_seq_len, embed_dim)

        # Create attention mask for reduced sequence
        if attention_mask is not None:
            # Adjust attention mask for CNN pooling
            reduced_seq_len = projected_features.size(1)
            pooling_factor = seq_len // reduced_seq_len if reduced_seq_len > 0 else 1
            reduced_mask = attention_mask[:, ::pooling_factor][:, :reduced_seq_len]

            # Convert to key padding mask (True for padding)
            key_padding_mask = ~reduced_mask.bool()
        else:
            key_padding_mask = None

        # Transformer encoding
        transformer_output = self.transformer(projected_features, key_padding_mask)

        # Global pooling for classification
        if attention_mask is not None:
            # Masked average pooling
            mask_expanded = reduced_mask.unsqueeze(-1).float()
            pooled = (transformer_output * mask_expanded).sum(dim=1) / mask_expanded.sum(
                dim=1
            ).clamp(min=1e-8)
        else:
            # Simple average pooling
            pooled = transformer_output.mean(dim=1)

        pooled = self.dropout(pooled)

        # Multi-task predictions
        predictions = {}
        for task_name, head in self.classification_heads.items():
            predictions[task_name] = head(pooled)

        return predictions

    def predict_with_confidence(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        mc_samples: int = 30,
    ) -> dict[str, dict[str, torch.Tensor]]:
        """Predict with confidence estimation using Monte Carlo dropout

        Args:
            input_ids: Token IDs
            attention_mask: Attention mask
            mc_samples: Number of Monte Carlo samples

        Returns:
            Dictionary with predictions and confidence scores
        """
        self.train()  # Enable dropout

        all_predictions = {task: [] for task in self.classification_heads.keys()}

        with torch.no_grad():
            for _ in range(mc_samples):
                pred = self(input_ids, attention_mask)
                for task_name, task_pred in pred.items():
                    all_predictions[task_name].append(F.softmax(task_pred, dim=-1))

        self.eval()  # Return to eval mode

        # Calculate statistics
        results = {}
        for task_name, predictions_list in all_predictions.items():
            stacked_preds = torch.stack(
                predictions_list, dim=0
            )  # (mc_samples, batch_size, num_classes)

            mean_pred = stacked_preds.mean(dim=0)
            std_pred = stacked_preds.std(dim=0)
            confidence = 1.0 - std_pred.mean(dim=-1)  # Higher confidence = lower uncertainty

            results[task_name] = {
                "prediction": mean_pred,
                "confidence": confidence,
                "uncertainty": std_pred.mean(dim=-1),
            }

        return results

    def get_attention_weights(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None
    ) -> torch.Tensor:
        """Extract attention weights from transformer layers

        Args:
            input_ids: Token IDs
            attention_mask: Attention mask

        Returns:
            Attention weights from last transformer layer
        """
        # Note: This is a simplified version. Full implementation would require
        # modifying the transformer to return attention weights
        self.eval()
        with torch.no_grad():
            _ = self(input_ids, attention_mask)

        # Placeholder - would need to hook into transformer attention
        batch_size = input_ids.size(0)
        seq_len = input_ids.size(1)
        return torch.ones(batch_size, self.transformer.nhead, seq_len, seq_len)

    def analyze_content_features(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor | None = None
    ) -> dict[str, Any]:
        """Comprehensive content analysis

        Args:
            input_ids: Token IDs
            attention_mask: Attention mask

        Returns:
            Detailed content analysis
        """
        self.eval()

        with torch.no_grad():
            # Get predictions with confidence
            confident_preds = self.predict_with_confidence(input_ids, attention_mask, mc_samples=20)

            # Get standard predictions
            self(input_ids, attention_mask)

            # Process results
            analysis = {
                "content_scores": {},
                "confidence_metrics": {},
                "risk_assessment": {},
                "recommendations": [],
            }

            for task_name, confident_pred in confident_preds.items():
                pred_probs = confident_pred["prediction"]
                confidence = confident_pred["confidence"]

                # Get predicted class and probability
                pred_class = torch.argmax(pred_probs, dim=-1)
                pred_prob = torch.max(pred_probs, dim=-1)[0]

                analysis["content_scores"][task_name] = {
                    "predicted_class": pred_class.cpu().numpy().tolist(),
                    "probability": pred_prob.cpu().numpy().tolist(),
                    "all_probabilities": pred_probs.cpu().numpy().tolist(),
                }

                analysis["confidence_metrics"][task_name] = {
                    "confidence": confidence.cpu().numpy().tolist(),
                    "uncertainty": confident_pred["uncertainty"].cpu().numpy().tolist(),
                }

            # Risk assessment
            toxicity_prob = confident_preds["toxicity"]["prediction"][:, 1]  # Toxic class
            quality_score = torch.argmax(confident_preds["quality"]["prediction"], dim=-1)

            analysis["risk_assessment"] = {
                "toxicity_risk": (
                    "high"
                    if toxicity_prob.mean() > 0.7
                    else "medium"
                    if toxicity_prob.mean() > 0.3
                    else "low"
                ),
                "quality_level": (
                    "high"
                    if quality_score.float().mean() >= 4
                    else "medium"
                    if quality_score.float().mean() >= 3
                    else "low"
                ),
                "overall_safety": ("safe" if toxicity_prob.mean() < 0.3 else "review_needed"),
            }

            # Generate recommendations
            if toxicity_prob.mean() > 0.5:
                analysis["recommendations"].append("Content may require moderation review")
            if quality_score.float().mean() < 3:
                analysis["recommendations"].append("Content quality could be improved")
            if confident_preds["engagement"]["confidence"].mean() < 0.6:
                analysis["recommendations"].append("Engagement prediction has low confidence")

        return analysis

    def _initialize_weights(self):
        """Initialize model weights using best practices"""
        for name, param in self.named_parameters():
            if "weight" in name:
                if "embedding" in name:
                    nn.init.normal_(param, mean=0, std=0.1)
                elif "linear" in name or "fc" in name:
                    nn.init.xavier_uniform_(param)
                elif "conv" in name:
                    nn.init.kaiming_uniform_(param, nonlinearity="relu")
            elif "bias" in name:
                nn.init.zeros_(param)

    def get_model_info(self) -> dict[str, Any]:
        """Get comprehensive model information"""
        return {
            "name": "CNN + Transformer Content Analyzer",
            "version": self.version,
            "architecture": {
                "vocab_size": self.vocab_size,
                "embed_dim": self.embed_dim,
                "max_seq_length": self.max_seq_length,
                "cnn_layers": len(self.cnn_extractor.conv_layers),
                "transformer_layers": self.transformer.num_layers,
                "transformer_heads": self.transformer.nhead,
                "num_classes": self.num_classes,
                "dropout_rate": self.dropout_rate,
            },
            "parameters": {
                "total": self.get_param_count(),
                "trainable": self.get_trainable_param_count(),
            },
            "tasks": list(self.classification_heads.keys()),
            "capabilities": [
                "multi_task_classification",
                "confidence_estimation",
                "attention_analysis",
                "content_risk_assessment",
                "feature_extraction",
            ],
        }

    def get_param_count(self) -> int:
        """Get total parameter count"""
        return sum(p.numel() for p in self.parameters())

    def get_trainable_param_count(self) -> int:
        """Get trainable parameter count"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


class CNNTransformerConfig:
    """Configuration class for CNN + Transformer model"""

    def __init__(
        self,
        vocab_size: int = 10000,
        embed_dim: int = 256,
        max_seq_length: int = 512,
        cnn_channels: list[int] | None = None,
        transformer_layers: int = 4,
        transformer_heads: int = 8,
        num_classes: int = 5,
        dropout_rate: float = 0.1,
        learning_rate: float = 0.0001,
    ):
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_seq_length = max_seq_length
        self.cnn_channels = cnn_channels or [embed_dim, embed_dim * 2, embed_dim]
        self.transformer_layers = transformer_layers
        self.transformer_heads = transformer_heads
        self.num_classes = num_classes
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "vocab_size": self.vocab_size,
            "embed_dim": self.embed_dim,
            "max_seq_length": self.max_seq_length,
            "cnn_channels": self.cnn_channels,
            "transformer_layers": self.transformer_layers,
            "transformer_heads": self.transformer_heads,
            "num_classes": self.num_classes,
            "dropout_rate": self.dropout_rate,
            "learning_rate": self.learning_rate,
        }

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "CNNTransformerConfig":
        """Create config from dictionary"""
        return cls(**config_dict)
