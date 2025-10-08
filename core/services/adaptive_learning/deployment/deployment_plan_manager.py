"""
Deployment Plan Manager
======================

Manages deployment planning, validation, and strategy selection.
Extracted from ModelUpdateService god object to focus on planning concerns.
"""

import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from ..protocols.learning_protocols import (
    DeploymentStrategy,
    ModelMetadata,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class DeploymentRisk(Enum):
    """Deployment risk levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PerformanceRequirement:
    """Performance requirement for deployment"""

    metric_name: str
    min_value: float
    max_degradation_percent: float
    critical_threshold: float


@dataclass
class DeploymentConstraint:
    """Deployment constraint"""

    constraint_type: str
    description: str
    is_blocking: bool
    validation_function: str


@dataclass
class DeploymentPlan:
    """Comprehensive deployment plan"""

    plan_id: str
    model_id: str
    source_version: str
    target_version: str
    strategy: DeploymentStrategy
    risk_level: DeploymentRisk

    # Planning details
    planned_at: datetime
    estimated_duration: timedelta
    rollback_strategy: str

    # Requirements and constraints
    performance_requirements: list[PerformanceRequirement]
    deployment_constraints: list[DeploymentConstraint]

    # Validation
    pre_deployment_checks: list[str]
    post_deployment_checks: list[str]

    # Metadata
    metadata: dict[str, Any]
    approval_required: bool
    approved_by: str | None = None
    approved_at: datetime | None = None


@dataclass
class RiskAssessmentResult:
    """Risk assessment result"""

    overall_risk: DeploymentRisk
    risk_factors: list[dict[str, Any]]
    mitigation_strategies: list[str]
    confidence: float
    assessment_details: dict[str, Any]


class DeploymentPlanManager:
    """
    Manages deployment planning and strategy selection.

    Focuses solely on planning concerns - what, when, how to deploy.
    Delegates actual execution to DeploymentExecutor.
    """

    def __init__(self):
        # Plan management
        self.active_plans: dict[str, DeploymentPlan] = {}
        self.plan_history: list[DeploymentPlan] = []

        # Strategy configuration
        self.strategy_rules: dict[str, dict[str, Any]] = self._initialize_strategy_rules()
        self.risk_thresholds: dict[str, float] = self._initialize_risk_thresholds()

        # Performance baselines
        self.performance_baselines: dict[str, dict[str, float]] = {}

        logger.info("🎯 Deployment Plan Manager initialized")

    async def create_deployment_plan(
        self,
        model_id: str,
        source_version: str,
        target_version: str,
        target_metadata: ModelMetadata,
        requirements: list[PerformanceRequirement] | None = None,
        constraints: list[DeploymentConstraint] | None = None,
    ) -> DeploymentPlan | None:
        """Create comprehensive deployment plan"""
        try:
            plan_id = f"plan_{model_id}_{target_version}_{uuid.uuid4().hex[:8]}"

            # Assess deployment risk
            risk_assessment = await self._assess_deployment_risk(
                model_id, source_version, target_version, target_metadata
            )

            # Select deployment strategy
            strategy = await self._select_deployment_strategy(
                model_id, risk_assessment.overall_risk, target_metadata
            )

            # Estimate deployment duration
            estimated_duration = await self._estimate_deployment_duration(
                strategy, risk_assessment.overall_risk
            )

            # Generate checks
            pre_checks = await self._generate_pre_deployment_checks(model_id, target_metadata)
            post_checks = await self._generate_post_deployment_checks(model_id, target_metadata)

            # Determine approval requirement
            approval_required = await self._requires_approval(
                risk_assessment.overall_risk, strategy
            )

            plan = DeploymentPlan(
                plan_id=plan_id,
                model_id=model_id,
                source_version=source_version,
                target_version=target_version,
                strategy=strategy,
                risk_level=risk_assessment.overall_risk,
                planned_at=datetime.utcnow(),
                estimated_duration=estimated_duration,
                rollback_strategy=await self._select_rollback_strategy(
                    strategy, risk_assessment.overall_risk
                ),
                performance_requirements=requirements
                or await self._generate_default_requirements(model_id),
                deployment_constraints=constraints or [],
                pre_deployment_checks=pre_checks,
                post_deployment_checks=post_checks,
                metadata={
                    "risk_assessment": asdict(risk_assessment),
                    "target_metadata": asdict(target_metadata),
                    "planning_context": {
                        "created_by": "deployment_plan_manager",
                        "planning_version": "1.0.0",
                    },
                },
                approval_required=approval_required,
            )

            self.active_plans[plan_id] = plan

            logger.info(
                f"📋 Created deployment plan {plan_id}: {strategy.value} strategy, {risk_assessment.overall_risk.value} risk"
            )
            return plan

        except Exception as e:
            logger.error(f"❌ Failed to create deployment plan: {e}")
            return None

    async def validate_deployment_plan(self, plan_id: str) -> ValidationResult:
        """Validate deployment plan"""
        try:
            if plan_id not in self.active_plans:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Plan {plan_id} not found"],
                    warnings=[],
                    validation_details={},
                )

            plan = self.active_plans[plan_id]
            errors = []
            warnings = []
            details = {}

            # Validate performance requirements
            perf_validation = await self._validate_performance_requirements(plan)
            if not perf_validation["valid"]:
                errors.extend(perf_validation["errors"])
            warnings.extend(perf_validation["warnings"])
            details["performance"] = perf_validation

            # Validate constraints
            constraint_validation = await self._validate_deployment_constraints(plan)
            if not constraint_validation["valid"]:
                errors.extend(constraint_validation["errors"])
            details["constraints"] = constraint_validation

            # Validate strategy compatibility
            strategy_validation = await self._validate_strategy_compatibility(plan)
            if not strategy_validation["valid"]:
                errors.extend(strategy_validation["errors"])
            details["strategy"] = strategy_validation

            # Check resource availability
            resource_validation = await self._validate_resource_availability(plan)
            if not resource_validation["valid"]:
                errors.extend(resource_validation["errors"])
            warnings.extend(resource_validation["warnings"])
            details["resources"] = resource_validation

            is_valid = len(errors) == 0

            logger.info(f"🔍 Plan validation: {'✅ VALID' if is_valid else '❌ INVALID'}")

            return ValidationResult(
                is_valid=is_valid, errors=errors, warnings=warnings, validation_details=details
            )

        except Exception as e:
            logger.error(f"❌ Plan validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {e}"],
                warnings=[],
                validation_details={},
            )

    async def approve_deployment_plan(self, plan_id: str, approver: str) -> bool:
        """Approve deployment plan"""
        try:
            if plan_id not in self.active_plans:
                logger.error(f"❌ Plan {plan_id} not found")
                return False

            plan = self.active_plans[plan_id]

            if not plan.approval_required:
                logger.info(f"ℹ️ Plan {plan_id} doesn't require approval")
                return True

            plan.approved_by = approver
            plan.approved_at = datetime.utcnow()

            logger.info(f"✅ Plan {plan_id} approved by {approver}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to approve plan: {e}")
            return False

    async def get_deployment_plan(self, plan_id: str) -> DeploymentPlan | None:
        """Get deployment plan"""
        return self.active_plans.get(plan_id)

    async def list_active_plans(self, model_id: str | None = None) -> list[DeploymentPlan]:
        """List active deployment plans"""
        plans = list(self.active_plans.values())

        if model_id:
            plans = [p for p in plans if p.model_id == model_id]

        return sorted(plans, key=lambda p: p.planned_at, reverse=True)

    async def cancel_deployment_plan(self, plan_id: str, reason: str) -> bool:
        """Cancel deployment plan"""
        try:
            if plan_id not in self.active_plans:
                logger.error(f"❌ Plan {plan_id} not found")
                return False

            plan = self.active_plans.pop(plan_id)
            plan.metadata["cancellation"] = {
                "cancelled_at": datetime.utcnow().isoformat(),
                "reason": reason,
            }

            self.plan_history.append(plan)

            logger.info(f"🚫 Cancelled deployment plan {plan_id}: {reason}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to cancel plan: {e}")
            return False

    async def _assess_deployment_risk(
        self,
        model_id: str,
        source_version: str,
        target_version: str,
        target_metadata: ModelMetadata,
    ) -> RiskAssessmentResult:
        """Assess deployment risk"""

        risk_factors = []
        mitigation_strategies = []

        # Model performance risk
        if hasattr(target_metadata, "performance_metrics"):
            perf_metrics = target_metadata.performance_metrics
            if model_id in self.performance_baselines:
                baseline = self.performance_baselines[model_id]

                for metric, value in perf_metrics.items():
                    if metric in baseline:
                        degradation = (baseline[metric] - value) / baseline[metric]
                        if degradation > 0.1:  # 10% degradation
                            risk_factors.append(
                                {
                                    "type": "performance_degradation",
                                    "metric": metric,
                                    "degradation": degradation,
                                    "severity": "high" if degradation > 0.2 else "medium",
                                }
                            )
                            mitigation_strategies.append(
                                f"Monitor {metric} closely during deployment"
                            )

        # Model complexity risk
        if hasattr(target_metadata, "model_size"):
            size_mb = target_metadata.model_size / (1024 * 1024)
            if size_mb > 500:  # Large model
                risk_factors.append(
                    {"type": "model_size", "size_mb": size_mb, "severity": "medium"}
                )
                mitigation_strategies.append("Use staged deployment for large models")

        # Architecture change risk
        if hasattr(target_metadata, "architecture") and hasattr(
            target_metadata, "previous_architecture"
        ):
            if target_metadata.architecture != target_metadata.previous_architecture:
                risk_factors.append(
                    {
                        "type": "architecture_change",
                        "from": target_metadata.previous_architecture,
                        "to": target_metadata.architecture,
                        "severity": "high",
                    }
                )
                mitigation_strategies.append("Extensive pre-deployment testing required")

        # Calculate overall risk
        high_risk_count = len([f for f in risk_factors if f.get("severity") == "high"])
        medium_risk_count = len([f for f in risk_factors if f.get("severity") == "medium"])

        if high_risk_count >= 2:
            overall_risk = DeploymentRisk.CRITICAL
        elif high_risk_count >= 1:
            overall_risk = DeploymentRisk.HIGH
        elif medium_risk_count >= 2:
            overall_risk = DeploymentRisk.MEDIUM
        else:
            overall_risk = DeploymentRisk.LOW

        confidence = max(0.5, 1.0 - (len(risk_factors) * 0.1))

        return RiskAssessmentResult(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            confidence=confidence,
            assessment_details={
                "total_risk_factors": len(risk_factors),
                "high_risk_factors": high_risk_count,
                "medium_risk_factors": medium_risk_count,
                "assessment_timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _select_deployment_strategy(
        self, model_id: str, risk_level: DeploymentRisk, metadata: ModelMetadata
    ) -> DeploymentStrategy:
        """Select optimal deployment strategy"""

        # Risk-based strategy selection
        if risk_level == DeploymentRisk.CRITICAL:
            return DeploymentStrategy.CANARY
        elif risk_level == DeploymentRisk.HIGH:
            return DeploymentStrategy.BLUE_GREEN
        elif risk_level == DeploymentRisk.MEDIUM:
            return DeploymentStrategy.ROLLING
        else:
            return DeploymentStrategy.DIRECT

    async def _estimate_deployment_duration(
        self, strategy: DeploymentStrategy, risk_level: DeploymentRisk
    ) -> timedelta:
        """Estimate deployment duration"""

        base_durations = {
            DeploymentStrategy.DIRECT: 15,  # 15 minutes
            DeploymentStrategy.ROLLING: 30,  # 30 minutes
            DeploymentStrategy.BLUE_GREEN: 45,  # 45 minutes
            DeploymentStrategy.CANARY: 120,  # 2 hours
        }

        risk_multipliers = {
            DeploymentRisk.LOW: 1.0,
            DeploymentRisk.MEDIUM: 1.2,
            DeploymentRisk.HIGH: 1.5,
            DeploymentRisk.CRITICAL: 2.0,
        }

        base_minutes = base_durations[strategy]
        multiplier = risk_multipliers[risk_level]

        return timedelta(minutes=int(base_minutes * multiplier))

    async def _generate_pre_deployment_checks(
        self, model_id: str, metadata: ModelMetadata
    ) -> list[str]:
        """Generate pre-deployment checks"""

        checks = [
            "model_validation",
            "performance_benchmarking",
            "resource_availability",
            "dependency_verification",
        ]

        # Add specific checks based on metadata
        if hasattr(metadata, "requires_gpu") and metadata.requires_gpu:
            checks.append("gpu_availability")

        if hasattr(metadata, "model_size") and metadata.model_size > 100 * 1024 * 1024:  # 100MB
            checks.append("storage_capacity")

        return checks

    async def _generate_post_deployment_checks(
        self, model_id: str, metadata: ModelMetadata
    ) -> list[str]:
        """Generate post-deployment checks"""

        return [
            "health_check",
            "performance_validation",
            "prediction_accuracy",
            "latency_verification",
            "error_rate_monitoring",
        ]

    async def _requires_approval(
        self, risk_level: DeploymentRisk, strategy: DeploymentStrategy
    ) -> bool:
        """Determine if deployment requires approval"""

        # High-risk deployments always require approval
        if risk_level in [DeploymentRisk.HIGH, DeploymentRisk.CRITICAL]:
            return True

        # Production strategies require approval
        if strategy in [DeploymentStrategy.BLUE_GREEN, DeploymentStrategy.CANARY]:
            return True

        return False

    async def _select_rollback_strategy(
        self, deployment_strategy: DeploymentStrategy, risk_level: DeploymentRisk
    ) -> str:
        """Select rollback strategy"""

        if deployment_strategy == DeploymentStrategy.BLUE_GREEN:
            return "instant_switch"
        elif deployment_strategy == DeploymentStrategy.CANARY:
            return "traffic_reduction"
        elif deployment_strategy == DeploymentStrategy.ROLLING:
            return "reverse_rolling"
        else:
            return "version_revert"

    async def _generate_default_requirements(self, model_id: str) -> list[PerformanceRequirement]:
        """Generate default performance requirements"""

        return [
            PerformanceRequirement(
                metric_name="accuracy",
                min_value=0.8,
                max_degradation_percent=5.0,
                critical_threshold=0.7,
            ),
            PerformanceRequirement(
                metric_name="latency_p95",
                min_value=0.0,
                max_degradation_percent=20.0,
                critical_threshold=2000.0,  # 2 seconds
            ),
            PerformanceRequirement(
                metric_name="error_rate",
                min_value=0.0,
                max_degradation_percent=100.0,
                critical_threshold=0.05,  # 5%
            ),
        ]

    async def _validate_performance_requirements(self, plan: DeploymentPlan) -> dict[str, Any]:
        """Validate performance requirements"""

        errors = []
        warnings = []

        for req in plan.performance_requirements:
            if req.min_value < 0 and req.metric_name not in ["error_rate"]:
                errors.append(f"Invalid min_value for {req.metric_name}: {req.min_value}")

            if req.max_degradation_percent < 0:
                errors.append(
                    f"Invalid max_degradation_percent for {req.metric_name}: {req.max_degradation_percent}"
                )

            if req.max_degradation_percent > 50:
                warnings.append(
                    f"High degradation tolerance for {req.metric_name}: {req.max_degradation_percent}%"
                )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    async def _validate_deployment_constraints(self, plan: DeploymentPlan) -> dict[str, Any]:
        """Validate deployment constraints"""

        errors = []

        for constraint in plan.deployment_constraints:
            if not constraint.constraint_type:
                errors.append("Constraint missing type")

            if constraint.is_blocking and not constraint.validation_function:
                errors.append(
                    f"Blocking constraint {constraint.constraint_type} missing validation function"
                )

        return {"valid": len(errors) == 0, "errors": errors}

    async def _validate_strategy_compatibility(self, plan: DeploymentPlan) -> dict[str, Any]:
        """Validate strategy compatibility"""

        errors = []

        # Check strategy-risk compatibility
        if (
            plan.risk_level == DeploymentRisk.CRITICAL
            and plan.strategy == DeploymentStrategy.DIRECT
        ):
            errors.append("Critical risk level incompatible with direct deployment")

        return {"valid": len(errors) == 0, "errors": errors}

    async def _validate_resource_availability(self, plan: DeploymentPlan) -> dict[str, Any]:
        """Validate resource availability"""

        # Mock validation - in real implementation, check actual resources
        warnings = []

        if plan.strategy in [DeploymentStrategy.BLUE_GREEN, DeploymentStrategy.CANARY]:
            warnings.append("Strategy requires additional resources for parallel deployment")

        return {"valid": True, "errors": [], "warnings": warnings}

    def _initialize_strategy_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize deployment strategy rules"""

        return {
            "risk_based": {
                "low": DeploymentStrategy.DIRECT,
                "medium": DeploymentStrategy.ROLLING,
                "high": DeploymentStrategy.BLUE_GREEN,
                "critical": DeploymentStrategy.CANARY,
            }
        }

    def _initialize_risk_thresholds(self) -> dict[str, float]:
        """Initialize risk assessment thresholds"""

        return {
            "performance_degradation_low": 0.05,
            "performance_degradation_medium": 0.10,
            "performance_degradation_high": 0.20,
            "model_size_large_mb": 500,
            "model_size_huge_mb": 1000,
        }

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""

        return {
            "service": "deployment_plan_manager",
            "status": "healthy",
            "active_plans": len(self.active_plans),
            "total_plans_created": len(self.plan_history) + len(self.active_plans),
            "strategy_rules_loaded": len(self.strategy_rules),
            "performance_baselines": len(self.performance_baselines),
        }
