#!/usr/bin/env python3
"""
Simple MTProto Test - Direct Telegram Connection Test

Tests Telegram API connection without complex dependency injection.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import minimal dependencies
try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError
except ImportError:
    print("❌ Telethon not installed. Install with: pip install telethon")
    sys.exit(1)


async def test_telegram_connection():
    """Test direct Telegram connection."""
    print("🔗 Testing Telegram API Connection...")

    # Load environment from .env file
    import os
    from pathlib import Path

    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#") and "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)

    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    session_name = os.getenv("TELEGRAM_SESSION_NAME", "test_session")

    if not api_id or not api_hash:
        print("❌ Missing Telegram credentials in environment")
        print("   TELEGRAM_API_ID and TELEGRAM_API_HASH must be set in .env")
        return False

    print(f"   API ID: {api_id}")
    print(f"   API Hash: {api_hash[:8]}...")
    print(f"   Session: {session_name}")

    # Ensure data directory exists
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Create client
    client = TelegramClient(str(data_dir / session_name), int(api_id), api_hash)

    try:
        print("\n🔐 Starting authentication...")
        await client.start()

        print("✅ Authentication successful!")

        # Get user info
        me = await client.get_me()
        print(f"   Connected as: {me.first_name}")
        if me.username:
            print(f"   Username: @{me.username}")
        print(f"   User ID: {me.id}")

        # Test a simple API call
        dialogs = await client.get_dialogs(limit=5)
        print(f"   Found {len(dialogs)} recent chats")

        print("\n🎉 Telegram API connection test successful!")
        return True

    except SessionPasswordNeededError:
        print("❌ Two-factor authentication is enabled")
        print("   Please enter your 2FA password when prompted")
        password = input("Enter 2FA password: ")
        await client.sign_in(password=password)

        me = await client.get_me()
        print(f"✅ 2FA authentication successful! Connected as {me.first_name}")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("   This might be:")
        print("   - Invalid API credentials")
        print("   - Network connectivity issue")
        print("   - First-time authentication needed")
        return False

    finally:
        try:
            await client.disconnect()
        except:
            pass


async def test_database_connection():
    """Test database connection."""
    print("\n🗄️  Testing Database Connection...")

    try:
        import os

        import asyncpg

        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://analytic:change_me@localhost:5433/analytic_bot",
        )

        # Parse URL for asyncpg
        if database_url.startswith("postgresql+asyncpg://"):
            db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        else:
            db_url = database_url

        # Test connection
        conn = await asyncpg.connect(db_url)

        # Test query
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
        )

        await conn.close()

        print("✅ Database connection successful!")
        print(f"   Found {result} tables in database")
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 MTProto Simple Connection Test")
    print("=" * 40)

    # Test database first
    db_ok = await test_database_connection()

    # Test Telegram connection
    tg_ok = await test_telegram_connection()

    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Database: {'✅ OK' if db_ok else '❌ Failed'}")
    print(f"   Telegram: {'✅ OK' if tg_ok else '❌ Failed'}")

    if db_ok and tg_ok:
        print("\n🎉 All tests passed! Ready for data collection.")
        print("\nNext steps:")
        print("1. Add channels to monitor: MTPROTO_PEERS")
        print("2. Start data collection: python scripts/mtproto_service.py history")
        return True
    else:
        print("\n⚠️  Fix the issues above before proceeding.")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
