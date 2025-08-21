"""
Centralized error handling utilities.
"""

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class ErrorContext:
    """Error context for better debugging"""

    def __init__(self):
        self.context: dict[str, Any] = {}

    def add(self, key: str, value: Any) -> "ErrorContext":
        """Add context information"""
        self.context[key] = value
        return self

    def get_context(self) -> dict[str, Any]:
        """Get all context information"""
        return self.context.copy()


class ErrorHandler:
    """Centralized error handling"""

    @staticmethod
    def log_error(
        error: Exception,
        context: ErrorContext | None = None,
        level: int = logging.ERROR,
        exc_info: bool = True,
    ) -> str:
        """
        Log error with context information.
        Returns error ID for tracking.
        """
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}"

        log_data = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
        }

        if context:
            log_data["context"] = context.get_context()

        logger.log(
            level, f"Error {error_id}: {error}", extra=log_data, exc_info=exc_info
        )

        return error_id

    @staticmethod
    def handle_telegram_api_error(
        error: Exception, context: ErrorContext | None = None
    ) -> str:
        """Handle Telegram API specific errors"""
        if context is None:
            context = ErrorContext()

        context.add("error_source", "telegram_api")

        # Check for specific Telegram errors
        error_msg = str(error).lower()
        if "bot was kicked" in error_msg:
            context.add("error_category", "bot_kicked")
        elif "message to delete not found" in error_msg:
            context.add("error_category", "message_not_found")
        elif "rate limit" in error_msg or "too many requests" in error_msg:
            context.add("error_category", "rate_limit")
        else:
            context.add("error_category", "unknown_telegram_error")

        return ErrorHandler.log_error(error, context)

    @staticmethod
    def handle_database_error(
        error: Exception, context: ErrorContext | None = None
    ) -> str:
        """Handle database specific errors"""
        if context is None:
            context = ErrorContext()

        context.add("error_source", "database")

        # Check for specific database errors
        error_msg = str(error).lower()
        if "connection" in error_msg:
            context.add("error_category", "connection_error")
        elif "timeout" in error_msg:
            context.add("error_category", "timeout")
        elif "constraint" in error_msg:
            context.add("error_category", "constraint_violation")
        else:
            context.add("error_category", "unknown_database_error")

        return ErrorHandler.log_error(error, context)


def safe_execute(func, *args, **kwargs):
    """
    Safely execute a function with error handling
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = ErrorContext().add("function", func.__name__)
        ErrorHandler.log_error(e, context)
        return None


async def safe_execute_async(func, *args, **kwargs):
    """
    Safely execute an async function with error handling
    """
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        context = ErrorContext().add("function", func.__name__)
        ErrorHandler.log_error(e, context)
        return None
