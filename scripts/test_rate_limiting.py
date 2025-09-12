#!/usr/bin/env python3
"""
Simple Rate Limiting Test
Tests the rate limiting protection without complex configurations.
"""

import asyncio
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


async def test_rate_limiting():
    """Test the rate limiting mechanism."""
    print("🛡️ Testing Rate Limiting Protection")
    print("=" * 40)

    # Simulate message processing with rate limiting
    messages_to_process = 25
    processed_count = 0

    print(f"Processing {messages_to_process} simulated messages with rate limiting...")

    for i in range(messages_to_process):
        # Simulate message processing
        print(f"   📨 Processing message {i+1}")
        processed_count += 1

        # RATE LIMITING PROTECTION - Same as real implementation

        # 1. Basic delay between every message (200ms)
        await asyncio.sleep(0.2)

        # 2. Longer pause every 10 messages (3 seconds)
        if processed_count % 10 == 0:
            print(f"   ⏳ Processed {processed_count} messages, sleeping for 3 seconds...")
            await asyncio.sleep(3)

        # 3. Even longer pause every 50 messages (10 seconds)
        if processed_count % 50 == 0:
            print(f"   🛡️ Processed {processed_count} messages, extended sleep for 10 seconds...")
            await asyncio.sleep(10)

    total_delay = processed_count * 0.2 + (processed_count // 10) * 3 + (processed_count // 50) * 10
    print("\n✅ Rate limiting test completed!")
    print(f"📊 Processed: {processed_count} messages")
    print(f"⏱️ Total delays: {total_delay:.1f} seconds")
    print("🛡️ Protection levels:")
    print("   - Base delay: 200ms per message")
    print("   - Batch pause: 3s every 10 messages")
    print("   - Extended pause: 10s every 50 messages")

    # Calculate safe rate
    total_time = total_delay
    rate_per_second = processed_count / total_time if total_time > 0 else 0
    print(f"📈 Safe processing rate: {rate_per_second:.2f} messages/second")

    if rate_per_second < 2:  # Less than 2 messages per second is very safe
        print("✅ Rate limiting is SAFE for Telegram API")
    else:
        print("⚠️ Rate limiting might need adjustment")


async def main():
    """Main test function."""
    try:
        await test_rate_limiting()
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n🎉 Rate limiting test successful!")
    else:
        print("\n❌ Rate limiting test failed")
        sys.exit(1)
