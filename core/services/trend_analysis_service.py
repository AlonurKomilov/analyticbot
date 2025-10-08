"""
Trend Analysis Service - Advanced Trend Detection and Forecasting
Extracted from AnalyticsFusionService for better separation of concerns
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np
from scipy.stats import ttest_ind

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Specialized service for advanced trend analysis, anomaly detection, and forecasting"""

    def __init__(self, channel_daily_repo, post_repo, metrics_repo):
        self._daily = channel_daily_repo
        self._posts = post_repo
        self._metrics = metrics_repo

    async def analyze_advanced_trends(
        self,
        channel_id: int,
        metric: str = "views",
        days: int = 60,
        trend_analysis_type: str = "comprehensive",
    ) -> dict:
        """
        📈 Advanced Trend Analysis with Anomaly Detection

        Performs sophisticated trend analysis using multiple algorithms:
        - Seasonal decomposition
        - Change point detection
        - Anomaly identification
        - Forecast trends with confidence intervals

        Args:
            channel_id: Target channel ID
            metric: Metric to analyze ('views', 'growth', 'engagement')
            days: Historical period for analysis
            trend_analysis_type: Type of analysis ('basic', 'comprehensive', 'predictive')

        Returns:
            Advanced trend analysis with anomalies, change points, and forecasts
        """
        try:
            now = datetime.now()
            start_date = now - timedelta(days=days)

            # Get time series data
            if metric == "views":
                data_points = await self._get_daily_views(channel_id, start_date, now)
            elif metric == "growth":
                data_points = await self._get_daily_growth(channel_id, start_date, now)
            elif metric == "engagement":
                data_points = await self._get_daily_engagement(channel_id, start_date, now)
            else:
                raise ValueError(f"Unsupported metric: {metric}")

            if len(data_points) < 14:
                return {
                    "channel_id": channel_id,
                    "metric": metric,
                    "status": "insufficient_data",
                    "message": "Need at least 14 days of data for trend analysis",
                    "min_required_days": 14,
                    "actual_days": len(data_points),
                }

            # Convert to numpy array for analysis
            time_series = np.array(data_points)

            # Initialize analysis results
            analysis = {
                "channel_id": channel_id,
                "metric": metric,
                "period": {
                    "start": start_date.isoformat(),
                    "end": now.isoformat(),
                    "days": days,
                    "data_points": len(data_points),
                },
                "trend_analysis": {},
                "anomalies": {},
                "change_points": {},
                "forecasts": {},
                "insights": [],
                "timestamp": now.isoformat(),
            }

            # Perform trend analysis
            analysis["trend_analysis"] = await self._analyze_trend_components(time_series)

            # Detect anomalies
            analysis["anomalies"] = await self._detect_anomalies(time_series)

            # Find change points
            analysis["change_points"] = await self._detect_change_points(time_series)

            # Generate forecasts if requested
            if trend_analysis_type in ["comprehensive", "predictive"]:
                analysis["forecasts"] = await self._generate_trend_forecasts(time_series)

            # Generate insights
            analysis["insights"] = await self._generate_trend_insights(analysis)

            logger.info(f"Advanced trend analysis completed for {metric} on channel {channel_id}")
            return analysis

        except Exception as e:
            logger.error(f"Advanced trend analysis failed: {e}")
            return {
                "channel_id": channel_id,
                "metric": metric,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _analyze_trend_components(self, time_series: np.ndarray) -> dict:
        """Analyze trend components using statistical decomposition"""
        try:
            # Basic trend analysis
            x = np.arange(len(time_series))

            # Linear trend (slope)
            slope, intercept = np.polyfit(x, time_series, 1)

            # Polynomial trend (for non-linear patterns)
            poly_coeffs = (
                np.polyfit(x, time_series, 2) if len(time_series) > 10 else [0, slope, intercept]
            )

            # Moving averages for trend smoothing
            window_size = min(7, len(time_series) // 3)
            moving_avg = np.convolve(time_series, np.ones(window_size) / window_size, mode="valid")

            # Trend strength (how much variation is explained by trend)
            trend_line = slope * x + intercept
            trend_variance = np.var(trend_line)
            total_variance = np.var(time_series)
            trend_strength = trend_variance / total_variance if total_variance > 0 else 0

            # Trend direction classification
            if abs(slope) < np.std(time_series) * 0.1:
                direction = "stable"
            elif slope > 0:
                direction = "increasing"
            else:
                direction = "decreasing"

            # Volatility analysis
            volatility = (
                np.std(time_series) / np.mean(time_series) if np.mean(time_series) > 0 else 0
            )

            return {
                "linear_trend": {
                    "slope": float(slope),
                    "intercept": float(intercept),
                    "direction": direction,
                    "strength": float(trend_strength),
                },
                "polynomial_trend": {
                    "coefficients": [float(c) for c in poly_coeffs],
                    "curvature": float(poly_coeffs[0]) if len(poly_coeffs) > 2 else 0.0,
                },
                "moving_average": {
                    "values": [float(v) for v in moving_avg],
                    "window_size": window_size,
                },
                "volatility": {
                    "coefficient": float(volatility),
                    "classification": self._classify_volatility(volatility),
                },
                "summary": {
                    "overall_direction": direction,
                    "trend_strength": float(trend_strength),
                    "is_volatile": volatility > 0.3,
                },
            }

        except Exception as e:
            logger.error(f"Trend component analysis failed: {e}")
            return {"error": str(e)}

    async def _detect_anomalies(self, time_series: np.ndarray) -> dict:
        """Detect anomalies using statistical methods"""
        try:
            anomalies = {"outliers": [], "statistical_anomalies": [], "summary": {}}

            # Statistical outliers (IQR method)
            q25 = np.percentile(time_series, 25)
            q75 = np.percentile(time_series, 75)
            iqr = q75 - q25
            lower_bound = q25 - 1.5 * iqr
            upper_bound = q75 + 1.5 * iqr

            outlier_indices = np.where((time_series < lower_bound) | (time_series > upper_bound))[0]

            for idx in outlier_indices:
                anomalies["outliers"].append(
                    {
                        "index": int(idx),
                        "value": float(time_series[idx]),
                        "type": "high" if time_series[idx] > upper_bound else "low",
                        "deviation": float(abs(time_series[idx] - np.median(time_series))),
                    }
                )

            # Z-score based anomalies (for normal distributions)
            z_scores = np.abs((time_series - np.mean(time_series)) / np.std(time_series))
            z_anomaly_indices = np.where(z_scores > 2.5)[0]  # 2.5 sigma threshold

            for idx in z_anomaly_indices:
                anomalies["statistical_anomalies"].append(
                    {
                        "index": int(idx),
                        "value": float(time_series[idx]),
                        "z_score": float(z_scores[idx]),
                        "severity": "extreme" if z_scores[idx] > 3 else "moderate",
                    }
                )

            # Anomaly summary
            anomalies["summary"] = {
                "total_outliers": len(outlier_indices),
                "total_statistical_anomalies": len(z_anomaly_indices),
                "anomaly_rate": float(len(outlier_indices) / len(time_series)),
                "has_significant_anomalies": len(outlier_indices) > len(time_series) * 0.05,
            }

            return anomalies

        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {"error": str(e)}

    async def _detect_change_points(self, time_series: np.ndarray) -> dict:
        """Detect significant change points in the time series"""
        try:
            change_points = []

            # Simple change point detection using moving window variance
            window_size = max(5, len(time_series) // 10)

            for i in range(window_size, len(time_series) - window_size):
                # Compare variance before and after point
                before_window = time_series[i - window_size : i]
                after_window = time_series[i : i + window_size]

                before_mean = np.mean(before_window)
                after_mean = np.mean(after_window)

                # Check for significant mean change
                mean_change = abs(after_mean - before_mean)
                threshold = np.std(time_series) * 0.8  # Threshold for significance

                if mean_change > threshold:
                    # Perform t-test for statistical significance
                    t_stat, p_value = ttest_ind(before_window, after_window)

                    if p_value < 0.05:  # Statistically significant
                        change_points.append(
                            {
                                "index": int(i),
                                "before_mean": float(before_mean),
                                "after_mean": float(after_mean),
                                "change_magnitude": float(mean_change),
                                "change_direction": "increase"
                                if after_mean > before_mean
                                else "decrease",
                                "statistical_significance": float(p_value),
                                "confidence": "high" if p_value < 0.01 else "medium",
                            }
                        )

            return {
                "detected_changes": change_points,
                "total_change_points": len(change_points),
                "most_significant": max(change_points, key=lambda x: x["change_magnitude"])
                if change_points
                else None,
            }

        except Exception as e:
            logger.error(f"Change point detection failed: {e}")
            return {"error": str(e)}

    async def _generate_trend_forecasts(
        self, time_series: np.ndarray, forecast_days: int = 7
    ) -> dict:
        """Generate trend forecasts using multiple methods"""
        try:
            forecasts = {}

            # Linear extrapolation
            x = np.arange(len(time_series))
            slope, intercept = np.polyfit(x, time_series, 1)

            future_x = np.arange(len(time_series), len(time_series) + forecast_days)
            linear_forecast = slope * future_x + intercept

            # Moving average forecast
            window_size = min(7, len(time_series) // 3)
            recent_avg = np.mean(time_series[-window_size:])
            ma_forecast = np.full(forecast_days, recent_avg)

            # Exponential smoothing (simple)
            alpha = 0.3  # Smoothing parameter
            exp_forecast = []
            last_value = time_series[-1]

            for _ in range(forecast_days):
                next_value = alpha * last_value + (1 - alpha) * recent_avg
                exp_forecast.append(next_value)
                last_value = next_value

            # Calculate confidence intervals (assuming normal distribution)
            recent_std = (
                np.std(time_series[-14:]) if len(time_series) >= 14 else np.std(time_series)
            )

            forecasts = {
                "linear_forecast": {
                    "values": [float(v) for v in linear_forecast],
                    "method": "linear_extrapolation",
                    "confidence_intervals": {
                        "lower": [float(v - 1.96 * recent_std) for v in linear_forecast],
                        "upper": [float(v + 1.96 * recent_std) for v in linear_forecast],
                    },
                },
                "moving_average_forecast": {
                    "values": [float(v) for v in ma_forecast],
                    "method": "moving_average",
                    "window_size": window_size,
                },
                "exponential_smoothing": {
                    "values": [float(v) for v in exp_forecast],
                    "method": "exponential_smoothing",
                    "alpha": alpha,
                },
                "forecast_period": {"days": forecast_days, "confidence_level": 0.95},
            }

            return forecasts

        except Exception as e:
            logger.error(f"Trend forecasting failed: {e}")
            return {"error": str(e)}

    def _classify_volatility(self, volatility: float) -> str:
        """Classify volatility level"""
        if volatility < 0.1:
            return "very_low"
        elif volatility < 0.2:
            return "low"
        elif volatility < 0.4:
            return "moderate"
        elif volatility < 0.6:
            return "high"
        else:
            return "very_high"

    async def _generate_trend_insights(self, analysis: dict) -> list:
        """Generate actionable insights from trend analysis"""
        insights = []

        try:
            trend = analysis.get("trend_analysis", {})
            anomalies = analysis.get("anomalies", {})
            change_points = analysis.get("change_points", {})

            # Trend direction insights
            if trend.get("linear_trend", {}).get("direction") == "increasing":
                insights.append(
                    {
                        "type": "trend_direction",
                        "insight": f"Positive trend detected with {trend['linear_trend']['strength']:.2f} strength",
                        "recommendation": "Continue current growth strategies",
                        "priority": "medium",
                    }
                )
            elif trend.get("linear_trend", {}).get("direction") == "decreasing":
                insights.append(
                    {
                        "type": "trend_direction",
                        "insight": "Declining trend requires attention",
                        "recommendation": "Investigate causes and implement recovery strategies",
                        "priority": "high",
                    }
                )

            # Volatility insights
            volatility_class = trend.get("volatility", {}).get("classification")
            if volatility_class in ["high", "very_high"]:
                insights.append(
                    {
                        "type": "volatility",
                        "insight": f"High volatility detected ({volatility_class})",
                        "recommendation": "Focus on consistency to reduce performance swings",
                        "priority": "medium",
                    }
                )

            # Anomaly insights
            anomaly_rate = anomalies.get("summary", {}).get("anomaly_rate", 0)
            if anomaly_rate > 0.1:  # More than 10% anomalies
                insights.append(
                    {
                        "type": "anomalies",
                        "insight": f"High anomaly rate detected ({anomaly_rate:.1%})",
                        "recommendation": "Investigate unusual spikes or drops in performance",
                        "priority": "high",
                    }
                )

            # Change point insights
            total_changes = change_points.get("total_change_points", 0)
            if total_changes > 0:
                insights.append(
                    {
                        "type": "change_points",
                        "insight": f"Detected {total_changes} significant change points",
                        "recommendation": "Analyze what caused these changes for optimization",
                        "priority": "medium",
                    }
                )

            return insights

        except Exception as e:
            logger.error(f"Trend insights generation failed: {e}")
            return [{"type": "error", "insight": "Failed to generate insights", "priority": "low"}]

    # Helper methods for data retrieval
    async def _get_daily_views(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get daily view data for trend analysis"""
        try:
            current_date = start_date
            daily_views = []

            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)
                daily_view_sum = await self._posts.sum_views(channel_id, current_date, next_date)
                daily_views.append(daily_view_sum or 0)
                current_date = next_date

            return daily_views

        except Exception as e:
            logger.error(f"Failed to get daily views: {e}")
            return []

    async def _get_daily_growth(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get daily growth data for trend analysis"""
        try:
            followers_data = await self._daily.series_data(
                channel_id, "followers", start_date, end_date
            )

            if not followers_data:
                # Try subscribers metric as fallback
                followers_data = await self._daily.series_data(
                    channel_id, "subscribers", start_date, end_date
                )

            if not followers_data:
                return []

            # Calculate daily growth
            growth_data = []
            prev_value = None

            for data_point in followers_data:
                if prev_value is not None:
                    growth = data_point["value"] - prev_value
                    growth_data.append(growth)
                else:
                    growth_data.append(0)  # First day has 0 growth
                prev_value = data_point["value"]

            return growth_data

        except Exception as e:
            logger.error(f"Failed to get daily growth: {e}")
            return []

    async def _get_daily_engagement(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list:
        """Get daily engagement data for trend analysis"""
        try:
            current_date = start_date
            daily_engagement = []

            while current_date <= end_date:
                next_date = current_date + timedelta(days=1)

                # Get daily posts and views
                daily_posts = await self._posts.count(channel_id, current_date, next_date)
                daily_views = await self._posts.sum_views(channel_id, current_date, next_date)

                # Get current subscriber count for engagement calculation
                current_subs = await self._daily.series_value(channel_id, "followers", current_date)
                if current_subs is None:
                    current_subs = await self._daily.series_value(
                        channel_id, "subscribers", current_date
                    )

                # Calculate engagement rate
                if daily_posts > 0 and current_subs and current_subs > 0:
                    avg_views_per_post = daily_views / daily_posts
                    engagement_rate = (avg_views_per_post / current_subs) * 100
                else:
                    engagement_rate = 0.0

                daily_engagement.append(engagement_rate)
                current_date = next_date

            return daily_engagement

        except Exception as e:
            logger.error(f"Failed to get daily engagement: {e}")
            return []
