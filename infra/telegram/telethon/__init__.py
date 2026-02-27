"""
Telethon-based MTProto Client Infrastructure.

This module provides Telegram MTProto protocol integration using Telethon.
Used for:
- Data collection from channels
- Message history retrieval
- Real-time updates
- Statistics collection

Components:
- client.py: Main Telethon client wrapper
- account_pool.py: Multi-account pool management
- dc_router.py: Data center routing and migration
- proxy_pool.py: Proxy rotation and management
- parsers.py: Message/update normalization
- stats_parsers.py: Statistics data parsing
"""

from infra.telegram.telethon.account_pool import (
    AccountPool,
    AccountState,
    AccountStatus,
)
from infra.telegram.telethon.client import TelethonTGClient
from infra.telegram.telethon.dc_router import DCRouter
from infra.telegram.telethon.parsers import normalize_message, normalize_update
from infra.telegram.telethon.proxy_pool import ProxyPool, ProxyState, ProxyStatus

__all__ = [
    "TelethonTGClient",
    "AccountPool",
    "AccountState",
    "AccountStatus",
    "DCRouter",
    "ProxyPool",
    "ProxyState",
    "ProxyStatus",
    "normalize_message",
    "normalize_update",
]
