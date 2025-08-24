"""
Bot ishga tushirish script
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Bot ishga tushirish"""
    try:
        from apps.bot.bot import main as bot_main

        asyncio.run(bot_main())
    except Exception as e:
        print(f"Bot ishga tushishda xatolik: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
