"""
Multivariate Drift Analyzer
===========================

Handles multivariate drift detection using distance metrics,
dimensionality reduction, and ensemble methods.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MultivariateDriftResult:
    """Result of multivariate drift analysis"""

    method_name: str
    drift_score: float
    detected: bool
    confidence: float
    computation_time_ms: float
    metadata: dict[str, Any]


@dataclass
class DimensionalityReductionResult:
    """Result of dimensionality reduction analysis"""

    method: str
    original_dimensions: int
    reduced_dimensions: int
    explained_variance: float
    drift_detected: bool
    drift_score: float


class MultivariateDriftAnalyzer:
    """
    Specialized service for multivariate drift analysis.

    Handles high-dimensional drift detection using various distance metrics
    and dimensionality reduction techniques.
    """

    def __init__(self, max_samples_for_computation: int = 1000):
        self.max_samples = max_samples_for_computation
        self.supported_methods = [
            "maximum_mean_discrepancy",
            "energy_distance",
            "wasserstein_distance",
            "hotelling_t2",
            "pca_drift",
        ]

        logger.info("🌐 Multivariate Drift Analyzer initialized")

    async def analyze_multivariate_drift(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        methods: list[str] | None = None,
    ) -> dict[str, MultivariateDriftResult]:
        """Analyze multivariate drift using multiple methods"""
        try:
            if methods is None:
                methods = self.supported_methods

            # Sample data if too large for efficient computation
            ref_sample = self._sample_data(reference_data)
            curr_sample = self._sample_data(current_data)

            results = {}

            # Run methods concurrently
            tasks = []
            for method in methods:
                if method in self.supported_methods:
                    task = self._run_drift_method(method, ref_sample, curr_sample)
                    tasks.append((method, task))

            # Collect results
            for method, task in tasks:
                try:
                    result = await task
                    results[method] = result
                except Exception as e:
                    logger.error(f"❌ Method {method} failed: {e}")
                    results[method] = self._create_failed_result(method)

            logger.info(f"🌐 Completed multivariate drift analysis with {len(results)} methods")
            return results

        except Exception as e:
            logger.error(f"❌ Failed multivariate drift analysis: {e}")
            return {}

    async def maximum_mean_discrepancy(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        gamma: float | None = None,
    ) -> MultivariateDriftResult:
        """Calculate Maximum Mean Discrepancy using RBF kernel"""
        start_time = datetime.utcnow()

        try:
            if gamma is None:
                gamma = 1.0 / reference_data.shape[1]  # Heuristic

            # Sample for computational efficiency
            ref_sample = self._sample_data(reference_data, max_size=500)
            curr_sample = self._sample_data(current_data, max_size=500)

            # Calculate kernel matrices
            mmd_score = await self._calculate_mmd_kernel(ref_sample, curr_sample, gamma)

            # Determine drift detection
            threshold = 0.1  # Configurable threshold
            detected = mmd_score > threshold
            confidence = min(0.95, mmd_score / threshold) if detected else max(0.1, 1.0 - mmd_score)

            computation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return MultivariateDriftResult(
                method_name="maximum_mean_discrepancy",
                drift_score=float(mmd_score),
                detected=detected,
                confidence=float(confidence),
                computation_time_ms=float(computation_time),
                metadata={
                    "gamma": gamma,
                    "reference_samples": len(ref_sample),
                    "current_samples": len(curr_sample),
                },
            )

        except Exception as e:
            logger.error(f"❌ MMD calculation failed: {e}")
            return self._create_failed_result("maximum_mean_discrepancy")

    async def energy_distance(
        self, reference_data: np.ndarray, current_data: np.ndarray
    ) -> MultivariateDriftResult:
        """Calculate energy distance between distributions"""
        start_time = datetime.utcnow()

        try:
            # Sample for computational efficiency
            ref_sample = self._sample_data(reference_data, max_size=300)
            curr_sample = self._sample_data(current_data, max_size=300)

            # Calculate energy distance components
            energy_dist = await self._calculate_energy_distance(ref_sample, curr_sample)

            # Normalize and determine detection
            threshold = 0.2
            detected = energy_dist > threshold
            confidence = (
                min(0.95, energy_dist / threshold) if detected else max(0.1, 1.0 - energy_dist)
            )

            computation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return MultivariateDriftResult(
                method_name="energy_distance",
                drift_score=float(energy_dist),
                detected=detected,
                confidence=float(confidence),
                computation_time_ms=float(computation_time),
                metadata={
                    "reference_samples": len(ref_sample),
                    "current_samples": len(curr_sample),
                },
            )

        except Exception as e:
            logger.error(f"❌ Energy distance calculation failed: {e}")
            return self._create_failed_result("energy_distance")

    async def wasserstein_distance(
        self, reference_data: np.ndarray, current_data: np.ndarray
    ) -> MultivariateDriftResult:
        """Calculate Wasserstein distance (1D approximation for efficiency)"""
        start_time = datetime.utcnow()

        try:
            # For multivariate data, calculate average Wasserstein distance across features
            n_features = reference_data.shape[1]
            wasserstein_scores = []

            for i in range(n_features):
                ref_feature = reference_data[:, i]
                curr_feature = current_data[:, i]

                # Calculate 1D Wasserstein distance
                w_dist = self._wasserstein_1d(ref_feature, curr_feature)
                wasserstein_scores.append(w_dist)

            # Average across features
            avg_wasserstein = np.mean(wasserstein_scores)

            # Determine detection
            threshold = 0.15
            detected = avg_wasserstein > threshold
            confidence = (
                min(0.95, avg_wasserstein / threshold)
                if detected
                else max(0.1, 1.0 - avg_wasserstein)
            )

            computation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return MultivariateDriftResult(
                method_name="wasserstein_distance",
                drift_score=float(avg_wasserstein),
                detected=detected,
                confidence=float(confidence),
                computation_time_ms=float(computation_time),
                metadata={
                    "features_analyzed": n_features,
                    "per_feature_scores": wasserstein_scores,
                },
            )

        except Exception as e:
            logger.error(f"❌ Wasserstein distance calculation failed: {e}")
            return self._create_failed_result("wasserstein_distance")

    async def hotelling_t2_test(
        self, reference_data: np.ndarray, current_data: np.ndarray
    ) -> MultivariateDriftResult:
        """Perform Hotelling's T² test for multivariate mean comparison"""
        start_time = datetime.utcnow()

        try:
            # Sample for computational efficiency
            ref_sample = self._sample_data(reference_data, max_size=400)
            curr_sample = self._sample_data(current_data, max_size=400)

            # Calculate means
            ref_mean = np.mean(ref_sample, axis=0)
            curr_mean = np.mean(curr_sample, axis=0)

            # Calculate pooled covariance matrix
            n1, n2 = len(ref_sample), len(curr_sample)
            p = ref_sample.shape[1]

            cov1 = np.cov(ref_sample.T)
            cov2 = np.cov(curr_sample.T)
            pooled_cov = ((n1 - 1) * cov1 + (n2 - 1) * cov2) / (n1 + n2 - 2)

            # Add regularization to avoid singular matrix
            pooled_cov += np.eye(p) * 1e-6

            # Calculate T² statistic
            mean_diff = curr_mean - ref_mean
            try:
                inv_cov = np.linalg.inv(pooled_cov)
                t2_stat = (n1 * n2) / (n1 + n2) * np.dot(mean_diff, np.dot(inv_cov, mean_diff))
            except np.linalg.LinAlgError:
                # Use pseudo-inverse if matrix is singular
                inv_cov = np.linalg.pinv(pooled_cov)
                t2_stat = (n1 * n2) / (n1 + n2) * np.dot(mean_diff, np.dot(inv_cov, mean_diff))

            # Convert to F-statistic and approximate p-value
            f_stat = ((n1 + n2 - p - 1) * t2_stat) / ((n1 + n2 - 2) * p)

            # Simple threshold-based detection
            threshold = 10.0  # Configurable
            detected = f_stat > threshold
            confidence = (
                min(0.95, f_stat / threshold)
                if detected
                else max(0.1, threshold / max(f_stat, 1.0))
            )

            computation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return MultivariateDriftResult(
                method_name="hotelling_t2",
                drift_score=float(f_stat),
                detected=detected,
                confidence=float(confidence),
                computation_time_ms=float(computation_time),
                metadata={
                    "t2_statistic": float(t2_stat),
                    "f_statistic": float(f_stat),
                    "dimensions": p,
                },
            )

        except Exception as e:
            logger.error(f"❌ Hotelling T² test failed: {e}")
            return self._create_failed_result("hotelling_t2")

    async def pca_based_drift_detection(
        self,
        reference_data: np.ndarray,
        current_data: np.ndarray,
        n_components: int | None = None,
    ) -> MultivariateDriftResult:
        """Detect drift using PCA-based dimensionality reduction"""
        start_time = datetime.utcnow()

        try:
            # Determine number of components
            if n_components is None:
                n_components = min(10, reference_data.shape[1])

            # Perform PCA on reference data
            ref_centered = reference_data - np.mean(reference_data, axis=0)
            cov_matrix = np.cov(ref_centered.T)
            eigenvals, eigenvecs = np.linalg.eigh(cov_matrix)

            # Sort by eigenvalue magnitude
            idx = np.argsort(eigenvals)[::-1]
            eigenvals = eigenvals[idx]
            eigenvecs = eigenvecs[:, idx]

            # Select top components
            top_components = eigenvecs[:, :n_components]

            # Project both datasets
            ref_projected = np.dot(ref_centered, top_components)
            curr_centered = current_data - np.mean(current_data, axis=0)
            curr_projected = np.dot(curr_centered, top_components)

            # Calculate drift in projected space using energy distance
            projected_drift = await self._calculate_energy_distance(ref_projected, curr_projected)

            # Calculate explained variance
            explained_variance = np.sum(eigenvals[:n_components]) / np.sum(eigenvals)

            # Determine detection
            threshold = 0.3
            detected = projected_drift > threshold
            confidence = (
                min(0.95, projected_drift / threshold)
                if detected
                else max(0.1, 1.0 - projected_drift)
            )

            computation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return MultivariateDriftResult(
                method_name="pca_drift",
                drift_score=float(projected_drift),
                detected=detected,
                confidence=float(confidence),
                computation_time_ms=float(computation_time),
                metadata={
                    "n_components": n_components,
                    "explained_variance": float(explained_variance),
                    "original_dimensions": reference_data.shape[1],
                },
            )

        except Exception as e:
            logger.error(f"❌ PCA drift detection failed: {e}")
            return self._create_failed_result("pca_drift")

    async def _run_drift_method(
        self, method: str, reference_data: np.ndarray, current_data: np.ndarray
    ) -> MultivariateDriftResult:
        """Run specific drift detection method"""
        if method == "maximum_mean_discrepancy":
            return await self.maximum_mean_discrepancy(reference_data, current_data)
        elif method == "energy_distance":
            return await self.energy_distance(reference_data, current_data)
        elif method == "wasserstein_distance":
            return await self.wasserstein_distance(reference_data, current_data)
        elif method == "hotelling_t2":
            return await self.hotelling_t2_test(reference_data, current_data)
        elif method == "pca_drift":
            return await self.pca_based_drift_detection(reference_data, current_data)
        else:
            raise ValueError(f"Unknown method: {method}")

    async def _calculate_mmd_kernel(self, X: np.ndarray, Y: np.ndarray, gamma: float) -> float:
        """Calculate MMD using RBF kernel with optimized computation"""
        try:
            # Optimized kernel computation for smaller samples
            n, m = min(len(X), 100), min(len(Y), 100)
            X_sample = X[:n] if len(X) > n else X
            Y_sample = Y[:m] if len(Y) > m else Y

            # Kernel computation
            def rbf_kernel_matrix(A, B):
                # Vectorized distance computation
                A_norm = np.sum(A**2, axis=1, keepdims=True)
                B_norm = np.sum(B**2, axis=1, keepdims=True)
                distances = A_norm + B_norm.T - 2 * np.dot(A, B.T)
                return np.exp(-gamma * distances)

            K_XX = rbf_kernel_matrix(X_sample, X_sample)
            K_YY = rbf_kernel_matrix(Y_sample, Y_sample)
            K_XY = rbf_kernel_matrix(X_sample, Y_sample)

            # MMD² calculation
            mmd_squared = np.mean(K_XX) + np.mean(K_YY) - 2 * np.mean(K_XY)
            mmd = np.sqrt(max(0, mmd_squared))

            return float(mmd)

        except Exception as e:
            logger.error(f"❌ MMD kernel calculation failed: {e}")
            return 0.0

    async def _calculate_energy_distance(self, X: np.ndarray, Y: np.ndarray) -> float:
        """Calculate energy distance with optimized computation"""
        try:
            # Sample for efficiency
            n, m = min(len(X), 150), min(len(Y), 150)
            X_sample = X[:n] if len(X) > n else X
            Y_sample = Y[:m] if len(Y) > m else Y

            # Vectorized distance calculations
            def pairwise_distances(A, B):
                A_norm = np.sum(A**2, axis=1, keepdims=True)
                B_norm = np.sum(B**2, axis=1, keepdims=True)
                distances = np.sqrt(A_norm + B_norm.T - 2 * np.dot(A, B.T))
                return distances

            # Energy distance components
            d_XX = np.mean(pairwise_distances(X_sample, X_sample))
            d_YY = np.mean(pairwise_distances(Y_sample, Y_sample))
            d_XY = np.mean(pairwise_distances(X_sample, Y_sample))

            energy_dist = 2 * d_XY - d_XX - d_YY

            # Normalize
            max_dist = max(d_XX, d_YY, d_XY)
            normalized_energy = energy_dist / max_dist if max_dist > 0 else 0.0

            return float(max(0.0, normalized_energy))

        except Exception as e:
            logger.error(f"❌ Energy distance calculation failed: {e}")
            return 0.0

    def _wasserstein_1d(self, x: np.ndarray, y: np.ndarray) -> float:
        """Calculate 1D Wasserstein distance"""
        try:
            # Sort arrays
            x_sorted = np.sort(x)
            y_sorted = np.sort(y)

            # Interpolate to same length
            n = min(len(x_sorted), len(y_sorted), 1000)  # Limit for efficiency
            x_interp = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(x_sorted)), x_sorted)
            y_interp = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(y_sorted)), y_sorted)

            # Calculate Wasserstein distance
            wasserstein = np.mean(np.abs(x_interp - y_interp))

            # Normalize by data range
            data_range = max(np.max(x) - np.min(x), np.max(y) - np.min(y))
            normalized_wasserstein = wasserstein / data_range if data_range > 0 else 0.0

            return float(normalized_wasserstein)

        except Exception as e:
            logger.error(f"❌ Wasserstein calculation failed: {e}")
            return 0.0

    def _sample_data(self, data: np.ndarray, max_size: int | None = None) -> np.ndarray:
        """Sample data for computational efficiency"""
        if max_size is None:
            max_size = self.max_samples

        if len(data) <= max_size:
            return data

        # Random sampling
        indices = np.random.choice(len(data), max_size, replace=False)
        return data[indices]

    def _create_failed_result(self, method_name: str) -> MultivariateDriftResult:
        """Create a failed result"""
        return MultivariateDriftResult(
            method_name=method_name,
            drift_score=0.0,
            detected=False,
            confidence=0.0,
            computation_time_ms=0.0,
            metadata={"error": "Computation failed"},
        )

    def get_supported_methods(self) -> list[str]:
        """Get list of supported methods"""
        return self.supported_methods.copy()

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "multivariate_drift_analyzer",
            "status": "healthy",
            "supported_methods": len(self.supported_methods),
            "max_samples": self.max_samples,
        }
