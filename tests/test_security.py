"""
Security Tests for AnalyticBot
Tests security-related functionality and vulnerability prevention
"""
import hashlib
import secrets
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

# Security-related imports

# Test factories


@pytest.mark.security
class TestInputSanitization:
    """Test input sanitization and validation"""
    
    def test_username_sanitization(self):
        """Test username input sanitization"""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "admin' OR '1'='1",
            "\x00\x01\x02",  # Null bytes
            "a" * 1000,  # Very long input
        ]
        
        def sanitize_username(username: str) -> str:
            """Simple username sanitization"""
            if not username or len(username) > 50:
                return ""
                
            # Remove dangerous characters
            dangerous_chars = ["<", ">", "'", '"', ";", "--", "/", "\\", "\x00"]
            for char in dangerous_chars:
                username = username.replace(char, "")
                
            return username.strip()
        
        for dangerous_input in dangerous_inputs:
            sanitized = sanitize_username(dangerous_input)
            
            # Should not contain dangerous patterns
            assert "<script>" not in sanitized.lower()
            assert "drop table" not in sanitized.lower()
            assert "../" not in sanitized
            assert "'" not in sanitized
            assert len(sanitized) <= 50
    
    def test_payment_amount_validation(self):
        """Test payment amount validation against manipulation"""
        test_amounts = [
            ("25.00", True),
            ("0.01", True),
            ("9999.99", True),
            ("-25.00", False),  # Negative amounts
            ("0", False),  # Zero amounts
            ("abc", False),  # Non-numeric
            ("25.999", False),  # Too many decimal places
            ("99999999.99", False),  # Too large
            ("", False),  # Empty
            (None, False),  # Null
        ]
        
        def validate_payment_amount(amount) -> bool:
            """Validate payment amount"""
            if not amount:
                return False
                
            try:
                amount_float = float(amount)
                
                # Must be positive
                if amount_float <= 0:
                    return False
                    
                # Maximum reasonable amount
                if amount_float > 10000:
                    return False
                    
                # Check decimal places (max 2)
                amount_str = str(amount)
                if '.' in amount_str:
                    decimal_places = len(amount_str.split('.')[1])
                    if decimal_places > 2:
                        return False
                        
                return True
                
            except (ValueError, TypeError):
                return False
        
        for amount, expected_valid in test_amounts:
            is_valid = validate_payment_amount(amount)
            assert is_valid == expected_valid, f"Amount {amount} validation failed"


@pytest.mark.security
class TestAuthenticationSecurity:
    """Test authentication and authorization security"""
    
    def test_session_token_generation(self):
        """Test secure session token generation"""
        def generate_session_token() -> str:
            """Generate cryptographically secure session token"""
            return secrets.token_urlsafe(32)
        
        # Generate multiple tokens
        tokens = [generate_session_token() for _ in range(100)]
        
        # All tokens should be unique
        assert len(set(tokens)) == 100
        
        # All tokens should be proper length (base64url encoded 32 bytes = 43 chars)
        for token in tokens:
            assert len(token) >= 40  # Account for base64 padding variations
            assert len(token) <= 45
            
            # Should only contain URL-safe characters
            allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
            assert set(token).issubset(allowed_chars)
    
    def test_password_hashing_security(self):
        """Test password hashing security"""
        test_passwords = [
            "password123",
            "super_secure_password!@#",
            "短密码",  # Unicode password
            "a" * 100,  # Long password
        ]
        
        def hash_password(password: str) -> str:
            """Secure password hashing"""
            # Add salt for security
            salt = secrets.token_hex(16)
            
            # Use SHA-256 (in production, use bcrypt/scrypt/argon2)
            password_with_salt = password + salt
            hashed = hashlib.sha256(password_with_salt.encode()).hexdigest()
            
            return f"{salt}:{hashed}"
        
        def verify_password(password: str, hash_with_salt: str) -> bool:
            """Verify password against hash"""
            try:
                salt, stored_hash = hash_with_salt.split(":", 1)
                password_with_salt = password + salt
                computed_hash = hashlib.sha256(password_with_salt.encode()).hexdigest()
                return secrets.compare_digest(stored_hash, computed_hash)
            except ValueError:
                return False
        
        for password in test_passwords:
            # Hash password
            password_hash = hash_password(password)
            
            # Should be able to verify correct password
            assert verify_password(password, password_hash) is True
            
            # Should reject incorrect password
            assert verify_password(password + "wrong", password_hash) is False
            assert verify_password("wrong" + password, password_hash) is False
            
            # Hash should contain salt and be sufficiently long
            assert ":" in password_hash
            salt, hash_part = password_hash.split(":", 1)
            assert len(salt) == 32  # 16 bytes hex = 32 chars
            assert len(hash_part) == 64  # SHA-256 = 64 chars hex


