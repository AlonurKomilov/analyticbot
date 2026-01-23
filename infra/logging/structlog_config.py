"""
Structured logging configuration with JSON format using structlog.

This module provides standardized JSON logging across the application
with proper correlation IDs, error context, and performance metrics.

Usage:
    from infra.logging.structlog_config import configure_logging, get_logger

    # Configure at application startup
    configure_logging(
        log_level="INFO",
        json_format=True,
        correlation_id=True
    )

    # Use in modules
    logger = get_logger(__name__)
    logger.info("User logged in", user_id=123, session_id="abc-123")
"""

import json
import logging
import os
import sys
import time
from contextlib import contextmanager
from typing import Any

try:
    import structlog
    from structlog import stdlib
    from structlog.processors import TimeStamper

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    structlog = None


class AnalyticBotJSONRenderer:
    """Custom JSON renderer for AnalyticBot with standardized fields."""

    def __init__(self, serializer=json.dumps, **dumps_kw):
        self.serializer = serializer
        self.dumps_kw = dumps_kw

    def __call__(self, logger, method_name, event_dict):
        """Render log entry as JSON with standardized structure."""

        # Extract standard fields
        timestamp = event_dict.pop("timestamp", time.time())
        level = event_dict.pop("level", method_name.upper())
        event = event_dict.pop("event", "")

        # Build standardized log structure
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "event": event,
            "service": "analyticbot",
            "version": "1.0.0",
        }

        # Add correlation ID if available
        if "correlation_id" in event_dict:
            log_entry["correlation_id"] = event_dict.pop("correlation_id")

        # Add error context if available
        if "error" in event_dict:
            error_info = event_dict.pop("error")
            if isinstance(error_info, dict):
                log_entry["error"] = error_info
            else:
                log_entry["error"] = {"message": str(error_info)}

        # Add performance metrics if available
        if "duration_ms" in event_dict:
            log_entry["performance"] = {"duration_ms": event_dict.pop("duration_ms")}

        # Add remaining fields as context
        if event_dict:
            log_entry["context"] = event_dict

        return self.serializer(log_entry, **self.dumps_kw)


class PlainTextRenderer:
    """Fallback plain text renderer when structlog is not available."""

    def __call__(self, logger, method_name, event_dict):
        """Render log entry as plain text."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        level = method_name.upper()
        event = event_dict.pop("event", "")

        # Format context
        context_parts = []
        for key, value in event_dict.items():
            if key not in ["timestamp", "level"]:
                context_parts.append(f"{key}={value}")

        context_str = " ".join(context_parts)
        if context_str:
            return f"{timestamp} [{level}] {event} | {context_str}"
        else:
            return f"{timestamp} [{level}] {event}"


class CorrelationIdProcessor:
    """Processor to add correlation IDs to log entries."""

    def __init__(self):
        self._correlation_id = None

    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current context."""
        self._correlation_id = correlation_id

    def clear_correlation_id(self):
        """Clear correlation ID."""
        self._correlation_id = None

    def __call__(self, logger, method_name, event_dict):
        """Add correlation ID to log entry if available."""
        if self._correlation_id:
            event_dict["correlation_id"] = self._correlation_id
        return event_dict


# Global correlation ID processor instance
correlation_processor = CorrelationIdProcessor()


def configure_logging(
    log_level: str = None,
    json_format: bool = None,
    correlation_id: bool = True,
    performance_logging: bool = True,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON format (default: True in production)
        correlation_id: Whether to include correlation IDs
        performance_logging: Whether to enable performance logging
    """

    # Determine defaults from environment
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if json_format is None:
        # Use JSON format in production, plain text in development
        env = os.getenv("ENVIRONMENT", "development")
        json_format = env.lower() in ["production", "prod"]

    # Configure standard library logging
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=getattr(logging, log_level))

    if STRUCTLOG_AVAILABLE:
        # Configure structlog processors
        processors = [
            stdlib.filter_by_level,
            stdlib.add_logger_name,
            stdlib.add_log_level,
        ]

        if correlation_id:
            processors.append(correlation_processor)

        processors.extend(
            [
                stdlib.PositionalArgumentsFormatter(),
                TimeStamper(fmt="iso", utc=True),
                stdlib.ProcessorFormatter.wrap_for_formatter,
            ]
        )

        # Configure structlog
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=stdlib.LoggerFactory(),
            wrapper_class=stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Configure formatter for standard library integration
        formatter = stdlib.ProcessorFormatter(
            processor=AnalyticBotJSONRenderer() if json_format else PlainTextRenderer(),
        )
    else:
        # Fallback to standard logging when structlog unavailable
        if json_format:
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"event": "%(message)s", "service": "analyticbot"}'
            )
        else:
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Apply formatter to root logger
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)


def get_logger(name: str = None):
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance (structlog if available, otherwise standard logging)
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


@contextmanager
def correlation_context(correlation_id: str):
    """
    Context manager for correlation ID logging.

    Usage:
        with correlation_context("req-123"):
            logger.info("Processing request")  # Will include correlation_id=req-123
    """
    correlation_processor.set_correlation_id(correlation_id)
    try:
        yield
    finally:
        correlation_processor.clear_correlation_id()


@contextmanager
def performance_context(operation_name: str, logger=None):
    """
    Context manager for performance logging.

    Usage:
        with performance_context("database_query", logger):
            # Perform database operation
            pass
        # Automatically logs duration
    """
    if logger is None:
        logger = get_logger(__name__)

    start_time = time.time()
    try:
        yield
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            "Operation failed",
            operation=operation_name,
            duration_ms=duration_ms,
            error=str(e),
        )
        raise
    else:
        duration_ms = (time.time() - start_time) * 1000
        logger.info("Operation completed", operation=operation_name, duration_ms=duration_ms)


def log_error_with_context(
    logger, message: str, error: Exception, context: dict[str, Any] = None
) -> str:
    """
    Log error with standardized context and return error ID.

    Args:
        logger: Logger instance
        message: Error message
        error: Exception instance
        context: Additional context dictionary

    Returns:
        Error ID for tracking
    """
    import uuid

    error_id = str(uuid.uuid4())[:8]

    error_context = {
        "error_id": error_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    if context:
        error_context.update(context)

    logger.error(message, **error_context)

    return error_id


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    configure_logging(log_level="INFO", json_format=True)

    # Get logger
    logger = get_logger(__name__)

    # Test basic logging
    logger.info("Application started", version="1.0.0", environment="development")

    # Test with correlation ID
    with correlation_context("test-123"):
        logger.info("Processing request", user_id=456)

        # Test performance logging
        with performance_context("test_operation", logger):
            time.sleep(0.1)  # Simulate work

    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_id = log_error_with_context(
            logger, "Test error occurred", e, {"operation": "testing", "user_id": 123}
        )
        print(f"Error logged with ID: {error_id}")
