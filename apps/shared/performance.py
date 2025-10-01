# apps/shared/performance.py
"""
Performance monitoring abstraction for apps layer
Provides performance timing without direct infra imports
"""
from __future__ import annotations

import time
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

__all__ = [
    'performance_timer',
    'PerformanceMetrics', 
    'create_performance_timer'
]


@dataclass
class PerformanceMetrics:
    """Performance metrics data"""
    operation: str
    duration_ms: float
    status: str = "success"
    metadata: Optional[Dict[str, Any]] = None


class PerformanceTimer:
    """
    Synchronous performance timer that matches infra.db.performance interface
    """
    
    def __init__(self, operation_name: str, infra_performance_recorder=None):
        self.operation_name = operation_name
        self.start_time = None
        self.infra_recorder = infra_performance_recorder
        self.logger = logging.getLogger("apps.performance")
    
    def __enter__(self):
        """Enter synchronous context manager"""
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit synchronous context manager"""
        if self.start_time:
            duration_ms = (time.perf_counter() - self.start_time) * 1000
            
            # Log performance
            if exc_type:
                self.logger.warning(f"⏱️ {self.operation_name}: {duration_ms:.2f}ms [ERROR: {exc_val}]")
            elif duration_ms > 1000:  # Log slow operations
                self.logger.warning(f"⏱️ {self.operation_name}: {duration_ms:.2f}ms [SLOW]")
            else:
                self.logger.debug(f"⏱️ {self.operation_name}: {duration_ms:.2f}ms [OK]")
            
            # Try to send to infra performance system if available
            try:
                self._send_to_infra_performance(duration_ms, exc_type is not None)
            except Exception as e:
                self.logger.debug(f"Could not send metrics to infra: {e}")
    
    def _send_to_infra_performance(self, duration_ms: float, has_error: bool):
        """Try to send metrics to infra performance system via DI (sync)"""
        try:
            # Use injected recorder if available
            if self.infra_recorder:
                # Call the injected recorder
                pass  # Implementation depends on recorder interface
            else:
                # Fallback: dynamic import (will be removed when DI is complete)
                logger.warning("Performance recorder not injected, using fallback")
                from infra.db.performance import performance_timer as infra_timer_func
                # The infra performance_timer might have a record method or similar
                pass
        except ImportError:
            # Infra performance system not available - that's fine
            pass
        except Exception as e:
            pass  # Ignore infra integration errors


class PerformanceMetricsCollector:
    """
    Async performance metrics collector for advanced use cases
    """
    
    def __init__(self, logger_name: Optional[str] = None):
        self.logger = logging.getLogger(logger_name or __name__)
        self._metrics: list[PerformanceMetrics] = []
    
    @asynccontextmanager
    async def measure(self, operation_name: str, **metadata):
        """Async context manager for measuring operation performance"""
        start_time = time.perf_counter()
        status = "success"
        
        try:
            yield
        except Exception as e:
            status = "error"
            self.logger.warning(f"Operation {operation_name} failed: {e}")
            raise
        finally:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            # Record metrics
            metrics = PerformanceMetrics(
                operation=operation_name,
                duration_ms=duration_ms,
                status=status,
                metadata=metadata
            )
            self._metrics.append(metrics)
            
            # Log performance
            self.logger.info(f"⏱️ {operation_name}: {duration_ms:.2f}ms [{status}]")
    
    def get_metrics(self) -> list[PerformanceMetrics]:
        """Get all recorded metrics"""
        return self._metrics.copy()
    
    def clear_metrics(self) -> None:
        """Clear all recorded metrics"""
        self._metrics.clear()


# Global performance metrics collector for advanced use cases
_global_collector = PerformanceMetricsCollector("apps.performance")


def performance_timer(operation_name: str) -> PerformanceTimer:
    """
    Performance timer function that matches the infra.db.performance interface
    Usage: with performance_timer("operation_name"): ...
    Returns synchronous context manager compatible with existing router code.
    """
    return PerformanceTimer(operation_name)


def create_performance_timer(operation_name: str) -> PerformanceTimer:
    """Create a new performance timer instance for a specific operation"""
    return PerformanceTimer(operation_name)


# Decorator for easy performance measurement
def measure_performance(operation_name: str):
    """Decorator for measuring function performance"""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                async with _global_collector.measure(operation_name):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                with performance_timer(operation_name):
                    return func(*args, **kwargs)
            return sync_wrapper
    return decorator


# For backward compatibility - expose as module-level function  
async def measure_operation(operation_name: str, **metadata):
    """Module-level function for measuring operations"""
    return _global_collector.measure(operation_name, **metadata)