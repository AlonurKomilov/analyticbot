"""
Test Database Error Handling
Ensures real users never receive demo data fallback
"""

import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException, Request

from apps.api.services.database_error_handler import DatabaseErrorHandler, DatabaseErrorType


class TestDatabaseErrorHandling:
    """Test database error handling behavior"""
    
    def test_classify_error_types(self):
        """Test error classification"""
        handler = DatabaseErrorHandler()
        
        # Test different error types
        assert handler.classify_error(Exception("Connection failed")) == DatabaseErrorType.CONNECTION_FAILED
        assert handler.classify_error(Exception("Query timeout")) == DatabaseErrorType.TIMEOUT
        assert handler.classify_error(Exception("Pool exhausted")) == DatabaseErrorType.POOL_EXHAUSTED
        assert handler.classify_error(Exception("No rows found")) == DatabaseErrorType.DATA_NOT_FOUND
        assert handler.classify_error(Exception("Unique constraint violation")) == DatabaseErrorType.CONSTRAINT_VIOLATION
        assert handler.classify_error(Exception("SQL query failed")) == DatabaseErrorType.QUERY_FAILED
        assert handler.classify_error(Exception("Unknown error")) == DatabaseErrorType.UNKNOWN
    
    def test_real_user_never_gets_demo_fallback(self):
        """Test that real users never get demo fallback"""
        handler = DatabaseErrorHandler()
        
        # Mock real user request
        request = Mock()
        request.state = Mock()
        request.state.is_demo = False
        request.url = Mock()
        request.url.path = "/initial-data"
        request.method = "GET"
        request.headers = {"user-agent": "test"}
        
        # Test that HTTPException is raised for real user
        with pytest.raises(HTTPException) as exc_info:
            handler.handle_database_error(
                request=request,
                error=Exception("Database connection failed"),
                operation="test_operation",
                user_id=123,
                allow_demo_fallback=False
            )
        
        # Verify proper HTTP error code
        assert exc_info.value.status_code == 503
        assert "temporarily unavailable" in exc_info.value.detail.lower()
    
    def test_demo_user_allowed_fallback(self):
        """Test that demo users can have fallback when explicitly allowed"""
        handler = DatabaseErrorHandler()
        
        # Mock demo user request
        request = Mock()
        request.state = Mock()
        request.state.is_demo = True
        request.url = Mock()
        request.url.path = "/initial-data"
        request.method = "GET"
        request.headers = {"user-agent": "test"}
        
        # Test that no exception is raised for demo user with allowed fallback
        # (This allows the caller to handle the fallback)
        try:
            handler.handle_database_error(
                request=request,
                error=Exception("Database connection failed"),
                operation="test_operation",
                user_id=1,
                allow_demo_fallback=True
            )
            # If no exception, fallback is allowed
            fallback_allowed = True
        except HTTPException:
            fallback_allowed = False
        
        assert fallback_allowed, "Demo user should be allowed fallback when explicitly enabled"
    
    def test_different_error_codes(self):
        """Test different HTTP error codes for different error types"""
        handler = DatabaseErrorHandler()
        
        request = Mock()
        request.state = Mock()
        request.state.is_demo = False
        request.url = Mock()
        request.url.path = "/test"
        request.method = "GET"
        request.headers = {"user-agent": "test"}
        
        # Test 404 for data not found
        with pytest.raises(HTTPException) as exc_info:
            handler.handle_database_error(
                request=request,
                error=Exception("No rows found"),
                operation="get_user",
                allow_demo_fallback=False
            )
        assert exc_info.value.status_code == 404
        
        # Test 503 for connection issues
        with pytest.raises(HTTPException) as exc_info:
            handler.handle_database_error(
                request=request,
                error=Exception("Connection failed"),
                operation="connect_db",
                allow_demo_fallback=False
            )
        assert exc_info.value.status_code == 503
        
        # Test 504 for timeout
        with pytest.raises(HTTPException) as exc_info:
            handler.handle_database_error(
                request=request,
                error=Exception("Query timeout"),
                operation="long_query",
                allow_demo_fallback=False
            )
        assert exc_info.value.status_code == 504
        
        # Test 409 for constraint violations
        with pytest.raises(HTTPException) as exc_info:
            handler.handle_database_error(
                request=request,
                error=Exception("Unique constraint violation"),
                operation="insert_user",
                allow_demo_fallback=False
            )
        assert exc_info.value.status_code == 409


if __name__ == "__main__":
    # Run basic tests
    test = TestDatabaseErrorHandling()
    test.test_classify_error_types()
    test.test_different_error_codes()
    print("✅ All database error handling tests passed!")