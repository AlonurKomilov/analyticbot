"""
Version Comparator Service
===========================

Handles comparison operations between model versions
including metrics, metadata, and change analysis.
"""

import logging
from typing import Any

from core.services.adaptive_learning.versioning.models import ModelVersion

from ..management.version_manager import VersionManager

logger = logging.getLogger(__name__)


class VersionComparator:
    """
    Provides version comparison capabilities.

    Responsibilities:
    - Compare version metrics
    - Analyze version differences
    - Compare metadata
    - Calculate improvement metrics
    - Generate comparison reports
    """

    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager
        logger.info("🔍 Version Comparator initialized")

    async def compare_versions(self, version_id1: str, version_id2: str) -> dict[str, Any]:
        """Compare two model versions"""
        try:
            version1 = await self.version_manager.get_version(version_id1)
            version2 = await self.version_manager.get_version(version_id2)

            if not version1 or not version2:
                logger.error("❌ One or both versions not found")
                return {
                    "error": "Version(s) not found",
                    "version1_found": version1 is not None,
                    "version2_found": version2 is not None,
                }

            comparison = {
                "version1": {
                    "version_id": version1.version_id,
                    "version_number": version1.version_number,
                    "created_at": version1.created_at.isoformat(),
                    "status": version1.status.value,
                    "deployment_stage": version1.deployment_stage.value,
                },
                "version2": {
                    "version_id": version2.version_id,
                    "version_number": version2.version_number,
                    "created_at": version2.created_at.isoformat(),
                    "status": version2.status.value,
                    "deployment_stage": version2.deployment_stage.value,
                },
                "time_difference_hours": (version2.created_at - version1.created_at).total_seconds()
                / 3600,
                "size_difference_bytes": version2.size_bytes - version1.size_bytes,
                "is_parent_child": version2.parent_version == version1.version_id,
            }

            # Compare metrics
            metrics_comparison = await self._compare_metrics(version1, version2)
            comparison["metrics"] = metrics_comparison

            # Compare metadata
            metadata_comparison = await self._compare_metadata(version1, version2)
            comparison["metadata"] = metadata_comparison

            # Calculate improvements
            improvements = await self._calculate_improvements(version1, version2)
            comparison["improvements"] = improvements

            # Generate summary
            summary = await self._generate_comparison_summary(comparison)
            comparison["summary"] = summary

            logger.info(f"✅ Comparison completed: {version_id1} vs {version_id2}")
            return comparison

        except Exception as e:
            logger.error(f"❌ Failed to compare versions: {e}")
            return {"error": str(e)}

    async def _compare_metrics(
        self, version1: ModelVersion, version2: ModelVersion
    ) -> dict[str, Any]:
        """Compare performance metrics between versions"""
        metrics1 = version1.metrics
        metrics2 = version2.metrics

        comparison = {}

        # Compare common metrics
        all_metrics = set(metrics1.keys()) | set(metrics2.keys())

        for metric_name in all_metrics:
            value1 = metrics1.get(metric_name)
            value2 = metrics2.get(metric_name)

            metric_comparison = {
                "version1_value": value1,
                "version2_value": value2,
                "present_in_version1": value1 is not None,
                "present_in_version2": value2 is not None,
            }

            # Calculate change if both present
            if value1 is not None and value2 is not None:
                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    difference = value2 - value1
                    if value1 != 0:
                        percent_change = (difference / value1) * 100
                    else:
                        percent_change = None

                    metric_comparison["difference"] = difference
                    metric_comparison["percent_change"] = percent_change
                    metric_comparison["improved"] = difference > 0  # Assuming higher is better

            comparison[metric_name] = metric_comparison

        return comparison

    async def _compare_metadata(
        self, version1: ModelVersion, version2: ModelVersion
    ) -> dict[str, Any]:
        """Compare metadata between versions"""
        return {
            "tags": {
                "version1": version1.tags,
                "version2": version2.tags,
                "added": [t for t in version2.tags if t not in version1.tags],
                "removed": [t for t in version1.tags if t not in version2.tags],
            },
            "description": {
                "version1": version1.description,
                "version2": version2.description,
                "changed": version1.description != version2.description,
            },
            "dependencies": {
                "version1": version1.dependencies,
                "version2": version2.dependencies,
                "changed": version1.dependencies != version2.dependencies,
            },
            "configuration": {
                "version1_keys": list(version1.configuration.keys()),
                "version2_keys": list(version2.configuration.keys()),
                "changed": version1.configuration != version2.configuration,
            },
        }

    async def _calculate_improvements(
        self, version1: ModelVersion, version2: ModelVersion
    ) -> dict[str, Any]:
        """Calculate improvement metrics"""
        improvements = {
            "total_metrics_improved": 0,
            "total_metrics_degraded": 0,
            "overall_improvement": 0.0,
            "improved_metrics": [],
            "degraded_metrics": [],
        }

        metrics1 = version1.metrics
        metrics2 = version2.metrics

        for metric_name in metrics1.keys():
            if metric_name in metrics2:
                value1 = metrics1[metric_name]
                value2 = metrics2[metric_name]

                if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    if value2 > value1:
                        improvements["total_metrics_improved"] += 1
                        improvements["improved_metrics"].append(metric_name)
                    elif value2 < value1:
                        improvements["total_metrics_degraded"] += 1
                        improvements["degraded_metrics"].append(metric_name)

        # Calculate overall improvement score
        total_comparisons = (
            improvements["total_metrics_improved"] + improvements["total_metrics_degraded"]
        )
        if total_comparisons > 0:
            improvements["overall_improvement"] = (
                (improvements["total_metrics_improved"] - improvements["total_metrics_degraded"])
                / total_comparisons
            ) * 100

        return improvements

    async def _generate_comparison_summary(self, comparison: dict[str, Any]) -> dict[str, Any]:
        """Generate a summary of the comparison"""
        summary = {
            "recommendation": "unknown",
            "key_findings": [],
            "overall_verdict": "",
        }

        # Check improvements
        if "improvements" in comparison:
            improvements = comparison["improvements"]
            improvement_score = improvements.get("overall_improvement", 0)

            if improvement_score > 20:
                summary["recommendation"] = "upgrade"
                summary["overall_verdict"] = "Version 2 shows significant improvements"
            elif improvement_score > 0:
                summary["recommendation"] = "consider_upgrade"
                summary["overall_verdict"] = "Version 2 shows modest improvements"
            elif improvement_score < -20:
                summary["recommendation"] = "stay"
                summary["overall_verdict"] = "Version 1 performs better"
            else:
                summary["recommendation"] = "equivalent"
                summary["overall_verdict"] = "Versions are roughly equivalent"

            # Add key findings
            if improvements["improved_metrics"]:
                summary["key_findings"].append(
                    f"Improved metrics: {', '.join(improvements['improved_metrics'][:3])}"
                )

            if improvements["degraded_metrics"]:
                summary["key_findings"].append(
                    f"Degraded metrics: {', '.join(improvements['degraded_metrics'][:3])}"
                )

        # Check size difference
        if "size_difference_bytes" in comparison:
            size_diff = comparison["size_difference_bytes"]
            if abs(size_diff) > 1024 * 1024:  # > 1 MB
                summary["key_findings"].append(
                    f"Size difference: {size_diff / (1024 * 1024):.2f} MB"
                )

        # Check if parent-child relationship
        if comparison.get("is_parent_child"):
            summary["key_findings"].append("Version 2 is derived from Version 1")

        return summary

    async def compare_to_baseline(
        self, version_id: str, baseline_version_id: str | None = None
    ) -> dict[str, Any]:
        """
        Compare a version to baseline (first or specified version).

        Args:
            version_id: Version to compare
            baseline_version_id: Baseline version (if None, uses first version)
        """
        try:
            version = await self.version_manager.get_version(version_id)

            if not version:
                return {"error": "Version not found"}

            # Get baseline
            if baseline_version_id:
                baseline = await self.version_manager.get_version(baseline_version_id)
            else:
                # Get first version for this model
                versions = await self.version_manager.get_versions(model_id=version.model_id)
                versions.sort(key=lambda v: v.created_at)
                baseline = versions[0] if versions else None

            if not baseline:
                return {"error": "Baseline version not found"}

            # Perform comparison
            return await self.compare_versions(baseline.version_id, version.version_id)

        except Exception as e:
            logger.error(f"❌ Failed to compare to baseline: {e}")
            return {"error": str(e)}

    async def get_version_lineage(self, version_id: str) -> list[dict[str, Any]]:
        """
        Get the lineage of a version (chain of parent versions).

        Returns list from oldest to newest ancestor.
        """
        try:
            lineage = []
            current_id = version_id

            while current_id:
                version = await self.version_manager.get_version(current_id)

                if not version:
                    break

                lineage.append(
                    {
                        "version_id": version.version_id,
                        "version_number": version.version_number,
                        "created_at": version.created_at.isoformat(),
                        "description": version.description,
                        "metrics": version.metrics,
                    }
                )

                current_id = version.parent_version

            # Reverse to show oldest first
            lineage.reverse()

            logger.info(f"✅ Retrieved lineage for {version_id}: {len(lineage)} versions")
            return lineage

        except Exception as e:
            logger.error(f"❌ Failed to get version lineage: {e}")
            return []

    async def health_check(self) -> dict[str, Any]:
        """Check version comparator health"""
        return {"service": "version_comparator", "status": "healthy"}
