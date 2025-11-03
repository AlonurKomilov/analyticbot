"""
Deep Learning Orchestrator Service - Phase 4B Step 5
====================================================

Coordinates and orchestrates all deep learning microservices following clean architecture.
This service acts as a lightweight coordinator without business logic - just routing and coordination.

Implements: DeepLearningServiceProtocol (from core.protocols)

Key Features:
- Service discovery and health monitoring
- Load balancing and request routing
- Async coordination of multiple AI services
- Centralized monitoring and metrics
- Circuit breaker pattern for resilience
- Clean Architecture protocol compliance

Architecture: Clean microservice orchestrator implementing public protocol
"""

import asyncio
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

# Protocol import
from core.protocols import DeepLearningServiceProtocol

# Service imports
from ..content.content_analyzer_service import ContentAnalyzerService
from ..engagement.engagement_predictor_service import EngagementPredictorService
from ..growth_forecaster.growth_forecaster_service import GrowthForecasterService
from ..infrastructure.gpu_config import GPUConfigService

# Infrastructure imports
from ..infrastructure.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Information about a registered service"""

    name: str
    service_type: str
    instance: Any
    status: ServiceStatus
    last_health_check: datetime
    response_time_ms: float
    error_count: int
    success_count: int


@dataclass
class OrchestrationRequest:
    """Request for orchestrated AI processing"""

    request_id: str
    content: str
    services: list[str]  # Which services to run
    priority: int = 5  # 1=highest, 10=lowest
    timeout_ms: int = 30000
    metadata: dict | None = None


@dataclass
class OrchestrationResult:
    """Result from orchestrated processing"""

    request_id: str
    success: bool
    results: dict[str, Any]
    execution_time_ms: float
    services_used: list[str]
    errors: list[str]
    metadata: dict[str, Any]


class DLOrchestratorService(DeepLearningServiceProtocol):
    """
    Deep Learning Orchestrator Service

    Lightweight coordinator for all deep learning microservices.
    Handles service discovery, load balancing, and coordinated processing.

    Implements: DeepLearningServiceProtocol
    """

    def __init__(
        self,
        model_loader: ModelLoader | None = None,
        gpu_config: GPUConfigService | None = None,
        max_concurrent_requests: int = 10,
        health_check_interval: int = 30,
    ):
        # Core infrastructure
        self.model_loader = model_loader or ModelLoader()
        self.gpu_config = gpu_config or GPUConfigService()

        # Service registry
        self.services: dict[str, ServiceInfo] = {}
        self.service_instances: dict[str, Any] = {}

        # Configuration
        self.max_concurrent_requests = max_concurrent_requests
        self.health_check_interval = health_check_interval

        # Orchestration state
        self.active_requests: dict[str, OrchestrationRequest] = {}
        self.request_semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0

        # Service startup
        self.is_running = False
        self.health_check_task: asyncio.Task | None = None

        logger.info("🎯 DL Orchestrator Service initialized")

    async def start_services(self) -> bool:
        """Start and register all deep learning services"""
        try:
            logger.info("🚀 Starting deep learning services...")

            # Register Content Analyzer
            content_service = ContentAnalyzerService(
                model_loader=self.model_loader, gpu_config=self.gpu_config
            )
            await self._register_service("content_analyzer", "content", content_service)

            # Register Growth Forecaster
            growth_service = GrowthForecasterService(
                model_loader=self.model_loader, gpu_config=self.gpu_config
            )
            await self._register_service("growth_forecaster", "growth", growth_service)

            # Register Engagement Predictor
            engagement_service = EngagementPredictorService(
                model_loader=self.model_loader, gpu_config=self.gpu_config
            )
            await self._register_service("engagement_predictor", "engagement", engagement_service)

            # Start health monitoring
            self.is_running = True
            self.health_check_task = asyncio.create_task(self._health_monitor())

            logger.info(f"✅ All {len(self.services)} services started successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start services: {e}")
            return False

    async def stop_services(self) -> bool:
        """Stop all services gracefully"""
        try:
            logger.info("🛑 Stopping deep learning services...")

            self.is_running = False

            # Cancel health monitoring
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass

            # Wait for active requests to complete (with timeout)
            await self._wait_for_active_requests(timeout=10.0)

            # Clear service registry
            self.services.clear()
            self.service_instances.clear()
            self.active_requests.clear()

            logger.info("✅ All services stopped successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error stopping services: {e}")
            return False

    async def orchestrate_request(self, request: OrchestrationRequest) -> OrchestrationResult:
        """
        Orchestrate a multi-service AI processing request

        Args:
            request: The orchestration request

        Returns:
            Orchestration result with all service outputs
        """
        start_time = time.time()

        try:
            # Acquire semaphore for concurrency control
            async with self.request_semaphore:
                logger.info(
                    f"🎯 Orchestrating request {request.request_id} for services: {request.services}"
                )

                # Track active request
                self.active_requests[request.request_id] = request
                self.total_requests += 1

                # Execute services in parallel
                results = await self._execute_services_parallel(request)

                # Calculate execution time
                execution_time = (time.time() - start_time) * 1000

                # Update metrics
                self._update_metrics(execution_time, len(results.get("errors", [])) == 0)

                # Create result
                orchestration_result = OrchestrationResult(
                    request_id=request.request_id,
                    success=len(results.get("errors", [])) == 0,
                    results=results.get("outputs", {}),
                    execution_time_ms=execution_time,
                    services_used=request.services,
                    errors=results.get("errors", []),
                    metadata={
                        "timestamp": datetime.utcnow().isoformat(),
                        "orchestrator_version": "1.0.0",
                        "gpu_info": self.gpu_config.get_device_info(),
                    },
                )

                # Remove from active requests
                self.active_requests.pop(request.request_id, None)

                logger.info(f"✅ Request {request.request_id} completed in {execution_time:.2f}ms")
                return orchestration_result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._update_metrics(execution_time, False)
            self.active_requests.pop(request.request_id, None)

            logger.error(f"❌ Orchestration failed for {request.request_id}: {e}")

            return OrchestrationResult(
                request_id=request.request_id,
                success=False,
                results={},
                execution_time_ms=execution_time,
                services_used=request.services,
                errors=[str(e)],
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": "orchestration_failure",
                },
            )

    async def _execute_services_parallel(self, request: OrchestrationRequest) -> dict[str, Any]:
        """Execute multiple services in parallel"""
        outputs = {}
        errors = []

        # Create tasks for all requested services
        tasks = []
        service_names = []

        for service_name in request.services:
            if service_name in self.service_instances:
                task = self._execute_single_service(service_name, request)
                tasks.append(task)
                service_names.append(service_name)
            else:
                errors.append(f"Service {service_name} not available")

        # Execute all tasks in parallel
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(results):
                    service_name = service_names[i]

                    if isinstance(result, Exception):
                        errors.append(f"{service_name}: {str(result)}")
                    else:
                        outputs[service_name] = result

            except Exception as e:
                errors.append(f"Parallel execution failed: {str(e)}")

        return {"outputs": outputs, "errors": errors}

    async def _execute_single_service(
        self, service_name: str, request: OrchestrationRequest
    ) -> Any:
        """Execute a single service"""
        service_instance = self.service_instances[service_name]

        try:
            # Route to appropriate service method based on service type
            if service_name == "content_analyzer":
                result = await service_instance.analyze_content(
                    content=request.content,
                    analysis_types=[
                        "sentiment",
                        "toxicity",
                        "quality",
                        "engagement",
                        "relevance",
                    ],
                )
            elif service_name == "growth_forecaster":
                # Convert content to growth metrics (simplified)
                metrics = {
                    "views": len(request.content) * 10,
                    "engagement_rate": 0.05,
                    "subscriber_growth": 0.02,
                }
                result = await service_instance.forecast_growth(
                    historical_data=[metrics] * 30,  # 30 days of data
                    forecast_days=7,
                )
            elif service_name == "engagement_predictor":
                # Convert content to engagement features (simplified)
                features = {
                    "content_length": len(request.content),
                    "word_count": len(request.content.split()),
                    "hour_of_day": datetime.now().hour,
                }
                result = await service_instance.predict_engagement(
                    content_features=features, channel_context={"followers": 1000}
                )
            else:
                raise ValueError(f"Unknown service: {service_name}")

            return result

        except Exception as e:
            logger.error(f"❌ Service {service_name} execution failed: {e}")
            raise

    async def _register_service(self, name: str, service_type: str, instance: Any) -> None:
        """Register a service in the registry"""
        try:
            # Test service health
            health = instance.get_service_health()
            status = (
                ServiceStatus.HEALTHY
                if health.get("status") == "healthy"
                else ServiceStatus.DEGRADED
            )

            # Create service info
            service_info = ServiceInfo(
                name=name,
                service_type=service_type,
                instance=instance,
                status=status,
                last_health_check=datetime.utcnow(),
                response_time_ms=0.0,
                error_count=0,
                success_count=0,
            )

            # Register service
            self.services[name] = service_info
            self.service_instances[name] = instance

            logger.info(f"✅ Registered service: {name} ({service_type}) - {status.value}")

        except Exception as e:
            logger.error(f"❌ Failed to register service {name}: {e}")
            raise

    async def _health_monitor(self) -> None:
        """Continuous health monitoring of all services"""
        while self.is_running:
            try:
                await asyncio.sleep(self.health_check_interval)

                if not self.is_running:
                    break

                logger.debug("🔍 Performing health checks...")

                for service_name, service_info in self.services.items():
                    try:
                        start_time = time.time()

                        # Get service health
                        health = service_info.instance.get_service_health()
                        response_time = (time.time() - start_time) * 1000

                        # Update service status
                        if health.get("status") == "healthy":
                            service_info.status = ServiceStatus.HEALTHY
                            service_info.success_count += 1
                        else:
                            service_info.status = ServiceStatus.DEGRADED
                            service_info.error_count += 1

                        service_info.last_health_check = datetime.utcnow()
                        service_info.response_time_ms = response_time

                    except Exception as e:
                        logger.warning(f"Health check failed for {service_name}: {e}")
                        service_info.status = ServiceStatus.UNHEALTHY
                        service_info.error_count += 1
                        service_info.last_health_check = datetime.utcnow()

                logger.debug("✅ Health checks completed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")

    async def _wait_for_active_requests(self, timeout: float = 10.0) -> None:
        """Wait for active requests to complete with timeout"""
        start_time = time.time()

        while self.active_requests and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)

        if self.active_requests:
            logger.warning(f"⚠️ {len(self.active_requests)} requests still active after timeout")

    def _update_metrics(self, execution_time: float, success: bool) -> None:
        """Update orchestration metrics"""
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        # Update average response time (exponential moving average)
        alpha = 0.1
        self.average_response_time = (alpha * execution_time) + (
            (1 - alpha) * self.average_response_time
        )

    def get_service_name(self) -> str:
        """Get service identifier"""
        return "dl_orchestrator"

    async def health_check(self) -> dict[str, Any]:
        """
        Service health check

        Implements: ServiceProtocol.health_check
        """
        return self.get_service_health()

    def get_service_health(self) -> dict[str, Any]:
        """Get orchestrator service health"""
        healthy_services = sum(
            1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY
        )
        total_services = len(self.services)

        return {
            "service": "dl_orchestrator",
            "status": (
                "healthy" if self.is_running and healthy_services == total_services else "degraded"
            ),
            "is_running": self.is_running,
            "registered_services": total_services,
            "healthy_services": healthy_services,
            "active_requests": len(self.active_requests),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "average_response_time_ms": self.average_response_time,
            "max_concurrent_requests": self.max_concurrent_requests,
            "gpu_info": self.gpu_config.get_device_info(),
            "services": {
                name: {
                    "status": info.status.value,
                    "last_health_check": info.last_health_check.isoformat(),
                    "response_time_ms": info.response_time_ms,
                    "success_count": info.success_count,
                    "error_count": info.error_count,
                }
                for name, info in self.services.items()
            },
        }

    def get_orchestration_stats(self) -> dict[str, Any]:
        """Get detailed orchestration statistics"""
        return {
            "orchestrator_metrics": {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": self.successful_requests / max(self.total_requests, 1),
                "average_response_time_ms": self.average_response_time,
                "active_requests": len(self.active_requests),
                "max_concurrent_requests": self.max_concurrent_requests,
            },
            "service_registry": {name: asdict(info) for name, info in self.services.items()},
            "system_info": {
                "is_running": self.is_running,
                "health_check_interval": self.health_check_interval,
                "gpu_config": self.gpu_config.get_device_info(),
            },
        }

    # ==================== DeepLearningServiceProtocol Implementation ====================

    async def predict_growth(
        self,
        channel_id: int,
        historical_data: list[dict[str, Any]],
        forecast_horizon: int = 7,
        include_uncertainty: bool = True,
    ) -> dict[str, Any]:
        """
        Predict channel growth using ML models

        Implements: DeepLearningServiceProtocol.predict_growth
        """
        try:
            # Get growth forecaster service
            if "growth_forecaster" not in self.service_instances:
                await self.start_services()

            growth_service = self.service_instances["growth_forecaster"]

            # Call the growth forecaster
            result = await growth_service.forecast_growth(
                historical_data=historical_data, forecast_days=forecast_horizon
            )

            return {
                "channel_id": channel_id,
                "forecast_horizon": forecast_horizon,
                "include_uncertainty": include_uncertainty,
                "predictions": result,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Growth prediction failed: {e}")
            return {"channel_id": channel_id, "error": str(e), "status": "failed"}

    async def predict_engagement(
        self,
        content: str,
        channel_id: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Predict content engagement

        Implements: DeepLearningServiceProtocol.predict_engagement
        """
        try:
            # Get engagement predictor service
            if "engagement_predictor" not in self.service_instances:
                await self.start_services()

            engagement_service = self.service_instances["engagement_predictor"]

            # Prepare features
            features = {
                "content_length": len(content),
                "word_count": len(content.split()),
                "hour_of_day": datetime.now().hour,
            }
            if metadata:
                features.update(metadata)

            # Call the engagement predictor
            result = await engagement_service.predict_engagement(
                content_features=features, channel_context={"channel_id": channel_id}
            )

            return {
                "channel_id": channel_id,
                "content_length": len(content),
                "predictions": result,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}")
            return {"channel_id": channel_id, "error": str(e), "status": "failed"}

    async def analyze_content(
        self,
        content: str,
        analysis_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Analyze content quality and characteristics

        Implements: DeepLearningServiceProtocol.analyze_content
        """
        try:
            # Get content analyzer service
            if "content_analyzer" not in self.service_instances:
                await self.start_services()

            content_service = self.service_instances["content_analyzer"]

            # Default analysis types
            if not analysis_types:
                analysis_types = [
                    "sentiment",
                    "toxicity",
                    "quality",
                    "engagement",
                    "relevance",
                ]

            # Call the content analyzer
            result = await content_service.analyze_content(
                content=content, analysis_types=analysis_types
            )

            return {
                "content_length": len(content),
                "analysis_types": analysis_types,
                "analysis": result,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def train_model(
        self,
        channel_id: int,
        model_type: str,
        training_data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Train ML model with new data

        Implements: DeepLearningServiceProtocol.train_model
        """
        try:
            # Route to appropriate service based on model type
            if model_type == "growth":
                if "growth_forecaster" not in self.service_instances:
                    await self.start_services()
                self.service_instances["growth_forecaster"]
            elif model_type == "engagement":
                if "engagement_predictor" not in self.service_instances:
                    await self.start_services()
                self.service_instances["engagement_predictor"]
            else:
                raise ValueError(f"Unknown model type: {model_type}")

            # Train the model (if service supports it)
            # Note: This would need to be implemented in the individual services
            result = {
                "channel_id": channel_id,
                "model_type": model_type,
                "status": "training_submitted",
                "message": "Training functionality to be implemented in service",
                "timestamp": datetime.utcnow().isoformat(),
            }

            return result

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {
                "channel_id": channel_id,
                "model_type": model_type,
                "error": str(e),
                "status": "failed",
            }

    async def get_model_performance(
        self,
        channel_id: int,
        model_type: str,
    ) -> dict[str, Any]:
        """
        Get model performance metrics

        Implements: DeepLearningServiceProtocol.get_model_performance
        """
        try:
            # Get service health as proxy for model performance
            if model_type == "growth":
                service_name = "growth_forecaster"
            elif model_type == "engagement":
                service_name = "engagement_predictor"
            elif model_type == "content":
                service_name = "content_analyzer"
            else:
                raise ValueError(f"Unknown model type: {model_type}")

            if service_name in self.services:
                service_info = self.services[service_name]
                return {
                    "channel_id": channel_id,
                    "model_type": model_type,
                    "status": service_info.status.value,
                    "success_count": service_info.success_count,
                    "error_count": service_info.error_count,
                    "success_rate": service_info.success_count
                    / max(service_info.success_count + service_info.error_count, 1),
                    "last_health_check": service_info.last_health_check.isoformat(),
                    "response_time_ms": service_info.response_time_ms,
                }
            else:
                return {
                    "channel_id": channel_id,
                    "model_type": model_type,
                    "status": "not_available",
                    "message": "Service not initialized",
                }

        except Exception as e:
            logger.error(f"Failed to get model performance: {e}")
            return {
                "channel_id": channel_id,
                "model_type": model_type,
                "error": str(e),
                "status": "failed",
            }

    def clear_cache(self) -> None:
        """
        Clear prediction cache

        Implements: DeepLearningServiceProtocol.clear_cache
        """
        try:
            # Clear cache for all services
            for service_name, service_instance in self.service_instances.items():
                if hasattr(service_instance, "clear_cache"):
                    service_instance.clear_cache()
                    logger.info(f"Cleared cache for {service_name}")

            logger.info("✅ All service caches cleared")

        except Exception as e:
            logger.error(f"Failed to clear caches: {e}")
