#!/usr/bin/env python3
"""
Real Telegram Data Collection with Rate Limiting Protection
This script safely collects real data from Telegram channels using the MTProto client.
INCLUDES RATE LIMITING to prevent Telegram API blocks.
"""

import asyncio
import logging
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from config.settings import load_env


async def create_real_repositories():
    """Create repositories for PostgreSQL (V2 system)."""
    from infra.db.connection_manager import ConnectionManager
    from infra.db.repositories.channel_repository import ChannelRepository
    from infra.db.repositories.post_repository import PostRepository
    from infra.db.repositories.user_repository import UserRepository
    
    # Initialize connection manager
    conn_manager = ConnectionManager()
    await conn_manager.connect()
    
    # Create repositories
    class Repositories:
        def __init__(self):
            self.channel_repo = ChannelRepository(conn_manager)
            self.post_repo = PostRepository(conn_manager)
            self.user_repo = UserRepository(conn_manager)
    
    return Repositories()


async def collect_channel_data_safe(client, repos, channel_username: str, limit: int = 50):
    """
    Collect data from a single channel with RATE LIMITING protection.
    
    Args:
        client: Telethon client
        repos: Repository container
        channel_username: Channel username (with or without @)
        limit: Maximum number of messages to collect
    
    Returns:
        int: Number of messages collected
    """
    try:
        print(f"\n📥 Collecting from {channel_username}...")
        
        # Get channel entity
        entity = await client._client.get_entity(channel_username)
        print(f"   Found channel: {entity.title} (ID: {entity.id})")
        
        # Store/update channel
        await repos.channel_repo.upsert_channel(
            channel_id=entity.id,
            username=channel_username.replace("@", ""),
            title=entity.title,
            is_supergroup=hasattr(entity, 'megagroup') and getattr(entity, 'megagroup', False)
        )
        
        messages_collected = 0
        processed_count = 0
        
        print(f"   Processing messages with rate limiting protection...")
        
        # Collect recent messages with SAFE RATE LIMITING
        async for message in client._client.iter_messages(entity, limit=limit):
            if message.text:
                try:
                    # Create post data
                    post_data = {
                        "channel_id": entity.id,
                        "msg_id": message.id,
                        "text": message.text,
                        "date": message.date,
                        "links_json": []
                    }
                    
                    # Store post
                    result = await repos.post_repo.upsert_post(**post_data)
                    
                    # Track results
                    if result.get("inserted"):
                        messages_collected += 1
                        print(f"   ✅ Stored new message {message.id}")
                    elif result.get("updated"):
                        print(f"   🔄 Updated message {message.id}")
                        
                except Exception as e:
                    print(f"   ⚠️ Error storing message {message.id}: {e}")
                
                processed_count += 1
                
                # RATE LIMITING PROTECTION - Critical for avoiding Telegram blocks
                
                # 1. Basic delay between every message (increased for safety)
                await asyncio.sleep(0.5)  # 500ms between messages
                
                # 2. Longer pause every 5 messages (reduced frequency for safety)
                if processed_count % 5 == 0:
                    print(f"   ⏳ Processed {processed_count} messages, sleeping for 5 seconds...")
                    await asyncio.sleep(5)
                
                # 3. Even longer pause every 25 messages
                if processed_count % 25 == 0:
                    print(f"   🛡️ Processed {processed_count} messages, extended sleep for 15 seconds...")
                    await asyncio.sleep(15)
        
        print(f"✅ Safely collected {messages_collected} messages from {channel_username}")
        print(f"   Rate limiting: {processed_count * 0.5 + (processed_count // 5) * 5 + (processed_count // 25) * 15:.1f}s total delays")
        return messages_collected
        
    except Exception as e:
        print(f"❌ Error collecting from {channel_username}: {e}")
        return 0


async def main():
    """Main data collection function with rate limiting protection."""
    print("📊 SAFE Real Telegram Data Collection")
    print("🛡️ WITH RATE LIMITING PROTECTION")
    print("=" * 50)
    
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
        
        print(f"🔧 Initializing SAFE collection for {len(settings.MTPROTO_PEERS)} channels...")
        print("🛡️ Rate limiting enabled: 500ms per message + frequent pauses")
        
        # Create repositories
        repos = await create_real_repositories()
        print("✅ Database connection established")
        
        # Create Telegram client
        client = TelethonTGClient(
            api_id=settings.TELEGRAM_API_ID,
            api_hash=settings.TELEGRAM_API_HASH,
            session_name="analyticbot_session"
        )
        
        # Connect to Telegram
        if not await client.connect():
            print("❌ Failed to connect to Telegram")
            return False
        
        print("✅ Connected to Telegram safely")
        
        # Collect data from each channel with rate limiting
        total_collected = 0
        for i, channel in enumerate(settings.MTPROTO_PEERS):
            print(f"\n📊 Processing channel {i+1}/{len(settings.MTPROTO_PEERS)}: {channel}")
            collected = await collect_channel_data_safe(
                client=client,
                repos=repos,
                channel_username=channel,
                limit=50  # Conservative limit to reduce API load
            )
            total_collected += collected
            
            # INTER-CHANNEL RATE LIMITING (increased)
            if i < len(settings.MTPROTO_PEERS) - 1:  # Don't sleep after last channel
                print("🛡️ Sleeping 10 seconds between channels to avoid rate limits...")
                await asyncio.sleep(10)
        
        print(f"\n🎉 Safe collection completed!")
        print(f"📊 Total messages collected: {total_collected}")
        print("🛡️ Rate limiting protected your Telegram account")
        
        # Cleanup
        await client.disconnect()
        
        return True
        
    except Exception as e:
        print(f"❌ Collection error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n✅ Safe data collection completed successfully!")
    else:
        print("\n❌ Data collection failed")
        sys.exit(1)
