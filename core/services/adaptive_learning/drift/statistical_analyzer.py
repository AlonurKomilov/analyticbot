"""
Statistical Drift Analyzer
==========================

Handles statistical tests for drift detection including KS tests,
Mann-Whitney tests, and Chi-square tests for distribution comparison.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import scipy.stats as stats

logger = logging.getLogger(__name__)


@dataclass
class StatisticalTestResult:
    """Result of a statistical test"""

    test_name: str
    test_statistic: float
    p_value: float
    detected: bool
    confidence: float
    distribution_metrics: dict[str, float]


@dataclass
class FeatureAnalysisResult:
    """Result of feature-level drift analysis"""

    feature_name: str
    drift_detected: bool
    drift_score: float
    best_test: StatisticalTestResult
    all_tests: dict[str, StatisticalTestResult]


class StatisticalDriftAnalyzer:
    """
    Specialized service for statistical drift analysis.

    Performs various statistical tests to detect distribution changes
    between reference and current data samples.
    """

    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.supported_tests = [
            "kolmogorov_smirnov",
            "mann_whitney",
            "chi_square",
            "anderson_darling",
        ]

        logger.info("📊 Statistical Drift Analyzer initialized")

    async def analyze_feature_drift(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> list[FeatureAnalysisResult]:
        """Analyze drift for individual features"""
        try:
            results = []
            n_features = reference_data.shape[1]

            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(n_features)]

            for i in range(n_features):
                feature_name = feature_names[i] if i < len(feature_names) else f"feature_{i}"

                ref_feature = reference_data[:, i]
                curr_feature = current_data[:, i]

                # Run all statistical tests
                test_results = await self._run_all_tests(ref_feature, curr_feature)

                # Select best test (most significant)
                best_test = min(test_results.values(), key=lambda x: x.p_value)

                # Calculate overall drift score
                drift_score = self._calculate_feature_drift_score(test_results)

                result = FeatureAnalysisResult(
                    feature_name=feature_name,
                    drift_detected=best_test.detected,
                    drift_score=drift_score,
                    best_test=best_test,
                    all_tests=test_results,
                )

                results.append(result)

            logger.info(f"📊 Analyzed {len(results)} features for drift")
            return results

        except Exception as e:
            logger.error(f"❌ Failed to analyze feature drift: {e}")
            return []

    async def kolmogorov_smirnov_test(
        self, reference_sample: np.ndarray, current_sample: np.ndarray
    ) -> StatisticalTestResult:
        """Perform Kolmogorov-Smirnov test"""
        try:
            ks_statistic, p_value = stats.ks_2samp(reference_sample, current_sample)

            detected = p_value < self.significance_level
            confidence = 1.0 - p_value if detected else p_value

            distribution_metrics = self._calculate_distribution_metrics(
                reference_sample, current_sample
            )

            return StatisticalTestResult(
                test_name="kolmogorov_smirnov",
                test_statistic=float(ks_statistic),
                p_value=float(p_value),
                detected=detected,
                confidence=float(confidence),
                distribution_metrics=distribution_metrics,
            )

        except Exception as e:
            logger.error(f"❌ KS test failed: {e}")
            return self._create_failed_test_result("kolmogorov_smirnov")

    async def mann_whitney_test(
        self, reference_sample: np.ndarray, current_sample: np.ndarray
    ) -> StatisticalTestResult:
        """Perform Mann-Whitney U test"""
        try:
            mw_statistic, p_value = stats.mannwhitneyu(
                reference_sample, current_sample, alternative="two-sided"
            )

            detected = p_value < self.significance_level
            confidence = 1.0 - p_value if detected else p_value

            distribution_metrics = self._calculate_distribution_metrics(
                reference_sample, current_sample
            )

            return StatisticalTestResult(
                test_name="mann_whitney",
                test_statistic=float(mw_statistic),
                p_value=float(p_value),
                detected=detected,
                confidence=float(confidence),
                distribution_metrics=distribution_metrics,
            )

        except Exception as e:
            logger.error(f"❌ Mann-Whitney test failed: {e}")
            return self._create_failed_test_result("mann_whitney")

    async def chi_square_test(
        self, reference_sample: np.ndarray, current_sample: np.ndarray, bins: int = 10
    ) -> StatisticalTestResult:
        """Perform Chi-square test using histogram binning"""
        try:
            # Create histograms
            data_range = (
                min(np.min(reference_sample), np.min(current_sample)),
                max(np.max(reference_sample), np.max(current_sample)),
            )

            ref_hist, bin_edges = np.histogram(reference_sample, bins=bins, range=data_range)
            curr_hist, _ = np.histogram(current_sample, bins=bin_edges)

            # Avoid zero frequencies by adding small constant
            ref_hist = ref_hist + 1
            curr_hist = curr_hist + 1

            # Normalize to same total count
            ref_total = np.sum(ref_hist)
            curr_total = np.sum(curr_hist)
            expected = ref_hist * (curr_total / ref_total)

            chi2_statistic, p_value = stats.chisquare(curr_hist, expected)

            detected = p_value < self.significance_level
            confidence = 1.0 - p_value if detected else p_value

            distribution_metrics = self._calculate_distribution_metrics(
                reference_sample, current_sample
            )

            return StatisticalTestResult(
                test_name="chi_square",
                test_statistic=float(chi2_statistic),
                p_value=float(p_value),
                detected=detected,
                confidence=float(confidence),
                distribution_metrics=distribution_metrics,
            )

        except Exception as e:
            logger.error(f"❌ Chi-square test failed: {e}")
            return self._create_failed_test_result("chi_square")

    async def anderson_darling_test(
        self, reference_sample: np.ndarray, current_sample: np.ndarray
    ) -> StatisticalTestResult:
        """Perform Anderson-Darling test"""
        try:
            # Use 2-sample Anderson-Darling test
            ad_statistic, critical_values, significance_level = stats.anderson_ksamp(
                [reference_sample, current_sample]
            )

            # Determine if drift is detected based on critical values
            detected = ad_statistic > critical_values[2]  # Use 1% significance level
            p_value = 0.01 if detected else 0.1  # Approximate p-value
            confidence = 1.0 - p_value if detected else p_value

            distribution_metrics = self._calculate_distribution_metrics(
                reference_sample, current_sample
            )

            return StatisticalTestResult(
                test_name="anderson_darling",
                test_statistic=float(ad_statistic),
                p_value=float(p_value),
                detected=detected,
                confidence=float(confidence),
                distribution_metrics=distribution_metrics,
            )

        except Exception as e:
            logger.error(f"❌ Anderson-Darling test failed: {e}")
            return self._create_failed_test_result("anderson_darling")

    async def population_stability_index(
        self, reference_sample: np.ndarray, current_sample: np.ndarray, bins: int = 10
    ) -> float:
        """Calculate Population Stability Index (PSI)"""
        try:
            # Create bins based on reference data percentiles
            percentiles = np.linspace(0, 100, bins + 1)
            bin_edges = np.percentile(reference_sample, percentiles)
            bin_edges[0] = -np.inf
            bin_edges[-1] = np.inf

            # Calculate proportions
            ref_counts, _ = np.histogram(reference_sample, bins=bin_edges)
            curr_counts, _ = np.histogram(current_sample, bins=bin_edges)

            ref_props = ref_counts / len(reference_sample)
            curr_props = curr_counts / len(current_sample)

            # Avoid division by zero
            ref_props = np.where(ref_props == 0, 0.0001, ref_props)
            curr_props = np.where(curr_props == 0, 0.0001, curr_props)

            # Calculate PSI
            psi = np.sum((curr_props - ref_props) * np.log(curr_props / ref_props))

            return float(psi)

        except Exception as e:
            logger.error(f"❌ PSI calculation failed: {e}")
            return 0.0

    async def _run_all_tests(
        self, reference_sample: np.ndarray, current_sample: np.ndarray
    ) -> dict[str, StatisticalTestResult]:
        """Run all available statistical tests"""
        tests = {}

        # Run tests concurrently
        test_tasks = [
            self.kolmogorov_smirnov_test(reference_sample, current_sample),
            self.mann_whitney_test(reference_sample, current_sample),
            self.chi_square_test(reference_sample, current_sample),
            self.anderson_darling_test(reference_sample, current_sample),
        ]

        try:
            results = await asyncio.gather(*test_tasks, return_exceptions=True)

            test_names = [
                "kolmogorov_smirnov",
                "mann_whitney",
                "chi_square",
                "anderson_darling",
            ]

            for test_name, result in zip(test_names, results, strict=False):
                if isinstance(result, StatisticalTestResult):
                    tests[test_name] = result
                else:
                    logger.error(f"❌ Test {test_name} failed: {result}")
                    tests[test_name] = self._create_failed_test_result(test_name)

        except Exception as e:
            logger.error(f"❌ Failed to run statistical tests: {e}")
            # Create failed results for all tests
            for test_name in [
                "kolmogorov_smirnov",
                "mann_whitney",
                "chi_square",
                "anderson_darling",
            ]:
                tests[test_name] = self._create_failed_test_result(test_name)

        return tests

    def _calculate_distribution_metrics(
        self, reference_sample: np.ndarray, current_sample: np.ndarray
    ) -> dict[str, float]:
        """Calculate distribution comparison metrics"""
        try:
            metrics = {
                "mean_shift": float(abs(np.mean(current_sample) - np.mean(reference_sample))),
                "std_shift": float(abs(np.std(current_sample) - np.std(reference_sample))),
                "median_shift": float(abs(np.median(current_sample) - np.median(reference_sample))),
                "quantile_25_shift": float(
                    abs(np.percentile(current_sample, 25) - np.percentile(reference_sample, 25))
                ),
                "quantile_75_shift": float(
                    abs(np.percentile(current_sample, 75) - np.percentile(reference_sample, 75))
                ),
                "skewness_shift": float(
                    abs(stats.skew(current_sample) - stats.skew(reference_sample))
                ),
                "kurtosis_shift": float(
                    abs(stats.kurtosis(current_sample) - stats.kurtosis(reference_sample))
                ),
            }

            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to calculate distribution metrics: {e}")
            return {}

    def _calculate_feature_drift_score(
        self, test_results: dict[str, StatisticalTestResult]
    ) -> float:
        """Calculate overall drift score from test results"""
        try:
            # Weight tests by their reliability
            test_weights = {
                "kolmogorov_smirnov": 0.3,
                "mann_whitney": 0.25,
                "chi_square": 0.25,
                "anderson_darling": 0.2,
            }

            weighted_score = 0.0
            total_weight = 0.0

            for test_name, result in test_results.items():
                if test_name in test_weights:
                    weight = test_weights[test_name]
                    # Convert p-value to drift score (lower p-value = higher drift)
                    drift_contribution = (
                        min(1.0, 1.0 - result.p_value) if result.p_value < 1.0 else 0.0
                    )
                    weighted_score += weight * drift_contribution
                    total_weight += weight

            return float(weighted_score / total_weight if total_weight > 0 else 0.0)

        except Exception as e:
            logger.error(f"❌ Failed to calculate drift score: {e}")
            return 0.0

    def _create_failed_test_result(self, test_name: str) -> StatisticalTestResult:
        """Create a failed test result"""
        return StatisticalTestResult(
            test_name=test_name,
            test_statistic=0.0,
            p_value=1.0,
            detected=False,
            confidence=0.0,
            distribution_metrics={},
        )

    def get_supported_tests(self) -> list[str]:
        """Get list of supported statistical tests"""
        return self.supported_tests.copy()

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "statistical_drift_analyzer",
            "status": "healthy",
            "supported_tests": len(self.supported_tests),
            "significance_level": self.significance_level,
        }
