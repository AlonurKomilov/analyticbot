"""
Basic Security Tests - No External Dependencies
Tests core security functionality without database or external service dependencies
"""
import hashlib
import secrets
import hmac
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List


def test_basic_input_sanitization():
    """Test basic input sanitization"""
    def sanitize_username(username: str) -> str:
        """Simple username sanitization"""
        if not username or len(username) > 50:
            return ""
            
        # Remove dangerous characters
        dangerous_chars = ["<", ">", "'", '"', ";", "--", "/", "\\", "\x00"]
        for char in dangerous_chars:
            username = username.replace(char, "")
            
        return username.strip()
    
    # Test dangerous inputs
    assert sanitize_username("<script>alert('xss')</script>") == "scriptalert(xss)script"  # Single quotes removed
    assert sanitize_username("'; DROP TABLE users; --") == "DROP TABLE users"  # Dangerous chars removed and trimmed
    assert sanitize_username("validuser123") == "validuser123"
    assert sanitize_username("a" * 100) == ""  # Too long
    assert sanitize_username("") == ""  # Empty


def test_basic_password_hashing():
    """Test password hashing security"""
    def hash_password(password: str) -> str:
        """Secure password hashing with salt"""
        salt = secrets.token_hex(16)
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
    
    password = "test_password_123"
    password_hash = hash_password(password)
    
    # Should verify correctly
    assert verify_password(password, password_hash) is True
    
    # Should reject wrong password
    assert verify_password("wrong_password", password_hash) is False
    
    # Hash should contain salt
    assert ":" in password_hash
    salt, hash_part = password_hash.split(":", 1)
    assert len(salt) == 32  # 16 bytes hex
    assert len(hash_part) == 64  # SHA-256 hex


def test_basic_session_token_generation():
    """Test secure session token generation"""
    def generate_session_token() -> str:
        return secrets.token_urlsafe(32)
    
    tokens = [generate_session_token() for _ in range(10)]
    
    # All tokens should be unique
    assert len(set(tokens)) == 10
    
    # Proper length and character set
    for token in tokens:
        assert len(token) >= 40
        assert len(token) <= 45
        allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")
        assert set(token).issubset(allowed_chars)


def test_basic_rate_limiting():
    """Test basic rate limiting logic"""
    from collections import defaultdict
    import time
    
    class SimpleRateLimiter:
        def __init__(self, max_requests: int = 5, window_seconds: int = 60):
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
            
            # Check limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False
            
            self.requests[user_id].append(now)
            return True
    
    limiter = SimpleRateLimiter(max_requests=3, window_seconds=10)
    
    # First 3 requests allowed
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    assert limiter.is_allowed("user1") is True
    
    # 4th request blocked
    assert limiter.is_allowed("user1") is False
    
    # Different user still allowed
    assert limiter.is_allowed("user2") is True


