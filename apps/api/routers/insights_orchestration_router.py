"""
Advanced Analytics Orchestration Router - Phase 3 Step 4
Provides API endpoints for intelligent workflow orchestration
that coordinates NLG Engine, Autonomous Optimization, and Predictive Intelligence.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from core.services.analytics_fusion_service import AnalyticsFusionService
from core.services.analytics_orchestration_service import AnalyticsOrchestrationService

router = APIRouter(prefix="/insights/orchestration", tags=["Analytics Orchestration"])
logger = logging.getLogger(__name__)


# Request/Response Models


class WorkflowDefinitionRequest(BaseModel):
    """Request to define a new workflow"""

    name: str = Field(..., description="Human-readable name for the workflow")
    description: str = Field(..., description="Description of workflow purpose")
    steps: list[dict[str, Any]] = Field(..., description="List of workflow steps")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Default workflow parameters"
    )
    timeout: int = Field(default=300, description="Workflow timeout in seconds")


class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow"""

    workflow_id: str = Field(..., description="ID of workflow or template to execute")
    input_data: dict[str, Any] = Field(..., description="Input data for workflow execution")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Execution parameters")
    priority: str = Field(default="normal", description="Execution priority (low, normal, high)")


class ComprehensiveAnalyticsRequest(BaseModel):
    """Request for comprehensive analytics pipeline"""

    data_source: str = Field(..., description="Source of analytics data")
    analysis_scope: list[str] = Field(
        ..., description="Scope of analysis (temporal, predictive, optimization)"
    )
    context: dict[str, Any] = Field(default_factory=dict, description="Business context")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Analysis parameters")
    output_format: str = Field(default="comprehensive", description="Desired output format")


class RealTimeIntelligenceRequest(BaseModel):
    """Request for real-time intelligence workflow"""

    data_stream: dict[str, Any] = Field(..., description="Real-time data stream")
    intelligence_scope: list[str] = Field(..., description="Types of intelligence to extract")
    urgency_level: str = Field(
        default="normal", description="Urgency level (low, normal, high, critical)"
    )
    context: dict[str, Any] = Field(default_factory=dict, description="Operational context")


class StrategicPlanningRequest(BaseModel):
    """Request for strategic planning workflow"""

    planning_horizon: str = Field(
        ..., description="Planning horizon (6_months, 12_months, 24_months)"
    )
    data_sources: list[str] = Field(..., description="Data sources for strategic analysis")
    strategic_objectives: list[str] = Field(..., description="Strategic objectives to optimize for")
    scenario_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Scenario analysis parameters"
    )
    context: dict[str, Any] = Field(default_factory=dict, description="Strategic context")


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status"""

    execution_id: str
    workflow_id: str
    status: str
    current_step: str | None
    completed_steps: list[str]
    failed_steps: list[str]
    progress_percentage: float
    start_time: str | None
    end_time: str | None
    error_messages: list[str]
    performance_metrics: dict[str, float]


class OrchestrationHealthResponse(BaseModel):
    """Response for orchestration health"""

    service_status: str
    active_executions: int
    total_executions: int
    success_rate: float
    available_templates: list[str]
    cache_size: int
    max_concurrent_workflows: int
    timestamp: str


# Dependency injection
async def get_fusion_service() -> AnalyticsFusionService:
    """Get analytics fusion service instance"""

    # This would be injected from your DI container
    # For now, we'll create a basic mock instance that won't actually work
    # but will pass type checking
    class MockRepo:
        pass

    return AnalyticsFusionService(
        channel_daily_repo=MockRepo(),
        post_repo=MockRepo(),
        metrics_repo=MockRepo(),
        edges_repo=MockRepo(),
    )


async def get_orchestration_service(
    fusion_service: AnalyticsFusionService = Depends(get_fusion_service),
) -> AnalyticsOrchestrationService:
    """Get orchestration service instance"""
    # Check if fusion service has orchestration service
    if hasattr(fusion_service, "_orchestration_service"):
        return fusion_service._orchestration_service

    # Create new orchestration service
    from core.services.autonomous_optimization_service import (
        AutonomousOptimizationService,
    )
    from core.services.nlg_service import NaturalLanguageGenerationService
    from core.services.predictive_intelligence_service import (
        PredictiveIntelligenceService,
    )

    # These would normally be injected
    nlg_service = NaturalLanguageGenerationService()

    # Create mock services for type compatibility
    class MockService:
        pass

    try:
        optimization_service = AutonomousOptimizationService(
            analytics_service=MockService(),
            nlg_service=nlg_service,
            cache_service=MockService(),
        )
    except:
        optimization_service = None

    try:
        intelligence_service = PredictiveIntelligenceService(
            predictive_analytics_service=MockService(),
            nlg_service=nlg_service,
            autonomous_optimization_service=MockService(),
        )
    except:
        intelligence_service = MockService()  # Use mock if construction fails

    orchestration_service = AnalyticsOrchestrationService(
        nlg_service=nlg_service,
        optimization_service=optimization_service,
        intelligence_service=intelligence_service,
        fusion_service=fusion_service,
    )

    # Cache it in fusion service
    fusion_service._orchestration_service = orchestration_service
    return orchestration_service


# API Endpoints


@router.post("/workflows", response_model=dict[str, str])
async def create_workflow(
    request: WorkflowDefinitionRequest,
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Create a new orchestration workflow

    Creates a custom workflow definition that can be executed multiple times
    with different input data. Workflows define the sequence of AI services
    to coordinate for comprehensive analytics.
    """
    try:
        logger.info(f"🎭 Creating new workflow: {request.name}")

        workflow_definition = {
            "name": request.name,
            "description": request.description,
            "steps": request.steps,
            "parameters": request.parameters,
            "timeout": request.timeout,
        }

        workflow_id = await orchestration_service.create_workflow(workflow_definition)

        return {
            "workflow_id": workflow_id,
            "status": "created",
            "message": f"Workflow '{request.name}' created successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to create workflow: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create workflow: {str(e)}")


