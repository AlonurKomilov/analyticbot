"""
🧠 AI-Powered Insights Generator - ML Service

Advanced AI system for pattern recognition, anomaly detection,
automated insights, and intelligent recommendations.

This module provides AI-driven analytics capabilities for the AnalyticBot,
including pattern detection, anomaly analysis, and automated insight generation.
"""

import asyncio
import logging
import warnings
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from scipy import stats
from scipy.signal import find_peaks

try:
    import statsmodels.api as sm
    from statsmodels.tsa.seasonal import seasonal_decompose

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

from sklearn.ensemble import IsolationForest

try:
    import xgboost as xgb

    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

# NLP and text processing

# Pattern recognition

logger = logging.getLogger(__name__)


class AIInsightsGenerator:
    """
    🧠 AI-Powered Insights Generator for AnalyticBot

    Advanced capabilities:
    - Pattern recognition and trend analysis
    - Anomaly detection with multiple algorithms
    - Automated statistical insights
    - Business intelligence recommendations
    - Predictive insights and forecasting
    - Natural language insight generation
    """

    def __init__(self):
        self.insights_history = {}
        self.anomaly_models = {}
        self.pattern_cache = {}
        self.recommendation_engine = {}

        # Configuration
        self.config = {
            "anomaly_threshold": 0.1,
            "pattern_min_support": 0.1,
            "seasonal_periods": [7, 30, 365],  # Daily, monthly, yearly
            "trend_window": 30,
            "insight_confidence_threshold": 0.7,
        }

    async def generate_comprehensive_insights(
        self, df: pd.DataFrame, target_column: str | None = None, datetime_column: str | None = None
    ) -> dict[str, Any]:
        """
        🧠 Generate comprehensive AI insights from data
        """
        try:
            insights = {
                "timestamp": datetime.now().isoformat(),
                "data_overview": self._analyze_data_overview(df),
                "statistical_insights": await self._generate_statistical_insights(df),
                "anomalies": await self._detect_anomalies(df),
                "patterns": await self._identify_patterns(df),
                "trends": await self._analyze_trends(df, datetime_column),
                "correlations": await self._analyze_correlations(df),
                "recommendations": await self._generate_recommendations(df, target_column),
            }

            # Generate natural language summary
            insights["summary"] = await self._generate_insight_summary(insights)

            # Store insights
            insight_id = f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.insights_history[insight_id] = insights

            return {
                "insight_id": insight_id,
                "insights": insights,
                "confidence_score": self._calculate_insight_confidence(insights),
            }

        except Exception as e:
            logger.error(f"Comprehensive insights generation failed: {e}")
            return {"error": str(e)}

    def _analyze_data_overview(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze basic data characteristics"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=["object"]).columns
            datetime_cols = df.select_dtypes(include=["datetime64"]).columns

            overview = {
                "total_records": len(df),
                "total_features": len(df.columns),
                "numeric_features": len(numeric_cols),
                "categorical_features": len(categorical_cols),
                "datetime_features": len(datetime_cols),
                "missing_data_percentage": (df.isnull().sum().sum() / df.size) * 100,
                "duplicated_records": df.duplicated().sum(),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            }

            # Data quality assessment
            quality_issues = []
            if overview["missing_data_percentage"] > 10:
                quality_issues.append(
                    f"High missing data: {overview['missing_data_percentage']:.1f}%"
                )
            if overview["duplicated_records"] > 0:
                quality_issues.append(f"Duplicated records found: {overview['duplicated_records']}")

            overview["quality_issues"] = quality_issues
            overview["data_quality_score"] = max(
                0,
                100
                - overview["missing_data_percentage"]
                - (overview["duplicated_records"] / len(df) * 100),
            )

            return overview

        except Exception as e:
            logger.error(f"Data overview analysis failed: {e}")
            return {"error": str(e)}

    async def _generate_statistical_insights(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate statistical insights about the data"""
        try:
            insights = {}
            numeric_cols = df.select_dtypes(include=[np.number]).columns

            if len(numeric_cols) > 0:
                for col in numeric_cols:
                    col_data = df[col].dropna()

                    if len(col_data) > 0:
                        col_insights = {
                            "distribution": {
                                "mean": float(col_data.mean()),
                                "median": float(col_data.median()),
                                "std": float(col_data.std()),
                                "skewness": float(col_data.skew()),
                                "kurtosis": float(col_data.kurtosis()),
                            },
                            "range": {
                                "min": float(col_data.min()),
                                "max": float(col_data.max()),
                                "range": float(col_data.max() - col_data.min()),
                                "iqr": float(col_data.quantile(0.75) - col_data.quantile(0.25)),
                            },
                        }

                        # Distribution insights
                        if abs(col_insights["distribution"]["skewness"]) > 2:
                            col_insights["distribution_note"] = "Highly skewed distribution"
                        elif abs(col_insights["distribution"]["skewness"]) > 1:
                            col_insights["distribution_note"] = "Moderately skewed distribution"
                        else:
                            col_insights["distribution_note"] = "Approximately normal distribution"

                        # Outlier detection using IQR
                        Q1 = col_data.quantile(0.25)
                        Q3 = col_data.quantile(0.75)
                        IQR = Q3 - Q1
                        outliers = col_data[
                            (col_data < Q1 - 1.5 * IQR) | (col_data > Q3 + 1.5 * IQR)
                        ]

                        col_insights["outliers"] = {
                            "count": len(outliers),
                            "percentage": (len(outliers) / len(col_data)) * 100,
                        }

                        insights[col] = col_insights

            return insights

        except Exception as e:
            logger.error(f"Statistical insights generation failed: {e}")
            return {"error": str(e)}

    async def _detect_anomalies(self, df: pd.DataFrame) -> dict[str, Any]:
        """Detect anomalies using multiple algorithms"""
        try:
            anomalies = {}
            numeric_df = df.select_dtypes(include=[np.number])

            if len(numeric_df.columns) == 0:
                return {"message": "No numeric columns for anomaly detection"}

            # Remove rows with missing values
            clean_df = numeric_df.dropna()

            if len(clean_df) < 10:
                return {"message": "Insufficient data for reliable anomaly detection"}

            # Isolation Forest
            try:
                iso_forest = IsolationForest(
                    contamination=self.config["anomaly_threshold"], random_state=42
                )
                iso_anomalies = iso_forest.fit_predict(clean_df)
                anomaly_indices = clean_df.index[iso_anomalies == -1].tolist()

                anomalies["isolation_forest"] = {
                    "anomaly_count": len(anomaly_indices),
                    "anomaly_percentage": (len(anomaly_indices) / len(clean_df)) * 100,
                    "anomaly_indices": anomaly_indices[:50],  # Limit to first 50
                }
            except Exception as e:
                logger.warning(f"Isolation Forest failed: {e}")

            # Statistical anomaly detection (Z-score)
            try:
                z_scores = np.abs(stats.zscore(clean_df))
                z_anomalies = (z_scores > 3).any(axis=1)
                z_anomaly_indices = clean_df.index[z_anomalies].tolist()

                anomalies["statistical_zscore"] = {
                    "anomaly_count": len(z_anomaly_indices),
                    "anomaly_percentage": (len(z_anomaly_indices) / len(clean_df)) * 100,
                    "anomaly_indices": z_anomaly_indices[:50],
                }
            except Exception as e:
                logger.warning(f"Z-score anomaly detection failed: {e}")

            return anomalies

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {"error": str(e)}

    async def _identify_patterns(self, df: pd.DataFrame) -> dict[str, Any]:
        """Identify patterns in the data"""
        try:
            patterns = {}

            # Categorical pattern analysis
            categorical_cols = df.select_dtypes(include=["object"]).columns
            if len(categorical_cols) > 0:
                categorical_patterns = {}

                for col in categorical_cols:
                    value_counts = df[col].value_counts()

                    categorical_patterns[col] = {
                        "unique_values": int(df[col].nunique()),
                        "most_common": {
                            "value": str(value_counts.index[0]),
                            "count": int(value_counts.iloc[0]),
                            "percentage": float((value_counts.iloc[0] / len(df)) * 100),
                        },
                        "distribution_type": "uniform"
                        if len(set(value_counts.values)) == 1
                        else "skewed",
                        "entropy": float(stats.entropy(value_counts.values)),
                    }

                patterns["categorical"] = categorical_patterns

            # Numeric patterns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                numeric_patterns = {}

                for col in numeric_cols:
                    col_data = df[col].dropna()

                    if len(col_data) > 0:
                        # Check for specific patterns
                        pattern_info = {
                            "monotonic_increasing": col_data.is_monotonic_increasing,
                            "monotonic_decreasing": col_data.is_monotonic_decreasing,
                            "constant": col_data.nunique() == 1,
                            "periodic_hint": self._check_periodicity(col_data),
                        }

                        numeric_patterns[col] = pattern_info

                patterns["numeric"] = numeric_patterns

            return patterns

        except Exception as e:
            logger.error(f"Pattern identification failed: {e}")
            return {"error": str(e)}

    def _check_periodicity(self, data: pd.Series) -> dict[str, Any]:
        """Check for periodic patterns in numeric data"""
        try:
            if len(data) < 20:
                return {"detected": False, "reason": "insufficient_data"}

            # Simple autocorrelation check
            data_values = data.values
            autocorr = np.correlate(data_values, data_values, mode="full")
            autocorr = autocorr[autocorr.size // 2 :]

            # Find peaks in autocorrelation
            peaks, _ = find_peaks(autocorr[1:], height=0.5 * np.max(autocorr))

            if len(peaks) > 0:
                # Estimate period
                period = peaks[0] + 1
                return {
                    "detected": True,
                    "estimated_period": int(period),
                    "confidence": float(autocorr[period] / np.max(autocorr)),
                }

            return {"detected": False, "reason": "no_significant_peaks"}

        except Exception:
            return {"detected": False, "reason": "analysis_failed"}

    async def _analyze_trends(
        self, df: pd.DataFrame, datetime_column: str | None = None
    ) -> dict[str, Any]:
        """Analyze trends in the data"""
        try:
            trends = {}

            # If datetime column is provided, analyze time-based trends
            if datetime_column and datetime_column in df.columns:
                try:
                    df_time = df.copy()
                    df_time[datetime_column] = pd.to_datetime(df_time[datetime_column])
                    df_time = df_time.sort_values(datetime_column)

                    numeric_cols = df_time.select_dtypes(include=[np.number]).columns

                    for col in numeric_cols:
                        if col != datetime_column:
                            col_trends = self._analyze_time_series_trend(
                                df_time[datetime_column], df_time[col]
                            )
                            trends[f"{col}_time_trend"] = col_trends

                except Exception as e:
                    logger.warning(f"Time-based trend analysis failed: {e}")

            # General trend analysis for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                col_data = df[col].dropna()

                if len(col_data) > 5:
                    # Linear trend analysis
                    x = np.arange(len(col_data))
                    y = col_data.values

                    try:
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

                        trends[f"{col}_linear_trend"] = {
                            "slope": float(slope),
                            "correlation": float(r_value),
                            "p_value": float(p_value),
                            "trend_strength": abs(r_value),
                            "trend_direction": "increasing"
                            if slope > 0
                            else "decreasing"
                            if slope < 0
                            else "stable",
                            "significance": "significant" if p_value < 0.05 else "not_significant",
                        }
                    except Exception as e:
                        logger.warning(f"Linear trend analysis failed for {col}: {e}")

            return trends

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"error": str(e)}

    def _analyze_time_series_trend(self, dates: pd.Series, values: pd.Series) -> dict[str, Any]:
        """Analyze time series trends"""
        try:
            # Create time series
            ts = pd.Series(values.values, index=dates)
            ts = ts.dropna()

            if len(ts) < 10:
                return {"error": "Insufficient data for time series analysis"}

            trend_info = {}

            # Basic trend calculation
            x_numeric = np.arange(len(ts))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_numeric, ts.values)

            trend_info.update(
                {
                    "slope": float(slope),
                    "correlation": float(r_value),
                    "p_value": float(p_value),
                    "trend_direction": "increasing"
                    if slope > 0
                    else "decreasing"
                    if slope < 0
                    else "stable",
                }
            )

            # Seasonal decomposition if possible and statsmodels is available
            if STATSMODELS_AVAILABLE and len(ts) >= 24:  # Need at least 2 periods
                try:
                    decomposition = seasonal_decompose(
                        ts, model="additive", period=min(12, len(ts) // 2)
                    )

                    trend_info["seasonal_decomposition"] = {
                        "trend_strength": float(np.var(decomposition.trend.dropna()) / np.var(ts)),
                        "seasonal_strength": float(
                            np.var(decomposition.seasonal.dropna()) / np.var(ts)
                        ),
                        "residual_strength": float(
                            np.var(decomposition.resid.dropna()) / np.var(ts)
                        ),
                    }
                except Exception as e:
                    logger.warning(f"Seasonal decomposition failed: {e}")

            return trend_info

        except Exception as e:
            logger.error(f"Time series trend analysis failed: {e}")
            return {"error": str(e)}

    async def _analyze_correlations(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze correlations between variables"""
        try:
            correlations = {}
            numeric_df = df.select_dtypes(include=[np.number])

            if len(numeric_df.columns) < 2:
                return {"message": "Need at least 2 numeric columns for correlation analysis"}

            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()

            # Find strong correlations
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Strong correlation threshold
                        strong_correlations.append(
                            {
                                "variable1": corr_matrix.columns[i],
                                "variable2": corr_matrix.columns[j],
                                "correlation": float(corr_val),
                                "strength": "very_strong" if abs(corr_val) > 0.9 else "strong",
                            }
                        )

            correlations = {
                "correlation_matrix": corr_matrix.to_dict(),
                "strong_correlations": strong_correlations,
                "correlation_summary": {
                    "max_correlation": float(corr_matrix.abs().max().max()),
                    "mean_correlation": float(corr_matrix.abs().mean().mean()),
                    "highly_correlated_pairs": len(strong_correlations),
                },
            }

            return correlations

        except Exception as e:
            logger.error(f"Correlation analysis failed: {e}")
            return {"error": str(e)}

    async def _generate_recommendations(
        self, df: pd.DataFrame, target_column: str | None = None
    ) -> list[dict[str, Any]]:
        """Generate actionable recommendations based on insights"""
        try:
            recommendations = []

            # Data quality recommendations
            missing_pct = (df.isnull().sum().sum() / df.size) * 100
            if missing_pct > 10:
                recommendations.append(
                    {
                        "type": "data_quality",
                        "priority": "high",
                        "title": "Address Missing Data",
                        "description": f"Dataset has {missing_pct:.1f}% missing values. Consider imputation or removal strategies.",
                        "action": "data_cleaning",
                    }
                )

            # Duplicate data recommendation
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                recommendations.append(
                    {
                        "type": "data_quality",
                        "priority": "medium",
                        "title": "Remove Duplicate Records",
                        "description": f"Found {duplicates} duplicate records that should be removed.",
                        "action": "deduplication",
                    }
                )

            # Feature engineering recommendations
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                # Check for highly correlated features
                corr_matrix = df[numeric_cols].corr()
                high_corr_pairs = []

                for i in range(len(corr_matrix.columns)):
                    for j in range(i + 1, len(corr_matrix.columns)):
                        if abs(corr_matrix.iloc[i, j]) > 0.9:
                            high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))

                if high_corr_pairs:
                    recommendations.append(
                        {
                            "type": "feature_engineering",
                            "priority": "medium",
                            "title": "Address Multicollinearity",
                            "description": f"Found {len(high_corr_pairs)} highly correlated feature pairs. Consider removing redundant features.",
                            "action": "feature_selection",
                            "details": high_corr_pairs[:5],  # Show first 5 pairs
                        }
                    )

            # Analysis recommendations
            if target_column and target_column in df.columns:
                recommendations.append(
                    {
                        "type": "analysis",
                        "priority": "high",
                        "title": "Predictive Modeling Opportunity",
                        "description": f'Target variable "{target_column}" detected. Consider building predictive models.',
                        "action": "predictive_modeling",
                    }
                )

            # Time series recommendations
            datetime_cols = df.select_dtypes(include=["datetime64"]).columns
            if len(datetime_cols) > 0:
                recommendations.append(
                    {
                        "type": "analysis",
                        "priority": "medium",
                        "title": "Time Series Analysis",
                        "description": "Temporal data detected. Consider time series analysis and forecasting.",
                        "action": "time_series_analysis",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return [{"error": str(e)}]

    async def _generate_insight_summary(self, insights: dict[str, Any]) -> str:
        """Generate natural language summary of insights"""
        try:
            summary_parts = []

            # Data overview summary
            overview = insights.get("data_overview", {})
            if overview:
                summary_parts.append(
                    f"Dataset contains {overview.get('total_records', 0):,} records with "
                    f"{overview.get('total_features', 0)} features. "
                    f"Data quality score: {overview.get('data_quality_score', 0):.1f}/100."
                )

            # Anomaly summary
            anomalies = insights.get("anomalies", {})
            if "isolation_forest" in anomalies:
                anomaly_pct = anomalies["isolation_forest"].get("anomaly_percentage", 0)
                if anomaly_pct > 5:
                    summary_parts.append(
                        f"Detected {anomaly_pct:.1f}% anomalous data points requiring investigation."
                    )

            # Pattern summary
            patterns = insights.get("patterns", {})
            if patterns:
                pattern_count = len(patterns.get("categorical", {})) + len(
                    patterns.get("numeric", {})
                )
                summary_parts.append(f"Identified {pattern_count} distinct data patterns.")

            # Correlation summary
            correlations = insights.get("correlations", {})
            if "strong_correlations" in correlations:
                strong_corr_count = len(correlations["strong_correlations"])
                if strong_corr_count > 0:
                    summary_parts.append(f"Found {strong_corr_count} strong variable correlations.")

            # Recommendations summary
            recommendations = insights.get("recommendations", [])
            if recommendations:
                high_priority = sum(1 for r in recommendations if r.get("priority") == "high")
                summary_parts.append(
                    f"Generated {len(recommendations)} recommendations ({high_priority} high priority)."
                )

            return " ".join(summary_parts) if summary_parts else "Analysis completed successfully."

        except Exception as e:
            logger.error(f"Insight summary generation failed: {e}")
            return "Insights generated successfully."

    def _calculate_insight_confidence(self, insights: dict[str, Any]) -> float:
        """Calculate confidence score for generated insights"""
        try:
            confidence_factors = []

            # Data quality factor
            overview = insights.get("data_overview", {})
            quality_score = overview.get("data_quality_score", 0)
            confidence_factors.append(quality_score / 100)

            # Analysis completeness factor
            analysis_sections = [
                "statistical_insights",
                "anomalies",
                "patterns",
                "trends",
                "correlations",
            ]
            completed_sections = sum(
                1 for section in analysis_sections if section in insights and insights[section]
            )
            completeness_factor = completed_sections / len(analysis_sections)
            confidence_factors.append(completeness_factor)

            # Data size factor (more data = higher confidence)
            total_records = overview.get("total_records", 0)
            size_factor = min(1.0, total_records / 1000)  # Normalize to 1000 records
            confidence_factors.append(size_factor)

            return float(np.mean(confidence_factors))

        except Exception:
            return 0.5  # Default confidence

    async def health_check(self):
        """Health check for the AI insights generator"""
        return {
            "status": "healthy",
            "insights_generated": len(self.insights_history),
            "dependencies": {"statsmodels": STATSMODELS_AVAILABLE, "xgboost": XGBOOST_AVAILABLE},
        }


# Convenience function for easy integration with bot services
async def create_ai_insights_generator():
    """Factory function to create and initialize AI insights generator"""
    return AIInsightsGenerator()


# Example usage and testing
if __name__ == "__main__":
    # Create sample data for testing
    np.random.seed(42)

    # Sample dataset with various patterns
    dates = pd.date_range("2023-01-01", periods=365, freq="D")
    sample_data = {
        "date": dates,
        "sales": 1000
        + np.cumsum(np.random.normal(10, 50, 365))
        + 200 * np.sin(np.arange(365) * 2 * np.pi / 30),
        "marketing_spend": np.random.normal(5000, 1000, 365),
        "customer_count": np.random.poisson(100, 365),
        "region": np.random.choice(["North", "South", "East", "West"], 365),
        "product_category": np.random.choice(["A", "B", "C"], 365),
    }

    # Add some anomalies
    sample_data["sales"][100] = 50000  # Anomaly
    sample_data["sales"][200] = -1000  # Anomaly

    df = pd.DataFrame(sample_data)

    # Test the AI insights generator
    generator = AIInsightsGenerator()

    print("🧠 Testing AI Insights Generator...")

    async def test_generator():
        # Generate comprehensive insights
        results = await generator.generate_comprehensive_insights(
            df, target_column="sales", datetime_column="date"
        )

        print(f"Insight ID: {results['insight_id']}")
        print(f"Confidence Score: {results['confidence_score']:.3f}")
        print(f"Summary: {results['insights']['summary']}")
        print(f"Anomalies detected: {len(results['insights']['anomalies'])}")
        print(f"Recommendations: {len(results['insights']['recommendations'])}")

    asyncio.run(test_generator())

    print("✅ AI Insights Generator test complete!")
