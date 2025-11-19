"""
Test Token Validator with Real Bot Token

Instructions to get a real bot token:
1. Open Telegram and search for @BotFather
2. Send /newbot command
3. Follow instructions to create a new bot
4. Copy the token provided by BotFather
5. Set it as environment variable: export TEST_BOT_TOKEN="your_token_here"
6. Run this script

This script tests the token validator with a real Telegram bot token.
"""

import asyncio
import os
import sys

from apps.bot.multi_tenant.token_validator import TokenValidator


async def test_real_token():
    """Test with real bot token from environment"""
    
    # Get token from environment
    token = os.getenv("TEST_BOT_TOKEN")
    
    if not token:
        print("❌ Error: TEST_BOT_TOKEN environment variable not set")
        print("")
        print("To get a bot token:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot")
        print("3. Follow instructions to create a test bot")
        print("4. Copy the token")
        print("5. Run: export TEST_BOT_TOKEN='your_token_here'")
        print("6. Run this script again")
        sys.exit(1)
    
    print("=" * 60)
    print("🧪 Testing Token Validator with Real Token")
    print("=" * 60)
    print("")
    
    validator = TokenValidator()
    
    # Test 1: Format validation
    print("Test 1: Format Validation")
    print("-" * 60)
    is_valid_format = validator.validate_format(token)
    print(f"Token format valid: {is_valid_format}")
    
    if not is_valid_format:
        print("❌ Token format is invalid!")
        print(f"Token: {token[:20]}...")
        sys.exit(1)
    else:
        print("✅ Token format is valid")
    print("")
    
    # Test 2: Live validation
    print("Test 2: Live Validation (connecting to Telegram)")
    print("-" * 60)
    result = await validator.validate_live(token)
    
    print(f"Status: {result.status.value}")
    print(f"Valid: {result.is_valid}")
    print(f"Message: {result.message}")
    
    if result.bot_id:
        print(f"Bot ID: {result.bot_id}")
    if result.bot_username:
        print(f"Bot Username: @{result.bot_username}")
    
    print(f"Validated at: {result.validated_at}")
    print("")
    
    if result.is_valid:
        print("✅ Token is VALID and connected successfully!")
        print("")
        print("Token Details:")
        print(f"  - Bot ID: {result.bot_id}")
        print(f"  - Username: @{result.bot_username}")
        print("")
        return True
    else:
        print(f"❌ Token validation FAILED: {result.message}")
        print("")
        return False
    
    print("=" * 60)


async def test_invalid_token():
    """Test with obviously invalid token"""
    
    print("Test 3: Invalid Token Test")
    print("-" * 60)
    
    validator = TokenValidator()
    
    # Test invalid format
    invalid_tokens = [
        "invalid_token",
        "123:short",
        "not_a_token",
        "123456789:SHORT",
    ]
    
    for token in invalid_tokens:
        result = validator.validate_format(token)
        status = "❌ Invalid (expected)" if not result.is_valid else "⚠️ Valid (unexpected)"
        print(f"Token '{token[:20]}...': {status}")
    
    print("")
    
    # Test invalid token with live validation
    print("Testing invalid token with live validation...")
    fake_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz12345"
    result = await validator.validate_live(fake_token)
    
    print(f"Status: {result.status.value}")
    print(f"Valid: {result.is_valid}")
    print(f"Message: {result.message}")
    print("")
    
    if not result.is_valid:
        print("✅ Invalid token correctly detected")
    else:
        print("⚠️ Invalid token was not detected")
    
    print("")


if __name__ == "__main__":
    async def main():
        # Test with real token
        real_token_valid = await test_real_token()
        
        print("")
        
        # Test with invalid tokens
        await test_invalid_token()
        
        print("=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        if real_token_valid:
            print("✅ Real token validation: PASSED")
            print("✅ Invalid token detection: PASSED")
            print("")
            print("🎉 All tests PASSED!")
        else:
            print("❌ Real token validation: FAILED")
            print("Please check your token and try again")
        print("=" * 60)
    
    asyncio.run(main())
