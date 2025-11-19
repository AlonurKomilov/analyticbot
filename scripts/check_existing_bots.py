"""
Check if there are existing bot tokens in the database we can use for testing
"""
import asyncio
import os
import sys

# Set environment
os.environ.setdefault('ENV', 'development')

async def check_existing_bots():
    try:
        from infra.db.database import async_session_factory
        from infra.db.repositories.user_bot_repository import UserBotRepository
        
        print("=" * 60)
        print("🔍 Checking for existing bots in database...")
        print("=" * 60)
        print("")
        
        async with async_session_factory() as session:
            repo = UserBotRepository(session)
            
            try:
                bots = await repo.get_all_user_bots_for_admin()
                
                if not bots:
                    print("ℹ️  No bots found in database")
                    print("")
                    print("You'll need to create a test bot with @BotFather")
                    return
                
                print(f"✅ Found {len(bots)} bot(s) in database:")
                print("")
                
                for i, bot in enumerate(bots[:5], 1):  # Show first 5
                    print(f"Bot {i}:")
                    print(f"  User ID: {bot.user_id}")
                    print(f"  Is Active: {bot.is_active}")
                    print(f"  Created: {bot.created_at}")
                    print("")
                
                print("Note: Tokens are encrypted in the database.")
                print("You would need to:")
                print("1. Log in to the app")
                print("2. Go to bot settings")
                print("3. View/copy the bot token")
                print("")
                print("OR create a new test bot with @BotFather (recommended)")
                
            except Exception as e:
                print(f"⚠️  Could not fetch bots: {e}")
                print("")
                print("This is okay - database might not be set up yet.")
                
    except ImportError as e:
        print("⚠️  Could not import database modules")
        print(f"Error: {e}")
        print("")
        print("Database might not be configured.")
        print("Please use @BotFather to create a test bot instead.")
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("")
        print("Please use @BotFather to create a test bot instead.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_existing_bots())
