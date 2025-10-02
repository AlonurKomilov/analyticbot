"""
Database Error Handler
Comprehensive error handling and auditing for database operations
"""

import logging
from datetime import datetime
from enum import Enum

from fastapi import HTTPException, Request

from config import settings

logger = logging.getLogger(__name__)


class DatabaseErrorType(str, Enum):
    """Types of database errors"""

    CONNECTION_FAILED = "connection_failed"
    QUERY_FAILED = "query_failed"
    TIMEOUT = "timeout"
    POOL_EXHAUSTED = "pool_exhausted"
    DATA_NOT_FOUND = "data_not_found"
    CONSTRAINT_VIOLATION = "constraint_violation"
    UNKNOWN = "unknown"


class DatabaseErrorHandler:
    """
    Centralized database error handling and auditing
    Ensures proper error responses and prevents inappropriate demo fallbacks
    """

    @staticmethod
    def classify_error(error: Exception) -> DatabaseErrorType:
        """Classify database error type for proper handling"""
        error_msg = str(error).lower()

        if "connection" in error_msg or "connect" in error_msg:
            return DatabaseErrorType.CONNECTION_FAILED
        elif "timeout" in error_msg:
            return DatabaseErrorType.TIMEOUT
        elif "pool" in error_msg:
            return DatabaseErrorType.POOL_EXHAUSTED
        elif "not found" in error_msg or "no rows" in error_msg:
            return DatabaseErrorType.DATA_NOT_FOUND
        elif "constraint" in error_msg or "unique" in error_msg:
            return DatabaseErrorType.CONSTRAINT_VIOLATION
        elif "query" in error_msg or "sql" in error_msg:
            return DatabaseErrorType.QUERY_FAILED
        else:
            return DatabaseErrorType.UNKNOWN

    @staticmethod
    def audit_database_error(
        request: Request,
        error: Exception,
        operation: str,
        user_id: int | None = None,
        fallback_activated: bool = False,
    ):
        """
        Audit database errors for monitoring and security

        Args:
            request: HTTP request context
            error: The database error that occurred
            operation: Description of the operation that failed
            user_id: User ID if available
            fallback_activated: Whether fallback was used
        """
        error_type = DatabaseErrorHandler.classify_error(error)

        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": error_type.value,
            "operation": operation,
            "error_message": str(error),
            "user_id": user_id,
            "request_path": str(request.url.path) if request else "unknown",
            "request_method": request.method if request else "unknown",
            "user_agent": (request.headers.get("user-agent", "unknown") if request else "unknown"),
            "fallback_activated": fallback_activated,
            "is_demo_user": (getattr(request.state, "is_demo", False) if request else False),
        }

        # Log based on severity
        if error_type in [
            DatabaseErrorType.CONNECTION_FAILED,
            DatabaseErrorType.POOL_EXHAUSTED,
        ]:
            logger.critical(f"🚨 Critical database error: {audit_data}")
        elif error_type in [DatabaseErrorType.TIMEOUT, DatabaseErrorType.QUERY_FAILED]:
            logger.error(f"❌ Database error: {audit_data}")
        elif error_type == DatabaseErrorType.DATA_NOT_FOUND:
            logger.warning(f"⚠️ Data not found: {audit_data}")
        else:
            logger.error(f"❌ Unknown database error: {audit_data}")

        # In production, would send to monitoring system
        if settings.ENVIRONMENT == "production":
            # TODO: Send to monitoring system (e.g., Sentry, DataDog)
            pass

    @staticmethod
    def handle_database_error(
        request: Request,
        error: Exception,
        operation: str,
        user_id: int | None = None,
        allow_demo_fallback: bool = False,
    ) -> None:
        """
        Handle database errors with proper response and auditing

        Args:
            request: HTTP request context
            error: The database error that occurred
            operation: Description of the operation that failed
            user_id: User ID if available
            allow_demo_fallback: Whether demo fallback is allowed for this operation

        Raises:
            HTTPException: Appropriate HTTP error response
        """
        error_type = DatabaseErrorHandler.classify_error(error)

        # Check if demo fallback is appropriate
        fallback_activated = False
        is_demo_user = getattr(request.state, "is_demo", False) if request else False

        if allow_demo_fallback and is_demo_user:
            fallback_activated = True
            logger.info(f"Demo fallback activated for demo user due to {error_type.value}")

        # Audit the error
        DatabaseErrorHandler.audit_database_error(
            request=request,
            error=error,
            operation=operation,
            user_id=user_id,
            fallback_activated=fallback_activated,
        )

        # If fallback is activated, don't raise exception (let caller handle fallback)
        if fallback_activated:
            return

        # For real users, always return proper HTTP errors
        if error_type == DatabaseErrorType.DATA_NOT_FOUND:
            raise HTTPException(status_code=404, detail="Requested resource not found")
        elif error_type in [
            DatabaseErrorType.CONNECTION_FAILED,
            DatabaseErrorType.POOL_EXHAUSTED,
        ]:
            raise HTTPException(
                status_code=503,
                detail="Database service temporarily unavailable. Please try again later.",
            )
        elif error_type == DatabaseErrorType.TIMEOUT:
            raise HTTPException(status_code=504, detail="Request timeout. Please try again.")
        elif error_type == DatabaseErrorType.CONSTRAINT_VIOLATION:
            raise HTTPException(
                status_code=409,
                detail="Data conflict. Please check your input and try again.",
            )
        else:
            raise HTTPException(
                status_code=500, detail="Internal server error. Please try again later."
            )


# Convenience instance
db_error_handler = DatabaseErrorHandler()
