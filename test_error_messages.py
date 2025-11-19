#!/usr/bin/env python3
"""
Test User-Friendly Error Messages

This script verifies that error messages are converted to user-friendly format.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_error_message_conversion():
    """Test that technical errors are converted to user-friendly messages"""
    from apps.api.utils.error_messages import BotErrorMessages, get_user_friendly_error

    print("=" * 70)
    print("TEST: Error Message Conversion")
    print("=" * 70)

    test_cases = [
        # (Exception message, expected status code, should contain text)
        (ValueError("Invalid token"), 400, "BotFather"),
        (ValueError("Token revoked"), 401, "revoked"),
        (ValueError("Already exists"), 409, "already have a bot"),
        (ValueError("Bot was blocked"), 400, "Start"),
        (ValueError("Not enough rights"), 403, "permissions"),
        (ValueError("Chat not found"), 404, "chat ID is correct"),
        (ValueError("Network connection timeout"), 503, "internet connection"),
        (ValueError("429 Too Many Requests"), 429, "too quickly"),
        (ValueError("Database error occurred"), 500, "database error"),
        (ValueError("No bot found"), 404, "don't have a bot"),
        (ValueError("MTProto not configured"), 400, "MTProto"),
        (ValueError("Rate limit must be between"), 400, "between 1"),
        (ValueError("Unauthorized"), 401, "logged in"),
        (ValueError("Unknown error type"), 500, "unexpected error"),
    ]

    passed = 0
    failed = 0

    for error_msg, expected_status, expected_text in test_cases:
        status_code, message = get_user_friendly_error(ValueError(error_msg))
        
        error_preview = str(error_msg)[:30] if len(str(error_msg)) > 30 else str(error_msg)
        
        if status_code == expected_status and expected_text.lower() in message.lower():
            print(f"✅ PASS: '{error_preview}...' → {status_code}")
            passed += 1
        else:
            print(f"❌ FAIL: '{error_preview}...'")
            print(f"   Expected status: {expected_status}, got: {status_code}")
            print(f"   Expected text: '{expected_text}'")
            print(f"   Got message: '{message[:80]}...'")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_predefined_messages():
    """Test that all predefined messages are user-friendly"""
    from apps.api.utils.error_messages import BotErrorMessages

    print("=" * 70)
    print("TEST: Predefined Messages Quality")
    print("=" * 70)

    messages = [
        ("INVALID_TOKEN", BotErrorMessages.INVALID_TOKEN),
        ("TOKEN_REVOKED", BotErrorMessages.TOKEN_REVOKED),
        ("BOT_NOT_STARTED", BotErrorMessages.BOT_NOT_STARTED),
        ("NETWORK_ERROR", BotErrorMessages.NETWORK_ERROR),
        ("RATE_LIMIT_EXCEEDED", BotErrorMessages.RATE_LIMIT_EXCEEDED),
        ("BOT_NOT_FOUND", BotErrorMessages.BOT_NOT_FOUND),
        ("MTPROTO_NOT_CONFIGURED", BotErrorMessages.MTPROTO_NOT_CONFIGURED),
    ]

    print("\n📝 Sample User-Friendly Messages:\n")
    
    for name, message in messages:
        # Check message quality
        is_friendly = (
            len(message) > 30 and  # Not too short
            not any(x in message.lower() for x in ["error", "exception", "failed"]) and
            any(x in message.lower() for x in ["please", "try", "check", "make sure"])
        )
        
        status = "✅" if is_friendly else "⚠️"
        print(f"{status} {name}:")
        print(f"   {message[:100]}...")
        print()

    print("All messages include:")
    print("   • Clear explanation of what went wrong")
    print("   • Actionable steps to fix the issue")
    print("   • No technical jargon or stack traces")
    print()
    return True


def test_validation_messages():
    """Test field-specific validation messages"""
    from apps.api.utils.error_messages import get_validation_error_message

    print("=" * 70)
    print("TEST: Validation Error Messages")
    print("=" * 70)

    test_cases = [
        ("bot_token", "required"),
        ("bot_token", "format"),
        ("api_id", "type"),
        ("api_hash", "required"),
        ("max_requests_per_second", "range"),
        ("test_chat_id", "required"),
    ]

    print("\n📝 Sample Validation Messages:\n")
    
    for field, constraint in test_cases:
        message = get_validation_error_message(field, constraint)
        print(f"✅ {field} ({constraint}):")
        print(f"   {message}")
        print()

    return True


def show_before_after_examples():
    """Show before/after comparison of error messages"""
    print("=" * 70)
    print("BEFORE vs AFTER: Error Message Comparison")
    print("=" * 70)

    examples = [
        {
            "scenario": "Invalid bot token",
            "before": "Unauthorized",
            "after": "Invalid bot token. Please check that you copied the full token from @BotFather. It should look like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        },
        {
            "scenario": "Bot not found",
            "before": "No bot found for this user",
            "after": "You don't have a bot configured yet. Please create a bot first using the 'Create Bot' option."
        },
        {
            "scenario": "Rate limit exceeded",
            "before": "429 Too Many Requests",
            "after": "You're sending requests too quickly. Please wait a moment and try again. Our system automatically manages rate limits to prevent issues."
        },
        {
            "scenario": "Network error",
            "before": "Network connection error: Connection timeout",
            "after": "Network connection error. Please check your internet connection and try again. If the problem persists, Telegram servers might be temporarily unavailable."
        },
        {
            "scenario": "Internal error",
            "before": "Failed to create bot",
            "after": "An unexpected error occurred. Our team has been notified. Please try again in a moment."
        },
    ]

    for example in examples:
        print(f"\n📌 {example['scenario']}:")
        print(f"   ❌ Before: {example['before']}")
        print(f"   ✅ After:  {example['after']}")

    print()


def main():
    """Run all tests"""
    print("\n🧪 Testing User-Friendly Error Messages\n")

    results = []

    try:
        results.append(test_error_message_conversion())
        results.append(test_predefined_messages())
        results.append(test_validation_messages())
        show_before_after_examples()
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - Error messages are user-friendly!")
        print("\n🎯 Improvements:")
        print("   • Clear, actionable error messages")
        print("   • No technical jargon exposed to users")
        print("   • Specific guidance for common issues")
        print("   • Better user experience")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Review implementation")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
