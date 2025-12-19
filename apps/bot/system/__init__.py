"""
System Bot - The main analytics bot application.

This module contains the system-level bot that uses ENV-configured credentials
(BOT_TOKEN from environment variables).

Components:
- bot.py: Main bot entry point (main() function)
- handlers/: Command and message handlers
- middlewares/: Bot middleware (auth, logging, etc.)
- services/: Bot-specific services
- api/: Health and webhook endpoints
"""

# Lazy imports - don't import bot.py at module level to avoid circular imports
# Use: from apps.bot.system.bot import main as start_system_bot

__all__ = [
    "start_system_bot",
]


def start_system_bot():
    """Lazy loader for system bot main function."""
    from apps.bot.system.bot import main
    return main
