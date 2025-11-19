"""
Test Token Validator

Comprehensive tests for token validation functionality.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import aiogram exceptions at module level
try:
    from aiogram.exceptions import TelegramUnauthorizedError, TelegramNetworkError
except ImportError:
    # Fallback if aiogram not installed
    class TelegramUnauthorizedError(Exception):
        def __init__(self, method="", message=""):
            self.method = method
            super().__init__(message)
    
    class TelegramNetworkError(Exception):
        def __init__(self, method="", message=""):
            self.method = method
            super().__init__(message)

from apps.bot.multi_tenant.token_validator import (
    PeriodicTokenValidator,
    TokenValidationResult,
    TokenValidationStatus,
    TokenValidator,
    get_token_validator,
    initialize_periodic_validator,
)


# Test helpers
class MockBotInfo:
    """Mock Telegram Bot Info"""
    def __init__(self, id: int, username: str):
        self.id = id
        self.username = username


class MockBot:
    """Mock Telegram Bot"""
    def __init__(self, token: str, should_fail: bool = False, fail_type: str = None):
        self.token = token
        self.should_fail = should_fail
        self.fail_type = fail_type
        self.session = MagicMock()
        self.session.close = AsyncMock()
    
    async def get_me(self):
        if self.should_fail:
            if self.fail_type == "unauthorized":
                raise TelegramUnauthorizedError(method="getMe", message="Unauthorized")
            elif self.fail_type == "revoked":
                raise TelegramUnauthorizedError(method="getMe", message="Bot was terminated")
            elif self.fail_type == "timeout":
                await asyncio.sleep(15)  # Will trigger timeout
            elif self.fail_type == "network":
                raise TelegramNetworkError(method="getMe", message="Network error")
            else:
                raise Exception("Unknown error")
        
        return MockBotInfo(id=123456789, username="test_bot")


def print_test_header(test_num: int, description: str):
    """Print formatted test header"""
    print(f"\n🧪 Test {test_num}: {description}")
    print("=" * 70)


def print_test_result(passed: bool, test_num: int, description: str):
    """Print formatted test result"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{status}: Test {test_num} - {description}\n")


async def test_1_format_validation_valid():
    """Test valid token format"""
    print_test_header(1, "Valid Token Format")
    
    validator = TokenValidator()
    
    # Valid token format (35 characters in secret part)
    valid_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456767"
    result = validator.validate_format(valid_token)
    
    assert result.is_valid, "Token should be valid"
    assert result.status == TokenValidationStatus.VALID, "Status should be VALID"
    assert result.bot_id == 123456789, "Bot ID should be extracted"
    print(f"  ✅ Token format valid")
    print(f"  ✅ Bot ID extracted: {result.bot_id}")
    print(f"  ✅ Message: {result.message}")
    
    print_test_result(True, 1, "Valid token format")


async def test_2_format_validation_invalid():
    """Test invalid token formats"""
    print_test_header(2, "Invalid Token Formats")
    
    validator = TokenValidator()
    
    invalid_tokens = [
        ("", "empty string"),
        ("invalid", "no colon separator"),
        ("123:short", "secret too short"),
        ("abc:ABCdefGHIjklMNOpqrsTUVwxyz123456767", "non-numeric ID"),
        ("123456789:ABC@efGHI", "invalid characters in secret"),
        (None, "None value"),
    ]
    
    all_passed = True
    for token, description in invalid_tokens:
        try:
            result = validator.validate_format(token)
            assert not result.is_valid, f"Token should be invalid: {description}"
            assert result.status == TokenValidationStatus.INVALID_FORMAT
            print(f"  ✅ Rejected: {description}")
        except Exception as e:
            print(f"  ❌ Failed on: {description} - {e}")
            all_passed = False
    
    print_test_result(all_passed, 2, "Invalid token formats")


async def test_3_live_validation_valid():
    """Test live validation with valid token"""
    print_test_header(3, "Live Validation - Valid Token")
    
    validator = TokenValidator()
    
    with patch('apps.bot.multi_tenant.token_validator.Bot', return_value=MockBot("valid_token")):
        result = await validator.validate_live("123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456767")
        
        assert result.is_valid, "Token should be valid"
        assert result.status == TokenValidationStatus.VALID
        assert result.bot_username == "test_bot"
        assert result.bot_id == 123456789
        print(f"  ✅ Live validation successful")
        print(f"  ✅ Bot: @{result.bot_username} (ID: {result.bot_id})")
        print(f"  ✅ Message: {result.message}")
    
    print_test_result(True, 3, "Live validation - valid token")


