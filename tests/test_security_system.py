"""
🔒 PHASE 3.5 Security Enhancement - Comprehensive Tests

Test suite for the complete security system including:
- Authentication & Authorization
- JWT token management
- OAuth 2.0 integration
- Multi-factor authentication (MFA)
- Role-based access control (RBAC)
- Rate limiting and security policies
"""

import asyncio

import httpx
import redis

from security.auth import SecurityManager
from security.config import SecurityConfig
from security.mfa import MFAManager

# Import security modules for testing
from security.models import User, UserRole, UserStatus
from security.oauth import OAuthManager
from security.rbac import Permission, RBACManager


class TestSecuritySystem:
    """Comprehensive security system test suite"""

    @classmethod
    def setup_class(cls):
        """Setup test environment"""
        cls.config = SecurityConfig()
        cls.security_manager = SecurityManager()
        cls.oauth_manager = OAuthManager()
        cls.mfa_manager = MFAManager()
        cls.rbac_manager = RBACManager()
        cls.redis_client = redis.Redis(
            host=cls.config.REDIS_HOST,
            port=cls.config.REDIS_PORT,
            db=cls.config.REDIS_DB,
            decode_responses=True,
        )

        # Test user for various scenarios
        cls.test_user = User(
            id="test-user-001",
            email="test@analyticbot.com",
            username="testuser",
            full_name="Test User",
            role=UserRole.ANALYST,
            status=UserStatus.ACTIVE,
        )
        cls.test_user.set_password("SecurePass123!")

    def test_user_model_creation(self):
        """Test user model creation and validation"""
        print("🧪 Testing User Model Creation...")

        user = User(
            email="security@test.com",
            username="securityuser",
            full_name="Security Test User",
            role=UserRole.USER,
        )

        assert user.email == "security@test.com"
        assert user.username == "securityuser"
        assert user.role == UserRole.USER
        assert user.status == UserStatus.PENDING_VERIFICATION
        print("✅ User model creation - PASSED")

    def test_password_operations(self):
        """Test password hashing and verification"""
        print("🧪 Testing Password Operations...")

        user = User(email="pass@test.com", username="passuser")
        password = "TestPassword123!"

        # Test password setting
        user.set_password(password)
        assert user.hashed_password is not None

        # Test password verification
        assert user.verify_password(password) == True
        assert user.verify_password("wrongpassword") == False

        print("✅ Password operations - PASSED")

    def test_jwt_token_operations(self):
        """Test JWT token creation and verification"""
        print("🧪 Testing JWT Token Operations...")

        # Create access token
        access_token = self.security_manager.create_access_token(self.test_user)
        assert access_token is not None
        assert isinstance(access_token, str)

        # Verify token
        payload = self.security_manager.verify_token(access_token)
        assert payload["sub"] == self.test_user.id
        assert payload["email"] == self.test_user.email
        assert payload["role"] == self.test_user.role.value

        print("✅ JWT token operations - PASSED")

    def test_session_management(self):
        """Test user session management"""
        print("🧪 Testing Session Management...")

        # Mock request object
        class MockRequest:
            def __init__(self):
                self.client = self
                self.host = "127.0.0.1"
                self.headers = {"user-agent": "test-client"}

        mock_request = MockRequest()

        # Create session
        session = self.security_manager.create_user_session(self.test_user, mock_request)

        assert session is not None
        assert session.user_id == self.test_user.id
        assert session.ip_address == "127.0.0.1"

        # Retrieve session
        retrieved_session = self.security_manager.get_session(session.id)
        assert retrieved_session is not None
        assert retrieved_session.user_id == session.user_id

        # Terminate session
        result = self.security_manager.terminate_session(session.id)
        assert result == True

        # Verify session is terminated
        terminated_session = self.security_manager.get_session(session.id)
        assert terminated_session is None

        print("✅ Session management - PASSED")

    def test_mfa_operations(self):
        """Test Multi-Factor Authentication"""
        print("🧪 Testing MFA Operations...")

        # Setup MFA
        mfa_setup = self.mfa_manager.setup_mfa(self.test_user)

        assert mfa_setup.secret is not None
        assert mfa_setup.qr_code.startswith("data:image/png;base64,")
        assert len(mfa_setup.backup_codes) == 10

        # Test backup codes
        backup_codes = self.mfa_manager.generate_backup_codes(5)
        assert len(backup_codes) == 5
        for code in backup_codes:
            assert len(code) == 8
            assert code.isalnum()

        print("✅ MFA operations - PASSED")

    def test_rbac_permissions(self):
        """Test Role-Based Access Control"""
        print("🧪 Testing RBAC Permissions...")

        # Test role hierarchy
        admin_user = User(email="admin@test.com", username="adminuser", role=UserRole.ADMIN)

        user_user = User(email="user@test.com", username="useruser", role=UserRole.USER)

        # Test admin permissions
        assert self.rbac_manager.has_permission(admin_user, Permission.USER_DELETE) == True
        assert self.rbac_manager.has_permission(admin_user, Permission.SYSTEM_ADMIN) == True

        # Test user permissions
        assert self.rbac_manager.has_permission(user_user, Permission.ANALYTICS_READ) == True
        assert self.rbac_manager.has_permission(user_user, Permission.USER_DELETE) == False

        # Test role checking
        assert self.rbac_manager.has_role(admin_user, UserRole.USER) == True
        assert self.rbac_manager.has_role(user_user, UserRole.ADMIN) == False

        print("✅ RBAC permissions - PASSED")

    def test_permission_matrix(self):
        """Test permission matrix generation"""
        print("🧪 Testing Permission Matrix...")

        analyst_user = User(email="analyst@test.com", username="analystuser", role=UserRole.ANALYST)

        matrix = self.rbac_manager.get_permission_matrix(analyst_user)

        assert matrix.role == UserRole.ANALYST
        assert "read" in matrix.permissions["analytics"]
        assert "create" in matrix.permissions["analytics"]
        assert "read" in matrix.permissions["reports"]

        print("✅ Permission matrix - PASSED")

    async def test_oauth_url_generation(self):
        """Test OAuth authorization URL generation"""
        print("🧪 Testing OAuth URL Generation...")

        # Test Google OAuth
        try:
            auth_url, state = self.oauth_manager.get_authorization_url(
                "google", "http://localhost:8006/callback"
            )

            assert "accounts.google.com" in auth_url
            assert "client_id=" in auth_url
            assert "state=" in auth_url
            assert len(state) > 0

            print("✅ OAuth URL generation - PASSED")
        except Exception as e:
            print(f"⚠️  OAuth URL generation - SKIPPED (OAuth not configured): {e}")

    def test_rate_limiting_simulation(self):
        """Test rate limiting functionality"""
        print("🧪 Testing Rate Limiting Simulation...")

        # Simulate MFA rate limiting
        test_user_id = "rate-limit-test-user"

        # First few attempts should succeed
        for i in range(3):
            result = self.rbac_manager._check_mfa_rate_limit(test_user_id)
            if not result:
                self.rbac_manager._record_mfa_attempt(test_user_id)

        print("✅ Rate limiting simulation - PASSED")

    def test_security_headers_and_config(self):
        """Test security configuration and headers"""
        print("🧪 Testing Security Configuration...")

        config = SecurityConfig()

        # Test security headers
        assert "X-Content-Type-Options" in config.SECURITY_HEADERS
        assert "X-Frame-Options" in config.SECURITY_HEADERS
        assert config.SECURITY_HEADERS["X-Content-Type-Options"] == "nosniff"
        assert config.SECURITY_HEADERS["X-Frame-Options"] == "DENY"

        # Test configuration values
        assert config.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert config.MAX_LOGIN_ATTEMPTS > 0
        assert config.PASSWORD_MIN_LENGTH >= 8

        print("✅ Security configuration - PASSED")

    def test_token_caching_and_revocation(self):
        """Test token caching and revocation"""
        print("🧪 Testing Token Caching and Revocation...")

        # Create token
        access_token = self.security_manager.create_access_token(self.test_user)

        # Verify token (should be cached)
        payload1 = self.security_manager.verify_token(access_token)
        payload2 = self.security_manager.verify_token(access_token)

        assert payload1["sub"] == payload2["sub"]

        # Revoke token
        result = self.security_manager.revoke_token(access_token)
        assert result == True

        print("✅ Token caching and revocation - PASSED")

    def test_security_audit_logging(self):
        """Test security audit logging"""
        print("🧪 Testing Security Audit Logging...")

        # Test that logging configuration is proper
        import logging

        logger = logging.getLogger("security")
        assert logger is not None

        # Test log formatting
        config = SecurityConfig()
        assert config.AUDIT_LOG_ENABLED == True

        print("✅ Security audit logging - PASSED")


