#!/usr/bin/env python3
"""
Test Multi-Provider AI System
===============================

Tests the complete flow:
1. Add user's API key
2. Test connection
3. Run channel analysis with real AI
4. Track usage and cost
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.security.encryption import APIKeyEncryption
from core.services.ai.models import AIMessage, AIProviderConfig
from core.services.ai.provider_registry import AIProviderRegistry


async def test_provider(provider_name: str, api_key: str, model: str):
    """Test a specific provider."""
    print(f"\n{'=' * 60}")
    print(f"Testing {provider_name.upper()} Provider")
    print(f"{'=' * 60}")

    # Get provider class
    provider_class = AIProviderRegistry.get_provider_class(provider_name)

    # Create provider instance
    config = AIProviderConfig(
        api_key=api_key,
        model=model,
        temperature=0.7,
        max_tokens=500,
    )

    provider = provider_class(config)

    print("\n1. Provider Info:")
    info = provider.provider_info
    print(f"   Name: {info.display_name}")
    print(f"   Available Models: {', '.join(info.available_models[:3])}...")
    print(f"   Default Model: {info.default_model}")

    # Test connection
    print("\n2. Testing API Key...")
    is_valid = await provider.test_connection()

    if not is_valid:
        print("   ❌ API key is invalid!")
        return False

    print("   ✅ API key is valid!")

    # Test channel analysis
    print("\n3. Running Channel Analysis...")

    messages = [
        AIMessage(
            role="system",
            content="You are a Telegram channel analyst. Provide brief insights.",
        ),
        AIMessage(
            role="user",
            content=(
                "Analyze this channel:\n"
                "Name: Tech News\n"
                "Subscribers: 50,000\n"
                "Avg Views: 2,500\n"
                "Engagement: 5%\n\n"
                "Give 3 key insights."
            ),
        ),
    ]

    response = await provider.complete(messages, max_tokens=300)

    print("\n4. Results:")
    print(f"   Model: {response.model}")
    print(f"   Tokens Used: {response.tokens_used}")
    print(f"   Input Tokens: {response.input_tokens}")
    print(f"   Output Tokens: {response.output_tokens}")
    print(f"   Cost: ${response.cost_usd:.6f}")
    print(f"   Finish Reason: {response.finish_reason}")

    print("\n5. AI Response:")
    print(f"   {'-' * 56}")
    print(f"   {response.content[:200]}...")
    print(f"   {'-' * 56}")

    return True


async def test_encryption():
    """Test API key encryption."""
    print(f"\n{'=' * 60}")
    print("Testing API Key Encryption")
    print(f"{'=' * 60}")

    encryption = APIKeyEncryption()

    # Test data
    original_key = "sk-test-1234567890abcdefghijklmnopqrstuvwxyz"

    print(f"\n1. Original Key: {original_key[:20]}...")

    # Encrypt
    encrypted = encryption.encrypt(original_key)
    print(f"2. Encrypted: {encrypted[:30]}...")

    # Decrypt
    decrypted = encryption.decrypt(encrypted)
    print(f"3. Decrypted: {decrypted[:20]}...")

    # Verify
    if decrypted == original_key:
        print("✅ Encryption/Decryption works correctly!")
        return True
    else:
        print("❌ Encryption/Decryption failed!")
        return False


async def test_registry():
    """Test provider registry."""
    print(f"\n{'=' * 60}")
    print("Testing Provider Registry")
    print(f"{'=' * 60}")

    providers = AIProviderRegistry.list_providers()

    print(f"\nRegistered Providers: {len(providers)}")
    for p in providers:
        print(f"\n  • {p['display_name']} ({p['name']})")
        print(f"    Default Model: {p['default_model']}")
        print(f"    Models: {len(p['available_models'])} available")

    return True


async def main():
    """Run all tests."""
    print(f"\n{'#' * 60}")
    print("# Multi-Provider AI System Test Suite")
    print(f"{'#' * 60}")

    # Test 1: Encryption
    await test_encryption()

    # Test 2: Registry
    await test_registry()

    # Test 3: Provider (requires real API key)
    print(f"\n\n{'=' * 60}")
    print("Provider Tests (requires API keys)")
    print(f"{'=' * 60}")

    # Check for API keys in environment
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        await test_provider("openai", openai_key, "gpt-4o-mini")
    else:
        print("\n⚠️  Skipping OpenAI test (no API key in OPENAI_API_KEY)")

    if claude_key:
        await test_provider("claude", claude_key, "claude-3-5-sonnet-20241022")
    else:
        print("\n⚠️  Skipping Claude test (no API key in ANTHROPIC_API_KEY)")

    print(f"\n\n{'#' * 60}")
    print("# All Tests Complete!")
    print(f"{'#' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
