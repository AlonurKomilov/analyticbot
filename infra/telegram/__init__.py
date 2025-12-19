"""
Telegram Infrastructure Module.

This module consolidates all Telegram-related infrastructure:

- aiogram/: Bot API client using aiogram library
  - For sending messages, media, bot operations
  - Implements TelegramService port from core

- telethon/: MTProto client using Telethon library  
  - For data collection from channels
  - Message history, real-time updates
  - Statistics and analytics data

Usage:
    # For bot operations (sending messages)
    from infra.telegram.aiogram import AiogramTelegramService
    
    # For data collection (MTProto)
    from infra.telegram.telethon import TelethonTGClient, AccountPool
"""

# Re-export commonly used classes for convenience
from infra.telegram.aiogram import AiogramTelegramService
from infra.telegram.telethon import (
    TelethonTGClient,
    AccountPool,
    DCRouter,
    ProxyPool,
    normalize_message,
    normalize_update,
)

__all__ = [
    # Aiogram (Bot API)
    "AiogramTelegramService",
    # Telethon (MTProto)
    "TelethonTGClient",
    "AccountPool", 
    "DCRouter",
    "ProxyPool",
    "normalize_message",
    "normalize_update",
]
