"""
Monitoring Tools
================

Tools for checking worker health, collecting metrics, and analyzing logs.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING

# Lazy import for aiohttp (loaded at runtime when needed)
if TYPE_CHECKING:
    import aiohttp

from apps.ai.system.tools.base import (
    BaseTool,
    ToolCategory,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
)

logger = logging.getLogger(__name__)


class HealthCheckTool(BaseTool):
    """
    Check health status of a worker or service.
    
    Safe, read-only operation.
    """
    
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="health_check",
            description="Check health status of a worker or service endpoint",
            category=ToolCategory.MONITORING,
            risk_level=ToolRiskLevel.SAFE,
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {"type": "string", "description": "Name of worker to check"},
                    "endpoint": {"type": "string", "description": "Health endpoint URL (optional)"},
                    "timeout": {"type": "integer", "default": 5, "description": "Timeout in seconds"},
                },
                "required": ["worker_name"],
            },
        )
    
    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        endpoint = params.get("endpoint")
        timeout = params.get("timeout", 5)
        
        try:
            # If endpoint provided, do HTTP check
            if endpoint:
                import aiohttp
                start_time = time.monotonic()
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                    async with session.get(endpoint) as response:
                        elapsed_ms = int((time.monotonic() - start_time) * 1000)
                        response_text = await response.text()
                        
                        health_data = {
                            "worker_name": worker_name,
                            "endpoint": endpoint,
                            "status_code": response.status,
                            "healthy": response.status == 200,
                            "response_time_ms": elapsed_ms,
                        }
                        
                        # Try to parse JSON response
                        try:
                            import json
                            health_data["details"] = json.loads(response_text)
                        except Exception:
                            health_data["details"] = {"raw": response_text[:500]}
                        
                        return ToolResult(
                            success=True,
                            tool_name=self.definition.name,
                            data=health_data,
                            message=f"Worker {worker_name} is {'healthy' if health_data['healthy'] else 'unhealthy'}",
                        )
            
            # Without endpoint, check if worker exists in registry
            from apps.ai.system.registry import WorkerRegistry
            registry = WorkerRegistry()
            
            worker = await registry.get_worker(worker_name)
            state = await registry.get_worker_state(worker_name) if worker else None
            
            if not worker:
                return ToolResult(
                    success=True,
                    tool_name=self.definition.name,
                    data={"worker_name": worker_name, "found": False},
                    message=f"Worker {worker_name} not found in registry",
                )
            
            health_data = {
                "worker_name": worker_name,
                "found": True,
                "worker_type": worker.worker_type.value,
                "ai_manageable": worker.ai_manageable,
                "status": state.status.value if state else "unknown",
                "last_seen": state.last_seen.isoformat() if state and state.last_seen else None,
            }
            
            if state:
                health_data.update({
                    "cpu_percent": state.cpu_percent,
                    "memory_percent": state.memory_percent,
                    "errors_count": state.errors_count,
                })
            
            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data=health_data,
                message=f"Worker {worker_name} status: {health_data['status']}",
            )
            
        except httpx.TimeoutException:
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=f"Health check timed out after {timeout}s",
                data={"worker_name": worker_name, "endpoint": endpoint},
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )


@dataclass
class MetricPoint:
    """Single metric data point"""
    name: str
    value: float
    timestamp: datetime
    labels: dict[str, str]


class MetricsCollectorTool(BaseTool):
    """
    Collect metrics from workers and services.
    
    Safe, read-only operation.
    """
    
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="collect_metrics",
            description="Collect current metrics from workers and services",
            category=ToolCategory.MONITORING,
            risk_level=ToolRiskLevel.SAFE,
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {"type": "string", "description": "Worker name (optional, all if not specified)"},
                    "metric_names": {"type": "array", "items": {"type": "string"}, "description": "Specific metrics to collect"},
                    "include_system": {"type": "boolean", "default": True, "description": "Include system metrics (CPU, memory)"},
                },
            },
        )
    
    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        metric_names = params.get("metric_names", [])
        include_system = params.get("include_system", True)
        
        try:
            metrics = {}
            
            # Collect system metrics
            if include_system:
                try:
                    import psutil
                    metrics["system"] = {
                        "cpu_percent": psutil.cpu_percent(interval=0.1),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage("/").percent,
                        "load_average": list(psutil.getloadavg()),
                    }
                except ImportError:
                    metrics["system"] = {"error": "psutil not installed"}
            
            # Get worker metrics from registry
            from apps.ai.system.registry import WorkerRegistry
            registry = WorkerRegistry()
            
            workers = await registry.list_workers()
            
            for worker in workers:
                if worker_name and worker.name != worker_name:
                    continue
                
                state = await registry.get_worker_state(worker.name)
                if state:
                    worker_metrics = {
                        "status": state.status.value,
                        "cpu_percent": state.cpu_percent,
                        "memory_percent": state.memory_percent,
                        "tasks_processed": state.tasks_processed,
                        "errors_count": state.errors_count,
                        "last_seen": state.last_seen.isoformat() if state.last_seen else None,
                    }
                    
                    # Filter metrics if specific names requested
                    if metric_names:
                        worker_metrics = {
                            k: v for k, v in worker_metrics.items()
                            if k in metric_names
                        }
                    
                    metrics[worker.name] = worker_metrics
            
            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data={
                    "metrics": metrics,
                    "collected_at": datetime.utcnow().isoformat(),
                    "worker_count": len(metrics) - (1 if "system" in metrics else 0),
                },
                message=f"Collected metrics for {len(metrics)} sources",
            )
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )


class LogAnalyzerTool(BaseTool):
    """
    Analyze logs for patterns, errors, and anomalies.
    
    Safe, read-only operation.
    """
    
    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="analyze_logs",
            description="Analyze logs for patterns, errors, and anomalies",
            category=ToolCategory.ANALYSIS,
            risk_level=ToolRiskLevel.SAFE,
            parameters_schema={
                "type": "object",
                "properties": {
                    "worker_name": {"type": "string", "description": "Worker to analyze logs for"},
                    "log_file": {"type": "string", "description": "Path to log file"},
                    "time_range_hours": {"type": "integer", "default": 1, "description": "Hours of logs to analyze"},
                    "patterns": {"type": "array", "items": {"type": "string"}, "description": "Patterns to search for"},
                },
            },
        )
    
    async def execute(self, **params: Any) -> ToolResult:
        worker_name = params.get("worker_name")
        log_file = params.get("log_file")
        time_range_hours = params.get("time_range_hours", 1)
        patterns = params.get("patterns", ["ERROR", "CRITICAL", "Exception", "Traceback"])
        
        try:
            # Determine log file path
            if not log_file:
                log_file = f"logs/{worker_name}.log" if worker_name else "logs/app.log"
            
            analysis = {
                "log_file": log_file,
                "time_range_hours": time_range_hours,
                "patterns_searched": patterns,
                "matches": {},
                "summary": {
                    "total_lines": 0,
                    "error_count": 0,
                    "warning_count": 0,
                },
            }
            
            import os
            if not os.path.exists(log_file):
                return ToolResult(
                    success=True,
                    tool_name=self.definition.name,
                    data=analysis,
                    message=f"Log file not found: {log_file}",
                )
            
            # Read and analyze log file
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            # Simple pattern matching
            for pattern in patterns:
                matches = []
                for i, line in enumerate(lines[-10000:]):  # Last 10k lines
                    if pattern.lower() in line.lower():
                        matches.append({
                            "line_num": len(lines) - 10000 + i + 1,
                            "content": line.strip()[:200],
                        })
                
                analysis["matches"][pattern] = {
                    "count": len(matches),
                    "samples": matches[-5],  # Last 5 matches
                }
                
                if pattern.upper() == "ERROR":
                    analysis["summary"]["error_count"] = len(matches)
                elif pattern.upper() == "WARNING":
                    analysis["summary"]["warning_count"] = len(matches)
            
            analysis["summary"]["total_lines"] = len(lines)
            
            return ToolResult(
                success=True,
                tool_name=self.definition.name,
                data=analysis,
                message=f"Analyzed {len(lines)} lines, found {analysis['summary']['error_count']} errors",
            )
            
        except Exception as e:
            logger.error(f"Log analysis failed: {e}")
            return ToolResult(
                success=False,
                tool_name=self.definition.name,
                error=str(e),
            )