def test_webhook_signature_validation():
    """Test webhook signature validation"""
    def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
        try:
            if not signature.startswith("sha256="):
                return False
            
            expected_signature = signature[7:]
            computed_signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return secrets.compare_digest(expected_signature, computed_signature)
        except Exception:
            return False
    
    webhook_secret = "webhook_secret_123"
    payload = '{"event": "payment.completed", "amount": "25.00"}'
    
    # Generate valid signature
    valid_signature = "sha256=" + hmac.new(
        webhook_secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Test valid signature
    assert validate_webhook_signature(payload, valid_signature, webhook_secret) is True
    
    # Test invalid signatures
    assert validate_webhook_signature(payload, "sha256=wrong_hash", webhook_secret) is False
    assert validate_webhook_signature(payload, "invalid_format", webhook_secret) is False
    assert validate_webhook_signature(payload, valid_signature, "wrong_secret") is False


def test_pii_data_masking():
    """Test PII data masking"""
    def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        sensitive_fields = ['password', 'token', 'secret', 'card_number', 'email']
        masked_data = data.copy()
        
        for key, value in masked_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                if isinstance(value, str) and len(value) > 4:
                    masked_data[key] = f"{value[:2]}***{value[-2:]}"
                else:
                    masked_data[key] = "***"
                    
        return masked_data
    
    test_data = {
        "user_id": 123456789,
        "email": "user@example.com",
        "password": "secretpassword123",
        "api_token": "sk_live_abcdef123456789",
        "amount": "25.00",
    }
    
    masked = mask_sensitive_data(test_data)
    
    assert masked["email"] == "us***om"
    assert masked["password"] == "se***23"
    assert masked["api_token"] == "sk***89"
    assert masked["user_id"] == 123456789  # Not sensitive
    assert masked["amount"] == "25.00"  # Not sensitive


def test_payment_amount_validation():
    """Test payment amount validation"""
    def validate_payment_amount(amount) -> bool:
        if not amount:
            return False
            
        try:
            amount_float = float(amount)
            
            if amount_float <= 0:
                return False
                
            if amount_float > 10000:
                return False
                
            # Check decimal places
            amount_str = str(amount)
            if '.' in amount_str:
                decimal_places = len(amount_str.split('.')[1])
                if decimal_places > 2:
                    return False
                    
            return True
        except (ValueError, TypeError):
            return False
    
    # Valid amounts
    assert validate_payment_amount("25.00") is True
    assert validate_payment_amount("0.01") is True
    assert validate_payment_amount("9999.99") is True
    
    # Invalid amounts
    assert validate_payment_amount("-25.00") is False  # Negative
    assert validate_payment_amount("0") is False  # Zero
    assert validate_payment_amount("99999.99") is False  # Too large
    assert validate_payment_amount("25.999") is False  # Too many decimals
    assert validate_payment_amount("abc") is False  # Non-numeric
    assert validate_payment_amount("") is False  # Empty
    assert validate_payment_amount(None) is False  # None


def test_security_configuration_validation():
    """Test security configuration validation"""
    def validate_security_config(config: Dict[str, Any]) -> List[str]:
        issues = []
        
        # Required settings
        required_settings = ["session_timeout", "max_login_attempts", "webhook_secret"]
        
        for setting in required_settings:
            if setting not in config:
                issues.append(f"Missing required setting: {setting}")
        
        # Value validation
        if config.get("session_timeout", 0) < 300:
            issues.append("Session timeout too short")
            
        if config.get("max_login_attempts", 0) < 1:
            issues.append("Max login attempts must be at least 1")
            
        if config.get("webhook_secret", "") == "":
            issues.append("Webhook secret must not be empty")
        
        return issues
    
    # Valid config
    valid_config = {
        "session_timeout": 1800,
        "max_login_attempts": 5,
        "webhook_secret": "secure_secret_123"
    }
    
    assert len(validate_security_config(valid_config)) == 0
    
    # Invalid config
    invalid_config = {
        "session_timeout": 60,  # Too short
        "max_login_attempts": 0,  # Too low  
        "webhook_secret": ""  # Empty
    }
    
    issues = validate_security_config(invalid_config)
    assert len(issues) == 3


if __name__ == "__main__":
    print("Running basic security tests...")
    test_basic_input_sanitization()
    print("✅ Input sanitization test passed")
    
    test_basic_password_hashing()
    print("✅ Password hashing test passed")
    
    test_basic_session_token_generation()
    print("✅ Session token generation test passed")
    
    test_basic_rate_limiting()
    print("✅ Rate limiting test passed")
    
    test_webhook_signature_validation()
    print("✅ Webhook signature validation test passed")
    
    test_pii_data_masking()
    print("✅ PII data masking test passed")
    
    test_payment_amount_validation()
    print("✅ Payment amount validation test passed")
    
    test_security_configuration_validation()
    print("✅ Security configuration validation test passed")
    
    print("🎉 All basic security tests passed!")
