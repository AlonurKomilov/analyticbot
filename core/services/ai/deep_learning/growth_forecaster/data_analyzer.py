"""
Data Analyzer Service
====================

Microservice responsible for data processing and growth pattern analysis.
Handles data preparation, validation, and pattern classification.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

from .models import (
    DataAnalyzerProtocol,
    GrowthPattern,
    HealthMetrics,
    ServiceHealth,
)

logger = logging.getLogger(__name__)


class DataAnalyzer(DataAnalyzerProtocol):
    """
    Data processing and analysis service for growth forecasting.

    Single responsibility: Data preparation and pattern analysis.
    """

    def __init__(self, data_processor: Any):  # GrowthDataProcessor
        self.data_processor = data_processor

        # Health tracking
        self.health_metrics = HealthMetrics()

        logger.info("📊 Data Analyzer initialized")

    def analyze_patterns(self, data: pd.DataFrame) -> dict[str, Any]:
        """
        Analyze growth patterns and trends in historical data

        Args:
            data: Historical growth data

        Returns:
            Comprehensive pattern analysis results
        """
        try:
            logger.info("📈 Starting growth pattern analysis")

            # Prepare and validate data
            df = self.prepare_data(data)

            # Check if data processor is available
            if self.data_processor is None:
                raise RuntimeError("Data processor not initialized")

            # Engineer features for analysis
            processed_df = self.data_processor.engineer_growth_features(df)

            # Calculate basic growth statistics
            growth_stats = self._calculate_growth_statistics(processed_df)

            # Classify growth patterns
            pattern_classification = self.classify_patterns(processed_df)

            # Data quality assessment
            quality_assessment = self._assess_data_quality(df)

            # Feature importance analysis
            feature_importance = self._get_feature_importance()

            result = {
                "growth_statistics": growth_stats,
                "pattern_classification": {
                    "pattern_type": pattern_classification.pattern_type,
                    "confidence": pattern_classification.confidence,
                    "characteristics": pattern_classification.characteristics,
                    "recommendations": pattern_classification.recommendations,
                },
                "data_quality": quality_assessment,
                "feature_importance": feature_importance,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "data_points_analyzed": len(df),
            }

            # Update health metrics
            self.health_metrics.successful_predictions += 1
            self.health_metrics.last_prediction_time = datetime.utcnow()

            logger.info(f"✅ Pattern analysis completed for {len(df)} data points")
            return result

        except Exception as e:
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Pattern analysis failed: {e}")
            raise

    def prepare_data(self, raw_data: pd.DataFrame | list[dict] | dict) -> pd.DataFrame:
        """
        Prepare and validate input data for analysis

        Args:
            raw_data: Raw input data in various formats

        Returns:
            Standardized and validated DataFrame
        """
        try:
            logger.debug("🔧 Preparing input data")

            # Convert to DataFrame
            if isinstance(raw_data, pd.DataFrame):
                df = raw_data.copy()
            elif isinstance(raw_data, list):
                df = pd.DataFrame(raw_data)
            elif isinstance(raw_data, dict):
                df = pd.DataFrame([raw_data])
            else:
                raise ValueError(f"Unsupported data type: {type(raw_data)}")

            # Basic data validation
            if df.empty:
                raise ValueError("Input data is empty")

            if len(df) < 3:
                raise ValueError("Insufficient data points (minimum 3 required)")

            # Ensure required columns exist or can be inferred
            if "value" not in df.columns and "growth" not in df.columns:
                # Try to infer the value column
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) == 0:
                    raise ValueError("No numeric columns found for analysis")
                df["value"] = df[numeric_columns[0]]

            # Handle missing values
            if df.isnull().any().any():
                logger.warning("⚠️ Missing values detected, applying forward fill")
                df = df.ffill().bfill()

            # Sort by timestamp if available
            timestamp_columns = ["timestamp", "date", "time"]
            for col in timestamp_columns:
                if col in df.columns:
                    df = df.sort_values(col)
                    break

            logger.debug(f"✅ Data prepared: {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"❌ Data preparation failed: {e}")
            raise

    def classify_patterns(self, data: pd.DataFrame) -> GrowthPattern:
        """
        Classify growth patterns in the data

        Args:
            data: Processed growth data

        Returns:
            Growth pattern classification result
        """
        try:
            logger.debug("🔍 Classifying growth patterns")

            if "growth_rate" not in data.columns:
                raise ValueError("Growth rate column not found in processed data")

            growth_rates = np.array(data["growth_rate"].values)

            # Calculate pattern metrics
            mean_growth = np.mean(growth_rates)
            std_growth = np.std(growth_rates)
            cv = std_growth / abs(mean_growth) if mean_growth != 0 else float("inf")

            # Trend analysis
            self._calculate_trend_strength(growth_rates)

            # Pattern classification logic
            if mean_growth > 0.1 and cv < 0.5:
                pattern_type = "steady_growth"
                confidence = 0.9
                characteristics = {
                    "direction": "positive",
                    "stability": "high",
                    "predictability": "high",
                }
                recommendations = [
                    "Continue current growth strategies",
                    "Consider scaling operations",
                    "Monitor for potential ceiling effects",
                ]
            elif mean_growth > 0.05 and cv < 1.0:
                pattern_type = "moderate_growth"
                confidence = 0.8
                characteristics = {
                    "direction": "positive",
                    "stability": "medium",
                    "predictability": "medium",
                }
                recommendations = [
                    "Optimize growth consistency",
                    "Identify and reduce volatility sources",
                    "Plan for sustainable expansion",
                ]
            elif abs(mean_growth) < 0.02:
                pattern_type = "stagnant"
                confidence = 0.85
                characteristics = {
                    "direction": "neutral",
                    "stability": "high" if cv < 0.3 else "low",
                    "predictability": "medium",
                }
                recommendations = [
                    "Investigate growth barriers",
                    "Consider new growth strategies",
                    "Analyze competitive landscape",
                ]
            elif cv > 2.0:
                pattern_type = "volatile"
                confidence = 0.75
                characteristics = {
                    "direction": "positive" if mean_growth > 0 else "negative",
                    "stability": "low",
                    "predictability": "low",
                }
                recommendations = [
                    "Focus on stabilizing operations",
                    "Identify volatility causes",
                    "Implement risk management strategies",
                ]
            elif mean_growth < -0.05:
                pattern_type = "declining"
                confidence = 0.8
                characteristics = {
                    "direction": "negative",
                    "stability": "medium",
                    "predictability": "medium",
                }
                recommendations = [
                    "Urgent intervention required",
                    "Analyze decline causes",
                    "Implement recovery strategies",
                ]
            else:
                pattern_type = "mixed"
                confidence = 0.6
                characteristics = {
                    "direction": "mixed",
                    "stability": "variable",
                    "predictability": "low",
                }
                recommendations = [
                    "Require deeper analysis",
                    "Consider longer time horizon",
                    "Segment analysis by periods",
                ]

            return GrowthPattern(
                pattern_type=pattern_type,
                confidence=confidence,
                characteristics=characteristics,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"❌ Pattern classification failed: {e}")
            return GrowthPattern(
                pattern_type="unknown",
                confidence=0.0,
                characteristics={},
                recommendations=["Analysis failed - check data quality"],
            )

    def get_health(self) -> ServiceHealth:
        """Get data analyzer health status"""
        try:
            is_healthy = (
                self.data_processor is not None
                and self.health_metrics.failed_predictions
                < self.health_metrics.successful_predictions
            )

            return ServiceHealth(
                service_name="data_analyzer",
                is_healthy=is_healthy,
                metrics=self.health_metrics,
                last_check=datetime.utcnow(),
            )

        except Exception as e:
            return ServiceHealth(
                service_name="data_analyzer",
                is_healthy=False,
                metrics=HealthMetrics(),
                error_message=str(e),
            )

    # Private helper methods

    def _calculate_growth_statistics(self, processed_df: pd.DataFrame) -> dict[str, Any]:
        """Calculate comprehensive growth statistics"""
        try:
            stats = {}

            if "growth_rate" in processed_df.columns:
                growth_rates = processed_df["growth_rate"]
                stats.update(
                    {
                        "mean_growth": float(growth_rates.mean()),
                        "std_growth": float(growth_rates.std()),
                        "min_growth": float(growth_rates.min()),
                        "max_growth": float(growth_rates.max()),
                        "volatility": (
                            float(growth_rates.std() / abs(growth_rates.mean()))
                            if growth_rates.mean() != 0
                            else float("inf")
                        ),
                    }
                )

            if "trend_strength" in processed_df.columns:
                stats["trend_strength"] = float(processed_df["trend_strength"].mean())

            if "momentum" in processed_df.columns:
                stats["momentum"] = float(
                    processed_df["momentum"].iloc[-1] if len(processed_df) > 0 else 0
                )

            if "velocity" in processed_df.columns:
                stats["recent_velocity"] = float(processed_df["velocity"].tail(5).mean())

            if "acceleration" in processed_df.columns:
                stats["acceleration"] = float(processed_df["acceleration"].tail(5).mean())

            return stats

        except Exception as e:
            logger.error(f"❌ Statistics calculation failed: {e}")
            return {}

    def _assess_data_quality(self, df: pd.DataFrame) -> dict[str, Any]:
        """Assess data quality and return validation results"""
        try:
            if self.data_processor and hasattr(self.data_processor, "validate_data"):
                return self.data_processor.validate_data(df)

            # Basic quality assessment
            return {
                "valid": True,
                "issues": [],
                "data_points": len(df),
                "completeness": 1.0 - df.isnull().sum().sum() / (len(df) * len(df.columns)),
                "quality_score": 0.8,  # Default score
            }

        except Exception as e:
            logger.error(f"❌ Data quality assessment failed: {e}")
            return {"valid": False, "issues": [str(e)]}

    def _get_feature_importance(self) -> dict[str, float]:
        """Get feature importance weights from data processor"""
        try:
            if self.data_processor and hasattr(
                self.data_processor, "get_feature_importance_weights"
            ):
                return self.data_processor.get_feature_importance_weights()

            # Default feature importance
            return {
                "growth_rate": 0.4,
                "trend_strength": 0.3,
                "momentum": 0.2,
                "volatility": 0.1,
            }

        except Exception as e:
            logger.error(f"❌ Feature importance extraction failed: {e}")
            return {}

    def _calculate_trend_strength(self, values: np.ndarray) -> float:
        """Calculate trend strength in the data"""
        try:
            if len(values) < 3:
                return 0.0

            # Simple linear trend calculation
            x = np.arange(len(values))
            correlation = np.corrcoef(x, values)[0, 1]

            return abs(correlation) if not np.isnan(correlation) else 0.0

        except Exception as e:
            logger.error(f"❌ Trend strength calculation failed: {e}")
            return 0.0
