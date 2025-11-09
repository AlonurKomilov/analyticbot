#!/usr/bin/env python3
"""
Collect ALL posts from ABC LEGACY NEWS channel
This will fetch up to 5000 messages with the updated configuration
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

logger = logging.getLogger(__name__)


async def main():
    """Collect all posts from ABC LEGACY NEWS"""

    print("\n" + "=" * 70)
    print("📊 ABC LEGACY NEWS - FULL HISTORY COLLECTION")
    print("=" * 70 + "\n")

    try:
        from apps.di import get_container
        from apps.mtproto.services.data_collection_service import MTProtoDataCollectionService

        # Initialize container
        container = get_container()
        pool = await container.database.asyncpg_pool()

        # Get channel and user info
        channel_id = 1002678877654  # ABC LEGACY NEWS

        async with pool.acquire() as conn:
            channel_row = await conn.fetchrow(
                "SELECT user_id, title FROM channels WHERE id = $1", channel_id
            )

            if not channel_row:
                print(f"❌ Channel {channel_id} not found!")
                return False

            user_id = channel_row["user_id"]
            channel_title = channel_row["title"]

            print(f"✅ Channel: {channel_title}")
            print(f"✅ Owner User ID: {user_id}")
            print(f"✅ Channel ID: {channel_id}")

            # Check current posts count
            current_count = await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE channel_id = $1", channel_id
            )
            print(f"📝 Current posts in database: {current_count}")

        # Initialize collection service
        print("\n🔧 Initializing MTProto collection service...")
        service = MTProtoDataCollectionService()
        await service.initialize()

        # Collect with increased limit
        print("\n📥 Starting full history collection...")
        print("   Limit per run: 5000 messages")
        print("   This may take several minutes...\n")

        result = await service.collect_user_channel_history(
            user_id=user_id,
            limit_per_channel=5000,  # Use the new limit from .env
        )

        print("\n" + "=" * 70)
        print("📊 COLLECTION RESULTS")
        print("=" * 70)
        print(f"✅ Success: {result.get('success')}")
        print(f"📺 Channels synced: {result.get('channels_synced', 0)}")
        print(f"📝 Total messages collected: {result.get('total_messages', 0)}")

        if result.get("errors"):
            print("\n⚠️  Errors encountered:")
            for error in result["errors"]:
                print(f"   - {error}")

        # Check final count
        async with pool.acquire() as conn:
            final_count = await conn.fetchval(
                "SELECT COUNT(*) FROM posts WHERE channel_id = $1", channel_id
            )
            new_posts = final_count - current_count

            print("\n📈 STATISTICS:")
            print(f"   Previous posts: {current_count}")
            print(f"   New posts added: {new_posts}")
            print(f"   Total posts now: {final_count}")

            # Get date range
            date_range = await conn.fetchrow(
                """
                SELECT
                    MIN(date) as oldest,
                    MAX(date) as newest,
                    MIN(msg_id) as min_msg,
                    MAX(msg_id) as max_msg
                FROM posts
                WHERE channel_id = $1
                """,
                channel_id,
            )

            if date_range:
                print("\n📅 DATE RANGE:")
                print(f"   Oldest post: {date_range['oldest']}")
                print(f"   Newest post: {date_range['newest']}")
                print(f"   Message ID range: {date_range['min_msg']} - {date_range['max_msg']}")

        print("\n" + "=" * 70)
        print("✅ COLLECTION COMPLETE!")
        print("=" * 70)

        return True

    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