@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting security measures"""
    
    def test_request_rate_limiting(self):
        """Test basic request rate limiting"""
        import time
        from collections import defaultdict
        
        class SimpleRateLimiter:
            def __init__(self, max_requests: int = 10, window_seconds: int = 60):
                self.max_requests = max_requests
                self.window_seconds = window_seconds
                self.requests = defaultdict(list)
            
            def is_allowed(self, user_id: str) -> bool:
                now = time.time()
                
                # Clean old requests
                self.requests[user_id] = [
                    req_time for req_time in self.requests[user_id]
                    if now - req_time < self.window_seconds
                ]
                
                # Check if under limit
                if len(self.requests[user_id]) >= self.max_requests:
                    return False
                
                # Record this request
                self.requests[user_id].append(now)
                return True
        
        rate_limiter = SimpleRateLimiter(max_requests=5, window_seconds=10)
        user_id = "test_user_123"
        
        # First 5 requests should be allowed
        for _i in range(5):
            assert rate_limiter.is_allowed(user_id) is True
        
        # 6th request should be blocked
        assert rate_limiter.is_allowed(user_id) is False
        
        # Different user should still be allowed
        other_user = "other_user_456"
        assert rate_limiter.is_allowed(other_user) is True
    
    def test_payment_rate_limiting(self):
        """Test payment-specific rate limiting"""
        class PaymentRateLimiter:
            def __init__(self):
                self.payment_attempts = defaultdict(list)
                self.max_attempts_per_hour = 3
            
            def can_attempt_payment(self, user_id: int) -> bool:
                now = datetime.utcnow()
                one_hour_ago = now - timedelta(hours=1)
                
                # Clean old attempts
                self.payment_attempts[user_id] = [
                    attempt_time for attempt_time in self.payment_attempts[user_id]
                    if attempt_time > one_hour_ago
                ]
                
                # Check if under limit
                if len(self.payment_attempts[user_id]) >= self.max_attempts_per_hour:
                    return False
                
                # Record attempt
                self.payment_attempts[user_id].append(now)
                return True
        
        limiter = PaymentRateLimiter()
        user_id = 123456789
        
        # First 3 payment attempts should be allowed
        for _i in range(3):
            assert limiter.can_attempt_payment(user_id) is True
        
        # 4th attempt should be blocked
        assert limiter.can_attempt_payment(user_id) is False
        
        # Different user should still be allowed
        assert limiter.can_attempt_payment(987654321) is True


@pytest.mark.security
class TestDataPrivacySecurity:
    """Test data privacy and PII protection"""
    
    def test_pii_masking(self):
        """Test PII data masking for logs"""
        def mask_sensitive_data(data: dict[str, Any]) -> dict[str, Any]:
            """Mask sensitive data in logs"""
            sensitive_fields = ['password', 'token', 'secret', 'card_number', 'email']
            masked_data = data.copy()
            
            for key, value in masked_data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    if isinstance(value, str) and len(value) > 4:
                        # Show first 2 and last 2 characters
                        masked_data[key] = f"{value[:2]}***{value[-2:]}"
                    else:
                        masked_data[key] = "***"
                        
            return masked_data
        
        test_data = {
            "user_id": 123456789,
            "username": "testuser",
            "email": "user@example.com",
            "password": "secretpassword123",
            "api_token": "sk_live_abcdef123456789",
            "card_number": "4111111111111111",
            "amount": "25.00",
            "description": "Test payment"
        }
        
        masked = mask_sensitive_data(test_data)
        
        # Sensitive fields should be masked
        assert masked["email"] == "us***om"
        assert masked["password"] == "se***23"
        assert masked["api_token"] == "sk***89"
        assert masked["card_number"] == "41***11"
        
        # Non-sensitive fields should remain
        assert masked["user_id"] == 123456789
        assert masked["username"] == "testuser"
        assert masked["amount"] == "25.00"
    
    def test_user_data_anonymization(self):
        """Test user data anonymization"""
        def anonymize_user(user_data: dict[str, Any]) -> dict[str, Any]:
            """Anonymize user data"""
            anonymized = user_data.copy()
            
            # Replace identifiable fields
            anonymized["username"] = f"user_{hash(user_data['user_id']) % 100000}"
            anonymized["first_name"] = "Anonymous"
            anonymized["last_name"] = "User"
            
            # Remove potentially identifying fields
            fields_to_remove = ["email", "phone", "last_seen", "ip_address"]
            for field in fields_to_remove:
                anonymized.pop(field, None)
                
            return anonymized
        
        user_data = {
            "user_id": 123456789,
            "username": "realusername",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@email.com",
            "phone": "+1234567890",
            "created_at": "2024-01-01T00:00:00Z",
            "last_seen": "2024-01-15T10:30:00Z",
            "plan_type": "premium"
        }
        
        anonymized = anonymize_user(user_data)
        
        # Check anonymization
        assert anonymized["username"].startswith("user_")
        assert anonymized["first_name"] == "Anonymous"
        assert anonymized["last_name"] == "User"
        assert "email" not in anonymized
        assert "phone" not in anonymized
        assert "last_seen" not in anonymized
        
        # Preserve non-identifying data
        assert anonymized["user_id"] == 123456789
        assert anonymized["created_at"] == "2024-01-01T00:00:00Z"
        assert anonymized["plan_type"] == "premium"


@pytest.mark.security
class TestWebhookSecurity:
    """Test webhook security validation"""
    
    def test_webhook_signature_validation(self):
        """Test webhook signature validation"""
        import hmac
        
        def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
            """Validate webhook signature"""
            try:
                # Expected signature format: "sha256=<hex_digest>"
                if not signature.startswith("sha256="):
                    return False
                
                expected_signature = signature[7:]  # Remove "sha256=" prefix
                
                # Compute signature
                computed_signature = hmac.new(
                    secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                # Use constant-time comparison
                return secrets.compare_digest(expected_signature, computed_signature)
                
            except Exception:
                return False
        
        webhook_secret = "webhook_secret_key_123"
        valid_payload = '{"event": "payment.completed", "amount": "25.00"}'
        
        # Generate valid signature
        valid_signature = "sha256=" + hmac.new(
            webhook_secret.encode(),
            valid_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Test valid signature
        assert validate_webhook_signature(valid_payload, valid_signature, webhook_secret) is True
        
        # Test invalid signatures
        assert validate_webhook_signature(valid_payload, "invalid_signature", webhook_secret) is False
        assert validate_webhook_signature(valid_payload, "sha256=wrong_hash", webhook_secret) is False
        assert validate_webhook_signature(valid_payload, valid_signature, "wrong_secret") is False
        
        # Test malformed signatures
        assert validate_webhook_signature(valid_payload, "wrong_format", webhook_secret) is False
        assert validate_webhook_signature(valid_payload, "", webhook_secret) is False
    
    def test_webhook_replay_attack_prevention(self):
        """Test webhook replay attack prevention"""
        from datetime import datetime
        
        class WebhookReplayProtector:
            def __init__(self, max_age_seconds: int = 300):  # 5 minutes
                self.max_age_seconds = max_age_seconds
                self.processed_webhooks = set()
            
            def is_valid_webhook(self, webhook_id: str, timestamp: str) -> bool:
                # Check if already processed
                if webhook_id in self.processed_webhooks:
                    return False
                
                # Check timestamp age
                try:
                    webhook_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    current_time = datetime.now(UTC)
                    age_seconds = (current_time - webhook_time).total_seconds()
                    
                    if age_seconds > self.max_age_seconds:
                        return False  # Too old
                        
                    if age_seconds < 0:
                        return False  # Future timestamp
                        
                except (ValueError, TypeError):
                    return False  # Invalid timestamp format
                
                # Mark as processed
                self.processed_webhooks.add(webhook_id)
                return True
        
        protector = WebhookReplayProtector(max_age_seconds=300)
        current_time = datetime.now(UTC)
        
        # Valid webhook (recent timestamp)
        webhook_id_1 = "webhook_123"
        recent_timestamp = current_time.isoformat().replace('+00:00', 'Z')
        assert protector.is_valid_webhook(webhook_id_1, recent_timestamp) is True
        
        # Replay attack (same webhook ID)
        assert protector.is_valid_webhook(webhook_id_1, recent_timestamp) is False
        
        # Old webhook (should be rejected)
        old_timestamp = (current_time - timedelta(minutes=10)).isoformat().replace('+00:00', 'Z')
        assert protector.is_valid_webhook("webhook_456", old_timestamp) is False
        
        # Future webhook (should be rejected)
        future_timestamp = (current_time + timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')
        assert protector.is_valid_webhook("webhook_789", future_timestamp) is False


@pytest.mark.security
class TestSecurityLogging:
    """Test security event logging"""
    
    def test_security_event_logging(self):
        """Test security event logging functionality"""
        security_events = []
        
        class SecurityLogger:
            @staticmethod
            def log_security_event(event_type: str, user_id: int, details: dict[str, Any]):
                event = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "event_type": event_type,
                    "user_id": user_id,
                    "details": details,
                    "severity": "WARNING" if "failed" in event_type else "INFO"
                }
                security_events.append(event)
        
        # Test various security events
        SecurityLogger.log_security_event(
            "login_failed", 
            123456789, 
            {"ip": "192.168.1.1", "reason": "invalid_password"}
        )
        
        SecurityLogger.log_security_event(
            "payment_failed",
            123456789,
            {"amount": "25.00", "reason": "insufficient_funds", "provider": "stripe"}
        )
        
        SecurityLogger.log_security_event(
            "webhook_validation_failed",
            0,  # System event
            {"endpoint": "/webhook/payment", "reason": "invalid_signature"}
        )
        
        # Verify events were logged correctly
        assert len(security_events) == 3
        
        # Check failed login event
        login_event = security_events[0]
        assert login_event["event_type"] == "login_failed"
        assert login_event["user_id"] == 123456789
        assert login_event["severity"] == "WARNING"
        assert "ip" in login_event["details"]
        
        # Check payment failure event
        payment_event = security_events[1]
        assert payment_event["event_type"] == "payment_failed"
        assert payment_event["severity"] == "WARNING"
        assert payment_event["details"]["amount"] == "25.00"
        
        # All events should have timestamps
        for event in security_events:
            assert "timestamp" in event
            assert isinstance(event["timestamp"], str)


@pytest.mark.security
def test_security_configuration_validation():
    """Test security configuration validation"""
    def validate_security_config(config: dict[str, Any]) -> list[str]:
        """Validate security configuration"""
        issues = []
        
        # Check required security settings
        required_settings = [
            "session_timeout",
            "max_login_attempts", 
            "webhook_secret",
            "rate_limit_enabled"
        ]
        
        for setting in required_settings:
            if setting not in config:
                issues.append(f"Missing required setting: {setting}")
        
        # Check specific values
        if config.get("session_timeout", 0) < 300:  # 5 minutes minimum
            issues.append("Session timeout too short (minimum 5 minutes)")
            
        if config.get("max_login_attempts", 0) < 1:
            issues.append("Max login attempts must be at least 1")
            
        if config.get("webhook_secret", "") == "":
            issues.append("Webhook secret must not be empty")
            
        if config.get("rate_limit_enabled") is not True:
            issues.append("Rate limiting should be enabled")
        
        return issues
    
    # Test valid configuration
    valid_config = {
        "session_timeout": 1800,  # 30 minutes
        "max_login_attempts": 5,
        "webhook_secret": "secure_webhook_secret_123",
        "rate_limit_enabled": True,
        "debug_mode": False
    }
    
    issues = validate_security_config(valid_config)
    assert len(issues) == 0
    
    # Test invalid configuration
    invalid_config = {
        "session_timeout": 60,  # Too short
        "max_login_attempts": 0,  # Too low
        "webhook_secret": "",  # Empty
        "rate_limit_enabled": False  # Should be enabled
    }
    
    issues = validate_security_config(invalid_config)
    assert len(issues) == 4  # Should have 4 issues
    assert any("timeout too short" in issue for issue in issues)
    assert any("login attempts must be" in issue for issue in issues)
    assert any("secret must not be empty" in issue for issue in issues)
    assert any("Rate limiting should be enabled" in issue for issue in issues)