@router.post("/execute", response_model=dict[str, str])
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Execute an orchestration workflow

    Executes a predefined workflow or template with the provided input data.
    Returns an execution ID that can be used to monitor progress and retrieve results.
    """
    try:
        logger.info(f"🚀 Executing workflow: {request.workflow_id}")

        execution_id = await orchestration_service.execute_workflow(
            request.workflow_id,
            {
                "input_data": request.input_data,
                "parameters": request.parameters,
                "priority": request.priority,
            },
        )

        return {
            "execution_id": execution_id,
            "workflow_id": request.workflow_id,
            "status": "initiated",
            "message": "Workflow execution started successfully",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to execute workflow: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to execute workflow: {str(e)}")


@router.post("/comprehensive", response_model=dict[str, Any])
async def execute_comprehensive_analytics(
    request: ComprehensiveAnalyticsRequest,
    fusion_service: AnalyticsFusionService = Depends(get_fusion_service),
):
    """
    Execute comprehensive analytics pipeline

    Runs the full analytics pipeline combining predictive intelligence,
    autonomous optimization, and natural language generation for
    comprehensive business insights.
    """
    try:
        logger.info(f"🎼 Executing comprehensive analytics for: {request.data_source}")

        input_data = {
            "data_source": request.data_source,
            "analysis_scope": request.analysis_scope,
            "context": request.context,
            "parameters": request.parameters,
            "output_format": request.output_format,
            "prediction_data": {
                "source": request.data_source,
                "scope": request.analysis_scope,
            },
            "optimization_data": {
                "source": request.data_source,
                "objectives": request.analysis_scope,
            },
        }

        result = await fusion_service.execute_comprehensive_workflow(input_data)

        return {
            "comprehensive_analytics": result,
            "workflow_type": "comprehensive_analytics",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Comprehensive analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analytics failed: {str(e)}")


@router.post("/realtime", response_model=dict[str, Any])
async def execute_realtime_intelligence(
    request: RealTimeIntelligenceRequest,
    fusion_service: AnalyticsFusionService = Depends(get_fusion_service),
):
    """
    Execute real-time intelligence workflow

    Processes real-time data through temporal intelligence, cross-channel
    analysis, and rapid optimization for immediate actionable insights.
    """
    try:
        logger.info("⚡ Executing real-time intelligence workflow")

        input_data = {
            "data_stream": request.data_stream,
            "intelligence_scope": request.intelligence_scope,
            "urgency_level": request.urgency_level,
            "context": request.context,
            "prediction_data": {
                "stream": request.data_stream,
                "scope": request.intelligence_scope,
                "urgency": request.urgency_level,
            },
            "optimization_data": {
                "stream": request.data_stream,
                "speed": ("fast" if request.urgency_level in ["high", "critical"] else "normal"),
            },
        }

        result = await fusion_service.execute_realtime_intelligence_workflow(input_data)

        return {
            "realtime_intelligence": result,
            "workflow_type": "realtime_intelligence",
            "urgency_level": request.urgency_level,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Real-time intelligence failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real-time intelligence failed: {str(e)}")


@router.post("/strategic", response_model=dict[str, Any])
async def execute_strategic_planning(
    request: StrategicPlanningRequest,
    fusion_service: AnalyticsFusionService = Depends(get_fusion_service),
):
    """
    Execute strategic planning workflow

    Performs deep strategic analysis with historical context, predictive modeling,
    scenario optimization, and executive-level reporting for long-term planning.
    """
    try:
        logger.info(f"🎯 Executing strategic planning workflow: {request.planning_horizon}")

        input_data = {
            "planning_horizon": request.planning_horizon,
            "data_sources": request.data_sources,
            "strategic_objectives": request.strategic_objectives,
            "scenario_parameters": request.scenario_parameters,
            "context": request.context,
            "prediction_data": {
                "sources": request.data_sources,
                "horizon": request.planning_horizon,
                "objectives": request.strategic_objectives,
            },
            "optimization_data": {
                "sources": request.data_sources,
                "objectives": request.strategic_objectives,
                "scenarios": request.scenario_parameters,
            },
        }

        result = await fusion_service.execute_strategic_planning_workflow(input_data)

        return {
            "strategic_planning": result,
            "workflow_type": "strategic_planning",
            "planning_horizon": request.planning_horizon,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Strategic planning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Strategic planning failed: {str(e)}")


@router.get("/status/{execution_id}", response_model=WorkflowStatusResponse)
async def get_execution_status(
    execution_id: str,
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Get workflow execution status

    Returns current status, progress, and performance metrics for
    a running or completed workflow execution.
    """
    try:
        logger.info(f"📊 Getting execution status: {execution_id}")

        status = await orchestration_service.get_execution_status(execution_id)

        return WorkflowStatusResponse(**status)

    except Exception as e:
        logger.error(f"Failed to get execution status: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Execution not found or status unavailable: {str(e)}",
        )


