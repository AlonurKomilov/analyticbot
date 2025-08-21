#!/usr/bin/env python3
"""
Bot ishga tushirish script
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Bot ishga tushirish"""
    try:
        # Import bot module  
        from bot.bot import main as bot_main
        # Run the bot
        asyncio.run(bot_main())
    except Exception as e:
        print(f"Bot ishga tushishda xatolik: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
