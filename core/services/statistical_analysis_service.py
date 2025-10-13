"""
Statistical Analysis Service - Advanced Statistical Testing & Analysis

Extracted from AnalyticsFusionService to follow Single Responsibility Principle.
Handles all statistical significance testing, hypothesis testing, and statistical computations.
"""

from __future__ import annotations

import logging
from datetime import datetime

import numpy as np
from scipy import stats
from scipy.stats import mannwhitneyu, ttest_ind

logger = logging.getLogger(__name__)


class StatisticalAnalysisService:
    """
    📊 Statistical Analysis Service

    Specialized service for statistical testing and analysis:
    - Statistical significance testing
    - Hypothesis testing (t-tests, Mann-Whitney U, Chi-square)
    - Effect size calculations
    - Confidence intervals
    - Data normality testing
    """

    def __init__(self, channel_daily_repo, post_repo, metrics_repo):
        """Initialize with required repositories"""
        self._daily = channel_daily_repo
        self._posts = post_repo
        self._metrics = metrics_repo

    async def calculate_statistical_significance(
        self,
        channel_id: int,
        metric_type: str = "views",
        comparison_period_days: int = 30,
        baseline_period_days: int = 30,
        confidence_level: float = 0.95,
    ) -> dict:
        """
        📊 Advanced Statistical Significance Testing

        Performs comprehensive statistical analysis to determine if changes
        in metrics are statistically significant or due to random variation.

        Args:
            channel_id: Target channel ID
            metric_type: Metric to analyze ('views', 'engagement', 'growth')
            comparison_period_days: Recent period for comparison
            baseline_period_days: Historical baseline period
            confidence_level: Statistical confidence level (0.95 = 95%)

        Returns:
            Comprehensive statistical analysis with significance tests
        """
        try:
            from datetime import datetime, timedelta

            now = datetime.now()

            # Define time periods
            comparison_start = now - timedelta(days=comparison_period_days)
            baseline_start = now - timedelta(days=comparison_period_days + baseline_period_days)
            baseline_end = now - timedelta(days=comparison_period_days)

            # Get data for both periods
            if metric_type == "views":
                comparison_data = await self._get_daily_views(channel_id, comparison_start, now)
                baseline_data = await self._get_daily_views(
                    channel_id, baseline_start, baseline_end
                )
            elif metric_type == "engagement":
                comparison_data = await self._get_daily_engagement(
                    channel_id, comparison_start, now
                )
                baseline_data = await self._get_daily_engagement(
                    channel_id, baseline_start, baseline_end
                )
            elif metric_type == "growth":
                comparison_data = await self._get_daily_growth(channel_id, comparison_start, now)
                baseline_data = await self._get_daily_growth(
                    channel_id, baseline_start, baseline_end
                )
            else:
                return {"error": f"Unsupported metric type: {metric_type}"}

            if not comparison_data or not baseline_data:
                return {
                    "channel_id": channel_id,
                    "status": "insufficient_data",
                    "message": f"Insufficient data for {metric_type} analysis",
                }

            # Convert to numpy arrays for statistical analysis
            comparison_array = np.array(comparison_data)
            baseline_array = np.array(baseline_data)

            # Perform comprehensive statistical tests
            statistical_tests = await self._perform_statistical_tests(
                comparison_array, baseline_array
            )

            # Calculate effect sizes and confidence intervals
            effect_size = self._calculate_effect_size(comparison_array, baseline_array)
            confidence_intervals = self._calculate_confidence_intervals(
                comparison_array, baseline_array, confidence_level
            )

            # Determine statistical significance
            alpha = 1 - confidence_level
            is_significant = statistical_tests["t_test"]["p_value"] < alpha

            # Generate comprehensive report
            significance_report = {
                "channel_id": channel_id,
                "metric_type": metric_type,
                "analysis_timestamp": now.isoformat(),
                "periods": {
                    "comparison_period": {
                        "start": comparison_start.isoformat(),
                        "end": now.isoformat(),
                        "days": comparison_period_days,
                    },
                    "baseline_period": {
                        "start": baseline_start.isoformat(),
                        "end": baseline_end.isoformat(),
                        "days": baseline_period_days,
                    },
                },
                "descriptive_statistics": {
                    "comparison": {
                        "mean": float(np.mean(comparison_array)),
                        "std": float(np.std(comparison_array)),
                        "median": float(np.median(comparison_array)),
                        "min": float(np.min(comparison_array)),
                        "max": float(np.max(comparison_array)),
                        "count": len(comparison_array),
                    },
                    "baseline": {
                        "mean": float(np.mean(baseline_array)),
                        "std": float(np.std(baseline_array)),
                        "median": float(np.median(baseline_array)),
                        "min": float(np.min(baseline_array)),
                        "max": float(np.max(baseline_array)),
                        "count": len(baseline_array),
                    },
                },
                "statistical_tests": statistical_tests,
                "effect_size": effect_size,
                "confidence_intervals": confidence_intervals,
                "significance_assessment": {
                    "is_statistically_significant": is_significant,
                    "confidence_level": confidence_level,
                    "alpha": alpha,
                    "interpretation": self._interpret_significance(
                        is_significant, effect_size, statistical_tests
                    ),
                },
                "practical_significance": {
                    "percent_change": (
                        float(
                            (np.mean(comparison_array) - np.mean(baseline_array))
                            / np.mean(baseline_array)
                            * 100
                        )
                        if np.mean(baseline_array) != 0
                        else 0
                    ),
                    "absolute_change": float(np.mean(comparison_array) - np.mean(baseline_array)),
                    "magnitude": self._classify_effect_magnitude(effect_size["cohens_d"]),
                },
            }

            logger.info(f"Statistical significance analysis completed for channel {channel_id}")
            return significance_report

        except Exception as e:
            logger.error(f"Statistical significance calculation failed: {e}")
            return {
                "channel_id": channel_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _perform_statistical_tests(
        self, comparison_data: np.ndarray, baseline_data: np.ndarray
    ) -> dict:
        """
        🧮 Perform comprehensive statistical hypothesis tests

        Tests performed:
        1. Independent t-test (parametric)
        2. Mann-Whitney U test (non-parametric)
        3. Normality tests (Shapiro-Wilk)
        4. Variance equality test (Levene's test)
        """
        try:
            tests = {}

            # 1. Normality tests
            comparison_normality = stats.shapiro(comparison_data)
            baseline_normality = stats.shapiro(baseline_data)

            tests["normality"] = {
                "comparison_normal": comparison_normality.pvalue > 0.05,
                "baseline_normal": baseline_normality.pvalue > 0.05,
                "comparison_shapiro_p": float(comparison_normality.pvalue),
                "baseline_shapiro_p": float(baseline_normality.pvalue),
            }

            # 2. Variance equality test (Levene's test)
            levene_stat, levene_p = stats.levene(comparison_data, baseline_data)
            equal_variances = levene_p > 0.05

            tests["variance_equality"] = {
                "equal_variances": equal_variances,
                "levene_statistic": float(levene_stat),
                "levene_p_value": float(levene_p),
            }

            # 3. Independent t-test (parametric)
            t_stat, t_p = ttest_ind(comparison_data, baseline_data, equal_var=equal_variances)

            tests["t_test"] = {
                "statistic": float(t_stat),
                "p_value": float(t_p),
                "degrees_of_freedom": len(comparison_data) + len(baseline_data) - 2,
                "test_type": ("Welch's t-test" if not equal_variances else "Student's t-test"),
            }

            # 4. Mann-Whitney U test (non-parametric alternative)
            u_stat, u_p = mannwhitneyu(comparison_data, baseline_data, alternative="two-sided")

            tests["mann_whitney_u"] = {
                "statistic": float(u_stat),
                "p_value": float(u_p),
                "test_type": "Mann-Whitney U (non-parametric)",
            }

            # 5. Recommended test based on data characteristics
            if tests["normality"]["comparison_normal"] and tests["normality"]["baseline_normal"]:
                recommended_test = "t_test"
                recommended_p_value = t_p
            else:
                recommended_test = "mann_whitney_u"
                recommended_p_value = u_p

            tests["recommendation"] = {
                "recommended_test": recommended_test,
                "recommended_p_value": float(recommended_p_value),
                "reason": (
                    "Normal distribution"
                    if recommended_test == "t_test"
                    else "Non-normal distribution"
                ),
            }

            return tests

        except Exception as e:
            logger.error(f"Statistical tests failed: {e}")
            return {"error": str(e)}

    def _calculate_effect_size(
        self, comparison_data: np.ndarray, baseline_data: np.ndarray
    ) -> dict:
        """Calculate effect sizes to measure practical significance"""
        try:
            # Cohen's d (standardized effect size)
            pooled_std = np.sqrt(
                (
                    (len(comparison_data) - 1) * np.var(comparison_data, ddof=1)
                    + (len(baseline_data) - 1) * np.var(baseline_data, ddof=1)
                )
                / (len(comparison_data) + len(baseline_data) - 2)
            )

            cohens_d = (np.mean(comparison_data) - np.mean(baseline_data)) / pooled_std

            # Glass's Delta (alternative effect size)
            glass_delta = (np.mean(comparison_data) - np.mean(baseline_data)) / np.std(
                baseline_data
            )

            # Hedge's g (bias-corrected Cohen's d)
            j = 1 - (3 / (4 * (len(comparison_data) + len(baseline_data)) - 9))
            hedges_g = cohens_d * j

            return {
                "cohens_d": float(cohens_d),
                "glass_delta": float(glass_delta),
                "hedges_g": float(hedges_g),
                "interpretation": self._interpret_effect_size(cohens_d),
            }

        except Exception as e:
            logger.error(f"Effect size calculation failed: {e}")
            return {"error": str(e)}

    def _calculate_confidence_intervals(
        self,
        comparison_data: np.ndarray,
        baseline_data: np.ndarray,
        confidence_level: float,
    ) -> dict:
        """Calculate confidence intervals for means and differences"""
        try:
            1 - confidence_level

            # Confidence interval for comparison mean
            comparison_ci = stats.t.interval(
                confidence_level,
                len(comparison_data) - 1,
                loc=np.mean(comparison_data),
                scale=stats.sem(comparison_data),
            )

            # Confidence interval for baseline mean
            baseline_ci = stats.t.interval(
                confidence_level,
                len(baseline_data) - 1,
                loc=np.mean(baseline_data),
                scale=stats.sem(baseline_data),
            )

            # Confidence interval for difference in means
            diff_mean = np.mean(comparison_data) - np.mean(baseline_data)
            diff_se = np.sqrt(stats.sem(comparison_data) ** 2 + stats.sem(baseline_data) ** 2)
            df = len(comparison_data) + len(baseline_data) - 2

            diff_ci = stats.t.interval(confidence_level, df, loc=diff_mean, scale=diff_se)

            return {
                "comparison_mean_ci": [
                    float(comparison_ci[0]),
                    float(comparison_ci[1]),
                ],
                "baseline_mean_ci": [float(baseline_ci[0]), float(baseline_ci[1])],
                "difference_ci": [float(diff_ci[0]), float(diff_ci[1])],
                "confidence_level": confidence_level,
            }

        except Exception as e:
            logger.error(f"Confidence interval calculation failed: {e}")
            return {"error": str(e)}

    def _interpret_significance(self, is_significant: bool, effect_size: dict, tests: dict) -> str:
        """Generate human-readable interpretation of statistical results"""
        try:
            if not is_significant:
                return "No statistically significant difference detected. Changes may be due to random variation."

            effect_magnitude = self._classify_effect_magnitude(effect_size.get("cohens_d", 0))
            p_value = tests.get("recommendation", {}).get("recommended_p_value", 0)

            if effect_magnitude == "large":
                return f"Statistically significant change with large practical effect (p={p_value:.4f}). Strong evidence of meaningful difference."
            elif effect_magnitude == "medium":
                return f"Statistically significant change with medium practical effect (p={p_value:.4f}). Moderate evidence of meaningful difference."
            elif effect_magnitude == "small":
                return f"Statistically significant change with small practical effect (p={p_value:.4f}). Limited practical significance despite statistical significance."
            else:
                return f"Statistically significant change detected (p={p_value:.4f}), but practical significance unclear."

        except Exception:
            return "Statistical interpretation unavailable due to calculation error."

    def _classify_effect_magnitude(self, cohens_d: float) -> str:
        """Classify effect size magnitude using Cohen's conventions"""
        abs_d = abs(cohens_d)
        if abs_d >= 0.8:
            return "large"
        elif abs_d >= 0.5:
            return "medium"
        elif abs_d >= 0.2:
            return "small"
        else:
            return "negligible"

    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d effect size"""
        magnitude = self._classify_effect_magnitude(cohens_d)
        direction = "increase" if cohens_d > 0 else "decrease"

        magnitude_descriptions = {
            "negligible": "negligible",
            "small": "small but detectable",
            "medium": "moderate",
            "large": "substantial",
        }

        return f"{magnitude_descriptions[magnitude]} {direction} (d={cohens_d:.3f})"

    async def _get_daily_views(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list[float]:
        """Get daily views data for statistical analysis"""
        try:
            daily_data = await self._daily.series_data(channel_id, "views", start_date, end_date)
            if not daily_data:
                return []

            return [float(d.get("value", 0)) for d in daily_data]

        except Exception as e:
            logger.error(f"Failed to get daily views: {e}")
            return []

    async def _get_daily_growth(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list[float]:
        """Get daily growth rates for statistical analysis"""
        try:
            # Get follower/subscriber data
            follower_data = await self._daily.series_data(
                channel_id, "followers", start_date, end_date
            )
            if not follower_data:
                follower_data = await self._daily.series_data(
                    channel_id, "subscribers", start_date, end_date
                )

            if not follower_data or len(follower_data) < 2:
                return []

            # Calculate daily growth rates
            growth_rates = []
            for i in range(1, len(follower_data)):
                current_value = follower_data[i].get("value", 0)
                previous_value = follower_data[i - 1].get("value", 0)

                if previous_value > 0:
                    growth_rate = (current_value - previous_value) / previous_value
                    growth_rates.append(growth_rate)

            return growth_rates

        except Exception as e:
            logger.error(f"Failed to get daily growth: {e}")
            return []

    async def _get_daily_engagement(
        self, channel_id: int, start_date: datetime, end_date: datetime
    ) -> list[float]:
        """Get daily engagement rates for statistical analysis"""
        try:
            # Get posts in the time period
            posts = await self._posts.top_by_views(channel_id, start_date, end_date, 1000)
            if not posts:
                return []

            # Group posts by day and calculate daily engagement
            daily_engagement = {}

            for post in posts:
                post_date = post.get("date")
                if not post_date:
                    continue

                try:
                    # Extract date part (YYYY-MM-DD)
                    date_key = post_date[:10]

                    # Calculate engagement metrics
                    views = post.get("views", 0)
                    forwards = post.get("forwards", 0)
                    replies = post.get("replies", 0)
                    reactions = post.get("reactions", {})

                    if isinstance(reactions, dict):
                        total_reactions = sum(reactions.values())
                    else:
                        total_reactions = 0

                    # Calculate engagement rate
                    if views > 0:
                        engagement_rate = (forwards + replies + total_reactions) / views

                        if date_key not in daily_engagement:
                            daily_engagement[date_key] = []
                        daily_engagement[date_key].append(engagement_rate)

                except Exception as e:
                    logger.warning(f"Failed to process post engagement: {e}")
                    continue

            # Calculate average engagement per day
            daily_averages = []
            for date_key in sorted(daily_engagement.keys()):
                avg_engagement = np.mean(daily_engagement[date_key])
                daily_averages.append(avg_engagement)

            return daily_averages

        except Exception as e:
            logger.error(f"Failed to get daily engagement: {e}")
            return []

    async def health_check(self) -> dict:
        """Health check for statistical analysis service"""
        return {
            "service": "StatisticalAnalysisService",
            "status": "healthy",
            "capabilities": [
                "statistical_significance_testing",
                "hypothesis_testing",
                "effect_size_calculation",
                "confidence_intervals",
                "normality_testing",
            ],
            "dependencies": {"scipy": True, "numpy": True},
            "timestamp": datetime.now().isoformat(),
        }
