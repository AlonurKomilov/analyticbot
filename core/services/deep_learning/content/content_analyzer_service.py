"""
Content Analyzer Service
========================

Microservice for content analysis using CNN + Transformer neural networks.
Analyzes text content for sentiment, toxicity, quality, engagement, and relevance.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np
import torch

from core.services.deep_learning.content.data_processors.content_data_processor import (
    ContentDataProcessor,
)
from core.services.deep_learning.content.models.cnn_transformer_model import (
    CNNTransformerConfig,
    CNNTransformerModel,
)
from core.services.deep_learning.infrastructure.gpu_config import GPUConfigService
from core.services.deep_learning.infrastructure.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class ContentAnalyzerService:
    """Content analysis service using CNN + Transformer neural networks"""

    def __init__(
        self,
        gpu_config: GPUConfigService,
        model_loader: ModelLoader,
        model_config: CNNTransformerConfig | None = None,
        cache_analyses: bool = True,
        max_cache_size: int = 1000,
    ):
        self.gpu_config = gpu_config
        self.model_loader = model_loader
        self.model_config = model_config or CNNTransformerConfig()
        self.cache_analyses = cache_analyses
        self.max_cache_size = max_cache_size

        # Initialize model and processor
        self.model: CNNTransformerModel | None = None
        self.data_processor: ContentDataProcessor | None = None
        self.device = self.gpu_config.device

        # Analysis cache
        self.analysis_cache: dict[str, dict] = {}
        self.cache_hits = 0
        self.cache_misses = 0

        # Health monitoring
        self.health_stats = {
            "analyses_performed": 0,
            "batch_analyses": 0,
            "risk_assessments": 0,
            "errors": 0,
            "last_analysis_time": None,
            "model_loaded": False,
        }

        # Task mappings for interpretation
        self.task_mappings = {
            "sentiment": {0: "positive", 1: "neutral", 2: "negative"},
            "toxicity": {0: "non_toxic", 1: "toxic"},
            "quality": {
                0: "very_low",
                1: "low",
                2: "medium",
                3: "high",
                4: "very_high",
            },
            "engagement": {0: "low", 1: "medium", 2: "high", 3: "viral"},
            "relevance": {
                0: "irrelevant",
                1: "somewhat_relevant",
                2: "highly_relevant",
            },
        }

        # Initialize components
        self._initialize_components()

        logger.info(f"📊 Content Analyzer Service initialized on device: {self.device}")

    def _initialize_components(self):
        """Initialize model and data processor"""
        try:
            # Initialize data processor
            self.data_processor = ContentDataProcessor(
                vocab_size=self.model_config.vocab_size,
                max_seq_length=self.model_config.max_seq_length,
                enable_preprocessing=True,
            )

            # Initialize model
            self.model = CNNTransformerModel(
                vocab_size=self.model_config.vocab_size,
                embed_dim=self.model_config.embed_dim,
                max_seq_length=self.model_config.max_seq_length,
                cnn_channels=self.model_config.cnn_channels,
                transformer_layers=self.model_config.transformer_layers,
                transformer_heads=self.model_config.transformer_heads,
                num_classes=self.model_config.num_classes,
                dropout_rate=self.model_config.dropout_rate,
            )

            # Move model to optimal device
            if self.model is not None:
                self.model = self.model.to(self.device)
                self.model.eval()

            self.health_stats["model_loaded"] = True
            logger.info("✅ Content analyzer components initialized successfully")

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Failed to initialize components: {e}")
            raise

    async def analyze_content(
        self,
        content: str | list[str],
        include_confidence: bool = True,
        include_features: bool = False,
        risk_assessment: bool = True,
    ) -> dict[str, Any]:
        """Analyze content for multiple aspects

        Args:
            content: Text content or list of texts
            include_confidence: Whether to include confidence scores
            include_features: Whether to include extracted features
            risk_assessment: Whether to perform risk assessment

        Returns:
            Dictionary with analysis results
        """
        try:
            # Check if service is properly initialized
            if self.model is None or self.data_processor is None:
                raise RuntimeError("Service not properly initialized")

            # Handle single text vs batch
            if isinstance(content, str):
                texts = [content]
                single_text = True
            else:
                texts = content
                single_text = False

            # Check cache for single text
            cache_key = None
            if single_text and self.cache_analyses:
                cache_key = self._generate_cache_key(texts[0], include_confidence, include_features)
                if cache_key in self.analysis_cache:
                    self.cache_hits += 1
                    logger.debug("📋 Returning cached analysis")
                    return self.analysis_cache[cache_key]

            self.cache_misses += 1

            # Validate inputs
            validation_result = self.data_processor.validate_inputs(texts)
            if not validation_result["valid"]:
                logger.warning(f"Input validation issues: {validation_result['issues']}")

            # Build vocabulary if not fitted (for demo - in practice would be pre-trained)
            if not self.data_processor.is_fitted:
                logger.info("📚 Building vocabulary from input texts...")
                vocab_stats = self.data_processor.build_vocabulary(texts)
                logger.info(f"✅ Vocabulary built: {vocab_stats}")

            # Process texts
            processed_batch = self.data_processor.process_batch(texts)

            # Move to device
            input_ids = processed_batch["input_ids"].to(self.device)
            attention_mask = processed_batch["attention_mask"].to(self.device)

            # Get predictions
            if self.model is not None:
                self.model.eval()

                if include_confidence:
                    predictions = self.model.predict_with_confidence(
                        input_ids, attention_mask, mc_samples=20
                    )
                else:
                    with torch.no_grad():
                        raw_predictions = self.model(input_ids, attention_mask)
                        predictions = {}
                        for task_name, task_pred in raw_predictions.items():
                            predictions[task_name] = {
                                "prediction": torch.softmax(task_pred, dim=-1),
                                "confidence": torch.ones(task_pred.size(0))
                                * 0.8,  # Default confidence
                            }

            # Process results
            result = await self._process_analysis_results(
                predictions=predictions,
                processed_batch=processed_batch,
                include_features=include_features,
                risk_assessment=risk_assessment,
                single_text=single_text,
            )

            # Update health stats
            self.health_stats["analyses_performed"] += 1
            self.health_stats["last_analysis_time"] = datetime.now().isoformat()
            if risk_assessment:
                self.health_stats["risk_assessments"] += 1

            # Cache result for single text
            if single_text and self.cache_analyses and cache_key:
                self._cache_analysis(cache_key, result)

            logger.info(f"📊 Content analysis completed for {len(texts)} text(s)")
            return result

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Content analysis failed: {e}")
            raise

    async def analyze_content_batch(
        self,
        content_batch: list[str],
        include_confidence: bool = True,
        batch_size: int = 32,
    ) -> list[dict[str, Any]]:
        """Analyze content in batches for better performance

        Args:
            content_batch: List of texts to analyze
            include_confidence: Whether to include confidence scores
            batch_size: Processing batch size

        Returns:
            List of analysis results
        """
        try:
            logger.info(f"🔄 Processing batch of {len(content_batch)} content analyses")

            # Process in chunks
            results = []
            for i in range(0, len(content_batch), batch_size):
                batch_texts = content_batch[i : i + batch_size]

                # Analyze batch
                batch_result = await self.analyze_content(
                    content=batch_texts,
                    include_confidence=include_confidence,
                    include_features=False,  # Skip features for batch processing
                    risk_assessment=True,
                )

                # Extract individual results
                if "batch_results" in batch_result:
                    results.extend(batch_result["batch_results"])
                else:
                    # Single result - wrap in list
                    results.append(batch_result)

            self.health_stats["batch_analyses"] += 1
            logger.info(f"✅ Batch analysis completed: {len(results)} results")

            return results

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Batch analysis failed: {e}")
            raise

    async def assess_content_risk(self, content: str) -> dict[str, Any]:
        """Perform comprehensive risk assessment on content

        Args:
            content: Text content to assess

        Returns:
            Risk assessment report
        """
        try:
            if self.model is None or self.data_processor is None:
                raise RuntimeError("Service not properly initialized")

            # Get full analysis
            analysis = await self.analyze_content(
                content=content,
                include_confidence=True,
                include_features=True,
                risk_assessment=True,
            )

            # Extract risk metrics
            content_scores = analysis.get("content_scores", {})
            confidence_metrics = analysis.get("confidence_metrics", {})

            # Calculate risk scores
            risk_scores = {}

            # Toxicity risk
            toxicity_data = content_scores.get("toxicity", {})
            if toxicity_data:
                all_probs = toxicity_data.get("all_probabilities", [0, 0])
                if isinstance(all_probs, list) and len(all_probs) >= 2:
                    toxic_prob = (
                        all_probs[1] if len(all_probs) > 1 else 0
                    )  # Toxic class probability
                else:
                    toxic_prob = 0.0
                risk_scores["toxicity"] = {
                    "score": float(toxic_prob),
                    "level": (
                        "high" if toxic_prob > 0.7 else "medium" if toxic_prob > 0.3 else "low"
                    ),
                    "confidence": float(
                        confidence_metrics.get("toxicity", {}).get("confidence", 0.5)
                    ),
                }

            # Quality risk (inverse of quality score)
            quality_data = content_scores.get("quality", {})
            if quality_data:
                quality_class = quality_data.get("predicted_class", 2)
                if isinstance(quality_class, list):
                    quality_class = quality_class[0] if quality_class else 2
                quality_risk = (4 - int(quality_class)) / 4  # Invert scale
                risk_scores["quality"] = {
                    "score": float(quality_risk),
                    "level": (
                        "high" if quality_risk > 0.6 else "medium" if quality_risk > 0.4 else "low"
                    ),
                    "quality_rating": self.task_mappings["quality"].get(
                        int(quality_class), "unknown"
                    ),
                }

            # Sentiment risk (negative sentiment)
            sentiment_data = content_scores.get("sentiment", {})
            if sentiment_data:
                all_probs = sentiment_data.get("all_probabilities", [0, 0, 0])
                if isinstance(all_probs, list) and len(all_probs) >= 3:
                    neg_prob = all_probs[2]  # Negative class
                else:
                    neg_prob = 0.0
                sentiment_class = sentiment_data.get("predicted_class", 1)
                if isinstance(sentiment_class, list):
                    sentiment_class = sentiment_class[0] if sentiment_class else 1
                risk_scores["sentiment"] = {
                    "score": float(neg_prob),
                    "level": ("high" if neg_prob > 0.7 else "medium" if neg_prob > 0.4 else "low"),
                    "sentiment": self.task_mappings["sentiment"].get(
                        int(sentiment_class), "unknown"
                    ),
                }

            # Overall risk assessment
            individual_risks = [risk_scores[task]["score"] for task in risk_scores]
            overall_risk = np.mean(individual_risks) if individual_risks else 0.0

            # Generate recommendations
            recommendations = []
            if risk_scores.get("toxicity", {}).get("score", 0) > 0.5:
                recommendations.append("Content may require moderation review due to toxicity")
            if risk_scores.get("quality", {}).get("score", 0) > 0.6:
                recommendations.append("Content quality is below acceptable standards")
            if risk_scores.get("sentiment", {}).get("score", 0) > 0.6:
                recommendations.append("Content has strongly negative sentiment")

            if not recommendations:
                recommendations.append("Content appears safe for publication")

            risk_report = {
                "overall_risk": {
                    "score": float(overall_risk),
                    "level": (
                        "high" if overall_risk > 0.6 else "medium" if overall_risk > 0.3 else "low"
                    ),
                    "safe_for_publication": overall_risk < 0.5,
                },
                "individual_risks": risk_scores,
                "recommendations": recommendations,
                "assessment_timestamp": datetime.now().isoformat(),
                "content_preview": (content[:100] + "..." if len(content) > 100 else content),
            }

            self.health_stats["risk_assessments"] += 1
            logger.info(f"🛡️ Risk assessment completed: {risk_report['overall_risk']['level']} risk")

            return risk_report

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Risk assessment failed: {e}")
            raise

    async def _process_analysis_results(
        self,
        predictions: dict[str, dict[str, torch.Tensor]],
        processed_batch: dict[str, Any],
        include_features: bool,
        risk_assessment: bool,
        single_text: bool,
    ) -> dict[str, Any]:
        """Process and format analysis results"""

        batch_size = len(processed_batch["original_texts"])

        # Process predictions for each text
        batch_results = []

        for i in range(batch_size):
            text_result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "content_scores": {},
                "confidence_metrics": {},
                "text_preview": (
                    processed_batch["original_texts"][i][:100] + "..."
                    if len(processed_batch["original_texts"][i]) > 100
                    else processed_batch["original_texts"][i]
                ),
            }

            # Process each task prediction
            for task_name, task_data in predictions.items():
                pred_probs = task_data["prediction"][i]
                confidence = (
                    task_data.get("confidence", torch.tensor(0.8))[i]
                    if hasattr(task_data.get("confidence", torch.tensor(0.8)), "__getitem__")
                    else task_data.get("confidence", torch.tensor(0.8))
                )

                # Get predicted class and probability
                pred_class = torch.argmax(pred_probs).item()
                pred_prob = torch.max(pred_probs).item()

                text_result["content_scores"][task_name] = {
                    "predicted_class": pred_class,
                    "predicted_label": self.task_mappings.get(task_name, {}).get(
                        int(pred_class), "unknown"
                    ),
                    "probability": pred_prob,
                    "all_probabilities": pred_probs.cpu().numpy().tolist(),
                }

                text_result["confidence_metrics"][task_name] = {
                    "confidence": (
                        confidence.item() if hasattr(confidence, "item") else float(confidence)
                    ),
                    "uncertainty": 1.0
                    - (confidence.item() if hasattr(confidence, "item") else float(confidence)),
                }

            # Add content features if requested
            if include_features:
                features = processed_batch["content_features"][i].cpu().numpy()
                feature_names = self.data_processor.content_features if self.data_processor else []
                text_result["content_features"] = {
                    name: float(value) for name, value in zip(feature_names, features, strict=False)
                }

                # Add complexity analysis
                if self.data_processor:
                    complexity = self.data_processor.analyze_text_complexity(
                        processed_batch["original_texts"][i]
                    )
                    text_result["complexity_analysis"] = complexity

            # Add risk assessment
            if risk_assessment:
                text_result["risk_indicators"] = self._calculate_risk_indicators(
                    text_result["content_scores"]
                )

            batch_results.append(text_result)

        # Return single result or batch results
        if single_text:
            result = batch_results[0]
            result["model_info"] = self.model.get_model_info() if self.model else None
            return result
        else:
            return {
                "success": True,
                "batch_size": batch_size,
                "batch_results": batch_results,
                "model_info": self.model.get_model_info() if self.model else None,
                "timestamp": datetime.now().isoformat(),
            }

    def _calculate_risk_indicators(self, content_scores: dict[str, dict]) -> dict[str, str]:
        """Calculate risk indicators from content scores"""
        risk_indicators = {}

        # Toxicity risk
        toxicity_data = content_scores.get("toxicity", {})
        if toxicity_data and "all_probabilities" in toxicity_data:
            toxic_prob = toxicity_data["all_probabilities"][1]  # Toxic class
            risk_indicators["toxicity_risk"] = (
                "high" if toxic_prob > 0.7 else "medium" if toxic_prob > 0.3 else "low"
            )

        # Quality risk
        quality_data = content_scores.get("quality", {})
        if quality_data and "predicted_class" in quality_data:
            quality_class = quality_data["predicted_class"]
            risk_indicators["quality_risk"] = (
                "high" if quality_class < 2 else "medium" if quality_class < 3 else "low"
            )

        # Sentiment risk
        sentiment_data = content_scores.get("sentiment", {})
        if sentiment_data and "predicted_class" in sentiment_data:
            sentiment_class = sentiment_data["predicted_class"]
            risk_indicators["sentiment_risk"] = (
                "high" if sentiment_class == 2 else "low"
            )  # 2 = negative

        return risk_indicators

    def _generate_cache_key(
        self, content: str, include_confidence: bool, include_features: bool
    ) -> str:
        """Generate cache key for analysis"""
        content_hash = hash(content)
        return f"content_{content_hash}_{include_confidence}_{include_features}"

    def _cache_analysis(self, cache_key: str, result: dict[str, Any]):
        """Cache analysis result"""
        if len(self.analysis_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.analysis_cache))
            del self.analysis_cache[oldest_key]

        self.analysis_cache[cache_key] = result

    def get_service_health(self) -> dict[str, Any]:
        """Get service health and statistics"""
        cache_efficiency = (
            self.cache_hits / (self.cache_hits + self.cache_misses)
            if (self.cache_hits + self.cache_misses) > 0
            else 0
        )

        return {
            "service_name": "ContentAnalyzerService",
            "status": (
                "healthy"
                if self.health_stats["model_loaded"] and self.model is not None
                else "unhealthy"
            ),
            "device": str(self.device),
            "model_info": (self.model.get_model_info() if self.model is not None else None),
            "health_stats": self.health_stats.copy(),
            "cache_stats": {
                "enabled": self.cache_analyses,
                "size": len(self.analysis_cache),
                "max_size": self.max_cache_size,
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "efficiency": cache_efficiency,
            },
            "processor_stats": (
                self.data_processor.get_processor_stats()
                if self.data_processor is not None
                else None
            ),
            "timestamp": datetime.now().isoformat(),
        }

    def clear_cache(self):
        """Clear analysis cache"""
        self.analysis_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("🧹 Analysis cache cleared")

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
                if self.model is not None:
                    self.model.eval()

                # Load processor if available
                if "data_processor" in model_info:
                    self.data_processor = model_info["data_processor"]

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
                "service_stats": self.get_service_health(),
            }

            if include_processor and self.data_processor is not None:
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
