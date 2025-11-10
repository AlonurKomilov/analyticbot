#!/usr/bin/env python3
"""
Quick data collection for ABC LEGACY NEWS channel
Run this to populate analytics data
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def collect_channel_data():
    """Collect data for ABC LEGACY NEWS channel"""

    print("\n" + "=" * 60)
    print("📊 ABC LEGACY NEWS - Data Collection")
    print("=" * 60 + "\n")

    try:
        # Import after path setup
        from apps.di import get_container
        from apps.mtproto.services.data_collection_service import (
            MTProtoDataCollectionService,
        )

        # Get user ID from your session (you'll need to replace this)
        # For now, let's get it from the database
        container = get_container()
        pool = await container.database.asyncpg_pool()

        async with pool.acquire() as conn:
            # Find the user who owns this channel
            channel_id = 100267887654
            user_row = await conn.fetchrow(
                """
                SELECT user_id FROM channels WHERE id = $1
            """,
                channel_id,
            )

            if not user_row:
                print(f"❌ Channel {channel_id} not found in database!")
                print("\nℹ️  This channel needs to be added to your account first.")
                print("   Go to: http://localhost:11400/channels")
                print("   Click 'Add Channel' and add: ABC LEGACY NEWS")
                return False

            user_id = user_row["user_id"]
            print(f"✅ Found channel owner: User ID {user_id}")

        # Initialize collection service
        print("\n🔧 Initializing MTProto collection service...")
        service = MTProtoDataCollectionService()
        await service.initialize()

        # Collect data for this user's channels
        print(f"\n📥 Collecting data for user {user_id}...")
        print("   This may take a few minutes...")

        result = await service.collect_user_channel_history(
            user_id=user_id,
            limit_per_channel=50,  # Get last 50 messages
        )

        print("\n" + "=" * 60)
        print("📊 Collection Results:")
        print("=" * 60)
        print(f"Success: {result.get('success')}")
        print(f"Channels synced: {result.get('channels_synced', 0)}")
        print(f"Total messages: {result.get('total_messages', 0)}")

        if result.get("errors"):
            print("\n⚠️  Errors encountered:")
            for error in result["errors"]:
                print(f"   - {error}")

        # Verify data was collected
        async with pool.acquire() as conn:
            posts_count = await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE channel_id = $1", channel_id
            )
            metrics_count = await conn.fetchval(
                "SELECT COUNT(*) FROM post_metrics WHERE channel_id = $1", channel_id
            )

            print("\n✅ Database verification:")
            print(f"   Posts collected: {posts_count}")
            print(f"   Metrics snapshots: {metrics_count}")

        print("\n🎉 Collection complete!")
        print("   Refresh your analytics dashboard to see the data")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(collect_channel_data())
    sys.exit(0 if success else 1)