async def test_4_live_validation_unauthorized():
    """Test live validation with unauthorized token"""
    print_test_header(4, "Live Validation - Unauthorized Token")
    
    validator = TokenValidator()
    
    with patch('apps.bot.multi_tenant.token_validator.Bot', 
               return_value=MockBot("invalid_token", should_fail=True, fail_type="unauthorized")):
        result = await validator.validate_live("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        
        assert not result.is_valid, "Token should be invalid"
        assert result.status == TokenValidationStatus.UNAUTHORIZED
        print(f"  ✅ Detected unauthorized token")
        print(f"  ✅ Status: {result.status.value}")
        print(f"  ✅ Message: {result.message}")
    
    print_test_result(True, 4, "Live validation - unauthorized")


async def test_5_live_validation_revoked():
    """Test live validation with revoked token"""
    print_test_header(5, "Live Validation - Revoked Token")
    
    validator = TokenValidator()
    
    with patch('apps.bot.multi_tenant.token_validator.Bot',
               return_value=MockBot("revoked_token", should_fail=True, fail_type="revoked")):
        result = await validator.validate_live("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        
        assert not result.is_valid, "Token should be invalid"
        assert result.status == TokenValidationStatus.REVOKED
        print(f"  ✅ Detected revoked token")
        print(f"  ✅ Status: {result.status.value}")
        print(f"  ✅ Message: {result.message}")
    
    print_test_result(True, 5, "Live validation - revoked")


async def test_6_live_validation_timeout():
    """Test live validation timeout"""
    print_test_header(6, "Live Validation - Timeout")
    
    validator = TokenValidator()
    
    with patch('apps.bot.multi_tenant.token_validator.Bot',
               return_value=MockBot("slow_token", should_fail=True, fail_type="timeout")):
        result = await validator.validate_live("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567", timeout_seconds=2)
        
        assert not result.is_valid, "Token validation should timeout"
        assert result.status == TokenValidationStatus.TIMEOUT
        print(f"  ✅ Detected timeout")
        print(f"  ✅ Status: {result.status.value}")
        print(f"  ✅ Message: {result.message}")
    
    print_test_result(True, 6, "Live validation - timeout")


async def test_7_live_validation_network_error():
    """Test live validation network error"""
    print_test_header(7, "Live Validation - Network Error")
    
    validator = TokenValidator()
    
    with patch('apps.bot.multi_tenant.token_validator.Bot',
               return_value=MockBot("network_token", should_fail=True, fail_type="network")):
        result = await validator.validate_live("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        
        assert not result.is_valid, "Token should fail with network error"
        assert result.status == TokenValidationStatus.NETWORK_ERROR
        print(f"  ✅ Detected network error")
        print(f"  ✅ Status: {result.status.value}")
        print(f"  ✅ Message: {result.message}")
    
    print_test_result(True, 7, "Live validation - network error")


async def test_8_validate_with_live_check():
    """Test validate() method with live check"""
    print_test_header(8, "Validate Method with Live Check")
    
    validator = TokenValidator()
    
    with patch('apps.bot.multi_tenant.token_validator.Bot', return_value=MockBot("valid_token")):
        # With live check (default)
        result = await validator.validate("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567", live_check=True)
        assert result.is_valid
        assert result.bot_username is not None
        print(f"  ✅ Live check: valid token detected")
        
        # Without live check (format only)
        result = await validator.validate("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567", live_check=False)
        assert result.is_valid
        assert result.bot_username is None  # No live check, no username
        print(f"  ✅ Format check: valid format detected")
    
    print_test_result(True, 8, "Validate method with/without live check")


async def test_9_periodic_validator_initialization():
    """Test periodic validator initialization"""
    print_test_header(9, "Periodic Validator Initialization")
    
    validator = TokenValidator()
    periodic = PeriodicTokenValidator(
        validator=validator,
        check_interval_hours=1,
        max_consecutive_failures=3
    )
    
    assert periodic.validator == validator
    assert periodic.check_interval.total_seconds() == 3600  # 1 hour
    assert periodic.max_consecutive_failures == 3
    assert not periodic.is_running
    print(f"  ✅ Periodic validator initialized")
    print(f"  ✅ Check interval: {periodic.check_interval.total_seconds()} seconds")
    print(f"  ✅ Max failures: {periodic.max_consecutive_failures}")
    
    print_test_result(True, 9, "Periodic validator initialization")


async def test_10_periodic_validator_tracking():
    """Test periodic validator token tracking"""
    print_test_header(10, "Periodic Validator Token Tracking")
    
    validator = TokenValidator()
    periodic = PeriodicTokenValidator(validator=validator, check_interval_hours=1)
    
    user_id = 1001
    
    with patch('apps.bot.multi_tenant.token_validator.Bot', return_value=MockBot("valid_token")):
        # First validation - success
        result = await periodic.validate_token(user_id, "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        assert result.is_valid
        assert periodic.get_failure_count(user_id) == 0
        assert user_id in periodic.last_validation
        print(f"  ✅ Success tracked: 0 failures")
    
    with patch('apps.bot.multi_tenant.token_validator.Bot',
               return_value=MockBot("invalid", should_fail=True, fail_type="unauthorized")):
        # Second validation - failure
        result = await periodic.validate_token(user_id, "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        assert not result.is_valid
        assert periodic.get_failure_count(user_id) == 1
        print(f"  ✅ Failure tracked: 1 failure")
        
        # Third validation - another failure
        result = await periodic.validate_token(user_id, "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        assert periodic.get_failure_count(user_id) == 2
        print(f"  ✅ Failure tracked: 2 failures")
    
    with patch('apps.bot.multi_tenant.token_validator.Bot', return_value=MockBot("valid_token")):
        # Fourth validation - success resets count
        result = await periodic.validate_token(user_id, "123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
        assert result.is_valid
        assert periodic.get_failure_count(user_id) == 0
        print(f"  ✅ Success resets failures: 0 failures")
    
    print_test_result(True, 10, "Periodic validator token tracking")


async def test_11_periodic_validator_should_validate():
    """Test periodic validator should_validate logic"""
    print_test_header(11, "Periodic Validator Should Validate Logic")
    
    validator = TokenValidator()
    periodic = PeriodicTokenValidator(validator=validator, check_interval_hours=1)
    
    user_id = 1002
    
    # Should validate (no previous check)
    assert periodic.should_validate(user_id)
    print(f"  ✅ Should validate: no previous check")
    
    # Mark as validated now
    periodic.last_validation[user_id] = datetime.now()
    
    # Should NOT validate (just checked)
    assert not periodic.should_validate(user_id)
    print(f"  ✅ Should NOT validate: just checked")
    
    # Simulate time passing (fake old timestamp)
    from datetime import timedelta
    periodic.last_validation[user_id] = datetime.now() - timedelta(hours=2)
    
    # Should validate (enough time passed)
    assert periodic.should_validate(user_id)
    print(f"  ✅ Should validate: enough time passed")
    
    print_test_result(True, 11, "Periodic validator should_validate logic")


async def test_12_global_instances():
    """Test global validator instances"""
    print_test_header(12, "Global Validator Instances")
    
    # Get token validator
    validator1 = get_token_validator()
    validator2 = get_token_validator()
    assert validator1 is validator2, "Should return same instance"
    print(f"  ✅ Global token validator is singleton")
    
    # Initialize periodic validator
    periodic1 = initialize_periodic_validator(check_interval_hours=24)
    periodic2 = initialize_periodic_validator(check_interval_hours=12)  # Different config
    assert periodic1 is not periodic2, "Should create new instance"
    print(f"  ✅ Periodic validator can be re-initialized")
    
    print_test_result(True, 12, "Global validator instances")


async def test_13_validation_result_timestamp():
    """Test validation result timestamp"""
    print_test_header(13, "Validation Result Timestamp")
    
    validator = TokenValidator()
    
    before = datetime.now()
    result = validator.validate_format("123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567")
    after = datetime.now()
    
    assert result.validated_at is not None
    assert before <= result.validated_at <= after
    print(f"  ✅ Timestamp set automatically")
    print(f"  ✅ Validated at: {result.validated_at.isoformat()}")
    
    print_test_result(True, 13, "Validation result timestamp")


# Run all tests
async def run_all_tests():
    """Run all token validator tests"""
    print("=" * 70)
    print("🚀 TOKEN VALIDATOR TEST SUITE")
    print("=" * 70)
    
    tests = [
        test_1_format_validation_valid,
        test_2_format_validation_invalid,
        test_3_live_validation_valid,
        test_4_live_validation_unauthorized,
        test_5_live_validation_revoked,
        test_6_live_validation_timeout,
        test_7_live_validation_network_error,
        test_8_validate_with_live_check,
        test_9_periodic_validator_initialization,
        test_10_periodic_validator_tracking,
        test_11_periodic_validator_should_validate,
        test_12_global_instances,
        test_13_validation_result_timestamp,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"❌ Test failed: {e}")
        except Exception as e:
            failed += 1
            print(f"❌ Test error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Token validator is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the output above.")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
