#!/usr/bin/env python3
"""
Real Data Collection Script - Final Working Version

Collects real Telegram data using the working authentication and stores in database.
"""

import asyncio
import logging
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


async def create_real_repositories():
    """Create real database repositories."""
    import asyncpg

    # Get database URL from environment
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://analytic:change_me@localhost:5433/analytic_bot"
    )

    # Convert for asyncpg
    if database_url.startswith("postgresql+asyncpg://"):
        db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    else:
        db_url = database_url

    # Create connection pool
    db_pool = await asyncpg.create_pool(
        db_url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )

    # Import repositories
    from infra.db.repositories.channel_repository import ChannelRepository
    from infra.db.repositories.post_metrics_repository import PostMetricsRepository
    from infra.db.repositories.post_repository import PostRepository

    # Create repository container
    class RepositoryContainer:
        def __init__(self, db_pool):
            self.channel_repo = ChannelRepository(db_pool)
            self.post_repo = PostRepository(db_pool)
            self.metrics_repo = PostMetricsRepository(db_pool)

    return RepositoryContainer(db_pool)


async def collect_from_channel(client, repos, channel_username, limit=50):
    """Collect messages from a specific channel."""
    print(f"📥 Collecting from {channel_username}...")

    try:
        # Get channel entity directly from the underlying Telethon client
        entity = await client._client.get_entity(channel_username)
        print(f"   Found channel: {entity.title}")

        # Ensure channel exists in database
        await repos.channel_repo.ensure_channel(
            channel_id=entity.id,
            username=channel_username.replace("@", ""),
            title=entity.title,
            is_supergroup=hasattr(entity, "megagroup") and getattr(entity, "megagroup", False),
        )

        messages_collected = 0
        processed_count = 0

        print("   🛡️ Processing with rate limiting protection...")

        # Collect recent messages using Telethon client directly with SAFE rate limiting
        async for message in client._client.iter_messages(entity, limit=limit):
            if message.text:
                try:
                    # Create post data
                    post_data = {
                        "channel_id": entity.id,
                        "msg_id": message.id,
                        "text": message.text,
                        "date": message.date,
                        "links_json": [],
                    }

                    # Store post
                    result = await repos.post_repo.upsert_post(**post_data)

                    # Skip metrics for now - will fix method signature later
                    if result.get("inserted"):
                        messages_collected += 1
                        print(f"   ✅ Stored new message {message.id}")
                    elif result.get("updated"):
                        print(f"   � Updated message {message.id}")

                except Exception as e:
                    print(f"   ⚠️ Error storing message {message.id}: {e}")
                    continue

                processed_count += 1

                # MULTI-LAYER RATE LIMITING: Critical protection against Telegram blocks

                # Layer 1: Base delay between every message
                await asyncio.sleep(0.5)  # 500ms delay between messages for safety

                # Layer 2: Extended pause every 5 messages
                if processed_count % 5 == 0:
                    print(f"   ⏳ Processed {processed_count} messages, sleeping 3 seconds...")
                    await asyncio.sleep(3)

                # Layer 3: Long pause every 20 messages
                if processed_count % 20 == 0:
                    print(
                        f"   🛡️ Processed {processed_count} messages, extended sleep 10 seconds..."
                    )
                    await asyncio.sleep(10)

        print(f"✅ Collected {messages_collected} messages from {channel_username}")
        print(
            f"   🛡️ Applied {processed_count * 0.5 + (processed_count // 5) * 3 + (processed_count // 20) * 10:.1f}s of rate limiting delays"
        )
        return messages_collected

    except Exception as e:
        print(f"❌ Error collecting from {channel_username}: {e}")
        return 0


async def main():
    """Main data collection function."""
    print("📊 Real Telegram Data Collection")
    print("=" * 40)

    # Load environment
    load_env()

    # Import after loading env
    from apps.mtproto.config import MTProtoSettings
    from infra.tg.telethon_client import TelethonTGClient

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Initialize settings
        settings = MTProtoSettings()

        if not settings.MTPROTO_ENABLED:
            print("❌ MTProto is disabled")
            return False

        if not settings.MTPROTO_PEERS:
            print("❌ No channels configured")
            print("   Add channels to MTPROTO_PEERS in .env")
            return False

        print(f"🔧 Initializing collection for {len(settings.MTPROTO_PEERS)} channels...")
        print("🛡️ MULTI-LAYER RATE LIMITING ENABLED:")
        print("   • 500ms delay between messages")
        print("   • 3s pause every 5 messages")
        print("   • 10s pause every 20 messages")
        print("   • 8s delay between channels")
        print("   • Max 50 messages per channel")

        # Create repositories
        repos = await create_real_repositories()
        print("✅ Database connection established")

        # Create Telegram client
        tg_client = TelethonTGClient(settings)
        await tg_client.start()

        me = await tg_client.get_me()
        print(f"✅ Connected as: {me.first_name}")

        # Collect from each channel
        total_collected = 0

        for channel in settings.MTPROTO_PEERS:
            try:
                print(f"\n📊 Processing channel: {channel}")
                count = await collect_from_channel(
                    tg_client,
                    repos,
                    channel,
                    limit=min(settings.MTPROTO_HISTORY_LIMIT_PER_RUN, 50),  # Cap at 50 for safety
                )
                total_collected += count

                # INTER-CHANNEL RATE LIMITING: Longer delay between channels
                print("🛡️ Sleeping 8 seconds between channels for safety...")
                await asyncio.sleep(8)

            except Exception as e:
                print(f"❌ Failed to collect from {channel}: {e}")
                continue

        await tg_client.stop()

        print("\n🎉 SAFE Collection complete!")
        print(f"   📊 Total messages collected: {total_collected}")
        print(f"   📺 Channels processed: {len(settings.MTPROTO_PEERS)}")
        print("   🛡️ Rate limiting protected your account")

        return True

    except Exception as e:
        print(f"❌ Collection failed: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