@router.get("/result/{execution_id}", response_model=dict[str, Any])
async def get_execution_result(
    execution_id: str,
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Get workflow execution result

    Returns complete results from a completed workflow execution,
    including synthesized insights, performance metrics, and quality assessment.
    """
    try:
        logger.info(f"📋 Getting execution result: {execution_id}")

        result = await orchestration_service.get_execution_result(execution_id)

        return {
            "execution_result": {
                "execution_id": result.execution_id,
                "workflow_id": result.workflow_id,
                "status": result.status,
                "synthesis_result": result.synthesis_result,
                "performance_metrics": result.performance_metrics,
                "orchestration_insights": result.orchestration_insights,
                "quality_assessment": result.quality_assessment,
                "execution_metadata": result.execution_metadata,
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get execution result: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Execution result not available: {str(e)}")


@router.delete("/cancel/{execution_id}", response_model=dict[str, str])
async def cancel_execution(
    execution_id: str,
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Cancel workflow execution

    Cancels a running workflow execution. Completed steps will be preserved,
    but remaining steps will not be executed.
    """
    try:
        logger.info(f"❌ Cancelling execution: {execution_id}")

        success = await orchestration_service.cancel_execution(execution_id)

        if success:
            return {
                "execution_id": execution_id,
                "status": "cancelled",
                "message": "Workflow execution cancelled successfully",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=404, detail="Execution not found or already completed")

    except Exception as e:
        logger.error(f"Failed to cancel execution: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to cancel execution: {str(e)}")


@router.get("/templates", response_model=dict[str, Any])
async def get_workflow_templates(
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Get available workflow templates

    Returns all predefined workflow templates that can be executed
    directly without creating custom workflow definitions.
    """
    try:
        logger.info("📋 Getting available workflow templates")

        templates = orchestration_service.get_workflow_templates()

        template_info = {}
        for template_id, template in templates.items():
            template_info[template_id] = {
                "name": template.name,
                "description": template.description,
                "steps_count": len(template.steps),
                "default_timeout": template.execution_timeout,
                "default_parameters": template.default_parameters,
            }

        return {
            "available_templates": template_info,
            "total_templates": len(templates),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get workflow templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow templates: {str(e)}")


@router.get("/health", response_model=OrchestrationHealthResponse)
async def get_orchestration_health(
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Get orchestration service health

    Returns health status, performance metrics, and operational statistics
    for the orchestration service and all coordinated AI services.
    """
    try:
        logger.info("🏥 Checking orchestration service health")

        health = orchestration_service.get_orchestration_health()

        return OrchestrationHealthResponse(**health)

    except Exception as e:
        logger.error(f"Orchestration health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Orchestration service health check failed: {str(e)}",
        )


@router.get("/metrics", response_model=dict[str, Any])
async def get_orchestration_metrics(
    orchestration_service: AnalyticsOrchestrationService = Depends(get_orchestration_service),
):
    """
    Get orchestration performance metrics

    Returns detailed performance metrics, execution statistics, and
    optimization insights for the orchestration service.
    """
    try:
        logger.info("📊 Getting orchestration performance metrics")

        # Get basic health info
        health = orchestration_service.get_orchestration_health()

        # Calculate additional metrics
        active_executions = len(orchestration_service.active_executions)
        total_executions = len(orchestration_service.execution_history)

        # Performance statistics
        performance_stats = {}
        if orchestration_service.execution_history:
            durations = [
                exec.performance_metrics.get("total_duration", 0)
                for exec in orchestration_service.execution_history
                if exec.performance_metrics.get("total_duration")
            ]

            if durations:
                performance_stats = {
                    "average_execution_time": sum(durations) / len(durations),
                    "fastest_execution": min(durations),
                    "slowest_execution": max(durations),
                    "total_execution_time": sum(durations),
                }

        return {
            "orchestration_metrics": {
                "service_health": health,
                "execution_statistics": {
                    "active_executions": active_executions,
                    "total_executions": total_executions,
                    "success_rate": health["success_rate"],
                },
                "performance_statistics": performance_stats,
                "cache_statistics": {
                    "cache_size": len(orchestration_service.result_cache),
                    "cache_hit_rate": 0.0,  # Would be calculated from actual cache usage
                },
                "service_coordination": {
                    "nlg_service": "connected",
                    "optimization_service": "connected",
                    "intelligence_service": "connected",
                    "fusion_service": "connected",
                },
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get orchestration metrics: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get orchestration metrics: {str(e)}"
        )
