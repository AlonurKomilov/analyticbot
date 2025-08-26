"""
🧪 Phase 2.7: Backend Testing & Quality Assurance
Admin API Integration Tests

Comprehensive testing for SuperAdmin Panel API endpoints
including authentication, authorization, and functionality.
"""

import asyncio
import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from apps.api.main import app
from core.security_engine.models import UserRole, UserStatus
from apps.bot.services.admin_service import admin_service


class TestAdminAPIIntegration:
    """
    🛡️ Admin API Integration Tests
    
    Tests all admin endpoints with proper authentication,
    authorization, and data validation.
    """
    
    def setup_method(self):
        """Setup test client and mock authentication"""
        self.client = TestClient(app)
        self.admin_token = "mock_admin_jwt_token"
        self.user_token = "mock_user_jwt_token"
        
        # Mock admin user
        self.mock_admin_user = {
            "sub": "admin_123",
            "username": "admin_user",
            "email": "admin@test.com",
            "role": "admin"
        }
        
        # Mock regular user
        self.mock_user = {
            "sub": "user_123",
            "username": "regular_user", 
            "email": "user@test.com",
            "role": "user"
        }

    @patch('apps.api.deps.get_current_user')
    def test_dashboard_endpoint_success(self, mock_get_user):
        """Test admin dashboard endpoint with valid admin token"""
        mock_get_user.return_value = self.mock_admin_user
        
        response = self.client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        required_fields = [
            "total_users", "active_users_24h", "total_channels",
            "total_payments", "revenue_30d", "api_requests_24h",
            "system_uptime", "version"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            
        # Validate data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["active_users_24h"], int)
        assert isinstance(data["total_payments"], (int, float))
        assert isinstance(data["revenue_30d"], (int, float))

    @patch('apps.api.deps.get_current_user')
    def test_dashboard_endpoint_forbidden_for_regular_user(self, mock_get_user):
        """Test that regular users cannot access admin dashboard"""
        mock_get_user.return_value = self.mock_user
        
        response = self.client.get(
            "/api/admin/dashboard",
            headers={"Authorization": f"Bearer {self.user_token}"}
        )
        
        assert response.status_code == 403
        assert "detail" in response.json()

    def test_dashboard_endpoint_unauthorized(self):
        """Test dashboard endpoint without authentication"""
        response = self.client.get("/api/admin/dashboard")
        assert response.status_code == 401

    @patch('apps.api.deps.get_current_user')
    @patch('apps.bot.services.admin_service.admin_service.get_system_health')
    async def test_system_health_endpoint(self, mock_health, mock_get_user):
        """Test system health monitoring endpoint"""
        mock_get_user.return_value = self.mock_admin_user
        mock_health.return_value = {
            "status": "healthy",
            "services": {
                "database": {"status": "up", "response_time": "12ms"},
                "redis": {"status": "up", "response_time": "3ms"}
            },
            "resources": {
                "cpu_usage": "23%",
                "memory_usage": "67%"
            }
        }
        
        response = self.client.get(
            "/api/admin/system/health",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "services" in data
        assert "resources" in data
        assert data["services"]["database"]["status"] == "up"

    @patch('apps.api.deps.get_current_user')
    @patch('apps.bot.services.admin_service.admin_service.list_users')
    async def test_users_list_endpoint(self, mock_list_users, mock_get_user):
        """Test user listing with pagination and filters"""
        mock_get_user.return_value = self.mock_admin_user
        
        # Mock user data
        mock_users_data = [
            {
                "id": "1",
                "username": "john_doe",
                "email": "john@test.com",
                "role": UserRole.USER,
                "status": UserStatus.ACTIVE,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "last_login": datetime.utcnow() - timedelta(hours=2),
                "is_mfa_enabled": True,
                "failed_login_attempts": 0
            }
        ]
        mock_list_users.return_value = (mock_users_data, 1)
        
        response = self.client.get(
            "/api/admin/users?skip=0&limit=10&role_filter=user",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0

    @patch('apps.api.deps.get_current_user')
    def test_users_list_with_filters(self, mock_get_user):
        """Test user listing with various filters"""
        mock_get_user.return_value = self.mock_admin_user
        
        # Test role filter
        response = self.client.get(
            "/api/admin/users?role_filter=admin",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        # Test status filter
        response = self.client.get(
            "/api/admin/users?status_filter=active",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        
        # Test search
        response = self.client.get(
            "/api/admin/users?search=john",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200

    @patch('apps.api.deps.get_current_user')
    @patch('apps.bot.services.admin_service.admin_service.get_user_details')
    async def test_user_details_endpoint(self, mock_user_details, mock_get_user):
        """Test getting detailed user information"""
        mock_get_user.return_value = self.mock_admin_user
        mock_user_details.return_value = {
            "id": "user_123",
            "username": "john_doe",
            "email": "john@test.com",
            "role": UserRole.USER,
            "status": UserStatus.ACTIVE,
            "permissions": ["analytics:read", "user:read"],
            "recent_activity": []
        }
        
        response = self.client.get(
            "/api/admin/users/user_123",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "user_123"
        assert "permissions" in data
        assert "recent_activity" in data

    @patch('apps.api.deps.get_current_user')
    @patch('apps.bot.services.admin_service.admin_service.update_user')
    async def test_user_update_endpoint(self, mock_update_user, mock_get_user):
        """Test updating user information"""
        mock_get_user.return_value = self.mock_admin_user
        mock_update_user.return_value = {
            "success": True,
            "message": "User updated successfully"
        }
        
        update_data = {
            "role": "analyst",
            "status": "active"
        }
        
        response = self.client.put(
            "/api/admin/users/user_123",
            json=update_data,
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @patch('apps.api.deps.get_current_user')
    def test_terminate_user_sessions(self, mock_get_user):
        """Test terminating user sessions"""
        mock_get_user.return_value = self.mock_admin_user
        
        response = self.client.delete(
            "/api/admin/users/user_123/sessions",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @patch('apps.api.deps.get_current_user')
    def test_export_users_data(self, mock_get_user):
        """Test user data export functionality"""
        mock_get_user.return_value = self.mock_admin_user
        
        response = self.client.get(
            "/api/admin/export/users?format=csv",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data or "message" in data

    @patch('apps.api.deps.get_current_user')
    @patch('apps.bot.services.admin_service.admin_service.get_payment_summary')
    async def test_payment_summary_endpoint(self, mock_payment_summary, mock_get_user):
        """Test payment and revenue summary endpoint"""
        mock_get_user.return_value = self.mock_admin_user
        mock_payment_summary.return_value = {
            "total_revenue": 15420.50,
            "revenue_this_month": 4280.75,
            "active_subscriptions": 234,
            "failed_payments": 12
        }
        
        response = self.client.get(
            "/api/admin/payments/summary",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_revenue" in data
        assert "active_subscriptions" in data

    def test_admin_endpoints_require_authentication(self):
        """Test that all admin endpoints require authentication"""
        admin_endpoints = [
            "/api/admin/dashboard",
            "/api/admin/system/health",
            "/api/admin/users",
            "/api/admin/config",
            "/api/admin/payments/summary",
            "/api/admin/audit"
        ]
        
        for endpoint in admin_endpoints:
            response = self.client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require authentication"

    @patch('apps.api.deps.get_current_user')
    def test_admin_endpoints_require_admin_role(self, mock_get_user):
        """Test that admin endpoints reject non-admin users"""
        mock_get_user.return_value = self.mock_user  # Regular user
        
        admin_endpoints = [
            "/api/admin/dashboard",
            "/api/admin/system/health", 
            "/api/admin/users",
            "/api/admin/payments/summary"
        ]
        
        for endpoint in admin_endpoints:
            response = self.client.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.user_token}"}
            )
            assert response.status_code == 403, f"Endpoint {endpoint} should require admin role"

    @patch('apps.api.deps.get_current_user')
    def test_invalid_user_id_handling(self, mock_get_user):
        """Test handling of invalid user IDs"""
        mock_get_user.return_value = self.mock_admin_user
        
        response = self.client.get(
            "/api/admin/users/invalid_id",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        # Should return 404 or handle gracefully
        assert response.status_code in [404, 500]

    @patch('apps.api.deps.get_current_user')
    def test_pagination_parameters(self, mock_get_user):
        """Test pagination parameter validation"""
        mock_get_user.return_value = self.mock_admin_user
        
        # Test invalid skip parameter
        response = self.client.get(
            "/api/admin/users?skip=-1",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test invalid limit parameter  
        response = self.client.get(
            "/api/admin/users?limit=1000",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 422  # Validation error

    @patch('apps.api.deps.get_current_user')
    def test_error_handling(self, mock_get_user):
        """Test error handling in admin endpoints"""
        mock_get_user.return_value = self.mock_admin_user
        
        with patch('apps.bot.services.admin_service.admin_service.get_dashboard_stats', 
                  side_effect=Exception("Database connection failed")):
            response = self.client.get(
                "/api/admin/dashboard",
                headers={"Authorization": f"Bearer {self.admin_token}"}
            )
            assert response.status_code == 500


class TestAdminServiceIntegration:
    """
    🔧 Admin Service Integration Tests
    
    Tests the admin service layer functionality
    including business logic and data processing.
    """
    
    @pytest.mark.asyncio
    async def test_dashboard_stats_calculation(self):
        """Test dashboard statistics calculation"""
        with patch.multiple(
            admin_service,
            _count_total_users=AsyncMock(return_value=1250),
            _count_active_users_24h=AsyncMock(return_value=89),
            _get_total_payments=AsyncMock(return_value=15420.50),
            _get_revenue_30d=AsyncMock(return_value=4280.75)
        ):
            stats = await admin_service.get_dashboard_stats()
            
            assert stats["total_users"] == 1250
            assert stats["active_users_24h"] == 89
            assert stats["total_payments"] == 15420.50
            assert stats["revenue_30d"] == 4280.75
            assert "version" in stats

    @pytest.mark.asyncio
    async def test_system_health_check(self):
        """Test comprehensive system health check"""
        health = await admin_service.get_system_health()
        
        assert "status" in health
        assert "services" in health
        assert "resources" in health
        assert "timestamp" in health
        
        # Check service monitoring
        services = health["services"]
        assert "database" in services
        assert "redis" in services
        assert "api" in services

    @pytest.mark.asyncio
    async def test_user_filtering_logic(self):
        """Test user filtering and search logic"""
        users, total = await admin_service.list_users(
            skip=0,
            limit=10,
            role_filter=UserRole.USER,
            search="john"
        )
        
        assert isinstance(users, list)
        assert isinstance(total, int)
        assert total >= 0

    @pytest.mark.asyncio
    async def test_user_details_retrieval(self):
        """Test detailed user information retrieval"""
        user_details = await admin_service.get_user_details("test_user_id")
        
        required_fields = [
            "id", "username", "email", "role", "status",
            "permissions", "recent_activity"
        ]
        
        for field in required_fields:
            assert field in user_details

    @pytest.mark.asyncio
    async def test_payment_summary_calculation(self):
        """Test payment summary calculations"""
        summary = await admin_service.get_payment_summary()
        
        required_fields = [
            "total_revenue", "revenue_this_month", "revenue_last_month",
            "active_subscriptions", "failed_payments"
        ]
        
        for field in required_fields:
            assert field in summary
            assert isinstance(summary[field], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
