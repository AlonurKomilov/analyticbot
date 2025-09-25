#!/usr/bin/env python3
"""
Simple MTProto Data Collection Test

Tests actual data collection without complex scaling components.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_env():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)


async def test_data_collection():
    """Test actual data collection."""
    print("📊 Testing MTProto Data Collection...")

    # Load environment
    load_env()

    # Import after loading env
    from apps.mtproto.collectors.history import HistoryCollector
    from apps.mtproto.config import MTProtoSettings
    from infra.tg.telethon_client import TelethonTGClient

    # Mock repositories for testing
    class MockRepository:
        async def ensure_channel(self, **kwargs):
            print(f"   📺 Would ensure channel: {kwargs.get('username', 'unknown')}")

        async def upsert_post(self, **kwargs):
            print(f"   📝 Would upsert post: {kwargs.get('content', 'N/A')[:50]}...")
            return {"inserted": True}

        async def add_or_update_snapshot(self, **kwargs):
            print("   📈 Would add metrics snapshot")

        async def max_msg_id(self, channel_id):
            return 0

    class MockRepos:
        def __init__(self):
            self.channel_repo = MockRepository()
            self.post_repo = MockRepository()
            self.metrics_repo = MockRepository()

    try:
        # Initialize settings
        settings = MTProtoSettings()

        if not settings.MTPROTO_ENABLED:
            print("❌ MTProto is disabled")
            return False

        print("✅ MTProto enabled")
        print(f"   History: {settings.MTPROTO_HISTORY_ENABLED}")
        print(f"   Updates: {settings.MTPROTO_UPDATES_ENABLED}")
        print(f"   Peers: {len(settings.MTPROTO_PEERS)}")

        # Create client
        tg_client = TelethonTGClient(settings)
        repos = MockRepos()

        # Test connection
        print("\n🔗 Testing Telegram connection...")
        await tg_client.start()

        me = await tg_client.get_me()
        print(f"✅ Connected as: {me.first_name}")

        # Test data collection if we have peers
        if settings.MTPROTO_PEERS:
            print(f"\n📥 Testing data collection from {len(settings.MTPROTO_PEERS)} peers...")

            collector = HistoryCollector(tg_client, repos, settings)

            # Collect just a few messages for testing
            result = await collector.backfill_history_for_peers(
                peers=settings.MTPROTO_PEERS[:1],  # Just first peer
                limit_per_peer=5,  # Just 5 messages
            )

            print(f"✅ Collection test completed: {result}")
        else:
            print("⚠️  No peers configured for testing")
            print("   Add channels to MTPROTO_PEERS in .env to test collection")

        await tg_client.stop()

        print("\n🎉 Data collection test successful!")
        return True

    except Exception as e:
        print(f"❌ Data collection test failed: {e}")
        return False


def show_usage():
    """Show usage instructions."""
    print("\n📋 To enable real data collection:")
    print("1. Add channels to monitor in .env:")
    print('   MTPROTO_PEERS=["@channel1","@channel2"]')
    print("\n2. Run this test again to verify collection")
    print("\n3. Start continuous collection:")
    print("   python scripts/collect_data.py")


async def main():
    """Main function."""
    print("🧪 MTProto Data Collection Test")
    print("=" * 40)

    success = await test_data_collection()

    if success:
        print("\n✅ Ready for real data collection!")
    else:
        print("\n❌ Fix issues before proceeding")

    show_usage()

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
