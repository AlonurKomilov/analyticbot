#!/usr/bin/env python3
"""
Simple MTProto Connection Test

Tests if we can connect to Telegram and fetch messages from ABC Legacy News.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_connection():
    """Test MTProto connection and message fetching."""

    print("=" * 60)
    print("🧪 MTProto Connection Test")
    print("=" * 60)
    print()

    try:
        # Import required services
        from apps.mtproto.multi_tenant.user_mtproto_service import (
            get_user_mtproto_service,
        )

        print("1️⃣ Getting MTProto service...")
        mtproto_service = get_user_mtproto_service()  # Not async
        print("   ✅ MTProto service initialized")
        print()

        print("2️⃣ Getting user's Telegram client...")
        user_id = 844338517  # Your user ID

        try:
            client = await mtproto_service.get_user_client(user_id=user_id)

            if not client:
                print("   ❌ Could not get client - user may need to reconnect MTProto")
                return

            print("   ✅ Client retrieved successfully!")
            print()

            print("3️⃣ Testing channel access...")
            channel_username = "abc_legacy_news"

            try:
                # Get underlying Telethon client
                telethon_client = client.client  # type: ignore

                # Get channel info
                print(f"   Fetching channel info for @{channel_username}...")
                channel = await telethon_client.get_entity(f"@{channel_username}")  # type: ignore

                print("   ✅ Channel found!")
                print(f"      Title: {channel.title}")  # type: ignore
                print(f"      ID: {channel.id}")  # type: ignore
                print(f"      Username: @{channel.username}")  # type: ignore
                if hasattr(channel, "participants_count"):
                    print(f"      Subscribers: {channel.participants_count}")  # type: ignore
                print()

                print("4️⃣ Fetching recent messages...")
                messages = await telethon_client.get_messages(f"@{channel_username}", limit=10)  # type: ignore

                print(f"   ✅ Retrieved {len(messages)} messages!")  # type: ignore
                print()

                if messages:
                    print("   📝 Sample messages:")
                    for i, msg in enumerate(messages[:5], 1):  # type: ignore
                        print(f"      {i}. Message ID: {msg.id}")
                        print(f"         Date: {msg.date}")
                        print(f"         Views: {getattr(msg, 'views', 0)}")
                        print(f"         Forwards: {getattr(msg, 'forwards', 0)}")
                        if msg.message:
                            preview = msg.message[:60].replace("\n", " ")
                            print(f"         Text: {preview}...")
                        print()

                    print("=" * 60)
                    print("✅ SUCCESS! MTProto is working perfectly!")
                    print("=" * 60)
                    print()
                    print("📊 Summary:")
                    print("   • Connected to Telegram: ✅")
                    print("   • Channel accessible: ✅")
                    print(f"   • Messages retrieved: {len(messages)}")  # type: ignore
                    print("   • Can fetch analytics data: ✅")
                    print()
                    print("🎯 Next Steps:")
                    print("   1. Data is being fetched successfully")
                    print("   2. Now we need to store it in the database")
                    print("   3. Then frontend will display the analytics")

                else:
                    print("   ⚠️  No messages found (channel may be empty)")

            except Exception as e:
                print(f"   ❌ Error accessing channel: {e}")
                import traceback

                traceback.print_exc()

        except Exception as e:
            print(f"   ❌ Error getting client: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())
