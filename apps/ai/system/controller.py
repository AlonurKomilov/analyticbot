"""
System AI Controller
====================

Central AI controller for infrastructure/worker management.
Configured via environment variables (not user-facing).
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from apps.ai.shared.models import (
    Action,
    ActionResult,
    ActionStatus,
    ActionType,
    ApprovalLevel,
    Decision,
    DecisionType,
    WorkerStatus,
)
from apps.ai.system.config import AIApprovalMode, SystemAIConfig, get_system_ai_config
from apps.ai.system.registry.worker_registry import WorkerRegistry

logger = logging.getLogger(__name__)


class SystemAIController:
    """
    System-level AI controller for autonomous worker management.
    
    This handles infrastructure concerns:
    - Worker monitoring (MTProto, Bot, API, Celery)
    - Auto-scaling decisions
    - Resource optimization
    - Health monitoring and auto-healing
    
    Configured via environment variables - not user configurable.
    For user-facing AI, see apps.ai.user.UserAIAgent.
    """

    def __init__(self, config: SystemAIConfig | None = None):
        self.config = config or get_system_ai_config()
        
        # Components
        self.registry = WorkerRegistry()

        # State
        self.is_running = False
        self.monitoring_task: asyncio.Task | None = None

        # Decision tracking
        self.decisions_made: list[Decision] = []
        self.actions_executed: list[Action] = []

        # Statistics
        self.stats = {
            "started_at": None,
            "total_decisions": 0,
            "auto_executed": 0,
            "pending_approval": 0,
            "successful_actions": 0,
            "failed_actions": 0,
        }

        logger.info(
            f"🤖 System AI Controller initialized "
            f"(enabled={self.config.enabled}, mode={self.config.approval_mode.value})"
        )

    async def start(self):
        """Start the System AI controller"""
        if not self.config.enabled:
            logger.warning("⚠️  System AI Controller is disabled")
            return False

        if self.is_running:
            logger.warning("⚠️  System AI Controller already running")
            return False

        try:
            # Discover workers
            await self.registry.discover_workers()

            # Start monitoring loop
            self.is_running = True
            self.stats["started_at"] = datetime.utcnow().isoformat()
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

            logger.info("✅ System AI Controller started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start System AI Controller: {e}")
            return False

    async def stop(self):
        """Stop the System AI controller"""
        if not self.is_running:
            return

        self.is_running = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("🛑 System AI Controller stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("👀 Starting System AI monitoring loop...")

        while self.is_running:
            try:
                # Collect worker states
                workers = await self.registry.list_workers()

                for worker_def in workers:
                    if not worker_def.ai_manageable:
                        continue

                    # Get current state
                    state = await self.registry.get_worker_state(worker_def.name)

                    if not state:
                        continue

                    # Analyze worker health
                    await self._analyze_worker(worker_def, state)

                # Sleep between checks
                await asyncio.sleep(60)  # Check every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _analyze_worker(self, worker_def: Any, state: Any):
        """Analyze a worker and make decisions if needed"""
        try:
            # Check if worker is unhealthy
            if state.status == WorkerStatus.ERROR or state.status == WorkerStatus.UNHEALTHY:
                logger.warning(
                    f"⚠️  Worker {worker_def.name} is {state.status.value}: {state.status_message}"
                )
                # TODO: Decide on action (restart, scale, etc.)

            # Check CPU usage
            if state.cpu_percent > 85.0:
                logger.warning(
                    f"⚠️  Worker {worker_def.name} high CPU: {state.cpu_percent}%"
                )
                # TODO: Decide on action (scale up, adjust interval, etc.)

            # Check memory usage
            if state.memory_percent > 85.0:
                logger.warning(
                    f"⚠️  Worker {worker_def.name} high memory: {state.memory_percent}%"
                )
                # TODO: Decide on action (restart, increase limit, etc.)

            # Check error rate
            if state.errors_count > 10:
                logger.warning(
                    f"⚠️  Worker {worker_def.name} has {state.errors_count} errors"
                )
                # TODO: Analyze errors and decide on action

        except Exception as e:
            logger.error(f"❌ Error analyzing worker {worker_def.name}: {e}")

    async def make_decision(
        self, decision_type: DecisionType, target_worker: str, **kwargs
    ) -> Decision | None:
        """
        Make a decision about worker management.

        This is the core AI decision-making method. In Phase 1, it's rule-based.
        In later phases, this will use LLM reasoning.
        """
        try:
            # Get worker info
            worker_def = await self.registry.get_worker(target_worker)
            if not worker_def or not worker_def.ai_manageable:
                logger.warning(f"⚠️  Worker {target_worker} is not AI-manageable")
                return None

            # Create decision context
            from apps.ai.shared.models.decision import DecisionContext

            context = DecisionContext(
                trigger=kwargs.get("trigger", "manual"),
                trigger_data=kwargs.get("trigger_data", {}),
            )

            # Create decision
            decision = Decision(
                decision_id=f"dec_{datetime.utcnow().timestamp()}",
                decision_type=decision_type,
                target_worker=target_worker,
                action=kwargs.get("action", ""),
                action_params=kwargs.get("params", {}),
                reasoning=kwargs.get("reasoning", "Automated decision by AI worker controller"),
                approval_level=self._determine_approval_level(decision_type, target_worker),
                risk_level=kwargs.get("risk_level", "low"),
                potential_impact=kwargs.get("impact", ""),
                confidence_score=kwargs.get("confidence", 0.8),
                context=context,
            )

            self.decisions_made.append(decision)
            self.stats["total_decisions"] += 1

            if decision.approval_level == ApprovalLevel.AUTO:
                # Can execute automatically
                decision.approved = True
                decision.approved_by = "ai_controller"
                decision.approved_at = datetime.utcnow()

            else:
                # Needs approval
                self.stats["pending_approval"] += 1
                logger.info(
                    f"📋 Decision {decision.decision_id} requires {decision.approval_level.value} approval"
                )

            return decision

        except Exception as e:
            logger.error(f"❌ Failed to make decision: {e}")
            return None

    def _determine_approval_level(self, decision_type: DecisionType, target_worker: str) -> ApprovalLevel:
        """Determine approval level for a decision"""
        # Phase 1: Conservative approach - most things need approval
        risky_actions = {
            DecisionType.SCALE: ApprovalLevel.REVIEW,
            DecisionType.RESTART: ApprovalLevel.AUTO,  # Restart is generally safe
            DecisionType.CONFIGURE: ApprovalLevel.APPROVAL,  # Config changes need approval
            DecisionType.OPTIMIZE: ApprovalLevel.AUTO,  # Optimization is safe
        }

        return risky_actions.get(decision_type, ApprovalLevel.REVIEW)

    async def execute_decision(self, decision: Decision) -> ActionResult | None:
        """Execute an approved decision"""
        try:
            if not decision.approved:
                logger.warning(f"⚠️  Decision {decision.decision_id} not approved yet")
                return None

            # Create action from decision
            action = Action(
                action_id=f"act_{datetime.utcnow().timestamp()}",
                action_type=ActionType[decision.action.upper()]
                if hasattr(ActionType, decision.action.upper())
                else ActionType.UPDATE_CONFIG,
                target_worker=decision.target_worker,
                parameters=decision.action_params,
                triggered_by="system_ai",
                related_decision_id=decision.decision_id,
                dry_run=self.config.dry_run,
            )

            # Execute action
            result = await self._execute_action(action)

            # Update decision
            decision.executed = True
            decision.executed_at = datetime.utcnow()
            decision.execution_result = result.message if result else "Failed"

            return result

        except Exception as e:
            logger.error(f"❌ Failed to execute decision {decision.decision_id}: {e}")
            return None

    async def _execute_action(self, action: Action) -> ActionResult:
        """Execute a specific action"""
        try:
            action.status = ActionStatus.EXECUTING
            action.started_at = datetime.utcnow()

            if action.dry_run:
                logger.info(f"🧪 [DRY RUN] Would execute: {action.action_type.value}")
                return ActionResult(
                    action_id=action.action_id,
                    success=True,
                    message="Dry run - no actual changes made",
                )

            # TODO: Implement actual action execution
            # For now, just log
            logger.info(f"⚙️  Executing action: {action.action_type.value}")

            action.status = ActionStatus.COMPLETED
            action.completed_at = datetime.utcnow()

            result = ActionResult(
                action_id=action.action_id, success=True, message="Action executed successfully"
            )

            self.stats["successful_actions"] += 1
            self.actions_executed.append(action)

            return result

        except Exception as e:
            logger.error(f"❌ Action execution failed: {e}")
            action.status = ActionStatus.FAILED
            action.error_message = str(e)

            self.stats["failed_actions"] += 1

            return ActionResult(
                action_id=action.action_id, success=False, message=f"Action failed: {e}"
            )

    async def get_status(self) -> dict[str, Any]:
        """Get System AI controller status"""
        return {
            "enabled": self.config.enabled,
            "status": "running" if self.is_running else "stopped",
            "mode": self.config.approval_mode.value,
            "dry_run": self.config.dry_run,
            "stats": self.stats,
            "registry_stats": await self.registry.get_registry_stats(),
            "pending_decisions": len([d for d in self.decisions_made if not d.approved]),
            "config": {
                "monitoring_interval": self.config.monitoring_interval_seconds,
                "auto_scale_enabled": self.config.auto_scale_enabled,
                "max_decisions_per_hour": self.config.max_decisions_per_hour,
                "max_actions_per_hour": self.config.max_actions_per_hour,
            }
        }
