"""
Predictive Workflow Orchestrator Service
========================================

Responsible for coordinating workflow execution strategies.

Single Responsibility:
- Determine execution strategies (parallel vs sequential)
- Execute parallel intelligence workflows
- Execute sequential intelligence workflows
- Manage workflow timing and timeouts
- Generate cache keys for results
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import IntelligenceContext

logger = logging.getLogger(__name__)


class PredictiveWorkflowOrchestratorService:
    """
    Workflow orchestration microservice for predictive intelligence.

    Single responsibility: Coordinate workflow execution strategies and timing.
    """

    def __init__(self, service_executor, config_manager=None):
        """Initialize workflow orchestrator"""
        self.service_executor = service_executor
        self.config_manager = config_manager

        # Workflow configuration
        self.workflow_config = {
            "timeouts": {
                "contextual_analysis": 30,  # seconds
                "temporal_intelligence": 45,
                "predictive_modeling": 60,
                "cross_channel_analysis": 90,
                "overall_workflow": 300,
            },
            "parallel_execution": {
                "enabled": True,
                "max_concurrent_services": 4,
                "fallback_sequential": True,
            },
            "workflow_priorities": {
                "comprehensive": ["contextual", "temporal", "modeling", "cross_channel"],
                "performance_focused": ["temporal", "modeling", "contextual"],
                "prediction_focused": ["modeling", "temporal", "cross_channel"],
                "analysis_focused": ["contextual", "cross_channel", "temporal"],
            },
        }

        # Workflow tracking
        self.active_workflows: dict[str, Any] = {}

    def determine_execution_strategy(
        self, context: IntelligenceContext, request: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Determine optimal execution strategy based on context and request.

        Args:
            context: Intelligence context for analysis
            request: Analysis request with parameters

        Returns:
            Execution strategy with services, priority, and timing
        """

        # Map context to priority order
        priority_mapping = {
            IntelligenceContext.COMPREHENSIVE: "comprehensive",
            IntelligenceContext.PERFORMANCE_FOCUSED: "performance_focused",
            IntelligenceContext.COMPETITIVE_ANALYSIS: "analysis_focused",
            IntelligenceContext.MARKET_INTELLIGENCE: "analysis_focused",
        }

        priority_key = priority_mapping.get(context, "comprehensive")
        service_priority = self.workflow_config["workflow_priorities"][priority_key]

        # Determine parallel vs sequential execution
        parallel_enabled = self.workflow_config["parallel_execution"]["enabled"]
        channel_count = len(request.get("channel_ids", []))

        # Use parallel for multiple channels and comprehensive analysis
        use_parallel = parallel_enabled and (
            channel_count > 2 or context == IntelligenceContext.COMPREHENSIVE
        )

        return {
            "parallel": use_parallel,
            "services": service_priority,
            "priority_order": service_priority,
            "estimated_duration": self.estimate_workflow_duration(service_priority, use_parallel),
            "context": context.value,
        }

    def estimate_workflow_duration(self, services: list[str], parallel: bool) -> int:
        """
        Estimate workflow duration in seconds.

        Args:
            services: List of services to execute
            parallel: Whether execution is parallel

        Returns:
            Estimated duration in seconds
        """
        timeouts = self.workflow_config["timeouts"]

        if parallel:
            # Parallel execution - use maximum individual timeout plus some overhead
            max_timeout = max([timeouts.get(service, 30) for service in services])
            return max_timeout + 30  # Add overhead
        else:
            # Sequential execution - sum all timeouts
            total_timeout = sum([timeouts.get(service, 30) for service in services])
            return total_timeout + 15  # Add minimal overhead

    async def execute_parallel_workflow(
        self,
        request: dict[str, Any],
        context: IntelligenceContext,
        execution_strategy: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        """
        Execute intelligence services in parallel.

        Args:
            request: Analysis request
            context: Intelligence context
            execution_strategy: Execution strategy details
            workflow_id: Workflow identifier

        Returns:
            Results from all services
        """
        logger.info("⚡ Executing parallel intelligence workflow")

        # Create tasks for parallel execution
        tasks = {}

        if "contextual" in execution_strategy["services"]:
            if self.service_executor.contextual_service:
                tasks["contextual"] = asyncio.create_task(
                    self.service_executor.execute_contextual_analysis(request, context, workflow_id)
                )

        if "temporal" in execution_strategy["services"]:
            if self.service_executor.temporal_service:
                tasks["temporal"] = asyncio.create_task(
                    self.service_executor.execute_temporal_intelligence(
                        request, context, workflow_id
                    )
                )

        if "cross_channel" in execution_strategy["services"]:
            if self.service_executor.cross_channel_service:
                tasks["cross_channel"] = asyncio.create_task(
                    self.service_executor.execute_cross_channel_analysis(
                        request, context, workflow_id
                    )
                )

        # Execute independent tasks in parallel
        independent_results: dict[str, Any] = {}
        if tasks:
            try:
                # Wait for independent tasks with timeout
                timeout = self.workflow_config["timeouts"]["overall_workflow"]
                done, pending = await asyncio.wait(
                    tasks.values(), timeout=timeout, return_when=asyncio.ALL_COMPLETED
                )

                # Collect results
                for service_name, task in tasks.items():
                    if task in done:
                        try:
                            independent_results[service_name] = await task
                            if workflow_id in self.active_workflows:
                                self.active_workflows[workflow_id]["completed_services"].append(
                                    service_name
                                )
                        except Exception as e:
                            logger.error(f"❌ {service_name} service failed: {e}")
                            independent_results[service_name] = {
                                "status": "failed",
                                "error": str(e),
                            }
                            if workflow_id in self.active_workflows:
                                self.active_workflows[workflow_id]["failed_services"].append(
                                    service_name
                                )
                    else:
                        # Task didn't complete in time
                        task.cancel()
                        independent_results[service_name] = {"status": "timeout"}
                        if workflow_id in self.active_workflows:
                            self.active_workflows[workflow_id]["failed_services"].append(
                                service_name
                            )

            except Exception as e:
                logger.error(f"❌ Parallel execution failed: {e}")
                independent_results = {"error": str(e)}

        # Execute dependent services (modeling)
        if "modeling" in execution_strategy["services"] and self.service_executor.modeling_service:
            try:
                # Get results with type safety
                contextual_result = independent_results.get("contextual")
                temporal_result = independent_results.get("temporal")

                # Ensure they are dicts (not strings or None)
                if not isinstance(contextual_result, dict):
                    contextual_result = {}
                if not isinstance(temporal_result, dict):
                    temporal_result = {}

                modeling_result = await self.service_executor.execute_predictive_modeling(
                    request, context, contextual_result, temporal_result, workflow_id
                )
                independent_results["modeling"] = modeling_result
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["completed_services"].append("modeling")
            except Exception as e:
                logger.error(f"❌ Modeling service failed: {e}")
                independent_results["modeling"] = {"status": "failed", "error": str(e)}
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["failed_services"].append("modeling")

        return independent_results

    async def execute_sequential_workflow(
        self,
        request: dict[str, Any],
        context: IntelligenceContext,
        execution_strategy: dict[str, Any],
        workflow_id: str,
    ) -> dict[str, Any]:
        """
        Execute intelligence services sequentially.

        Args:
            request: Analysis request
            context: Intelligence context
            execution_strategy: Execution strategy details
            workflow_id: Workflow identifier

        Returns:
            Results from all services
        """
        logger.info("🔄 Executing sequential intelligence workflow")

        results = {}

        # Execute services in order
        for service_name in execution_strategy["services"]:
            try:
                if service_name == "contextual" and self.service_executor.contextual_service:
                    result = await self.service_executor.execute_contextual_analysis(
                        request, context, workflow_id
                    )
                    results["contextual"] = result

                elif service_name == "temporal" and self.service_executor.temporal_service:
                    result = await self.service_executor.execute_temporal_intelligence(
                        request, context, workflow_id
                    )
                    results["temporal"] = result

                elif service_name == "modeling" and self.service_executor.modeling_service:
                    # Get results with type safety
                    contextual_result = results.get("contextual")
                    temporal_result = results.get("temporal")

                    # Ensure they are dicts (not None)
                    if not isinstance(contextual_result, dict):
                        contextual_result = {}
                    if not isinstance(temporal_result, dict):
                        temporal_result = {}

                    result = await self.service_executor.execute_predictive_modeling(
                        request, context, contextual_result, temporal_result, workflow_id
                    )
                    results["modeling"] = result

                elif (
                    service_name == "cross_channel" and self.service_executor.cross_channel_service
                ):
                    result = await self.service_executor.execute_cross_channel_analysis(
                        request, context, workflow_id
                    )
                    results["cross_channel"] = result

                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["completed_services"].append(service_name)

            except Exception as e:
                logger.error(f"❌ {service_name} service failed: {e}")
                results[service_name] = {"status": "failed", "error": str(e)}
                if workflow_id in self.active_workflows:
                    self.active_workflows[workflow_id]["failed_services"].append(service_name)

        return results

    def generate_cache_key(self, request: dict[str, Any], context: IntelligenceContext) -> str:
        """
        Generate cache key for intelligence results.

        Args:
            request: Analysis request
            context: Intelligence context

        Returns:
            Cache key string
        """
        channel_ids = sorted(request.get("channel_ids", []))
        return f"intelligence_{'-'.join(map(str, channel_ids))}_{context.value}_{datetime.now().strftime('%Y%m%d')}"

    def register_workflow(
        self, workflow_id: str, request: dict[str, Any], context: IntelligenceContext
    ) -> None:
        """
        Register a new workflow for tracking.

        Args:
            workflow_id: Unique workflow identifier
            request: Analysis request
            context: Intelligence context
        """
        self.active_workflows[workflow_id] = {
            "status": "running",
            "start_time": datetime.now(),
            "request": request,
            "context": context,
            "completed_services": [],
            "failed_services": [],
        }

    def complete_workflow(self, workflow_id: str, result: dict[str, Any]) -> None:
        """
        Mark workflow as completed.

        Args:
            workflow_id: Workflow identifier
            result: Final workflow result
        """
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["result"] = result

    def fail_workflow(self, workflow_id: str, error: str) -> None:
        """
        Mark workflow as failed.

        Args:
            workflow_id: Workflow identifier
            error: Error message
        """
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = error

    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Get status of a specific workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow status dictionary
        """
        return self.active_workflows.get(workflow_id, {"status": "not_found"})

    def get_active_workflows(self) -> dict[str, Any]:
        """
        Get all active workflows.

        Returns:
            Dictionary of active workflows
        """
        return self.active_workflows.copy()