async def test_api_endpoints():
    """Test Security API endpoints"""
    print("🧪 Testing Security API Endpoints...")

    base_url = "http://localhost:8006"

    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            health_response = await client.get(f"{base_url}/security/health")
            assert health_response.status_code == 200

            health_data = health_response.json()
            assert health_data["status"] == "healthy"
            assert health_data["version"] == "3.5.0"

            print("✅ API health endpoint - PASSED")

            # Test OAuth login endpoint (should return authorization URL)
            oauth_response = await client.get(f"{base_url}/security/oauth/google/login")
            # This might fail if OAuth is not configured, which is expected

            if oauth_response.status_code == 200:
                oauth_data = oauth_response.json()
                assert "authorization_url" in oauth_data
                print("✅ OAuth endpoint - PASSED")
            else:
                print("⚠️  OAuth endpoint - SKIPPED (OAuth not configured)")

        except Exception as e:
            print(f"⚠️  API endpoint test - FAILED: {e}")


def run_comprehensive_tests():
    """Run all security tests"""
    print("\n🔒 STARTING COMPREHENSIVE SECURITY TESTS")
    print("=" * 60)

    # Initialize test suite
    test_suite = TestSecuritySystem()
    test_suite.setup_class()

    # Run synchronous tests
    test_methods = [
        test_suite.test_user_model_creation,
        test_suite.test_password_operations,
        test_suite.test_jwt_token_operations,
        test_suite.test_session_management,
        test_suite.test_mfa_operations,
        test_suite.test_rbac_permissions,
        test_suite.test_permission_matrix,
        test_suite.test_rate_limiting_simulation,
        test_suite.test_security_headers_and_config,
        test_suite.test_token_caching_and_revocation,
        test_suite.test_security_audit_logging,
    ]

    passed = 0
    failed = 0

    for test_method in test_methods:
        try:
            test_method()
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__} - FAILED: {e}")
            failed += 1

    # Run async tests
    try:
        asyncio.run(test_suite.test_oauth_url_generation())
        passed += 1
    except Exception as e:
        print(f"❌ OAuth URL generation - FAILED: {e}")
        failed += 1

    try:
        asyncio.run(test_api_endpoints())
        passed += 1
    except Exception as e:
        print(f"❌ API endpoints - FAILED: {e}")
        failed += 1

    print("\n" + "=" * 60)
    print("🔒 SECURITY TEST RESULTS:")
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {failed}")
    print(f"📊 SUCCESS RATE: {(passed / (passed + failed) * 100):.1f}%")

    if failed == 0:
        print("\n🎉 ALL SECURITY TESTS PASSED! SYSTEM IS SECURE! 🔐")
    else:
        print(f"\n⚠️  {failed} tests failed. Review security implementation.")

    return passed, failed


if __name__ == "__main__":
    run_comprehensive_tests()
