#!/usr/bin/env python3
"""
Verify bot can access a channel and get the actual chat ID
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aiogram import Bot
from aiogram.types import Chat
from dotenv import load_dotenv

from core.services.encryption_service import EncryptionService

# Load environment
load_dotenv(".env.development")


async def verify_channel_access(bot_token: str, channel_username: str):
    """Verify bot can access channel and get details"""
    bot = Bot(token=bot_token)

    try:
        print(f"\n🔍 Checking bot access to @{channel_username}...")

        # Try to get chat info using username
        try:
            chat: Chat = await bot.get_chat(f"@{channel_username}")
            print("✅ Bot can access channel via username!")
            print(f"   Chat ID: {chat.id}")
            print(f"   Title: {chat.title}")
            print(f"   Type: {chat.type}")
            print(f"   Username: @{chat.username}")
            return chat.id
        except Exception as e:
            print(f"❌ Cannot access via @{channel_username}: {e}")

        # Try with -100 prefix format
        channel_id = 1002678877654
        chat_id_formats = [
            -1001002678877654,  # Standard format
            -100 - channel_id,  # Alternative
            -channel_id,  # Without -100
            channel_id,  # Positive
        ]

        print("\n🔍 Trying different chat ID formats...")
        for chat_id in chat_id_formats:
            try:
                chat = await bot.get_chat(chat_id)
                print(f"✅ Found channel with chat_id={chat_id}")
                print(f"   Title: {chat.title}")
                print(f"   Type: {chat.type}")
                print(f"   Username: @{chat.username if chat.username else 'N/A'}")
                return chat_id
            except Exception as e:
                print(f"❌ chat_id={chat_id}: {str(e)[:50]}")

        return None

    finally:
        await bot.session.close()


async def main():
    # Get bot token from database
    import psycopg2

    conn = psycopg2.connect(
        host="localhost",
        port=10100,
        database="analytic_bot",
        user="analytic",
        password="change_me",
    )

    cur = conn.cursor()
    cur.execute("SELECT bot_token FROM user_bot_credentials WHERE user_id = 844338517;")
    result = cur.fetchone()

    if not result:
        print("❌ No bot credentials found for user 844338517")
        return

    encrypted_token = result[0]
    print(f"✅ Found encrypted token: {encrypted_token[:20]}...")

    # Decrypt token
    encryption_service = EncryptionService()
    bot_token = encryption_service.decrypt(encrypted_token)
    print(f"✅ Decrypted bot token: {bot_token[:20]}...")

    # Verify access
    chat_id = await verify_channel_access(bot_token, "abclegacynews")

    if chat_id:
        print(f"\n✅ SUCCESS: Use chat_id={chat_id} to send messages")
    else:
        print("\n❌ FAILED: Bot cannot access the channel")
        print("\n💡 Solutions:")
        print("   1. Make sure the bot @abc_control_copyright_bot is added to the channel")
        print("   2. Make sure the bot is an admin (or channel is public)")
        print("   3. The channel ID in your database might be wrong")

    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
