#!/usr/bin/env python3
"""
Test MTProto Data Ingestion for ABC Legacy News Channel

This script tests if MTProto can fetch and store channel data.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_mtproto_ingestion():
    """Test MTProto data ingestion for ABC Legacy News channel."""

    print("=" * 60)
    print("🧪 MTProto Data Ingestion Test")
    print("=" * 60)
    print()

    # Step 1: Check database connectivity
    print("1️⃣ Checking database connection...")
    try:
        import asyncpg

        conn = await asyncpg.connect("postgresql://analytic:change_me@localhost:10100/analytic_bot")
        print("   ✅ Database connected")

        # Check channel exists
        channel = await conn.fetchrow("SELECT * FROM channels WHERE id = $1", 1002678877654)
        if channel:
            print(f"   ✅ Channel found: {channel['title']} (@{channel['username']})")
        else:
            print("   ❌ Channel not found in database")
            await conn.close()
            return

        # Check MTProto settings
        mtproto_settings = await conn.fetchrow(
            "SELECT * FROM channel_mtproto_settings WHERE channel_id = $1",
            1002678877654,
        )
        if mtproto_settings and mtproto_settings["mtproto_enabled"]:
            print("   ✅ MTProto enabled for channel")
        else:
            print("   ❌ MTProto not enabled for channel")
            await conn.close()
            return

        # Check user credentials
        user_creds = await conn.fetchrow(
            "SELECT * FROM user_bot_credentials WHERE user_id = $1", 844338517
        )
        if user_creds:
            has_session = user_creds.get("telegram_session_encrypted") is not None
            print(f"   MTProto credentials: {'✅ Has session' if has_session else '❌ No session'}")
            if not has_session:
                print("   ⚠️  User needs to complete MTProto setup first!")
                await conn.close()
                return
        else:
            print("   ❌ No user credentials found")
            await conn.close()
            return

        await conn.close()
        print()

    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return

    # Step 2: Check if we can initialize MTProto client
    print("2️⃣ Checking MTProto client initialization...")
    try:
        from apps.mtproto.multi_tenant.user_mtproto_service import UserMTProtoService
        from core.services.encryption_service import EncryptionService
        from infra.db.repositories.user_bot_repository_factory import (
            UserBotRepositoryFactory,
        )

        # Initialize services
        encryption_service = EncryptionService()

        # Create asyncpg pool
        db_pool = await asyncpg.create_pool(
            "postgresql://analytic:change_me@localhost:10100/analytic_bot",
            min_size=2,
            max_size=5,
        )

        # Create repository factory
        repo_factory = UserBotRepositoryFactory(db_pool)
        user_bot_repo = repo_factory.create()

        # Create MTProto service
        mtproto_service = UserMTProtoService(
            user_bot_repository=user_bot_repo, encryption_service=encryption_service
        )

        print("   ✅ MTProto service initialized")
        print()

        # Step 3: Try to get user's MTProto client
        print("3️⃣ Getting user's MTProto client...")
        try:
            client = await mtproto_service.get_user_client(user_id=844338517)
            if client:
                print("   ✅ MTProto client retrieved")

                # Test: Get channel info
                print()
                print("4️⃣ Fetching channel information...")
                try:
                    # Get channel entity
                    channel_entity = await client.get_entity("@abc_legacy_news")
                    print(f"   ✅ Channel: {channel_entity.title}")
                    print(f"      ID: {channel_entity.id}")
                    print(f"      Username: @{channel_entity.username}")
                    print(
                        f"      Participants: {getattr(channel_entity, 'participants_count', 'N/A')}"
                    )
                    print()

                    # Test: Fetch recent messages
                    print("5️⃣ Fetching recent messages (last 10)...")
                    messages = await client.get_messages("@abc_legacy_news", limit=10)
                    print(f"   ✅ Retrieved {len(messages)} messages")

                    if messages:
                        print()
                        print("   📝 Sample messages:")
                        for i, msg in enumerate(messages[:3], 1):
                            print(f"      {i}. Message ID: {msg.id}")
                            print(f"         Date: {msg.date}")
                            print(f"         Views: {getattr(msg, 'views', 'N/A')}")
                            if msg.message:
                                preview = msg.message[:50].replace("\n", " ")
                                print(f"         Text: {preview}...")
                            print()

                        print("   ✅ MTProto is working! Data can be fetched successfully!")
                        print()
                        print("=" * 60)
                        print("🎉 SUCCESS: MTProto ingestion is functional!")
                        print("=" * 60)
                        print()
                        print("Next steps:")
                        print("1. Create a background worker to run this periodically")
                        print("2. Store messages in the database")
                        print("3. Update frontend to display the data")

                    else:
                        print("   ⚠️  No messages found in channel")

                except Exception as e:
                    print(f"   ❌ Error fetching channel data: {e}")
                    import traceback

                    traceback.print_exc()
            else:
                print("   ❌ Could not get MTProto client")
                print("   ⚠️  User may need to set up MTProto credentials via the API")

        except Exception as e:
            print(f"   ❌ Error getting client: {e}")
            import traceback

            traceback.print_exc()

        finally:
            await db_pool.close()

    except Exception as e:
        print(f"   ❌ Error initializing MTProto: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mtproto_ingestion())
