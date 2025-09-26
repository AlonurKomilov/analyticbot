"""Test config loading"""

try:
    from src.config import settings

    print("✅ Config loaded successfully!")
    print(f"BOT_TOKEN exists: {bool(settings.BOT_TOKEN)}")
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"❌ Error loading config: {e}")
