#!/usr/bin/env python3
"""
Direct MTProto Test - Uses Telethon directly with stored credentials
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_mtproto():
    """Test MTProto connection directly with Telethon."""

    print("=" * 60)
    print("🧪 Direct MTProto Test")
    print("=" * 60)
    print()

    try:
        import asyncpg
        from telethon import TelegramClient
        from telethon.sessions import StringSession

        from core.services.system.encryption_service import EncryptionService

        # Step 1: Get credentials from database
        print("1️⃣ Fetching credentials from database...")
        conn = await asyncpg.connect("postgresql://analytic:change_me@localhost:10100/analytic_bot")

        creds = await conn.fetchrow(
            "SELECT mtproto_api_id, telegram_api_hash, session_string FROM user_bot_credentials WHERE user_id = $1",
            844338517,
        )

        if not creds:
            print("   ❌ No credentials found")
            return

        api_id = creds["mtproto_api_id"]
        encrypted_hash = creds["telegram_api_hash"]
        session_string = creds["session_string"]

        print("   ✅ Found credentials")
        print(f"      API ID: {api_id}")
        print(f"      Has API Hash: {'✅' if encrypted_hash else '❌'}")
        print(f"      Has Session: {'✅' if session_string else '❌'}")
        print()

        await conn.close()

        # Step 2: Decrypt credentials
        print("2️⃣ Decrypting credentials...")
        encryption_service = EncryptionService()
        api_hash = encryption_service.decrypt(encrypted_hash)
        decrypted_session = encryption_service.decrypt(session_string)
        print("   ✅ API hash decrypted")
        print("   ✅ Session string decrypted")
        print()

        # Step 3: Create Telethon client
        print("3️⃣ Creating Telegram client...")
        session = StringSession(decrypted_session)
        client = TelegramClient(
            session,
            api_id=api_id,
            api_hash=api_hash,
        )

        await client.connect()

        if await client.is_user_authorized():
            print("   ✅ Client connected and authorized!")
            print()

            # Step 4: Test channel access
            print("4️⃣ Testing channel access...")
            channel_id = -1002678877654  # Telegram channel ID (with -100 prefix)
            channel_username = "abc_legacy_news"

            try:
                # Try getting channel by ID first, fallback to username
                try:
                    channel = await client.get_entity(channel_id)  # type: ignore
                except:
                    print(f"   Trying username @{channel_username}...")
                    channel = await client.get_entity(f"@{channel_username}")  # type: ignore
                print(f"   ✅ Channel: {channel.title}")  # type: ignore
                print(f"      ID: {channel.id}")  # type: ignore
                print(f"      Username: @{channel.username}")  # type: ignore
                print()

                # Get messages
                print("5️⃣ Fetching recent messages...")
                messages = await client.get_messages(channel_id, limit=10)  # type: ignore
                print(f"   ✅ Retrieved {len(messages)} messages!")  # type: ignore
                print()

                if messages:
                    print("   📝 Recent messages:")
                    for i, msg in enumerate(messages[:5], 1):  # type: ignore
                        print(
                            f"      {i}. ID: {msg.id} | Date: {msg.date.strftime('%Y-%m-%d %H:%M')}"
                        )
                        print(
                            f"         Views: {getattr(msg, 'views', 0):,} | Forwards: {getattr(msg, 'forwards', 0):,}"
                        )
                        if msg.message:
                            preview = msg.message[:50].replace("\n", " ")
                            print(f"         Text: {preview}...")
                        print()

                    print("=" * 60)
                    print("🎉 SUCCESS! MTProto is fully functional!")
                    print("=" * 60)
                    print()
                    print("✅ What's working:")
                    print("   • Database credentials: ✅")
                    print("   • Telegram connection: ✅")
                    print("   • Channel access: ✅")
                    print("   • Message retrieval: ✅")
                    print()
                    print("📊 Data available:")
                    print(f"   • Total messages fetched: {len(messages)}")  # type: ignore
                    print(f"   • Total views: {sum(getattr(m, 'views', 0) for m in messages):,}")  # type: ignore
                    print(
                        f"   • Date range: {messages[-1].date.strftime('%Y-%m-%d')} to {messages[0].date.strftime('%Y-%m-%d')}"
                    )  # type: ignore
                    print()
                    print("🚀 Next steps:")
                    print("   1. ✅ MTProto setup complete")
                    print("   2. Create background worker to fetch data automatically")
                    print("   3. Store messages in database")
                    print("   4. Display analytics in frontend")

                else:
                    print("   ⚠️  Channel has no messages")

            except Exception as e:
                print(f"   ❌ Error accessing channel: {e}")
                import traceback

                traceback.print_exc()
        else:
            print("   ❌ Client not authorized")

        disconnect_result = client.disconnect()  # type: ignore
        if disconnect_result:
            await disconnect_result  # type: ignore

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mtproto())
